"""
Unit tests for Agent State Management System
"""

import unittest
import threading
import time
from datetime import datetime
from agents.base.data_model import Agent, AgentStatus, Position
from agents.base.state_manager import (
    AgentStateManager, StateTransitionValidator, StateTransitionError,
    StateEvent, StateEventType, StateObserver, StateCondition, StateMonitor
)


class TestStateObserver(StateObserver):
    """Test observer for tracking state changes"""

    def __init__(self):
        self.events = []

    def on_state_change(self, event: StateEvent) -> None:
        self.events.append(event)


class TestStateTransitionValidator(unittest.TestCase):
    """Test state transition validation"""

    def test_valid_transitions(self):
        """Test valid state transitions"""
        # From IDLE
        self.assertTrue(StateTransitionValidator.is_valid_transition(
            AgentStatus.IDLE, AgentStatus.MOVING
        ))
        self.assertTrue(StateTransitionValidator.is_valid_transition(
            AgentStatus.IDLE, AgentStatus.PLANNING
        ))

        # From MOVING
        self.assertTrue(StateTransitionValidator.is_valid_transition(
            AgentStatus.MOVING, AgentStatus.IDLE
        ))
        self.assertTrue(StateTransitionValidator.is_valid_transition(
            AgentStatus.MOVING, AgentStatus.INTERACTING
        ))

        # Same state is always valid
        self.assertTrue(StateTransitionValidator.is_valid_transition(
            AgentStatus.IDLE, AgentStatus.IDLE
        ))

    def test_invalid_transitions(self):
        """Test invalid state transitions"""
        # Cannot go from OFFLINE to MOVING directly
        self.assertFalse(StateTransitionValidator.is_valid_transition(
            AgentStatus.OFFLINE, AgentStatus.MOVING
        ))

        # Cannot go from ERROR to PLANNING directly
        self.assertFalse(StateTransitionValidator.is_valid_transition(
            AgentStatus.ERROR, AgentStatus.PLANNING
        ))

    def test_get_valid_transitions(self):
        """Test getting valid transitions from a state"""
        valid_from_idle = StateTransitionValidator.get_valid_transitions(AgentStatus.IDLE)
        self.assertIn(AgentStatus.MOVING, valid_from_idle)
        self.assertIn(AgentStatus.PLANNING, valid_from_idle)
        self.assertNotIn(AgentStatus.ERROR, valid_from_idle)


