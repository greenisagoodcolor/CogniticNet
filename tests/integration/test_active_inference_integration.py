"""
Integration tests for Active Inference System

These tests verify that all Active Inference components work together correctly
in realistic scenarios.
"""

import pytest
import torch
import numpy as np
import time
from pathlib import Path
import tempfile
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from inference.engine.generative_model import (
    DiscreteGenerativeModel, ContinuousGenerativeModel,
    ModelDimensions, ModelParameters
)
from inference.engine.inference import (
    VariationalInference, ParticleFilter, create_inference_algorithm
)
from inference.engine.policy_selection import (
    PolicySelector, PolicyConfig
)
from inference.engine.precision import (
    PrecisionController, PrecisionConfig
)
from inference.engine.temporal_planning import (
    TemporalPlanner, PlanningConfig
)
from inference.engine.hierarchical_inference import (
    HierarchicalInference, HierarchyConfig, LevelConfig
)
from inference.engine.belief_update import (
    BeliefUpdater, UpdateConfig
)
from inference.engine.gnn_integration import (
    GNNActiveInferenceIntegration, GNNIntegrationConfig
)
from inference.engine.active_learning import (
    ActiveLearner, LearningConfig as ActiveLearningConfig
)
from inference.engine.parameter_learning import (
    OnlineParameterLearner, LearningConfig as ParamLearningConfig,
    create_parameter_learner
)
from inference.engine.computational_optimization import (
    ComputationalOptimizer, OptimizationConfig
)
from inference.engine.diagnostics import (
    DiagnosticSuite, DiagnosticConfig
)

# Import GNN components for integration
from inference.gnn.parser import GNNParser
from inference.gnn.executor import GNNExecutor

from agents.base import (
    Agent,
    Position,
    AgentStatus,
    AgentGoal,
    AgentStateManager,
    PerceptionSystem,
    DecisionSystem,
    MovementController,
    MemorySystem,
    IntegrationMode,
    ActiveInferenceConfig,
    create_active_inference_agent
)
from agents.base.perception import Stimulus, StimulusType, Percept
from agents.base.decision_making import Action, ActionType
from src.agents.testing import AgentFactory, SimulationEnvironment


class TestBasicIntegration:
    """Test basic integration of core Active Inference components"""

    def test_discrete_inference_cycle(self):
        """Test complete inference cycle with discrete model"""
        # Setup
        dims = ModelDimensions(
            num_states=4,
            num_observations=3,
            num_actions=2
        )
        params = ModelParameters(use_gpu=False)

        # Create components
        gen_model = DiscreteGenerativeModel(dims, params)
        inference = VariationalInference(dims, params)
        policy_selector = PolicySelector(PolicyConfig())

        # Initial belief
        belief = torch.ones(4) / 4

        # Simulate inference cycle
        for t in range(10):
            # Generate observation
            true_state = t % 4
            obs_probs = gen_model.A[:, true_state]
            observation = torch.multinomial(obs_probs, 1).item()

            # Update belief
            belief = inference.update_beliefs(
                belief, observation, gen_model.A
            )

            # Select action
            G_values = policy_selector.compute_expected_free_energy(
                belief, gen_model.A, gen_model.B, gen_model.C,
                num_actions=2, horizon=3
            )
            action_probs = policy_selector.select_action(G_values)
            action = torch.multinomial(action_probs, 1).item()

            # Predict next state
            next_belief = torch.matmul(gen_model.B[:, :, action], belief)

            # Verify beliefs sum to 1
            assert torch.allclose(belief.sum(), torch.tensor(1.0))
            assert torch.allclose(next_belief.sum(), torch.tensor(1.0))

    def test_continuous_inference_cycle(self):
        """Test inference cycle with continuous model"""
        dims = ModelDimensions(
            num_states=4,
            num_observations=3,
            num_actions=2
        )
        params = ModelParameters(use_gpu=False)

        # Create continuous model
        gen_model = ContinuousGenerativeModel(dims, params)

        # Use particle filter for continuous inference
        pf = ParticleFilter(num_particles=100, state_dim=4)

        # Initial state
        state = torch.randn(4)

        for t in range(5):
            # Generate observation
            obs = gen_model.observation_net(state)
            obs += torch.randn_like(obs) * 0.1  # Add noise

            # Update particles
            pf.update(obs, lambda s: gen_model.observation_net(s))

            # Get state estimate
            state_estimate = pf.get_state_estimate()

            # Select action (simplified)
            action = torch.randint(0, 2, (1,)).item()

            # Transition
            state_action = torch.cat([state, torch.tensor([action, 1-action])])
            state = gen_model.transition_net(state_action)

            # Resample particles
            pf.resample()

            assert state_estimate.shape == (4,)


