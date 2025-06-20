"""
Pattern Extraction System
Identify recurring patterns in agent experiences for learning.
"""

import numpy as np
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict
import logging
import json
from sklearn.cluster import DBSCAN

from ..knowledge.knowledge_graph import AgentKnowledgeGraph, ExperienceNode, BeliefNode

logger = logging.getLogger(__name__)


@dataclass
class ActionSequence:
    """Represents a sequence of actions and their outcomes."""

    actions: List[Dict[str, Any]]
    initial_state: Dict[str, Any]
    final_outcome: Dict[str, Any]
    experiences: List[str]  # Experience IDs
    total_free_energy_change: float
    success: bool

    def to_tuple(self) -> tuple:
        """Convert to hashable tuple for comparison."""
        # Serialize actions for hashing
        action_str = json.dumps(self.actions, sort_keys=True)
        return (action_str, self.success)


@dataclass
class ExtractedPattern:
    """A pattern extracted from experiences."""

    pattern_id: str
    action_sequence: List[Dict[str, Any]]
    trigger_conditions: Dict[str, Any]
    expected_outcomes: List[Dict[str, Any]]
    confidence: float
    occurrence_count: int
    success_rate: float
    variance: float
    source_experiences: List[str]

    def meets_criteria(
        self, min_confidence: float = 0.8, min_occurrences: int = 3
    ) -> bool:
        """Check if pattern meets extraction criteria."""
        return (
            self.confidence >= min_confidence
            and self.occurrence_count >= min_occurrences
        )


