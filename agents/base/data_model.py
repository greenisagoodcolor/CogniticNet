"""
Agent Data Model for FreeAgentics

This module defines the core data structures for agents, including:
- Agent properties (position, orientation, health, etc.)
- Agent capabilities and personality traits
- Relationships to other entities
- Extensibility for future agent types
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import uuid
from datetime import datetime
import numpy as np
from numpy.typing import NDArray


class AgentStatus(Enum):
    """Possible agent states"""
    IDLE = "idle"
    MOVING = "moving"
    INTERACTING = "interacting"
    PLANNING = "planning"
    LEARNING = "learning"
    OFFLINE = "offline"
    ERROR = "error"


class PersonalityTraits(Enum):
    """Big Five personality traits for agents"""
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class AgentCapability(Enum):
    """Agent capabilities that can be enabled/disabled"""
    MOVEMENT = "movement"
    PERCEPTION = "perception"
    COMMUNICATION = "communication"
    MEMORY = "memory"
    LEARNING = "learning"
    PLANNING = "planning"
    RESOURCE_MANAGEMENT = "resource_management"
    SOCIAL_INTERACTION = "social_interaction"


@dataclass
class Position:
    """3D position in the environment"""
    x: float
    y: float
    z: float = 0.0

    def to_array(self) -> NDArray[np.float64]:
        """Convert to numpy array"""
        return np.array([self.x, self.y, self.z])

    def distance_to(self, other: 'Position') -> float:
        """Calculate Euclidean distance to another position"""
        return float(np.linalg.norm(self.to_array() - other.to_array()))


@dataclass
class Orientation:
    """Agent orientation using quaternion representation"""
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_euler(self) -> Tuple[float, float, float]:
        """Convert quaternion to Euler angles (roll, pitch, yaw)"""
        # Conversion formula
        roll = np.arctan2(2*(self.w*self.x + self.y*self.z),
                          1 - 2*(self.x**2 + self.y**2))
        pitch = np.arcsin(2*(self.w*self.y - self.z*self.x))
        yaw = np.arctan2(2*(self.w*self.z + self.x*self.y),
                         1 - 2*(self.y**2 + self.z**2))
        return roll, pitch, yaw


@dataclass
class AgentPersonality:
    """Agent personality based on Big Five model"""
    openness: float = 0.5  # 0.0 to 1.0
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

    def to_vector(self) -> np.ndarray:
        """Convert personality to vector for GNN processing"""
        return np.array([
            self.openness,
            self.conscientiousness,
            self.extraversion,
            self.agreeableness,
            self.neuroticism
        ])

    def validate(self) -> bool:
        """Validate that all traits are within valid range"""
        traits = [self.openness, self.conscientiousness,
                 self.extraversion, self.agreeableness, self.neuroticism]
        return all(0.0 <= trait <= 1.0 for trait in traits)


@dataclass
class AgentResources:
    """Agent resource management"""
    energy: float = 100.0
    health: float = 100.0
    memory_capacity: float = 100.0
    memory_used: float = 0.0

    def has_sufficient_energy(self, required: float) -> bool:
        """Check if agent has enough energy for an action"""
        return self.energy >= required

    def consume_energy(self, amount: float) -> None:
        """Consume energy, ensuring it doesn't go negative"""
        self.energy = max(0.0, self.energy - amount)

    def restore_energy(self, amount: float) -> None:
        """Restore energy up to maximum"""
        self.energy = min(100.0, self.energy + amount)


@dataclass
class SocialRelationship:
    """Relationship between agents"""
    target_agent_id: str
    relationship_type: str  # friend, enemy, neutral, ally, etc.
    trust_level: float = 0.5  # 0.0 to 1.0
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None

    def update_trust(self, delta: float) -> None:
        """Update trust level, keeping it within bounds"""
        self.trust_level = max(0.0, min(1.0, self.trust_level + delta))


@dataclass
class AgentGoal:
    """Individual agent goal"""
    goal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    priority: float = 0.5  # 0.0 to 1.0
    target_position: Optional[Position] = None
    target_agent_id: Optional[str] = None
    deadline: Optional[datetime] = None
    completed: bool = False
    progress: float = 0.0  # 0.0 to 1.0

    def is_expired(self) -> bool:
        """Check if goal has passed its deadline"""
        if self.deadline is None:
            return False
        return datetime.now() > self.deadline


