"""
Basic Agent System for FreeAgentics

This module provides the foundational agent system with:
- Agent data models and state management
- Movement mechanics and pathfinding
- Perception and decision-making
- Memory and learning capabilities
- Integration with Active Inference Engine
"""
from .data_model import Agent, Position, Orientation, AgentStatus, AgentCapability, PersonalityTraits, AgentPersonality, AgentResources, SocialRelationship, AgentGoal, SpecializedAgent, ResourceAgent, SocialAgent
from .state_manager import AgentStateManager, StateTransitionValidator, StateTransitionError, StateEvent, StateEventType, StateObserver, LoggingObserver, AsyncStateObserver, StateSnapshot, StateCondition, StateMonitor
from .movement import MovementController, MovementConstraints, MovementState, MovementMode, TerrainType, CollisionSystem, PathfindingGrid, SteeringBehaviors
from .perception import PerceptionSystem, PerceptionCapabilities, PerceptionType, PerceptionMemory, PerceptionFilter, ImportanceFilter, AttentionFilter, Stimulus, StimulusType, Percept, SensorSystem, VisualSensor, AuditorySensor, ProximitySensor
from .decision_making import DecisionSystem, DecisionMaker, DecisionStrategy, DecisionContext, ActionType, Action, ActionGenerator, UtilityFunction, SafetyUtility, GoalUtility, ResourceUtility, SocialUtility, BehaviorTree, BehaviorNode, SequenceNode, SelectorNode, ConditionNode, ActionNode
from .memory import MemorySystem, Memory, MemoryType, MemoryImportance, Experience, Pattern, WorkingMemory, MemoryConsolidator, ReinforcementLearner, PatternRecognizer, InMemoryStorage, MemoryStorage
from .interaction import InteractionType, MessageType, ResourceType, Message, InteractionRequest, InteractionResult, ResourceExchange, CommunicationProtocol, ResourceManager, ConflictResolver, InteractionSystem
from .persistence import AgentPersistence, AgentSnapshot, AGENT_SCHEMA_VERSION
from .active_inference_integration import IntegrationMode, ActiveInferenceConfig, StateToBeliefMapper, PerceptionToObservationMapper, ActionMapper, ActiveInferenceIntegration, create_active_inference_agent

# New components
from .interfaces import (
    IAgentComponent, IAgentLifecycle, IAgentBehavior, IBehaviorTree, IAgentFactory,
    IAgentRegistry, ICommunicationProtocol, IWorldInterface, IActiveInferenceInterface,
    IAgentEventHandler, IAgentPlugin, IConfigurationProvider, IAgentExtension, IAgentLogger
)
from .agent import BaseAgent, AgentLogger, create_agent
from .behaviors import (
    BehaviorPriority, BehaviorStatus, BaseBehavior, IdleBehavior, WanderBehavior,
    GoalSeekingBehavior, SocialInteractionBehavior, ExplorationBehavior,
    BehaviorTreeManager, create_behavior_tree
)
from .agent_factory import (
    AgentFactory, AgentRegistry, get_default_factory, get_default_registry,
    create_and_register_agent, quick_agent_setup
)

__all__ = [
    # Data models
    'Agent', 'Position', 'Orientation', 'AgentStatus', 'AgentCapability', 'PersonalityTraits',
    'AgentPersonality', 'AgentResources', 'SocialRelationship', 'AgentGoal', 'SpecializedAgent',
    'ResourceAgent', 'SocialAgent',

    # State management
    'AgentStateManager', 'StateTransitionValidator', 'StateTransitionError', 'StateEvent',
    'StateEventType', 'StateObserver', 'LoggingObserver', 'AsyncStateObserver', 'StateSnapshot',
    'StateCondition', 'StateMonitor',

    # Movement
    'MovementController', 'MovementConstraints', 'MovementState', 'MovementMode', 'TerrainType',
    'CollisionSystem', 'PathfindingGrid', 'SteeringBehaviors',

    # Perception
    'PerceptionSystem', 'PerceptionCapabilities', 'PerceptionType', 'PerceptionMemory',
    'PerceptionFilter', 'ImportanceFilter', 'AttentionFilter', 'Stimulus', 'StimulusType',
    'Percept', 'SensorSystem', 'VisualSensor', 'AuditorySensor', 'ProximitySensor',

    # Decision making
    'DecisionSystem', 'DecisionMaker', 'DecisionStrategy', 'DecisionContext', 'ActionType',
    'Action', 'ActionGenerator', 'UtilityFunction', 'SafetyUtility', 'GoalUtility',
    'ResourceUtility', 'SocialUtility', 'BehaviorTree', 'BehaviorNode', 'SequenceNode',
    'SelectorNode', 'ConditionNode', 'ActionNode',

    # Memory
    'MemorySystem', 'Memory', 'MemoryType', 'MemoryImportance', 'Experience', 'Pattern',
    'WorkingMemory', 'MemoryConsolidator', 'ReinforcementLearner', 'PatternRecognizer',
    'InMemoryStorage', 'MemoryStorage',

    # Interaction
    'InteractionType', 'MessageType', 'ResourceType', 'Message', 'InteractionRequest',
    'InteractionResult', 'ResourceExchange', 'CommunicationProtocol', 'ResourceManager',
    'ConflictResolver', 'InteractionSystem',

    # Persistence
    'AgentPersistence', 'AgentSnapshot', 'AGENT_SCHEMA_VERSION',

    # Active Inference integration
    'IntegrationMode', 'ActiveInferenceConfig', 'StateToBeliefMapper', 'PerceptionToObservationMapper',
    'ActionMapper', 'ActiveInferenceIntegration', 'create_active_inference_agent',

    # Interfaces
    'IAgentComponent', 'IAgentLifecycle', 'IAgentBehavior', 'IBehaviorTree', 'IAgentFactory',
    'IAgentRegistry', 'ICommunicationProtocol', 'IWorldInterface', 'IActiveInferenceInterface',
    'IAgentEventHandler', 'IAgentPlugin', 'IConfigurationProvider', 'IAgentExtension', 'IAgentLogger',

    # Main agent classes
    'BaseAgent', 'AgentLogger', 'create_agent',

    # Behaviors
    'BehaviorPriority', 'BehaviorStatus', 'BaseBehavior', 'IdleBehavior', 'WanderBehavior',
    'GoalSeekingBehavior', 'SocialInteractionBehavior', 'ExplorationBehavior',
    'BehaviorTreeManager', 'create_behavior_tree',

    # Factory and Registry
    'AgentFactory', 'AgentRegistry', 'get_default_factory', 'get_default_registry',
    'create_and_register_agent', 'quick_agent_setup'
]
__version__ = '0.1.0'
