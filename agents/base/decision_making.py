"""
Agent Decision-Making Framework

This module provides decision-making capabilities for agents including:
- Utility-based decision making
- Goal prioritization and planning
- Action selection mechanisms
- Integration with Active Inference Engine
- Behavioral patterns and strategies
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import math
from collections import defaultdict
import heapq

from .data_model import Agent, AgentGoal, AgentStatus, Position, AgentCapability
from .state_manager import AgentStateManager
from .perception import Percept, PerceptionSystem, StimulusType
from .movement import MovementController

# Import Active Inference components if available
try:
    from ...agents.active_inference import (
        create_generative_model,
        create_policy_selector,
        DiscreteGenerativeModel,
        DiscreteExpectedFreeEnergy
    )
    ACTIVE_INFERENCE_AVAILABLE = True
except ImportError:
    ACTIVE_INFERENCE_AVAILABLE = False


class ActionType(Enum):
    """Types of actions an agent can take"""
    MOVE = "move"
    INTERACT = "interact"
    COMMUNICATE = "communicate"
    WAIT = "wait"
    EXPLORE = "explore"
    FLEE = "flee"
    APPROACH = "approach"
    GATHER = "gather"
    USE_ITEM = "use_item"


class DecisionStrategy(Enum):
    """Decision-making strategies"""
    UTILITY_BASED = "utility_based"
    GOAL_ORIENTED = "goal_oriented"
    REACTIVE = "reactive"
    DELIBERATIVE = "deliberative"
    ACTIVE_INFERENCE = "active_inference"
    HYBRID = "hybrid"


@dataclass
class Action:
    """Represents an action an agent can take"""
    action_type: ActionType
    target: Optional[Any] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    expected_utility: float = 0.0
    prerequisites: List[str] = field(default_factory=list)
    effects: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    duration: float = 1.0  # seconds

    def __hash__(self):
        """Make Action hashable for use in sets"""
        return hash((self.action_type, str(self.target), tuple(self.parameters.items())))


@dataclass
class DecisionContext:
    """Context for making decisions"""
    agent: Agent
    percepts: List[Percept]
    current_goal: Optional[AgentGoal]
    available_actions: List[Action]
    world_state: Dict[str, Any] = field(default_factory=dict)
    time_pressure: float = 0.0  # 0.0 to 1.0

    def get_perceived_threats(self) -> List[Percept]:
        """Get perceived threats from percepts"""
        return [p for p in self.percepts
                if p.stimulus.stimulus_type == StimulusType.DANGER]

    def get_perceived_agents(self) -> List[Percept]:
        """Get perceived agents from percepts"""
        return [p for p in self.percepts
                if p.stimulus.stimulus_type == StimulusType.AGENT]

    def get_perceived_resources(self) -> List[Percept]:
        """Get perceived resources from percepts"""
        return [p for p in self.percepts
                if p.stimulus.metadata.get("is_resource", False)]


class UtilityFunction:
    """Base class for utility functions"""

    def calculate(self, action: Action, context: DecisionContext) -> float:
        """Calculate utility of an action in given context"""
        raise NotImplementedError


class SafetyUtility(UtilityFunction):
    """Utility function for safety/survival"""

    def calculate(self, action: Action, context: DecisionContext) -> float:
        """Calculate safety utility"""
        utility = 0.0
        threats = context.get_perceived_threats()

        if not threats:
            return 0.0  # No threats, no safety concern

        # Fleeing from threats has high utility
        if action.action_type == ActionType.FLEE:
            utility += 10.0 * len(threats)

        # Moving away from threats
        if action.action_type == ActionType.MOVE and action.target:
            agent_pos = context.agent.position
            for threat in threats:
                threat_distance = agent_pos.distance_to(threat.stimulus.position)
                target_distance = action.target.distance_to(threat.stimulus.position)

                if target_distance > threat_distance:
                    utility += 5.0  # Moving away from threat
                else:
                    utility -= 5.0  # Moving towards threat

        # Waiting near threats is bad
        if action.action_type == ActionType.WAIT and threats:
            utility -= 3.0 * len(threats)

        return utility


class GoalUtility(UtilityFunction):
    """Utility function for goal achievement"""

    def calculate(self, action: Action, context: DecisionContext) -> float:
        """Calculate goal utility"""
        if not context.current_goal:
            return 0.0

        utility = 0.0
        goal = context.current_goal

        # Actions that directly contribute to goal
        if action.action_type == ActionType.MOVE and goal.target_position:
            # Moving towards goal position
            current_distance = context.agent.position.distance_to(goal.target_position)
            if action.target:
                new_distance = action.target.distance_to(goal.target_position)
                progress = current_distance - new_distance
                utility += progress * goal.priority * 2.0

        # Interacting with goal target
        if (action.action_type == ActionType.INTERACT and
            goal.target_agent_id and
            hasattr(action.target, "agent_id") and
            goal.target_agent_id == action.target.agent_id):
            utility += 10.0 * goal.priority

        # Goal-specific actions could be added via context.world_state
        # For now, just check if action helps with goal progress

        return utility


class ResourceUtility(UtilityFunction):
    """Utility function for resource management"""

    def calculate(self, action: Action, context: DecisionContext) -> float:
        """Calculate resource utility"""
        utility = 0.0
        agent = context.agent

        # Low energy makes resource gathering more valuable
        energy_ratio = agent.resources.energy / 100.0

        if action.action_type == ActionType.GATHER:
            # Gathering is more valuable when resources are low
            utility += (1.0 - energy_ratio) * 8.0

        # Moving towards resources when low
        if action.action_type == ActionType.MOVE and energy_ratio < 0.3:
            resources = context.get_perceived_resources()
            if resources and action.target:
                closest_resource = min(resources,
                    key=lambda r: r.distance)

                current_distance = context.agent.position.distance_to(
                    closest_resource.stimulus.position)
                new_distance = action.target.distance_to(
                    closest_resource.stimulus.position)

                if new_distance < current_distance:
                    utility += (1.0 - energy_ratio) * 5.0

        # Consider action cost
        if agent.resources.energy < action.cost * 2:
            utility -= 10.0  # Can't afford this action

        return utility


class SocialUtility(UtilityFunction):
    """Utility function for social interactions"""

    def calculate(self, action: Action, context: DecisionContext) -> float:
        """Calculate social utility"""
        utility = 0.0
        perceived_agents = context.get_perceived_agents()

        if not perceived_agents:
            return 0.0

        # Communication has value when agents are nearby
        if action.action_type == ActionType.COMMUNICATE:
            utility += len(perceived_agents) * 2.0

        # Approaching friendly agents
        if action.action_type == ActionType.APPROACH:
            for percept in perceived_agents:
                agent_id = percept.stimulus.metadata.get("agent_id")
                if agent_id:
                    relationship = context.agent.get_relationship(agent_id)
                    if relationship and relationship.trust_level > 0.6:
                        utility += 3.0

        # Interacting with agents based on relationship
        if action.action_type == ActionType.INTERACT and hasattr(action.target, "agent_id"):
            relationship = context.agent.get_relationship(action.target.agent_id)
            if relationship:
                utility += (relationship.trust_level - 0.5) * 10.0

        return utility


class DecisionMaker:
    """Base class for decision-making systems"""

    def __init__(self, strategy: DecisionStrategy = DecisionStrategy.UTILITY_BASED):
        self.strategy = strategy
        self.utility_functions: List[UtilityFunction] = [
            SafetyUtility(),
            GoalUtility(),
            ResourceUtility(),
            SocialUtility(),
        ]
        self.utility_weights: Dict[type, float] = {
            SafetyUtility: 2.0,
            GoalUtility: 1.5,
            ResourceUtility: 1.0,
            SocialUtility: 0.8,
        }

    def decide(self, context: DecisionContext) -> Optional[Action]:
        """Make a decision based on context"""
        if self.strategy == DecisionStrategy.UTILITY_BASED:
            return self._utility_based_decision(context)
        elif self.strategy == DecisionStrategy.GOAL_ORIENTED:
            return self._goal_oriented_decision(context)
        elif self.strategy == DecisionStrategy.REACTIVE:
            return self._reactive_decision(context)
        elif self.strategy == DecisionStrategy.ACTIVE_INFERENCE:
            return self._active_inference_decision(context)
        else:
            return self._hybrid_decision(context)

    def _utility_based_decision(self, context: DecisionContext) -> Optional[Action]:
        """Make decision based on utility maximization"""
        if not context.available_actions:
            return None

        best_action = None
        best_utility = float('-inf')

        for action in context.available_actions:
            total_utility = 0.0

            # Calculate weighted utility from all functions
            for utility_func in self.utility_functions:
                weight = self.utility_weights.get(type(utility_func), 1.0)
                utility = utility_func.calculate(action, context)
                total_utility += weight * utility

            # Apply time pressure factor
            if context.time_pressure > 0.5 and action.duration > 2.0:
                total_utility *= (1.0 - context.time_pressure * 0.5)

            # Store expected utility
            action.expected_utility = total_utility

            if total_utility > best_utility:
                best_utility = total_utility
                best_action = action

        return best_action

    def _goal_oriented_decision(self, context: DecisionContext) -> Optional[Action]:
        """Make decision focused on current goal"""
        if not context.current_goal or not context.available_actions:
            return self._utility_based_decision(context)

        # Filter actions that contribute to goal
        goal_actions = []
        for action in context.available_actions:
            utility = GoalUtility().calculate(action, context)
            if utility > 0:
                action.expected_utility = utility
                goal_actions.append(action)

        if not goal_actions:
            return self._utility_based_decision(context)

        # Choose action with highest goal utility
        return max(goal_actions, key=lambda a: a.expected_utility)

    def _reactive_decision(self, context: DecisionContext) -> Optional[Action]:
        """Make quick reactive decision based on immediate stimuli"""
        # Check for immediate threats
        threats = context.get_perceived_threats()
        if threats:
            # Find flee action
            flee_actions = [a for a in context.available_actions
                          if a.action_type == ActionType.FLEE]
            if flee_actions:
                return flee_actions[0]

        # Check for critical resources
        if context.agent.resources.energy < 20:
            gather_actions = [a for a in context.available_actions
                            if a.action_type == ActionType.GATHER]
            if gather_actions:
                return gather_actions[0]

        # Default to waiting
        wait_actions = [a for a in context.available_actions
                       if a.action_type == ActionType.WAIT]
        return wait_actions[0] if wait_actions else None

    def _active_inference_decision(self, context: DecisionContext) -> Optional[Action]:
        """Make decision using Active Inference if available"""
        if not ACTIVE_INFERENCE_AVAILABLE:
            return self._utility_based_decision(context)

        # Convert context to Active Inference format
        # This is a simplified integration
        num_states = 10  # Simplified state space
        num_observations = len(context.percepts) + 1
        num_actions = len(context.available_actions)

        if num_actions == 0:
            return None

        # Create simple generative model
        model = create_generative_model(
            model_type="discrete",
            num_states=num_states,
            num_observations=num_observations,
            num_actions=num_actions
        )

        # Create policy selector
        policy_selector = create_policy_selector(
            selector_type="discrete",
            generative_model=model,
            planning_horizon=3
        )

        # Convert current state to belief
        belief = np.ones(num_states) / num_states  # Uniform prior

        # Update belief based on percepts
        if context.percepts:
            # Simple mapping of percepts to observations
            observation_idx = min(len(context.percepts), num_observations - 1)
            # This would need proper belief updating in real implementation

        # Select action using Active Inference
        # In real implementation, this would use the policy selector
        action_idx = np.random.choice(num_actions)  # Placeholder

        return context.available_actions[action_idx]

    def _hybrid_decision(self, context: DecisionContext) -> Optional[Action]:
        """Combine multiple decision strategies"""
        # Start with utility-based decision
        utility_action = self._utility_based_decision(context)

        # Override with reactive if needed
        if context.time_pressure > 0.8 or context.get_perceived_threats():
            reactive_action = self._reactive_decision(context)
            if reactive_action:
                return reactive_action

        return utility_action


class BehaviorTree:
    """Simple behavior tree implementation for complex behaviors"""

    def __init__(self):
        self.root = None

    def execute(self, context: DecisionContext) -> Optional[Action]:
        """Execute the behavior tree"""
        if self.root:
            return self.root.execute(context)
        return None


class BehaviorNode:
    """Base class for behavior tree nodes"""

    def execute(self, context: DecisionContext) -> Optional[Action]:
        """Execute this node"""
        raise NotImplementedError


class SequenceNode(BehaviorNode):
    """Execute children in sequence until one fails"""

    def __init__(self, children: List[BehaviorNode]):
        self.children = children
        self.current_index = 0

    def execute(self, context: DecisionContext) -> Optional[Action]:
        """Execute children in sequence"""
        while self.current_index < len(self.children):
            result = self.children[self.current_index].execute(context)
            if result is None:
                return None  # Child failed
            self.current_index += 1
            if result.action_type != ActionType.WAIT:
                return result  # Return non-wait action

        self.current_index = 0  # Reset for next execution
        return None


class SelectorNode(BehaviorNode):
    """Execute children until one succeeds"""

    def __init__(self, children: List[BehaviorNode]):
        self.children = children

    def execute(self, context: DecisionContext) -> Optional[Action]:
        """Try each child until one succeeds"""
        for child in self.children:
            result = child.execute(context)
            if result is not None:
                return result
        return None


class ConditionNode(BehaviorNode):
    """Execute based on condition"""

    def __init__(self, condition: Callable[[DecisionContext], bool],
                 true_node: BehaviorNode, false_node: Optional[BehaviorNode] = None):
        self.condition = condition
        self.true_node = true_node
        self.false_node = false_node

    def execute(self, context: DecisionContext) -> Optional[Action]:
        """Execute based on condition result"""
        if self.condition(context):
            return self.true_node.execute(context)
        elif self.false_node:
            return self.false_node.execute(context)
        return None


class ActionNode(BehaviorNode):
    """Leaf node that returns an action"""

    def __init__(self, action_generator: Callable[[DecisionContext], Optional[Action]]):
        self.action_generator = action_generator

    def execute(self, context: DecisionContext) -> Optional[Action]:
        """Generate and return action"""
        return self.action_generator(context)


class ActionGenerator:
    """Generates available actions based on agent state and environment"""

    def __init__(self, movement_controller: Optional[MovementController] = None):
        self.movement_controller = movement_controller

    def generate_actions(self, agent: Agent, percepts: List[Percept]) -> List[Action]:
        """Generate all available actions for an agent"""
        actions = []

        # Always available actions
        actions.append(Action(ActionType.WAIT, cost=0.1))

        # Movement actions
        if agent.has_capability(AgentCapability.MOVEMENT):
            actions.extend(self._generate_movement_actions(agent, percepts))

        # Interaction actions
        if agent.has_capability(AgentCapability.SOCIAL_INTERACTION):
            actions.extend(self._generate_interaction_actions(agent, percepts))

        # Communication actions
        if agent.has_capability(AgentCapability.COMMUNICATION):
            actions.extend(self._generate_communication_actions(agent, percepts))

        # Resource actions
        if agent.has_capability(AgentCapability.RESOURCE_MANAGEMENT):
            actions.extend(self._generate_resource_actions(agent, percepts))

        return actions

    def _generate_movement_actions(self, agent: Agent, percepts: List[Percept]) -> List[Action]:
        """Generate movement-related actions"""
        actions = []

        # Explore action
        actions.append(Action(
            ActionType.EXPLORE,
            cost=agent.resources.energy * 0.05,
            duration=5.0
        ))

        # Move to perceived locations
        for percept in percepts[:5]:  # Limit to nearest 5
            move_action = Action(
                ActionType.MOVE,
                target=percept.stimulus.position,
                cost=percept.distance * 0.1,
                duration=percept.distance / 5.0  # Assuming speed of 5
            )
            actions.append(move_action)

        # Flee from threats
        threats = [p for p in percepts if p.stimulus.stimulus_type == StimulusType.DANGER]
        if threats:
            actions.append(Action(
                ActionType.FLEE,
                cost=agent.resources.energy * 0.1,
                duration=2.0,
                parameters={"urgency": "high"}
            ))

        return actions

    def _generate_interaction_actions(self, agent: Agent, percepts: List[Percept]) -> List[Action]:
        """Generate interaction actions"""
        actions = []

        # Interact with perceived agents
        agent_percepts = [p for p in percepts
                         if p.stimulus.stimulus_type == StimulusType.AGENT]

        for percept in agent_percepts[:3]:  # Limit interactions
            if percept.distance < 5.0:  # Close enough to interact
                actions.append(Action(
                    ActionType.INTERACT,
                    target=percept.stimulus.source,
                    cost=1.0,
                    duration=3.0
                ))

        # Approach interesting agents
        for percept in agent_percepts:
            if percept.distance > 5.0 and percept.distance < 20.0:
                actions.append(Action(
                    ActionType.APPROACH,
                    target=percept.stimulus.source,
                    cost=percept.distance * 0.05,
                    duration=percept.distance / 5.0
                ))

        return actions

    def _generate_communication_actions(self, agent: Agent, percepts: List[Percept]) -> List[Action]:
        """Generate communication actions"""
        actions = []

        # Communicate with nearby agents
        agent_percepts = [p for p in percepts
                         if p.stimulus.stimulus_type == StimulusType.AGENT
                         and p.distance < 10.0]

        if agent_percepts:
            actions.append(Action(
                ActionType.COMMUNICATE,
                cost=0.5,
                duration=1.0,
                parameters={"message_type": "greeting"}
            ))

        return actions

    def _generate_resource_actions(self, agent: Agent, percepts: List[Percept]) -> List[Action]:
        """Generate resource-related actions"""
        actions = []

        # Gather resources if any are perceived
        resource_percepts = [p for p in percepts
                           if p.stimulus.metadata.get("is_resource", False)]

        for percept in resource_percepts:
            if percept.distance < 2.0:  # Close enough to gather
                actions.append(Action(
                    ActionType.GATHER,
                    target=percept.stimulus,
                    cost=2.0,
                    duration=3.0,
                    effects={"energy": 20.0}
                ))

        return actions


class DecisionSystem:
    """Main decision-making system integrating all components"""

    def __init__(self, state_manager: AgentStateManager,
                 perception_system: PerceptionSystem,
                 movement_controller: MovementController):
        self.state_manager = state_manager
        self.perception_system = perception_system
        self.movement_controller = movement_controller
        self.action_generator = ActionGenerator(movement_controller)
        self.decision_makers: Dict[str, DecisionMaker] = {}
        self.behavior_trees: Dict[str, BehaviorTree] = {}
        self.decision_history: Dict[str, List[Tuple[DecisionContext, Action]]] = defaultdict(list)

    def register_agent(self, agent: Agent,
                      strategy: DecisionStrategy = DecisionStrategy.HYBRID) -> None:
        """Register an agent with the decision system"""
        self.decision_makers[agent.agent_id] = DecisionMaker(strategy)

        # Set up default behavior tree
        tree = self._create_default_behavior_tree()
        self.behavior_trees[agent.agent_id] = tree

    def make_decision(self, agent_id: str) -> Optional[Action]:
        """Make a decision for an agent"""
        agent = self.state_manager.get_agent(agent_id)
        if not agent:
            return None

        # Get current percepts
        percepts = self.perception_system.perceive(agent_id)

        # Generate available actions
        available_actions = self.action_generator.generate_actions(agent, percepts)

        # Create decision context
        context = DecisionContext(
            agent=agent,
            percepts=percepts,
            current_goal=agent.current_goal,
            available_actions=available_actions,
            time_pressure=self._calculate_time_pressure(agent)
        )

        # Make decision
        decision_maker = self.decision_makers.get(agent_id)
        if not decision_maker:
            return None

        action = decision_maker.decide(context)

        # Store in history
        if action:
            self.decision_history[agent_id].append((context, action))
            if len(self.decision_history[agent_id]) > 100:
                self.decision_history[agent_id] = self.decision_history[agent_id][-50:]

        return action

    def execute_action(self, agent_id: str, action: Action) -> bool:
        """Execute a decided action"""
        agent = self.state_manager.get_agent(agent_id)
        if not agent:
            return False

        # Check prerequisites
        if not self._check_prerequisites(agent, action):
            return False

        # Apply costs
        if action.cost > 0:
            self.state_manager.update_agent_resources(
                agent_id, energy_delta=-action.cost
            )

        # Execute based on action type
        success = False
        if action.action_type == ActionType.MOVE and action.target:
            success = self.movement_controller.set_destination(agent_id, action.target)

        elif action.action_type == ActionType.WAIT:
            self.state_manager.update_agent_status(agent_id, AgentStatus.IDLE)
            success = True

        elif action.action_type == ActionType.FLEE:
            # Move away from nearest threat
            threats = [p for p in self.perception_system.perceive(agent_id)
                      if p.stimulus.stimulus_type == StimulusType.DANGER]
            if threats:
                nearest_threat = min(threats, key=lambda t: t.distance)
                # Calculate flee direction
                threat_dir = nearest_threat.stimulus.position.to_array() - agent.position.to_array()
                flee_dir = -threat_dir / np.linalg.norm(threat_dir) * 20.0
                flee_pos = Position(
                    agent.position.x + flee_dir[0],
                    agent.position.y + flee_dir[1],
                    agent.position.z
                )
                success = self.movement_controller.set_destination(agent_id, flee_pos)

        elif action.action_type == ActionType.INTERACT:
            self.state_manager.update_agent_status(agent_id, AgentStatus.INTERACTING)
            success = True

        # Apply effects
        if success and action.effects:
            for effect_type, value in action.effects.items():
                if effect_type == "energy":
                    self.state_manager.update_agent_resources(
                        agent_id, energy_delta=value
                    )

        return success

    def _check_prerequisites(self, agent: Agent, action: Action) -> bool:
        """Check if action prerequisites are met"""
        # Check energy
        if agent.resources.energy < action.cost:
            return False

        # Check specific prerequisites
        for prereq in action.prerequisites:
            if prereq == "has_target" and action.target is None:
                return False
            # Add more prerequisite checks as needed

        return True

    def _calculate_time_pressure(self, agent: Agent) -> float:
        """Calculate time pressure based on agent state"""
        pressure = 0.0

        # Low resources increase time pressure
        if agent.resources.energy < 30:
            pressure += (30 - agent.resources.energy) / 30 * 0.5

        if agent.resources.health < 50:
            pressure += (50 - agent.resources.health) / 50 * 0.5

        # Goal deadlines
        if agent.current_goal and agent.current_goal.deadline:
            # Simple deadline pressure (would need proper time handling)
            pressure += 0.3

        return min(pressure, 1.0)

    def _create_default_behavior_tree(self) -> BehaviorTree:
        """Create a default behavior tree"""
        tree = BehaviorTree()

        # Root is a selector (try options in order)
        root = SelectorNode([
            # First priority: Handle threats
            ConditionNode(
                lambda ctx: len(ctx.get_perceived_threats()) > 0,
                ActionNode(lambda ctx: next(
                    (a for a in ctx.available_actions if a.action_type == ActionType.FLEE),
                    None
                ))
            ),

            # Second priority: Critical resources
            ConditionNode(
                lambda ctx: ctx.agent.resources.energy < 20,
                ActionNode(lambda ctx: next(
                    (a for a in ctx.available_actions if a.action_type == ActionType.GATHER),
                    None
                ))
            ),

            # Third priority: Goal pursuit
            ConditionNode(
                lambda ctx: ctx.current_goal is not None,
                ActionNode(lambda ctx: ctx.decision_maker._goal_oriented_decision(ctx)
                          if hasattr(ctx, 'decision_maker') else None)
            ),

            # Default: Explore or wait
            ActionNode(lambda ctx: next(
                (a for a in ctx.available_actions
                 if a.action_type in [ActionType.EXPLORE, ActionType.WAIT]),
                None
            ))
        ])

        tree.root = root
        return tree

    def get_decision_history(self, agent_id: str, limit: int = 10) -> List[Tuple[DecisionContext, Action]]:
        """Get recent decision history for an agent"""
        history = self.decision_history.get(agent_id, [])
        return history[-limit:]

    def set_decision_strategy(self, agent_id: str, strategy: DecisionStrategy) -> None:
        """Change decision strategy for an agent"""
        if agent_id in self.decision_makers:
            self.decision_makers[agent_id].strategy = strategy
