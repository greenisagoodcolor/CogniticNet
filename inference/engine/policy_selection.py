"""
Policy Selection Mechanism for Active Inference

This module implements action selection based on expected free energy minimization,
including both epistemic (information gain) and pragmatic (goal-seeking) components.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, field
import numpy as np
import logging
from abc import ABC, abstractmethod
from .generative_model import GenerativeModel, DiscreteGenerativeModel
from .inference import InferenceAlgorithm
logger = logging.getLogger(__name__)

@dataclass
class PolicyConfig:
    """Configuration for policy selection"""
    planning_horizon: int = 5
    num_policies: Optional[int] = None
    policy_length: int = 1
    epistemic_weight: float = 1.0
    pragmatic_weight: float = 1.0
    exploration_constant: float = 1.0
    habit_strength: float = 0.0
    use_gpu: bool = True
    dtype: torch.dtype = torch.float32
    eps: float = 1e-16
    use_sampling: bool = False
    num_samples: int = 100
    enable_pruning: bool = True
    pruning_threshold: float = 0.01

class Policy:
    """Represents a sequence of actions (policy)"""

    def __init__(self, actions: Union[List[int], torch.Tensor], horizon: Optional[int]=None):
        if isinstance(actions, list):
            self.actions = torch.tensor(actions)
        else:
            self.actions = actions
        self.length = len(self.actions)
        self.horizon = horizon or self.length

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        return self.actions[idx]

    def __repr__(self):
        return f'Policy({self.actions.tolist()})'

class PolicySelector(ABC):
    """Abstract base class for policy selection"""

    def __init__(self, config: PolicyConfig):
        self.config = config
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

    @abstractmethod
    def select_policy(self, beliefs: torch.Tensor, generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> Tuple[Policy, torch.Tensor]:
        """Select policy based on expected free energy"""
        pass

    @abstractmethod
    def compute_expected_free_energy(self, policy: Policy, beliefs: torch.Tensor, generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> torch.Tensor:
        """Compute expected free energy for a policy"""
        pass

class DiscreteExpectedFreeEnergy(PolicySelector):
    """
    Expected free energy calculation for discrete state spaces.

    Implements G(π) = E_q[log q(s'|π) - log p(s'|π) - log p(o'|π)]
    """

    def __init__(self, config: PolicyConfig, inference_algorithm: InferenceAlgorithm):
        super().__init__(config)
        self.inference = inference_algorithm
        self.eps = config.eps

    def enumerate_policies(self, num_actions: int) -> List[Policy]:
        """Enumerate all possible policies up to specified length"""
        if self.config.num_policies is not None:
            policies = []
            for _ in range(self.config.num_policies):
                actions = torch.randint(0, num_actions, (self.config.policy_length,))
                policies.append(Policy(actions, self.config.planning_horizon))
            return policies
        elif self.config.policy_length == 1:
            return [Policy([a]) for a in range(num_actions)]
        else:
            import itertools
            all_combos = itertools.product(range(num_actions), repeat=self.config.policy_length)
            return [Policy(list(combo), self.config.planning_horizon) for combo in all_combos]

    def select_policy(self, beliefs: torch.Tensor, generative_model: DiscreteGenerativeModel, preferences: Optional[torch.Tensor]=None) -> Tuple[Policy, torch.Tensor]:
        """
        Select policy that minimizes expected free energy.

        Args:
            beliefs: Current beliefs over states
            generative_model: Generative model
            preferences: Optional preferences over observations

        Returns:
            selected_policy: Best policy
            policy_probs: Probabilities over all policies
        """
        if preferences is None:
            preferences = generative_model.get_preferences()
        policies = self.enumerate_policies(generative_model.dims.num_actions)
        G_values = []
        for policy in policies:
            G = self.compute_expected_free_energy(policy, beliefs, generative_model, preferences)
            G_values.append(G)
        G_tensor = torch.stack(G_values)
        if self.config.habit_strength > 0:
            habit_prior = torch.zeros_like(G_tensor)
            G_tensor = G_tensor - self.config.habit_strength * habit_prior
        policy_probs = F.softmax(-G_tensor / self.config.exploration_constant, dim=0)
        if self.config.enable_pruning:
            mask = policy_probs > self.config.pruning_threshold
            if mask.sum() > 0:
                policy_probs = policy_probs * mask
                policy_probs = policy_probs / policy_probs.sum()
        if self.config.use_sampling:
            policy_idx = torch.multinomial(policy_probs, 1).item()
        else:
            policy_idx = torch.argmax(policy_probs).item()
        selected_policy = policies[policy_idx]
        return (selected_policy, policy_probs)

    def compute_expected_free_energy(self, policy: Policy, beliefs: torch.Tensor, generative_model: DiscreteGenerativeModel, preferences: Optional[torch.Tensor]=None) -> torch.Tensor:
        """
        Compute expected free energy for a policy.

        G(π) = ∑_τ [epistemic_value + pragmatic_value]

        Where:
        - epistemic_value = E_q[H[P(o_τ|s_τ)] - H[P(o_τ|s_τ,π)]]
        - pragmatic_value = E_q[log P(o_τ) - log Q(o_τ|π)]
        """
        G = torch.tensor(0.0, device=self.device)
        current_beliefs = beliefs.to(self.device)
        A = generative_model.A.to(self.device)
        B = generative_model.B.to(self.device)
        if preferences is None:
            preferences = generative_model.get_preferences()
        for t in range(min(len(policy), self.config.planning_horizon)):
            action = policy[t]
            next_beliefs = B[:, :, action] @ current_beliefs
            expected_obs = A @ next_beliefs
            if self.config.epistemic_weight > 0:
                H_expected = -torch.sum(expected_obs * torch.log(expected_obs + self.eps))
                H_conditional = 0
                for s in range(generative_model.dims.num_states):
                    if next_beliefs[s] > self.eps:
                        obs_given_state = A[:, s]
                        H_s = -torch.sum(obs_given_state * torch.log(obs_given_state + self.eps))
                        H_conditional += next_beliefs[s] * H_s
                epistemic_value = H_expected - H_conditional
                G += self.config.epistemic_weight * epistemic_value
            if self.config.pragmatic_weight > 0:
                if preferences.dim() > 1 and t < preferences.shape[1]:
                    pref_t = preferences[:, t]
                else:
                    pref_t = preferences[:, 0] if preferences.dim() > 1 else preferences
                expected_log_pref = torch.sum(expected_obs * pref_t)
                pragmatic_value = -expected_log_pref
                G += self.config.pragmatic_weight * pragmatic_value
            current_beliefs = next_beliefs
        return G

class ContinuousExpectedFreeEnergy(PolicySelector):
    """
    Expected free energy for continuous state spaces.

    Uses sampling-based approximations for continuous distributions.
    """

    def __init__(self, config: PolicyConfig, inference_algorithm: InferenceAlgorithm):
        super().__init__(config)
        self.inference = inference_algorithm

    def sample_policies(self, action_dim: int, num_policies: int) -> List[Policy]:
        """Sample continuous action policies"""
        policies = []
        for _ in range(num_policies):
            actions = torch.randn(self.config.policy_length, action_dim) * 0.5
            actions = torch.clamp(actions, -1.0, 1.0)
            policies.append(Policy(actions, self.config.planning_horizon))
        return policies

    def select_policy(self, beliefs: Tuple[torch.Tensor, torch.Tensor], generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> Tuple[Policy, torch.Tensor]:
        """
        Select policy for continuous states.

        Args:
            beliefs: (mean, variance) of current state beliefs
            generative_model: Generative model
            preferences: Optional preferences

        Returns:
            selected_policy: Best policy
            policy_values: Values for sampled policies
        """
        num_policies = self.config.num_policies or 100
        policies = self.sample_policies(generative_model.dims.num_actions, num_policies)
        G_values = []
        for policy in policies:
            G = self.compute_expected_free_energy(policy, beliefs, generative_model, preferences)
            G_values.append(G)
        G_tensor = torch.stack(G_values)
        if self.config.use_sampling:
            probs = F.softmax(-G_tensor / self.config.exploration_constant, dim=0)
            policy_idx = torch.multinomial(probs, 1).item()
        else:
            policy_idx = torch.argmin(G_tensor).item()
        return (policies[policy_idx], G_tensor)

    def compute_expected_free_energy(self, policy: Policy, beliefs: Tuple[torch.Tensor, torch.Tensor], generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> torch.Tensor:
        """
        Compute expected free energy using Monte Carlo approximation.
        """
        mean, var = beliefs
        mean = mean.to(self.device)
        var = var.to(self.device)
        G = torch.tensor(0.0, device=self.device)
        num_samples = self.config.num_samples
        for _ in range(num_samples):
            std = torch.sqrt(var)
            current_state = mean + std * torch.randn_like(mean)
            for t in range(min(len(policy), self.config.planning_horizon)):
                action = policy[t]
                if hasattr(generative_model, 'transition_model'):
                    next_mean, next_var = generative_model.transition_model(current_state.unsqueeze(0), action.unsqueeze(0))
                    next_mean = next_mean.squeeze(0)
                    next_var = next_var.squeeze(0)
                else:
                    next_mean = current_state + action * 0.1
                    next_var = var * 1.1
                if hasattr(generative_model, 'observation_model'):
                    obs_mean, obs_var = generative_model.observation_model(next_mean.unsqueeze(0))
                    obs_mean = obs_mean.squeeze(0)
                    obs_var = obs_var.squeeze(0)
                else:
                    obs_mean = next_mean
                    obs_var = next_var
                if self.config.epistemic_weight > 0:
                    info_gain = 0.5 * torch.sum(torch.log(var / next_var))
                    G -= self.config.epistemic_weight * info_gain
                if self.config.pragmatic_weight > 0 and preferences is not None:
                    if preferences.dim() > 1 and t < preferences.shape[1]:
                        pref_t = preferences[:, t]
                    else:
                        pref_t = preferences
                    prag_value = -torch.sum((obs_mean - pref_t) ** 2 / obs_var)
                    G -= self.config.pragmatic_weight * prag_value
                current_state = next_mean
                var = next_var
        G = G / num_samples
        return G

class HierarchicalPolicySelector(PolicySelector):
    """
    Hierarchical policy selection with temporal abstraction.

    Higher levels select abstract policies, lower levels implement them.
    """

    def __init__(self, config: PolicyConfig, level_selectors: List[PolicySelector], level_horizons: List[int]):
        super().__init__(config)
        self.level_selectors = level_selectors
        self.level_horizons = level_horizons
        self.num_levels = len(level_selectors)

    def select_policy(self, beliefs: List[torch.Tensor], generative_models: List[GenerativeModel], preferences: Optional[List[torch.Tensor]]=None) -> Tuple[List[Policy], List[torch.Tensor]]:
        """
        Select policies at each hierarchical level.

        Args:
            beliefs: Beliefs at each level
            generative_models: Models at each level
            preferences: Optional preferences at each level

        Returns:
            policies: Selected policies at each level
            policy_probs: Policy probabilities at each level
        """
        policies = []
        all_probs = []
        for level in range(self.num_levels):
            if level > 0:
                context = policies[level - 1]
            else:
                context = None
            level_beliefs = beliefs[level]
            level_model = generative_models[level]
            level_prefs = preferences[level] if preferences else None
            policy, probs = self.level_selectors[level].select_policy(level_beliefs, level_model, level_prefs)
            policies.append(policy)
            all_probs.append(probs)
        return (policies, all_probs)

    def compute_expected_free_energy(self, policies: List[Policy], beliefs: List[torch.Tensor], generative_models: List[GenerativeModel], preferences: Optional[List[torch.Tensor]]=None) -> torch.Tensor:
        """Compute total expected free energy across levels"""
        total_G = torch.tensor(0.0, device=self.device)
        for level in range(self.num_levels):
            G = self.level_selectors[level].compute_expected_free_energy(policies[level], beliefs[level], generative_models[level], preferences[level] if preferences else None)
            weight = 1.0 / (level + 1)
            total_G += weight * G
        return total_G

class SophisticatedInference(PolicySelector):
    """
    Sophisticated inference considering counterfactual policies.

    Evaluates policies by considering what the agent would believe
    and do in future timesteps.
    """

    def __init__(self, config: PolicyConfig, inference_algorithm: InferenceAlgorithm, base_selector: PolicySelector):
        super().__init__(config)
        self.inference = inference_algorithm
        self.base_selector = base_selector
        self.sophistication_depth = 3

    def select_policy(self, beliefs: torch.Tensor, generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> Tuple[Policy, torch.Tensor]:
        """
        Select policy using sophisticated inference.

        Considers future belief updates and policy selections.
        """
        base_policy, base_probs = self.base_selector.select_policy(beliefs, generative_model, preferences)
        if self.sophistication_depth > 0:
            refined_policy = self._sophisticated_refinement(base_policy, beliefs, generative_model, preferences)
            return (refined_policy, base_probs)
        else:
            return (base_policy, base_probs)

    def _sophisticated_refinement(self, initial_policy: Policy, beliefs: torch.Tensor, generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> Policy:
        """
        Refine policy by considering future belief updates.
        """
        current_beliefs = beliefs
        refined_actions = []
        for t in range(len(initial_policy)):
            action = initial_policy[t]
            if isinstance(generative_model, DiscreteGenerativeModel):
                next_beliefs = generative_model.transition_model(current_beliefs, action)
                expected_obs = generative_model.observation_model(next_beliefs)
                updated_beliefs = self.inference.infer_states(expected_obs, generative_model, next_beliefs)
            else:
                updated_beliefs = current_beliefs
            if t < self.sophistication_depth:
                future_policy, _ = self.base_selector.select_policy(updated_beliefs, generative_model, preferences)
                refined_action = future_policy[0]
            else:
                refined_action = action
            refined_actions.append(refined_action)
            current_beliefs = updated_beliefs
        return Policy(refined_actions, initial_policy.horizon)

    def compute_expected_free_energy(self, policy: Policy, beliefs: torch.Tensor, generative_model: GenerativeModel, preferences: Optional[torch.Tensor]=None) -> torch.Tensor:
        """Compute expected free energy with sophisticated inference"""
        return self.base_selector.compute_expected_free_energy(policy, beliefs, generative_model, preferences)

def create_policy_selector(selector_type: str, config: Optional[PolicyConfig]=None, **kwargs) -> PolicySelector:
    """
    Factory function to create policy selectors.

    Args:
        selector_type: Type of selector ('discrete', 'continuous', 'hierarchical', 'sophisticated')
        config: Policy configuration
        **kwargs: Selector-specific parameters

    Returns:
        Policy selector instance
    """
    if config is None:
        config = PolicyConfig()
    if selector_type == 'discrete':
        inference = kwargs.get('inference_algorithm')
        if inference is None:
            raise ValueError('Discrete selector requires inference_algorithm')
        return DiscreteExpectedFreeEnergy(config, inference)
    elif selector_type == 'continuous':
        inference = kwargs.get('inference_algorithm')
        if inference is None:
            raise ValueError('Continuous selector requires inference_algorithm')
        return ContinuousExpectedFreeEnergy(config, inference)
    elif selector_type == 'hierarchical':
        level_selectors = kwargs.get('level_selectors')
        level_horizons = kwargs.get('level_horizons', [5, 10, 20])
        if level_selectors is None:
            raise ValueError('Hierarchical selector requires level_selectors')
        return HierarchicalPolicySelector(config, level_selectors, level_horizons)
    elif selector_type == 'sophisticated':
        inference = kwargs.get('inference_algorithm')
        base_selector = kwargs.get('base_selector')
        if inference is None or base_selector is None:
            raise ValueError('Sophisticated selector requires inference_algorithm and base_selector')
        return SophisticatedInference(config, inference, base_selector)
    else:
        raise ValueError(f'Unknown selector type: {selector_type}')
if __name__ == '__main__':
    from .generative_model import ModelDimensions, ModelParameters
    from .inference import VariationalMessagePassing, InferenceConfig
    dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
    params = ModelParameters(use_gpu=False)
    model = DiscreteGenerativeModel(dims, params)
    inf_config = InferenceConfig(use_gpu=False)
    inference = VariationalMessagePassing(inf_config)
    policy_config = PolicyConfig(planning_horizon=3, policy_length=1, use_gpu=False)
    selector = DiscreteExpectedFreeEnergy(policy_config, inference)
    beliefs = torch.ones(4) / 4
    preferences = torch.tensor([-1.0, 2.0, -1.0])
    model.set_preferences(preferences)
    policy, probs = selector.select_policy(beliefs, model)
    print(f'Selected policy: {policy}')
    print(f'Policy probabilities: {probs}')
