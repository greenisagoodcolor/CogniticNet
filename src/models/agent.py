"""
Agent Models - Enhanced for CogniticNet with GNN compatibility
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum


class Position(BaseModel):
    """Grid position model"""
    x: int = Field(..., ge=0, description="X coordinate")
    y: int = Field(..., ge=0, description="Y coordinate")


class KnowledgeEntry(BaseModel):
    """Knowledge entry for agent's memory"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tags: List[str] = Field(default_factory=list)


class AgentToolPermissions(BaseModel):
    """Tool permissions for agent capabilities"""
    # Information Access Tools
    internet_search: bool = False
    web_scraping: bool = False
    wikipedia_access: bool = False
    news_api: bool = False
    academic_search: bool = False
    document_retrieval: bool = False
    
    # Content Generation & Processing
    image_generation: bool = False
    text_summarization: bool = False
    translation: bool = False
    code_execution: bool = False
    
    # Knowledge & Reasoning Tools
    calculator: bool = False
    knowledge_graph_query: bool = False
    fact_checking: bool = False
    timeline_generator: bool = False
    
    # External Integrations
    weather_data: bool = False
    map_location_data: bool = False
    financial_data: bool = False
    public_datasets: bool = False
    
    # Agent-Specific Tools
    memory_search: bool = True
    cross_agent_knowledge: bool = True
    conversation_analysis: bool = True


class AgentBase(BaseModel):
    """Base agent model with all core properties"""
    name: str = Field(..., min_length=1, max_length=100)
    biography: str = Field(default="", description="Agent's background story")
    energy: int = Field(default=100, ge=0, le=100)
    resources: int = Field(default=10, ge=0)
    position: Position = Field(default_factory=lambda: Position(x=0, y=0))
    location: Optional[str] = Field(None, description="H3 cell index for geospatial location")
    color: str = Field(default="#0000FF", pattern="^#[0-9A-Fa-f]{6}$")
    in_conversation: bool = Field(default=False)
    autonomy_enabled: bool = Field(default=False)
    knowledge: List[KnowledgeEntry] = Field(default_factory=list)
    tool_permissions: AgentToolPermissions = Field(default_factory=AgentToolPermissions)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('location')
    def validate_h3_index(cls, v):
        """Validate H3 index format if provided"""
        if v is not None:
            # Basic H3 validation - should be a hex string of appropriate length
            # H3 indexes are typically 15 characters for resolution 9
            if not (8 <= len(v) <= 16) or not all(c in '0123456789abcdef' for c in v.lower()):
                raise ValueError("Invalid H3 cell index format")
        return v


class AgentCreate(BaseModel):
    """Model for creating a new agent - allows partial specification"""
    name: str = Field(..., min_length=1, max_length=100)
    biography: Optional[str] = None
    energy: Optional[int] = Field(default=100, ge=0, le=100)
    resources: Optional[int] = Field(default=10, ge=0)
    position: Optional[Position] = None
    location: Optional[str] = None
    color: Optional[str] = Field(default="#0000FF", pattern="^#[0-9A-Fa-f]{6}$")
    autonomy_enabled: Optional[bool] = False
    knowledge: Optional[List[KnowledgeEntry]] = None
    tool_permissions: Optional[AgentToolPermissions] = None
    metadata: Optional[Dict[str, Any]] = None


class AgentUpdate(BaseModel):
    """Model for updating an agent - all fields optional"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    biography: Optional[str] = None
    energy: Optional[int] = Field(None, ge=0, le=100)
    resources: Optional[int] = Field(None, ge=0)
    position: Optional[Position] = None
    location: Optional[str] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")
    in_conversation: Optional[bool] = None
    autonomy_enabled: Optional[bool] = None
    knowledge: Optional[List[KnowledgeEntry]] = None
    tool_permissions: Optional[AgentToolPermissions] = None
    metadata: Optional[Dict[str, Any]] = None


class Agent(AgentBase):
    """Complete agent model with ID and timestamps"""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat()
        }
    
    def to_gnn_format(self) -> Dict[str, Any]:
        """Convert agent to GNN-compatible format for future integration"""
        return {
            "id": str(self.id),
            "features": {
                "energy": self.energy / 100.0,  # Normalize to [0, 1]
                "resources": self.resources / 100.0,  # Normalize assuming max 100
                "autonomy": float(self.autonomy_enabled),
                "in_conversation": float(self.in_conversation),
                "knowledge_count": len(self.knowledge),
                "tool_permissions_count": sum(1 for v in self.tool_permissions.dict().values() if v)
            },
            "state": {
                "energy": self.energy,
                "resources": self.resources,
                "position": self.position.dict(),
                "in_conversation": self.in_conversation
            },
            "location": self.location or f"{self.position.x},{self.position.y}",  # Fallback to grid position
            "metadata": {
                "name": self.name,
                "color": self.color,
                "biography": self.biography,
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat()
            }
        }
    
    def to_frontend_format(self) -> Dict[str, Any]:
        """Convert to format compatible with frontend TypeScript interface"""
        return {
            "id": str(self.id),
            "name": self.name,
            "biography": self.biography,
            "inConversation": self.in_conversation,
            "position": self.position.dict(),
            "color": self.color,
            "knowledge": [k.dict() for k in self.knowledge],
            "autonomyEnabled": self.autonomy_enabled,
            "toolPermissions": {
                # Convert snake_case to camelCase for frontend
                "internetSearch": self.tool_permissions.internet_search,
                "webScraping": self.tool_permissions.web_scraping,
                "wikipediaAccess": self.tool_permissions.wikipedia_access,
                "newsApi": self.tool_permissions.news_api,
                "academicSearch": self.tool_permissions.academic_search,
                "documentRetrieval": self.tool_permissions.document_retrieval,
                "imageGeneration": self.tool_permissions.image_generation,
                "textSummarization": self.tool_permissions.text_summarization,
                "translation": self.tool_permissions.translation,
                "codeExecution": self.tool_permissions.code_execution,
                "calculator": self.tool_permissions.calculator,
                "knowledgeGraphQuery": self.tool_permissions.knowledge_graph_query,
                "factChecking": self.tool_permissions.fact_checking,
                "timelineGenerator": self.tool_permissions.timeline_generator,
                "weatherData": self.tool_permissions.weather_data,
                "mapLocationData": self.tool_permissions.map_location_data,
                "financialData": self.tool_permissions.financial_data,
                "publicDatasets": self.tool_permissions.public_datasets,
                "memorySearch": self.tool_permissions.memory_search,
                "crossAgentKnowledge": self.tool_permissions.cross_agent_knowledge,
                "conversationAnalysis": self.tool_permissions.conversation_analysis
            }
        }


# Response models for API
class AgentResponse(BaseModel):
    """Agent response model for API"""
    id: str
    name: str
    biography: str
    energy: int
    resources: int
    position: Position
    location: Optional[str]
    color: str
    in_conversation: bool
    autonomy_enabled: bool
    knowledge_count: int
    created_at: str
    updated_at: str
    
    @classmethod
    def from_agent(cls, agent: Agent) -> "AgentResponse":
        """Create response from Agent model"""
        return cls(
            id=str(agent.id),
            name=agent.name,
            biography=agent.biography,
            energy=agent.energy,
            resources=agent.resources,
            position=agent.position,
            location=agent.location,
            color=agent.color,
            in_conversation=agent.in_conversation,
            autonomy_enabled=agent.autonomy_enabled,
            knowledge_count=len(agent.knowledge),
            created_at=agent.created_at.isoformat(),
            updated_at=agent.updated_at.isoformat()
        ) 