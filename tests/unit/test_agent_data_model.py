"""
Unit tests for Agent Data Model
"""
import unittest
import numpy as np
from datetime import datetime, timedelta
from .......agents.base.data-model import Agent, Position, Orientation, AgentStatus, AgentCapability, AgentPersonality, AgentResources, SocialRelationship, AgentGoal, ResourceAgent, SocialAgent

class TestPosition(unittest.TestCase):
    """Test Position class"""

    def test_position_creation(self):
        """Test position creation with default and custom values"""
        pos1 = Position(1.0, 2.0)
        self.assertEqual(pos1.x, 1.0)
        self.assertEqual(pos1.y, 2.0)
        self.assertEqual(pos1.z, 0.0)
        pos2 = Position(1.0, 2.0, 3.0)
        self.assertEqual(pos2.z, 3.0)

    def test_position_to_array(self):
        """Test conversion to numpy array"""
        pos = Position(1.0, 2.0, 3.0)
        arr = pos.to_array()
        np.testing.assert_array_equal(arr, np.array([1.0, 2.0, 3.0]))

    def test_distance_calculation(self):
        """Test distance calculation between positions"""
        pos1 = Position(0.0, 0.0, 0.0)
        pos2 = Position(3.0, 4.0, 0.0)
        self.assertAlmostEqual(pos1.distance_to(pos2), 5.0)
        pos3 = Position(1.0, 1.0, 1.0)
        pos4 = Position(2.0, 2.0, 2.0)
        expected_distance = np.sqrt(3)
        self.assertAlmostEqual(pos3.distance_to(pos4), expected_distance)

class TestOrientation(unittest.TestCase):
    """Test Orientation class"""

    def test_orientation_creation(self):
        """Test orientation creation with default quaternion"""
        orient = Orientation()
        self.assertEqual(orient.w, 1.0)
        self.assertEqual(orient.x, 0.0)
        self.assertEqual(orient.y, 0.0)
        self.assertEqual(orient.z, 0.0)

    def test_orientation_to_euler(self):
        """Test quaternion to Euler angle conversion"""
        orient = Orientation()
        roll, pitch, yaw = orient.to_euler()
        self.assertAlmostEqual(roll, 0.0)
        self.assertAlmostEqual(pitch, 0.0)
        self.assertAlmostEqual(yaw, 0.0)

class TestAgentPersonality(unittest.TestCase):
    """Test AgentPersonality class"""

    def test_personality_creation(self):
        """Test personality creation with default values"""
        personality = AgentPersonality()
        self.assertEqual(personality.openness, 0.5)
        self.assertEqual(personality.conscientiousness, 0.5)
        self.assertEqual(personality.extraversion, 0.5)
        self.assertEqual(personality.agreeableness, 0.5)
        self.assertEqual(personality.neuroticism, 0.5)

    def test_personality_to_vector(self):
        """Test conversion to vector for GNN processing"""
        personality = AgentPersonality(openness=0.8, conscientiousness=0.6, extraversion=0.7, agreeableness=0.9, neuroticism=0.3)
        vec = personality.to_vector()
        expected = np.array([0.8, 0.6, 0.7, 0.9, 0.3])
        np.testing.assert_array_equal(vec, expected)

    def test_personality_validation(self):
        """Test personality trait validation"""
        valid_personality = AgentPersonality()
        self.assertTrue(valid_personality.validate())
        invalid_personality = AgentPersonality()
        invalid_personality.openness = 1.5
        self.assertFalse(invalid_personality.validate())

class TestAgentResources(unittest.TestCase):
    """Test AgentResources class"""

    def test_resources_creation(self):
        """Test resources creation with default values"""
        resources = AgentResources()
        self.assertEqual(resources.energy, 100.0)
        self.assertEqual(resources.health, 100.0)
        self.assertEqual(resources.memory_capacity, 100.0)
        self.assertEqual(resources.memory_used, 0.0)

    def test_energy_management(self):
        """Test energy consumption and restoration"""
        resources = AgentResources()
        resources.consume_energy(30.0)
        self.assertEqual(resources.energy, 70.0)
        resources.consume_energy(80.0)
        self.assertEqual(resources.energy, 0.0)
        resources.restore_energy(50.0)
        self.assertEqual(resources.energy, 50.0)
        resources.restore_energy(60.0)
        self.assertEqual(resources.energy, 100.0)

    def test_sufficient_energy_check(self):
        """Test energy sufficiency check"""
        resources = AgentResources(energy=50.0)
        self.assertTrue(resources.has_sufficient_energy(30.0))
        self.assertFalse(resources.has_sufficient_energy(60.0))