class PatternExtractor:
    """
    Extracts behavioral patterns from agent experiences.

    Identifies successful action sequences and reliable patterns
    that can be encoded into agent's cognitive model.
    """

    MIN_CONFIDENCE = 0.8
    MIN_OCCURRENCES = 3
    SEQUENCE_WINDOW = 5  # Max actions in a sequence

    def __init__(self, knowledge_graph: AgentKnowledgeGraph):
        """
        Initialize pattern extractor.

        Args:
            knowledge_graph: Agent's knowledge graph
        """
        self.knowledge_graph = knowledge_graph
        self.extracted_patterns: List[ExtractedPattern] = []

    def extract_patterns(
        self,
        recent_limit: Optional[int] = None,
        min_confidence: float = MIN_CONFIDENCE,
        min_occurrences: int = MIN_OCCURRENCES,
    ) -> List[ExtractedPattern]:
        """
        Extract patterns from experiences in knowledge graph.

        Args:
            recent_limit: Only consider this many recent experiences
            min_confidence: Minimum confidence threshold
            min_occurrences: Minimum occurrence count

        Returns:
            List of extracted patterns meeting criteria
        """
        # Get experiences from knowledge graph
        experiences = self._get_experiences(recent_limit)

        if len(experiences) < self.MIN_OCCURRENCES:
            logger.info(
                f"Not enough experiences for pattern extraction: {len(experiences)}"
            )
            return []

        # Find action sequences
        sequences = self._find_action_sequences(experiences)

        # Group similar sequences
        grouped_sequences = self._group_similar_sequences(sequences)

        # Extract patterns from groups
        patterns = []
        for group in grouped_sequences:
            pattern = self._create_pattern_from_group(group)
            if pattern and pattern.meets_criteria(min_confidence, min_occurrences):
                patterns.append(pattern)

        # Rank patterns by quality
        patterns.sort(key=lambda p: p.confidence * p.success_rate, reverse=True)

        self.extracted_patterns = patterns
        logger.info(
            f"Extracted {len(patterns)} patterns from {len(experiences)} experiences"
        )

        return patterns

    def _get_experiences(
        self, recent_limit: Optional[int] = None
    ) -> List[ExperienceNode]:
        """Get experiences from knowledge graph."""
        experiences = []

        for node_id, node_data in self.knowledge_graph.graph.nodes(data=True):
            if node_data["type"].value == "experience":
                experiences.append(node_data["data"])

        # Sort by timestamp
        experiences.sort(key=lambda e: e.timestamp, reverse=True)

        if recent_limit:
            experiences = experiences[:recent_limit]

        return experiences

    def _find_action_sequences(
        self, experiences: List[ExperienceNode], window_size: int = SEQUENCE_WINDOW
    ) -> List[ActionSequence]:
        """Find sequences of actions from consecutive experiences."""
        sequences = []

        # Sort experiences by timestamp
        sorted_exps = sorted(experiences, key=lambda e: e.timestamp)

        # Sliding window through experiences
        for i in range(len(sorted_exps) - 1):
            # Start a sequence
            for length in range(2, min(window_size + 1, len(sorted_exps) - i + 1)):
                seq_experiences = sorted_exps[i : i + length]

                # Extract action sequence
                actions = [exp.action for exp in seq_experiences[:-1]]
                initial_state = seq_experiences[0].observation
                final_outcome = seq_experiences[-1].outcome

                # Calculate total free energy change
                fe_change = (
                    seq_experiences[-1].free_energy - seq_experiences[0].free_energy
                )

                # Determine success (free energy reduction is good)
                success = fe_change < 0 or self._is_positive_outcome(final_outcome)

                sequence = ActionSequence(
                    actions=actions,
                    initial_state=initial_state,
                    final_outcome=final_outcome,
                    experiences=[exp.id for exp in seq_experiences],
                    total_free_energy_change=fe_change,
                    success=success,
                )

                sequences.append(sequence)

        return sequences

    def _is_positive_outcome(self, outcome: Dict[str, Any]) -> bool:
        """Determine if an outcome is positive."""
        # Check for explicit success indicators
        if outcome.get("success", False):
            return True

        # Check for resource gains
        resource_gained = sum(outcome.get("resources_gained", {}).values())
        if resource_gained > 0:
            return True

        # Check for goal achievement
        if outcome.get("goal_achieved", False):
            return True

        # Check for discovery
        if outcome.get("discovery_made", False):
            return True

        return False

    def _group_similar_sequences(
        self, sequences: List[ActionSequence]
    ) -> List[List[ActionSequence]]:
        """Group similar action sequences together."""
        if not sequences:
            return []

        # Create feature vectors for sequences
        feature_vectors = []
        for seq in sequences:
            # Features: action types, success, free energy change
            features = []

            # Action type histogram
            action_types = defaultdict(int)
            for action in seq.actions:
                action_types[action.get("type", "unknown")] += 1

            # Add action counts as features
            for action_type in ["move", "gather", "communicate", "explore", "trade"]:
                features.append(action_types.get(action_type, 0))

            # Add success and normalized FE change
            features.append(1.0 if seq.success else 0.0)
            features.append(np.tanh(seq.total_free_energy_change / 100))  # Normalize

            feature_vectors.append(features)

        # Use DBSCAN clustering
        feature_matrix = np.array(feature_vectors)

        # Adjust eps based on data
        if len(sequences) < 10:
            eps = 1.5
        else:
            eps = 0.5

        clustering = DBSCAN(eps=eps, min_samples=2).fit(feature_matrix)

        # Group by cluster
        groups = defaultdict(list)
        for i, label in enumerate(clustering.labels_):
            if label >= 0:  # Not noise
                groups[label].append(sequences[i])
            else:
                # Singleton group for noise points
                groups[f"singleton_{i}"] = [sequences[i]]

        return list(groups.values())

    def _create_pattern_from_group(
        self, sequence_group: List[ActionSequence]
    ) -> Optional[ExtractedPattern]:
        """Create a pattern from a group of similar sequences."""
        if not sequence_group:
            return None

        # Find common actions
        action_sequences = [seq.actions for seq in sequence_group]
        common_actions = self._find_common_subsequence(action_sequences)

        if not common_actions:
            return None

        # Aggregate trigger conditions
        trigger_conditions = self._aggregate_conditions(
            [seq.initial_state for seq in sequence_group]
        )

        # Aggregate outcomes
        outcomes = [seq.final_outcome for seq in sequence_group]
        expected_outcomes = outcomes  # Keep all for variance calculation

        # Calculate statistics
        success_count = sum(1 for seq in sequence_group if seq.success)
        success_rate = success_count / len(sequence_group)

        # Calculate outcome variance
        variance = self._calculate_outcome_variance(outcomes)

        # Calculate confidence
        confidence = self._calculate_confidence(
            occurrence_count=len(sequence_group),
            success_rate=success_rate,
            variance=variance,
        )

        # Collect source experiences
        source_experiences = []
        for seq in sequence_group:
            source_experiences.extend(seq.experiences)
        source_experiences = list(set(source_experiences))  # Unique

        pattern = ExtractedPattern(
            pattern_id=f"pattern_{len(self.extracted_patterns)}",
            action_sequence=common_actions,
            trigger_conditions=trigger_conditions,
            expected_outcomes=expected_outcomes,
            confidence=confidence,
            occurrence_count=len(sequence_group),
            success_rate=success_rate,
            variance=variance,
            source_experiences=source_experiences,
        )

        return pattern

    def _find_common_subsequence(
        self, action_sequences: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Find common subsequence in action sequences."""
        if not action_sequences:
            return []

        # Simple approach: find the most common action pattern
        # In production, use more sophisticated sequence alignment

        # Start with the shortest sequence
        shortest = min(action_sequences, key=len)

        # Try to find this pattern in others
        common = []
        for i, action in enumerate(shortest):
            # Check if this action appears at similar position in others
            appears_in_most = True
            for other_seq in action_sequences:
                if i >= len(other_seq):
                    appears_in_most = False
                    break

                # Check if actions are similar
                if not self._actions_similar(action, other_seq[i]):
                    appears_in_most = False
                    break

            if appears_in_most:
                common.append(action)
            else:
                break  # Stop at first mismatch

        return common

    def _actions_similar(
        self, action1: Dict[str, Any], action2: Dict[str, Any]
    ) -> bool:
        """Check if two actions are similar."""
        # Same type is required
        if action1.get("type") != action2.get("type"):
            return False

        # For movement, direction can vary
        if action1.get("type") == "move":
            return True

        # For other actions, check key parameters
        key_params = ["target", "resource", "intent"]
        for param in key_params:
            if param in action1 and param in action2:
                if action1[param] != action2[param]:
                    return False

        return True

    def _aggregate_conditions(self, states: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate multiple states into common conditions."""
        if not states:
            return {}

        aggregated = {}

        # Find common keys
        all_keys = set()
        for state in states:
            all_keys.update(state.keys())

        for key in all_keys:
            values = [state.get(key) for state in states if key in state]

            if not values:
                continue

            # Aggregate based on type
            if all(isinstance(v, (int, float)) for v in values):
                # Numeric: use mean and range
                aggregated[key] = {
                    "mean": np.mean(values),
                    "min": min(values),
                    "max": max(values),
                }
            elif all(isinstance(v, str) for v in values):
                # String: most common value
                from collections import Counter

                counter = Counter(values)
                aggregated[key] = counter.most_common(1)[0][0]
            elif all(isinstance(v, dict) for v in values):
                # Recursive aggregation for dicts
                aggregated[key] = self._aggregate_conditions(values)
            else:
                # Mixed types: just take first
                aggregated[key] = values[0]

        return aggregated

    def _calculate_outcome_variance(self, outcomes: List[Dict[str, Any]]) -> float:
        """Calculate variance in outcomes."""
        if len(outcomes) <= 1:
            return 0.0

        # Extract numeric features from outcomes
        feature_lists = defaultdict(list)

        for outcome in outcomes:
            for key, value in outcome.items():
                if isinstance(value, (int, float)):
                    feature_lists[key].append(value)
                elif isinstance(value, dict):
                    # Handle nested values like resources
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            feature_lists[f"{key}.{sub_key}"].append(sub_value)

        # Calculate variance for each feature
        variances = []
        for feature_values in feature_lists.values():
            if len(feature_values) > 1:
                variances.append(np.var(feature_values))

        # Return mean variance
        return np.mean(variances) if variances else 0.0

    def _calculate_confidence(
        self, occurrence_count: int, success_rate: float, variance: float
    ) -> float:
        """
        Calculate pattern confidence based on multiple factors.

        Args:
            occurrence_count: How many times pattern occurred
            success_rate: Fraction of successful outcomes
            variance: Variance in outcomes

        Returns:
            Confidence score between 0 and 1
        """
        # Occurrence factor (sigmoid)
        occurrence_factor = 1 - np.exp(-occurrence_count / 5)

        # Success factor
        success_factor = success_rate

        # Consistency factor (inverse of normalized variance)
        consistency_factor = 1 / (1 + variance / 100)

        # Weighted combination
        confidence = (
            0.3 * occurrence_factor + 0.5 * success_factor + 0.2 * consistency_factor
        )

        return min(1.0, confidence)

    def encode_patterns_to_gnn(
        self, patterns: List[ExtractedPattern], gnn_model_path: str
    ) -> bool:
        """
        Encode high-confidence patterns into agent's GNN model.

        Args:
            patterns: Patterns to encode
            gnn_model_path: Path to agent's GNN model file

        Returns:
            Success status
        """
        try:
            # Read existing GNN model
            with open(gnn_model_path, "r") as f:
                gnn_content = f.read()

            # Find the behavioral rules section
            lines = gnn_content.split("\n")
            rules_start = -1
            rules_end = -1

            for i, line in enumerate(lines):
                if "## Behavioral Rules" in line:
                    rules_start = i
                elif rules_start > -1 and line.startswith("##"):
                    rules_end = i
                    break

            if rules_start == -1:
                # Add new section
                lines.append("\n## Behavioral Rules\n")
                rules_start = len(lines) - 1
                rules_end = len(lines)

            # Generate rules from patterns
            new_rules = []
            for pattern in patterns:
                rule = self._pattern_to_gnn_rule(pattern)
                new_rules.append(rule)

            # Insert new rules
            lines[rules_start + 1 : rules_end] = new_rules

            # Write back
            with open(gnn_model_path, "w") as f:
                f.write("\n".join(lines))

            logger.info(f"Encoded {len(patterns)} patterns to GNN model")
            return True

        except Exception as e:
            logger.error(f"Failed to encode patterns to GNN: {e}")
            return False

    def _pattern_to_gnn_rule(self, pattern: ExtractedPattern) -> str:
        """Convert pattern to GNN rule format."""
        # Create condition string
        conditions = []
        for key, value in pattern.trigger_conditions.items():
            if isinstance(value, dict) and "mean" in value:
                conditions.append(f"{key} ∈ [{value['min']:.1f}, {value['max']:.1f}]")
            else:
                conditions.append(f"{key} = {value}")

        condition_str = " ∧ ".join(conditions) if conditions else "true"

        # Create action string
        action_strs = []
        for action in pattern.action_sequence:
            action_type = action.get("type", "unknown")
            params = [f"{k}={v}" for k, v in action.items() if k != "type"]
            action_str = (
                f"{action_type}({', '.join(params)})" if params else action_type
            )
            action_strs.append(action_str)

        action_sequence = " → ".join(action_strs)

        # Create rule
        rule = f"""
### Pattern: {pattern.pattern_id}
- **Confidence**: {pattern.confidence:.2f}
- **Success Rate**: {pattern.success_rate:.2f}
- **Occurrences**: {pattern.occurrence_count}

**Rule**: IF {condition_str} THEN {action_sequence}

**Expected Outcome**: Free energy reduction with {pattern.success_rate*100:.0f}% success rate
"""

        return rule

    def update_beliefs_from_patterns(self, patterns: List[ExtractedPattern]):
        """Update agent's beliefs based on extracted patterns."""
        for pattern in patterns:
            # Create belief about the pattern
            belief_statement = (
                f"Action sequence {' then '.join([a.get('type', 'unknown') for a in pattern.action_sequence])} "
                f"leads to success with {pattern.success_rate*100:.0f}% probability"
            )

            belief = BeliefNode(
                id="",
                statement=belief_statement,
                confidence=pattern.confidence,
                supporting_patterns=[pattern.pattern_id],
            )

            self.knowledge_graph.add_belief(belief)

        logger.info(f"Updated {len(patterns)} beliefs from patterns")


# Standalone pattern analysis functions
def analyze_behavioral_patterns(experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze behavioral patterns from a list of experiences.

    Args:
        experiences: List of experience dictionaries

    Returns:
        Analysis results including common patterns and statistics
    """
    analysis = {
        "total_experiences": len(experiences),
        "action_distribution": defaultdict(int),
        "success_rate_by_action": defaultdict(lambda: {"success": 0, "total": 0}),
        "common_sequences": [],
        "resource_efficiency": {},
    }

    # Analyze action distribution
    for exp in experiences:
        action_type = exp.get("action", {}).get("type", "unknown")
        analysis["action_distribution"][action_type] += 1

        # Track success rates
        success = exp.get("outcome", {}).get("success", False)
        analysis["success_rate_by_action"][action_type]["total"] += 1
        if success:
            analysis["success_rate_by_action"][action_type]["success"] += 1

    # Calculate success rates
    for action_type, stats in analysis["success_rate_by_action"].items():
        if stats["total"] > 0:
            stats["rate"] = stats["success"] / stats["total"]

    # Find common action sequences (bigrams)
    action_bigrams = defaultdict(int)
    for i in range(len(experiences) - 1):
        action1 = experiences[i].get("action", {}).get("type", "unknown")
        action2 = experiences[i + 1].get("action", {}).get("type", "unknown")
        action_bigrams[(action1, action2)] += 1

    # Top sequences
    analysis["common_sequences"] = [
        {"sequence": list(seq), "count": count}
        for seq, count in sorted(
            action_bigrams.items(), key=lambda x: x[1], reverse=True
        )[:5]
    ]

    return dict(analysis)


# Example usage
if __name__ == "__main__":
    # Create mock knowledge graph and experiences
    from ..knowledge.knowledge_graph import AgentKnowledgeGraph

    kg = AgentKnowledgeGraph("test_agent")

    # Add mock experiences
    for i in range(20):
        exp = ExperienceNode(
            id=f"exp_{i}",
            timestamp=datetime.utcnow(),
            location=f"hex_{i % 3}",
            observation={
                "resources": {"food": 50 - i, "water": 30 + i},
                "nearby_agents": 1 if i % 4 == 0 else 0,
            },
            action={
                "type": "gather" if i % 3 == 0 else "move",
                "target": "food" if i % 3 == 0 else f"hex_{(i+1) % 3}",
            },
            outcome={
                "success": i % 2 == 0,
                "resources_gained": {"food": 10} if i % 3 == 0 and i % 2 == 0 else {},
            },
            free_energy=100 - i * 3,
            confidence=0.7,
        )
        kg.add_experience(exp)

    # Extract patterns
    extractor = PatternExtractor(kg)
    patterns = extractor.extract_patterns(recent_limit=20)

    print(f"Extracted {len(patterns)} patterns:")
    for pattern in patterns:
        print(f"\nPattern {pattern.pattern_id}:")
        print(f"  Actions: {[a.get('type') for a in pattern.action_sequence]}")
        print(f"  Confidence: {pattern.confidence:.2f}")
        print(f"  Success rate: {pattern.success_rate:.2f}")
        print(f"  Occurrences: {pattern.occurrence_count}")
