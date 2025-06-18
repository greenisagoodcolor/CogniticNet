"""
Agent Knowledge Graph Construction
Dynamic knowledge graph for each agent's learning and memory using NetworkX.
"""

import networkx as nx
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging
from sklearn.metrics.pairwise import cosine_similarity
import hashlib

logger = logging.getLogger(__name__)


class NodeType(Enum):
    """Types of nodes in the knowledge graph."""
    EXPERIENCE = "experience"
    PATTERN = "pattern"
    BELIEF = "belief"
    GOAL = "goal"
    PREDICTION = "prediction"


@dataclass
class ExperienceNode:
    """Represents a single experience in the knowledge graph."""
    id: str
    timestamp: datetime
    location: str  # H3 hex ID
    observation: Dict[str, Any]
    action: Dict[str, Any]
    outcome: Dict[str, Any]
    free_energy: float
    confidence: float = 0.5
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "observation": self.observation,
            "action": self.action,
            "outcome": self.outcome,
            "free_energy": self.free_energy,
            "confidence": self.confidence
        }


@dataclass
class PatternNode:
    """Represents a learned pattern from experiences."""
    id: str
    name: str
    trigger_conditions: Dict[str, Any]
    action_sequence: List[Dict[str, Any]]
    expected_outcome: Dict[str, Any]
    confidence: float = 0.0
    occurrence_count: int = 0
    success_rate: float = 0.0
    source_experiences: List[str] = field(default_factory=list)
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "trigger_conditions": self.trigger_conditions,
            "action_sequence": self.action_sequence,
            "expected_outcome": self.expected_outcome,
            "confidence": self.confidence,
            "occurrence_count": self.occurrence_count,
            "success_rate": self.success_rate,
            "source_experiences": self.source_experiences
        }


@dataclass
class BeliefNode:
    """Represents a belief about the world."""
    id: str
    statement: str
    confidence: float
    supporting_patterns: List[str] = field(default_factory=list)
    contradicting_patterns: List[str] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "statement": self.statement,
            "confidence": self.confidence,
            "supporting_patterns": self.supporting_patterns,
            "contradicting_patterns": self.contradicting_patterns,
            "last_updated": self.last_updated.isoformat()
        }


