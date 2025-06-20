"""
Variational Bayes Inference Algorithms for Active Inference

This module implements various approximate Bayesian inference algorithms
for updating beliefs about hidden states in Active Inference agents.
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Optional, Union, Tuple, Any
from dataclasses import dataclass
import numpy as np
import logging
from abc import ABC, abstractmethod
from .generative-model import GenerativeModel, DiscreteGenerativeModel
logger = logging.getLogger(__name__)

@dataclass
class InferenceConfig:
    """Configuration for inference algorithms"""
    num_iterations: int = 16
    convergence_threshold: float = 0.0001
    learning_rate: float = 0.1
    gradient_clip: float = 1.0
    use_natural_gradient: bool = True
    damping_factor: float = 0.1
    momentum: float = 0.9
    use_gpu: bool = True
    dtype: torch.dtype = torch.float32

class InferenceAlgorithm(ABC):
    """Abstract base class for inference algorithms"""

    def __init__(self, config: InferenceConfig):
        self.config = config
        self.device = torch.device('cuda' if config.use_gpu and torch.cuda.is_available() else 'cpu')

    @abstractmethod
    def infer_states(self, observations: torch.Tensor, generative_model: GenerativeModel, prior: Optional[torch.Tensor]=None) -> torch.Tensor:
        """Infer hidden states given observations"""
        pass

    @abstractmethod
    def compute_free_energy(self, beliefs: torch.Tensor, observations: torch.Tensor, generative_model: GenerativeModel) -> torch.Tensor:
        """Compute variational free energy"""
        pass

class VariationalMessagePassing(InferenceAlgorithm):
    """
    Variational Message Passing for discrete state spaces.

    Implements belief propagation with messages between factors and variables
    in the generative model's factor graph representation.
    """

    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.eps = 1e-16

    def infer_states(self, observations: torch.Tensor, generative_model: DiscreteGenerativeModel, prior: Optional[torch.Tensor]=None) -> torch.Tensor:
        """
        Perform variational message passing to infer states.

        Args:
            observations: Observation indices or distributions [batch_size] or [batch_size x num_obs]
            generative_model: Discrete generative model
            prior: Optional prior beliefs [batch_size x num_states] or [num_states]

        Returns:
            beliefs: Posterior beliefs over states [batch_size x num_states] or [num_states]
        """
        if observations.dim() == 0:
            observations = observations.unsqueeze(0)
            single_obs = True
        else:
            single_obs = False
        batch_size = observations.shape[0]
        num_states = generative_model.dims.num_states
        if prior is not None:
            beliefs = prior.to(self.device)
            if beliefs.dim() == 1 and batch_size > 1:
                beliefs = beliefs.unsqueeze(0).expand(batch_size, -1)
        else:
            beliefs = torch.ones(batch_size, num_states, device=self.device) / num_states
        A = generative_model.A.to(self.device)
        for iteration in range(self.config.num_iterations):
            beliefs_old = beliefs.clone()
            if observations.dtype == torch.long:
                obs_messages = torch.zeros(batch_size, num_states, device=self.device)
                for b in range(batch_size):
                    obs_messages[b] = A[observations[b], :]
            else:
                obs_messages = observations @ A
            if prior is not None:
                beliefs = obs_messages * beliefs
            else:
                beliefs = obs_messages * generative_model.D.to(self.device)
            beliefs = self._normalize(beliefs)
            if torch.max(torch.abs(beliefs - beliefs_old)) < self.config.convergence_threshold:
                logger.debug(f'VMP converged in {iteration + 1} iterations')
                break
        return beliefs.squeeze(0) if single_obs else beliefs

    def compute_free_energy(self, beliefs: torch.Tensor, observations: torch.Tensor, generative_model: DiscreteGenerativeModel) -> torch.Tensor:
        """
        Compute variational free energy F = E_q[log q] - E_q[log p(o,s)]

        Args:
            beliefs: Beliefs over states q(s) [batch_size x num_states] or [num_states]
            observations: Observations [batch_size] or [batch_size x num_obs]
            generative_model: Generative model

        Returns:
            free_energy: Variational free energy [batch_size] or scalar
        """
        if beliefs.dim() == 1:
            beliefs = beliefs.unsqueeze(0)
            single = True
        else:
            single = False
        entropy = -torch.sum(beliefs * torch.log(beliefs + self.eps), dim=-1)
        A = generative_model.A.to(self.device)
        if observations.dtype == torch.long:
            log_likelihood = torch.zeros(beliefs.shape[0], device=self.device)
            for b in range(beliefs.shape[0]):
                obs_prob = A[observations[b], :] @ beliefs[b]
                log_likelihood[b] = torch.log(obs_prob + self.eps)
        else:
            obs_probs = beliefs @ A.T
            log_likelihood = torch.sum(observations * torch.log(obs_probs + self.eps), dim=-1)
        log_prior = torch.sum(beliefs * torch.log(generative_model.D.to(self.device) + self.eps), dim=-1)
        free_energy = -entropy - log_likelihood - log_prior
        return free_energy.squeeze() if single else free_energy

    def _normalize(self, tensor: torch.Tensor) -> torch.Tensor:
        """Normalize probability distributions"""
        return tensor / (tensor.sum(dim=-1, keepdim=True) + self.eps)

class BeliefPropagation(InferenceAlgorithm):
    """
    Belief Propagation algorithm for factor graphs.

    Implements sum-product message passing for exact inference
    in tree-structured graphs and approximate inference in loopy graphs.
    """

    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.eps = 1e-16

    def infer_states(self, observations: torch.Tensor, generative_model: DiscreteGenerativeModel, prior: Optional[torch.Tensor]=None, actions: Optional[torch.Tensor]=None, previous_states: Optional[torch.Tensor]=None) -> torch.Tensor:
        """
        Perform belief propagation considering temporal dynamics.

        Args:
            observations: Current observations
            generative_model: Generative model
            prior: Prior beliefs
            actions: Actions taken (for transition model)
            previous_states: Previous state beliefs

        Returns:
            beliefs: Updated beliefs
        """
        vmp = VariationalMessagePassing(self.config)
        beliefs = vmp.infer_states(observations, generative_model, prior)
        if actions is not None and previous_states is not None:
            beliefs = self._temporal_update(beliefs, previous_states, actions, generative_model)
        return beliefs

    def _temporal_update(self, current_beliefs: torch.Tensor, previous_beliefs: torch.Tensor, actions: torch.Tensor, model: DiscreteGenerativeModel) -> torch.Tensor:
        """Update beliefs using temporal transition model"""
        predicted_current = model.transition_model(previous_beliefs, actions)
        combined_beliefs = current_beliefs * predicted_current
        return combined_beliefs / (combined_beliefs.sum(dim=-1, keepdim=True) + self.eps)

    def compute_free_energy(self, beliefs: torch.Tensor, observations: torch.Tensor, generative_model: DiscreteGenerativeModel) -> torch.Tensor:
        """Compute free energy (delegates to VMP)"""
        vmp = VariationalMessagePassing(self.config)
        return vmp.compute_free_energy(beliefs, observations, generative_model)

class GradientDescentInference(InferenceAlgorithm):
    """
    Gradient-based inference for continuous state spaces.

    Uses gradient descent on the variational free energy to optimize beliefs.
    """

    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.momentum_buffer = None

    def infer_states(self, observations: torch.Tensor, generative_model: GenerativeModel, prior: Optional[torch.Tensor]=None) -> torch.Tensor:
        """
        Perform gradient descent on free energy to infer states.

        For continuous models, returns mean and variance of Gaussian beliefs.
        """
        if prior is not None:
            if isinstance(prior, tuple):
                mean, log_var = prior
                mean = mean.to(self.device).requires_grad_(True)
                log_var = log_var.to(self.device).requires_grad_(True)
            else:
                mean = prior.to(self.device).requires_grad_(True)
                log_var = torch.zeros_like(mean).requires_grad_(True)
        elif hasattr(generative_model, 'D_mean'):
            mean = generative_model.D_mean.clone().detach().requires_grad_(True)
            log_var = generative_model.D_log_var.clone().detach().requires_grad_(True)
        else:
            mean = torch.zeros(generative_model.dims.num_states, device=self.device).requires_grad_(True)
            log_var = torch.zeros_like(mean).requires_grad_(True)
        optimizer = torch.optim.Adam([mean, log_var], lr=self.config.learning_rate)
        for iteration in range(self.config.num_iterations):
            optimizer.zero_grad()
            std = torch.exp(0.5 * log_var)
            eps = torch.randn_like(std)
            states = mean + eps * std
            free_energy = self._compute_continuous_free_energy(states, mean, log_var, observations, generative_model)
            free_energy.backward()
            torch.nn.utils.clip_grad_norm_([mean, log_var], self.config.gradient_clip)
            optimizer.step()
            if iteration > 0:
                param_change = torch.max(torch.abs(mean - mean_old))
                if param_change < self.config.convergence_threshold:
                    logger.debug(f'Gradient descent converged in {iteration + 1} iterations')
                    break
            mean_old = mean.clone()
        return (mean.detach(), torch.exp(log_var).detach())

    def _compute_continuous_free_energy(self, states: torch.Tensor, mean: torch.Tensor, log_var: torch.Tensor, observations: torch.Tensor, model: GenerativeModel) -> torch.Tensor:
        """Compute free energy for continuous states"""
        if hasattr(model, 'D_mean'):
            prior_mean = model.D_mean
            prior_log_var = model.D_log_var
            kl_div = 0.5 * torch.sum(torch.exp(log_var - prior_log_var) + (mean - prior_mean) ** 2 / torch.exp(prior_log_var) - 1 + prior_log_var - log_var)
        else:
            kl_div = 0.5 * torch.sum(torch.exp(log_var) + mean ** 2 - 1 - log_var)
        obs_mean, obs_var = model.observation_model(states)
        nll = 0.5 * torch.sum((observations - obs_mean) ** 2 / obs_var + torch.log(obs_var))
        return kl_div + nll

    def compute_free_energy(self, beliefs: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], observations: torch.Tensor, generative_model: GenerativeModel) -> torch.Tensor:
        """Compute free energy for given beliefs"""
        if isinstance(beliefs, tuple):
            mean, var = beliefs
            log_var = torch.log(var)
            states = mean
        else:
            states = beliefs
            mean = beliefs
            log_var = torch.zeros_like(mean)
        return self._compute_continuous_free_energy(states, mean, log_var, observations, generative_model)

class NaturalGradientInference(GradientDescentInference):
    """
    Natural gradient descent for more efficient inference.

    Uses the Fisher information matrix to perform gradient descent
    in the natural parameter space.
    """

    def __init__(self, config: InferenceConfig):
        super().__init__(config)
        self.fisher_moving_avg = None
        self.fisher_alpha = 0.95

    def _natural_gradient_step(self, grad_mean: torch.Tensor, grad_log_var: torch.Tensor, mean: torch.Tensor, log_var: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Compute natural gradient using Fisher information matrix.

        For Gaussian distributions, the Fisher information has a simple form.
        """
        var = torch.exp(log_var)
        nat_grad_mean = grad_mean * var
        nat_grad_log_var = grad_log_var * var / 2
        if self.config.damping_factor > 0:
            nat_grad_mean = nat_grad_mean / (1 + self.config.damping_factor)
            nat_grad_log_var = nat_grad_log_var / (1 + self.config.damping_factor)
        return (nat_grad_mean, nat_grad_log_var)

    def infer_states(self, observations: torch.Tensor, generative_model: GenerativeModel, prior: Optional[torch.Tensor]=None) -> torch.Tensor:
        """
        Perform natural gradient descent for inference.
        """
        if prior is not None:
            if isinstance(prior, tuple):
                mean, log_var = prior
                mean = mean.to(self.device).requires_grad_(True)
                log_var = log_var.to(self.device).requires_grad_(True)
            else:
                mean = prior.to(self.device).requires_grad_(True)
                log_var = torch.zeros_like(mean).requires_grad_(True)
        elif hasattr(generative_model, 'D_mean'):
            mean = generative_model.D_mean.clone().detach().requires_grad_(True)
            log_var = generative_model.D_log_var.clone().detach().requires_grad_(True)
        else:
            mean = torch.zeros(generative_model.dims.num_states, device=self.device).requires_grad_(True)
            log_var = torch.zeros_like(mean).requires_grad_(True)
        for iteration in range(self.config.num_iterations):
            std = torch.exp(0.5 * log_var)
            eps = torch.randn_like(std)
            states = mean + eps * std
            free_energy = self._compute_continuous_free_energy(states, mean, log_var, observations, generative_model)
            free_energy.backward()
            with torch.no_grad():
                nat_grad_mean, nat_grad_log_var = self._natural_gradient_step(mean.grad, log_var.grad, mean, log_var)
                mean -= self.config.learning_rate * nat_grad_mean
                log_var -= self.config.learning_rate * nat_grad_log_var
                mean.grad.zero_()
                log_var.grad.zero_()
            if iteration > 0:
                param_change = torch.max(torch.abs(mean - mean_old))
                if param_change < self.config.convergence_threshold:
                    logger.debug(f'Natural gradient converged in {iteration + 1} iterations')
                    break
            mean_old = mean.clone()
        return (mean.detach(), torch.exp(log_var).detach())

