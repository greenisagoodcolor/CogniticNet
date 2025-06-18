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
]

__version__ = "0.1.0"
