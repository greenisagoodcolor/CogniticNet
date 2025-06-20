"""
Agent Readiness Evaluator

Determines when agents are ready for autonomous hardware deployment by evaluating
across 5 key dimensions: knowledge maturity, goal achievement, model stability,
collaboration, and resource management.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path
import json

logger = logging.getLogger(__name__)


@dataclass
class ReadinessThresholds:
    """Configurable thresholds for readiness evaluation."""

    # Knowledge maturity
    min_experiences: int = 1000
    min_patterns: int = 50
    pattern_confidence: float = 0.85

    # Goal achievement
    success_rate: float = 0.9
    complex_goals_completed: int = 5

    # Model stability
    convergence_threshold: float = 0.01
    min_stable_iterations: int = 100

    # Collaboration
    successful_interactions: int = 20
    knowledge_shared: int = 10

    # Resource management
    efficiency: float = 0.8
    sustainability: float = 0.9

    # Overall readiness
    overall_threshold: float = 0.85


@dataclass
class ReadinessScore:
    """Detailed readiness evaluation results."""

    agent_id: str
    timestamp: datetime

    # Dimension scores (0-1)
    knowledge_maturity: float = 0.0
    goal_achievement: float = 0.0
    model_stability: float = 0.0
    collaboration: float = 0.0
    resource_management: float = 0.0

    # Overall readiness
    overall_score: float = 0.0
    is_ready: bool = False

    # Detailed metrics
    metrics: Dict[str, Any] = field(default_factory=dict)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "agent_id": self.agent_id,
            "timestamp": self.timestamp.isoformat(),
            "scores": {
                "knowledge_maturity": self.knowledge_maturity,
                "goal_achievement": self.goal_achievement,
                "model_stability": self.model_stability,
                "collaboration": self.collaboration,
                "resource_management": self.resource_management,
                "overall": self.overall_score,
            },
            "is_ready": self.is_ready,
            "metrics": self.metrics,
            "recommendations": self.recommendations,
        }


class AgentReadinessEvaluator:
    """
    Evaluates agent readiness for autonomous hardware deployment.

    Uses embedded analytics for agent introspection and learning metrics
    as suggested by Hannes Mühleisen.
    """

    def __init__(self, thresholds: Optional[ReadinessThresholds] = None):
        """Initialize evaluator with configurable thresholds."""
        self.thresholds = thresholds or ReadinessThresholds()
        self._evaluation_history: Dict[str, List[ReadinessScore]] = {}

    def evaluate_agent(self, agent) -> ReadinessScore:
        """
        Comprehensive evaluation across all 5 dimensions.

        Args:
            agent: Agent instance to evaluate

        Returns:
            ReadinessScore with detailed evaluation results
        """
        logger.info(f"Evaluating readiness for agent {agent.id}")

        score = ReadinessScore(agent_id=agent.id, timestamp=datetime.now())

        # Evaluate each dimension
        score.knowledge_maturity = self._evaluate_knowledge(agent, score)
        score.goal_achievement = self._evaluate_goals(agent, score)
        score.model_stability = self._evaluate_model_stability(agent, score)
        score.collaboration = self._evaluate_collaboration(agent, score)
        score.resource_management = self._evaluate_resources(agent, score)

        # Calculate overall readiness
        dimension_scores = [
            score.knowledge_maturity,
            score.goal_achievement,
            score.model_stability,
            score.collaboration,
            score.resource_management,
        ]

        # Weighted average (can be customized)
        weights = [0.25, 0.20, 0.20, 0.20, 0.15]
        score.overall_score = sum(s * w for s, w in zip(dimension_scores, weights))

        # Determine if ready
        score.is_ready = (
            score.overall_score >= self.thresholds.overall_threshold
            and all(s >= 0.7 for s in dimension_scores)  # No dimension below 0.7
        )

        # Generate recommendations
        self._generate_recommendations(score)

        # Store in history
        if agent.id not in self._evaluation_history:
            self._evaluation_history[agent.id] = []
        self._evaluation_history[agent.id].append(score)

        logger.info(
            f"Agent {agent.id} readiness: {score.overall_score:.2f} "
            f"({'READY' if score.is_ready else 'NOT READY'})"
        )

        return score

    def _evaluate_knowledge(self, agent, score: ReadinessScore) -> float:
        """Evaluate knowledge maturity dimension."""
        try:
            # Get knowledge metrics
            experience_count = len(agent.knowledge_graph.experiences)
            pattern_count = len(agent.knowledge_graph.patterns)

            # Calculate average pattern confidence
            if pattern_count > 0:
                avg_confidence = np.mean(
                    [p.confidence for p in agent.knowledge_graph.patterns.values()]
                )
            else:
                avg_confidence = 0.0

            # Store metrics
            score.metrics["knowledge"] = {
                "experience_count": experience_count,
                "pattern_count": pattern_count,
                "avg_pattern_confidence": avg_confidence,
            }

            # Calculate sub-scores
            exp_score = min(1.0, experience_count / self.thresholds.min_experiences)
            pattern_score = min(1.0, pattern_count / self.thresholds.min_patterns)
            confidence_score = avg_confidence / self.thresholds.pattern_confidence

            # Weighted combination
            knowledge_score = (
                exp_score * 0.3 + pattern_score * 0.4 + confidence_score * 0.3
            )

            return min(1.0, knowledge_score)

        except Exception as e:
            logger.error(f"Error evaluating knowledge: {e}")
            return 0.0

    def _evaluate_goals(self, agent, score: ReadinessScore) -> float:
        """Evaluate goal achievement dimension."""
        try:
            # Get goal metrics from agent history
            total_goals = agent.stats.get("total_goals_attempted", 0)
            successful_goals = agent.stats.get("successful_goals", 0)
            complex_goals = agent.stats.get("complex_goals_completed", 0)

            # Calculate success rate
            if total_goals > 0:
                success_rate = successful_goals / total_goals
            else:
                success_rate = 0.0

            # Store metrics
            score.metrics["goals"] = {
                "total_attempted": total_goals,
                "successful": successful_goals,
                "success_rate": success_rate,
                "complex_completed": complex_goals,
            }

            # Calculate sub-scores
            rate_score = success_rate / self.thresholds.success_rate
            complex_score = min(
                1.0, complex_goals / self.thresholds.complex_goals_completed
            )

            # Need minimum attempts for valid score
            if total_goals < 10:
                return 0.0

            # Weighted combination
            goal_score = rate_score * 0.6 + complex_score * 0.4

            return min(1.0, goal_score)

        except Exception as e:
            logger.error(f"Error evaluating goals: {e}")
            return 0.0

    def _evaluate_model_stability(self, agent, score: ReadinessScore) -> float:
        """Evaluate GNN model stability dimension."""
        try:
            # Get model update history
            model_updates = agent.model_update_history

            if len(model_updates) < 10:
                # Not enough history
                score.metrics["model_stability"] = {
                    "update_count": len(model_updates),
                    "is_converged": False,
                    "stable_iterations": 0,
                }
                return 0.0

            # Calculate convergence metrics
            recent_updates = model_updates[-20:]
            update_magnitudes = [u.get("magnitude", 0) for u in recent_updates]

            # Check if converged (low update magnitudes)
            avg_magnitude = np.mean(update_magnitudes[-10:])
            is_converged = avg_magnitude < self.thresholds.convergence_threshold

            # Count stable iterations
            stable_iterations = 0
            for mag in reversed(update_magnitudes):
                if mag < self.thresholds.convergence_threshold:
                    stable_iterations += 1
                else:
                    break

            # Store metrics
            score.metrics["model_stability"] = {
                "update_count": len(model_updates),
                "avg_recent_magnitude": avg_magnitude,
                "is_converged": is_converged,
                "stable_iterations": stable_iterations,
            }

            # Calculate score
            convergence_score = 1.0 if is_converged else 0.5
            stability_score = min(
                1.0, stable_iterations / self.thresholds.min_stable_iterations
            )

            return convergence_score * 0.5 + stability_score * 0.5

        except Exception as e:
            logger.error(f"Error evaluating model stability: {e}")
            return 0.0

    def _evaluate_collaboration(self, agent, score: ReadinessScore) -> float:
        """Evaluate collaboration dimension."""
        try:
            # Get collaboration metrics
            total_interactions = agent.stats.get("total_interactions", 0)
            successful_interactions = agent.stats.get("successful_interactions", 0)
            knowledge_shared = agent.stats.get("knowledge_items_shared", 0)
            unique_collaborators = len(agent.stats.get("collaborators", set()))

            # Store metrics
            score.metrics["collaboration"] = {
                "total_interactions": total_interactions,
                "successful_interactions": successful_interactions,
                "knowledge_shared": knowledge_shared,
                "unique_collaborators": unique_collaborators,
            }

            # Calculate sub-scores
            interaction_score = min(
                1.0, successful_interactions / self.thresholds.successful_interactions
            )
            sharing_score = min(
                1.0, knowledge_shared / self.thresholds.knowledge_shared
            )
            diversity_score = min(1.0, unique_collaborators / 5)  # 5+ is good

            # Weighted combination
            collab_score = (
                interaction_score * 0.4 + sharing_score * 0.4 + diversity_score * 0.2
            )

            return collab_score

        except Exception as e:
            logger.error(f"Error evaluating collaboration: {e}")
            return 0.0

    def _evaluate_resources(self, agent, score: ReadinessScore) -> float:
        """Evaluate resource management dimension."""
        try:
            # Get resource metrics
            energy_efficiency = agent.stats.get("energy_efficiency", 0.0)
            resource_waste = agent.stats.get("resource_waste_ratio", 1.0)
            sustainability_score = agent.stats.get("sustainability_score", 0.0)

            # Calculate efficiency (inverse of waste)
            actual_efficiency = 1.0 - resource_waste

            # Store metrics
            score.metrics["resources"] = {
                "energy_efficiency": energy_efficiency,
                "resource_efficiency": actual_efficiency,
                "sustainability_score": sustainability_score,
                "avg_energy_level": agent.stats.get("avg_energy_level", 0.0),
            }

            # Calculate sub-scores
            efficiency_score = actual_efficiency / self.thresholds.efficiency
            sustainability_score_norm = (
                sustainability_score / self.thresholds.sustainability
            )

            # Weighted combination
            resource_score = efficiency_score * 0.6 + sustainability_score_norm * 0.4

            return min(1.0, resource_score)

        except Exception as e:
            logger.error(f"Error evaluating resources: {e}")
            return 0.0

    def _generate_recommendations(self, score: ReadinessScore):
        """Generate specific recommendations for improvement."""
        recommendations = []

        # Knowledge recommendations
        if score.knowledge_maturity < 0.8:
            if (
                score.metrics["knowledge"]["experience_count"]
                < self.thresholds.min_experiences
            ):
                recommendations.append(
                    f"Gain more experience: {score.metrics['knowledge']['experience_count']}"
                    f"/{self.thresholds.min_experiences} experiences"
                )
            if (
                score.metrics["knowledge"]["pattern_count"]
                < self.thresholds.min_patterns
            ):
                recommendations.append(
                    f"Extract more patterns: {score.metrics['knowledge']['pattern_count']}"
                    f"/{self.thresholds.min_patterns} patterns"
                )

        # Goal recommendations
        if score.goal_achievement < 0.8:
            if score.metrics["goals"]["success_rate"] < self.thresholds.success_rate:
                recommendations.append(
                    f"Improve goal success rate: {score.metrics['goals']['success_rate']:.1%}"
                    f" (target: {self.thresholds.success_rate:.1%})"
                )
            if (
                score.metrics["goals"]["complex_completed"]
                < self.thresholds.complex_goals_completed
            ):
                recommendations.append(
                    "Complete more complex goals for deployment readiness"
                )

        # Model stability recommendations
        if score.model_stability < 0.8:
            if not score.metrics["model_stability"]["is_converged"]:
                recommendations.append("Model has not converged - continue training")
            if (
                score.metrics["model_stability"]["stable_iterations"]
                < self.thresholds.min_stable_iterations
            ):
                recommendations.append(
                    f"Need more stable iterations: "
                    f"{score.metrics['model_stability']['stable_iterations']}"
                    f"/{self.thresholds.min_stable_iterations}"
                )

        # Collaboration recommendations
        if score.collaboration < 0.8:
            if (
                score.metrics["collaboration"]["successful_interactions"]
                < self.thresholds.successful_interactions
            ):
                recommendations.append("Engage in more successful collaborations")
            if (
                score.metrics["collaboration"]["knowledge_shared"]
                < self.thresholds.knowledge_shared
            ):
                recommendations.append("Share more knowledge with other agents")

        # Resource recommendations
        if score.resource_management < 0.8:
            if (
                score.metrics["resources"]["resource_efficiency"]
                < self.thresholds.efficiency
            ):
                recommendations.append(
                    f"Improve resource efficiency: "
                    f"{score.metrics['resources']['resource_efficiency']:.1%}"
                )

        score.recommendations = recommendations

    def get_readiness_history(self, agent_id: str) -> List[ReadinessScore]:
        """Get evaluation history for an agent."""
        return self._evaluation_history.get(agent_id, [])

    def get_readiness_trend(
        self, agent_id: str, window: timedelta = timedelta(hours=24)
    ) -> Dict[str, List[float]]:
        """Get readiness score trends over time."""
        history = self.get_readiness_history(agent_id)

        if not history:
            return {}

        # Filter by time window
        cutoff = datetime.now() - window
        recent = [h for h in history if h.timestamp >= cutoff]

        if not recent:
            return {}

        # Extract trends
        trends = {
            "timestamps": [h.timestamp.isoformat() for h in recent],
            "overall": [h.overall_score for h in recent],
            "knowledge": [h.knowledge_maturity for h in recent],
            "goals": [h.goal_achievement for h in recent],
            "stability": [h.model_stability for h in recent],
            "collaboration": [h.collaboration for h in recent],
            "resources": [h.resource_management for h in recent],
        }

        return trends

    def export_readiness_report(self, agent_id: str, output_path: Path) -> Path:
        """Export detailed readiness report for an agent."""
        history = self.get_readiness_history(agent_id)

        if not history:
            raise ValueError(f"No evaluation history for agent {agent_id}")

        latest = history[-1]
        trends = self.get_readiness_trend(agent_id)

        report = {
            "agent_id": agent_id,
            "report_timestamp": datetime.now().isoformat(),
            "latest_evaluation": latest.to_dict(),
            "trends": trends,
            "evaluation_count": len(history),
            "first_evaluation": history[0].timestamp.isoformat(),
            "recommendation_summary": latest.recommendations,
        }

        # Save report
        report_file = (
            output_path
            / f"readiness_report_{agent_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Exported readiness report to {report_file}")
        return report_file

    def batch_evaluate(self, agents: List[Any]) -> Dict[str, ReadinessScore]:
        """Evaluate multiple agents and return results."""
        results = {}

        for agent in agents:
            try:
                score = self.evaluate_agent(agent)
                results[agent.id] = score
            except Exception as e:
                logger.error(f"Failed to evaluate agent {agent.id}: {e}")

        return results
