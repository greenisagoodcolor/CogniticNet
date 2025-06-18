"""
Unit tests for Active Learning
"""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, MagicMock

from src.agents.active_inference.active_learning import (
    ActiveLearningConfig,
    InformationMetric,
    EntropyBasedSeeker,
    MutualInformationSeeker,
    ActiveLearningAgent,
    InformationGainPlanner,
    create_active_learner
)
from src.agents.active_inference.generative_model import (
    DiscreteGenerativeModel,
    ModelDimensions,
    ModelParameters
)
from src.agents.active_inference.inference import (
    VariationalMessagePassing,
    InferenceConfig
)
from src.agents.active_inference.policy_selection import (
    DiscreteExpectedFreeEnergy,
    PolicyConfig,
    Policy
)


class TestActiveLearningConfig:
    def test_default_config(self):
        """Test default configuration values"""
        config = ActiveLearningConfig()
        assert config.exploration_weight == 0.3
        assert config.information_metric == InformationMetric.EXPECTED_INFORMATION_GAIN
        assert config.min_uncertainty_threshold == 0.1
        assert config.max_uncertainty_threshold == 0.9
        assert config.curiosity_decay == 0.99
        assert config.planning_horizon == 5

    def test_custom_config(self):
        """Test custom configuration"""
        config = ActiveLearningConfig(
            exploration_weight=0.5,
            information_metric=InformationMetric.ENTROPY,
            planning_horizon=10,
            use_gpu=False
        )
        assert config.exploration_weight == 0.5
        assert config.information_metric == InformationMetric.ENTROPY
        assert config.planning_horizon == 10
        assert config.use_gpu == False


class TestEntropyBasedSeeker:
    @pytest.fixture
    def setup_seeker(self):
        """Setup entropy-based seeker"""
        config = ActiveLearningConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        seeker = EntropyBasedSeeker(config, gen_model)

        return seeker, config, gen_model

    def test_initialization(self, setup_seeker):
        """Test seeker initialization"""
        seeker, config, gen_model = setup_seeker

        assert seeker.config == config
        assert seeker.generative_model == gen_model

    def test_compute_entropy(self, setup_seeker):
        """Test entropy computation"""
        seeker, _, _ = setup_seeker

        # Test uniform distribution (max entropy)
        uniform_beliefs = torch.ones(2, 4) / 4
        entropy = seeker.compute_entropy(uniform_beliefs)

        assert entropy.shape == (2,)
        expected_entropy = -4 * (0.25 * np.log(0.25))
        assert torch.allclose(entropy, torch.tensor(expected_entropy), atol=1e-5)

        # Test deterministic distribution (min entropy)
        deterministic_beliefs = torch.zeros(2, 4)
        deterministic_beliefs[:, 0] = 1.0
        entropy = seeker.compute_entropy(deterministic_beliefs)

        assert torch.allclose(entropy, torch.zeros(2), atol=1e-5)

    def test_compute_information_value(self, setup_seeker):
        """Test information value computation"""
        seeker, _, _ = setup_seeker

        beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        possible_observations = torch.randn(3, 3)

        info_values = seeker.compute_information_value(beliefs, possible_observations)

        assert info_values.shape == (3,)
        assert torch.all(info_values >= 0)  # Information gain should be non-negative

    def test_select_informative_action(self, setup_seeker):
        """Test informative action selection"""
        seeker, _, _ = setup_seeker

        beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        available_actions = torch.eye(2)

        action = seeker.select_informative_action(beliefs, available_actions)

        assert isinstance(action, torch.Tensor)
        assert action >= 0 and action < 2


class TestMutualInformationSeeker:
    @pytest.fixture
    def setup_mi_seeker(self):
        """Setup mutual information seeker"""
        config = ActiveLearningConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        seeker = MutualInformationSeeker(config, gen_model, inference)

        return seeker, config, gen_model

    def test_initialization(self, setup_mi_seeker):
        """Test MI seeker initialization"""
        seeker, config, gen_model = setup_mi_seeker

        assert seeker.config == config
        assert seeker.generative_model == gen_model
        assert seeker.inference is not None

    def test_compute_mutual_information(self, setup_mi_seeker):
        """Test mutual information computation"""
        seeker, _, _ = setup_mi_seeker

        beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        observation_dist = torch.softmax(torch.randn(3), dim=-1)

        mi = seeker.compute_mutual_information(beliefs, observation_dist)

        assert isinstance(mi, torch.Tensor)
        assert mi >= 0  # MI should be non-negative


