"""
Temporal Horizon Planning System for Active Inference

This module implements multi-step planning capabilities to evaluate policies
over multiple time steps, including tree search and trajectory sampling methods.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any, Callable, Set
from dataclasses import dataclass, field
import numpy as np
import logging
from abc import ABC, abstractmethod
from collections import defaultdict, deque
import heapq

from .generative_model import GenerativeModel, DiscreteGenerativeModel
from .inference import InferenceAlgorithm
from .policy_selection import Policy, PolicySelector, DiscreteExpectedFreeEnergy

logger = logging.getLogger(__name__)


@dataclass
class PlanningConfig:
    """Configuration for temporal planning"""
    # Planning parameters
    planning_horizon: int = 10
    max_depth: int = 5
    branching_factor: int = 3

    # Search parameters
    search_type: str = 'mcts'  # 'mcts', 'beam', 'astar', 'sampling'
    num_simulations: int = 100
    num_trajectories: int = 50

    # Pruning parameters
    enable_pruning: bool = True
    pruning_threshold: float = 0.01
    beam_width: int = 10

    # Evaluation parameters
    discount_factor: float = 0.95
    exploration_constant: float = 1.0

    # Computational parameters
    use_gpu: bool = True
    dtype: torch.dtype = torch.float32
    eps: float = 1e-16

    # Memory parameters
    max_nodes: int = 10000
    enable_caching: bool = True


class TreeNode:
    """Node in the planning tree"""

    def __init__(self, state: torch.Tensor, action: Optional[int] = None,
                 parent: Optional['TreeNode'] = None, depth: int = 0):
        self.state = state
        self.action = action
        self.parent = parent
        self.depth = depth
        self.children: List['TreeNode'] = []

        # Statistics for MCTS
        self.visits = 0
        self.value = 0.0
        self.expected_free_energy = float('inf')

        # Cached computations
        self._hash = None
        self._is_terminal = False

    def add_child(self, child: 'TreeNode'):
        """Add child node"""
        self.children.append(child)

    def is_leaf(self) -> bool:
        """Check if node is a leaf"""
        return len(self.children) == 0

    def is_fully_expanded(self, num_actions: int) -> bool:
        """Check if all actions have been tried"""
        return len(self.children) == num_actions

    def best_child(self, exploration_constant: float = 1.0) -> 'TreeNode':
        """Select best child using UCB1"""
        if not self.children:
            return None

        def ucb1(child):
            if child.visits == 0:
                return float('inf')
            exploitation = -child.expected_free_energy
            exploration = exploration_constant * np.sqrt(np.log(self.visits) / child.visits)
            return exploitation + exploration

        return max(self.children, key=ucb1)

    def __hash__(self):
        """Hash for caching"""
        if self._hash is None:
            self._hash = hash((self.state.numpy().tobytes(), self.action, self.depth))
        return self._hash


class TemporalPlanner(ABC):
    """Abstract base class for temporal planning"""

    def __init__(self, config: PlanningConfig,
                 policy_selector: PolicySelector,
                 inference_algorithm: InferenceAlgorithm):
        self.config = config
        self.policy_selector = policy_selector
        self.inference = inference_algorithm
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

    @abstractmethod
    def plan(self, initial_beliefs: torch.Tensor,
             generative_model: GenerativeModel,
             preferences: Optional[torch.Tensor] = None) -> Tuple[Policy, float]:
        """Plan over temporal horizon"""
        pass

    @abstractmethod
    def evaluate_trajectory(self, trajectory: List[TreeNode],
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> float:
        """Evaluate a trajectory"""
        pass


class MonteCarloTreeSearch(TemporalPlanner):
    """
    Monte Carlo Tree Search for temporal planning.

    Balances exploration and exploitation to find optimal policies
    over extended time horizons.
    """

    def __init__(self, config: PlanningConfig,
                 policy_selector: PolicySelector,
                 inference_algorithm: InferenceAlgorithm):
        super().__init__(config, policy_selector, inference_algorithm)
        self.node_count = 0
        self.node_cache = {}

    def plan(self, initial_beliefs: torch.Tensor,
             generative_model: GenerativeModel,
             preferences: Optional[torch.Tensor] = None) -> Tuple[Policy, float]:
        """
        Plan using MCTS.

        Args:
            initial_beliefs: Initial belief state
            generative_model: Generative model
            preferences: Optional preferences

        Returns:
            best_policy: Best policy found
            expected_value: Expected value of policy
        """
        # Initialize root node
        root = TreeNode(initial_beliefs, depth=0)

        # Run simulations
        for _ in range(self.config.num_simulations):
            if self.node_count >= self.config.max_nodes:
                break

            # Selection
            node = self._select(root, generative_model)

            # Expansion
            if not node.is_terminal and node.depth < self.config.max_depth:
                node = self._expand(node, generative_model)

            # Simulation
            value = self._simulate(node, generative_model, preferences)

            # Backpropagation
            self._backpropagate(node, value)

        # Extract best policy
        best_policy = self._extract_policy(root)
        expected_value = root.value / max(root.visits, 1)

        return best_policy, expected_value

    def _select(self, node: TreeNode, generative_model: GenerativeModel) -> TreeNode:
        """Select node to expand using tree policy"""
        while not node.is_leaf():
            if not node.is_fully_expanded(generative_model.dims.num_actions):
                return node
            else:
                node = node.best_child(self.config.exploration_constant)
        return node

    def _expand(self, node: TreeNode, generative_model: GenerativeModel) -> TreeNode:
        """Expand node by adding new child"""
        # Get untried actions
        tried_actions = {child.action for child in node.children}
        untried_actions = [a for a in range(generative_model.dims.num_actions)
                          if a not in tried_actions]

        if not untried_actions:
            return node

        # Select random untried action
        action = np.random.choice(untried_actions)

        # Predict next state
        if isinstance(generative_model, DiscreteGenerativeModel):
            next_beliefs = generative_model.B[:, :, action] @ node.state
        else:
            # Simplified for continuous
            next_beliefs = node.state

        # Create child node
        child = TreeNode(next_beliefs, action, node, node.depth + 1)
        node.add_child(child)
        self.node_count += 1

        return child

    def _simulate(self, node: TreeNode, generative_model: GenerativeModel,
                  preferences: Optional[torch.Tensor] = None) -> float:
        """Simulate from node to estimate value"""
        current_node = node
        current_beliefs = node.state.clone()
        total_G = 0.0
        discount = 1.0

        # Random rollout
        for t in range(self.config.planning_horizon - node.depth):
            if t >= self.config.max_depth - node.depth:
                break

            # Select random action
            action = np.random.randint(0, generative_model.dims.num_actions)
            policy = Policy([action])

            # Compute expected free energy
            G = self.policy_selector.compute_expected_free_energy(
                policy, current_beliefs, generative_model, preferences
            )

            total_G += discount * G.item()
            discount *= self.config.discount_factor

            # Update beliefs
            if isinstance(generative_model, DiscreteGenerativeModel):
                current_beliefs = generative_model.B[:, :, action] @ current_beliefs

        return -total_G  # Negative because we minimize free energy

    def _backpropagate(self, node: TreeNode, value: float):
        """Backpropagate value up the tree"""
        while node is not None:
            node.visits += 1
            node.value += value
            node = node.parent

    def _extract_policy(self, root: TreeNode) -> Policy:
        """Extract policy from tree"""
        actions = []
        node = root

        while node.children and len(actions) < self.config.planning_horizon:
            # Select most visited child
            best_child = max(node.children, key=lambda c: c.visits)
            actions.append(best_child.action)
            node = best_child

        return Policy(actions)

    def evaluate_trajectory(self, trajectory: List[TreeNode],
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> float:
        """Evaluate a trajectory of nodes"""
        total_G = 0.0
        discount = 1.0

        for i in range(len(trajectory) - 1):
            node = trajectory[i]
            next_node = trajectory[i + 1]

            if next_node.action is not None:
                policy = Policy([next_node.action])
                G = self.policy_selector.compute_expected_free_energy(
                    policy, node.state, generative_model, preferences
                )
                total_G += discount * G.item()
                discount *= self.config.discount_factor

        return -total_G


class BeamSearchPlanner(TemporalPlanner):
    """
    Beam search for temporal planning.

    Maintains top-k trajectories at each depth level.
    """

    def __init__(self, config: PlanningConfig,
                 policy_selector: PolicySelector,
                 inference_algorithm: InferenceAlgorithm):
        super().__init__(config, policy_selector, inference_algorithm)

    def plan(self, initial_beliefs: torch.Tensor,
             generative_model: GenerativeModel,
             preferences: Optional[torch.Tensor] = None) -> Tuple[Policy, float]:
        """
        Plan using beam search.

        Args:
            initial_beliefs: Initial belief state
            generative_model: Generative model
            preferences: Optional preferences

        Returns:
            best_policy: Best policy found
            expected_value: Expected value of policy
        """
        # Initialize beam with root
        beam = [(0.0, [], initial_beliefs)]  # (cost, actions, beliefs)

        for depth in range(min(self.config.planning_horizon, self.config.max_depth)):
            new_beam = []

            for cost, actions, beliefs in beam:
                # Try all actions
                for action in range(generative_model.dims.num_actions):
                    # Create policy for this action
                    policy = Policy([action])

                    # Compute expected free energy
                    G = self.policy_selector.compute_expected_free_energy(
                        policy, beliefs, generative_model, preferences
                    )

                    # Update cost (cumulative with discount)
                    new_cost = cost + (self.config.discount_factor ** depth) * G.item()

                    # Predict next beliefs
                    if isinstance(generative_model, DiscreteGenerativeModel):
                        next_beliefs = generative_model.B[:, :, action] @ beliefs
                    else:
                        next_beliefs = beliefs  # Simplified

                    # Add to new beam
                    new_actions = actions + [action]
                    new_beam.append((new_cost, new_actions, next_beliefs))

            # Keep top-k trajectories
            new_beam.sort(key=lambda x: x[0])
            beam = new_beam[:self.config.beam_width]

            # Early stopping if beam converges
            if len(set(tuple(b[1]) for b in beam)) == 1:
                break

        # Return best trajectory
        best_cost, best_actions, _ = beam[0]
        best_policy = Policy(best_actions)

        return best_policy, -best_cost

    def evaluate_trajectory(self, trajectory: List[TreeNode],
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> float:
        """Evaluate trajectory (not used in beam search)"""
        # Convert nodes to actions and evaluate
        actions = [node.action for node in trajectory[1:] if node.action is not None]
        if not actions:
            return 0.0

        policy = Policy(actions)
        G = self.policy_selector.compute_expected_free_energy(
            policy, trajectory[0].state, generative_model, preferences
        )
        return -G.item()


class AStarPlanner(TemporalPlanner):
    """
    A* search for temporal planning.

    Uses heuristic to guide search toward promising trajectories.
    """

    def __init__(self, config: PlanningConfig,
                 policy_selector: PolicySelector,
                 inference_algorithm: InferenceAlgorithm):
        super().__init__(config, policy_selector, inference_algorithm)

    def plan(self, initial_beliefs: torch.Tensor,
             generative_model: GenerativeModel,
             preferences: Optional[torch.Tensor] = None) -> Tuple[Policy, float]:
        """
        Plan using A* search.

        Args:
            initial_beliefs: Initial belief state
            generative_model: Generative model
            preferences: Optional preferences

        Returns:
            best_policy: Best policy found
            expected_value: Expected value of policy
        """
        # Priority queue: (f_score, g_score, actions, beliefs)
        open_set = [(0.0, 0.0, [], initial_beliefs)]
        closed_set = set()

        # Best scores for visited states
        g_scores = defaultdict(lambda: float('inf'))
        g_scores[self._hash_beliefs(initial_beliefs)] = 0.0

        while open_set and len(closed_set) < self.config.max_nodes:
            # Pop best node
            f_score, g_score, actions, beliefs = heapq.heappop(open_set)

            # Check if we've reached horizon
            if len(actions) >= self.config.planning_horizon:
                return Policy(actions), -g_score

            # Skip if already visited
            state_hash = self._hash_beliefs(beliefs)
            if state_hash in closed_set:
                continue
            closed_set.add(state_hash)

            # Expand node
            for action in range(generative_model.dims.num_actions):
                # Create policy for this action
                policy = Policy([action])

                # Compute expected free energy
                G = self.policy_selector.compute_expected_free_energy(
                    policy, beliefs, generative_model, preferences
                )

                # Calculate new g_score
                step_cost = (self.config.discount_factor ** len(actions)) * G.item()
                new_g_score = g_score + step_cost

                # Predict next beliefs
                if isinstance(generative_model, DiscreteGenerativeModel):
                    next_beliefs = generative_model.B[:, :, action] @ beliefs
                else:
                    next_beliefs = beliefs  # Simplified

                next_hash = self._hash_beliefs(next_beliefs)

                # Skip if not better path
                if new_g_score >= g_scores[next_hash]:
                    continue

                g_scores[next_hash] = new_g_score

                # Calculate heuristic (remaining steps * average expected G)
                h_score = self._heuristic(
                    next_beliefs, len(actions) + 1,
                    generative_model, preferences
                )

                # Add to open set
                new_f_score = new_g_score + h_score
                new_actions = actions + [action]
                heapq.heappush(open_set, (new_f_score, new_g_score, new_actions, next_beliefs))

        # Return best found so far
        if not open_set:
            return Policy([]), 0.0

        _, g_score, actions, _ = open_set[0]
        return Policy(actions), -g_score

    def _hash_beliefs(self, beliefs: torch.Tensor) -> int:
        """Hash belief state for efficient lookup"""
        return hash(beliefs.numpy().tobytes())

    def _heuristic(self, beliefs: torch.Tensor, depth: int,
                   generative_model: GenerativeModel,
                   preferences: Optional[torch.Tensor] = None) -> float:
        """Heuristic function for remaining cost"""
        # Simple heuristic: average expected free energy * remaining steps
        remaining_steps = self.config.planning_horizon - depth
        if remaining_steps <= 0:
            return 0.0

        # Sample a few random actions to estimate average G
        sample_G = []
        for _ in range(min(3, generative_model.dims.num_actions)):
            action = np.random.randint(0, generative_model.dims.num_actions)
            policy = Policy([action])
            G = self.policy_selector.compute_expected_free_energy(
                policy, beliefs, generative_model, preferences
            )
            sample_G.append(G.item())

        avg_G = np.mean(sample_G) if sample_G else 0.0

        # Discounted sum of expected G
        discount_sum = (1 - self.config.discount_factor ** remaining_steps) / (1 - self.config.discount_factor)
        return avg_G * discount_sum * (self.config.discount_factor ** depth)

    def evaluate_trajectory(self, trajectory: List[TreeNode],
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> float:
        """Evaluate trajectory"""
        total_G = 0.0
        discount = 1.0

        for i in range(len(trajectory) - 1):
            if trajectory[i+1].action is not None:
                policy = Policy([trajectory[i+1].action])
                G = self.policy_selector.compute_expected_free_energy(
                    policy, trajectory[i].state, generative_model, preferences
                )
                total_G += discount * G.item()
                discount *= self.config.discount_factor

        return -total_G


class TrajectorySampling(TemporalPlanner):
    """
    Trajectory sampling for temporal planning.

    Samples multiple trajectories and selects the best one.
    """

    def __init__(self, config: PlanningConfig,
                 policy_selector: PolicySelector,
                 inference_algorithm: InferenceAlgorithm):
        super().__init__(config, policy_selector, inference_algorithm)

    def plan(self, initial_beliefs: torch.Tensor,
             generative_model: GenerativeModel,
             preferences: Optional[torch.Tensor] = None) -> Tuple[Policy, float]:
        """
        Plan by sampling trajectories.

        Args:
            initial_beliefs: Initial belief state
            generative_model: Generative model
            preferences: Optional preferences

        Returns:
            best_policy: Best policy found
            expected_value: Expected value of policy
        """
        best_trajectory = None
        best_value = float('-inf')

        for _ in range(self.config.num_trajectories):
            # Sample trajectory
            trajectory, value = self._sample_trajectory(
                initial_beliefs, generative_model, preferences
            )

            # Update best
            if value > best_value:
                best_value = value
                best_trajectory = trajectory

        # Extract actions from best trajectory
        actions = [node.action for node in best_trajectory[1:]
                  if node.action is not None]
        best_policy = Policy(actions)

        return best_policy, best_value

    def _sample_trajectory(self, initial_beliefs: torch.Tensor,
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> Tuple[List[TreeNode], float]:
        """Sample a single trajectory"""
        trajectory = [TreeNode(initial_beliefs, depth=0)]
        current_beliefs = initial_beliefs.clone()
        total_value = 0.0
        discount = 1.0

        for depth in range(min(self.config.planning_horizon, self.config.max_depth)):
            # Sample action based on current policy
            temp_policy, probs = self.policy_selector.select_policy(
                current_beliefs, generative_model, preferences
            )

            # For trajectory sampling, we might want stochastic selection
            if len(temp_policy) > 0:
                action = temp_policy[0].item()
            else:
                action = np.random.randint(0, generative_model.dims.num_actions)

            # Compute expected free energy
            policy = Policy([action])
            G = self.policy_selector.compute_expected_free_energy(
                policy, current_beliefs, generative_model, preferences
            )

            total_value += discount * (-G.item())  # Negative because we minimize G
            discount *= self.config.discount_factor

            # Update beliefs
            if isinstance(generative_model, DiscreteGenerativeModel):
                next_beliefs = generative_model.B[:, :, action] @ current_beliefs
            else:
                next_beliefs = current_beliefs  # Simplified

            # Add to trajectory
            node = TreeNode(next_beliefs, action, trajectory[-1], depth + 1)
            trajectory.append(node)
            current_beliefs = next_beliefs

        return trajectory, total_value

    def evaluate_trajectory(self, trajectory: List[TreeNode],
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> float:
        """Evaluate a sampled trajectory"""
        total_value = 0.0
        discount = 1.0

        for i in range(len(trajectory) - 1):
            if trajectory[i+1].action is not None:
                policy = Policy([trajectory[i+1].action])
                G = self.policy_selector.compute_expected_free_energy(
                    policy, trajectory[i].state, generative_model, preferences
                )
                total_value += discount * (-G.item())
                discount *= self.config.discount_factor

        return total_value


class AdaptiveHorizonPlanner(TemporalPlanner):
    """
    Adaptive horizon planning that adjusts planning depth based on uncertainty.

    Plans deeper when uncertainty is high, shallower when confident.
    """

    def __init__(self, config: PlanningConfig,
                 policy_selector: PolicySelector,
                 inference_algorithm: InferenceAlgorithm,
                 base_planner: TemporalPlanner):
        super().__init__(config, policy_selector, inference_algorithm)
        self.base_planner = base_planner
        self.uncertainty_threshold = 0.5

    def plan(self, initial_beliefs: torch.Tensor,
             generative_model: GenerativeModel,
             preferences: Optional[torch.Tensor] = None) -> Tuple[Policy, float]:
        """
        Plan with adaptive horizon based on uncertainty.

        Args:
            initial_beliefs: Initial belief state
            generative_model: Generative model
            preferences: Optional preferences

        Returns:
            best_policy: Best policy found
            expected_value: Expected value of policy
        """
        # Measure initial uncertainty
        uncertainty = self._measure_uncertainty(initial_beliefs)

        # Adapt planning horizon
        if uncertainty > self.uncertainty_threshold:
            # High uncertainty: plan deeper
            adaptive_horizon = min(
                int(self.config.planning_horizon * 1.5),
                self.config.max_depth * 2
            )
        else:
            # Low uncertainty: shorter horizon is sufficient
            adaptive_horizon = max(
                int(self.config.planning_horizon * 0.7),
                3
            )

        # Update config temporarily
        original_horizon = self.config.planning_horizon
        self.config.planning_horizon = adaptive_horizon

        # Plan with adapted horizon
        policy, value = self.base_planner.plan(
            initial_beliefs, generative_model, preferences
        )

        # Restore original horizon
        self.config.planning_horizon = original_horizon

        return policy, value

    def _measure_uncertainty(self, beliefs: torch.Tensor) -> float:
        """Measure uncertainty in beliefs"""
        # For discrete beliefs: use entropy
        if beliefs.dim() == 1:
            # Normalize to ensure valid probability
            probs = F.softmax(beliefs, dim=0)
            entropy = -torch.sum(probs * torch.log(probs + self.config.eps))
            # Normalize by max entropy
            max_entropy = torch.log(torch.tensor(float(beliefs.shape[0])))
            return (entropy / max_entropy).item()
        else:
            # For continuous: could use variance or other measures
            return torch.var(beliefs).item()

    def evaluate_trajectory(self, trajectory: List[TreeNode],
                          generative_model: GenerativeModel,
                          preferences: Optional[torch.Tensor] = None) -> float:
        """Delegate to base planner"""
        return self.base_planner.evaluate_trajectory(
            trajectory, generative_model, preferences
        )


def create_temporal_planner(planner_type: str,
                          config: Optional[PlanningConfig] = None,
                          **kwargs) -> TemporalPlanner:
    """
    Factory function to create temporal planners.

    Args:
        planner_type: Type of planner ('mcts', 'beam', 'astar', 'sampling', 'adaptive')
        config: Planning configuration
        **kwargs: Planner-specific parameters

    Returns:
        Temporal planner instance
    """
    if config is None:
        config = PlanningConfig()

    # Required components
    policy_selector = kwargs.get('policy_selector')
    inference_algorithm = kwargs.get('inference_algorithm')

    if policy_selector is None or inference_algorithm is None:
        raise ValueError("Temporal planner requires policy_selector and inference_algorithm")

    if planner_type == 'mcts':
        return MonteCarloTreeSearch(config, policy_selector, inference_algorithm)

    elif planner_type == 'beam':
        return BeamSearchPlanner(config, policy_selector, inference_algorithm)

    elif planner_type == 'astar':
        return AStarPlanner(config, policy_selector, inference_algorithm)

    elif planner_type == 'sampling':
        return TrajectorySampling(config, policy_selector, inference_algorithm)

    elif planner_type == 'adaptive':
        base_planner_type = kwargs.get('base_planner_type', 'mcts')
        base_planner = create_temporal_planner(
            base_planner_type, config,
            policy_selector=policy_selector,
            inference_algorithm=inference_algorithm
        )
        return AdaptiveHorizonPlanner(
            config, policy_selector, inference_algorithm, base_planner
        )

    else:
        raise ValueError(f"Unknown planner type: {planner_type}")


# Example usage
if __name__ == "__main__":
    from .generative_model import ModelDimensions, ModelParameters
    from .inference import VariationalMessagePassing, InferenceConfig
    from .policy_selection import PolicyConfig

    # Create a simple discrete model
    dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
    params = ModelParameters(use_gpu=False)
    model = DiscreteGenerativeModel(dims, params)

    # Create inference algorithm
    inf_config = InferenceConfig(use_gpu=False)
    inference = VariationalMessagePassing(inf_config)

    # Create policy selector
    policy_config = PolicyConfig(use_gpu=False)
    policy_selector = DiscreteExpectedFreeEnergy(policy_config, inference)

    # Create temporal planner
    planning_config = PlanningConfig(
        planning_horizon=5,
        num_simulations=50,
        use_gpu=False
    )
    planner = MonteCarloTreeSearch(planning_config, policy_selector, inference)

    # Initial beliefs
    beliefs = torch.ones(4) / 4

    # Plan
    policy, value = planner.plan(beliefs, model)
    print(f"Best policy: {policy}")
    print(f"Expected value: {value}")
