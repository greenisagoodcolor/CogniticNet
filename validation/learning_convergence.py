"""
Learning Convergence Validation Module
Tests and monitors learning algorithm convergence in Active Inference agents.
"""

import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class ConvergenceMetrics:
    """Metrics for tracking learning convergence."""

    iteration: int
    loss: float
    free_energy: float
    gradient_norm: float
    parameter_change: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "iteration": self.iteration,
            "loss": self.loss,
            "free_energy": self.free_energy,
            "gradient_norm": self.gradient_norm,
            "parameter_change": self.parameter_change,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ConvergenceReport:
    """Report on learning convergence status."""

    is_converged: bool
    convergence_rate: float
    oscillation_detected: bool
    plateau_detected: bool
    divergence_risk: float
    metrics_history: List[ConvergenceMetrics]
    recommendations: List[str]

    def summary(self) -> str:
        """Generate human-readable summary."""
        status = "CONVERGED" if self.is_converged else "NOT CONVERGED"
        return (
            f"Convergence Status: {status}\n"
            f"Convergence Rate: {self.convergence_rate:.4f}\n"
            f"Oscillation: {'Yes' if self.oscillation_detected else 'No'}\n"
            f"Plateau: {'Yes' if self.plateau_detected else 'No'}\n"
            f"Divergence Risk: {self.divergence_risk:.2%}\n"
            f"Recommendations: {', '.join(self.recommendations)}"
        )


