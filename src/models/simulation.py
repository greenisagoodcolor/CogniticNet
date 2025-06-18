"""
Simulation Models
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class SimulationState(str, Enum):
    """Simulation state enumeration"""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"

class SimulationConfig(BaseModel):
    """Simulation configuration model"""
    tick_interval: float = Field(default=1.0, gt=0, description="Time between ticks in seconds")
    grid_width: int = Field(default=20, ge=10, le=100)
    grid_height: int = Field(default=20, ge=10, le=100)
    max_agents: int = Field(default=50, ge=1, le=200)
    energy_decay_rate: float = Field(default=1.0, ge=0, le=10)
    resource_initialize_rate: float = Field(default=0.1, ge=0, le=1)

class SimulationStatus(BaseModel):
    """Current simulation status"""
    state: SimulationState
    tick: int = Field(ge=0)
    agent_count: int = Field(ge=0)
    total_resources: int = Field(ge=0)
    start_time: Optional[datetime] = None
    elapsed_time: float = Field(default=0.0, ge=0)
    config: SimulationConfig

class SimulationMetrics(BaseModel):
    """Simulation metrics and statistics"""
    total_ticks: int = Field(ge=0)
    total_agents_created: int = Field(ge=0)
    total_interactions: int = Field(ge=0)
    average_agent_lifespan: float = Field(ge=0)
    resource_efficiency: float = Field(ge=0, le=1)

class SimulationSnapshot(BaseModel):
    """Complete simulation state snapshot"""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: SimulationStatus
    metrics: SimulationMetrics
    grid_state: List[List[Any]] = Field(default_factory=list)
    agent_positions: Dict[str, Dict[str, int]] = Field(default_factory=dict) 