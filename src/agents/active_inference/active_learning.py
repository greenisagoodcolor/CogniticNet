"""
Active Learning for Active Inference

This module implements active learning mechanisms that enable agents
to actively seek information to reduce uncertainty and improve their models.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, field
import numpy as np
import logging
from abc import ABC, abstractmethod
from enum import Enum

from .generative_model import GenerativeModel, DiscreteGenerativeModel
from .inference import InferenceAlgorithm
from .policy_selection import PolicySelector, Policy
from .precision import PrecisionOptimizer

logger = logging.getLogger(__name__)


class InformationMetric(Enum):
    """Types of information metrics for active learning"""
    ENTROPY = "entropy"
    MUTUAL_INFORMATION = "mutual_information"
    EXPECTED_INFORMATION_GAIN = "expected_information_gain"
    BAYESIAN_SURPRISE = "bayesian_surprise"
    PREDICTION_ERROR = "prediction_error"


@dataclass
class ActiveLearningConfig:
    """Configuration for active learning"""
    # Information seeking parameters
    exploration_weight: float = 0.3
    information_metric: InformationMetric = InformationMetric.EXPECTED_INFORMATION_GAIN
    min_uncertainty_threshold: float = 0.1
    max_uncertainty_threshold: float = 0.9

    # Exploration strategies
    curiosity_decay: float = 0.99
    novelty_weight: float = 0.2
    diversity_weight: float = 0.1

    # Planning parameters
    planning_horizon: int = 5
    num_samples: int = 100

    # Computational
    use_gpu: bool = True
    dtype: torch.dtype = torch.float32
    eps: float = 1e-16


class InformationSeeker(ABC):
    """Abstract base class for information seeking strategies"""

    def __init__(self, config: ActiveLearningConfig):
        self.config = config
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

    @abstractmethod
    def compute_information_value(self, beliefs: torch.Tensor,
                                possible_observations: torch.Tensor) -> torch.Tensor:
        """Compute the value of potential observations for reducing uncertainty"""
        pass

    @abstractmethod
    def select_informative_action(self, beliefs: torch.Tensor,
                                available_actions: torch.Tensor) -> torch.Tensor:
        """Select action that maximizes information gain"""
        pass


class EntropyBasedSeeker(InformationSeeker):
    """
    Information seeker based on entropy reduction.

    Seeks observations that would maximally reduce belief entropy.
    """

    def __init__(self, config: ActiveLearningConfig,
                 generative_model: GenerativeModel):
        super().__init__(config)
        self.generative_model = generative_model

    def compute_entropy(self, beliefs: torch.Tensor) -> torch.Tensor:
        """Compute Shannon entropy of beliefs"""
        # Add small epsilon to avoid log(0)
        safe_beliefs = beliefs + self.config.eps
        entropy = -torch.sum(safe_beliefs * torch.log(safe_beliefs), dim=-1)
        return entropy

    def compute_information_value(self, beliefs: torch.Tensor,
                                possible_observations: torch.Tensor) -> torch.Tensor:
        """
        Compute expected entropy reduction for each possible observation.

        Args:
            beliefs: Current belief states [batch_size x num_states]
            possible_observations: Potential observations [num_obs x obs_dim]

        Returns:
            Information value for each observation [num_obs]
        """
        batch_size = beliefs.shape[0]
        num_obs = possible_observations.shape[0]

        # Current entropy
        current_entropy = self.compute_entropy(beliefs)

        # Expected entropy after each observation
        expected_entropies = torch.zeros(num_obs, device=self.device)

        if isinstance(self.generative_model, DiscreteGenerativeModel):
            # For discrete models, use observation likelihood matrix
            A_matrix = self.generative_model.A

            for i in range(num_obs):
                # Compute posterior for this observation
                likelihood = A_matrix[i]  # P(o|s)
                posterior = likelihood * beliefs
                posterior = posterior / (posterior.sum(dim=-1, keepdim=True) + self.config.eps)

                # Compute entropy of posterior
                posterior_entropy = self.compute_entropy(posterior)
                expected_entropies[i] = posterior_entropy.mean()
        else:
            # For continuous models, approximate with sampling
            for i in range(num_obs):
                # This is simplified - real implementation would use proper likelihood
                posterior_entropy = current_entropy * 0.8  # Placeholder
                expected_entropies[i] = posterior_entropy.mean()

        # Information value is entropy reduction
        info_values = current_entropy.mean() - expected_entropies

        return info_values

    def select_informative_action(self, beliefs: torch.Tensor,
                                available_actions: torch.Tensor) -> torch.Tensor:
        """
        Select action that leads to most informative observations.

        Args:
            beliefs: Current beliefs [batch_size x num_states]
            available_actions: Available actions [num_actions x action_dim]

        Returns:
            Selected action index
        """
        if isinstance(self.generative_model, DiscreteGenerativeModel):
            # Use transition matrix to predict future states
            B_matrix = self.generative_model.B
            num_actions = available_actions.shape[0]

            expected_info_gains = torch.zeros(num_actions, device=self.device)

            for a in range(num_actions):
                # Predict next state distribution
                next_beliefs = torch.matmul(beliefs, B_matrix[:, :, a].T)

                # Compute expected entropy
                expected_entropy = self.compute_entropy(next_beliefs)
                expected_info_gains[a] = beliefs.shape[0] - expected_entropy.mean()

            # Select action with highest expected information gain
            best_action = torch.argmax(expected_info_gains)

            return best_action
        else:
            # For continuous models, return random exploration
            return torch.randint(0, available_actions.shape[0], (1,))[0]


class MutualInformationSeeker(InformationSeeker):
    """
    Information seeker based on mutual information.

    Maximizes mutual information between beliefs and observations.
    """

    def __init__(self, config: ActiveLearningConfig,
                 generative_model: GenerativeModel,
                 inference_algorithm: InferenceAlgorithm):
        super().__init__(config)
        self.generative_model = generative_model
        self.inference = inference_algorithm

    def compute_mutual_information(self, beliefs: torch.Tensor,
                                 observation_dist: torch.Tensor) -> torch.Tensor:
        """
        Compute mutual information I(S;O) = H(S) - H(S|O)

        Args:
            beliefs: Belief distribution over states
            observation_dist: Distribution over observations

        Returns:
            Mutual information value
        """
        # Entropy of beliefs H(S)
        belief_entropy = -torch.sum(beliefs * torch.log(beliefs + self.config.eps), dim=-1)

        # Conditional entropy H(S|O)
        if isinstance(self.generative_model, DiscreteGenerativeModel):
            A_matrix = self.generative_model.A

            # Joint distribution P(s,o) = P(o|s)P(s)
            joint = A_matrix.unsqueeze(0) * beliefs.unsqueeze(1).unsqueeze(2)

            # Marginal P(o)
            marginal_obs = joint.sum(dim=2)

            # Conditional entropy
            conditional_entropy = -torch.sum(
                joint * torch.log(joint / (marginal_obs.unsqueeze(2) + self.config.eps) + self.config.eps)
            ).mean()
        else:
            # Approximate for continuous case
            conditional_entropy = belief_entropy * 0.7  # Placeholder

        mutual_info = belief_entropy.mean() - conditional_entropy

        return mutual_info

    def compute_information_value(self, beliefs: torch.Tensor,
                                possible_observations: torch.Tensor) -> torch.Tensor:
        """Compute information value based on mutual information"""
        num_obs = possible_observations.shape[0]
        info_values = torch.zeros(num_obs, device=self.device)

        for i in range(num_obs):
            # Create observation distribution (one-hot for specific observation)
            obs_dist = torch.zeros(num_obs, device=self.device)
            obs_dist[i] = 1.0

            info_values[i] = self.compute_mutual_information(beliefs, obs_dist)

        return info_values

    def select_informative_action(self, beliefs: torch.Tensor,
                                available_actions: torch.Tensor) -> torch.Tensor:
        """Select action that maximizes mutual information"""
        num_actions = available_actions.shape[0]
        expected_mi = torch.zeros(num_actions, device=self.device)

        if isinstance(self.generative_model, DiscreteGenerativeModel):
            B_matrix = self.generative_model.B
            A_matrix = self.generative_model.A

            for a in range(num_actions):
                # Predict next beliefs
                next_beliefs = torch.matmul(beliefs, B_matrix[:, :, a].T)

                # Expected observations from next state
                expected_obs_dist = torch.matmul(next_beliefs, A_matrix.sum(dim=0).T)
                expected_obs_dist = expected_obs_dist / expected_obs_dist.sum()

                # Compute mutual information
                expected_mi[a] = self.compute_mutual_information(next_beliefs, expected_obs_dist)

        return torch.argmax(expected_mi)


class ActiveLearningAgent:
    """
    Main active learning agent that combines information seeking with action selection.

    Balances exploration for information gain with exploitation for reward.
    """

    def __init__(self, config: ActiveLearningConfig,
                 generative_model: GenerativeModel,
                 inference_algorithm: InferenceAlgorithm,
                 policy_selector: PolicySelector,
                 information_seeker: Optional[InformationSeeker] = None):
        self.config = config
        self.generative_model = generative_model
        self.inference = inference_algorithm
        self.policy_selector = policy_selector
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

        # Initialize information seeker
        if information_seeker is None:
            if config.information_metric == InformationMetric.ENTROPY:
                self.info_seeker = EntropyBasedSeeker(config, generative_model)
            else:
                self.info_seeker = MutualInformationSeeker(config, generative_model, inference_algorithm)
        else:
            self.info_seeker = information_seeker

        # Exploration state
        self.exploration_rate = config.exploration_weight
        self.novelty_memory = []
        self.visit_counts = {}

    def compute_epistemic_value(self, beliefs: torch.Tensor,
                              policies: List[Policy]) -> torch.Tensor:
        """
        Compute epistemic value (information gain) for each policy.

        Args:
            beliefs: Current beliefs
            policies: List of possible policies

        Returns:
            Epistemic values for each policy
        """
        num_policies = len(policies)
        epistemic_values = torch.zeros(num_policies, device=self.device)

        for i, policy in enumerate(policies):
            # Simulate policy execution
            predicted_observations = self._simulate_policy_observations(beliefs, policy)

            # Compute expected information gain
            info_gains = self.info_seeker.compute_information_value(beliefs, predicted_observations)
            epistemic_values[i] = info_gains.mean()

        return epistemic_values

    def compute_pragmatic_value(self, beliefs: torch.Tensor,
                              policies: List[Policy],
                              preferences: Optional[torch.Tensor] = None) -> torch.Tensor:
        """
        Compute pragmatic value (expected utility) for each policy.

        Args:
            beliefs: Current beliefs
            policies: List of possible policies
            preferences: Optional preferences over outcomes

        Returns:
            Pragmatic values for each policy
        """
        # Use policy selector to compute expected free energy
        pragmatic_values = []

        for policy in policies:
            G = self.policy_selector.compute_expected_free_energy(
                policy, beliefs, self.generative_model, preferences
            )
            pragmatic_values.append(-G)  # Negative because we minimize free energy

        return torch.stack(pragmatic_values)

    def select_exploratory_action(self, beliefs: torch.Tensor,
                                available_actions: torch.Tensor,
                                preferences: Optional[torch.Tensor] = None) -> Tuple[int, Dict[str, float]]:
        """
        Select action balancing exploration and exploitation.

        Args:
            beliefs: Current beliefs
            available_actions: Available actions
            preferences: Optional preferences

        Returns:
            Selected action index and info dict
        """
        # Generate candidate policies
        policies = self._generate_policies(available_actions)

        # Compute epistemic value (exploration)
        epistemic_values = self.compute_epistemic_value(beliefs, policies)

        # Compute pragmatic value (exploitation)
        pragmatic_values = self.compute_pragmatic_value(beliefs, policies, preferences)

        # Compute novelty bonus
        novelty_values = self._compute_novelty_bonus(beliefs, policies)

        # Combine values
        total_values = (
            self.exploration_rate * epistemic_values +
            (1 - self.exploration_rate) * pragmatic_values +
            self.config.novelty_weight * novelty_values
        )

        # Select best policy
        best_policy_idx = torch.argmax(total_values)
        best_policy = policies[best_policy_idx]

        # Get first action from policy
        selected_action = best_policy.actions[0] if len(best_policy.actions) > 0 else 0

        # Update exploration rate
        self.exploration_rate *= self.config.curiosity_decay

        # Return info for monitoring
        info = {
            'epistemic_value': epistemic_values[best_policy_idx].item(),
            'pragmatic_value': pragmatic_values[best_policy_idx].item(),
            'novelty_value': novelty_values[best_policy_idx].item(),
            'exploration_rate': self.exploration_rate
        }

        return selected_action, info

    def _simulate_policy_observations(self, beliefs: torch.Tensor,
                                    policy: Policy) -> torch.Tensor:
        """Simulate expected observations from executing a policy"""
        current_beliefs = beliefs.clone()
        observations = []

        if isinstance(self.generative_model, DiscreteGenerativeModel):
            B_matrix = self.generative_model.B
            A_matrix = self.generative_model.A

            for action in policy.actions[:self.config.planning_horizon]:
                # Transition beliefs
                next_beliefs = torch.matmul(current_beliefs, B_matrix[:, :, action].T)

                # Expected observations
                expected_obs = torch.matmul(next_beliefs, A_matrix.sum(dim=0).T)
                observations.append(expected_obs)

                current_beliefs = next_beliefs

        if observations:
            return torch.stack(observations)
        else:
            return torch.zeros(1, self.generative_model.dims.num_observations, device=self.device)

    def _generate_policies(self, available_actions: torch.Tensor) -> List[Policy]:
        """Generate candidate policies for evaluation"""
        policies = []
        num_actions = available_actions.shape[0]

        # Random policies
        for _ in range(self.config.num_samples):
            actions = torch.randint(0, num_actions, (self.config.planning_horizon,))
            policy = Policy(
                actions=actions.tolist(),
                horizon=self.config.planning_horizon
            )
            policies.append(policy)

        return policies

    def _compute_novelty_bonus(self, beliefs: torch.Tensor,
                             policies: List[Policy]) -> torch.Tensor:
        """Compute novelty bonus for each policy based on state visitation"""
        novelty_values = torch.zeros(len(policies), device=self.device)

        for i, policy in enumerate(policies):
            # Simple novelty: inverse of visitation count
            state_hash = self._hash_belief_state(beliefs)
            visit_count = self.visit_counts.get(state_hash, 0)
            novelty_values[i] = 1.0 / (1.0 + visit_count)

        return novelty_values

    def _hash_belief_state(self, beliefs: torch.Tensor) -> str:
        """Create hash of belief state for novelty tracking"""
        # Discretize beliefs for hashing
        discretized = (beliefs * 100).round().int()
        return str(discretized.tolist())

    def update_novelty_memory(self, beliefs: torch.Tensor, observation: torch.Tensor):
        """Update novelty memory with new experience"""
        state_hash = self._hash_belief_state(beliefs)
        self.visit_counts[state_hash] = self.visit_counts.get(state_hash, 0) + 1

        # Store in novelty memory (limited size)
        self.novelty_memory.append((beliefs.clone(), observation.clone()))
        if len(self.novelty_memory) > 1000:
            self.novelty_memory.pop(0)


class InformationGainPlanner:
    """
    Planner that explicitly plans information-gathering trajectories.

    Plans sequences of actions to reduce uncertainty about specific aspects.
    """

    def __init__(self, config: ActiveLearningConfig,
                 generative_model: GenerativeModel,
                 information_seeker: InformationSeeker):
        self.config = config
        self.generative_model = generative_model
        self.info_seeker = information_seeker
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

    def plan_information_gathering(self, current_beliefs: torch.Tensor,
                                 target_uncertainty: float = 0.1,
                                 max_steps: int = 10) -> List[int]:
        """
        Plan sequence of actions to reduce uncertainty below target.

        Args:
            current_beliefs: Current belief state
            target_uncertainty: Target uncertainty level
            max_steps: Maximum planning steps

        Returns:
            Sequence of actions
        """
        planned_actions = []
        beliefs = current_beliefs.clone()

        for step in range(max_steps):
            # Compute current uncertainty
            entropy = -torch.sum(beliefs * torch.log(beliefs + self.config.eps), dim=-1).mean()

            if entropy < target_uncertainty:
                break  # Target reached

            # Find most informative action
            if isinstance(self.generative_model, DiscreteGenerativeModel):
                num_actions = self.generative_model.dims.num_actions
                action_values = torch.zeros(num_actions, device=self.device)

                B_matrix = self.generative_model.B

                for a in range(num_actions):
                    # Predict beliefs after action
                    next_beliefs = torch.matmul(beliefs, B_matrix[:, :, a].T)

                    # Estimate information gain
                    next_entropy = -torch.sum(
                        next_beliefs * torch.log(next_beliefs + self.config.eps), dim=-1
                    ).mean()

                    action_values[a] = entropy - next_entropy  # Information gain

                # Select best action
                best_action = torch.argmax(action_values)
                planned_actions.append(best_action.item())

                # Update beliefs
                beliefs = torch.matmul(beliefs, B_matrix[:, :, best_action].T)

        return planned_actions


def create_active_learner(learner_type: str,
                         config: Optional[ActiveLearningConfig] = None,
                         **kwargs) -> Union[ActiveLearningAgent, InformationGainPlanner]:
    """
    Factory function to create active learners.

    Args:
        learner_type: Type of learner ('agent', 'planner')
        config: Configuration
        **kwargs: Additional parameters

    Returns:
        Active learner instance
    """
    if config is None:
        config = ActiveLearningConfig()

    if learner_type == 'agent':
        generative_model = kwargs.get('generative_model')
        inference_algorithm = kwargs.get('inference_algorithm')
        policy_selector = kwargs.get('policy_selector')

        if None in [generative_model, inference_algorithm, policy_selector]:
            raise ValueError("Agent requires generative_model, inference_algorithm, and policy_selector")

        return ActiveLearningAgent(
            config, generative_model, inference_algorithm, policy_selector
        )

    elif learner_type == 'planner':
        generative_model = kwargs.get('generative_model')

        if generative_model is None:
            raise ValueError("Planner requires generative_model")

        # Create information seeker
        if config.information_metric == InformationMetric.ENTROPY:
            info_seeker = EntropyBasedSeeker(config, generative_model)
        else:
            inference_algorithm = kwargs.get('inference_algorithm')
            if inference_algorithm is None:
                raise ValueError("Mutual information seeker requires inference_algorithm")
            info_seeker = MutualInformationSeeker(config, generative_model, inference_algorithm)

        return InformationGainPlanner(config, generative_model, info_seeker)

    else:
        raise ValueError(f"Unknown learner type: {learner_type}")


# Example usage
if __name__ == "__main__":
    from .generative_model import DiscreteGenerativeModel, ModelDimensions, ModelParameters
    from .inference import VariationalMessagePassing, InferenceConfig
    from .policy_selection import DiscreteExpectedFreeEnergy, PolicyConfig

    # Configuration
    config = ActiveLearningConfig(
        exploration_weight=0.3,
        information_metric=InformationMetric.ENTROPY,
        use_gpu=False
    )

    # Create components
    dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
    params = ModelParameters(use_gpu=False)
    gen_model = DiscreteGenerativeModel(dims, params)

    inf_config = InferenceConfig(use_gpu=False)
    inference = VariationalMessagePassing(inf_config)

    pol_config = PolicyConfig(use_gpu=False)
    policy_selector = DiscreteExpectedFreeEnergy(pol_config)

    # Create active learner
    learner = ActiveLearningAgent(config, gen_model, inference, policy_selector)

    # Example usage
    beliefs = torch.softmax(torch.randn(1, 4), dim=-1)
    available_actions = torch.eye(2)

    action, info = learner.select_exploratory_action(beliefs, available_actions)
    print(f"Selected action: {action}")
    print(f"Info: {info}")
