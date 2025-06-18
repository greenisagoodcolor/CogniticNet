"""
Agent Testing Framework

This module provides comprehensive testing utilities for agent behaviors,
including fixtures, simulation environments, performance benchmarking,
and behavior validation tools.
"""

import time
import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Callable, Any, Set
from datetime import datetime, timedelta
import threading
import multiprocessing
import json
import numpy as np
from contextlib import contextmanager
import logging

from src.agents.basic_agent.data_model import (
    Agent, Position, Orientation, AgentStatus, AgentCapability,
    AgentPersonality, AgentResources, SocialRelationship, AgentGoal,
    ResourceAgent, SocialAgent
)
from src.agents.basic_agent.state_manager import AgentStateManager
from src.agents.basic_agent.movement import MovementController
from src.agents.basic_agent.perception import PerceptionSystem
from src.agents.basic_agent.decision_making import DecisionSystem
from src.agents.basic_agent.interaction import InteractionSystem
from src.agents.basic_agent.memory import MemorySystem

logger = logging.getLogger(__name__)


@dataclass
class TestScenario:
    """Represents a test scenario for agent behavior"""
    name: str
    description: str
    duration: float  # seconds
    agent_configs: List[Dict[str, Any]]
    environment_config: Dict[str, Any]
    success_criteria: Dict[str, Any]
    metrics_to_track: List[str]


@dataclass
class TestMetrics:
    """Metrics collected during test execution"""
    scenario_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    agent_metrics: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    environment_metrics: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    success: Optional[bool] = None
    failure_reason: Optional[str] = None


class AgentFactory:
    """Factory for creating test agents with various configurations"""

    @staticmethod
    def create_basic_agent(
        agent_id: str,
        position: Position = None,
        personality: AgentPersonality = None,
        capabilities: Set[AgentCapability] = None
    ) -> Agent:
        """Create a basic test agent"""
        if position is None:
            position = Position(
                random.uniform(-100, 100),
                random.uniform(-100, 100),
                0
            )

        if personality is None:
            personality = AgentPersonality(
                openness=random.random(),
                conscientiousness=random.random(),
                extraversion=random.random(),
                agreeableness=random.random(),
                neuroticism=random.random()
            )

        if capabilities is None:
            capabilities = {AgentCapability.MOVEMENT, AgentCapability.PERCEPTION}

        return Agent(
            id=agent_id,
            name=f"TestAgent_{agent_id}",
            position=position,
            orientation=Orientation(0, 0, 0, 1),
            personality=personality,
            capabilities=capabilities,
            resources=AgentResources(energy=100.0, health=100.0, memory_capacity=100)
        )

    @staticmethod
    def create_resource_agent(
        agent_id: str,
        resource_types: List[str] = None
    ) -> ResourceAgent:
        """Create a resource-focused test agent"""
        agent = AgentFactory.create_basic_agent(agent_id)
        if resource_types is None:
            resource_types = ["energy", "materials"]

        return ResourceAgent(
            id=agent.id,
            name=agent.name,
            position=agent.position,
            orientation=agent.orientation,
            personality=agent.personality,
            capabilities=agent.capabilities | {AgentCapability.RESOURCE_MANAGEMENT},
            resources=agent.resources,
            managed_resources=resource_types,
            exchange_rates={"energy": 1.0, "materials": 2.0}
        )

    @staticmethod
    def create_social_agent(
        agent_id: str,
        trust_threshold: float = 0.5
    ) -> SocialAgent:
        """Create a socially-focused test agent"""
        agent = AgentFactory.create_basic_agent(agent_id)

        return SocialAgent(
            id=agent.id,
            name=agent.name,
            position=agent.position,
            orientation=agent.orientation,
            personality=agent.personality,
            capabilities=agent.capabilities | {AgentCapability.COMMUNICATION},
            resources=agent.resources,
            trust_threshold=trust_threshold,
            cooperation_history={}
        )