class TestSocialRelationship(unittest.TestCase):
    """Test SocialRelationship class"""

    def test_relationship_creation(self):
        """Test relationship creation"""
        rel = SocialRelationship(target_agent_id='agent_123', relationship_type='friend')
        self.assertEqual(rel.target_agent_id, 'agent_123')
        self.assertEqual(rel.relationship_type, 'friend')
        self.assertEqual(rel.trust_level, 0.5)
        self.assertEqual(rel.interaction_count, 0)
        self.assertIsNone(rel.last_interaction)

    def test_trust_update(self):
        """Test trust level updates"""
        rel = SocialRelationship(target_agent_id='agent_123', relationship_type='neutral')
        rel.update_trust(0.3)
        self.assertAlmostEqual(rel.trust_level, 0.8)
        rel.update_trust(0.5)
        self.assertEqual(rel.trust_level, 1.0)
        rel.update_trust(-0.7)
        self.assertAlmostEqual(rel.trust_level, 0.3)
        rel.update_trust(-0.5)
        self.assertEqual(rel.trust_level, 0.0)

class TestAgentGoal(unittest.TestCase):
    """Test AgentGoal class"""

    def test_goal_creation(self):
        """Test goal creation with defaults"""
        goal = AgentGoal(description='Find food')
        self.assertIsNotNone(goal.goal_id)
        self.assertEqual(goal.description, 'Find food')
        self.assertEqual(goal.priority, 0.5)
        self.assertFalse(goal.completed)
        self.assertEqual(goal.progress, 0.0)

    def test_goal_expiration(self):
        """Test goal expiration check"""
        goal1 = AgentGoal(description='Explore')
        self.assertFalse(goal1.is_expired())
        future_deadline = datetime.now() + timedelta(hours=1)
        goal2 = AgentGoal(description='Time-sensitive task', deadline=future_deadline)
        self.assertFalse(goal2.is_expired())
        past_deadline = datetime.now() - timedelta(hours=1)
        goal3 = AgentGoal(description='Expired task', deadline=past_deadline)
        self.assertTrue(goal3.is_expired())