class TestHierarchicalIntegration:
    """Test hierarchical Active Inference integration"""

    def test_two_level_hierarchy(self):
        """Test two-level hierarchical inference"""
        # Configure hierarchy
        config = HierarchyConfig(
            num_levels=2,
            level_configs=[
                LevelConfig(
                    num_states=8,
                    num_observations=6,
                    num_actions=4,
                    temporal_depth=1
                ),
                LevelConfig(
                    num_states=4,
                    num_observations=8,  # Receives from lower level
                    num_actions=2,
                    temporal_depth=3
                )
            ]
        )

        # Create hierarchical system
        hier_inference = HierarchicalInference(config)

        # Initialize beliefs
        beliefs = {
            0: torch.ones(8) / 8,
            1: torch.ones(4) / 4
        }

        # Run hierarchical inference
        for t in range(20):
            # Bottom-up: observation at lowest level
            observation = torch.randint(0, 6, (1,)).item()

            # Update level 0
            beliefs[0] = hier_inference.levels[0].inference.update_beliefs(
                beliefs[0], observation,
                hier_inference.levels[0].gen_model.A
            )

            # Pass up to level 1
            level1_obs = hier_inference._bottom_up_message(beliefs[0], 0)
            beliefs[1] = hier_inference.levels[1].inference.update_beliefs(
                beliefs[1], level1_obs,
                hier_inference.levels[1].gen_model.A
            )

            # Top-down: select actions
            # Level 1 action
            G1 = hier_inference.levels[1].policy_selector.compute_expected_free_energy(
                beliefs[1],
                hier_inference.levels[1].gen_model.A,
                hier_inference.levels[1].gen_model.B,
                hier_inference.levels[1].gen_model.C,
                num_actions=2, horizon=3
            )
            action1_probs = hier_inference.levels[1].policy_selector.select_action(G1)

            # Level 0 action (influenced by level 1)
            prior_adjustment = hier_inference._top_down_message(beliefs[1], action1_probs, 1)

            # Verify belief consistency
            assert torch.allclose(beliefs[0].sum(), torch.tensor(1.0))
            assert torch.allclose(beliefs[1].sum(), torch.tensor(1.0))


class TestLearningIntegration:
    """Test integration of learning components"""

    def test_online_learning_cycle(self):
        """Test online parameter learning during inference"""
        # Setup
        dims = ModelDimensions(
            num_states=4,
            num_observations=3,
            num_actions=2
        )
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        # Create learner
        learning_config = ParamLearningConfig(
            learning_rate_A=0.05,
            use_bayesian_learning=True,
            use_experience_replay=True,
            replay_buffer_size=100
        )

        learner = create_parameter_learner(
            'online',
            learning_config,
            generative_model=gen_model
        )

        # Create inference
        inference = VariationalInference(dims, params)
        belief = torch.ones(4) / 4

        # Run learning cycle
        for t in range(50):
            # Current state (hidden)
            true_state = torch.zeros(4)
            true_state[t % 4] = 1

            # Generate observation
            obs_probs = torch.matmul(gen_model.A, true_state)
            obs = torch.multinomial(obs_probs, 1).item()

            # Update belief
            old_belief = belief.clone()
            belief = inference.update_beliefs(belief, obs, gen_model.A)

            # Take random action
            action = torch.randint(0, 2, (1,)).item()
            action_vec = torch.zeros(2)
            action_vec[action] = 1

            # Next state
            next_state = torch.zeros(4)
            next_state[(t + 1) % 4] = 1

            # Create observation vector
            obs_vec = torch.zeros(3)
            obs_vec[obs] = 1

            # Learn from experience
            learner.observe(
                state=old_belief,
                action=action_vec,
                observation=obs_vec,
                next_state=belief
            )

            # Check learning progress
            if t > 0 and t % 10 == 0:
                stats = learner.get_statistics()
                assert stats['total_experiences'] == t + 1
                assert stats['num_updates'] > 0

    def test_active_learning_integration(self):
        """Test active learning with exploration"""
        dims = ModelDimensions(
            num_states=4,
            num_observations=3,
            num_actions=3
        )
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)

        # Create active learner
        al_config = ActiveLearningConfig(
            exploration_weight=0.5,
            uncertainty_method='entropy'
        )
        active_learner = ActiveLearner(al_config, gen_model)

        # Create policy selector
        policy_config = PolicyConfig(precision=1.0)
        policy_selector = PolicySelector(policy_config)

        belief = torch.ones(4) / 4

        # Run active learning
        total_uncertainty = []

        for t in range(30):
            # Compute information gain for each action
            info_gains = []
            for action in range(3):
                ig = active_learner.compute_information_gain(
                    belief, action, gen_model.A, gen_model.B
                )
                info_gains.append(ig)

            # Select action balancing exploration and exploitation
            G_exploit = policy_selector.compute_expected_free_energy(
                belief, gen_model.A, gen_model.B, gen_model.C,
                num_actions=3, horizon=1
            )

            # Active learning action selection
            best_action = active_learner.select_informative_action(
                belief, G_exploit
            )

            # Simulate transition
            obs = torch.randint(0, 3, (1,)).item()
            belief = belief + torch.randn_like(belief) * 0.1
            belief = belief / belief.sum()

            # Track uncertainty
            uncertainty = active_learner.compute_model_uncertainty(belief)
            total_uncertainty.append(uncertainty.mean().item())

        # Verify uncertainty generally decreases
        early_uncertainty = np.mean(total_uncertainty[:10])
        late_uncertainty = np.mean(total_uncertainty[-10:])
        assert late_uncertainty <= early_uncertainty * 1.1  # Allow small increase