class ExpectationMaximization(InferenceAlgorithm):
    """
    Expectation-Maximization algorithm for parameter learning and inference.

    Alternates between E-step (state inference) and M-step (parameter updates).
    """

    def __init__(self, config: InferenceConfig, base_algorithm: Optional[InferenceAlgorithm]=None):
        super().__init__(config)
        self.base_algorithm = base_algorithm or VariationalMessagePassing(config)

    def infer_states(self, observations: torch.Tensor, generative_model: GenerativeModel, prior: Optional[torch.Tensor]=None) -> torch.Tensor:
        """E-step: Infer states using base algorithm"""
        return self.base_algorithm.infer_states(observations, generative_model, prior)

    def update_parameters(self, observations: List[torch.Tensor], beliefs: List[torch.Tensor], generative_model: GenerativeModel, actions: Optional[List[torch.Tensor]]=None):
        """
        M-step: Update model parameters given beliefs.

        Args:
            observations: Sequence of observations
            beliefs: Sequence of state beliefs
            generative_model: Model to update
            actions: Optional sequence of actions
        """
        if hasattr(generative_model, 'update_model'):
            if actions is not None:
                generative_model.update_model(observations, beliefs, actions)
            else:
                generative_model.update_model(observations, beliefs, [0] * (len(beliefs) - 1))
        else:
            logger.warning('Model does not support parameter updates')

    def em_iteration(self, observations: List[torch.Tensor], generative_model: GenerativeModel, initial_beliefs: Optional[List[torch.Tensor]]=None, actions: Optional[List[torch.Tensor]]=None) -> List[torch.Tensor]:
        """
        Perform one complete EM iteration.

        Returns:
            Updated beliefs after E-step
        """
        beliefs = []
        for t, obs in enumerate(observations):
            if initial_beliefs and t < len(initial_beliefs):
                prior = initial_beliefs[t]
            else:
                prior = None
            belief = self.infer_states(obs, generative_model, prior)
            beliefs.append(belief)
        self.update_parameters(observations, beliefs, generative_model, actions)
        return beliefs

    def compute_free_energy(self, beliefs: torch.Tensor, observations: torch.Tensor, generative_model: GenerativeModel) -> torch.Tensor:
        """Compute free energy using base algorithm"""
        return self.base_algorithm.compute_free_energy(beliefs, observations, generative_model)