@dataclass
class Agent:
    """Core agent data model"""
    # Unique identification
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "Agent"
    agent_type: str = "basic"

    # Physical properties
    position: Position = field(default_factory=lambda: Position(0.0, 0.0, 0.0))
    orientation: Orientation = field(default_factory=Orientation)
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(3))

    # Status and capabilities
    status: AgentStatus = AgentStatus.IDLE
    capabilities: Set[AgentCapability] = field(default_factory=lambda: {
        AgentCapability.MOVEMENT,
        AgentCapability.PERCEPTION,
        AgentCapability.COMMUNICATION,
        AgentCapability.MEMORY,
        AgentCapability.LEARNING
    })

    # Personality and behavior
    personality: AgentPersonality = field(default_factory=AgentPersonality)

    # Resources
    resources: AgentResources = field(default_factory=AgentResources)

    # Social aspects
    relationships: Dict[str, SocialRelationship] = field(default_factory=dict)

    # Goals and objectives
    goals: List[AgentGoal] = field(default_factory=list)
    current_goal: Optional[AgentGoal] = None

    # Memory and experience
    short_term_memory: List[Dict[str, Any]] = field(default_factory=list)
    long_term_memory: List[Dict[str, Any]] = field(default_factory=list)
    experience_count: int = 0

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Active Inference integration
    belief_state: Optional[np.ndarray] = None
    generative_model_params: Dict[str, Any] = field(default_factory=dict)

    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability"""
        return capability in self.capabilities

    def add_capability(self, capability: AgentCapability) -> None:
        """Add a new capability to the agent"""
        self.capabilities.add(capability)

    def remove_capability(self, capability: AgentCapability) -> None:
        """Remove a capability from the agent"""
        self.capabilities.discard(capability)

    def add_relationship(self, relationship: SocialRelationship) -> None:
        """Add or update a social relationship"""
        self.relationships[relationship.target_agent_id] = relationship

    def get_relationship(self, agent_id: str) -> Optional[SocialRelationship]:
        """Get relationship with another agent"""
        return self.relationships.get(agent_id)

    def add_goal(self, goal: AgentGoal) -> None:
        """Add a new goal to the agent's objectives"""
        self.goals.append(goal)
        # Sort goals by priority
        self.goals.sort(key=lambda g: g.priority, reverse=True)

    def select_next_goal(self) -> Optional[AgentGoal]:
        """Select the next goal to pursue"""
        # Filter out completed and expired goals
        active_goals = [g for g in self.goals
                       if not g.completed and not g.is_expired()]
        if active_goals:
            self.current_goal = active_goals[0]
            return self.current_goal
        return None

    def add_to_memory(self, experience: Dict[str, Any],
                     is_important: bool = False) -> None:
        """Add an experience to memory"""
        timestamped_experience = {
            "timestamp": datetime.now(),
            "experience": experience,
            "importance": is_important
        }

        self.short_term_memory.append(timestamped_experience)
        self.experience_count += 1

        # Move to long-term memory if important or short-term is full
        if is_important or len(self.short_term_memory) > 100:
            if is_important:
                self.long_term_memory.append(timestamped_experience)
            # Trim short-term memory
            if len(self.short_term_memory) > 100:
                self.short_term_memory = self.short_term_memory[-50:]

    def update_position(self, new_position: Position) -> None:
        """Update agent position and timestamp"""
        self.position = new_position
        self.last_updated = datetime.now()

    def update_status(self, new_status: AgentStatus) -> None:
        """Update agent status"""
        self.status = new_status
        self.last_updated = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary for serialization"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "position": {
                "x": self.position.x,
                "y": self.position.y,
                "z": self.position.z
            },
            "orientation": {
                "w": self.orientation.w,
                "x": self.orientation.x,
                "y": self.orientation.y,
                "z": self.orientation.z
            },
            "velocity": self.velocity.tolist(),
            "status": self.status.value,
            "capabilities": [cap.value for cap in self.capabilities],
            "personality": {
                "openness": self.personality.openness,
                "conscientiousness": self.personality.conscientiousness,
                "extraversion": self.personality.extraversion,
                "agreeableness": self.personality.agreeableness,
                "neuroticism": self.personality.neuroticism
            },
            "resources": {
                "energy": self.resources.energy,
                "health": self.resources.health,
                "memory_capacity": self.resources.memory_capacity,
                "memory_used": self.resources.memory_used
            },
            "relationships": {
                agent_id: {
                    "target_agent_id": rel.target_agent_id,
                    "relationship_type": rel.relationship_type,
                    "trust_level": rel.trust_level,
                    "interaction_count": rel.interaction_count,
                    "last_interaction": rel.last_interaction.isoformat() if rel.last_interaction else None
                } for agent_id, rel in self.relationships.items()
            },
            "goals": [
                {
                    "goal_id": goal.goal_id,
                    "description": goal.description,
                    "priority": goal.priority,
                    "completed": goal.completed,
                    "progress": goal.progress
                } for goal in self.goals
            ],
            "experience_count": self.experience_count,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        """Create agent from dictionary"""
        agent = cls()

        # Basic properties
        agent.agent_id = data.get("agent_id", agent.agent_id)
        agent.name = data.get("name", agent.name)
        agent.agent_type = data.get("agent_type", agent.agent_type)

        # Position and orientation
        if "position" in data:
            agent.position = Position(**data["position"])
        if "orientation" in data:
            agent.orientation = Orientation(**data["orientation"])
        if "velocity" in data:
            agent.velocity = np.array(data["velocity"])

        # Status and capabilities
        if "status" in data:
            agent.status = AgentStatus(data["status"])
        if "capabilities" in data:
            agent.capabilities = {AgentCapability(cap) for cap in data["capabilities"]}

        # Personality
        if "personality" in data:
            agent.personality = AgentPersonality(**data["personality"])

        # Resources
        if "resources" in data:
            agent.resources = AgentResources(**data["resources"])

        # Goals
        if "goals" in data:
            for goal_data in data["goals"]:
                goal = AgentGoal(
                    goal_id=goal_data["goal_id"],
                    description=goal_data["description"],
                    priority=goal_data["priority"],
                    completed=goal_data["completed"],
                    progress=goal_data["progress"]
                )
                agent.goals.append(goal)

        # Metadata
        agent.experience_count = data.get("experience_count", 0)
        if "created_at" in data:
            agent.created_at = datetime.fromisoformat(data["created_at"])
        if "last_updated" in data:
            agent.last_updated = datetime.fromisoformat(data["last_updated"])
        agent.metadata = data.get("metadata", {})

        return agent