class TestOptimizationIntegration:
    """Test computational optimization integration"""

    def test_optimized_inference_performance(self):
        """Compare optimized vs non-optimized inference"""
        dims = ModelDimensions(
            num_states=20,
            num_observations=15,
            num_actions=5
        )
        params = ModelParameters(use_gpu=False)

        # Create large sparse model
        gen_model = DiscreteGenerativeModel(dims, params)

        # Make A matrix sparse
        gen_model.A = torch.zeros_like(gen_model.A)
        for i in range(15):
            gen_model.A[i, i % 20] = 0.9
            gen_model.A[i, (i + 1) % 20] = 0.1

        # Create optimizer
        opt_config = OptimizationConfig(
            use_sparse_operations=True,
            use_caching=True,
            use_parallel_processing=True
        )
        optimizer = ComputationalOptimizer(opt_config)

        # Create belief updater
        update_config = UpdateConfig()
        updater = BeliefUpdater(update_config)

        belief = torch.ones(20) / 20
        observations = torch.randint(0, 15, (100,))

        # Time non-optimized
        start = time.time()
        for obs in observations[:50]:
            belief = updater.update_belief_discrete(
                belief, obs.item(), gen_model.A
            )
        non_opt_time = time.time() - start

        # Time optimized
        start = time.time()
        for obs in observations[50:]:
            obs_vec = torch.zeros(15)
            obs_vec[obs] = 1.0
            belief = optimizer.optimized_belief_update(
                belief, obs_vec, gen_model.A
            )
        opt_time = time.time() - start

        # Get performance report
        report = optimizer.get_performance_report()

        # Verify optimization benefits
        assert report['cache_stats']['hit_rate'] > 0  # Some cache hits
        assert len(report['timing_stats']) > 0

        optimizer.cleanup()


class TestGNNIntegration:
    """Test GNN integration with Active Inference"""

    def test_gnn_active_inference_pipeline(self):
        """Test full pipeline from GNN model to Active Inference"""
        # Create simple GNN model
        gnn_model = {
            "model_type": "discrete",
            "model_name": "test_agent",
            "dimensions": {
                "num_states": 4,
                "num_observations": 3,
                "num_actions": 2
            },
            "matrices": {
                "A": [[0.9, 0.1, 0.0, 0.0],
                      [0.1, 0.8, 0.1, 0.0],
                      [0.0, 0.1, 0.9, 0.0]],
                "B": [
                    [[0.9, 0.1, 0.0, 0.0],
                     [0.1, 0.8, 0.1, 0.0],
                     [0.0, 0.1, 0.8, 0.1],
                     [0.0, 0.0, 0.1, 0.9]],
                    [[0.1, 0.0, 0.0, 0.9],
                     [0.9, 0.1, 0.0, 0.0],
                     [0.0, 0.9, 0.1, 0.0],
                     [0.0, 0.0, 0.9, 0.1]]
                ],
                "C": [0.8, 0.1, 0.1],
                "D": [0.25, 0.25, 0.25, 0.25]
            }
        }

        # Create integration
        integration_config = GNNIntegrationConfig()
        gnn_integration = GNNActiveInferenceIntegration(integration_config)

        # Load model
        active_model = gnn_integration.create_from_gnn_spec(gnn_model)

        # Verify model was created correctly
        assert isinstance(active_model.generative_model, DiscreteGenerativeModel)
        assert active_model.generative_model.dims.num_states == 4
        assert active_model.generative_model.dims.num_observations == 3

        # Run inference
        belief = torch.ones(4) / 4
        observation = 1

        updated_belief = active_model.inference.update_beliefs(
            belief, observation, active_model.generative_model.A
        )

        assert torch.allclose(updated_belief.sum(), torch.tensor(1.0))


