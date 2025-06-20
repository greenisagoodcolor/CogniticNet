"""
Main Agent Class for FreeAgentics

This module provides the primary Agent class that orchestrates all agent components
and implements the agent lifecycle, following ADR-002, ADR-003, and ADR-004.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Type, Callable
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .data_model import Agent as AgentData, AgentStatus, Position, Action
from .interfaces import (
    IAgentLifecycle, IAgentBehavior, IBehaviorTree, IWorldInterface,
    IActiveInferenceInterface, IAgentEventHandler, IAgentPlugin,
    IConfigurationProvider, IAgentLogger
)
from .state_manager import AgentStateManager
from .perception import PerceptionSystem
from .decision_making import DecisionSystem
from .memory import MemorySystem
from .movement import MovementController
from .interaction import InteractionSystem
from .active_inference_integration import ActiveInferenceIntegration
from .behaviors import BehaviorTreeManager


class AgentLogger(IAgentLogger):
    """Default logger implementation for agents"""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.logger = logging.getLogger(f"agent.{agent_id}")

    def log_debug(self, agent_id: str, message: str, **kwargs) -> None:
        self.logger.debug(f"[{agent_id}] {message}", extra=kwargs)

    def log_info(self, agent_id: str, message: str, **kwargs) -> None:
        self.logger.info(f"[{agent_id}] {message}", extra=kwargs)

    def log_warning(self, agent_id: str, message: str, **kwargs) -> None:
        self.logger.warning(f"[{agent_id}] {message}", extra=kwargs)

    def log_error(self, agent_id: str, message: str, **kwargs) -> None:
        self.logger.error(f"[{agent_id}] {message}", extra=kwargs)


class BaseAgent(IAgentLifecycle):
    """
    Main Agent class that orchestrates all agent components and provides
    a unified interface for agent behavior and lifecycle management.

    This class follows the composition pattern to integrate various agent
    subsystems while maintaining separation of concerns.
    """

    def __init__(
        self,
        agent_data: AgentData,
        world_interface: Optional[IWorldInterface] = None,
        active_inference_interface: Optional[IActiveInferenceInterface] = None,
        config_provider: Optional[IConfigurationProvider] = None,
        logger: Optional[IAgentLogger] = None
    ):
        """
        Initialize the agent with its data model and optional interfaces.

        Args:
            agent_data: The agent's data model
            world_interface: Interface for world interaction
            active_inference_interface: Interface for Active Inference integration
            config_provider: Configuration provider
            logger: Logger instance
        """
        # Core data
        self.data = agent_data

        # External interfaces
        self.world_interface = world_interface
        self.active_inference_interface = active_inference_interface
        self.config_provider = config_provider
        self.logger = logger or AgentLogger(self.data.agent_id)

        # Internal state
        self._is_running = False
        self._is_paused = False
        self._last_update_time = datetime.now()
        self._update_interval = timedelta(milliseconds=100)  # 10 FPS default

        # Component systems
        self._components: Dict[str, Any] = {}
        self._plugins: List[IAgentPlugin] = []
        self._event_handlers: List[IAgentEventHandler] = []

        # Thread management
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix=f"agent-{self.data.agent_id}")
        self._main_loop_task = None

        # Initialize core components
        self._initialize_core_components()

        self.logger.log_info(self.data.agent_id, f"Agent {self.data.name} initialized")

    def _initialize_core_components(self) -> None:
        """Initialize core agent components"""
        try:
            # State manager
            self._components['state_manager'] = AgentStateManager(self.data)

            # Core systems (using existing implementations)
            self._components['perception'] = PerceptionSystem()
            self._components['decision'] = DecisionSystem()
            self._components['memory'] = MemorySystem()
            self._components['movement'] = MovementController()
            self._components['interaction'] = InteractionSystem()

            # Behavior tree
            self._components['behavior_tree'] = BehaviorTreeManager()

            # Active Inference integration
            if self.active_inference_interface:
                self._components['active_inference'] = ActiveInferenceIntegration(
                    self.active_inference_interface
                )

            # Initialize all components
            for name, component in self._components.items():
                if hasattr(component, 'initialize'):
                    component.initialize(self.data)

        except Exception as e:
            self.logger.log_error(self.data.agent_id, f"Failed to initialize components: {e}")
            raise

    @property
    def agent_id(self) -> str:
        """Get agent ID"""
        return self.data.agent_id

    @property
    def is_running(self) -> bool:
        """Check if agent is running"""
        return self._is_running

    @property
    def is_paused(self) -> bool:
        """Check if agent is paused"""
        return self._is_paused

    def start(self) -> None:
        """Start the agent and initialize all components"""
        if self._is_running:
            self.logger.log_warning(self.data.agent_id, "Agent is already running")
            return

        try:
            self.logger.log_info(self.data.agent_id, "Starting agent")

            # Initialize plugins
            for plugin in self._plugins:
                plugin.initialize(self.data)

            # Update status
            self.data.update_status(AgentStatus.IDLE)
            self._is_running = True
            self._is_paused = False

            # Start main loop
            self._start_main_loop()

            # Notify event handlers
            for handler in self._event_handlers:
                handler.on_agent_created(self.data)

            self.logger.log_info(self.data.agent_id, "Agent started successfully")

        except Exception as e:
            self.logger.log_error(self.data.agent_id, f"Failed to start agent: {e}")
            self._is_running = False
            raise

    def stop(self) -> None:
        """Stop the agent and cleanup resources"""
        if not self._is_running:
            self.logger.log_warning(self.data.agent_id, "Agent is not running")
            return

        try:
            self.logger.log_info(self.data.agent_id, "Stopping agent")

            self._is_running = False
            self._is_paused = False

            # Stop main loop
            if self._main_loop_task:
                self._main_loop_task.cancel()
                self._main_loop_task = None

            # Update status
            self.data.update_status(AgentStatus.OFFLINE)

            # Cleanup plugins
            for plugin in self._plugins:
                plugin.cleanup(self.data)

            # Cleanup components
            for component in self._components.values():
                if hasattr(component, 'cleanup'):
                    component.cleanup()

            # Notify event handlers
            for handler in self._event_handlers:
                handler.on_agent_destroyed(self.data)

            # Cleanup executor
            self._executor.shutdown(wait=True)

            self.logger.log_info(self.data.agent_id, "Agent stopped successfully")

        except Exception as e:
            self.logger.log_error(self.data.agent_id, f"Error during agent shutdown: {e}")

    def pause(self) -> None:
        """Pause agent execution"""
        if not self._is_running:
            self.logger.log_warning(self.data.agent_id, "Cannot pause - agent is not running")
            return

        self._is_paused = True
        self.data.update_status(AgentStatus.IDLE)
        self.logger.log_info(self.data.agent_id, "Agent paused")

    def resume(self) -> None:
        """Resume agent execution"""
        if not self._is_running:
            self.logger.log_warning(self.data.agent_id, "Cannot resume - agent is not running")
            return

        self._is_paused = False
        self.logger.log_info(self.data.agent_id, "Agent resumed")

    def restart(self) -> None:
        """Restart the agent (stop and start)"""
        self.logger.log_info(self.data.agent_id, "Restarting agent")
        self.stop()
        time.sleep(0.1)  # Brief pause
        self.start()

    def _start_main_loop(self) -> None:
        """Start the main agent loop"""
        async def main_loop():
            while self._is_running:
                try:
                    if not self._is_paused:
                        await self._update_cycle()

                    # Calculate sleep time to maintain update rate
                    elapsed = datetime.now() - self._last_update_time
                    sleep_time = max(0, (self._update_interval - elapsed).total_seconds())
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)

                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.log_error(self.data.agent_id, f"Error in main loop: {e}")
                    self.data.update_status(AgentStatus.ERROR)
                    await asyncio.sleep(1)  # Error recovery delay

        # Start the main loop as a task
        self._main_loop_task = asyncio.create_task(main_loop())

    async def _update_cycle(self) -> None:
        """Execute one update cycle"""
        current_time = datetime.now()
        delta_time = (current_time - self._last_update_time).total_seconds()
        self._last_update_time = current_time

        try:
            # Update plugins
            for plugin in self._plugins:
                plugin.update(self.data, delta_time)

            # Perception phase
            if 'perception' in self._components:
                observations = self._components['perception'].perceive(
                    self.data, self.world_interface
                )

                # Update beliefs if Active Inference is available
                if self.active_inference_interface and observations is not None:
                    self.active_inference_interface.update_beliefs(self.data, observations)

            # Decision phase
            if 'behavior_tree' in self._components and 'decision' in self._components:
                context = self._build_decision_context()

                # Get behavior from behavior tree
                behavior = self._components['behavior_tree'].evaluate(self.data, context)

                if behavior:
                    # Execute behavior
                    self.data.update_status(AgentStatus.PLANNING)
                    result = behavior.execute(self.data, context)

                    # Process behavior result
                    if result and 'action' in result:
                        await self._execute_action(result['action'])

            # Memory consolidation
            if 'memory' in self._components:
                self._components['memory'].consolidate_memory(self.data)

        except Exception as e:
            self.logger.log_error(self.data.agent_id, f"Error in update cycle: {e}")
            self.data.update_status(AgentStatus.ERROR)

    def _build_decision_context(self) -> Dict[str, Any]:
        """Build context for decision making"""
        context = {
            'timestamp': datetime.now(),
            'delta_time': (datetime.now() - self._last_update_time).total_seconds(),
            'agent_data': self.data,
            'world_interface': self.world_interface,
        }

        # Add component states
        for name, component in self._components.items():
            if hasattr(component, 'get_state'):
                context[f'{name}_state'] = component.get_state()

        return context

    async def _execute_action(self, action: Action) -> None:
        """Execute an action"""
        try:
            self.data.update_status(AgentStatus.MOVING if action.action_type.value == 'move' else AgentStatus.INTERACTING)

            # Execute action through world interface
            if self.world_interface:
                result = self.world_interface.perform_action(self.data, action)

                # Process action result
                if result.get('success', False):
                    # Update agent state based on action
                    if action.action_type.value == 'move' and 'new_position' in result:
                        old_position = self.data.position
                        new_position = Position(**result['new_position'])
                        self.data.update_position(new_position)

                        # Notify event handlers
                        for handler in self._event_handlers:
                            handler.on_agent_moved(self.data, old_position, new_position)

                # Add to memory
                self.data.add_to_memory({
                    'action': action.to_dict(),
                    'result': result,
                    'timestamp': datetime.now()
                })

            self.data.update_status(AgentStatus.IDLE)

        except Exception as e:
            self.logger.log_error(self.data.agent_id, f"Error executing action: {e}")
            self.data.update_status(AgentStatus.ERROR)

    def add_behavior(self, behavior: IAgentBehavior) -> None:
        """Add a behavior to the agent"""
        if 'behavior_tree' in self._components:
            self._components['behavior_tree'].add_behavior(behavior)
            self.logger.log_info(self.data.agent_id, f"Added behavior: {type(behavior).__name__}")

    def remove_behavior(self, behavior: IAgentBehavior) -> None:
        """Remove a behavior from the agent"""
        if 'behavior_tree' in self._components:
            self._components['behavior_tree'].remove_behavior(behavior)
            self.logger.log_info(self.data.agent_id, f"Removed behavior: {type(behavior).__name__}")

    def add_plugin(self, plugin: IAgentPlugin) -> None:
        """Add a plugin to the agent"""
        self._plugins.append(plugin)
        if self._is_running:
            plugin.initialize(self.data)
        self.logger.log_info(self.data.agent_id, f"Added plugin: {plugin.get_name()}")

    def remove_plugin(self, plugin: IAgentPlugin) -> None:
        """Remove a plugin from the agent"""
        if plugin in self._plugins:
            if self._is_running:
                plugin.cleanup(self.data)
            self._plugins.remove(plugin)
            self.logger.log_info(self.data.agent_id, f"Removed plugin: {plugin.get_name()}")

    def add_event_handler(self, handler: IAgentEventHandler) -> None:
        """Add an event handler"""
        self._event_handlers.append(handler)

    def remove_event_handler(self, handler: IAgentEventHandler) -> None:
        """Remove an event handler"""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    def get_component(self, name: str) -> Optional[Any]:
        """Get a component by name"""
        return self._components.get(name)

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the agent's current state"""
        return {
            'agent_id': self.data.agent_id,
            'name': self.data.name,
            'type': self.data.agent_type,
            'status': self.data.status.value,
            'position': self.data.position.to_array().tolist(),
            'is_running': self._is_running,
            'is_paused': self._is_paused,
            'energy': self.data.resources.energy,
            'health': self.data.resources.health,
            'goal_count': len(self.data.goals),
            'current_goal': self.data.current_goal.description if self.data.current_goal else None,
            'relationship_count': len(self.data.relationships),
            'plugin_count': len(self._plugins),
            'last_update': self._last_update_time.isoformat()
        }

    def __repr__(self) -> str:
        return f"BaseAgent(id={self.data.agent_id}, name={self.data.name}, type={self.data.agent_type}, status={self.data.status.value})"


# Convenience function for creating agents
def create_agent(
    agent_type: str = "basic",
    name: str = "Agent",
    position: Optional[Position] = None,
    **kwargs
) -> BaseAgent:
    """
    Convenience function to create a new agent.

    Args:
        agent_type: Type of agent to create
        name: Agent name
        position: Initial position
        **kwargs: Additional agent data parameters

    Returns:
        BaseAgent instance
    """
    agent_data = AgentData(
        name=name,
        agent_type=agent_type,
        position=position or Position(0.0, 0.0, 0.0),
        **kwargs
    )

    return BaseAgent(agent_data)