class ParticleFilterInference(InferenceAlgorithm):
    """
    Sequential Monte Carlo (Particle Filter) for non-linear, non-Gaussian inference.

    Maintains a set of weighted particles to represent the posterior distribution.
    """

    def __init__(self, config: InferenceConfig, num_particles: int=100):
        super().__init__(config)
        self.num_particles = num_particles
        self.eps = 1e-16

    def infer_states(self, observations: torch.Tensor, generative_model: GenerativeModel, prior: Optional[torch.Tensor]=None, particles: Optional[torch.Tensor]=None, weights: Optional[torch.Tensor]=None) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Perform particle filter inference.

        Returns:
            mean: Mean of particle distribution
            particles: Updated particles
            weights: Updated weights
        """
        device = self.device
        if particles is None:
            if prior is not None:
                if isinstance(prior, tuple):
                    mean, var = prior
                    std = torch.sqrt(var)
                    particles = mean + std * torch.randn(self.num_particles, mean.shape[-1], device=device)
                else:
                    particles = prior + 0.1 * torch.randn(self.num_particles, prior.shape[-1], device=device)
            elif hasattr(generative_model, 'D'):
                probs = generative_model.D.to(device)
                particles = torch.multinomial(probs, self.num_particles, replacement=True).float()
            else:
                mean = generative_model.D_mean.to(device)
                std = torch.exp(0.5 * generative_model.D_log_var).to(device)
                particles = mean + std * torch.randn(self.num_particles, mean.shape[-1], device=device)
        if weights is None:
            weights = torch.ones(self.num_particles, device=device) / self.num_particles
        if hasattr(generative_model, 'A'):
            particle_indices = particles.long()
            A = generative_model.A.to(device)
            if observations.dtype == torch.long:
                likelihoods = A[observations, particle_indices]
            else:
                likelihoods = torch.sum(observations * A[:, particle_indices], dim=0)
        else:
            obs_mean, obs_var = generative_model.observation_model(particles)
            likelihoods = torch.exp(-0.5 * torch.sum((observations - obs_mean) ** 2 / obs_var, dim=-1))
        weights = weights * likelihoods
        weights = weights / (weights.sum() + self.eps)
        ess = 1.0 / (torch.sum(weights ** 2) + self.eps)
        if ess < self.num_particles / 2:
            particles, weights = self._resample(particles, weights)
        if hasattr(generative_model, 'A'):
            states = torch.zeros(generative_model.dims.num_states, device=device)
            for i in range(self.num_particles):
                states[particle_indices[i]] += weights[i]
            mean = states
        else:
            mean = torch.sum(particles * weights.unsqueeze(-1), dim=0)
        return (mean, particles, weights)

    def _resample(self, particles: torch.Tensor, weights: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Systematic resampling of particles"""
        device = particles.device
        N = self.num_particles
        cumsum = torch.cumsum(weights, dim=0)
        positions = (torch.arange(N, device=device).float() + torch.rand(1, device=device)) / N
        indices = torch.searchsorted(cumsum, positions)
        indices = torch.clamp(indices, 0, N - 1)
        new_particles = particles[indices]
        new_weights = torch.ones(N, device=device) / N
        return (new_particles, new_weights)

    def compute_free_energy(self, beliefs: torch.Tensor, observations: torch.Tensor, generative_model: GenerativeModel) -> torch.Tensor:
        """
        Approximate free energy computation using particles.

        This is an approximation since particle filters don't directly optimize free energy.
        """
        if isinstance(beliefs, tuple) and len(beliefs) == 3:
            mean, particles, weights = beliefs
        else:
            mean = beliefs
            particles = None
            weights = None
        if particles is not None and weights is not None:
            entropy = -torch.sum(weights * torch.log(weights + self.eps))
            if hasattr(generative_model, 'A'):
                A = generative_model.A.to(self.device)
                particle_indices = particles.long()
                if observations.dtype == torch.long:
                    log_likelihoods = torch.log(A[observations, particle_indices] + self.eps)
                else:
                    log_likelihoods = torch.log(torch.sum(observations * A[:, particle_indices], dim=0) + self.eps)
            else:
                obs_mean, obs_var = generative_model.observation_model(particles)
                log_likelihoods = -0.5 * torch.sum((observations - obs_mean) ** 2 / obs_var + torch.log(obs_var), dim=-1)
            expected_log_likelihood = torch.sum(weights * log_likelihoods)
            free_energy = -entropy - expected_log_likelihood
        elif hasattr(generative_model, 'A'):
            vmp = VariationalMessagePassing(self.config)
            free_energy = vmp.compute_free_energy(mean, observations, generative_model)
        else:
            gd = GradientDescentInference(self.config)
            free_energy = gd.compute_free_energy(mean, observations, generative_model)
        return free_energy