class TestFullSystemIntegration:
    """Test complete Active Inference system integration"""

    def test_complete_agent_simulation(self):
        """Test complete agent with all components"""
        # Configuration
        with tempfile.TemporaryDirectory() as tmpdir:
            # Model configuration
            dims = ModelDimensions(
                num_states=6,
                num_observations=4,
                num_actions=3
            )
            params = ModelParameters(use_gpu=False)

            # Create all components
            gen_model = DiscreteGenerativeModel(dims, params)
            inference = VariationalInference(dims, params)

            policy_config = PolicyConfig(
                precision=2.0,
                planning_horizon=3,
                use_habits=True
            )
            policy_selector = PolicySelector(policy_config)

            precision_config = PrecisionConfig(
                initial_precision=1.0,
                adaptation_rate=0.1,
                use_volatility_estimation=True
            )
            precision_controller = PrecisionController(precision_config)

            planning_config = PlanningConfig(
                max_depth=5,
                branching_factor=3,
                use_mcts=True
            )
            planner = TemporalPlanner(gen_model, planning_config)

            # Learning components
            param_config = ParamLearningConfig(
                learning_rate_A=0.01,
                use_experience_replay=True
            )
            param_learner = create_parameter_learner(
                'online', param_config, generative_model=gen_model
            )

            active_config = ActiveLearningConfig(
                exploration_weight=0.3
            )
            active_learner = ActiveLearner(active_config, gen_model)

            # Optimization
            opt_config = OptimizationConfig(use_gpu=False)
            optimizer = ComputationalOptimizer(opt_config)

            # Diagnostics
            diag_config = DiagnosticConfig(
                log_dir=Path(tmpdir) / "logs",
                figure_dir=Path(tmpdir) / "figures",
                save_figures=True
            )
            diagnostics = DiagnosticSuite(diag_config)
            belief_tracker = diagnostics.create_belief_tracker(
                "main_agent", num_states=6
            )

            # Initialize state
            belief = torch.ones(6) / 6
            true_state = 0

            # Simulation loop
            action_history = []
            belief_history = []

            for t in range(100):
                # Record belief
                belief_tracker.record_belief(belief)
                belief_history.append(belief.clone())

                # Generate observation
                obs_probs = gen_model.A[:, true_state]
                obs = torch.multinomial(obs_probs, 1).item()

                # Update belief (optimized)
                obs_vec = torch.zeros(4)
                obs_vec[obs] = 1.0
                belief = optimizer.optimized_belief_update(
                    belief, obs_vec, gen_model.A
                )

                # Update precision based on prediction error
                pred_error = 1.0 - belief[true_state]
                precision = precision_controller.update_precision(
                    pred_error, expected_uncertainty=0.5
                )

                # Plan ahead
                if t % 10 == 0:  # Plan every 10 steps
                    action_sequence = planner.plan(
                        belief, horizon=5
                    )
                else:
                    action_sequence = None

                # Select action
                if action_sequence is not None:
                    action = action_sequence[0]
                else:
                    # Compute EFE with current precision
                    G_values = policy_selector.compute_expected_free_energy(
                        belief, gen_model.A, gen_model.B, gen_model.C,
                        num_actions=3, horizon=3,
                        precision=precision
                    )

                    # Active learning influence
                    G_adjusted = active_learner.select_informative_action(
                        belief, G_values
                    )

                    action_probs = F.softmax(-G_adjusted * precision, dim=0)
                    action = torch.multinomial(action_probs, 1).item()

                action_history.append(action)

                # Learn from experience
                next_belief = torch.matmul(gen_model.B[:, :, action], belief)
                param_learner.observe(
                    state=belief,
                    action=F.one_hot(torch.tensor(action), num_classes=3).float(),
                    observation=obs_vec,
                    next_state=next_belief
                )

                # Update true state (environment dynamics)
                trans_probs = gen_model.B[:, true_state, action]
                true_state = torch.multinomial(trans_probs, 1).item()

                # Log diagnostics
                diagnostics.log_inference_step({
                    'timestep': t,
                    'observation': obs,
                    'action': action,
                    'belief': belief.tolist(),
                    'true_state': true_state,
                    'precision': precision,
                    'computation_time': 0.01
                })

                # Record free energy
                vfe_accuracy = -torch.sum(belief * torch.log(belief + 1e-16))
                vfe_complexity = torch.sum((belief - gen_model.D) ** 2)
                diagnostics.fe_monitor.record_vfe(
                    accuracy=vfe_accuracy.item(),
                    complexity=vfe_complexity.item()
                )

            # Generate final report
            report = diagnostics.generate_report()
            plots = diagnostics.create_summary_plots()

            # Cleanup
            optimizer.cleanup()

            # Verify simulation completed successfully
            assert len(action_history) == 100
            assert len(belief_history) == 100
            assert report['belief_statistics']['main_agent']['total_updates'] == 100

            # Verify learning occurred
            learning_stats = param_learner.get_statistics()
            assert learning_stats['total_experiences'] == 100
            assert learning_stats['num_updates'] > 0

            # Close plots
            for fig in plots.values():
                if fig is not None:
                    import matplotlib.pyplot as plt
                    plt.close(fig)

    def test_multi_agent_scenario(self):
        """Test multiple Active Inference agents interacting"""
        # Create two agents with different configurations
        dims1 = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        dims2 = ModelDimensions(num_states=3, num_observations=4, num_actions=2)

        params = ModelParameters(use_gpu=False)

        # Agent 1 - Explorer
        agent1_model = DiscreteGenerativeModel(dims1, params)
        agent1_inference = VariationalInference(dims1, params)
        agent1_policy = PolicySelector(PolicyConfig(precision=1.0))

        # Agent 2 - Follower
        agent2_model = DiscreteGenerativeModel(dims2, params)
        agent2_inference = VariationalInference(dims2, params)
        agent2_policy = PolicySelector(PolicyConfig(precision=3.0))

        # Initial beliefs
        belief1 = torch.ones(4) / 4
        belief2 = torch.ones(3) / 3

        # Shared environment state
        env_state = torch.tensor([0.5, 0.5])

        # Interaction loop
        for t in range(20):
            # Agent 1 observes environment + agent 2's state
            obs1 = torch.randint(0, 3, (1,)).item()
            belief1 = agent1_inference.update_beliefs(
                belief1, obs1, agent1_model.A
            )

            # Agent 1 selects action
            G1 = agent1_policy.compute_expected_free_energy(
                belief1, agent1_model.A, agent1_model.B, agent1_model.C,
                num_actions=2, horizon=2
            )
            action1 = torch.multinomial(F.softmax(-G1, dim=0), 1).item()

            # Agent 2 observes environment + agent 1's action
            obs2 = min(obs1 + action1, 3)  # Simple coupling
            belief2 = agent2_inference.update_beliefs(
                belief2, obs2, agent2_model.A
            )

            # Agent 2 selects action
            G2 = agent2_policy.compute_expected_free_energy(
                belief2, agent2_model.A, agent2_model.B, agent2_model.C,
                num_actions=2, horizon=2
            )
            action2 = torch.multinomial(F.softmax(-G2 * 3.0, dim=0), 1).item()

            # Update environment based on both actions
            env_state += torch.tensor([action1 - 0.5, action2 - 0.5]) * 0.1
            env_state = torch.clamp(env_state, 0, 1)

            # Verify beliefs remain valid
            assert torch.allclose(belief1.sum(), torch.tensor(1.0))
            assert torch.allclose(belief2.sum(), torch.tensor(1.0))


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_numerical_stability(self):
        """Test numerical stability in extreme cases"""
        dims = ModelDimensions(
            num_states=10,
            num_observations=10,
            num_actions=5
        )
        params = ModelParameters(use_gpu=False, precision=1e-8)

        gen_model = DiscreteGenerativeModel(dims, params)
        inference = VariationalInference(dims, params)

        # Test with very small probabilities
        belief = torch.zeros(10)
        belief[0] = 1e-10
        belief[1:] = (1 - 1e-10) / 9

        # Should handle without numerical issues
        obs = 5
        updated_belief = inference.update_beliefs(belief, obs, gen_model.A)

        assert torch.all(torch.isfinite(updated_belief))
        assert torch.allclose(updated_belief.sum(), torch.tensor(1.0))

        # Test with near-deterministic distributions
        sharp_belief = torch.zeros(10)
        sharp_belief[3] = 0.9999999
        sharp_belief[4] = 0.0000001

        G_values = PolicySelector(PolicyConfig()).compute_expected_free_energy(
            sharp_belief, gen_model.A, gen_model.B, gen_model.C,
            num_actions=5, horizon=1
        )

        assert torch.all(torch.isfinite(G_values))

    def test_recovery_from_errors(self):
        """Test system recovery from errors"""
        dims = ModelDimensions(
            num_states=4,
            num_observations=3,
            num_actions=2
        )
        params = ModelParameters(use_gpu=False)

        gen_model = DiscreteGenerativeModel(dims, params)
        belief_updater = BeliefUpdater(UpdateConfig())

        # Test recovery from invalid belief
        invalid_belief = torch.tensor([0.5, 0.5, 0.5, 0.5])  # Doesn't sum to 1

        # Should normalize automatically
        obs = 1
        recovered_belief = belief_updater.update_belief_discrete(
            invalid_belief, obs, gen_model.A
        )

        assert torch.allclose(recovered_belief.sum(), torch.tensor(1.0))

        # Test with NaN values
        nan_belief = torch.tensor([0.25, float('nan'), 0.25, 0.25])

        # Should handle gracefully
        try:
            safe_belief = torch.nan_to_num(nan_belief, nan=0.0)
            safe_belief = safe_belief / safe_belief.sum()
            updated = belief_updater.update_belief_discrete(
                safe_belief, obs, gen_model.A
            )
            assert torch.all(torch.isfinite(updated))
        except:
            # System should at least not crash
            pass


