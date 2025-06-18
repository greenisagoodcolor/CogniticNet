"""
GNN Model Refinement System
Agents refine their cognitive models based on learned patterns.
Implements Daniel Friedman's vision: 'Agents should write their own GNN models.'
"""

import os
import shutil
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging
import json

from ..gnn.parser import GNNParser
from ..gnn.validator import GNNValidator
from ..gnn.generator import GNNGenerator
from ..learning.pattern_extraction import ExtractedPattern, PatternExtractor
from ..knowledge.knowledge_graph import AgentKnowledgeGraph, BeliefNode

logger = logging.getLogger(__name__)


@dataclass
class ModelVersion:
    """Represents a version of the GNN model."""
    version_id: str
    timestamp: datetime
    file_path: str
    patterns_added: List[str]  # Pattern IDs
    performance_metrics: Dict[str, float]
    parent_version: Optional[str] = None
    refinement_reason: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "version_id": self.version_id,
            "timestamp": self.timestamp.isoformat(),
            "file_path": self.file_path,
            "patterns_added": self.patterns_added,
            "performance_metrics": self.performance_metrics,
            "parent_version": self.parent_version,
            "refinement_reason": self.refinement_reason
        }


class GNNModelRefinement:
    """
    System for agents to refine their own GNN models based on experience.
    
    Critical innovation: agents modify their cognitive models autonomously,
    encoding learned patterns as new behavioral rules.
    """
    
    REFINEMENT_INTERVAL = 10  # Refine every N experiences
    MIN_PATTERN_CONFIDENCE = 0.8
    MODEL_HISTORY_DIR = ".gnn_history"
    
    def __init__(self, 
                 agent_id: str,
                 model_path: str,
                 knowledge_graph: AgentKnowledgeGraph):
        """
        Initialize model refinement system.
        
        Args:
            agent_id: Unique agent identifier
            model_path: Path to current GNN model file
            knowledge_graph: Agent's knowledge graph
        """
        self.agent_id = agent_id
        self.model_path = model_path
        self.knowledge_graph = knowledge_graph
        
        # Components
        self.parser = GNNParser()
        self.validator = GNNValidator()
        self.generator = GNNGenerator()
        self.pattern_extractor = PatternExtractor(knowledge_graph)
        
        # Model versioning
        self.model_versions: List[ModelVersion] = []
        self.current_version: Optional[ModelVersion] = None
        
        # Performance tracking
        self.experience_count_since_refinement = 0
        self.performance_baseline: Dict[str, float] = {}
        
        # Initialize history directory
        self._init_history_dir()
        
        logger.info(f"Initialized GNN refinement for agent {agent_id}")
        
    def _init_history_dir(self):
        """Initialize model history directory."""
        history_dir = os.path.join(
            os.path.dirname(self.model_path),
            self.MODEL_HISTORY_DIR,
            self.agent_id
        )
        os.makedirs(history_dir, exist_ok=True)
        self.history_dir = history_dir
        
    def check_refinement_needed(self) -> bool:
        """
        Check if model refinement should be triggered.
        
        Returns:
            True if refinement should occur
        """
        # Check experience count
        experience_count = len([
            n for n, d in self.knowledge_graph.graph.nodes(data=True)
            if d["type"].value == "experience"
        ])
        
        experiences_since_last = (
            experience_count - self.experience_count_since_refinement
        )
        
        if experiences_since_last >= self.REFINEMENT_INTERVAL:
            logger.info(f"Refinement triggered: {experiences_since_last} new experiences")
            return True
            
        # Could add other triggers:
        # - Performance degradation
        # - High uncertainty
        # - External request
        
        return False
        
    def refine_model(self, 
                    force: bool = False,
                    reason: str = "Periodic refinement") -> Optional[ModelVersion]:
        """
        Refine the agent's GNN model based on learned patterns.
        
        Args:
            force: Force refinement even if not triggered
            reason: Reason for refinement
            
        Returns:
            New model version if refinement occurred
        """
        if not force and not self.check_refinement_needed():
            return None
            
        logger.info(f"Starting model refinement for agent {self.agent_id}")
        
        try:
            # Extract patterns from recent experiences
            patterns = self.pattern_extractor.extract_patterns(
                min_confidence=self.MIN_PATTERN_CONFIDENCE
            )
            
            if not patterns:
                logger.info("No high-confidence patterns found for refinement")
                return None
                
            # Read current model
            current_model = self._read_current_model()
            if not current_model:
                logger.error("Failed to read current model")
                return None
                
            # Apply refinements
            refined_model = self._apply_refinements(current_model, patterns)
            
            # Validate refined model
            if not self._validate_refined_model(refined_model):
                logger.error("Refined model failed validation")
                return None
                
            # Create new version
            new_version = self._create_model_version(
                refined_model,
                patterns,
                reason
            )
            
            # Update beliefs about self
            self._update_self_beliefs(patterns, new_version)
            
            # Reset experience counter
            self.experience_count_since_refinement = len([
                n for n, d in self.knowledge_graph.graph.nodes(data=True)
                if d["type"].value == "experience"
            ])
            
            logger.info(f"Model refinement complete: version {new_version.version_id}")
            return new_version
            
        except Exception as e:
            logger.error(f"Error during model refinement: {e}")
            return None
            
    def _read_current_model(self) -> Optional[str]:
        """Read current GNN model content."""
        try:
            with open(self.model_path, 'r') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read model: {e}")
            return None
            
    def _apply_refinements(self, 
                          model_content: str,
                          patterns: List[ExtractedPattern]) -> str:
        """
        Apply pattern refinements to GNN model.
        
        Args:
            model_content: Current model content
            patterns: Patterns to encode
            
        Returns:
            Refined model content
        """
        lines = model_content.split('\n')
        
        # Find or create sections
        preferences_idx = self._find_section(lines, "## Preferences")
        rules_idx = self._find_section(lines, "## Behavioral Rules")
        
        # Add preferences from patterns
        if preferences_idx >= 0:
            new_preferences = self._generate_preferences_from_patterns(patterns)
            self._insert_content(lines, preferences_idx, new_preferences)
            
        # Add behavioral rules from patterns
        if rules_idx >= 0:
            new_rules = self._generate_rules_from_patterns(patterns)
            self._insert_content(lines, rules_idx, new_rules)
        else:
            # Create new section
            lines.append("\n## Behavioral Rules")
            lines.append("*Learned through experience*\n")
            lines.extend(self._generate_rules_from_patterns(patterns))
            
        # Update metadata
        self._update_model_metadata(lines, patterns)
        
        return '\n'.join(lines)
        
    def _find_section(self, lines: List[str], section_header: str) -> int:
        """Find index of section header in lines."""
        for i, line in enumerate(lines):
            if line.strip() == section_header:
                return i
        return -1
        
    def _insert_content(self, 
                       lines: List[str], 
                       after_index: int,
                       content: List[str]):
        """Insert content after specified index."""
        # Find end of section
        end_idx = after_index + 1
        while end_idx < len(lines) and not lines[end_idx].startswith('##'):
            end_idx += 1
            
        # Insert before end of section
        for i, line in enumerate(content):
            lines.insert(end_idx + i, line)
            
    def _generate_preferences_from_patterns(self, 
                                          patterns: List[ExtractedPattern]) -> List[str]:
        """Generate preference entries from patterns."""
        preferences = []
        
        for pattern in patterns:
            # Extract preference type from pattern
            if any(a.get("type") == "gather" for a in pattern.action_sequence):
                resource_prefs = self._extract_resource_preferences(pattern)
                for pref in resource_prefs:
                    preferences.append(f"- {pref}")
                    
            elif any(a.get("type") == "communicate" for a in pattern.action_sequence):
                social_pref = f"communication_style: {pattern.action_sequence[0].get('intent', 'cooperative')}"
                preferences.append(f"- {social_pref}")
                
        return preferences
        
    def _extract_resource_preferences(self, 
                                    pattern: ExtractedPattern) -> List[str]:
        """Extract resource preferences from pattern."""
        prefs = []
        
        # Analyze expected outcomes for resource preferences
        resource_gains = {}
        for outcome in pattern.expected_outcomes:
            for resource, amount in outcome.get("resources_gained", {}).items():
                if resource not in resource_gains:
                    resource_gains[resource] = []
                resource_gains[resource].append(amount)
                
        # Create preferences based on gains
        for resource, amounts in resource_gains.items():
            avg_gain = sum(amounts) / len(amounts)
            if avg_gain > 10:  # Significant gain
                prefs.append(f"resource_priority: {resource} (learned)")
                
        return prefs
        
    def _generate_rules_from_patterns(self, 
                                    patterns: List[ExtractedPattern]) -> List[str]:
        """Generate behavioral rules from patterns."""
        rules = []
        
        for i, pattern in enumerate(patterns):
            rules.append(f"\n### Learned Pattern {i + 1}")
            rules.append(f"*Confidence: {pattern.confidence:.2f}, Success Rate: {pattern.success_rate:.2f}*")
            
            # Create condition
            conditions = []
            for key, value in pattern.trigger_conditions.items():
                if isinstance(value, dict) and "mean" in value:
                    conditions.append(f"{key} ∈ [{value['min']:.1f}, {value['max']:.1f}]")
                else:
                    conditions.append(f"{key} = {value}")
                    
            condition_str = " ∧ ".join(conditions) if conditions else "always"
            
            # Create action sequence
            actions = []
            for action in pattern.action_sequence:
                action_type = action.get("type", "act")
                params = [f"{k}={v}" for k, v in action.items() if k != "type"]
                action_str = f"{action_type}({', '.join(params)})" if params else action_type
                actions.append(action_str)
                
            action_str = " → ".join(actions)
            
            # Create rule
            rules.append(f"- **Rule**: IF {condition_str} THEN {action_str}")
            rules.append(f"- **Expected**: Free energy reduction, {pattern.success_rate*100:.0f}% success")
            rules.append(f"- **Learned from**: {pattern.occurrence_count} experiences")
            
        return rules
        
    def _update_model_metadata(self, 
                             lines: List[str],
                             patterns: List[ExtractedPattern]):
        """Update model metadata with refinement info."""
        # Find metadata section
        metadata_idx = self._find_section(lines, "---")
        if metadata_idx < 0:
            return
            
        # Find end of metadata
        end_idx = metadata_idx + 1
        while end_idx < len(lines) and lines[end_idx].strip() != "---":
            end_idx += 1
            
        # Insert refinement info
        timestamp = datetime.utcnow().isoformat()
        refinement_info = [
            f"last_refined: {timestamp}",
            f"patterns_learned: {len(patterns)}",
            f"total_experiences: {self.experience_count_since_refinement}"
        ]
        
        for info in refinement_info:
            lines.insert(end_idx, info)
            
    def _validate_refined_model(self, model_content: str) -> bool:
        """Validate refined model maintains GNN syntax."""
        try:
            # Parse model
            model = self.parser.parse(model_content)
            if not model:
                return False
                
            # Validate syntax
            is_valid, errors = self.validator.validate_syntax(model)
            if not is_valid:
                logger.error(f"Validation errors: {errors}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False
            
    def _create_model_version(self,
                            model_content: str,
                            patterns: List[ExtractedPattern],
                            reason: str) -> ModelVersion:
        """Create and save new model version."""
        # Generate version ID
        timestamp = datetime.utcnow()
        version_id = f"v{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Save model file
        version_path = os.path.join(
            self.history_dir,
            f"{self.agent_id}_{version_id}.gnn.md"
        )
        
        with open(version_path, 'w') as f:
            f.write(model_content)
            
        # Update current model
        shutil.copy(version_path, self.model_path)
        
        # Calculate performance metrics
        metrics = self._calculate_performance_metrics()
        
        # Create version record
        version = ModelVersion(
            version_id=version_id,
            timestamp=timestamp,
            file_path=version_path,
            patterns_added=[p.pattern_id for p in patterns],
            performance_metrics=metrics,
            parent_version=self.current_version.version_id if self.current_version else None,
            refinement_reason=reason
        )
        
        # Update version tracking
        self.model_versions.append(version)
        self.current_version = version
        
        # Save version history
        self._save_version_history()
        
        return version
        
    def _calculate_performance_metrics(self) -> Dict[str, float]:
        """Calculate current performance metrics."""
        metrics = {}
        
        # Free energy statistics
        recent_fe = []
        for node_id, node_data in self.knowledge_graph.graph.nodes(data=True):
            if node_data["type"].value == "experience":
                recent_fe.append(node_data["data"].free_energy)
                
        if recent_fe:
            metrics["avg_free_energy"] = sum(recent_fe) / len(recent_fe)
            metrics["min_free_energy"] = min(recent_fe)
            
        # Success rate
        success_count = sum(
            1 for node_id, node_data in self.knowledge_graph.graph.nodes(data=True)
            if node_data["type"].value == "experience" and 
            node_data["data"].outcome.get("success", False)
        )
        total_exp = len(recent_fe)
        metrics["success_rate"] = success_count / total_exp if total_exp > 0 else 0
        
        # Pattern confidence
        pattern_confidences = [
            node_data["data"].confidence
            for node_id, node_data in self.knowledge_graph.graph.nodes(data=True)
            if node_data["type"].value == "pattern"
        ]
        if pattern_confidences:
            metrics["avg_pattern_confidence"] = sum(pattern_confidences) / len(pattern_confidences)
            
        return metrics
        
    def _update_self_beliefs(self,
                           patterns: List[ExtractedPattern],
                           version: ModelVersion):
        """Update agent's beliefs about its own capabilities."""
        # Belief about learning capability
        learning_belief = BeliefNode(
            id="",
            statement=f"I have learned {len(patterns)} new behavioral patterns",
            confidence=0.9,
            supporting_patterns=[p.pattern_id for p in patterns]
        )
        self.knowledge_graph.add_belief(learning_belief)
        
        # Belief about improvement
        if self.performance_baseline:
            current_metrics = version.performance_metrics
            improvement = (
                current_metrics.get("success_rate", 0) - 
                self.performance_baseline.get("success_rate", 0)
            )
            
            if improvement > 0:
                improvement_belief = BeliefNode(
                    id="",
                    statement=f"My performance has improved by {improvement*100:.1f}%",
                    confidence=0.8
                )
                self.knowledge_graph.add_belief(improvement_belief)
                
        # Update baseline
        self.performance_baseline = version.performance_metrics
        
    def _save_version_history(self):
        """Save version history to file."""
        history_file = os.path.join(self.history_dir, "version_history.json")
        
        history_data = {
            "agent_id": self.agent_id,
            "current_version": self.current_version.version_id if self.current_version else None,
            "versions": [v.to_dict() for v in self.model_versions]
        }
        
        with open(history_file, 'w') as f:
            json.dump(history_data, f, indent=2)
            
    def rollback_to_version(self, version_id: str) -> bool:
        """
        Rollback model to a previous version.
        
        Args:
            version_id: Version to rollback to
            
        Returns:
            Success status
        """
        # Find version
        version = None
        for v in self.model_versions:
            if v.version_id == version_id:
                version = v
                break
                
        if not version:
            logger.error(f"Version {version_id} not found")
            return False
            
        try:
            # Copy version file to current
            shutil.copy(version.file_path, self.model_path)
            
            # Update current version
            self.current_version = version
            
            # Add rollback belief
            rollback_belief = BeliefNode(
                id="",
                statement=f"I have reverted to model version {version_id}",
                confidence=1.0
            )
            self.knowledge_graph.add_belief(rollback_belief)
            
            logger.info(f"Rolled back to version {version_id}")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return False
            
    def get_version_history(self) -> List[ModelVersion]:
        """Get model version history."""
        return self.model_versions.copy()
        
    def compare_versions(self, 
                        version1_id: str,
                        version2_id: str) -> Dict[str, Any]:
        """
        Compare two model versions.
        
        Args:
            version1_id: First version ID
            version2_id: Second version ID
            
        Returns:
            Comparison results
        """
        v1 = next((v for v in self.model_versions if v.version_id == version1_id), None)
        v2 = next((v for v in self.model_versions if v.version_id == version2_id), None)
        
        if not v1 or not v2:
            return {"error": "Version not found"}
            
        comparison = {
            "version1": version1_id,
            "version2": version2_id,
            "patterns_difference": len(v2.patterns_added) - len(v1.patterns_added),
            "performance_change": {}
        }
        
        # Compare metrics
        for metric in v1.performance_metrics:
            if metric in v2.performance_metrics:
                change = v2.performance_metrics[metric] - v1.performance_metrics[metric]
                comparison["performance_change"][metric] = {
                    "v1": v1.performance_metrics[metric],
                    "v2": v2.performance_metrics[metric],
                    "change": change,
                    "percent_change": (change / v1.performance_metrics[metric] * 100) if v1.performance_metrics[metric] != 0 else 0
                }
                
        return comparison


# Example usage
if __name__ == "__main__":
    # Create mock components
    from ..knowledge.knowledge_graph import AgentKnowledgeGraph
    
    kg = AgentKnowledgeGraph("test_agent")
    
    # Create refinement system
    refinement = GNNModelRefinement(
        agent_id="test_agent",
        model_path="test_agent.gnn.md",
        knowledge_graph=kg
    )
    
    # Simulate learning and refinement
    print("Simulating agent learning and model refinement...")
    
    # Check if refinement needed
    if refinement.check_refinement_needed():
        print("Refinement triggered!")
        new_version = refinement.refine_model(reason="Test refinement")
        
        if new_version:
            print(f"Created new model version: {new_version.version_id}")
            print(f"Patterns added: {len(new_version.patterns_added)}")
            print(f"Performance metrics: {new_version.performance_metrics}")
    else:
        print("No refinement needed yet") 