class LearningConvergenceValidator:
    """
    Validates that learning algorithms converge properly.

    Monitors:
    - Loss function trends
    - Free energy minimization
    - Parameter stability
    - Gradient behavior
    """

    def __init__(
        self, patience: int = 50, min_delta: float = 1e-4, window_size: int = 20
    ):
        self.patience = patience
        self.min_delta = min_delta
        self.window_size = window_size
        self.history: deque = deque(maxlen=1000)

        # Convergence criteria
        self.loss_threshold = 1e-3
        self.gradient_threshold = 1e-5
        self.oscillation_threshold = 0.1
        self.plateau_threshold = 0.01

    def track_iteration(
        self,
        iteration: int,
        loss: float,
        free_energy: float,
        gradients: Optional[np.ndarray] = None,
        parameters: Optional[np.ndarray] = None,
        prev_parameters: Optional[np.ndarray] = None,
    ) -> ConvergenceMetrics:
        """
        Track metrics for a single learning iteration.

        Args:
            iteration: Current iteration number
            loss: Current loss value
            free_energy: Current free energy
            gradients: Current gradient values
            parameters: Current parameter values
            prev_parameters: Previous parameter values

        Returns:
            ConvergenceMetrics for this iteration
        """
        # Calculate gradient norm
        gradient_norm = np.linalg.norm(gradients) if gradients is not None else 0.0

        # Calculate parameter change
        parameter_change = 0.0
        if parameters is not None and prev_parameters is not None:
            parameter_change = np.linalg.norm(parameters - prev_parameters)

        metrics = ConvergenceMetrics(
            iteration=iteration,
            loss=loss,
            free_energy=free_energy,
            gradient_norm=gradient_norm,
            parameter_change=parameter_change,
        )

        self.history.append(metrics)
        return metrics

    def check_convergence(self, min_iterations: int = 100) -> ConvergenceReport:
        """
        Check if learning has converged based on tracked metrics.

        Args:
            min_iterations: Minimum iterations before checking convergence

        Returns:
            ConvergenceReport with convergence analysis
        """
        if len(self.history) < min_iterations:
            return ConvergenceReport(
                is_converged=False,
                convergence_rate=0.0,
                oscillation_detected=False,
                plateau_detected=False,
                divergence_risk=0.0,
                metrics_history=list(self.history),
                recommendations=["Insufficient iterations for convergence analysis"],
            )

        # Extract recent metrics
        recent_metrics = list(self.history)[-self.window_size :]
        losses = [m.loss for m in recent_metrics]
        free_energies = [m.free_energy for m in recent_metrics]
        gradient_norms = [m.gradient_norm for m in recent_metrics]

        # Check convergence criteria
        is_converged = self._check_loss_convergence(losses)
        convergence_rate = self._calculate_convergence_rate(losses)
        oscillation_detected = self._detect_oscillation(losses)
        plateau_detected = self._detect_plateau(losses)
        divergence_risk = self._calculate_divergence_risk(losses, free_energies)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            is_converged,
            oscillation_detected,
            plateau_detected,
            divergence_risk,
            gradient_norms,
        )

        return ConvergenceReport(
            is_converged=is_converged,
            convergence_rate=convergence_rate,
            oscillation_detected=oscillation_detected,
            plateau_detected=plateau_detected,
            divergence_risk=divergence_risk,
            metrics_history=list(self.history),
            recommendations=recommendations,
        )

    def _check_loss_convergence(self, losses: List[float]) -> bool:
        """Check if loss has converged."""
        if not losses:
            return False

        # Check if loss is below threshold
        if losses[-1] > self.loss_threshold:
            return False

        # Check if loss is stable
        if len(losses) < self.patience:
            return False

        recent_losses = losses[-self.patience :]
        loss_std = np.std(recent_losses)
        loss_trend = np.polyfit(range(len(recent_losses)), recent_losses, 1)[0]

        return loss_std < self.min_delta and abs(loss_trend) < self.min_delta

    def _calculate_convergence_rate(self, losses: List[float]) -> float:
        """Calculate convergence rate from loss history."""
        if len(losses) < 2:
            return 0.0

        # Fit exponential decay: loss = a * exp(-rate * t) + c
        try:
            t = np.arange(len(losses))
            log_losses = np.log(np.array(losses) - min(losses) + 1e-10)
            rate = -np.polyfit(t, log_losses, 1)[0]
            return max(0.0, rate)
        except:
            return 0.0

    def _detect_oscillation(self, losses: List[float]) -> bool:
        """Detect oscillation in loss values."""
        if len(losses) < 10:
            return False

        # Count sign changes in loss differences
        diffs = np.diff(losses)
        sign_changes = np.sum(np.diff(np.sign(diffs)) != 0)

        # High frequency of sign changes indicates oscillation
        oscillation_ratio = sign_changes / (len(diffs) - 1)
        return oscillation_ratio > self.oscillation_threshold

    def _detect_plateau(self, losses: List[float]) -> bool:
        """Detect if learning has plateaued."""
        if len(losses) < self.patience:
            return False

        recent_losses = losses[-self.patience :]
        loss_range = max(recent_losses) - min(recent_losses)
        mean_loss = np.mean(recent_losses)

        # Plateau if range is very small relative to mean
        return loss_range < self.plateau_threshold * mean_loss

    def _calculate_divergence_risk(
        self, losses: List[float], free_energies: List[float]
    ) -> float:
        """Calculate risk of divergence."""
        if len(losses) < 10:
            return 0.0

        # Check if losses are increasing
        loss_trend = np.polyfit(range(len(losses)), losses, 1)[0]

        # Check if free energy is increasing
        fe_trend = 0.0
        if len(free_energies) >= 10:
            fe_trend = np.polyfit(range(len(free_energies)), free_energies, 1)[0]

        # Risk based on positive trends
        loss_risk = max(0.0, loss_trend) / (abs(loss_trend) + 1e-10)
        fe_risk = max(0.0, fe_trend) / (abs(fe_trend) + 1e-10)

        return 0.7 * loss_risk + 0.3 * fe_risk

    def _generate_recommendations(
        self,
        is_converged: bool,
        oscillation_detected: bool,
        plateau_detected: bool,
        divergence_risk: float,
        gradient_norms: List[float],
    ) -> List[str]:
        """Generate recommendations based on convergence analysis."""
        recommendations = []

        if not is_converged:
            if oscillation_detected:
                recommendations.append("Reduce learning rate to address oscillation")

            if plateau_detected:
                recommendations.append(
                    "Consider increasing learning rate or using momentum"
                )
                recommendations.append("Check if model capacity is sufficient")

            if divergence_risk > 0.5:
                recommendations.append(
                    "High divergence risk - reduce learning rate immediately"
                )
                recommendations.append("Check for numerical instabilities")

            if gradient_norms and np.mean(gradient_norms) < self.gradient_threshold:
                recommendations.append("Gradients vanishing - check model architecture")

            if gradient_norms and np.max(gradient_norms) > 100:
                recommendations.append(
                    "Gradient explosion detected - use gradient clipping"
                )

        if not recommendations:
            recommendations.append("Learning is progressing normally")

        return recommendations


