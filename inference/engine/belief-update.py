"""
Belief Updating with GNN Features

This module implements belief updating mechanisms that incorporate
GNN-extracted features into the Active Inference framework.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass, field
import numpy as np
import logging
from abc import ABC, abstractmethod

from .generative_model import GenerativeModel, DiscreteGenerativeModel, ContinuousGenerativeModel
from .inference import InferenceAlgorithm, VariationalMessagePassing, BeliefPropagation
from .gnn_integration import GNNActiveInferenceAdapter, GraphFeatureAggregator

logger = logging.getLogger(__name__)


@dataclass
class BeliefUpdateConfig:
    """Configuration for belief updating with GNN features"""
    # Update parameters
    update_method: str = 'bayesian'  # 'bayesian', 'gradient', 'hybrid'
    learning_rate: float = 0.01
    momentum: float = 0.9

    # Integration parameters
    feature_weighting: str = 'learned'  # 'uniform', 'learned', 'attention'
    temporal_integration: bool = True
    use_graph_priors: bool = True

    # Normalization
    normalize_features: bool = True
    feature_scale: float = 1.0

    # Computational
    use_gpu: bool = True
    dtype: torch.dtype = torch.float32
    eps: float = 1e-16


class GraphObservationModel(ABC):
    """Abstract base class for models that convert graph features to observations"""

    def __init__(self, config: BeliefUpdateConfig):
        self.config = config
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

    @abstractmethod
    def compute_likelihood(self, graph_features: torch.Tensor,
                         states: torch.Tensor) -> torch.Tensor:
        """Compute likelihood P(graph_features | states)"""
        pass

    @abstractmethod
    def generate_observations(self, graph_features: torch.Tensor) -> torch.Tensor:
        """Generate observations from graph features"""
        pass


class DirectGraphObservationModel(GraphObservationModel):
    """
    Direct observation model that treats graph features as noisy observations.
    """

    def __init__(self, config: BeliefUpdateConfig,
                 state_dim: int,
                 feature_dim: int):
        super().__init__(config)
        self.state_dim = state_dim
        self.feature_dim = feature_dim

        # Observation matrix mapping states to expected features
        self.observation_matrix = nn.Parameter(
            torch.randn(feature_dim, state_dim, device=self.device) * 0.1
        )

        # Observation noise (precision)
        self.log_precision = nn.Parameter(
            torch.zeros(feature_dim, device=self.device)
        )

    def compute_likelihood(self, graph_features: torch.Tensor,
                         states: torch.Tensor) -> torch.Tensor:
        """
        Compute Gaussian likelihood of graph features given states.

        Args:
            graph_features: Graph features [batch_size x feature_dim]
            states: State beliefs [batch_size x state_dim]

        Returns:
            Log-likelihood [batch_size]
        """
        # Expected features given states
        expected_features = states @ self.observation_matrix.T

        # Precision (inverse variance)
        precision = torch.exp(self.log_precision)

        # Gaussian log-likelihood
        diff = graph_features - expected_features
        log_likelihood = -0.5 * torch.sum(
            precision * diff ** 2, dim=-1
        ) - 0.5 * torch.sum(torch.log(2 * np.pi / precision))

        return log_likelihood

    def generate_observations(self, graph_features: torch.Tensor) -> torch.Tensor:
        """Direct pass-through with optional normalization"""
        if self.config.normalize_features:
            return F.normalize(graph_features, dim=-1) * self.config.feature_scale
        return graph_features


class LearnedGraphObservationModel(GraphObservationModel):
    """
    Learned observation model with neural network mapping.
    """

    def __init__(self, config: BeliefUpdateConfig,
                 state_dim: int,
                 feature_dim: int,
                 hidden_dim: int = 64):
        super().__init__(config)
        self.state_dim = state_dim
        self.feature_dim = feature_dim

        # Feature encoder
        self.feature_encoder = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        ).to(self.device)

        # State encoder
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        ).to(self.device)

        # Likelihood network
        self.likelihood_net = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, 1)
        ).to(self.device)

        # Observation decoder
        self.observation_decoder = nn.Sequential(
            nn.Linear(feature_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim, state_dim)
        ).to(self.device)

    def compute_likelihood(self, graph_features: torch.Tensor,
                         states: torch.Tensor) -> torch.Tensor:
        """Compute learned likelihood using neural networks"""
        # Encode features and states
        feature_encoding = self.feature_encoder(graph_features)
        state_encoding = self.state_encoder(states)

        # Concatenate and compute likelihood
        combined = torch.cat([feature_encoding, state_encoding], dim=-1)
        log_likelihood = self.likelihood_net(combined).squeeze(-1)

        return log_likelihood

    def generate_observations(self, graph_features: torch.Tensor) -> torch.Tensor:
        """Generate observations using learned decoder"""
        return self.observation_decoder(graph_features)


class GNNBeliefUpdater:
    """
    Main class for updating beliefs using GNN features.

    Integrates graph neural network outputs with Active Inference
    belief updating mechanisms.
    """

    def __init__(self, config: BeliefUpdateConfig,
                 generative_model: GenerativeModel,
                 inference_algorithm: InferenceAlgorithm,
                 observation_model: GraphObservationModel):
        self.config = config
        self.generative_model = generative_model
        self.inference = inference_algorithm
        self.observation_model = observation_model
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

        # Feature weighting
        if config.feature_weighting == 'learned':
            self.feature_weights = nn.Parameter(
                torch.ones(1, device=self.device)
            )
        elif config.feature_weighting == 'attention':
            self.attention_net = nn.Sequential(
                nn.Linear(observation_model.feature_dim, 64),
                nn.Tanh(),
                nn.Linear(64, 1)
            ).to(self.device)

        # Temporal integration
        if config.temporal_integration:
            self.temporal_decay = nn.Parameter(
                torch.tensor(0.9, device=self.device)
            )

    def update_beliefs(self, current_beliefs: torch.Tensor,
                      graph_features: torch.Tensor,
                      actions: Optional[torch.Tensor] = None,
                      previous_beliefs: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Update beliefs incorporating GNN features.

        Args:
            current_beliefs: Current belief states [batch_size x state_dim]
            graph_features: GNN-extracted features [batch_size x feature_dim]
            actions: Optional actions taken [batch_size x action_dim]
            previous_beliefs: Optional previous beliefs for temporal integration

        Returns:
            Updated beliefs [batch_size x state_dim]
        """
        if self.config.update_method == 'bayesian':
            return self._bayesian_update(current_beliefs, graph_features, actions)
        elif self.config.update_method == 'gradient':
            return self._gradient_update(current_beliefs, graph_features, actions)
        elif self.config.update_method == 'hybrid':
            return self._hybrid_update(current_beliefs, graph_features, actions, previous_beliefs)
        else:
            raise ValueError(f"Unknown update method: {self.config.update_method}")

    def _bayesian_update(self, current_beliefs: torch.Tensor,
                        graph_features: torch.Tensor,
                        actions: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Bayesian belief update using graph features as observations.
        """
        # Generate observations from graph features
        observations = self.observation_model.generate_observations(graph_features)

        # Compute likelihood for discrete states
        if isinstance(self.generative_model, DiscreteGenerativeModel):
            # Get observation likelihood matrix
            A_matrix = self.generative_model.A

            # If we have continuous observations, discretize them
            if observations.dtype == torch.float32:
                # Simple discretization - could be more sophisticated
                obs_indices = torch.argmax(observations, dim=-1)
                likelihood = A_matrix[obs_indices]
            else:
                likelihood = A_matrix[observations]

            # Apply feature weighting if learned
            if self.config.feature_weighting == 'learned':
                likelihood = likelihood ** self.feature_weights

            # Bayesian update: posterior ∝ likelihood × prior
            posterior = likelihood * current_beliefs.unsqueeze(1)
            posterior = posterior / (posterior.sum(dim=-1, keepdim=True) + self.config.eps)

            return posterior.squeeze(1)
        else:
            # For continuous states, use the inference algorithm
            return self.inference.infer_states(observations, self.generative_model, current_beliefs)

    def _gradient_update(self, current_beliefs: torch.Tensor,
                        graph_features: torch.Tensor,
                        actions: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Gradient-based belief update to maximize likelihood.
        """
        beliefs = current_beliefs.clone().requires_grad_(True)

        # Compute log-likelihood
        log_likelihood = self.observation_model.compute_likelihood(graph_features, beliefs)

        # Compute gradient
        grad = torch.autograd.grad(log_likelihood.sum(), beliefs)[0]

        # Gradient ascent update
        updated_beliefs = beliefs + self.config.learning_rate * grad

        # Normalize for valid probability distribution
        if isinstance(self.generative_model, DiscreteGenerativeModel):
            updated_beliefs = F.softmax(updated_beliefs, dim=-1)
        else:
            # For continuous states, ensure beliefs stay in valid range
            updated_beliefs = torch.clamp(updated_beliefs, -10, 10)

        return updated_beliefs.detach()

    def _hybrid_update(self, current_beliefs: torch.Tensor,
                      graph_features: torch.Tensor,
                      actions: Optional[torch.Tensor] = None,
                      previous_beliefs: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Hybrid update combining Bayesian and gradient approaches with temporal integration.
        """
        # Bayesian update
        bayesian_beliefs = self._bayesian_update(current_beliefs, graph_features, actions)

        # Gradient update
        gradient_beliefs = self._gradient_update(current_beliefs, graph_features, actions)

        # Combine updates
        alpha = 0.7  # Weight for Bayesian update
        combined_beliefs = alpha * bayesian_beliefs + (1 - alpha) * gradient_beliefs

        # Temporal integration if available
        if self.config.temporal_integration and previous_beliefs is not None:
            decay = torch.sigmoid(self.temporal_decay)
            combined_beliefs = decay * combined_beliefs + (1 - decay) * previous_beliefs

        # Normalize
        if isinstance(self.generative_model, DiscreteGenerativeModel):
            combined_beliefs = combined_beliefs / (combined_beliefs.sum(dim=-1, keepdim=True) + self.config.eps)

        return combined_beliefs

    def update_with_graph_sequence(self, initial_beliefs: torch.Tensor,
                                 graph_sequence: List[Dict[str, torch.Tensor]],
                                 actions: Optional[List[torch.Tensor]] = None) -> List[torch.Tensor]:
        """
        Update beliefs through a sequence of graph observations.

        Args:
            initial_beliefs: Initial belief state
            graph_sequence: Sequence of graph data dictionaries
            actions: Optional sequence of actions

        Returns:
            Sequence of updated beliefs
        """
        beliefs = initial_beliefs
        belief_trajectory = [beliefs]
        previous_beliefs = None

        for t, graph_data in enumerate(graph_sequence):
            # Extract features from graph
            if 'graph_features' in graph_data:
                features = graph_data['graph_features']
            else:
                # Aggregate node features if needed
                aggregator = GraphFeatureAggregator(self.config)
                features = aggregator.aggregate_single(graph_data['node_features'])

            # Get action if available
            action = actions[t] if actions is not None else None

            # Update beliefs
            beliefs = self.update_beliefs(beliefs, features, action, previous_beliefs)
            belief_trajectory.append(beliefs)

            # Store for temporal integration
            previous_beliefs = beliefs

        return belief_trajectory


class AttentionGraphBeliefUpdater(GNNBeliefUpdater):
    """
    Attention-based belief updater that learns to focus on relevant graph features.
    """

    def __init__(self, config: BeliefUpdateConfig,
                 generative_model: GenerativeModel,
                 inference_algorithm: InferenceAlgorithm,
                 observation_model: GraphObservationModel,
                 num_heads: int = 4):
        super().__init__(config, generative_model, inference_algorithm, observation_model)

        self.num_heads = num_heads
        state_dim = generative_model.dims.num_states
        feature_dim = observation_model.feature_dim

        # Multi-head attention for feature selection
        self.attention = nn.MultiheadAttention(
            embed_dim=feature_dim,
            num_heads=num_heads,
            dropout=0.1
        ).to(self.device)

        # Query generation from beliefs
        self.query_net = nn.Linear(state_dim, feature_dim).to(self.device)

    def _compute_attended_features(self, beliefs: torch.Tensor,
                                 graph_features: torch.Tensor) -> torch.Tensor:
        """
        Compute attention-weighted graph features based on current beliefs.

        Args:
            beliefs: Current beliefs [batch_size x state_dim]
            graph_features: Graph features [batch_size x seq_len x feature_dim]

        Returns:
            Attended features [batch_size x feature_dim]
        """
        # Generate queries from beliefs
        queries = self.query_net(beliefs).unsqueeze(0)  # [1 x batch_size x feature_dim]

        # Reshape features for attention
        if graph_features.dim() == 2:
            graph_features = graph_features.unsqueeze(1)  # Add sequence dimension

        keys = values = graph_features.transpose(0, 1)  # [seq_len x batch_size x feature_dim]

        # Apply attention
        attended_features, attention_weights = self.attention(queries, keys, values)

        return attended_features.squeeze(0), attention_weights

    def update_beliefs(self, current_beliefs: torch.Tensor,
                      graph_features: torch.Tensor,
                      actions: Optional[torch.Tensor] = None,
                      previous_beliefs: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Update beliefs using attention-weighted graph features.
        """
        # Compute attended features
        attended_features, _ = self._compute_attended_features(current_beliefs, graph_features)

        # Use attended features for update
        return super().update_beliefs(current_beliefs, attended_features, actions, previous_beliefs)


class HierarchicalBeliefUpdater:
    """
    Hierarchical belief updater for multi-scale graph processing.
    """

    def __init__(self, config: BeliefUpdateConfig,
                 level_updaters: List[GNNBeliefUpdater]):
        self.config = config
        self.level_updaters = level_updaters
        self.num_levels = len(level_updaters)
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

        # Inter-level coupling
        self.bottom_up_nets = nn.ModuleList([
            nn.Linear(
                level_updaters[i].generative_model.dims.num_states,
                level_updaters[i+1].generative_model.dims.num_states
            ).to(self.device)
            for i in range(self.num_levels - 1)
        ])

        self.top_down_nets = nn.ModuleList([
            nn.Linear(
                level_updaters[i+1].generative_model.dims.num_states,
                level_updaters[i].generative_model.dims.num_states
            ).to(self.device)
            for i in range(self.num_levels - 1)
        ])

    def update_hierarchical_beliefs(self,
                                  current_beliefs: List[torch.Tensor],
                                  graph_features_per_level: List[torch.Tensor],
                                  actions_per_level: Optional[List[torch.Tensor]] = None) -> List[torch.Tensor]:
        """
        Update beliefs hierarchically with bottom-up and top-down passes.

        Args:
            current_beliefs: Current beliefs at each level
            graph_features_per_level: Graph features at each level
            actions_per_level: Optional actions at each level

        Returns:
            Updated beliefs at each level
        """
        updated_beliefs = current_beliefs.copy()

        # Bottom-up pass
        for level in range(self.num_levels):
            # Get features and actions for this level
            features = graph_features_per_level[level]
            actions = actions_per_level[level] if actions_per_level else None

            # Add bottom-up influence if not at bottom level
            if level > 0:
                bottom_up_prior = self.bottom_up_nets[level-1](updated_beliefs[level-1])
                bottom_up_prior = F.softmax(bottom_up_prior, dim=-1)
                # Combine with current beliefs
                current_beliefs[level] = 0.7 * current_beliefs[level] + 0.3 * bottom_up_prior

            # Update beliefs at this level
            updated_beliefs[level] = self.level_updaters[level].update_beliefs(
                current_beliefs[level], features, actions
            )

        # Top-down pass
        for level in range(self.num_levels - 2, -1, -1):
            # Add top-down influence
            top_down_prior = self.top_down_nets[level](updated_beliefs[level+1])
            top_down_prior = F.softmax(top_down_prior, dim=-1)

            # Refine beliefs with top-down information
            updated_beliefs[level] = 0.8 * updated_beliefs[level] + 0.2 * top_down_prior

            # Normalize
            if isinstance(self.level_updaters[level].generative_model, DiscreteGenerativeModel):
                updated_beliefs[level] = updated_beliefs[level] / (
                    updated_beliefs[level].sum(dim=-1, keepdim=True) + self.config.eps
                )

        return updated_beliefs


def create_belief_updater(updater_type: str,
                         config: Optional[BeliefUpdateConfig] = None,
                         **kwargs) -> Union[GNNBeliefUpdater, AttentionGraphBeliefUpdater, HierarchicalBeliefUpdater]:
    """
    Factory function to create belief updaters.

    Args:
        updater_type: Type of updater ('standard', 'attention', 'hierarchical')
        config: Configuration for the updater
        **kwargs: Additional arguments for specific updater types

    Returns:
        Belief updater instance
    """
    if config is None:
        config = BeliefUpdateConfig()

    if updater_type == 'standard':
        generative_model = kwargs.get('generative_model')
        inference_algorithm = kwargs.get('inference_algorithm')
        observation_model = kwargs.get('observation_model')

        if None in [generative_model, inference_algorithm, observation_model]:
            raise ValueError("Standard updater requires generative_model, inference_algorithm, and observation_model")

        return GNNBeliefUpdater(config, generative_model, inference_algorithm, observation_model)

    elif updater_type == 'attention':
        generative_model = kwargs.get('generative_model')
        inference_algorithm = kwargs.get('inference_algorithm')
        observation_model = kwargs.get('observation_model')
        num_heads = kwargs.get('num_heads', 4)

        if None in [generative_model, inference_algorithm, observation_model]:
            raise ValueError("Attention updater requires generative_model, inference_algorithm, and observation_model")

        return AttentionGraphBeliefUpdater(
            config, generative_model, inference_algorithm, observation_model, num_heads
        )

    elif updater_type == 'hierarchical':
        level_updaters = kwargs.get('level_updaters', [])
        if not level_updaters:
            raise ValueError("Hierarchical updater requires level_updaters")

        return HierarchicalBeliefUpdater(config, level_updaters)

    else:
        raise ValueError(f"Unknown updater type: {updater_type}")


# Example usage
if __name__ == "__main__":
    from .generative_model import DiscreteGenerativeModel, ModelDimensions, ModelParameters
    from .inference import VariationalMessagePassing, InferenceConfig

    # Configuration
    config = BeliefUpdateConfig(
        update_method='hybrid',
        feature_weighting='learned',
        temporal_integration=True,
        use_gpu=False
    )

    # Create generative model
    dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
    params = ModelParameters(use_gpu=False)
    gen_model = DiscreteGenerativeModel(dims, params)

    # Create inference algorithm
    inf_config = InferenceConfig(use_gpu=False)
    inference = VariationalMessagePassing(inf_config)

    # Create observation model
    obs_model = DirectGraphObservationModel(config, state_dim=4, feature_dim=16)

    # Create belief updater
    updater = GNNBeliefUpdater(config, gen_model, inference, obs_model)

    # Example update
    current_beliefs = torch.softmax(torch.randn(2, 4), dim=-1)
    graph_features = torch.randn(2, 16)

    updated_beliefs = updater.update_beliefs(current_beliefs, graph_features)
    print(f"Updated beliefs shape: {updated_beliefs.shape}")
    print(f"Updated beliefs: {updated_beliefs}")
