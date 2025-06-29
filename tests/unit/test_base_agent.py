"""
Comprehensive tests for BaseAgent class.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any
from datetime import datetime

import torch

from agents.base.agent import BaseAgent
from agents.base.data_model import (
    Agent as AgentData, 
    AgentStatus, 
    Position, 
    AgentCapability, 
    AgentPersonality, 
    AgentResources,
    Orientation,
    AgentGoal
)
from agents.base.behaviors import BehaviorTreeManager
from agents.base.memory import MemorySystem
from agents.base.perception import PerceptionSystem
from agents.base.interfaces import IAgentLogger, IWorldInterface, IActiveInferenceInterface, IMarkovBlanketInterface


class TestAgentData:
    """Test AgentData dataclass."""
    
    def test_default_agent_data(self):
        """Test default agent data values."""
        agent_data = AgentData()
        assert agent_data.agent_id is not None
        assert agent_data.name == "Agent"
        assert agent_data.agent_type == "basic"
        assert agent_data.status == AgentStatus.IDLE
        assert isinstance(agent_data.position, Position)
        assert agent_data.position.x == 0.0
        assert agent_data.position.y == 0.0
        assert agent_data.position.z == 0.0
    
    def test_custom_agent_data(self):
        """Test custom agent data values."""
        pos = Position(10.0, 20.0, 5.0)
        agent_data = AgentData(
            agent_id="agent-001",
            name="TestAgent",
            agent_type="explorer",
            position=pos,
            status=AgentStatus.MOVING
        )
        assert agent_data.agent_id == "agent-001"
        assert agent_data.name == "TestAgent"
        assert agent_data.agent_type == "explorer"
        assert agent_data.position == pos
        assert agent_data.status == AgentStatus.MOVING
    
    def test_agent_capabilities(self):
        """Test agent capabilities."""
        agent_data = AgentData()
        assert AgentCapability.MOVEMENT in agent_data.capabilities
        assert AgentCapability.PERCEPTION in agent_data.capabilities
        assert AgentCapability.COMMUNICATION in agent_data.capabilities
        assert AgentCapability.MEMORY in agent_data.capabilities
        assert AgentCapability.LEARNING in agent_data.capabilities
    
    def test_agent_resources(self):
        """Test agent resources."""
        agent_data = AgentData()
        assert agent_data.resources.energy == 100.0
        assert agent_data.resources.health == 100.0
        assert agent_data.resources.memory_capacity == 100.0
        assert agent_data.resources.memory_used == 0.0
        
        # Test energy consumption
        agent_data.resources.consume_energy(20.0)
        assert agent_data.resources.energy == 80.0
        
        # Test energy restoration
        agent_data.resources.restore_energy(30.0)
        assert agent_data.resources.energy == 100.0  # Capped at max


class TestPosition:
    """Test Position dataclass."""
    
    def test_position_creation(self):
        """Test position creation."""
        pos = Position(1.0, 2.0, 3.0)
        assert pos.x == 1.0
        assert pos.y == 2.0
        assert pos.z == 3.0
    
    def test_position_default_z(self):
        """Test position with default z value."""
        pos = Position(1.0, 2.0)
        assert pos.x == 1.0
        assert pos.y == 2.0
        assert pos.z == 0.0
    
    def test_position_to_array(self):
        """Test conversion to numpy array."""
        pos = Position(1.0, 2.0, 3.0)
        arr = pos.to_array()
        assert isinstance(arr, np.ndarray)
        assert np.array_equal(arr, np.array([1.0, 2.0, 3.0]))
    
    def test_position_distance(self):
        """Test distance calculation."""
        pos1 = Position(0.0, 0.0, 0.0)
        pos2 = Position(3.0, 4.0, 0.0)
        distance = pos1.distance_to(pos2)
        assert distance == 5.0  # 3-4-5 triangle
    
    def test_position_hash(self):
        """Test position hashing."""
        pos1 = Position(1.0, 2.0, 3.0)
        pos2 = Position(1.0, 2.0, 3.0)
        pos3 = Position(1.0, 2.0, 4.0)
        
        assert hash(pos1) == hash(pos2)
        assert hash(pos1) != hash(pos3)
    
    def test_position_equality(self):
        """Test position equality."""
        pos1 = Position(1.0, 2.0, 3.0)
        pos2 = Position(1.0, 2.0, 3.0)
        pos3 = Position(1.0, 2.0, 4.0)
        
        assert pos1 == pos2
        assert pos1 != pos3


class TestBaseAgent:
    """Test BaseAgent class."""
    
    @pytest.fixture
    def agent_data(self):
        """Create test agent data."""
        return AgentData(
            agent_id="test-agent",
            name="TestAgent",
            agent_type="explorer",
            position=Position(0.0, 0.0, 0.0)
        )
    
    @pytest.fixture
    def mock_world_interface(self):
        """Create mock world interface."""
        mock = Mock(spec=IWorldInterface)
        mock.get_world_state.return_value = {"time": 0, "entities": []}
        mock.get_entities_in_radius.return_value = []
        return mock
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger."""
        mock = Mock(spec=IAgentLogger)
        return mock
    
    @pytest.fixture
    def test_agent(self, agent_data, mock_world_interface, mock_logger):
        """Create test agent with mocked components."""
        agent = BaseAgent(
            agent_data=agent_data,
            world_interface=mock_world_interface,
            logger=mock_logger
        )
        return agent
    
    def test_agent_initialization(self, agent_data, mock_world_interface):
        """Test agent initialization."""
        agent = BaseAgent(
            agent_data=agent_data,
            world_interface=mock_world_interface
        )
        
        assert agent.agent_data == agent_data
        assert agent.agent_id == "test-agent"
        assert agent.name == "TestAgent"
        assert hasattr(agent, 'perception_system')
        assert hasattr(agent, 'memory_system')
        assert hasattr(agent, 'behavior_manager')
    
    def test_agent_backward_compatibility(self, mock_world_interface):
        """Test agent initialization with backward compatibility parameters."""
        agent = BaseAgent(
            agent_id="old-agent",
            name="OldAgent",
            agent_type="basic",
            initial_position=(10.0, 20.0),
            world_interface=mock_world_interface
        )
        
        assert agent.agent_id == "old-agent"
        assert agent.name == "OldAgent"
        assert agent.agent_data.position.x == 10.0
        assert agent.agent_data.position.y == 20.0
    
    def test_agent_initialization_lifecycle(self, test_agent):
        """Test agent initialization lifecycle."""
        test_agent.initialize()
        
        assert test_agent._initialized
        assert test_agent.agent_data.status == AgentStatus.IDLE
    
    def test_agent_update_cycle(self, test_agent):
        """Test agent update cycle."""
        test_agent.initialize()
        test_agent.update(0.1)  # 0.1 second delta time
        
        # Should have called subsystem updates
        assert hasattr(test_agent, '_last_update_time')
    
    def test_agent_step_execution(self, test_agent):
        """Test agent step execution."""
        test_agent.initialize()
        test_agent.start()
        
        # Execute a step
        test_agent.step()
        
        # Check that step was executed
        assert test_agent._step_count > 0
    
    def test_agent_pause_resume(self, test_agent):
        """Test agent pause and resume."""
        test_agent.initialize()
        test_agent.start()
        
        assert test_agent._running
        
        test_agent.pause()
        assert not test_agent._running
        
        test_agent.resume()
        assert test_agent._running
    
    def test_agent_stop(self, test_agent):
        """Test agent stop."""
        test_agent.initialize()
        test_agent.start()
        test_agent.stop()
        
        assert not test_agent._running
        assert not test_agent._task_runner
    
    def test_agent_shutdown(self, test_agent):
        """Test agent shutdown."""
        test_agent.initialize()
        test_agent.start()
        test_agent.shutdown()
        
        assert not test_agent._running
        assert test_agent._shutdown
    
    def test_agent_position_update(self, test_agent):
        """Test agent position update."""
        new_pos = Position(5.0, 10.0, 0.0)
        test_agent.agent_data.position = new_pos
        
        assert test_agent.agent_data.position.x == 5.0
        assert test_agent.agent_data.position.y == 10.0
    
    def test_agent_status_update(self, test_agent):
        """Test agent status update."""
        test_agent.agent_data.status = AgentStatus.MOVING
        assert test_agent.agent_data.status == AgentStatus.MOVING
        
        test_agent.agent_data.status = AgentStatus.INTERACTING
        assert test_agent.agent_data.status == AgentStatus.INTERACTING
    
    def test_agent_energy_management(self, test_agent):
        """Test agent energy management."""
        initial_energy = test_agent.agent_data.resources.energy
        
        # Consume energy
        test_agent.agent_data.resources.consume_energy(30.0)
        assert test_agent.agent_data.resources.energy == initial_energy - 30.0
        
        # Check insufficient energy
        assert not test_agent.agent_data.resources.has_sufficient_energy(100.0)
        assert test_agent.agent_data.resources.has_sufficient_energy(50.0)
    
    def test_agent_goal_management(self, test_agent):
        """Test agent goal management."""
        goal = AgentGoal(
            description="Find food",
            priority=0.8,
            target_position=Position(10.0, 10.0, 0.0)
        )
        
        test_agent.agent_data.goals.append(goal)
        test_agent.agent_data.current_goal = goal
        
        assert len(test_agent.agent_data.goals) == 1
        assert test_agent.agent_data.current_goal == goal
        assert test_agent.agent_data.current_goal.priority == 0.8
    
    def test_agent_perception_integration(self, test_agent, mock_world_interface):
        """Test agent perception system integration."""
        test_agent.initialize()
        
        # Mock world state
        mock_world_interface.get_entities_in_radius.return_value = [
            {"type": "food", "position": Position(5.0, 5.0, 0.0)},
            {"type": "agent", "position": Position(10.0, 10.0, 0.0)}
        ]
        
        # Update perception
        test_agent._update_perception(0.1)
        
        # Verify perception was called
        mock_world_interface.get_entities_in_radius.assert_called()
    
    def test_agent_memory_integration(self, test_agent):
        """Test agent memory system integration."""
        test_agent.initialize()
        
        # Store experience
        experience = {
            "timestamp": datetime.now(),
            "type": "observation",
            "data": {"object": "food", "position": Position(5.0, 5.0, 0.0)}
        }
        
        test_agent.agent_data.short_term_memory.append(experience)
        assert len(test_agent.agent_data.short_term_memory) == 1
    
    def test_agent_behavior_execution(self, test_agent):
        """Test agent behavior execution."""
        test_agent.initialize()
        test_agent.start()
        
        # Set a simple goal
        goal = AgentGoal(description="Move to target", target_position=Position(10.0, 10.0, 0.0))
        test_agent.agent_data.current_goal = goal
        
        # Execute behavior update
        test_agent._update_behavior(0.1)
        
        # Should have attempted to execute behavior
        assert test_agent.agent_data.status in [AgentStatus.IDLE, AgentStatus.MOVING, AgentStatus.PLANNING]
    
    def test_agent_event_handling(self, test_agent, mock_logger):
        """Test agent event handling."""
        test_agent.initialize()
        
        # Trigger an event
        test_agent._handle_event("collision", {"object": "wall", "position": Position(1.0, 1.0, 0.0)})
        
        # Should have logged the event
        mock_logger.log_info.assert_called()
    
    def test_agent_serialization(self, test_agent):
        """Test agent state serialization."""
        test_agent.initialize()
        
        # Set some state
        test_agent.agent_data.position = Position(5.0, 10.0, 0.0)
        test_agent.agent_data.resources.energy = 75.0
        
        # Get agent state
        state = test_agent.get_state()
        
        assert state is not None
        assert "agent_id" in state
        assert state["agent_id"] == "test-agent"
    
    def test_agent_active_inference_integration(self, agent_data, mock_world_interface):
        """Test agent with active inference integration."""
        mock_ai_interface = Mock(spec=IActiveInferenceInterface)
        mock_ai_interface.update_beliefs.return_value = np.array([0.25, 0.25, 0.25, 0.25])
        
        agent = BaseAgent(
            agent_data=agent_data,
            world_interface=mock_world_interface,
            active_inference_interface=mock_ai_interface
        )
        
        agent.initialize()
        agent.update(0.1)
        
        # Should have updated beliefs
        mock_ai_interface.update_beliefs.assert_called()
    
    def test_agent_markov_blanket_integration(self, agent_data, mock_world_interface):
        """Test agent with Markov blanket integration."""
        mock_mb_interface = Mock(spec=IMarkovBlanketInterface)
        mock_mb_interface.get_boundary_state.return_value = {"internal": [], "external": []}
        
        agent = BaseAgent(
            agent_data=agent_data,
            world_interface=mock_world_interface,
            markov_blanket_interface=mock_mb_interface
        )
        
        agent.initialize()
        agent.update(0.1)
        
        # Should have checked boundary
        mock_mb_interface.get_boundary_state.assert_called()


