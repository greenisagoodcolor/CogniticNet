"""
Unit tests for Belief Update with GNN Features
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, MagicMock

from inference.engine.belief_update import (
    BeliefUpdateConfig,
    DirectGraphObservationModel,
    LearnedGraphObservationModel,
    GNNBeliefUpdater,
    AttentionGraphBeliefUpdater,
    HierarchicalBeliefUpdater,
    create_belief_updater
)
from inference.engine.generative_model import (
    DiscreteGenerativeModel,
    ContinuousGenerativeModel,
    ModelDimensions,
    ModelParameters
)
from inference.engine.inference import (
    VariationalMessagePassing,
    InferenceConfig
)


class TestBeliefUpdateConfig:
    def test_default_config(self):
        """Test default configuration values"""
        config = BeliefUpdateConfig()
        assert config.update_method == 'bayesian'
        assert config.learning_rate == 0.01
        assert config.feature_weighting == 'learned'
        assert config.temporal_integration == True
        assert config.normalize_features == True

    def test_custom_config(self):
        """Test custom configuration"""
        config = BeliefUpdateConfig(
            update_method='gradient',
            learning_rate=0.1,
            feature_weighting='attention',
            use_gpu=False
        )
        assert config.update_method == 'gradient'
        assert config.learning_rate == 0.1
        assert config.feature_weighting == 'attention'
        assert config.use_gpu == False


class TestDirectGraphObservationModel:
    def test_initialization(self):
        """Test model initialization"""
        config = BeliefUpdateConfig(use_gpu=False)
        model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        assert model.state_dim == 4
        assert model.feature_dim == 8
        assert model.observation_matrix.shape == (8, 4)
        assert model.log_precision.shape == (8,)

    def test_compute_likelihood(self):
        """Test likelihood computation"""
        config = BeliefUpdateConfig(use_gpu=False)
        model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        # Test data
        graph_features = torch.randn(3, 8)
        states = torch.softmax(torch.randn(3, 4), dim=-1)

        log_likelihood = model.compute_likelihood(graph_features, states)

        assert log_likelihood.shape == (3,)
        assert not torch.any(torch.isnan(log_likelihood))
        assert not torch.any(torch.isinf(log_likelihood))

    def test_generate_observations(self):
        """Test observation generation"""
        config = BeliefUpdateConfig(use_gpu=False, normalize_features=True)
        model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        graph_features = torch.randn(3, 8)
        observations = model.generate_observations(graph_features)

        assert observations.shape == (3, 8)
        # Check normalization
        norms = torch.norm(observations, dim=-1)
        assert torch.allclose(norms, torch.ones(3) * config.feature_scale, atol=1e-6)


class TestLearnedGraphObservationModel:
    def test_initialization(self):
        """Test learned model initialization"""
        config = BeliefUpdateConfig(use_gpu=False)
        model = LearnedGraphObservationModel(config, state_dim=4, feature_dim=8, hidden_dim=32)

        assert model.state_dim == 4
        assert model.feature_dim == 8
        assert isinstance(model.feature_encoder, nn.Sequential)
        assert isinstance(model.state_encoder, nn.Sequential)
        assert isinstance(model.likelihood_net, nn.Sequential)
        assert isinstance(model.observation_decoder, nn.Sequential)

    def test_compute_likelihood(self):
        """Test learned likelihood computation"""
        config = BeliefUpdateConfig(use_gpu=False)
        model = LearnedGraphObservationModel(config, state_dim=4, feature_dim=8)

        graph_features = torch.randn(3, 8)
        states = torch.softmax(torch.randn(3, 4), dim=-1)

        log_likelihood = model.compute_likelihood(graph_features, states)

        assert log_likelihood.shape == (3,)
        assert not torch.any(torch.isnan(log_likelihood))

    def test_generate_observations(self):
        """Test learned observation generation"""
        config = BeliefUpdateConfig(use_gpu=False)
        model = LearnedGraphObservationModel(config, state_dim=4, feature_dim=8)

        graph_features = torch.randn(3, 8)
        observations = model.generate_observations(graph_features)

        assert observations.shape == (3, 4)  # Maps to state dimension


class TestGNNBeliefUpdater:
    @pytest.fixture
    def setup_updater(self):
        """Setup belief updater with components"""
        config = BeliefUpdateConfig(use_gpu=False)

        # Create generative model
        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        # Create inference algorithm
        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        # Create observation model
        obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        updater = GNNBeliefUpdater(config, gen_model, inference, obs_model)

        return updater, config, gen_model, inference, obs_model

    def test_initialization(self, setup_updater):
        """Test updater initialization"""
        updater, config, gen_model, inference, obs_model = setup_updater

        assert updater.config == config
        assert updater.generative_model == gen_model
        assert updater.inference == inference
        assert updater.observation_model == obs_model

        # Check feature weighting initialization
        assert hasattr(updater, 'feature_weights')
        assert updater.feature_weights.shape == (1,)

    def test_bayesian_update(self, setup_updater):
        """Test Bayesian belief update"""
        updater, _, _, _, _ = setup_updater
        updater.config.update_method = 'bayesian'

        # Test data
        current_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        graph_features = torch.randn(2, 8)

        updated_beliefs = updater.update_beliefs(current_beliefs, graph_features)

        assert updated_beliefs.shape == (2, 4)
        # Check valid probability distribution
        assert torch.allclose(updated_beliefs.sum(dim=-1), torch.ones(2), atol=1e-6)
        assert torch.all(updated_beliefs >= 0)
        assert torch.all(updated_beliefs <= 1)

    def test_gradient_update(self, setup_updater):
        """Test gradient-based belief update"""
        updater, _, _, _, _ = setup_updater
        updater.config.update_method = 'gradient'

        current_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        graph_features = torch.randn(2, 8)

        updated_beliefs = updater.update_beliefs(current_beliefs, graph_features)

        assert updated_beliefs.shape == (2, 4)
        assert torch.allclose(updated_beliefs.sum(dim=-1), torch.ones(2), atol=1e-6)

    def test_hybrid_update(self, setup_updater):
        """Test hybrid belief update"""
        updater, _, _, _, _ = setup_updater
        updater.config.update_method = 'hybrid'

        current_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        graph_features = torch.randn(2, 8)

        updated_beliefs = updater.update_beliefs(current_beliefs, graph_features)

        assert updated_beliefs.shape == (2, 4)
        assert torch.allclose(updated_beliefs.sum(dim=-1), torch.ones(2), atol=1e-6)

        # Test with temporal integration
        previous_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        updated_with_temporal = updater.update_beliefs(
            current_beliefs, graph_features, None, previous_beliefs
        )

        assert updated_with_temporal.shape == (2, 4)
        assert torch.allclose(updated_with_temporal.sum(dim=-1), torch.ones(2), atol=1e-6)

    def test_update_with_graph_sequence(self, setup_updater):
        """Test sequential belief updates"""
        updater, _, _, _, _ = setup_updater

        initial_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)

        # Create sequence of graph data
        graph_sequence = [
            {'graph_features': torch.randn(2, 8)},
            {'graph_features': torch.randn(2, 8)},
            {'graph_features': torch.randn(2, 8)}
        ]

        belief_trajectory = updater.update_with_graph_sequence(
            initial_beliefs, graph_sequence
        )

        assert len(belief_trajectory) == 4  # Initial + 3 updates
        for beliefs in belief_trajectory:
            assert beliefs.shape == (2, 4)
            assert torch.allclose(beliefs.sum(dim=-1), torch.ones(2), atol=1e-6)


class TestAttentionGraphBeliefUpdater:
    @pytest.fixture
    def setup_attention_updater(self):
        """Setup attention-based updater"""
        config = BeliefUpdateConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        updater = AttentionGraphBeliefUpdater(
            config, gen_model, inference, obs_model, num_heads=2
        )

        return updater

    def test_initialization(self, setup_attention_updater):
        """Test attention updater initialization"""
        updater = setup_attention_updater

        assert updater.num_heads == 2
        assert isinstance(updater.attention, nn.MultiheadAttention)
        assert isinstance(updater.query_net, nn.Linear)

    def test_compute_attended_features(self, setup_attention_updater):
        """Test attention mechanism"""
        updater = setup_attention_updater

        beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        graph_features = torch.randn(2, 5, 8)  # batch x seq_len x feature_dim

        attended_features, attention_weights = updater._compute_attended_features(
            beliefs, graph_features
        )

        assert attended_features.shape == (2, 8)
        assert attention_weights is not None

    def test_update_beliefs_with_attention(self, setup_attention_updater):
        """Test belief update with attention"""
        updater = setup_attention_updater

        current_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
        graph_features = torch.randn(2, 8)

        updated_beliefs = updater.update_beliefs(current_beliefs, graph_features)

        assert updated_beliefs.shape == (2, 4)
        assert torch.allclose(updated_beliefs.sum(dim=-1), torch.ones(2), atol=1e-6)


class TestHierarchicalBeliefUpdater:
    @pytest.fixture
    def setup_hierarchical_updater(self):
        """Setup hierarchical updater"""
        config = BeliefUpdateConfig(use_gpu=False)

        # Create updaters for each level
        level_updaters = []
        for i in range(3):
            dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
            params = ModelParameters(use_gpu=False)
            gen_model = DiscreteGenerativeModel(dims, params)

            inf_config = InferenceConfig(use_gpu=False)
            inference = VariationalMessagePassing(inf_config)

            obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

            updater = GNNBeliefUpdater(config, gen_model, inference, obs_model)
            level_updaters.append(updater)

        hier_updater = HierarchicalBeliefUpdater(config, level_updaters)

        return hier_updater

    def test_initialization(self, setup_hierarchical_updater):
        """Test hierarchical updater initialization"""
        updater = setup_hierarchical_updater

        assert updater.num_levels == 3
        assert len(updater.level_updaters) == 3
        assert len(updater.bottom_up_nets) == 2
        assert len(updater.top_down_nets) == 2

    def test_update_hierarchical_beliefs(self, setup_hierarchical_updater):
        """Test hierarchical belief update"""
        updater = setup_hierarchical_updater

        # Current beliefs at each level
        current_beliefs = [
            torch.softmax(torch.randn(2, 4), dim=-1)
            for _ in range(3)
        ]

        # Graph features at each level
        graph_features_per_level = [
            torch.randn(2, 8)
            for _ in range(3)
        ]

        updated_beliefs = updater.update_hierarchical_beliefs(
            current_beliefs, graph_features_per_level
        )

        assert len(updated_beliefs) == 3
        for beliefs in updated_beliefs:
            assert beliefs.shape == (2, 4)
            assert torch.allclose(beliefs.sum(dim=-1), torch.ones(2), atol=1e-6)


class TestFactoryFunction:
    def test_create_standard_updater(self):
        """Test creating standard updater"""
        config = BeliefUpdateConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        updater = create_belief_updater(
            'standard',
            config,
            generative_model=gen_model,
            inference_algorithm=inference,
            observation_model=obs_model
        )

        assert isinstance(updater, GNNBeliefUpdater)

    def test_create_attention_updater(self):
        """Test creating attention updater"""
        config = BeliefUpdateConfig(use_gpu=False)

        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)

        obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

        updater = create_belief_updater(
            'attention',
            config,
            generative_model=gen_model,
            inference_algorithm=inference,
            observation_model=obs_model,
            num_heads=4
        )

        assert isinstance(updater, AttentionGraphBeliefUpdater)
        assert updater.num_heads == 4

    def test_create_hierarchical_updater(self):
        """Test creating hierarchical updater"""
        config = BeliefUpdateConfig(use_gpu=False)

        # Create level updaters
        level_updaters = []
        for i in range(2):
            dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
            params = ModelParameters(use_gpu=False)
            gen_model = DiscreteGenerativeModel(dims, params)

            inf_config = InferenceConfig(use_gpu=False)
            inference = VariationalMessagePassing(inf_config)

            obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=8)

            updater = GNNBeliefUpdater(config, gen_model, inference, obs_model)
            level_updaters.append(updater)

        hier_updater = create_belief_updater(
            'hierarchical',
            config,
            level_updaters=level_updaters
        )

        assert isinstance(hier_updater, HierarchicalBeliefUpdater)
        assert hier_updater.num_levels == 2

    def test_invalid_updater_type(self):
        """Test invalid updater type"""
        with pytest.raises(ValueError, match="Unknown updater type"):
            create_belief_updater('invalid')

    def test_missing_required_params(self):
        """Test missing required parameters"""
        config = BeliefUpdateConfig(use_gpu=False)

        # Missing parameters for standard updater
        with pytest.raises(ValueError, match="Standard updater requires"):
            create_belief_updater('standard', config)

        # Missing parameters for hierarchical updater
        with pytest.raises(ValueError, match="Hierarchical updater requires"):
            create_belief_updater('hierarchical', config)
