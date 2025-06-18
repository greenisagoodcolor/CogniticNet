"""
Unit tests for Agent Perception System
"""

import unittest
import numpy as np
import math
from datetime import datetime, timedelta
from agents.base.data_model import Agent, Position, Orientation
from agents.base.state_manager import AgentStateManager
from agents.base.perception import (
    PerceptionSystem, PerceptionCapabilities, PerceptionType,
    Stimulus, StimulusType, Percept, PerceptionMemory,
    VisualSensor, AuditorySensor, ProximitySensor,
    ImportanceFilter, AttentionFilter
)


class TestStimulus(unittest.TestCase):
    """Test Stimulus class"""

    def test_stimulus_creation(self):
        """Test creating a stimulus"""
        pos = Position(10.0, 20.0, 0.0)
        stimulus = Stimulus(
            stimulus_id="test_stim",
            stimulus_type=StimulusType.OBJECT,
            position=pos,
            intensity=0.8
        )

        self.assertEqual(stimulus.stimulus_id, "test_stim")
        self.assertEqual(stimulus.stimulus_type, StimulusType.OBJECT)
        self.assertEqual(stimulus.position, pos)
        self.assertEqual(stimulus.intensity, 0.8)

    def test_decay_over_distance(self):
        """Test intensity decay calculation"""
        stimulus = Stimulus(
            stimulus_id="test",
            stimulus_type=StimulusType.SOUND,
            position=Position(0, 0, 0),
            intensity=1.0,
            radius=10.0
        )

        # At source
        self.assertEqual(stimulus.decay_over_distance(0), 1.0)

        # Halfway
        self.assertAlmostEqual(stimulus.decay_over_distance(5), 0.5)

        # At edge
        self.assertEqual(stimulus.decay_over_distance(10), 0.0)

        # Beyond radius
        self.assertEqual(stimulus.decay_over_distance(15), 0.0)


class TestPerceptionCapabilities(unittest.TestCase):
    """Test PerceptionCapabilities"""

    def test_default_capabilities(self):
        """Test default perception capabilities"""
        cap = PerceptionCapabilities()

        self.assertEqual(cap.visual_range, 50.0)
        self.assertAlmostEqual(cap.field_of_view, math.pi * 2/3)
        self.assertEqual(cap.hearing_range, 100.0)
        self.assertIn(PerceptionType.VISUAL, cap.enabled_types)
        self.assertIn(PerceptionType.AUDITORY, cap.enabled_types)

    def test_custom_capabilities(self):
        """Test custom perception capabilities"""
        cap = PerceptionCapabilities(
            visual_range=30.0,
            hearing_range=150.0,
            enabled_types={PerceptionType.VISUAL}
        )

        self.assertEqual(cap.visual_range, 30.0)
        self.assertEqual(cap.hearing_range, 150.0)
        self.assertEqual(len(cap.enabled_types), 1)


class TestPerceptionMemory(unittest.TestCase):
    """Test PerceptionMemory"""

    def test_memory_storage(self):
        """Test storing percepts in memory"""
        memory = PerceptionMemory(memory_duration=5.0)

        stimulus = Stimulus("test", StimulusType.OBJECT, Position(0, 0, 0))
        percept = Percept(stimulus, PerceptionType.VISUAL)

        memory.add_percept(percept)

        recent = memory.get_recent_percepts()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0], percept)

    def test_memory_duration(self):
        """Test memory duration filtering"""
        memory = PerceptionMemory(memory_duration=1.0)

        # Add old percept
        old_stimulus = Stimulus("old", StimulusType.OBJECT, Position(0, 0, 0))
        old_percept = Percept(old_stimulus, PerceptionType.VISUAL)
        old_percept.timestamp = datetime.now() - timedelta(seconds=2)
        memory.add_percept(old_percept)

        # Add recent percept
        new_stimulus = Stimulus("new", StimulusType.OBJECT, Position(0, 0, 0))
        new_percept = Percept(new_stimulus, PerceptionType.VISUAL)
        memory.add_percept(new_percept)

        # Clean old memories
        memory.forget_old_memories()

        recent = memory.get_recent_percepts()
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0].stimulus.stimulus_id, "new")

    def test_stimulus_history(self):
        """Test tracking stimulus history"""
        memory = PerceptionMemory()

        stimulus = Stimulus("tracked", StimulusType.AGENT, Position(0, 0, 0))

        # Add multiple percepts of same stimulus
        for i in range(3):
            percept = Percept(stimulus, PerceptionType.VISUAL, distance=float(i))
            memory.add_percept(percept)

        history = memory.get_stimulus_history("tracked")
        self.assertEqual(len(history), 3)


