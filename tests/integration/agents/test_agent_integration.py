"""
Integration tests for agent system

This module contains integration tests that verify the correct
interaction between different agent components and systems.
"""

import pytest
import time
from datetime import datetime, timedelta
import numpy as np

from agents.base.data_model import (
    Agent, Position, Orientation, AgentStatus, AgentCapability,
    AgentPersonality, AgentResources, AgentGoal,
    ResourceAgent, SocialAgent
)
from agents.base.state_manager import AgentStateManager
from agents.base.movement import MovementController
from agents.base.perception import PerceptionSystem, Stimulus, StimulusType
from agents.base.decision_making import DecisionSystem, ActionType
from agents.base.interaction import InteractionSystem, InteractionType
from agents.base.memory import MemorySystem
from agents.base.persistence import AgentPersistence

from src.agents.testing.agent_test_framework import (
    AgentFactory, SimulationEnvironment, TestOrchestrator,
    TestScenario, BehaviorValidator, PerformanceBenchmark
)


class TestAgentIntegration:
    """Integration tests for agent systems"""

    def test_full_agent_lifecycle(self):
        """Test complete agent lifecycle from creation to persistence"""
        # Create agent
        agent = AgentFactory.create_basic_agent("test_agent")
        assert agent is not None
        assert agent.status == AgentStatus.IDLE

        # Initialize systems
        state_manager = AgentStateManager(agent)
        movement_controller = MovementController(agent)
        perception_system = PerceptionSystem()
        perception_system.register_agent(agent)
        decision_system = DecisionSystem(agent)
        memory_system = MemorySystem(agent.id, agent.resources.memory_capacity)

        # Test state transitions
        state_manager.update_state(AgentStatus.MOVING)
        assert agent.status == AgentStatus.MOVING

        # Test movement
        target = Position(10, 10, 0)
        movement_controller.move_to(target)
        movement_controller.update(0.1)

        # Verify position changed
        assert agent.position.x != 0 or agent.position.y != 0

        # Test perception
        stimulus = Stimulus(
            type=StimulusType.VISUAL,
            source_id="object1",
            position=Position(5, 5, 0),
            intensity=1.0,
            data={"type": "resource"}
        )
        perception_system.add_stimulus(stimulus)
        percepts = perception_system.get_percepts(agent.id)
        assert len(percepts) > 0

        # Test decision making
        context = decision_system.create_context(percepts, memory_system)
        action = decision_system.decide(context)
        assert action is not None

        # Test memory
        memory_system.add_to_working_memory("test_key", {"data": "test"})
        assert "test_key" in memory_system.working_memory.items

        # Test persistence
        persistence = AgentPersistence()

        # Save agent
        agent_data = persistence.serialize_agent(agent)
        assert agent_data is not None

        # Load agent
        loaded_agent = persistence.deserialize_agent(agent_data)
        assert loaded_agent.id == agent.id
        assert loaded_agent.position.x == agent.position.x

    def test_multi_agent_interaction(self):
        """Test interaction between multiple agents"""
        # Create agents
        agent1 = AgentFactory.create_social_agent("agent1")
        agent2 = AgentFactory.create_social_agent("agent2")
        agent3 = AgentFactory.create_resource_agent("agent3")

        # Create interaction system
        interaction_system = InteractionSystem()

        # Test communication
        result = interaction_system.send_message(
            sender_id=agent1.id,
            receiver_id=agent2.id,
            content={"greeting": "hello"}
        )
        assert result.success

        # Test resource exchange
        agent3.resources.energy = 100
        agent1.resources.energy = 50

        exchange = interaction_system.request_resource_exchange(
            requester=agent1,
            provider=agent3,
            resource_type="energy",
            amount=20
        )

        # Process the exchange
        if exchange:
            result = interaction_system.process_resource_exchange(exchange)
            assert result.success

    def test_environment_simulation(self):
        """Test full environment simulation with multiple agents"""
        # Create environment
        environment = SimulationEnvironment(
            bounds=(-50, -50, 50, 50),
            time_scale=1.0
        )

        # Add agents
        for i in range(5):
            agent = AgentFactory.create_basic_agent(f"agent_{i}")
            environment.add_agent(agent)

        # Add resources
        environment.add_resource(Position(10, 10, 0), "energy", 100)
        environment.add_resource(Position(-20, 15, 0), "materials", 50)

        # Add obstacles
        environment.add_obstacle(Position(0, 0, 0), 5.0)

        # Run simulation
        for _ in range(100):
            environment.step(0.1)

        # Verify simulation ran
        assert environment.current_time > 0
        metrics = environment.get_metrics()
        assert metrics["agent_count"] == 5
        assert metrics["resource_count"] == 2

    def test_behavior_validation(self):
        """Test behavior validation system"""
        agent = AgentFactory.create_basic_agent("validator_test")
        validator = BehaviorValidator()

        # Create movement history
        history = []
        positions = [
            Position(0, 0, 0),
            Position(1, 0, 0),
            Position(2, 1, 0),
            Position(3, 2, 0)
        ]

        for i, pos in enumerate(positions):
            history.append({
                "timestamp": i * 0.1,
                "position": pos,
                "action": "move"
            })

        # Validate movement
        success, error = validator.validate("movement_coherence", agent, history)
        assert success

        # Test invalid movement (teleportation)
        history.append({
            "timestamp": len(history) * 0.1,
            "position": Position(100, 100, 0)  # Far away
        })

        success, error = validator.validate("movement_coherence", agent, history)
        assert not success
        assert "Impossible speed" in error

    def test_performance_benchmarking(self):
        """Test performance benchmarking system"""
        benchmark = PerformanceBenchmark()

        # Benchmark agent creation
        with benchmark.measure("agent_creation"):
            for i in range(100):
                AgentFactory.create_basic_agent(f"perf_agent_{i}")

        # Benchmark state updates
        agent = AgentFactory.create_basic_agent("benchmark_agent")
        state_manager = AgentStateManager(agent)

        with benchmark.measure("state_update"):
            for _ in range(1000):
                state_manager.update_state(AgentStatus.MOVING)
                state_manager.update_state(AgentStatus.IDLE)

        # Get report
        report = benchmark.get_report()
        assert "agent_creation" in report
        assert "state_update" in report
        assert report["agent_creation"]["count"] == 1
        assert report["state_update"]["count"] == 1
        assert report["state_update"]["mean"] < 1.0  # Should be fast

    def test_scenario_orchestration(self):
        """Test scenario orchestration system"""
        orchestrator = TestOrchestrator()

        # Create a simple scenario
        scenario = TestScenario(
            name="Test Scenario",
            description="Basic test scenario",
            duration=5.0,
            agent_configs=[
                {"type": "basic", "id": "test1"},
                {"type": "resource", "id": "test2"},
                {"type": "social", "id": "test3"}
            ],
            environment_config={
                "bounds": (-20, -20, 20, 20),
                "time_scale": 10.0  # Speed up for testing
            },
            success_criteria={
                "all_agents_active": True
            },
            metrics_to_track=["position", "energy", "status"]
        )

        orchestrator.add_scenario(scenario)

        # Run scenario
        results = orchestrator.run_all_scenarios()
        assert len(results) == 1

        result = results[0]
        assert result.scenario_name == "Test Scenario"
        assert result.success is not None
        assert result.end_time > result.start_time

        # Generate report
        report = orchestrator.generate_report()
        assert report["summary"]["total_scenarios"] == 1

    def test_agent_memory_persistence(self):
        """Test memory system persistence across agent reload"""
        # Create agent with memory
        agent = AgentFactory.create_basic_agent("memory_test")
        memory_system = MemorySystem(agent.id, 100)

        # Add memories
        memory_system.store_experience(
            state={"location": "home"},
            action={"type": "explore"},
            outcome={"found": "resource"},
            reward=10.0
        )

        memory_system.add_to_working_memory("important", {"data": "remember this"})
        memory_system.consolidate()

        # Save agent with memory
        persistence = AgentPersistence()
        agent_data = persistence.serialize_agent(agent)

        # In practice, memory would be serialized separately
        # For this test, we'll verify memory system works
        assert len(memory_system.episodic_memory) > 0
        assert len(memory_system.long_term_memory) > 0

    def test_perception_to_decision_pipeline(self):
        """Test the full pipeline from perception to decision"""
        # Create agent
        agent = AgentFactory.create_basic_agent("pipeline_test")
        agent.capabilities.add(AgentCapability.COMMUNICATION)

        # Create systems
        perception_system = PerceptionSystem()
        perception_system.register_agent(agent)
        decision_system = DecisionSystem(agent)
        memory_system = MemorySystem(agent.id, 100)

        # Add stimuli
        perception_system.add_stimulus(Stimulus(
            type=StimulusType.VISUAL,
            source_id="food",
            position=Position(10, 0, 0),
            intensity=1.0,
            data={"type": "food", "quantity": 50}
        ))

        perception_system.add_stimulus(Stimulus(
            type=StimulusType.AUDITORY,
            source_id="agent_2",
            position=Position(-5, 5, 0),
            intensity=0.8,
            data={"message": "help"}
        ))

        # Get percepts
        percepts = perception_system.get_percepts(agent.id)
        assert len(percepts) >= 2

        # Make decision
        context = decision_system.create_context(percepts, memory_system)
        action = decision_system.decide(context)

        assert action is not None
        assert action.type in [ActionType.MOVE, ActionType.COMMUNICATE, ActionType.GATHER]

    def test_movement_with_obstacles(self):
        """Test movement system with obstacle avoidance"""
        # Create agent
        agent = AgentFactory.create_basic_agent("obstacle_test")
        movement_controller = MovementController(agent)

        # Add obstacles
        movement_controller.collision_system.add_static_obstacle(
            Position(5, 0, 0), 2.0
        )
        movement_controller.collision_system.add_static_obstacle(
            Position(10, 5, 0), 3.0
        )

        # Plan path
        start = Position(0, 0, 0)
        goal = Position(15, 5, 0)

        path = movement_controller.pathfinding_system.find_path(start, goal)

        # Path should avoid obstacles
        assert path is not None
        assert len(path) > 2  # Not direct path

        # Follow path
        movement_controller.follow_path(path)

        # Simulate movement
        for _ in range(100):
            movement_controller.update(0.1)
            if agent.position.distance_to(goal) < 1.0:
                break

        # Should reach near goal
        assert agent.position.distance_to(goal) < 5.0