class TestAgent(unittest.TestCase):
    """Test Agent class"""

    def test_agent_creation(self):
        """Test agent creation with defaults"""
        agent = Agent()
        self.assertIsNotNone(agent.agent_id)
        self.assertEqual(agent.name, 'Agent')
        self.assertEqual(agent.agent_type, 'basic')
        self.assertEqual(agent.status, AgentStatus.IDLE)
        self.assertIsInstance(agent.position, Position)
        self.assertIsInstance(agent.personality, AgentPersonality)
        self.assertIsInstance(agent.resources, AgentResources)

    def test_capability_management(self):
        """Test capability addition and removal"""
        agent = Agent()
        self.assertTrue(agent.has_capability(AgentCapability.MOVEMENT))
        self.assertTrue(agent.has_capability(AgentCapability.PERCEPTION))
        agent.add_capability(AgentCapability.RESOURCE_MANAGEMENT)
        self.assertTrue(agent.has_capability(AgentCapability.RESOURCE_MANAGEMENT))
        agent.remove_capability(AgentCapability.MOVEMENT)
        self.assertFalse(agent.has_capability(AgentCapability.MOVEMENT))

    def test_relationship_management(self):
        """Test relationship addition and retrieval"""
        agent = Agent()
        rel = SocialRelationship(target_agent_id='agent_456', relationship_type='ally', trust_level=0.8)
        agent.add_relationship(rel)
        retrieved = agent.get_relationship('agent_456')
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.relationship_type, 'ally')
        self.assertEqual(retrieved.trust_level, 0.8)
        self.assertIsNone(agent.get_relationship('non_existent'))

    def test_goal_management(self):
        """Test goal addition and selection"""
        agent = Agent()
        goal1 = AgentGoal(description='Low priority', priority=0.3)
        goal2 = AgentGoal(description='High priority', priority=0.9)
        goal3 = AgentGoal(description='Medium priority', priority=0.6)
        agent.add_goal(goal1)
        agent.add_goal(goal2)
        agent.add_goal(goal3)
        self.assertEqual(agent.goals[0].priority, 0.9)
        self.assertEqual(agent.goals[1].priority, 0.6)
        self.assertEqual(agent.goals[2].priority, 0.3)
        next_goal = agent.select_next_goal()
        self.assertIsNotNone(next_goal)
        self.assertEqual(next_goal.description, 'High priority')
        self.assertEqual(agent.current_goal, next_goal)

    def test_memory_management(self):
        """Test memory addition and management"""
        agent = Agent()
        experience1 = {'event': 'saw_food', 'location': Position(5, 5)}
        agent.add_to_memory(experience1)
        self.assertEqual(len(agent.short_term_memory), 1)
        self.assertEqual(agent.experience_count, 1)
        experience2 = {'event': 'found_treasure', 'value': 1000}
        agent.add_to_memory(experience2, is_important=True)
        self.assertEqual(len(agent.short_term_memory), 2)
        self.assertEqual(len(agent.long_term_memory), 1)
        self.assertEqual(agent.experience_count, 2)
        for i in range(110):
            agent.add_to_memory({'event': f'event_{i}'})
        self.assertLessEqual(len(agent.short_term_memory), 100)

    def test_position_and_status_updates(self):
        """Test position and status updates"""
        agent = Agent()
        initial_time = agent.last_updated
        new_position = Position(10.0, 20.0, 5.0)
        agent.update_position(new_position)
        self.assertEqual(agent.position, new_position)
        self.assertGreater(agent.last_updated, initial_time)
        agent.update_status(AgentStatus.MOVING)
        self.assertEqual(agent.status, AgentStatus.MOVING)

    def test_serialization(self):
        """Test agent serialization and deserialization"""
        agent = Agent(name='TestAgent')
        agent.personality.openness = 0.8
        agent.resources.energy = 75.0
        goal = AgentGoal(description='Test goal', priority=0.7)
        agent.add_goal(goal)
        rel = SocialRelationship(target_agent_id='friend_123', relationship_type='friend', trust_level=0.9)
        agent.add_relationship(rel)
        agent_dict = agent.to_dict()
        restored_agent = Agent.from_dict(agent_dict)
        self.assertEqual(restored_agent.name, 'TestAgent')
        self.assertEqual(restored_agent.personality.openness, 0.8)
        self.assertEqual(restored_agent.resources.energy, 75.0)
        self.assertEqual(len(restored_agent.goals), 1)
        self.assertEqual(restored_agent.goals[0].description, 'Test goal')
        self.assertIn('friend_123', restored_agent.relationships)

class TestSpecializedAgents(unittest.TestCase):
    """Test specialized agent types"""

    def test_resource_agent(self):
        """Test ResourceAgent specialization"""
        agent = ResourceAgent()
        self.assertEqual(agent.specialization, 'resource_management')
        self.assertTrue(agent.has_capability(AgentCapability.RESOURCE_MANAGEMENT))
        self.assertTrue(agent.has_specialized_capability('trading'))
        self.assertTrue(agent.has_specialized_capability('resource_optimization'))
        self.assertEqual(agent.resource_efficiency, 1.0)
        self.assertIsInstance(agent.managed_resources, dict)
        self.assertIsInstance(agent.trading_history, list)

    def test_social_agent(self):
        """Test SocialAgent specialization"""
        agent = SocialAgent()
        self.assertEqual(agent.specialization, 'social_interaction')
        self.assertTrue(agent.has_capability(AgentCapability.SOCIAL_INTERACTION))
        self.assertTrue(agent.has_specialized_capability('negotiation'))
        self.assertTrue(agent.has_specialized_capability('coalition_formation'))
        self.assertTrue(agent.has_specialized_capability('influence'))
        self.assertEqual(agent.influence_radius, 10.0)
        self.assertEqual(agent.reputation, 0.5)
        self.assertEqual(agent.communication_style, 'neutral')
if __name__ == '__main__':
    unittest.main()