class TestVisualSensor(unittest.TestCase):
    """Test VisualSensor"""

    def setUp(self):
        """Set up test fixtures"""
        self.sensor = VisualSensor()
        self.agent = Agent(
            name="Observer",
            position=Position(0, 0, 0),
            orientation=Orientation()  # Facing +X direction
        )
        self.agent.perception_capabilities = PerceptionCapabilities()

    def test_visual_detection_in_front(self):
        """Test detecting stimulus in front of agent"""
        # Stimulus directly in front
        stimulus = Stimulus(
            "front",
            StimulusType.OBJECT,
            Position(10, 0, 0)
        )

        percepts = self.sensor.sense(self.agent, [stimulus])

        self.assertEqual(len(percepts), 1)
        self.assertEqual(percepts[0].perception_type, PerceptionType.VISUAL)
        self.assertAlmostEqual(percepts[0].distance, 10.0)

    def test_visual_field_of_view(self):
        """Test field of view limitations"""
        # Stimulus behind agent
        behind_stimulus = Stimulus(
            "behind",
            StimulusType.OBJECT,
            Position(-10, 0, 0)
        )

        percepts = self.sensor.sense(self.agent, [behind_stimulus])
        self.assertEqual(len(percepts), 0)  # Should not see behind

        # Stimulus at edge of FOV
        fov_angle = self.agent.perception_capabilities.field_of_view / 2
        edge_x = 10 * math.cos(fov_angle - 0.1)  # Just inside FOV
        edge_y = 10 * math.sin(fov_angle - 0.1)
        edge_stimulus = Stimulus(
            "edge",
            StimulusType.OBJECT,
            Position(edge_x, edge_y, 0)
        )

        edge_percepts = self.sensor.sense(self.agent, [edge_stimulus])
        self.assertEqual(len(edge_percepts), 1)

    def test_visual_range_limit(self):
        """Test visual range limitations"""
        # Stimulus beyond visual range
        far_stimulus = Stimulus(
            "far",
            StimulusType.OBJECT,
            Position(100, 0, 0)  # Beyond default 50.0 range
        )

        percepts = self.sensor.sense(self.agent, [far_stimulus])
        self.assertEqual(len(percepts), 0)

    def test_visual_confidence_decay(self):
        """Test confidence decay with distance"""
        near_stimulus = Stimulus("near", StimulusType.OBJECT, Position(5, 0, 0))
        far_stimulus = Stimulus("far", StimulusType.OBJECT, Position(40, 0, 0))

        percepts = self.sensor.sense(self.agent, [near_stimulus, far_stimulus])

        self.assertEqual(len(percepts), 2)
        near_percept = next(p for p in percepts if p.stimulus.stimulus_id == "near")
        far_percept = next(p for p in percepts if p.stimulus.stimulus_id == "far")

        self.assertGreater(near_percept.confidence, far_percept.confidence)