class SimulationEnvironment:
    """Simulated environment for agent testing"""

    def __init__(self, bounds: Tuple[float, float, float, float], time_scale: float = 1.0):
        """
        Initialize simulation environment

        Args:
            bounds: (min_x, min_y, max_x, max_y)
            time_scale: Time multiplier for simulation speed
        """
        self.bounds = bounds
        self.time_scale = time_scale
        self.agents: Dict[str, Agent] = {}
        self.resources: Dict[Position, Dict[str, float]] = {}
        self.obstacles: List[Tuple[Position, float]] = []  # (position, radius)
        self.current_time = 0.0
        self.events: List[Dict[str, Any]] = []

        # Systems
        self.state_managers: Dict[str, AgentStateManager] = {}
        self.movement_controllers: Dict[str, MovementController] = {}
        self.perception_system = PerceptionSystem()
        self.decision_systems: Dict[str, DecisionSystem] = {}
        self.interaction_system = InteractionSystem()
        self.memory_systems: Dict[str, MemorySystem] = {}

    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the simulation"""
        self.agents[agent.id] = agent

        # Initialize systems for the agent
        self.state_managers[agent.id] = AgentStateManager(agent)
        self.movement_controllers[agent.id] = MovementController(agent)
        self.perception_system.register_agent(agent)
        self.decision_systems[agent.id] = DecisionSystem(agent)
        self.memory_systems[agent.id] = MemorySystem(
            agent_id=agent.id,
            capacity=agent.resources.memory_capacity
        )

    def add_resource(self, position: Position, resource_type: str, amount: float) -> None:
        """Add a resource to the environment"""
        if position not in self.resources:
            self.resources[position] = {}
        self.resources[position][resource_type] = amount

    def add_obstacle(self, position: Position, radius: float) -> None:
        """Add an obstacle to the environment"""
        self.obstacles.append((position, radius))

        # Update collision systems
        for controller in self.movement_controllers.values():
            controller.collision_system.add_static_obstacle(position, radius)

    def step(self, delta_time: float) -> None:
        """Advance simulation by one time step"""
        actual_delta = delta_time * self.time_scale
        self.current_time += actual_delta

        # Update all agents
        for agent_id, agent in self.agents.items():
            # Perception
            percepts = self.perception_system.get_percepts(agent_id)

            # Decision making
            decision_context = self.decision_systems[agent_id].create_context(
                percepts, self.memory_systems[agent_id]
            )
            action = self.decision_systems[agent_id].decide(decision_context)

            # Execute action
            if action:
                self._execute_action(agent, action, actual_delta)

            # Update memory
            self.memory_systems[agent_id].update(actual_delta)

    def _execute_action(self, agent: Agent, action: Any, delta_time: float) -> None:
        """Execute an agent's action"""
        # This would contain logic to execute different action types
        # For now, we'll keep it simple
        pass

    def get_metrics(self) -> Dict[str, Any]:
        """Get current environment metrics"""
        return {
            "time": self.current_time,
            "agent_count": len(self.agents),
            "resource_count": sum(len(r) for r in self.resources.values()),
            "total_resources": sum(
                amount
                for resources in self.resources.values()
                for amount in resources.values()
            ),
            "events": len(self.events)
        }


