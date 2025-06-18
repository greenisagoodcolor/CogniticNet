"""
Knowledge Sharing Protocol Module
Enables agents to share patterns and knowledge with each other.

Implements João Moura's principle: 
'Multi-agent coordination requires shared protocols and clear communication channels.'
"""

import uuid
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
import networkx as nx
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class SharingType(str, Enum):
    """Types of knowledge that can be shared."""
    PATTERN = "pattern"
    EXPERIENCE = "experience"
    MODEL_COMPONENT = "model_component"
    BELIEF_UPDATE = "belief_update"
    RESOURCE_LOCATION = "resource_location"


@dataclass
class KnowledgePackage:
    """
    A package of knowledge ready to be shared between agents.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = ""
    sharing_type: SharingType = SharingType.PATTERN
    content: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Convert to JSON for transmission."""
        return json.dumps({
            'id': self.id,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'sharing_type': self.sharing_type.value,
            'content': self.content,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        })
    
    @classmethod
    def from_json(cls, json_str: str) -> 'KnowledgePackage':
        """Create from JSON string."""
        data = json.loads(json_str)
        return cls(
            id=data['id'],
            sender_id=data['sender_id'],
            recipient_id=data['recipient_id'],
            sharing_type=SharingType(data['sharing_type']),
            content=data['content'],
            confidence=data['confidence'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data['metadata']
        )


class KnowledgeSharingProtocol:
    """
    Manages knowledge sharing between agents.
    
    Features:
    - Pattern packaging and transfer
    - Trust-based filtering
    - Knowledge integration
    - Conflict resolution
    """
    
    def __init__(
        self,
        min_confidence_threshold: float = 0.7,
        max_package_size: int = 1000
    ):
        self.min_confidence_threshold = min_confidence_threshold
        self.max_package_size = max_package_size
        self.trust_scores: Dict[Tuple[str, str], float] = {}  # (sender, recipient) -> trust
        self.sharing_history: List[KnowledgePackage] = []
    
    def prepare_pattern_package(
        self,
        agent_id: str,
        pattern: Dict[str, Any],
        recipient_id: str
    ) -> Optional[KnowledgePackage]:
        """
        Prepare a pattern for sharing.
        
        Args:
            agent_id: ID of the sharing agent
            pattern: Pattern data to share
            recipient_id: ID of the recipient agent
            
        Returns:
            KnowledgePackage if pattern meets sharing criteria
        """
        # Check pattern confidence
        confidence = pattern.get('confidence', 0.0)
        if confidence < self.min_confidence_threshold:
            logger.debug(f"Pattern confidence {confidence} below threshold")
            return None
        
        # Check pattern success rate
        success_rate = pattern.get('success_rate', 0.0)
        if success_rate < 0.6:  # Don't share patterns that fail often
            logger.debug(f"Pattern success rate {success_rate} too low")
            return None
        
        # Create package
        package = KnowledgePackage(
            sender_id=agent_id,
            recipient_id=recipient_id,
            sharing_type=SharingType.PATTERN,
            content={
                'pattern_id': pattern.get('id', str(uuid.uuid4())),
                'name': pattern.get('name', 'unnamed_pattern'),
                'trigger_conditions': pattern.get('trigger_conditions', {}),
                'action_sequence': pattern.get('action_sequence', []),
                'expected_outcome': pattern.get('expected_outcome', {}),
                'success_rate': success_rate,
                'occurrence_count': pattern.get('occurrence_count', 0)
            },
            confidence=confidence,
            metadata={
                'original_context': pattern.get('context', {}),
                'sharing_reason': self._determine_sharing_reason(pattern)
            }
        )
        
        return package
    
    def prepare_experience_package(
        self,
        agent_id: str,
        experience: Dict[str, Any],
        recipient_id: str
    ) -> Optional[KnowledgePackage]:
        """
        Prepare an experience for sharing.
        
        Args:
            agent_id: ID of the sharing agent
            experience: Experience data to share
            recipient_id: ID of the recipient agent
            
        Returns:
            KnowledgePackage if experience is worth sharing
        """
        # Check if experience led to significant learning
        free_energy_reduction = experience.get('free_energy_reduction', 0.0)
        if free_energy_reduction < 0.1:
            return None
        
        package = KnowledgePackage(
            sender_id=agent_id,
            recipient_id=recipient_id,
            sharing_type=SharingType.EXPERIENCE,
            content={
                'state': experience.get('state', {}),
                'action': experience.get('action', {}),
                'outcome': experience.get('outcome', {}),
                'free_energy_reduction': free_energy_reduction,
                'timestamp': experience.get('timestamp', datetime.utcnow()).isoformat()
            },
            confidence=min(1.0, free_energy_reduction),
            metadata={
                'location': experience.get('location', {}),
                'context': experience.get('context', {})
            }
        )
        
        return package
    
    def prepare_model_component_package(
        self,
        agent_id: str,
        component_type: str,
        component_data: Dict[str, Any],
        recipient_id: str
    ) -> Optional[KnowledgePackage]:
        """
        Prepare a model component for sharing.
        
        Args:
            agent_id: ID of the sharing agent
            component_type: Type of component (e.g., 'belief_update_rule')
            component_data: Component data
            recipient_id: ID of the recipient agent
            
        Returns:
            KnowledgePackage containing the component
        """
        # Validate component
        if not self._validate_component(component_type, component_data):
            return None
        
        package = KnowledgePackage(
            sender_id=agent_id,
            recipient_id=recipient_id,
            sharing_type=SharingType.MODEL_COMPONENT,
            content={
                'component_type': component_type,
                'component_data': component_data,
                'version': component_data.get('version', '1.0'),
                'compatibility': component_data.get('compatibility', {})
            },
            confidence=0.8,  # Model components have inherent confidence
            metadata={
                'performance_metrics': component_data.get('metrics', {}),
                'usage_count': component_data.get('usage_count', 0)
            }
        )
        
        return package
    
    def evaluate_package(
        self,
        package: KnowledgePackage,
        recipient_state: Dict[str, Any]
    ) -> Tuple[bool, float, str]:
        """
        Evaluate whether a knowledge package should be accepted.
        
        Args:
            package: Knowledge package to evaluate
            recipient_state: Current state of the recipient
            
        Returns:
            (should_accept, relevance_score, reason)
        """
        # Check trust score
        trust_key = (package.sender_id, package.recipient_id)
        trust_score = self.trust_scores.get(trust_key, 0.5)  # Default neutral trust
        
        if trust_score < 0.3:
            return False, 0.0, "Low trust in sender"
        
        # Check relevance based on type
        relevance_score = 0.0
        
        if package.sharing_type == SharingType.PATTERN:
            relevance_score = self._evaluate_pattern_relevance(
                package.content, recipient_state
            )
        elif package.sharing_type == SharingType.EXPERIENCE:
            relevance_score = self._evaluate_experience_relevance(
                package.content, recipient_state
            )
        elif package.sharing_type == SharingType.MODEL_COMPONENT:
            relevance_score = self._evaluate_component_relevance(
                package.content, recipient_state
            )
        
        # Combine trust and relevance
        acceptance_score = 0.6 * relevance_score + 0.4 * trust_score
        
        should_accept = acceptance_score > 0.5
        reason = "Accepted" if should_accept else "Relevance too low"
        
        return should_accept, relevance_score, reason
    
    def integrate_knowledge(
        self,
        package: KnowledgePackage,
        recipient_knowledge: nx.DiGraph
    ) -> Dict[str, Any]:
        """
        Integrate accepted knowledge into recipient's knowledge graph.
        
        Args:
            package: Knowledge package to integrate
            recipient_knowledge: Recipient's knowledge graph
            
        Returns:
            Integration result with statistics
        """
        result = {
            'success': False,
            'nodes_added': 0,
            'edges_added': 0,
            'conflicts_resolved': 0,
            'integration_type': package.sharing_type.value
        }
        
        try:
            if package.sharing_type == SharingType.PATTERN:
                result.update(self._integrate_pattern(
                    package.content, recipient_knowledge
                ))
            elif package.sharing_type == SharingType.EXPERIENCE:
                result.update(self._integrate_experience(
                    package.content, recipient_knowledge
                ))
            elif package.sharing_type == SharingType.MODEL_COMPONENT:
                result.update(self._integrate_component(
                    package.content, recipient_knowledge
                ))
            
            result['success'] = True
            
            # Update trust based on integration success
            self._update_trust(package, result)
            
        except Exception as e:
            logger.error(f"Knowledge integration failed: {e}")
            result['error'] = str(e)
        
        # Record in history
        self.sharing_history.append(package)
        
        return result
    
    def _determine_sharing_reason(self, pattern: Dict[str, Any]) -> str:
        """Determine why a pattern is worth sharing."""
        if pattern.get('success_rate', 0) > 0.9:
            return "highly_successful"
        elif pattern.get('occurrence_count', 0) > 100:
            return "frequently_used"
        elif pattern.get('free_energy_reduction', 0) > 1.0:
            return "significant_improvement"
        else:
            return "general_knowledge"
    
    def _validate_component(
        self,
        component_type: str,
        component_data: Dict[str, Any]
    ) -> bool:
        """Validate a model component before sharing."""
        valid_types = {
            'belief_update_rule', 'preference_function',
            'action_policy', 'observation_model'
        }
        
        if component_type not in valid_types:
            return False
        
        # Check required fields
        required_fields = {'name', 'parameters', 'implementation'}
        if not all(field in component_data for field in required_fields):
            return False
        
        return True
    
    def _evaluate_pattern_relevance(
        self,
        pattern: Dict[str, Any],
        recipient_state: Dict[str, Any]
    ) -> float:
        """Evaluate how relevant a pattern is to recipient."""
        relevance = 0.0
        
        # Check if trigger conditions match current state
        trigger_conditions = pattern.get('trigger_conditions', {})
        matches = 0
        for condition, value in trigger_conditions.items():
            if condition in recipient_state:
                if recipient_state[condition] == value:
                    matches += 1
        
        if trigger_conditions:
            relevance = matches / len(trigger_conditions)
        
        # Boost relevance for patterns addressing current challenges
        if recipient_state.get('free_energy', 0) > 5.0:
            relevance *= 1.5  # Recipient needs help
        
        return min(1.0, relevance)
    
    def _evaluate_experience_relevance(
        self,
        experience: Dict[str, Any],
        recipient_state: Dict[str, Any]
    ) -> float:
        """Evaluate how relevant an experience is to recipient."""
        relevance = 0.0
        
        # Check state similarity
        exp_state = experience.get('state', {})
        state_similarity = self._calculate_state_similarity(
            exp_state, recipient_state
        )
        
        # Check if outcome is desirable
        free_energy_reduction = experience.get('free_energy_reduction', 0)
        
        relevance = 0.7 * state_similarity + 0.3 * min(1.0, free_energy_reduction)
        
        return relevance
    
    def _evaluate_component_relevance(
        self,
        component: Dict[str, Any],
        recipient_state: Dict[str, Any]
    ) -> float:
        """Evaluate how relevant a model component is to recipient."""
        # Check compatibility
        compatibility = component.get('compatibility', {})
        agent_class = recipient_state.get('agent_class', 'unknown')
        
        if agent_class in compatibility:
            return compatibility[agent_class]
        
        return 0.5  # Neutral relevance if unknown
    
    def _calculate_state_similarity(
        self,
        state1: Dict[str, Any],
        state2: Dict[str, Any]
    ) -> float:
        """Calculate similarity between two states."""
        if not state1 or not state2:
            return 0.0
        
        common_keys = set(state1.keys()) & set(state2.keys())
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            val1 = state1[key]
            val2 = state2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                diff = abs(val1 - val2)
                max_val = max(abs(val1), abs(val2), 1.0)
                similarities.append(1.0 - diff / max_val)
            elif val1 == val2:
                similarities.append(1.0)
            else:
                similarities.append(0.0)
        
        return np.mean(similarities)
    
    def _integrate_pattern(
        self,
        pattern: Dict[str, Any],
        knowledge_graph: nx.DiGraph
    ) -> Dict[str, Any]:
        """Integrate a pattern into knowledge graph."""
        pattern_id = f"pattern_{pattern.get('pattern_id', uuid.uuid4())}"
        
        # Add pattern node
        knowledge_graph.add_node(
            pattern_id,
            type='pattern',
            data=pattern,
            timestamp=datetime.utcnow(),
            source='shared'
        )
        
        # Link to related concepts
        trigger_conditions = pattern.get('trigger_conditions', {})
        for condition in trigger_conditions:
            concept_id = f"concept_{condition}"
            if not knowledge_graph.has_node(concept_id):
                knowledge_graph.add_node(
                    concept_id,
                    type='concept',
                    data={'name': condition},
                    timestamp=datetime.utcnow()
                )
            knowledge_graph.add_edge(
                concept_id, pattern_id,
                type='triggers',
                weight=0.8
            )
        
        return {
            'nodes_added': 1 + len(trigger_conditions),
            'edges_added': len(trigger_conditions)
        }
    
    def _integrate_experience(
        self,
        experience: Dict[str, Any],
        knowledge_graph: nx.DiGraph
    ) -> Dict[str, Any]:
        """Integrate an experience into knowledge graph."""
        exp_id = f"experience_{uuid.uuid4()}"
        
        # Add experience node
        knowledge_graph.add_node(
            exp_id,
            type='experience',
            data=experience,
            timestamp=datetime.utcnow(),
            source='shared'
        )
        
        # Link to state concepts
        state = experience.get('state', {})
        edges_added = 0
        for key, value in state.items():
            concept_id = f"concept_{key}_{value}"
            if not knowledge_graph.has_node(concept_id):
                knowledge_graph.add_node(
                    concept_id,
                    type='concept',
                    data={'key': key, 'value': value},
                    timestamp=datetime.utcnow()
                )
            knowledge_graph.add_edge(
                concept_id, exp_id,
                type='relates_to',
                weight=0.6
            )
            edges_added += 1
        
        return {
            'nodes_added': 1 + len(state),
            'edges_added': edges_added
        }
    
    def _integrate_component(
        self,
        component: Dict[str, Any],
        knowledge_graph: nx.DiGraph
    ) -> Dict[str, Any]:
        """Integrate a model component into knowledge graph."""
        comp_id = f"component_{component.get('component_type')}_{uuid.uuid4()}"
        
        # Add component node
        knowledge_graph.add_node(
            comp_id,
            type='model_component',
            data=component,
            timestamp=datetime.utcnow(),
            source='shared'
        )
        
        return {
            'nodes_added': 1,
            'edges_added': 0,
            'component_stored': True
        }
    
    def _update_trust(
        self,
        package: KnowledgePackage,
        integration_result: Dict[str, Any]
    ) -> None:
        """Update trust score based on integration success."""
        trust_key = (package.sender_id, package.recipient_id)
        current_trust = self.trust_scores.get(trust_key, 0.5)
        
        if integration_result['success']:
            # Increase trust slightly
            new_trust = min(1.0, current_trust + 0.05)
        else:
            # Decrease trust
            new_trust = max(0.0, current_trust - 0.1)
        
        self.trust_scores[trust_key] = new_trust
    
    def get_sharing_statistics(self) -> Dict[str, Any]:
        """Get statistics about knowledge sharing."""
        if not self.sharing_history:
            return {
                'total_shared': 0,
                'by_type': {},
                'average_confidence': 0.0,
                'trust_network': {}
            }
        
        by_type = defaultdict(int)
        total_confidence = 0.0
        
        for package in self.sharing_history:
            by_type[package.sharing_type.value] += 1
            total_confidence += package.confidence
        
        return {
            'total_shared': len(self.sharing_history),
            'by_type': dict(by_type),
            'average_confidence': total_confidence / len(self.sharing_history),
            'trust_network': dict(self.trust_scores)
        }


class KnowledgeBroadcaster:
    """
    Manages broadcasting knowledge to multiple agents.
    """
    
    def __init__(self, protocol: KnowledgeSharingProtocol):
        self.protocol = protocol
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)  # topic -> agent_ids
    
    def subscribe(self, agent_id: str, topic: str) -> None:
        """Subscribe an agent to a knowledge topic."""
        self.subscribers[topic].add(agent_id)
    
    def broadcast_discovery(
        self,
        sender_id: str,
        discovery_type: str,
        discovery_data: Dict[str, Any]
    ) -> List[KnowledgePackage]:
        """
        Broadcast a discovery to interested agents.
        
        Args:
            sender_id: ID of discovering agent
            discovery_type: Type of discovery
            discovery_data: Discovery details
            
        Returns:
            List of knowledge packages sent
        """
        packages = []
        
        # Determine relevant topic
        topic = self._discovery_to_topic(discovery_type)
        
        # Get subscribers
        recipients = self.subscribers.get(topic, set())
        
        for recipient_id in recipients:
            if recipient_id == sender_id:
                continue  # Don't send to self
            
            # Create appropriate package
            if discovery_type == 'resource':
                package = KnowledgePackage(
                    sender_id=sender_id,
                    recipient_id=recipient_id,
                    sharing_type=SharingType.RESOURCE_LOCATION,
                    content=discovery_data,
                    confidence=0.9,
                    metadata={'discovery_type': discovery_type}
                )
            else:
                # Use experience package for other discoveries
                package = self.protocol.prepare_experience_package(
                    sender_id, discovery_data, recipient_id
                )
            
            if package:
                packages.append(package)
        
        return packages
    
    def _discovery_to_topic(self, discovery_type: str) -> str:
        """Map discovery type to subscription topic."""
        topic_map = {
            'resource': 'resource_locations',
            'danger': 'danger_alerts',
            'pattern': 'successful_patterns',
            'path': 'efficient_paths'
        }
        return topic_map.get(discovery_type, 'general_discoveries') 