class TestAuditorySensor(unittest.TestCase):
    """Test AuditorySensor"""

    def setUp(self):
        """Set up test fixtures"""
        self.sensor = AuditorySensor()
        self.agent = Agent(name="Listener", position=Position(0, 0, 0))
        self.agent.perception_capabilities = PerceptionCapabilities()

    def test_sound_detection(self):
        """Test detecting sound stimuli"""
        sound = Stimulus(
            "sound1",
            StimulusType.SOUND,
            Position(20, 0, 0),
            intensity=0.8,
            radius=30.0
        )

        percepts = self.sensor.sense(self.agent, [sound])

        self.assertEqual(len(percepts), 1)
        self.assertEqual(percepts[0].perception_type, PerceptionType.AUDITORY)

    def test_sound_decay(self):
        """Test sound intensity decay"""
        sound = Stimulus(
            "sound",
            StimulusType.SOUND,
            Position(15, 0, 0),
            intensity=1.0,
            radius=20.0
        )

        percepts = self.sensor.sense(self.agent, [sound])

        self.assertEqual(len(percepts), 1)
        # At 15 units distance with 20 unit radius, intensity should be 0.25
        expected_intensity = 1.0 * (1.0 - 15.0/20.0)
        self.assertAlmostEqual(
            percepts[0].metadata["perceived_intensity"],
            expected_intensity
        )

    def test_hearing_range(self):
        """Test hearing range limit"""
        distant_sound = Stimulus(
            "distant",
            StimulusType.SOUND,
            Position(150, 0, 0),  # Beyond 100 unit hearing range
            intensity=1.0
        )

        percepts = self.sensor.sense(self.agent, [distant_sound])
        self.assertEqual(len(percepts), 0)

    def test_non_sound_filtering(self):
        """Test that non-sound stimuli are ignored"""
        visual_stimulus = Stimulus(
            "visual",
            StimulusType.OBJECT,
            Position(10, 0, 0)
        )

        percepts = self.sensor.sense(self.agent, [visual_stimulus])
        self.assertEqual(len(percepts), 0)


class TestProximitySensor(unittest.TestCase):
    """Test ProximitySensor"""

    def setUp(self):
        """Set up test fixtures"""
        self.sensor = ProximitySensor()
        self.agent = Agent(name="Toucher", position=Position(0, 0, 0))
        self.agent.perception_capabilities = PerceptionCapabilities()

    def test_proximity_detection(self):
        """Test detecting nearby stimuli"""
        close_stimulus = Stimulus(
            "close",
            StimulusType.OBJECT,
            Position(2, 0, 0)  # Within 5 unit proximity range
        )

        percepts = self.sensor.sense(self.agent, [close_stimulus])

        self.assertEqual(len(percepts), 1)
        self.assertEqual(percepts[0].perception_type, PerceptionType.PROXIMITY)

    def test_touching_detection(self):
        """Test detecting touching"""
        touching_stimulus = Stimulus(
            "touching",
            StimulusType.OBJECT,
            Position(0.3, 0, 0)  # Very close
        )

        percepts = self.sensor.sense(self.agent, [touching_stimulus])

        self.assertEqual(len(percepts), 1)
        self.assertTrue(percepts[0].metadata["is_touching"])

    def test_proximity_confidence(self):
        """Test proximity confidence based on distance"""
        stim1 = Stimulus("s1", StimulusType.OBJECT, Position(1, 0, 0))
        stim2 = Stimulus("s2", StimulusType.OBJECT, Position(4, 0, 0))

        percepts = self.sensor.sense(self.agent, [stim1, stim2])

        self.assertEqual(len(percepts), 2)
        p1 = next(p for p in percepts if p.stimulus.stimulus_id == "s1")
        p2 = next(p for p in percepts if p.stimulus.stimulus_id == "s2")

        self.assertGreater(p1.confidence, p2.confidence)


class TestPerceptionFilters(unittest.TestCase):
    """Test perception filters"""

    def test_importance_filter(self):
        """Test ImportanceFilter"""
        filter = ImportanceFilter(importance_threshold=0.5)
        agent = Agent()

        # Create percepts with different importance
        danger_stimulus = Stimulus("danger", StimulusType.DANGER, Position(0, 0, 0))
        object_stimulus = Stimulus("object", StimulusType.OBJECT, Position(50, 0, 0))

        percepts = [
            Percept(danger_stimulus, PerceptionType.VISUAL, confidence=0.3, distance=20),
            Percept(object_stimulus, PerceptionType.VISUAL, confidence=0.4, distance=50),
        ]

        filtered = filter.filter(percepts, agent)

        # Danger should pass even with low confidence
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].stimulus.stimulus_type, StimulusType.DANGER)

    def test_attention_filter(self):
        """Test AttentionFilter"""
        filter = AttentionFilter()
        agent = Agent()
        agent.perception_capabilities = PerceptionCapabilities(attention_capacity=3)

        # Create many percepts
        percepts = []
        for i in range(5):
            stim = Stimulus(f"s{i}", StimulusType.OBJECT, Position(i, 0, 0))
            percept = Percept(stim, PerceptionType.VISUAL,
                            confidence=1.0 - i*0.1, distance=float(i))
            percepts.append(percept)

        filtered = filter.filter(percepts, agent)

        # Should keep only top 3
        self.assertEqual(len(filtered), 3)
        # Should be sorted by salience
        self.assertEqual(filtered[0].stimulus.stimulus_id, "s0")


