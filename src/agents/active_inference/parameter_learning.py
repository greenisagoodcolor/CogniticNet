"""
Parameter Learning for Active Inference

This module implements mechanisms for learning and updating generative model
parameters from experience using Bayesian learning principles.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any, Callable
from dataclasses import dataclass, field
import numpy as np
import logging
from abc import ABC, abstractmethod
from collections import deque

from .generative_model import GenerativeModel, DiscreteGenerativeModel, ContinuousGenerativeModel
from .inference import InferenceAlgorithm

logger = logging.getLogger(__name__)


@dataclass
class LearningConfig:
    """Configuration for parameter learning"""
    # Learning rates
    learning_rate_A: float = 0.01  # Observation model
    learning_rate_B: float = 0.01  # Transition model
    learning_rate_C: float = 0.01  # Prior preferences
    learning_rate_D: float = 0.01  # Initial state prior

    # Bayesian learning
    use_bayesian_learning: bool = True
    concentration_A: float = 1.0  # Dirichlet concentration for A
    concentration_B: float = 1.0  # Dirichlet concentration for B
    concentration_D: float = 1.0  # Dirichlet concentration for D

    # Experience replay
    use_experience_replay: bool = True
    replay_buffer_size: int = 10000
    batch_size: int = 32
    min_buffer_size: int = 100

    # Learning schedule
    decay_rate: float = 0.999
    min_learning_rate: float = 0.0001
    update_frequency: int = 10

    # Regularization
    use_regularization: bool = True
    l2_weight: float = 0.001
    entropy_weight: float = 0.01

    # Computational
    use_gpu: bool = True
    dtype: torch.dtype = torch.float32
    eps: float = 1e-16


@dataclass
class Experience:
    """Single experience tuple"""
    state: torch.Tensor
    action: torch.Tensor
    observation: torch.Tensor
    next_state: torch.Tensor
    reward: Optional[torch.Tensor] = None
    timestamp: int = 0


class ExperienceBuffer:
    """
    Experience replay buffer for storing and sampling experiences.
    """

    def __init__(self, max_size: int):
        self.buffer = deque(maxlen=max_size)
        self.max_size = max_size

    def add(self, experience: Experience):
        """Add experience to buffer"""
        self.buffer.append(experience)

    def sample(self, batch_size: int) -> List[Experience]:
        """Sample batch of experiences"""
        indices = np.random.choice(len(self.buffer), batch_size, replace=False)
        return [self.buffer[i] for i in indices]

    def clear(self):
        """Clear buffer"""
        self.buffer.clear()

    def __len__(self) -> int:
        return len(self.buffer)


class ParameterLearner(ABC):
    """Abstract base class for parameter learning"""

    def __init__(self, config: LearningConfig):
        self.config = config
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')
        self.update_count = 0

    @abstractmethod
    def update_parameters(self, experiences: List[Experience],
                         generative_model: GenerativeModel) -> Dict[str, float]:
        """Update model parameters from experiences"""
        pass

    @abstractmethod
    def get_learning_rates(self) -> Dict[str, float]:
        """Get current learning rates"""
        pass


class DiscreteParameterLearner(ParameterLearner):
    """
    Parameter learner for discrete generative models.

    Uses Bayesian learning with Dirichlet priors for discrete distributions.
    """

    def __init__(self, config: LearningConfig,
                 model_dims: Dict[str, int]):
        super().__init__(config)

        self.num_states = model_dims['num_states']
        self.num_observations = model_dims['num_observations']
        self.num_actions = model_dims['num_actions']

        # Initialize Dirichlet concentration parameters
        if config.use_bayesian_learning:
            # A matrix concentrations
            self.pA = torch.ones(
                self.num_observations, self.num_states,
                device=self.device
            ) * config.concentration_A

            # B matrix concentrations
            self.pB = torch.ones(
                self.num_states, self.num_states, self.num_actions,
                device=self.device
            ) * config.concentration_B

            # D vector concentrations
            self.pD = torch.ones(
                self.num_states,
                device=self.device
            ) * config.concentration_D

        # Learning rate schedules
        self.lr_A = config.learning_rate_A
        self.lr_B = config.learning_rate_B
        self.lr_D = config.learning_rate_D

    def update_parameters(self, experiences: List[Experience],
                         generative_model: DiscreteGenerativeModel) -> Dict[str, float]:
        """
        Update discrete model parameters using Bayesian learning.

        Args:
            experiences: List of experiences
            generative_model: Discrete generative model to update

        Returns:
            Dictionary of update metrics
        """
        metrics = {}

        if self.config.use_bayesian_learning:
            metrics.update(self._bayesian_update(experiences, generative_model))
        else:
            metrics.update(self._gradient_update(experiences, generative_model))

        # Apply learning rate decay
        self._decay_learning_rates()

        self.update_count += 1

        return metrics

    def _bayesian_update(self, experiences: List[Experience],
                        model: DiscreteGenerativeModel) -> Dict[str, float]:
        """Bayesian parameter update using conjugate priors"""
        # Accumulate sufficient statistics
        A_counts = torch.zeros_like(self.pA)
        B_counts = torch.zeros_like(self.pB)
        D_counts = torch.zeros_like(self.pD)

        for exp in experiences:
            # Extract indices
            if exp.state.dim() > 1:
                state_idx = torch.argmax(exp.state, dim=-1)
            else:
                state_idx = exp.state.long()

            if exp.observation.dim() > 1:
                obs_idx = torch.argmax(exp.observation, dim=-1)
            else:
                obs_idx = exp.observation.long()

            if exp.action.dim() > 1:
                action_idx = torch.argmax(exp.action, dim=-1)
            else:
                action_idx = exp.action.long()

            if exp.next_state.dim() > 1:
                next_state_idx = torch.argmax(exp.next_state, dim=-1)
            else:
                next_state_idx = exp.next_state.long()

            # Update counts
            A_counts[obs_idx, state_idx] += 1
            B_counts[next_state_idx, state_idx, action_idx] += 1

            # Initial state counts (only for first experiences)
            if exp.timestamp == 0:
                D_counts[state_idx] += 1

        # Update concentration parameters
        self.pA += A_counts * self.lr_A
        self.pB += B_counts * self.lr_B
        self.pD += D_counts * self.lr_D

        # Update model parameters (posterior mean)
        model.A = self._dirichlet_expectation(self.pA)
        model.B = self._dirichlet_expectation(self.pB)
        model.D = self._dirichlet_expectation(self.pD)

        # Compute update metrics
        metrics = {
            'A_update_norm': torch.norm(A_counts).item(),
            'B_update_norm': torch.norm(B_counts).item(),
            'D_update_norm': torch.norm(D_counts).item(),
            'A_entropy': self._compute_entropy(model.A).mean().item(),
            'B_entropy': self._compute_entropy(model.B).mean().item()
        }

        return metrics

    def _gradient_update(self, experiences: List[Experience],
                        model: DiscreteGenerativeModel) -> Dict[str, float]:
        """Gradient-based parameter update"""
        # Convert parameters to log space for unconstrained optimization
        log_A = torch.log(model.A + self.config.eps)
        log_B = torch.log(model.B + self.config.eps)
        log_D = torch.log(model.D + self.config.eps)

        # Compute gradients
        grad_A = torch.zeros_like(log_A)
        grad_B = torch.zeros_like(log_B)
        grad_D = torch.zeros_like(log_D)

        for exp in experiences:
            # Compute log-likelihood gradients
            # This is simplified - real implementation would use proper gradients
            state_prob = exp.state if exp.state.dim() > 1 else F.one_hot(exp.state.long(), self.num_states)
            obs_prob = exp.observation if exp.observation.dim() > 1 else F.one_hot(exp.observation.long(), self.num_observations)

            grad_A += torch.outer(obs_prob.squeeze(), state_prob.squeeze())

            if exp.timestamp == 0:
                grad_D += state_prob.squeeze()

        # Apply gradients with learning rates
        log_A += self.lr_A * grad_A
        log_B += self.lr_B * grad_B
        log_D += self.lr_D * grad_D

        # Convert back to probabilities
        model.A = F.softmax(log_A, dim=0)
        model.B = F.softmax(log_B, dim=0)
        model.D = F.softmax(log_D, dim=0)

        metrics = {
            'grad_A_norm': torch.norm(grad_A).item(),
            'grad_B_norm': torch.norm(grad_B).item(),
            'grad_D_norm': torch.norm(grad_D).item()
        }

        return metrics

    def _dirichlet_expectation(self, alpha: torch.Tensor) -> torch.Tensor:
        """Compute expectation of Dirichlet distribution"""
        if alpha.dim() == 2:
            return alpha / alpha.sum(dim=0, keepdim=True)
        elif alpha.dim() == 3:
            return alpha / alpha.sum(dim=0, keepdim=True)
        else:
            return alpha / alpha.sum()

    def _compute_entropy(self, probs: torch.Tensor) -> torch.Tensor:
        """Compute entropy of probability distribution"""
        safe_probs = probs + self.config.eps
        return -torch.sum(safe_probs * torch.log(safe_probs), dim=0)

    def _decay_learning_rates(self):
        """Apply learning rate decay"""
        self.lr_A = max(self.lr_A * self.config.decay_rate, self.config.min_learning_rate)
        self.lr_B = max(self.lr_B * self.config.decay_rate, self.config.min_learning_rate)
        self.lr_D = max(self.lr_D * self.config.decay_rate, self.config.min_learning_rate)

    def get_learning_rates(self) -> Dict[str, float]:
        """Get current learning rates"""
        return {
            'lr_A': self.lr_A,
            'lr_B': self.lr_B,
            'lr_D': self.lr_D
        }


class ContinuousParameterLearner(ParameterLearner):
    """
    Parameter learner for continuous generative models.

    Uses gradient-based optimization for neural network parameters.
    """

    def __init__(self, config: LearningConfig,
                 model: ContinuousGenerativeModel):
        super().__init__(config)

        self.model = model

        # Create optimizers for each network
        self.optimizers = {}
        if hasattr(model, 'transition_net'):
            self.optimizers['transition'] = torch.optim.Adam(
                model.transition_net.parameters(),
                lr=config.learning_rate_B
            )
        if hasattr(model, 'observation_net'):
            self.optimizers['observation'] = torch.optim.Adam(
                model.observation_net.parameters(),
                lr=config.learning_rate_A
            )
        if hasattr(model, 'prior_net'):
            self.optimizers['prior'] = torch.optim.Adam(
                model.prior_net.parameters(),
                lr=config.learning_rate_D
            )

        # Learning rate schedulers
        self.schedulers = {
            name: torch.optim.lr_scheduler.ExponentialLR(opt, self.config.decay_rate)
            for name, opt in self.optimizers.items()
        }

    def update_parameters(self, experiences: List[Experience],
                         generative_model: ContinuousGenerativeModel) -> Dict[str, float]:
        """
        Update continuous model parameters using gradient descent.

        Args:
            experiences: List of experiences
            generative_model: Continuous generative model to update

        Returns:
            Dictionary of update metrics
        """
        metrics = {}

        # Batch experiences
        states = torch.stack([exp.state for exp in experiences])
        actions = torch.stack([exp.action for exp in experiences])
        observations = torch.stack([exp.observation for exp in experiences])
        next_states = torch.stack([exp.next_state for exp in experiences])

        # Update transition model
        if 'transition' in self.optimizers:
            trans_loss = self._update_transition_model(
                states, actions, next_states, generative_model
            )
            metrics['transition_loss'] = trans_loss

        # Update observation model
        if 'observation' in self.optimizers:
            obs_loss = self._update_observation_model(
                states, observations, generative_model
            )
            metrics['observation_loss'] = obs_loss

        # Update prior model
        if 'prior' in self.optimizers:
            prior_loss = self._update_prior_model(
                states, generative_model
            )
            metrics['prior_loss'] = prior_loss

        # Step schedulers
        for scheduler in self.schedulers.values():
            scheduler.step()

        self.update_count += 1

        return metrics

    def _update_transition_model(self, states: torch.Tensor,
                                actions: torch.Tensor,
                                next_states: torch.Tensor,
                                model: ContinuousGenerativeModel) -> float:
        """Update transition network"""
        self.optimizers['transition'].zero_grad()

        # Predict next state
        state_action = torch.cat([states, actions], dim=-1)
        predicted_next = model.transition_net(state_action)

        # Compute loss
        loss = F.mse_loss(predicted_next, next_states)

        # Add regularization
        if self.config.use_regularization:
            l2_loss = sum(p.pow(2).sum() for p in model.transition_net.parameters())
            loss += self.config.l2_weight * l2_loss

        # Backward pass
        loss.backward()
        self.optimizers['transition'].step()

        return loss.item()

    def _update_observation_model(self, states: torch.Tensor,
                                observations: torch.Tensor,
                                model: ContinuousGenerativeModel) -> float:
        """Update observation network"""
        self.optimizers['observation'].zero_grad()

        # Predict observations
        predicted_obs = model.observation_net(states)

        # Compute loss
        loss = F.mse_loss(predicted_obs, observations)

        # Add regularization
        if self.config.use_regularization:
            l2_loss = sum(p.pow(2).sum() for p in model.observation_net.parameters())
            loss += self.config.l2_weight * l2_loss

        # Backward pass
        loss.backward()
        self.optimizers['observation'].step()

        return loss.item()

    def _update_prior_model(self, states: torch.Tensor,
                          model: ContinuousGenerativeModel) -> float:
        """Update prior network"""
        self.optimizers['prior'].zero_grad()

        # Compute prior log probability
        prior_params = model.prior_net(torch.zeros(1, model.dims.num_states))
        prior_mean = prior_params[:, :model.dims.num_states]
        prior_log_var = prior_params[:, model.dims.num_states:]

        # Compute KL divergence from standard normal
        kl_loss = -0.5 * torch.sum(
            1 + prior_log_var - prior_mean.pow(2) - prior_log_var.exp()
        )

        # Backward pass
        kl_loss.backward()
        self.optimizers['prior'].step()

        return kl_loss.item()

    def get_learning_rates(self) -> Dict[str, float]:
        """Get current learning rates"""
        rates = {}
        for name, optimizer in self.optimizers.items():
            rates[f'lr_{name}'] = optimizer.param_groups[0]['lr']
        return rates


class OnlineParameterLearner:
    """
    Online parameter learning system that updates models in real-time.

    Combines experience replay with immediate updates for rapid adaptation.
    """

    def __init__(self, config: LearningConfig,
                 generative_model: GenerativeModel,
                 parameter_learner: ParameterLearner):
        self.config = config
        self.generative_model = generative_model
        self.parameter_learner = parameter_learner
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

        # Experience replay buffer
        if config.use_experience_replay:
            self.replay_buffer = ExperienceBuffer(config.replay_buffer_size)
        else:
            self.replay_buffer = None

        # Update tracking
        self.total_experiences = 0
        self.update_metrics = []

    def observe(self, state: torch.Tensor,
               action: torch.Tensor,
               observation: torch.Tensor,
               next_state: torch.Tensor,
               reward: Optional[torch.Tensor] = None):
        """
        Process new experience and potentially update parameters.

        Args:
            state: Current state
            action: Action taken
            observation: Resulting observation
            next_state: Next state
            reward: Optional reward signal
        """
        # Create experience
        experience = Experience(
            state=state.detach(),
            action=action.detach(),
            observation=observation.detach(),
            next_state=next_state.detach(),
            reward=reward.detach() if reward is not None else None,
            timestamp=self.total_experiences
        )

        # Add to replay buffer
        if self.replay_buffer is not None:
            self.replay_buffer.add(experience)

        self.total_experiences += 1

        # Check if we should update
        if self._should_update():
            metrics = self.update()
            self.update_metrics.append(metrics)

    def update(self) -> Dict[str, float]:
        """Perform parameter update"""
        if self.replay_buffer is not None and len(self.replay_buffer) >= self.config.min_buffer_size:
            # Sample batch from replay buffer
            experiences = self.replay_buffer.sample(self.config.batch_size)
        else:
            # Use most recent experience
            experiences = [self.replay_buffer.buffer[-1]] if self.replay_buffer else []

        if experiences:
            metrics = self.parameter_learner.update_parameters(
                experiences, self.generative_model
            )
            metrics['total_experiences'] = self.total_experiences
            metrics['buffer_size'] = len(self.replay_buffer) if self.replay_buffer else 0
            return metrics

        return {}

    def _should_update(self) -> bool:
        """Determine if parameters should be updated"""
        if self.replay_buffer is None:
            return True  # Always update without replay buffer

        # Update based on frequency and buffer size
        return (
            len(self.replay_buffer) >= self.config.min_buffer_size and
            self.total_experiences % self.config.update_frequency == 0
        )

    def get_statistics(self) -> Dict[str, Any]:
        """Get learning statistics"""
        stats = {
            'total_experiences': self.total_experiences,
            'buffer_size': len(self.replay_buffer) if self.replay_buffer else 0,
            'num_updates': len(self.update_metrics),
            'learning_rates': self.parameter_learner.get_learning_rates()
        }

        # Aggregate update metrics
        if self.update_metrics:
            recent_metrics = self.update_metrics[-10:]  # Last 10 updates
            for key in recent_metrics[0]:
                values = [m[key] for m in recent_metrics]
                stats[f'avg_{key}'] = np.mean(values)
                stats[f'std_{key}'] = np.std(values)

        return stats


def create_parameter_learner(learner_type: str,
                           config: Optional[LearningConfig] = None,
                           **kwargs) -> Union[ParameterLearner, OnlineParameterLearner]:
    """
    Factory function to create parameter learners.

    Args:
        learner_type: Type of learner ('discrete', 'continuous', 'online')
        config: Learning configuration
        **kwargs: Additional parameters

    Returns:
        Parameter learner instance
    """
    if config is None:
        config = LearningConfig()

    if learner_type == 'discrete':
        model_dims = kwargs.get('model_dims')
        if model_dims is None:
            raise ValueError("Discrete learner requires model_dims")

        return DiscreteParameterLearner(config, model_dims)

    elif learner_type == 'continuous':
        model = kwargs.get('model')
        if model is None:
            raise ValueError("Continuous learner requires model")

        return ContinuousParameterLearner(config, model)

    elif learner_type == 'online':
        generative_model = kwargs.get('generative_model')
        if generative_model is None:
            raise ValueError("Online learner requires generative_model")

        # Create appropriate parameter learner
        if isinstance(generative_model, DiscreteGenerativeModel):
            model_dims = {
                'num_states': generative_model.dims.num_states,
                'num_observations': generative_model.dims.num_observations,
                'num_actions': generative_model.dims.num_actions
            }
            param_learner = DiscreteParameterLearner(config, model_dims)
        else:
            param_learner = ContinuousParameterLearner(config, generative_model)

        return OnlineParameterLearner(config, generative_model, param_learner)

    else:
        raise ValueError(f"Unknown learner type: {learner_type}")


# Example usage
if __name__ == "__main__":
    from .generative_model import DiscreteGenerativeModel, ModelDimensions, ModelParameters

    # Configuration
    config = LearningConfig(
        learning_rate_A=0.01,
        use_bayesian_learning=True,
        use_experience_replay=True,
        use_gpu=False
    )

    # Create generative model
    dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
    params = ModelParameters(use_gpu=False)
    gen_model = DiscreteGenerativeModel(dims, params)

    # Create online learner
    learner = create_parameter_learner(
        'online',
        config,
        generative_model=gen_model
    )

    # Simulate experience
    state = torch.tensor([1, 0, 0, 0], dtype=torch.float32)
    action = torch.tensor([0, 1], dtype=torch.float32)
    observation = torch.tensor([0, 1, 0], dtype=torch.float32)
    next_state = torch.tensor([0, 1, 0, 0], dtype=torch.float32)

    # Learn from experience
    learner.observe(state, action, observation, next_state)

    # Get statistics
    stats = learner.get_statistics()
    print(f"Learning statistics: {stats}")