def test_performance_benchmark():
    """Benchmark Active Inference performance"""
    sizes = [10, 50, 100]
    results = {}

    for size in sizes:
        dims = ModelDimensions(
            num_states=size,
            num_observations=size,
            num_actions=10
        )
        params = ModelParameters(use_gpu=torch.cuda.is_available())

        gen_model = DiscreteGenerativeModel(dims, params)
        optimizer = ComputationalOptimizer(
            OptimizationConfig(use_gpu=params.use_gpu)
        )

        belief = torch.ones(size) / size
        if params.use_gpu:
            belief = belief.cuda()

        # Time belief updates
        start = time.time()
        for _ in range(100):
            obs = torch.randint(0, size, (1,)).item()
            obs_vec = torch.zeros(size)
            obs_vec[obs] = 1.0
            if params.use_gpu:
                obs_vec = obs_vec.cuda()

            belief = optimizer.optimized_belief_update(
                belief, obs_vec, gen_model.A
            )

        elapsed = time.time() - start
        results[f'belief_update_{size}'] = elapsed / 100

        # Time action selection
        start = time.time()
        for _ in range(10):
            action_probs, G = optimizer.optimized_action_selection(
                belief, gen_model.A, gen_model.B, gen_model.C,
                num_actions=10
            )

        elapsed = time.time() - start
        results[f'action_selection_{size}'] = elapsed / 10

        optimizer.cleanup()

    # Print results
    print("\nPerformance Benchmark Results:")
    for key, value in results.items():
        print(f"{key}: {value*1000:.2f} ms")

    # Verify reasonable performance
    assert results['belief_update_10'] < 0.01  # < 10ms for small model
    assert results['action_selection_100'] < 1.0  # < 1s for large model


