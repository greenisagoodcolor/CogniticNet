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

from .decision_making import (
    DecisionSystem,
    DecisionMaker,
    DecisionStrategy,
    DecisionContext,
    ActionType,
    Action,
    ActionGenerator,
    UtilityFunction,
    SafetyUtility,
    GoalUtility,
    ResourceUtility,
    SocialUtility,
    BehaviorTree,
    BehaviorNode,
    SequenceNode,
    SelectorNode,
    ConditionNode,
    ActionNode,
)

from .memory import (
    MemorySystem,
    Memory,
    MemoryType,
    MemoryImportance,
    Experience,
    Pattern,
    WorkingMemory,
    MemoryConsolidator,
    ReinforcementLearner,
    PatternRecognizer,
    InMemoryStorage,
    MemoryStorage,
)

from .interaction import (
    InteractionType,
    MessageType,
    ResourceType,
    Message,
    InteractionRequest,
    InteractionResult,
    ResourceExchange,
    CommunicationProtocol,
    ResourceManager,
    ConflictResolver,
    InteractionSystem,
)

from .persistence import (
    AgentPersistence,
    AgentSnapshot,
    AGENT_SCHEMA_VERSION
)

from .active_inference_integration import (
    IntegrationMode,
    ActiveInferenceConfig,
    StateToBeliefMapper,
    PerceptionToObservationMapper,
    ActionMapper,
    ActiveInferenceIntegration,
    create_active_inference_agent
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

    # Decision-making system
    "DecisionSystem",
    "DecisionMaker",
    "DecisionStrategy",
    "DecisionContext",
    "ActionType",
    "Action",
    "ActionGenerator",
    "UtilityFunction",
    "SafetyUtility",
    "GoalUtility",
    "ResourceUtility",
    "SocialUtility",
    "BehaviorTree",
    "BehaviorNode",
    "SequenceNode",
    "SelectorNode",
    "ConditionNode",
    "ActionNode",

    # Memory system
    "MemorySystem",
    "Memory",
    "MemoryType",
    "MemoryImportance",
    "Experience",
    "Pattern",
    "WorkingMemory",
    "MemoryConsolidator",
    "ReinforcementLearner",
    "PatternRecognizer",
    "InMemoryStorage",
    "MemoryStorage",

    # Interaction
    "InteractionType",
    "MessageType",
    "ResourceType",
    "Message",
    "InteractionRequest",
    "InteractionResult",
    "ResourceExchange",
    "CommunicationProtocol",
    "ResourceManager",
    "ConflictResolver",
    "InteractionSystem",

    # Persistence
    "AgentPersistence",
    "AgentSnapshot",
    "AGENT_SCHEMA_VERSION",

    # Active Inference Integration
    "IntegrationMode",
    "ActiveInferenceConfig",
    "StateToBeliefMapper",
    "PerceptionToObservationMapper",
    "ActionMapper",
    "ActiveInferenceIntegration",
    "create_active_inference_agent"
]

__version__ = "0.1.0"
