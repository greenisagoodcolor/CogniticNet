"""
Validated Models using Pydantic
Comprehensive input validation and type safety for the entire system.
"""

from typing import Dict, List, Optional, Union, Any, Tuple
from pydantic import BaseModel, Field, validator, root_validator
from datetime import datetime
from enum import Enum
import re
from pathlib import Path


# Enums for constrained choices
class AgentClass(str, Enum):
    """Valid agent classes."""
    EXPLORER = "Explorer"
    MERCHANT = "Merchant"
    SCHOLAR = "Scholar"
    GUARDIAN = "Guardian"


class AgentStatus(str, Enum):
    """Valid agent statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LEARNING = "learning"
    RESTING = "resting"
    COMMUNICATING = "communicating"


class ResourceType(str, Enum):
    """Valid resource types in the world."""
    FOOD = "food"
    WATER = "water"
    ENERGY = "energy"
    KNOWLEDGE = "knowledge"
    MATERIALS = "materials"


class MessageType(str, Enum):
    """Valid message types for agent communication."""
    SHARE_DISCOVERY = "share_discovery"
    PROPOSE_TRADE = "propose_trade"
    FORM_ALLIANCE = "form_alliance"
    REQUEST_HELP = "request_help"
    SHARE_KNOWLEDGE = "share_knowledge"


# Base validators
def validate_name(name: str) -> str:
    """Validate agent/model names."""
    if not name:
        raise ValueError("Name cannot be empty")
    if len(name) > 100:
        raise ValueError("Name too long (max 100 characters)")
    if not re.match(r'^[a-zA-Z0-9_\- ]+$', name):
        raise ValueError("Name contains invalid characters")
    return name.strip()


def validate_hex_id(hex_id: str) -> str:
    """Validate H3 hexagon IDs."""
    if not hex_id:
        raise ValueError("Hex ID cannot be empty")
    # H3 IDs are 15 character hex strings
    if not re.match(r'^[0-9a-f]{15}$', hex_id.lower()):
        raise ValueError(f"Invalid H3 hex ID format: {hex_id}")
    return hex_id.lower()


def validate_file_path(path: str) -> str:
    """Validate file paths for GNN models."""
    if not path:
        return path  # Optional field
    p = Path(path)
    if not path.endswith('.gnn.md'):
        raise ValueError("GNN files must end with .gnn.md")
    return str(p)


# Personality model
class AgentPersonality(BaseModel):
    """Agent personality traits with validation."""
    exploration: float = Field(50.0, ge=0.0, le=100.0, description="Exploration drive (0-100)")
    cooperation: float = Field(50.0, ge=0.0, le=100.0, description="Cooperation tendency (0-100)")
    efficiency: float = Field(50.0, ge=0.0, le=100.0, description="Resource efficiency (0-100)")
    curiosity: float = Field(50.0, ge=0.0, le=100.0, description="Knowledge seeking (0-100)")
    risk_tolerance: float = Field(50.0, ge=0.0, le=100.0, description="Risk tolerance (0-100)")
    
    @validator('*')
    def validate_percentage(cls, v, field):
        """Ensure all personality values are valid percentages."""
        if not 0 <= v <= 100:
            raise ValueError(f"{field.name} must be between 0 and 100")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "exploration": 80.0,
                "cooperation": 60.0,
                "efficiency": 40.0,
                "curiosity": 90.0,
                "risk_tolerance": 70.0
            }
        }


# Agent position
class Position(BaseModel):
    """Agent position in the hexagonal world."""
    hex_id: str = Field(..., description="H3 hexagon ID")
    resolution: int = Field(8, ge=0, le=15, description="H3 resolution (0-15)")
    
    _validate_hex = validator('hex_id', allow_reuse=True)(validate_hex_id)
    
    @validator('resolution')
    def validate_resolution(cls, v):
        """Validate H3 resolution."""
        if not 0 <= v <= 15:
            raise ValueError("H3 resolution must be between 0 and 15")
        return v
    
    def neighbors(self, k: int = 1) -> List[str]:
        """Get neighboring hex IDs (placeholder - would use h3 library)."""
        # In real implementation, use h3.k_ring(self.hex_id, k)
        return [f"neighbor_{i}" for i in range(6 * k)]


# Resource model
class Resource(BaseModel):
    """Resource in the world."""
    type: ResourceType
    amount: float = Field(..., ge=0.0, description="Resource amount")
    position: Position
    regeneration_rate: float = Field(0.0, ge=0.0, le=1.0, description="Regeneration rate per step")
    
    @validator('amount')
    def validate_amount(cls, v):
        """Ensure amount is non-negative."""
        if v < 0:
            raise ValueError("Resource amount cannot be negative")
        return v


# Agent knowledge
class Experience(BaseModel):
    """Single experience in agent's knowledge graph."""
    id: str = Field(..., description="Unique experience ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Position
    observation: Dict[str, Any] = Field(..., description="What was observed")
    action: Dict[str, Any] = Field(..., description="Action taken")
    outcome: Dict[str, Any] = Field(..., description="Result of action")
    free_energy: float = Field(..., description="Free energy at this step")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="Confidence in this experience")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Ensure confidence is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Confidence must be between 0 and 1")
        return v