# Extension classes for specialized agent types
@dataclass
class SpecializedAgent(Agent):
    """Base class for specialized agent types"""
    specialization: str = "none"
    specialized_capabilities: Set[str] = field(default_factory=set)

    def has_specialized_capability(self, capability: str) -> bool:
        """Check for specialized capabilities"""
        return capability in self.specialized_capabilities


@dataclass
class ResourceAgent(SpecializedAgent):
    """Agent specialized in resource management"""
    specialization: str = "resource_management"

    # Resource-specific properties
    managed_resources: Dict[str, float] = field(default_factory=dict)
    resource_efficiency: float = 1.0
    trading_history: List[Dict[str, Any]] = field(default_factory=list)

    def __post_init__(self):
        """Initialize resource agent with specific capabilities"""
        self.add_capability(AgentCapability.RESOURCE_MANAGEMENT)
        self.specialized_capabilities.add("trading")
        self.specialized_capabilities.add("resource_optimization")


@dataclass
class SocialAgent(SpecializedAgent):
    """Agent specialized in social interactions"""
    specialization: str = "social_interaction"

    # Social-specific properties
    influence_radius: float = 10.0
    reputation: float = 0.5  # 0.0 to 1.0
    communication_style: str = "neutral"  # neutral, aggressive, passive, assertive
    social_network_size: int = 0

    def __post_init__(self):
        """Initialize social agent with enhanced social capabilities"""
        self.add_capability(AgentCapability.SOCIAL_INTERACTION)
        self.specialized_capabilities.add("negotiation")
        self.specialized_capabilities.add("coalition_formation")
        self.specialized_capabilities.add("influence")