class EmbeddingSystem:
    """
    Simple embedding system for experiences and patterns.
    Uses feature hashing for simplicity - could be replaced with
    more sophisticated embeddings (e.g., using language models).
    """
    
    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        
    def create_experience_embedding(self, experience: ExperienceNode) -> np.ndarray:
        """Create embedding for an experience."""
        # Combine all relevant features
        features = []
        
        # Location embedding (hash of hex ID)
        location_hash = int(hashlib.md5(experience.location.encode()).hexdigest()[:8], 16)
        features.append(location_hash)
        
        # Observation features
        features.extend(self._extract_features(experience.observation))
        
        # Action features
        features.extend(self._extract_features(experience.action))
        
        # Outcome features
        features.extend(self._extract_features(experience.outcome))
        
        # Free energy and confidence
        features.append(int(experience.free_energy * 1000))
        features.append(int(experience.confidence * 1000))
        
        # Create embedding using feature hashing
        embedding = np.zeros(self.embedding_dim)
        for i, feature in enumerate(features):
            # Hash feature to get index
            idx = hash((i, feature)) % self.embedding_dim
            # Add to embedding (handling collisions with addition)
            embedding[idx] += 1
            
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
        
    def create_pattern_embedding(self, pattern: PatternNode) -> np.ndarray:
        """Create embedding for a pattern."""
        features = []
        
        # Pattern name hash
        name_hash = int(hashlib.md5(pattern.name.encode()).hexdigest()[:8], 16)
        features.append(name_hash)
        
        # Trigger condition features
        features.extend(self._extract_features(pattern.trigger_conditions))
        
        # Action sequence features
        for action in pattern.action_sequence:
            features.extend(self._extract_features(action))
            
        # Expected outcome features
        features.extend(self._extract_features(pattern.expected_outcome))
        
        # Confidence and success rate
        features.append(int(pattern.confidence * 1000))
        features.append(int(pattern.success_rate * 1000))
        
        # Create embedding
        embedding = np.zeros(self.embedding_dim)
        for i, feature in enumerate(features):
            idx = hash((i, feature)) % self.embedding_dim
            embedding[idx] += 1
            
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
        
    def create_belief_embedding(self, belief: BeliefNode) -> np.ndarray:
        """Create embedding for a belief."""
        # Simple word-based embedding for belief statements
        words = belief.statement.lower().split()
        
        embedding = np.zeros(self.embedding_dim)
        for i, word in enumerate(words):
            # Hash word to get index
            idx = hash(word) % self.embedding_dim
            # TF-IDF-like weighting (simplified)
            weight = 1.0 / (1.0 + np.log(1 + i))
            embedding[idx] += weight
            
        # Add confidence as a feature
        embedding[0] = belief.confidence
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
        
    def _extract_features(self, data: Dict[str, Any]) -> List[int]:
        """Extract numerical features from dictionary data."""
        features = []
        
        for key, value in data.items():
            # Hash the key
            key_hash = hash(key) % 10000
            features.append(key_hash)
            
            # Handle different value types
            if isinstance(value, (int, float)):
                features.append(int(value * 100))
            elif isinstance(value, str):
                features.append(hash(value) % 10000)
            elif isinstance(value, bool):
                features.append(1 if value else 0)
            elif isinstance(value, (list, tuple)):
                features.append(len(value))
                for item in value[:5]:  # Limit to first 5 items
                    if isinstance(item, (int, float)):
                        features.append(int(item * 100))
                    else:
                        features.append(hash(str(item)) % 10000)
            elif isinstance(value, dict):
                features.extend(self._extract_features(value))
                
        return features
        
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        # Reshape for sklearn
        e1 = embedding1.reshape(1, -1)
        e2 = embedding2.reshape(1, -1)
        
        similarity = cosine_similarity(e1, e2)[0, 0]
        return float(similarity)