class TestPerceptionSystem(unittest.TestCase):
    """Test the main PerceptionSystem"""

    def setUp(self):
        """Set up test fixtures"""
        self.state_manager = AgentStateManager()
        self.perception_system = PerceptionSystem(self.state_manager)

        # Create test agents
        self.agent1 = Agent(name="Agent1", position=Position(0, 0, 0))
        self.agent2 = Agent(name="Agent2", position=Position(10, 0, 0))

        self.state_manager.register_agent(self.agent1)
        self.state_manager.register_agent(self.agent2)

        self.perception_system.register_agent(self.agent1)
        self.perception_system.register_agent(self.agent2)

    def test_agent_registration(self):
        """Test registering agents with perception system"""
        self.assertIn(self.agent1.agent_id, self.perception_system.perception_capabilities)
        self.assertIn(self.agent1.agent_id, self.perception_system.perception_memories)

    def test_stimulus_management(self):
        """Test adding and removing stimuli"""
        stimulus = Stimulus("test", StimulusType.OBJECT, Position(5, 0, 0))

        self.perception_system.add_stimulus(stimulus)
        self.assertEqual(len(self.perception_system.stimuli), 1)

        self.perception_system.remove_stimulus("test")
        self.assertEqual(len(self.perception_system.stimuli), 0)

    def test_agent_perception(self):
        """Test perceiving other agents"""
        # Update agent positions to create stimuli
        self.perception_system.update_agent_positions()

        # Agent1 should perceive Agent2
        percepts = self.perception_system.perceive(self.agent1.agent_id)

        # Should see the other agent
        agent_percepts = [p for p in percepts
                         if p.stimulus.stimulus_type == StimulusType.AGENT]
        self.assertEqual(len(agent_percepts), 1)

    def test_perceived_agents(self):
        """Test getting perceived agents"""
        self.perception_system.update_agent_positions()

        perceived = self.perception_system.get_perceived_agents(self.agent1.agent_id)

        self.assertEqual(len(perceived), 1)
        self.assertEqual(perceived[0].agent_id, self.agent2.agent_id)

    def test_can_perceive(self):
        """Test checking if one agent can perceive another"""
        # They should see each other (within visual range)
        self.assertTrue(self.perception_system.can_perceive(
            self.agent1.agent_id,
            self.agent2.agent_id,
            PerceptionType.VISUAL
        ))

        # Move agent2 far away
        self.agent2.position = Position(100, 0, 0)
        self.state_manager.update_agent_position(self.agent2.agent_id, self.agent2.position)

        # Now they shouldn't see each other
        self.assertFalse(self.perception_system.can_perceive(
            self.agent1.agent_id,
            self.agent2.agent_id,
            PerceptionType.VISUAL
        ))

    def test_sound_perception(self):
        """Test perceiving sounds"""
        # Create a sound
        sound = self.perception_system.create_sound_stimulus(
            Position(15, 0, 0),
            intensity=1.0,
            radius=20.0
        )
        self.perception_system.add_stimulus(sound)

        # Agent should hear it
        percepts = self.perception_system.perceive(self.agent1.agent_id)
        sound_percepts = [p for p in percepts
                         if p.perception_type == PerceptionType.AUDITORY]

        self.assertEqual(len(sound_percepts), 1)


if __name__ == "__main__":
    unittest.main()