class TestActiveLearningAgent:
    @pytest.fixture
    def setup_agent(self):
        """Setup active learning agent"""
        config = ActiveLearningConfig(
            exploration_weight=0.3,
            use_gpu=False
        )

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        pol_config = PolicyConfig(use_gpu=False)
        policy_selector = DiscreteExpectedFreeEnergy(pol_config)

        agent = ActiveLearningAgent(config, gen_model, inference, policy_selector)

        return agent, config, gen_model

    def test_initialization(self, setup_agent):
        """Test agent initialization"""
        agent, config, gen_model = setup_agent

        assert agent.config == config
        assert agent.generative_model == gen_model
        assert agent.exploration_rate == config.exploration_weight
        assert isinstance(agent.novelty_memory, list)
        assert isinstance(agent.visit_counts, dict)

    def test_compute_epistemic_value(self, setup_agent):
        """Test epistemic value computation"""
        agent, _, _ = setup_agent

        beliefs = torch.softmax(torch.randn(1, 4), dim=-1)

        # Create test policies
        policies = [
            Policy(actions=[0, 1], horizon=2),
            Policy(actions=[1, 0], horizon=2)
        ]

        epistemic_values = agent.compute_epistemic_value(beliefs, policies)

        assert epistemic_values.shape == (2,)
        assert torch.all(epistemic_values >= 0)

    def test_compute_pragmatic_value(self, setup_agent):
        """Test pragmatic value computation"""
        agent, _, _ = setup_agent

        beliefs = torch.softmax(torch.randn(1, 4), dim=-1)
        preferences = torch.randn(3)

        policies = [
            Policy(actions=[0], horizon=1),
            Policy(actions=[1], horizon=1)
        ]

        pragmatic_values = agent.compute_pragmatic_value(beliefs, policies, preferences)

        assert pragmatic_values.shape == (2,)

    def test_select_exploratory_action(self, setup_agent):
        """Test exploratory action selection"""
        agent, _, _ = setup_agent

        beliefs = torch.softmax(torch.randn(1, 4), dim=-1)
        available_actions = torch.eye(2)

        action, info = agent.select_exploratory_action(beliefs, available_actions)

        assert isinstance(action, int)
        assert action >= 0 and action < 2

        # Check info dict
        assert 'epistemic_value' in info
        assert 'pragmatic_value' in info
        assert 'novelty_value' in info
        assert 'exploration_rate' in info

    def test_exploration_decay(self, setup_agent):
        """Test exploration rate decay"""
        agent, config, _ = setup_agent

        initial_rate = agent.exploration_rate

        beliefs = torch.softmax(torch.randn(1, 4), dim=-1)
        available_actions = torch.eye(2)

        # Select action multiple times
        for _ in range(5):
            agent.select_exploratory_action(beliefs, available_actions)

        # Check exploration rate has decayed
        expected_rate = initial_rate * (config.curiosity_decay ** 5)
        assert abs(agent.exploration_rate - expected_rate) < 1e-6

    def test_novelty_tracking(self, setup_agent):
        """Test novelty memory and visit counts"""
        agent, _, _ = setup_agent

        beliefs = torch.softmax(torch.randn(1, 4), dim=-1)
        observation = torch.randn(1, 3)

        # Update novelty memory
        agent.update_novelty_memory(beliefs, observation)

        assert len(agent.novelty_memory) == 1
        state_hash = agent._hash_belief_state(beliefs)
        assert agent.visit_counts[state_hash] == 1

        # Update again
        agent.update_novelty_memory(beliefs, observation)
        assert agent.visit_counts[state_hash] == 2


class TestInformationGainPlanner:
    @pytest.fixture
    def setup_planner(self):
        """Setup information gain planner"""
        config = ActiveLearningConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        info_seeker = EntropyBasedSeeker(config, gen_model)
        planner = InformationGainPlanner(config, gen_model, info_seeker)

        return planner, config, gen_model

    def test_initialization(self, setup_planner):
        """Test planner initialization"""
        planner, config, gen_model = setup_planner

        assert planner.config == config
        assert planner.generative_model == gen_model
        assert planner.info_seeker is not None

    def test_plan_information_gathering(self, setup_planner):
        """Test information gathering planning"""
        planner, _, _ = setup_planner

        # Start with high entropy beliefs
        current_beliefs = torch.ones(1, 4) / 4  # Uniform distribution

        planned_actions = planner.plan_information_gathering(
            current_beliefs,
            target_uncertainty=0.5,
            max_steps=5
        )

        assert isinstance(planned_actions, list)
        assert len(planned_actions) <= 5
        assert all(isinstance(a, int) for a in planned_actions)
        assert all(0 <= a < 2 for a in planned_actions)


class TestFactoryFunction:
    def test_create_agent(self):
        """Test creating active learning agent"""
        config = ActiveLearningConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        pol_config = PolicyConfig(use_gpu=False)
        policy_selector = DiscreteExpectedFreeEnergy(pol_config)

        agent = create_active_learner(
            'agent',
            config,
            generative_model=gen_model,
            inference_algorithm=inference,
            policy_selector=policy_selector
        )

        assert isinstance(agent, ActiveLearningAgent)

    def test_create_planner(self):
        """Test creating information gain planner"""
        config = ActiveLearningConfig(
            information_metric=InformationMetric.ENTROPY,
            use_gpu=False
        )

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        planner = create_active_learner(
            'planner',
            config,
            generative_model=gen_model
        )

        assert isinstance(planner, InformationGainPlanner)

    def test_invalid_learner_type(self):
        """Test invalid learner type"""
        with pytest.raises(ValueError, match="Unknown learner type"):
            create_active_learner('invalid')

    def test_missing_required_params(self):
        """Test missing required parameters"""
        config = ActiveLearningConfig(use_gpu=False)

        # Missing parameters for agent
        with pytest.raises(ValueError, match="Agent requires"):
            create_active_learner('agent', config)

        # Missing parameters for planner
        with pytest.raises(ValueError, match="Planner requires"):
            create_active_learner('planner', config)
