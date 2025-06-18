"""
Basic Agent System for CogniticNet

This module provides the foundational agent system with:
- Agent data models and state management
- Movement mechanics and pathfinding
- Perception and decision-making
- Memory and learning capabilities
- Integration with Active Inference Engine
"""

from .data_model import (
    # Core classes
    Agent,
    Position,
    Orientation,

    # Enums
    AgentStatus,
    AgentCapability,
    PersonalityTraits,

    # Component classes
    AgentPersonality,
    AgentResources,
    SocialRelationship,
    AgentGoal,

    # Specialized agents
    SpecializedAgent,
    ResourceAgent,
    SocialAgent,
)

from .state_manager import (
    AgentStateManager,
    StateTransitionValidator,
    StateTransitionError,
    StateEvent,
    StateEventType,
    StateObserver,
    LoggingObserver,
    AsyncStateObserver,
    StateSnapshot,
    StateCondition,
    StateMonitor,
)

from .movement import (
    MovementController,
    MovementConstraints,
    MovementState,
    MovementMode,
    TerrainType,
    CollisionSystem,
    PathfindingGrid,
    SteeringBehaviors,
)

from .perception import (
    PerceptionSystem,
    PerceptionCapabilities,
    PerceptionType,
    PerceptionMemory,
    PerceptionFilter,
    ImportanceFilter,
    AttentionFilter,
    Stimulus,
    StimulusType,
    Percept,
    SensorSystem,
    VisualSensor,
    AuditorySensor,
    ProximitySensor,
)

__all__ = [
    # Core classes
    "Agent",
    "Position",
    "Orientation",

    # Enums
    "AgentStatus",
    "AgentCapability",
    "PersonalityTraits",

    # Component classes
    "AgentPersonality",
    "AgentResources",
    "SocialRelationship",
    "AgentGoal",

    # Specialized agents
    "SpecializedAgent",
    "ResourceAgent",
    "SocialAgent",

    # State management
    "AgentStateManager",
    "StateTransitionValidator",
    "StateTransitionError",
    "StateEvent",
    "StateEventType",
    "StateObserver",
    "LoggingObserver",
    "AsyncStateObserver",
    "StateSnapshot",
    "StateCondition",
    "StateMonitor",

    # Movement system
    "MovementController",
    "MovementConstraints",
    "MovementState",
    "MovementMode",
    "TerrainType",
    "CollisionSystem",
    "PathfindingGrid",
    "SteeringBehaviors",

    # Perception system
    "PerceptionSystem",
    "PerceptionCapabilities",
    "PerceptionType",
    "PerceptionMemory",
    "PerceptionFilter",
    "ImportanceFilter",
    "AttentionFilter",
    "Stimulus",
    "StimulusType",
    "Percept",
    "SensorSystem",
    "VisualSensor",
    "AuditorySensor",
    "ProximitySensor",
]

__version__ = "0.1.0"