class ActiveInferenceConvergenceMonitor:
    """
    Specialized convergence monitoring for Active Inference algorithms.
    """

    def __init__(self, validator: LearningConvergenceValidator):
        self.validator = validator
        self.vfe_history: deque = deque(maxlen=1000)  # Variational Free Energy
        self.efe_history: deque = deque(maxlen=1000)  # Expected Free Energy

    def track_active_inference_step(
        self,
        iteration: int,
        observations: np.ndarray,
        beliefs: np.ndarray,
        preferences: np.ndarray,
        actions: np.ndarray,
    ) -> Dict[str, float]:
        """
        Track Active Inference specific metrics.

        Args:
            iteration: Current iteration
            observations: Current observations
            beliefs: Current belief state
            preferences: Agent preferences
            actions: Selected actions

        Returns:
            Dictionary of Active Inference metrics
        """
        # Calculate Variational Free Energy
        vfe = self._calculate_vfe(observations, beliefs)
        self.vfe_history.append(vfe)

        # Calculate Expected Free Energy
        efe = self._calculate_efe(beliefs, preferences, actions)
        self.efe_history.append(efe)

        # Track in main validator
        self.validator.track_iteration(
            iteration=iteration,
            loss=vfe,  # VFE serves as loss
            free_energy=efe,
            gradients=self._estimate_gradients(beliefs),
            parameters=beliefs.flatten(),
        )

        return {
            "vfe": vfe,
            "efe": efe,
            "belief_entropy": self._calculate_entropy(beliefs),
            "action_entropy": self._calculate_entropy(actions),
        }

    def _calculate_vfe(self, observations: np.ndarray, beliefs: np.ndarray) -> float:
        """Calculate Variational Free Energy."""
        # Simplified VFE calculation
        # VFE = -log P(o|s) + KL[Q(s)||P(s)]

        # Observation likelihood term
        obs_likelihood = -np.sum(observations * np.log(beliefs + 1e-10))

        # KL divergence term (assuming uniform prior)
        prior = np.ones_like(beliefs) / beliefs.size
        kl_div = np.sum(beliefs * np.log(beliefs / prior + 1e-10))

        return obs_likelihood + kl_div

    def _calculate_efe(
        self, beliefs: np.ndarray, preferences: np.ndarray, actions: np.ndarray
    ) -> float:
        """Calculate Expected Free Energy."""
        # Simplified EFE calculation
        # EFE = -E[log P(o|s)] + E[KL[Q(s|π)||Q(s)]]

        # Expected observation term
        expected_obs = -np.sum(preferences * beliefs)

        # Information gain term
        info_gain = np.sum(actions * np.log(actions + 1e-10))

        return expected_obs + info_gain

    def _estimate_gradients(self, beliefs: np.ndarray) -> np.ndarray:
        """Estimate gradients from belief changes."""
        if len(self.vfe_history) < 2:
            return np.zeros_like(beliefs.flatten())

        # Approximate gradient as change in VFE over change in beliefs
        dvfe = self.vfe_history[-1] - self.vfe_history[-2]
        return np.full_like(beliefs.flatten(), dvfe)

    def _calculate_entropy(self, distribution: np.ndarray) -> float:
        """Calculate entropy of a probability distribution."""
        # Normalize to ensure valid probability distribution
        p = distribution / (np.sum(distribution) + 1e-10)
        return -np.sum(p * np.log(p + 1e-10))

    def check_active_inference_convergence(self) -> Dict[str, Any]:
        """
        Check convergence specific to Active Inference.

        Returns:
            Dictionary with Active Inference convergence metrics
        """
        base_report = self.validator.check_convergence()

        # Additional Active Inference checks
        vfe_stable = self._check_vfe_stability()
        efe_minimized = self._check_efe_minimization()

        return {
            "base_convergence": base_report,
            "vfe_stable": vfe_stable,
            "efe_minimized": efe_minimized,
            "ai_converged": base_report.is_converged and vfe_stable and efe_minimized,
        }

    def _check_vfe_stability(self) -> bool:
        """Check if VFE has stabilized."""
        if len(self.vfe_history) < 50:
            return False

        recent_vfe = list(self.vfe_history)[-50:]
        vfe_std = np.std(recent_vfe)
        return vfe_std < 0.01

    def _check_efe_minimization(self) -> bool:
        """Check if EFE is being minimized."""
        if len(self.efe_history) < 50:
            return False

        recent_efe = list(self.efe_history)[-50:]
        efe_trend = np.polyfit(range(len(recent_efe)), recent_efe, 1)[0]
        return efe_trend <= 0