class AgentKnowledgeGraph:
    """
    Dynamic knowledge graph for agent learning and memory.
    
    Uses NetworkX directed graph to store experiences, patterns,
    and beliefs with similarity-based connections.
    """
    
    PATTERN_EXTRACTION_INTERVAL = 10  # Extract patterns every N experiences
    SIMILARITY_THRESHOLD = 0.7  # Minimum similarity to create edge
    
    def __init__(self, agent_id: str, embedding_dim: int = 128):
        """
        Initialize knowledge graph for an agent.
        
        Args:
            agent_id: Unique identifier for the agent
            embedding_dim: Dimension of embedding vectors
        """
        self.agent_id = agent_id
        self.graph = nx.DiGraph()
        self.embedding_system = EmbeddingSystem(embedding_dim)
        
        # Counters and caches
        self.experience_count = 0
        self.pattern_count = 0
        self.belief_count = 0
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        
        logger.info(f"Created knowledge graph for agent {agent_id}")
        
    def add_experience(self, experience: ExperienceNode) -> str:
        """Add an experience to the knowledge graph."""
        # Generate ID if not provided
        if not experience.id:
            experience.id = f"exp_{self.agent_id}_{self.experience_count}"
            
        # Create embedding
        embedding = self.embedding_system.create_experience_embedding(experience)
        experience.embedding = embedding
        self.embeddings_cache[experience.id] = embedding
        
        # Add node to graph
        self.graph.add_node(
            experience.id,
            type=NodeType.EXPERIENCE,
            data=experience,
            timestamp=experience.timestamp
        )
        
        # Find and connect similar experiences
        similar_experiences = self._find_similar_experiences(experience)
        for sim_id, similarity in similar_experiences:
            self.graph.add_edge(
                experience.id,
                sim_id,
                weight=similarity,
                relation="similar_to"
            )
            # Bidirectional similarity
            self.graph.add_edge(
                sim_id,
                experience.id,
                weight=similarity,
                relation="similar_to"
            )
            
        self.experience_count += 1
        
        # Extract patterns periodically
        if self.experience_count % self.PATTERN_EXTRACTION_INTERVAL == 0:
            self._extract_patterns()
            
        logger.debug(f"Added experience {experience.id} to knowledge graph")
        return experience.id
        
    def add_pattern(self, pattern: PatternNode) -> str:
        """Add a learned pattern to the knowledge graph."""
        # Generate ID if not provided
        if not pattern.id:
            pattern.id = f"pat_{self.agent_id}_{self.pattern_count}"
            
        # Create embedding
        embedding = self.embedding_system.create_pattern_embedding(pattern)
        pattern.embedding = embedding
        self.embeddings_cache[pattern.id] = embedding
        
        # Add node to graph
        self.graph.add_node(
            pattern.id,
            type=NodeType.PATTERN,
            data=pattern
        )
        
        # Connect to source experiences
        for exp_id in pattern.source_experiences:
            if self.graph.has_node(exp_id):
                self.graph.add_edge(
                    pattern.id,
                    exp_id,
                    relation="derived_from"
                )
                
        # Find and connect similar patterns
        similar_patterns = self._find_similar_patterns(pattern)
        for sim_id, similarity in similar_patterns:
            self.graph.add_edge(
                pattern.id,
                sim_id,
                weight=similarity,
                relation="similar_to"
            )
            
        self.pattern_count += 1
        
        # Update beliefs based on new pattern
        self._update_beliefs(pattern)
        
        logger.debug(f"Added pattern {pattern.id} to knowledge graph")
        return pattern.id
        
    def add_belief(self, belief: BeliefNode) -> str:
        """Add a belief to the knowledge graph."""
        # Generate ID if not provided
        if not belief.id:
            belief.id = f"bel_{self.agent_id}_{self.belief_count}"
            
        # Create embedding
        embedding = self.embedding_system.create_belief_embedding(belief)
        belief.embedding = embedding
        self.embeddings_cache[belief.id] = embedding
        
        # Add node to graph
        self.graph.add_node(
            belief.id,
            type=NodeType.BELIEF,
            data=belief
        )
        
        # Connect to supporting/contradicting patterns
        for pat_id in belief.supporting_patterns:
            if self.graph.has_node(pat_id):
                self.graph.add_edge(
                    belief.id,
                    pat_id,
                    relation="supported_by"
                )
                
        for pat_id in belief.contradicting_patterns:
            if self.graph.has_node(pat_id):
                self.graph.add_edge(
                    belief.id,
                    pat_id,
                    relation="contradicted_by"
                )
                
        self.belief_count += 1
        
        logger.debug(f"Added belief {belief.id} to knowledge graph")
        return belief.id
        
    def query_similar_experiences(self, 
                                  observation: Dict[str, Any],
                                  k: int = 5) -> List[Tuple[ExperienceNode, float]]:
        """Find k most similar past experiences to current observation."""
        # Create a temporary experience for comparison
        temp_exp = ExperienceNode(
            id="temp",
            timestamp=datetime.utcnow(),
            location="",
            observation=observation,
            action={},
            outcome={},
            free_energy=0.0
        )
        
        embedding = self.embedding_system.create_experience_embedding(temp_exp)
        
        # Find similar experiences
        similarities = []
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == NodeType.EXPERIENCE:
                node_embedding = self.embeddings_cache.get(node_id)
                if node_embedding is not None:
                    similarity = self.embedding_system.calculate_similarity(
                        embedding, node_embedding
                    )
                    similarities.append((node_data["data"], similarity))
                    
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
        
    def get_applicable_patterns(self, 
                                observation: Dict[str, Any],
                                threshold: float = 0.6) -> List[PatternNode]:
        """Get patterns that might apply to current situation."""
        applicable = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == NodeType.PATTERN:
                pattern = node_data["data"]
                
                # Check if trigger conditions match (simplified)
                match_score = self._calculate_condition_match(
                    pattern.trigger_conditions,
                    observation
                )
                
                if match_score >= threshold:
                    applicable.append(pattern)
                    
        # Sort by confidence and success rate
        applicable.sort(
            key=lambda p: p.confidence * p.success_rate,
            reverse=True
        )
        
        return applicable
        
    def update_pattern_success(self, pattern_id: str, success: bool):
        """Update pattern statistics based on execution outcome."""
        if not self.graph.has_node(pattern_id):
            return
            
        node_data = self.graph.nodes[pattern_id]
        if node_data["type"] != NodeType.PATTERN:
            return
            
        pattern = node_data["data"]
        pattern.occurrence_count += 1
        
        # Update success rate with moving average
        alpha = 0.1  # Learning rate
        pattern.success_rate = (1 - alpha) * pattern.success_rate + alpha * (1.0 if success else 0.0)
        
        # Update confidence based on occurrence count and success rate
        pattern.confidence = min(1.0, pattern.occurrence_count / 100.0) * pattern.success_rate
        
        logger.debug(f"Updated pattern {pattern_id}: success_rate={pattern.success_rate:.2f}")
        
    def get_strongest_beliefs(self, k: int = 10) -> List[BeliefNode]:
        """Get the k strongest beliefs."""
        beliefs = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == NodeType.BELIEF:
                beliefs.append(node_data["data"])
                
        # Sort by confidence
        beliefs.sort(key=lambda b: b.confidence, reverse=True)
        return beliefs[:k]
        
    def _find_similar_experiences(self, 
                                  experience: ExperienceNode,
                                  k: int = 5) -> List[Tuple[str, float]]:
        """Find k most similar experiences already in the graph."""
        if experience.embedding is None:
            return []
            
        similarities = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if (node_data["type"] == NodeType.EXPERIENCE and 
                node_id != experience.id):
                node_embedding = self.embeddings_cache.get(node_id)
                if node_embedding is not None:
                    similarity = self.embedding_system.calculate_similarity(
                        experience.embedding,
                        node_embedding
                    )
                    if similarity >= self.SIMILARITY_THRESHOLD:
                        similarities.append((node_id, similarity))
                        
        # Sort and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
        
    def _find_similar_patterns(self,
                               pattern: PatternNode,
                               k: int = 3) -> List[Tuple[str, float]]:
        """Find k most similar patterns already in the graph."""
        if pattern.embedding is None:
            return []
            
        similarities = []
        
        for node_id, node_data in self.graph.nodes(data=True):
            if (node_data["type"] == NodeType.PATTERN and 
                node_id != pattern.id):
                node_embedding = self.embeddings_cache.get(node_id)
                if node_embedding is not None:
                    similarity = self.embedding_system.calculate_similarity(
                        pattern.embedding,
                        node_embedding
                    )
                    if similarity >= self.SIMILARITY_THRESHOLD:
                        similarities.append((node_id, similarity))
                        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
        
    def _extract_patterns(self):
        """Extract patterns from recent experiences."""
        # Get recent experiences
        recent_experiences = []
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == NodeType.EXPERIENCE:
                recent_experiences.append((node_id, node_data["data"]))
                
        # Sort by timestamp and take last N
        recent_experiences.sort(
            key=lambda x: x[1].timestamp,
            reverse=True
        )
        recent_experiences = recent_experiences[:self.PATTERN_EXTRACTION_INTERVAL * 2]
        
        # Look for repeated sequences (simplified pattern extraction)
        # In a real system, this would use more sophisticated sequence mining
        action_sequences = {}
        
        for i in range(len(recent_experiences) - 1):
            exp1_id, exp1 = recent_experiences[i]
            exp2_id, exp2 = recent_experiences[i + 1]
            
            # Create action sequence key
            action_key = (
                json.dumps(exp1.action, sort_keys=True),
                json.dumps(exp2.action, sort_keys=True)
            )
            
            if action_key not in action_sequences:
                action_sequences[action_key] = []
                
            action_sequences[action_key].append({
                "experiences": [exp1_id, exp2_id],
                "trigger": exp1.observation,
                "outcome": exp2.outcome,
                "free_energy_delta": exp2.free_energy - exp1.free_energy
            })
            
        # Create patterns from repeated sequences
        for action_key, occurrences in action_sequences.items():
            if len(occurrences) >= 2:  # Pattern must occur at least twice
                # Calculate average outcome
                avg_fe_delta = np.mean([o["free_energy_delta"] for o in occurrences])
                
                # Create pattern
                pattern = PatternNode(
                    id="",
                    name=f"pattern_from_actions_{self.pattern_count}",
                    trigger_conditions=occurrences[0]["trigger"],
                    action_sequence=[
                        json.loads(action_key[0]),
                        json.loads(action_key[1])
                    ],
                    expected_outcome=occurrences[0]["outcome"],
                    confidence=len(occurrences) / 10.0,  # Simple confidence
                    occurrence_count=len(occurrences),
                    success_rate=0.5 if avg_fe_delta < 0 else 0.8,  # FE reduction = success
                    source_experiences=[exp_id for o in occurrences for exp_id in o["experiences"]]
                )
                
                self.add_pattern(pattern)
                
        logger.info(f"Extracted {len(action_sequences)} potential patterns")
        
    def _update_beliefs(self, pattern: PatternNode):
        """Update beliefs based on new pattern."""
        # This is a simplified belief update
        # In a real system, this would use more sophisticated reasoning
        
        # Look for existing beliefs that might be affected
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data["type"] == NodeType.BELIEF:
                belief = node_data["data"]
                
                # Check if pattern supports or contradicts belief
                # (This is highly simplified - real implementation would be more sophisticated)
                if pattern.confidence > 0.7 and pattern.success_rate > 0.7:
                    # Strong pattern might support related beliefs
                    belief_keywords = set(belief.statement.lower().split())
                    pattern_keywords = set(pattern.name.lower().split())
                    
                    overlap = len(belief_keywords & pattern_keywords)
                    if overlap > 0:
                        belief.supporting_patterns.append(pattern.id)
                        belief.confidence = min(1.0, belief.confidence + 0.1)
                        belief.last_updated = datetime.utcnow()
                        
    def _calculate_condition_match(self,
                                   conditions: Dict[str, Any],
                                   observation: Dict[str, Any]) -> float:
        """Calculate how well conditions match an observation."""
        if not conditions:
            return 0.0
            
        matches = 0
        total = 0
        
        for key, expected_value in conditions.items():
            if key in observation:
                total += 1
                actual_value = observation[key]
                
                # Different matching strategies based on type
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    # Numeric similarity
                    diff = abs(expected_value - actual_value)
                    max_val = max(abs(expected_value), abs(actual_value), 1.0)
                    similarity = 1.0 - (diff / max_val)
                    matches += similarity
                elif expected_value == actual_value:
                    # Exact match
                    matches += 1
                elif isinstance(expected_value, str) and isinstance(actual_value, str):
                    # String similarity (simple)
                    if expected_value.lower() in actual_value.lower():
                        matches += 0.5
                        
        return matches / total if total > 0 else 0.0
        
    def visualize_subgraph(self, center_node: str, depth: int = 2) -> Dict[str, Any]:
        """Get subgraph around a node for visualization."""
        if not self.graph.has_node(center_node):
            return {}
            
        # Get all nodes within depth
        subgraph_nodes = {center_node}
        current_layer = {center_node}
        
        for _ in range(depth):
            next_layer = set()
            for node in current_layer:
                # Add predecessors and successors
                next_layer.update(self.graph.predecessors(node))
                next_layer.update(self.graph.successors(node))
            subgraph_nodes.update(next_layer)
            current_layer = next_layer
            
        # Create subgraph
        subgraph = self.graph.subgraph(subgraph_nodes)
        
        # Convert to visualization format
        viz_data = {
            "nodes": [],
            "edges": []
        }
        
        for node_id in subgraph.nodes():
            node_data = self.graph.nodes[node_id]
            viz_data["nodes"].append({
                "id": node_id,
                "type": node_data["type"].value,
                "label": self._get_node_label(node_data)
            })
            
        for source, target, edge_data in subgraph.edges(data=True):
            viz_data["edges"].append({
                "source": source,
                "target": target,
                "relation": edge_data.get("relation", ""),
                "weight": edge_data.get("weight", 1.0)
            })
            
        return viz_data
        
    def _get_node_label(self, node_data: Dict[str, Any]) -> str:
        """Get a short label for a node."""
        data = node_data["data"]
        node_type = node_data["type"]
        
        if node_type == NodeType.EXPERIENCE:
            return f"Exp: {data.location[:8]}..."
        elif node_type == NodeType.PATTERN:
            return f"Pat: {data.name}"
        elif node_type == NodeType.BELIEF:
            return f"Bel: {data.statement[:20]}..."
        else:
            return node_type.value
            
    def save_to_file(self, filepath: str):
        """Save knowledge graph to file."""
        # Convert graph to serializable format
        data = {
            "agent_id": self.agent_id,
            "experience_count": self.experience_count,
            "pattern_count": self.pattern_count,
            "belief_count": self.belief_count,
            "nodes": {},
            "edges": []
        }
        
        # Save nodes
        for node_id, node_data in self.graph.nodes(data=True):
            data["nodes"][node_id] = {
                "type": node_data["type"].value,
                "data": node_data["data"].to_dict()
            }
            
        # Save edges
        for source, target, edge_data in self.graph.edges(data=True):
            data["edges"].append({
                "source": source,
                "target": target,
                "data": edge_data
            })
            
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
            
    @classmethod
    def load_from_file(cls, filepath: str) -> 'AgentKnowledgeGraph':
        """Load knowledge graph from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
            
        # Create graph
        graph = cls(data["agent_id"])
        graph.experience_count = data["experience_count"]
        graph.pattern_count = data["pattern_count"]
        graph.belief_count = data["belief_count"]
        
        # Recreate nodes
        # (Would need to recreate proper objects from dict data)
        # This is simplified - full implementation would reconstruct
        # proper ExperienceNode, PatternNode, BeliefNode objects
        
        return graph


# Example usage
if __name__ == "__main__":
    # Create knowledge graph
    kg = AgentKnowledgeGraph("test_agent")
    
    # Add some experiences
    for i in range(20):
        exp = ExperienceNode(
            id=f"exp_{i}",
            timestamp=datetime.utcnow(),
            location=f"hex_{i % 5}",
            observation={
                "resources": {"food": i * 10, "water": 100 - i * 5},
                "nearby_agents": i % 3
            },
            action={"type": "gather", "target": "food" if i % 2 == 0 else "water"},
            outcome={"success": i % 3 != 0, "resource_gained": i * 2},
            free_energy=100 - i * 2,
            confidence=0.5 + i * 0.02
        )
        kg.add_experience(exp)
        
    # Query similar experiences
    similar = kg.query_similar_experiences(
        {"resources": {"food": 50, "water": 50}, "nearby_agents": 1}
    )
    
    print(f"Found {len(similar)} similar experiences")
    for exp, sim in similar[:3]:
        print(f"  - {exp.id}: similarity={sim:.2f}")
        
    # Get applicable patterns
    patterns = kg.get_applicable_patterns(
        {"resources": {"food": 30, "water": 70}}
    )
    
    print(f"\nFound {len(patterns)} applicable patterns")
    for pattern in patterns:
        print(f"  - {pattern.name}: confidence={pattern.confidence:.2f}") 