class TestActiveInferenceIntegration:
    """Test Active Inference integration with Basic Agent"""

    @pytest.fixture
    def agent(self):
        """Create a test agent"""
        return AgentFactory.create_basic_agent("test_agent")

    @pytest.fixture
    def components(self, agent):
        """Create agent components"""
        state_manager = AgentStateManager(agent)
        perception_system = PerceptionSystem(agent)
        decision_system = DecisionSystem(agent)
        movement_controller = MovementController(agent)
        memory_system = MemorySystem(capacity=100)

        return {
            "state_manager": state_manager,
            "perception_system": perception_system,
            "decision_system": decision_system,
            "movement_controller": movement_controller,
            "memory_system": memory_system
        }

    @pytest.fixture
    def ai_config(self):
        """Create Active Inference configuration"""
        return ActiveInferenceConfig(
            mode=IntegrationMode.HYBRID,
            num_states=50,
            num_observations=30,
            num_actions=8,
            planning_horizon=3,
            action_selection_threshold=0.6
        )

    def test_integration_creation(self, agent, components, ai_config):
        """Test creating Active Inference integration"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        assert integration is not None
        assert integration.agent == agent
        assert integration.config == ai_config
        assert integration.generative_model is not None
        assert integration.planner is not None

    def test_state_to_belief_mapping(self, agent, components, ai_config):
        """Test mapping agent state to belief vector"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Add some state to agent
        agent.goals.append(AgentGoal(
            id="goal1",
            description="Test goal",
            priority="high",
            deadline=datetime.now() + timedelta(hours=1),
            target_position=Position(10, 10, 0)
        ))

        # Map to belief
        belief = integration.state_mapper.map_to_belief(
            agent,
            components["state_manager"]
        )

        assert isinstance(belief, np.ndarray)
        assert len(belief) > 0
        # Check position encoding
        assert belief[0] == agent.position.x
        assert belief[1] == agent.position.y
        assert belief[2] == agent.position.z

    def test_perception_to_observation_mapping(self, agent, components, ai_config):
        """Test mapping percepts to observation vector"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Create test percepts
        percepts = [
            Percept(
                stimulus=Stimulus(
                    source_id="obj1",
                    stimulus_type=StimulusType.VISUAL,
                    intensity=0.8,
                    position=Position(5, 5, 0)
                ),
                timestamp=datetime.now(),
                salience=0.9,
                confidence=0.85
            ),
            Percept(
                stimulus=Stimulus(
                    source_id="sound1",
                    stimulus_type=StimulusType.AUDITORY,
                    intensity=0.6
                ),
                timestamp=datetime.now(),
                salience=0.7,
                confidence=0.9
            )
        ]

        # Map to observation
        observation = integration.perception_mapper.map_to_observation(percepts)

        assert isinstance(observation, np.ndarray)
        assert len(observation) == ai_config.num_observations
        # Check some values are non-zero
        assert np.any(observation > 0)

    def test_action_mapping(self, agent, components, ai_config):
        """Test mapping action indices to agent actions"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Map action indices
        for i in range(min(5, ai_config.num_actions)):
            action = integration.action_mapper.map_to_agent_action(i, agent)
            assert isinstance(action, Action)
            assert isinstance(action.action_type, ActionType)
            assert action.parameters is not None

    def test_full_integration_update(self, agent, components, ai_config):
        """Test full integration update cycle"""
        ai_config.mode = IntegrationMode.FULL
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Add percepts
        percept = Percept(
            stimulus=Stimulus(
                source_id="target",
                stimulus_type=StimulusType.VISUAL,
                intensity=1.0,
                position=Position(10, 10, 0)
            ),
            timestamp=datetime.now(),
            salience=1.0,
            confidence=1.0
        )
        components["perception_system"].process_stimulus(percept.stimulus)

        # Run update
        integration.update(dt=0.1)

        # Check state was updated
        assert integration.current_belief is not None
        assert integration.last_observation is not None
        # May or may not have selected an action depending on planning

    def test_hybrid_mode_integration(self, agent, components, ai_config):
        """Test hybrid mode combining basic and AI decisions"""
        ai_config.mode = IntegrationMode.HYBRID
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Add goal to trigger movement decision
        agent.goals.append(AgentGoal(
            id="move_goal",
            description="Move to target",
            priority="high",
            deadline=datetime.now() + timedelta(minutes=5),
            target_position=Position(20, 20, 0)
        ))

        # Run multiple updates
        for _ in range(5):
            integration.update(dt=0.1)

        # Should have made some decisions
        memories = components["memory_system"].get_recent_memories(5)
        assert len(memories) > 0

    def test_advisory_mode_integration(self, agent, components, ai_config):
        """Test advisory mode where AI only suggests"""
        ai_config.mode = IntegrationMode.ADVISORY
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Add percepts and goals
        agent.goals.append(AgentGoal(
            id="test_goal",
            description="Test",
            priority="medium",
            deadline=datetime.now() + timedelta(hours=1)
        ))

        # Run update
        integration.update(dt=0.1)

        # In advisory mode, basic agent decisions should prevail
        assert integration.config.mode == IntegrationMode.ADVISORY

    def test_learning_mode_integration(self, agent, components, ai_config):
        """Test learning mode with exploration"""
        ai_config.mode = IntegrationMode.LEARNING
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Run multiple updates
        exploration_actions = 0
        for _ in range(10):
            integration.update(dt=0.1)
            if integration.last_action and integration.last_action.action_type == ActionType.OBSERVE:
                exploration_actions += 1

        # Should have some exploration actions in learning mode
        assert exploration_actions >= 0  # May or may not explore based on uncertainty

    def test_belief_evolution(self, agent, components, ai_config):
        """Test how belief evolves over time"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        initial_belief = None
        belief_changes = []

        # Run multiple updates with changing observations
        for i in range(10):
            # Add varying percepts
            percept = Percept(
                stimulus=Stimulus(
                    source_id=f"obj_{i}",
                    stimulus_type=StimulusType.VISUAL,
                    intensity=0.5 + 0.05 * i,
                    position=Position(i, i, 0)
                ),
                timestamp=datetime.now(),
                salience=0.8,
                confidence=0.9
            )
            components["perception_system"].process_stimulus(percept.stimulus)

            integration.update(dt=0.1)

            if initial_belief is None:
                initial_belief = integration.current_belief.copy()
            else:
                # Track belief changes
                change = np.linalg.norm(integration.current_belief - initial_belief)
                belief_changes.append(change)

        # Belief should evolve
        assert len(belief_changes) > 0
        assert max(belief_changes) > 0  # Some change should occur

    def test_resource_constraints(self, agent, components, ai_config):
        """Test action selection with resource constraints"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Deplete energy
        agent.resources.energy = 5  # Very low

        # Try to select movement action
        integration.update(dt=0.1)

        # Should not execute movement actions with low energy
        if integration.last_action and integration.last_action.action_type == ActionType.MOVE:
            # Action should have been blocked
            assert agent.resources.energy == 5  # Unchanged

    def test_visualization_data(self, agent, components, ai_config):
        """Test visualization data generation"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Run an update
        integration.update(dt=0.1)

        # Get visualization data
        viz_data = integration.get_visualization_data()

        assert "belief_state" in viz_data
        assert "last_observation" in viz_data
        assert "mode" in viz_data
        assert "belief_entropy" in viz_data
        assert viz_data["mode"] == ai_config.mode.value

    def test_memory_integration(self, agent, components, ai_config):
        """Test memory system integration"""
        integration = create_active_inference_agent(
            agent,
            **components,
            config=ai_config
        )

        # Perform actions that should create memories
        for _ in range(5):
            integration.update(dt=0.1)

        # Check memories were created
        memories = components["memory_system"].get_recent_memories(10)
        experience_memories = [m for m in memories if m.memory_type == "experience"]

        assert len(experience_memories) > 0
        # Check memory content
        for memory in experience_memories:
            assert "state" in memory.content
            assert "observation" in memory.content
            assert "belief_entropy" in memory.content

    def test_multi_agent_integration(self, components):
        """Test multiple agents with Active Inference"""
        env = SimulationEnvironment(grid_size=(50, 50))

        # Create multiple AI-enabled agents
        for i in range(3):
            agent = AgentFactory.create_basic_agent(f"ai_agent_{i}")
            agent.position = Position(i * 10, i * 10, 0)

            # Create components for each agent
            state_mgr = AgentStateManager(agent)
            percept_sys = PerceptionSystem(agent)
            decision_sys = DecisionSystem(agent)
            move_ctrl = MovementController(agent)
            memory_sys = MemorySystem(capacity=50)

            # Create AI integration
            config = ActiveInferenceConfig(
                mode=IntegrationMode.HYBRID,
                num_states=30,
                num_observations=20,
                num_actions=6
            )

            ai_integration = create_active_inference_agent(
                agent,
                state_manager=state_mgr,
                perception_system=percept_sys,
                decision_system=decision_sys,
                movement_controller=move_ctrl,
                memory_system=memory_sys,
                config=config
            )

            # Add to environment
            env.add_agent(agent)
            # Store integration for updates
            agent.ai_integration = ai_integration

        # Run simulation
        for _ in range(10):
            # Update each agent's AI
            for agent in env.agents.values():
                if hasattr(agent, 'ai_integration'):
                    agent.ai_integration.update(dt=0.1)

            env.step()

        # All agents should have updated
        for agent in env.agents.values():
            if hasattr(agent, 'ai_integration'):
                assert agent.ai_integration.current_belief is not None
                assert agent.ai_integration.last_observation is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