class TestAgentStateManager(unittest.TestCase):
    """Test the main state management system"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = AgentStateManager()
        self.test_agent = Agent(name="TestAgent")
        self.test_observer = TestStateObserver()
        self.state_manager.add_observer(self.test_observer)

    def test_agent_registration(self):
        """Test agent registration and unregistration"""
        # Register agent
        self.state_manager.register_agent(self.test_agent)

        # Check agent is registered
        retrieved = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(retrieved.agent_id, self.test_agent.agent_id)

        # Check initial snapshot was created
        snapshots = self.state_manager.get_state_snapshots(self.test_agent.agent_id)
        self.assertEqual(len(snapshots), 1)

        # Unregister agent
        self.state_manager.unregister_agent(self.test_agent.agent_id)
        self.assertIsNone(self.state_manager.get_agent(self.test_agent.agent_id))

    def test_status_update_valid(self):
        """Test valid status updates"""
        self.state_manager.register_agent(self.test_agent)

        # Update to valid status
        self.state_manager.update_agent_status(
            self.test_agent.agent_id,
            AgentStatus.MOVING
        )

        # Check status was updated
        agent = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(agent.status, AgentStatus.MOVING)

        # Check event was fired
        events = self.test_observer.events
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].event_type, StateEventType.STATUS_CHANGED)
        self.assertEqual(events[0].old_value, AgentStatus.IDLE)
        self.assertEqual(events[0].new_value, AgentStatus.MOVING)

    def test_status_update_invalid(self):
        """Test invalid status updates"""
        self.state_manager.register_agent(self.test_agent)

        # First set to OFFLINE
        self.state_manager.update_agent_status(
            self.test_agent.agent_id,
            AgentStatus.OFFLINE
        )

        # Try invalid transition
        with self.assertRaises(StateTransitionError):
            self.state_manager.update_agent_status(
                self.test_agent.agent_id,
                AgentStatus.MOVING
            )

    def test_status_update_forced(self):
        """Test forced status updates bypass validation"""
        self.state_manager.register_agent(self.test_agent)

        # Set to OFFLINE
        self.state_manager.update_agent_status(
            self.test_agent.agent_id,
            AgentStatus.OFFLINE
        )

        # Force invalid transition
        self.state_manager.update_agent_status(
            self.test_agent.agent_id,
            AgentStatus.MOVING,
            force=True
        )

        agent = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(agent.status, AgentStatus.MOVING)

    def test_position_update(self):
        """Test position updates"""
        self.state_manager.register_agent(self.test_agent)

        new_position = Position(10.0, 20.0, 5.0)
        self.state_manager.update_agent_position(
            self.test_agent.agent_id,
            new_position
        )

        # Check position was updated
        agent = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(agent.position, new_position)

        # Check status changed to MOVING
        self.assertEqual(agent.status, AgentStatus.MOVING)

        # Check events
        events = [e for e in self.test_observer.events
                 if e.event_type == StateEventType.POSITION_UPDATED]
        self.assertEqual(len(events), 1)

    def test_resource_updates(self):
        """Test resource updates"""
        self.state_manager.register_agent(self.test_agent)

        # Consume energy
        self.state_manager.update_agent_resources(
            self.test_agent.agent_id,
            energy_delta=-30.0
        )

        agent = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(agent.resources.energy, 70.0)

        # Restore energy
        self.state_manager.update_agent_resources(
            self.test_agent.agent_id,
            energy_delta=20.0
        )

        agent = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(agent.resources.energy, 90.0)

        # Deplete energy completely
        self.state_manager.update_agent_resources(
            self.test_agent.agent_id,
            energy_delta=-100.0
        )

        agent = self.state_manager.get_agent(self.test_agent.agent_id)
        self.assertEqual(agent.resources.energy, 0.0)
        self.assertEqual(agent.status, AgentStatus.ERROR)

    def test_transition_callbacks(self):
        """Test state transition callbacks"""
        self.state_manager.register_agent(self.test_agent)

        callback_called = False
        callback_agent = None

        def test_callback(agent):
            nonlocal callback_called, callback_agent
            callback_called = True
            callback_agent = agent

        # Register callback
        self.state_manager.register_transition_callback(
            self.test_agent.agent_id,
            AgentStatus.IDLE,
            AgentStatus.MOVING,
            test_callback
        )

        # Trigger transition
        self.state_manager.update_agent_status(
            self.test_agent.agent_id,
            AgentStatus.MOVING
        )

        self.assertTrue(callback_called)
        self.assertEqual(callback_agent.agent_id, self.test_agent.agent_id)

    def test_state_history(self):
        """Test state history tracking"""
        self.state_manager.register_agent(self.test_agent)

        # Perform several updates
        self.state_manager.update_agent_status(
            self.test_agent.agent_id,
            AgentStatus.PLANNING
        )
        self.state_manager.update_agent_position(
            self.test_agent.agent_id,
            Position(5.0, 5.0)
        )
        self.state_manager.update_agent_resources(
            self.test_agent.agent_id,
            energy_delta=-10.0
        )

        # Get all history
        history = self.state_manager.get_state_history()
        self.assertGreaterEqual(len(history), 3)

        # Filter by agent
        agent_history = self.state_manager.get_state_history(
            agent_id=self.test_agent.agent_id
        )
        self.assertTrue(all(e.agent_id == self.test_agent.agent_id
                           for e in agent_history))

        # Filter by event type
        status_history = self.state_manager.get_state_history(
            event_type=StateEventType.STATUS_CHANGED
        )
        self.assertTrue(all(e.event_type == StateEventType.STATUS_CHANGED
                           for e in status_history))

    def test_state_summary(self):
        """Test agent state summary"""
        self.state_manager.register_agent(self.test_agent)

        summary = self.state_manager.get_agent_state_summary(self.test_agent.agent_id)

        self.assertEqual(summary["agent_id"], self.test_agent.agent_id)
        self.assertEqual(summary["name"], "TestAgent")
        self.assertEqual(summary["status"], "idle")
        self.assertEqual(summary["resources"]["energy"], 100.0)
        self.assertIsNone(summary["current_goal"])

    def test_batch_update(self):
        """Test batch state updates"""
        agent1 = Agent(name="Agent1")
        agent2 = Agent(name="Agent2")

        self.state_manager.register_agent(agent1)
        self.state_manager.register_agent(agent2)

        updates = [
            {"type": "status", "agent_id": agent1.agent_id, "value": AgentStatus.MOVING},
            {"type": "position", "agent_id": agent1.agent_id, "value": Position(10, 10)},
            {"type": "status", "agent_id": agent2.agent_id, "value": AgentStatus.PLANNING},
        ]

        self.state_manager.batch_update(updates)

        # Check updates were applied
        self.assertEqual(
            self.state_manager.get_agent(agent1.agent_id).status,
            AgentStatus.MOVING
        )
        self.assertEqual(
            self.state_manager.get_agent(agent2.agent_id).status,
            AgentStatus.PLANNING
        )

    def test_thread_safety(self):
        """Test thread-safe operations"""
        self.state_manager.register_agent(self.test_agent)

        errors = []

        def update_status_loop():
            try:
                for _ in range(50):
                    self.state_manager.update_agent_status(
                        self.test_agent.agent_id,
                        AgentStatus.PLANNING
                    )
                    self.state_manager.update_agent_status(
                        self.test_agent.agent_id,
                        AgentStatus.IDLE
                    )
            except Exception as e:
                errors.append(e)

        def update_position_loop():
            try:
                for i in range(50):
                    self.state_manager.update_agent_position(
                        self.test_agent.agent_id,
                        Position(i, i)
                    )
            except Exception as e:
                errors.append(e)

        # Run concurrent updates
        threads = []
        for _ in range(3):
            t1 = threading.Thread(target=update_status_loop)
            t2 = threading.Thread(target=update_position_loop)
            threads.extend([t1, t2])

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        # Check no errors occurred
        self.assertEqual(len(errors), 0)


class TestStateMonitor(unittest.TestCase):
    """Test state monitoring functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = AgentStateManager()
        self.monitor = StateMonitor(self.state_manager)
        self.test_agent = Agent(name="TestAgent")
        self.state_manager.register_agent(self.test_agent)

    def test_condition_monitoring(self):
        """Test condition monitoring"""
        condition_met = False

        def low_energy_callback(agent, condition):
            nonlocal condition_met
            condition_met = True

        # Add condition for low energy
        low_energy_condition = StateCondition(
            "low_energy",
            lambda agent: agent.resources.energy < 30.0
        )

        self.monitor.add_condition(
            self.test_agent.agent_id,
            low_energy_condition,
            low_energy_callback
        )

        # Start monitoring
        self.monitor.start_monitoring(interval=0.1)

        # Deplete energy
        self.state_manager.update_agent_resources(
            self.test_agent.agent_id,
            energy_delta=-75.0
        )

        # Wait for monitor to detect
        time.sleep(0.2)

        self.assertTrue(condition_met)

        # Stop monitoring
        self.monitor.stop_monitoring()


if __name__ == "__main__":
    unittest.main()