def create_inference_algorithm(algorithm_type: str, config: Optional[InferenceConfig]=None, **kwargs) -> InferenceAlgorithm:
    """
    Factory function to create inference algorithms.

    Args:
        algorithm_type: Type of algorithm ('vmp', 'bp', 'gradient', 'natural', 'em', 'particle')
        config: Inference configuration
        **kwargs: Algorithm-specific parameters

    Returns:
        Inference algorithm instance
    """
    if config is None:
        config = InferenceConfig()
    if algorithm_type == 'vmp':
        return VariationalMessagePassing(config)
    elif algorithm_type == 'bp':
        return BeliefPropagation(config)
    elif algorithm_type == 'gradient':
        return GradientDescentInference(config)
    elif algorithm_type == 'natural':
        return NaturalGradientInference(config)
    elif algorithm_type == 'em':
        base_algo = kwargs.get('base_algorithm')
        return ExpectationMaximization(config, base_algo)
    elif algorithm_type == 'particle':
        num_particles = kwargs.get('num_particles', 100)
        return ParticleFilterInference(config, num_particles)
    else:
        raise ValueError(f'Unknown algorithm type: {algorithm_type}')
if __name__ == '__main__':
    from .generative-model import DiscreteGenerativeModel, ModelDimensions, ModelParameters
    dims = ModelDimensions(num_states=5, num_observations=3, num_actions=2)
    params = ModelParameters(use_gpu=False)
    model = DiscreteGenerativeModel(dims, params)
    config = InferenceConfig(num_iterations=10, use_gpu=False)
    vmp = VariationalMessagePassing(config)
    observation = torch.tensor(1)
    beliefs = vmp.infer_states(observation, model)
    print(f'Inferred beliefs: {beliefs}')
    free_energy = vmp.compute_free_energy(beliefs, observation, model)
    print(f'Free energy: {free_energy.item()}')
