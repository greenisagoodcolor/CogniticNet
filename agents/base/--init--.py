"""
Basic Agent System for FreeAgentics

This module provides the foundational agent system with:
- Agent data models and state management
- Movement mechanics and pathfinding
- Perception and decision-making
- Memory and learning capabilities
- Integration with Active Inference Engine
"""
from .data-model import Agent, Position, Orientation, AgentStatus, AgentCapability, PersonalityTraits, AgentPersonality, AgentResources, SocialRelationship, AgentGoal, SpecializedAgent, ResourceAgent, SocialAgent
from .state-manager import AgentStateManager, StateTransitionValidator, StateTransitionError, StateEvent, StateEventType, StateObserver, LoggingObserver, AsyncStateObserver, StateSnapshot, StateCondition, StateMonitor
from .movement import MovementController, MovementConstraints, MovementState, MovementMode, TerrainType, CollisionSystem, PathfindingGrid, SteeringBehaviors
from .perception import PerceptionSystem, PerceptionCapabilities, PerceptionType, PerceptionMemory, PerceptionFilter, ImportanceFilter, AttentionFilter, Stimulus, StimulusType, Percept, SensorSystem, VisualSensor, AuditorySensor, ProximitySensor
from .decision-making import DecisionSystem, DecisionMaker, DecisionStrategy, DecisionContext, ActionType, Action, ActionGenerator, UtilityFunction, SafetyUtility, GoalUtility, ResourceUtility, SocialUtility, BehaviorTree, BehaviorNode, SequenceNode, SelectorNode, ConditionNode, ActionNode
from .memory import MemorySystem, Memory, MemoryType, MemoryImportance, Experience, Pattern, WorkingMemory, MemoryConsolidator, ReinforcementLearner, PatternRecognizer, InMemoryStorage, MemoryStorage
from .interaction import InteractionType, MessageType, ResourceType, Message, InteractionRequest, InteractionResult, ResourceExchange, CommunicationProtocol, ResourceManager, ConflictResolver, InteractionSystem
from .persistence import AgentPersistence, AgentSnapshot, AGENT_SCHEMA_VERSION
from .active-inference-integration import IntegrationMode, ActiveInferenceConfig, StateToBeliefMapper, PerceptionToObservationMapper, ActionMapper, ActiveInferenceIntegration, create_active_inference_agent
__all__ = ['Agent', 'Position', 'Orientation', 'AgentStatus', 'AgentCapability', 'PersonalityTraits', 'AgentPersonality', 'AgentResources', 'SocialRelationship', 'AgentGoal', 'SpecializedAgent', 'ResourceAgent', 'SocialAgent', 'AgentStateManager', 'StateTransitionValidator', 'StateTransitionError', 'StateEvent', 'StateEventType', 'StateObserver', 'LoggingObserver', 'AsyncStateObserver', 'StateSnapshot', 'StateCondition', 'StateMonitor', 'MovementController', 'MovementConstraints', 'MovementState', 'MovementMode', 'TerrainType', 'CollisionSystem', 'PathfindingGrid', 'SteeringBehaviors', 'PerceptionSystem', 'PerceptionCapabilities', 'PerceptionType', 'PerceptionMemory', 'PerceptionFilter', 'ImportanceFilter', 'AttentionFilter', 'Stimulus', 'StimulusType', 'Percept', 'SensorSystem', 'VisualSensor', 'AuditorySensor', 'ProximitySensor', 'DecisionSystem', 'DecisionMaker', 'DecisionStrategy', 'DecisionContext', 'ActionType', 'Action', 'ActionGenerator', 'UtilityFunction', 'SafetyUtility', 'GoalUtility', 'ResourceUtility', 'SocialUtility', 'BehaviorTree', 'BehaviorNode', 'SequenceNode', 'SelectorNode', 'ConditionNode', 'ActionNode', 'MemorySystem', 'Memory', 'MemoryType', 'MemoryImportance', 'Experience', 'Pattern', 'WorkingMemory', 'MemoryConsolidator', 'ReinforcementLearner', 'PatternRecognizer', 'InMemoryStorage', 'MemoryStorage', 'InteractionType', 'MessageType', 'ResourceType', 'Message', 'InteractionRequest', 'InteractionResult', 'ResourceExchange', 'CommunicationProtocol', 'ResourceManager', 'ConflictResolver', 'InteractionSystem', 'AgentPersistence', 'AgentSnapshot', 'AGENT_SCHEMA_VERSION', 'IntegrationMode', 'ActiveInferenceConfig', 'StateToBeliefMapper', 'PerceptionToObservationMapper', 'ActionMapper', 'ActiveInferenceIntegration', 'create_active_inference_agent']
__version__ = '0.1.0'