class TestAgentPerformance:
    """Test agent performance characteristics."""
    
    def test_agent_update_performance(self, agent_data, mock_world_interface):
        """Test agent update performance."""
        import time
        
        agent = BaseAgent(
            agent_data=agent_data,
            world_interface=mock_world_interface
        )
        agent.initialize()
        
        # Measure update time
        start = time.time()
        for _ in range(100):
            agent.update(0.01)
        elapsed = time.time() - start
        
        # Should complete 100 updates in reasonable time
        assert elapsed < 1.0  # Less than 1 second for 100 updates
    
    def test_agent_memory_efficiency(self, agent_data, mock_world_interface):
        """Test agent memory efficiency."""
        agent = BaseAgent(
            agent_data=agent_data,
            world_interface=mock_world_interface
        )
        agent.initialize()
        
        # Add many memories
        for i in range(1000):
            memory = {"index": i, "data": f"memory_{i}"}
            agent.agent_data.short_term_memory.append(memory)
        
        # Should handle large memory without issues
        assert len(agent.agent_data.short_term_memory) == 1000
    
    def test_multiple_agents_coordination(self, mock_world_interface):
        """Test multiple agents coordination."""
        agents = []
        
        # Create multiple agents
        for i in range(10):
            agent_data = AgentData(
                agent_id=f"agent-{i}",
                name=f"Agent{i}",
                position=Position(i * 10.0, i * 10.0, 0.0)
            )
            agent = BaseAgent(
                agent_data=agent_data,
                world_interface=mock_world_interface
            )
            agent.initialize()
            agents.append(agent)
        
        # Update all agents
        for agent in agents:
            agent.update(0.1)
        
        # All agents should have updated successfully
        assert len(agents) == 10
        for agent in agents:
            assert agent._initialized