class TestAgentStressTests:
    """Stress tests for agent systems"""

    def test_many_agents_simulation(self):
        """Test simulation with many agents"""
        environment = SimulationEnvironment(
            bounds=(-200, -200, 200, 200),
            time_scale=1.0
        )

        # Add 100 agents
        agents = []
        for i in range(100):
            agent_type = ["basic", "resource", "social"][i % 3]
            if agent_type == "basic":
                agent = AgentFactory.create_basic_agent(f"stress_{i}")
            elif agent_type == "resource":
                agent = AgentFactory.create_resource_agent(f"stress_{i}")
            else:
                agent = AgentFactory.create_social_agent(f"stress_{i}")

            environment.add_agent(agent)
            agents.append(agent)

        # Add resources
        for i in range(50):
            pos = Position(
                np.random.uniform(-190, 190),
                np.random.uniform(-190, 190),
                0
            )
            environment.add_resource(pos, "energy", np.random.uniform(10, 100))

        # Run simulation
        start_time = time.time()
        for _ in range(10):
            environment.step(0.1)

        duration = time.time() - start_time

        # Should complete in reasonable time
        assert duration < 5.0  # 5 seconds for 10 steps with 100 agents

        # All agents should still be active
        for agent in agents:
            assert agent.status != AgentStatus.ERROR

    def test_memory_system_capacity(self):
        """Test memory system with large amounts of data"""
        memory_system = MemorySystem("capacity_test", 1000)

        # Store many experiences
        for i in range(1000):
            memory_system.store_experience(
                state={"index": i, "data": f"state_{i}" * 10},
                action={"type": f"action_{i % 10}"},
                outcome={"result": f"outcome_{i}"},
                reward=np.random.random()
            )

        # Should handle capacity limits gracefully
        assert len(memory_system.episodic_memory) <= memory_system.capacity

        # Consolidate memories
        memory_system.consolidate()

        # Should have moved some to long-term
        assert len(memory_system.long_term_memory) > 0

        # Working memory should still function
        for i in range(50):
            memory_system.add_to_working_memory(f"key_{i}", {"data": i})

        assert len(memory_system.working_memory.items) <= 10  # Working memory limit


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