class Pattern(BaseModel):
    """Learned pattern from experiences."""
    id: str = Field(..., description="Pattern ID")
    name: str = Field(..., description="Pattern name")
    trigger_conditions: Dict[str, Any] = Field(..., description="When to apply pattern")
    action_sequence: List[Dict[str, Any]] = Field(..., description="Actions to take")
    expected_outcome: Dict[str, Any] = Field(..., description="Expected result")
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    occurrence_count: int = Field(0, ge=0)
    success_rate: float = Field(0.0, ge=0.0, le=1.0)
    
    _validate_name = validator('name', allow_reuse=True)(validate_name)
    
    @root_validator
    def validate_pattern(cls, values):
        """Validate pattern consistency."""
        if values.get('success_rate', 0) > 0 and values.get('occurrence_count', 0) == 0:
            raise ValueError("Cannot have success rate without occurrences")
        return values


# Communication models
class Message(BaseModel):
    """Message between agents."""
    id: str = Field(..., description="Message ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_id: str = Field(..., description="Sender agent ID")
    recipient_id: str = Field(..., description="Recipient agent ID")
    type: MessageType
    content: str = Field(..., max_length=1000, description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('content')
    def validate_content(cls, v):
        """Validate message content."""
        if not v or not v.strip():
            raise ValueError("Message content cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message too long (max 1000 characters)")
        return v.strip()


# Main Agent model
class ValidatedAgent(BaseModel):
    """Fully validated agent model."""
    id: str = Field(..., description="Unique agent ID")
    name: str = Field(..., description="Agent name")
    agent_class: AgentClass
    personality: AgentPersonality
    position: Position
    energy: float = Field(100.0, ge=0.0, le=100.0, description="Current energy (0-100)")
    status: AgentStatus = Field(AgentStatus.ACTIVE)
    
    # Resources and knowledge
    resources: Dict[ResourceType, float] = Field(default_factory=dict)
    knowledge_graph: List[Experience] = Field(default_factory=list)
    learned_patterns: List[Pattern] = Field(default_factory=list)
    
    # Social connections
    social_bonds: Dict[str, float] = Field(
        default_factory=dict,
        description="Agent ID -> bond strength (0-1)"
    )
    message_history: List[Message] = Field(default_factory=list)
    
    # GNN model
    gnn_model_path: Optional[str] = Field(None, description="Path to GNN model file")
    gnn_model_version: int = Field(1, ge=1, description="GNN model version")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_action_at: Optional[datetime] = None
    total_steps: int = Field(0, ge=0)
    
    _validate_name = validator('name', allow_reuse=True)(validate_name)
    _validate_gnn_path = validator('gnn_model_path', allow_reuse=True)(validate_file_path)
    
    @validator('energy')
    def validate_energy(cls, v):
        """Ensure energy is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Energy must be between 0 and 100")
        return v
    
    @validator('resources')
    def validate_resources(cls, v):
        """Ensure all resource amounts are non-negative."""
        for resource_type, amount in v.items():
            if amount < 0:
                raise ValueError(f"Resource {resource_type} cannot be negative")
        return v
    
    @validator('social_bonds')
    def validate_social_bonds(cls, v):
        """Ensure bond strengths are between 0 and 1."""
        for agent_id, bond_strength in v.items():
            if not 0 <= bond_strength <= 1:
                raise ValueError(f"Bond strength with {agent_id} must be between 0 and 1")
        return v
    
    @root_validator
    def validate_agent_consistency(cls, values):
        """Validate overall agent consistency."""
        # Check if inactive agents have zero energy
        if values.get('status') == AgentStatus.INACTIVE and values.get('energy', 0) > 0:
            values['energy'] = 0.0
            
        # Validate knowledge graph size
        knowledge = values.get('knowledge_graph', [])
        if len(knowledge) > 10000:
            raise ValueError("Knowledge graph too large (max 10000 experiences)")
            
        return values
    
    def can_act(self) -> bool:
        """Check if agent can perform actions."""
        return self.status == AgentStatus.ACTIVE and self.energy > 0
    
    def add_experience(self, experience: Experience) -> None:
        """Add new experience to knowledge graph."""
        self.knowledge_graph.append(experience)
        self.total_steps += 1
        self.last_action_at = experience.timestamp
    
    class Config:
        schema_extra = {
            "example": {
                "id": "agent_001",
                "name": "Explorer Alpha",
                "agent_class": "Explorer",
                "personality": {
                    "exploration": 80.0,
                    "cooperation": 60.0,
                    "efficiency": 40.0,
                    "curiosity": 90.0,
                    "risk_tolerance": 70.0
                },
                "position": {
                    "hex_id": "8a283082a677fff",
                    "resolution": 8
                },
                "energy": 85.5,
                "status": "active"
            }
        }


# Simulation models
class WorldConfig(BaseModel):
    """Configuration for the hexagonal world."""
    size: int = Field(100, ge=10, le=1000, description="World size (number of hexes)")
    resolution: int = Field(8, ge=0, le=15, description="H3 resolution")
    resource_density: float = Field(0.1, ge=0.0, le=1.0, description="Resource initialize density")
    regeneration_rate: float = Field(0.01, ge=0.0, le=1.0, description="Resource regeneration")
    
    @validator('size')
    def validate_size(cls, v):
        """Ensure world size is reasonable."""
        if v < 10:
            raise ValueError("World too small (min 10 hexes)")
        if v > 1000:
            raise ValueError("World too large (max 1000 hexes)")
        return v


class SimulationStep(BaseModel):
    """Single simulation step with validation."""
    step_number: int = Field(..., ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    active_agents: List[str] = Field(..., description="IDs of agents that acted")
    events: List[Dict[str, Any]] = Field(default_factory=list)
    total_free_energy: float = Field(..., description="Sum of all agent free energies")
    resource_changes: Dict[str, float] = Field(default_factory=dict)
    
    @validator('active_agents')
    def validate_agents(cls, v):
        """Ensure agent list is not empty in active simulation."""
        if len(v) == 0:
            raise ValueError("No active agents in simulation step")
        return v


class SimulationState(BaseModel):
    """Complete simulation state with validation."""
    id: str = Field(..., description="Simulation ID")
    world_config: WorldConfig
    agents: List[ValidatedAgent]
    resources: List[Resource]
    current_step: int = Field(0, ge=0)
    history: List[SimulationStep] = Field(default_factory=list)
    is_running: bool = Field(False)
    
    @validator('agents')
    def validate_unique_agents(cls, v):
        """Ensure all agent IDs are unique."""
        agent_ids = [agent.id for agent in v]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("Duplicate agent IDs found")
        return v
    
    @root_validator
    def validate_simulation(cls, values):
        """Validate simulation consistency."""
        agents = values.get('agents', [])
        world_config = values.get('world_config')
        
        if world_config and len(agents) > world_config.size:
            raise ValueError("Too many agents for world size")
            
        return values


# Export all models
__all__ = [
    'AgentClass',
    'AgentStatus', 
    'ResourceType',
    'MessageType',
    'AgentPersonality',
    'Position',
    'Resource',
    'Experience',
    'Pattern',
    'Message',
    'ValidatedAgent',
    'WorldConfig',
    'SimulationStep',
    'SimulationState'
] 