class BehaviorValidator:
    """Validates agent behaviors against expected patterns"""

    def __init__(self):
        self.validators: Dict[str, Callable] = {}
        self._register_default_validators()

    def _register_default_validators(self):
        """Register default behavior validators"""
        self.validators["movement_coherence"] = self._validate_movement_coherence
        self.validators["decision_consistency"] = self._validate_decision_consistency
        self.validators["resource_efficiency"] = self._validate_resource_efficiency
        self.validators["social_cooperation"] = self._validate_social_cooperation

    def validate(
        self,
        behavior_type: str,
        agent: Agent,
        history: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a specific behavior type

        Returns:
            (success, error_message)
        """
        if behavior_type not in self.validators:
            return False, f"Unknown behavior type: {behavior_type}"

        return self.validators[behavior_type](agent, history)

    def _validate_movement_coherence(
        self,
        agent: Agent,
        history: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """Validate that movement is coherent and follows physics"""
        positions = [h.get("position") for h in history if "position" in h]
        if len(positions) < 2:
            return True, None

        # Check for teleportation or impossible speeds
        for i in range(1, len(positions)):
            if positions[i] and positions[i-1]:
                distance = positions[i].distance_to(positions[i-1])
                time_delta = history[i].get("timestamp", 0) - history[i-1].get("timestamp", 0)

                if time_delta > 0:
                    speed = distance / time_delta
                    if speed > 100:  # Arbitrary max speed
                        return False, f"Impossible speed detected: {speed} units/s"

        return True, None

    def _validate_decision_consistency(
        self,
        agent: Agent,
        history: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """Validate that decisions are consistent with agent goals"""
        # Implementation would check decision patterns
        return True, None

    def _validate_resource_efficiency(
        self,
        agent: Agent,
        history: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """Validate resource usage efficiency"""
        # Implementation would analyze resource consumption patterns
        return True, None

    def _validate_social_cooperation(
        self,
        agent: Agent,
        history: List[Dict[str, Any]]
    ) -> Tuple[bool, Optional[str]]:
        """Validate social interaction patterns"""
        # Implementation would check cooperation metrics
        return True, None


class PerformanceBenchmark:
    """Performance benchmarking for agent operations"""

    def __init__(self):
        self.results: Dict[str, List[float]] = {}

    @contextmanager
    def measure(self, operation: str):
        """Context manager for measuring operation performance"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration = time.perf_counter() - start_time
            if operation not in self.results:
                self.results[operation] = []
            self.results[operation].append(duration)

    def get_statistics(self, operation: str) -> Dict[str, float]:
        """Get performance statistics for an operation"""
        if operation not in self.results or not self.results[operation]:
            return {}

        times = self.results[operation]
        return {
            "count": len(times),
            "mean": statistics.mean(times),
            "median": statistics.median(times),
            "min": min(times),
            "max": max(times),
            "stdev": statistics.stdev(times) if len(times) > 1 else 0.0
        }

    def get_report(self) -> Dict[str, Dict[str, float]]:
        """Get full performance report"""
        return {
            operation: self.get_statistics(operation)
            for operation in self.results
        }


class TestOrchestrator:
    """Orchestrates test execution and reporting"""

    def __init__(self):
        self.scenarios: List[TestScenario] = []
        self.results: List[TestMetrics] = []
        self.benchmark = PerformanceBenchmark()
        self.validator = BehaviorValidator()

    def add_scenario(self, scenario: TestScenario) -> None:
        """Add a test scenario"""
        self.scenarios.append(scenario)

    def run_scenario(self, scenario: TestScenario) -> TestMetrics:
        """Run a single test scenario"""
        logger.info(f"Running scenario: {scenario.name}")

        metrics = TestMetrics(
            scenario_name=scenario.name,
            start_time=datetime.now()
        )

        try:
            # Create environment
            env_config = scenario.environment_config
            environment = SimulationEnvironment(
                bounds=env_config.get("bounds", (-100, -100, 100, 100)),
                time_scale=env_config.get("time_scale", 1.0)
            )

            # Create and add agents
            agents = []
            for agent_config in scenario.agent_configs:
                agent_type = agent_config.get("type", "basic")
                agent_id = agent_config.get("id", f"agent_{len(agents)}")

                if agent_type == "resource":
                    agent = AgentFactory.create_resource_agent(agent_id)
                elif agent_type == "social":
                    agent = AgentFactory.create_social_agent(agent_id)
                else:
                    agent = AgentFactory.create_basic_agent(agent_id)

                environment.add_agent(agent)
                agents.append(agent)

            # Run simulation
            step_duration = 0.1  # 100ms per step
            steps = int(scenario.duration / step_duration)

            for step in range(steps):
                with self.benchmark.measure("simulation_step"):
                    environment.step(step_duration)

                # Collect metrics periodically
                if step % 10 == 0:
                    self._collect_metrics(environment, metrics)

            # Final metrics collection
            self._collect_metrics(environment, metrics)

            # Evaluate success criteria
            metrics.success = self._evaluate_criteria(
                scenario.success_criteria,
                metrics
            )

        except Exception as e:
            logger.error(f"Scenario failed: {e}")
            metrics.success = False
            metrics.failure_reason = str(e)

        metrics.end_time = datetime.now()
        self.results.append(metrics)

        return metrics

    def run_all_scenarios(self) -> List[TestMetrics]:
        """Run all test scenarios"""
        results = []
        for scenario in self.scenarios:
            result = self.run_scenario(scenario)
            results.append(result)
        return results

    def _collect_metrics(
        self,
        environment: SimulationEnvironment,
        metrics: TestMetrics
    ) -> None:
        """Collect metrics from the environment"""
        # Environment metrics
        metrics.environment_metrics = environment.get_metrics()

        # Agent metrics
        for agent_id, agent in environment.agents.items():
            if agent_id not in metrics.agent_metrics:
                metrics.agent_metrics[agent_id] = {}

            metrics.agent_metrics[agent_id].update({
                "position": (agent.position.x, agent.position.y, agent.position.z),
                "status": agent.status.value,
                "energy": agent.resources.energy,
                "health": agent.resources.health,
                "relationships": len(agent.relationships)
            })

        # Performance metrics
        metrics.performance_metrics = self.benchmark.get_report()

    def _evaluate_criteria(
        self,
        criteria: Dict[str, Any],
        metrics: TestMetrics
    ) -> bool:
        """Evaluate success criteria"""
        # Simple criteria evaluation
        # In practice, this would be more sophisticated
        return True

    def generate_report(self) -> Dict[str, Any]:
        """Generate test report"""
        return {
            "summary": {
                "total_scenarios": len(self.results),
                "successful": sum(1 for r in self.results if r.success),
                "failed": sum(1 for r in self.results if not r.success),
                "total_duration": sum(
                    (r.end_time - r.start_time).total_seconds()
                    for r in self.results
                    if r.end_time
                )
            },
            "scenarios": [
                {
                    "name": r.scenario_name,
                    "success": r.success,
                    "duration": (r.end_time - r.start_time).total_seconds() if r.end_time else None,
                    "failure_reason": r.failure_reason,
                    "metrics": {
                        "environment": r.environment_metrics,
                        "performance": r.performance_metrics
                    }
                }
                for r in self.results
            ],
            "performance": self.benchmark.get_report()
        }


# Predefined test scenarios
def create_basic_test_scenarios() -> List[TestScenario]:
    """Create basic test scenarios for agent testing"""
    scenarios = []

    # Movement test scenario
    scenarios.append(TestScenario(
        name="Basic Movement",
        description="Test basic agent movement capabilities",
        duration=10.0,
        agent_configs=[
            {"type": "basic", "id": "mover1"},
            {"type": "basic", "id": "mover2"}
        ],
        environment_config={
            "bounds": (-50, -50, 50, 50),
            "time_scale": 1.0
        },
        success_criteria={
            "all_agents_moved": True,
            "no_collisions": True
        },
        metrics_to_track=["position", "velocity", "energy"]
    ))

    # Resource collection scenario
    scenarios.append(TestScenario(
        name="Resource Collection",
        description="Test resource discovery and collection",
        duration=30.0,
        agent_configs=[
            {"type": "resource", "id": "collector1"},
            {"type": "resource", "id": "collector2"},
            {"type": "resource", "id": "collector3"}
        ],
        environment_config={
            "bounds": (-100, -100, 100, 100),
            "time_scale": 2.0,
            "resources": [
                {"position": (10, 10), "type": "energy", "amount": 50},
                {"position": (-20, 30), "type": "materials", "amount": 30},
                {"position": (40, -40), "type": "energy", "amount": 40}
            ]
        },
        success_criteria={
            "resources_collected": 0.5,  # 50% of resources
            "agent_survival": 1.0  # All agents survive
        },
        metrics_to_track=["resources", "energy", "position"]
    ))

    # Social interaction scenario
    scenarios.append(TestScenario(
        name="Social Cooperation",
        description="Test social interaction and cooperation",
        duration=20.0,
        agent_configs=[
            {"type": "social", "id": "social1"},
            {"type": "social", "id": "social2"},
            {"type": "social", "id": "social3"},
            {"type": "social", "id": "social4"}
        ],
        environment_config={
            "bounds": (-30, -30, 30, 30),
            "time_scale": 1.0
        },
        success_criteria={
            "relationships_formed": 4,  # At least 4 relationships
            "trust_established": True
        },
        metrics_to_track=["relationships", "trust", "communications"]
    ))

    return scenarios


if __name__ == "__main__":
    # Example usage
    orchestrator = TestOrchestrator()

    # Add test scenarios
    for scenario in create_basic_test_scenarios():
        orchestrator.add_scenario(scenario)

    # Run tests
    results = orchestrator.run_all_scenarios()

    # Generate report
    report = orchestrator.generate_report()
    print(json.dumps(report, indent=2))
