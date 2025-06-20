"""
Integration Tests for Agent System

Tests the integration of various agent components including:
- Agent creation and initialization
- Movement and world interaction
- Communication between agents
- Knowledge sharing
- Learning and adaptation
"""
import pytest
import asyncio
import json
import time
from pathlib import Path
from typing import List, Dict, Any
import sys
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))
from agents.agent import Agent, AgentClass
from .......world.h3-world import H3World, TerrainType
from communication.message_system import MessageSystem, MessageType
from knowledge.knowledge_graph import KnowledgeGraph
from gnn_processor.parser import GNNParser
from gnn_processor.executor import GNNExecutor

class TestAgentIntegration:
    """Integration tests for agent system."""

    @pytest.fixture
    async def world(self):
        """Create test world."""
        world = H3World(resolution=5)
        for i in range(5):
            world.add_resource(f'8502a{i:02x}ffffffff', 'food', 10)
            world.add_resource(f'8502b{i:02x}ffffffff', 'water', 5)
        return world

    @pytest.fixture
    async def message_system(self):
        """Create message system."""
        return MessageSystem()

    @pytest.fixture
    async def agents(self, world, message_system):
        """Create test agents."""
        agents = []
        agent_configs = [('Explorer1', AgentClass.EXPLORER, (0, 0)), ('Merchant1', AgentClass.MERCHANT, (1, 0)), ('Scholar1', AgentClass.SCHOLAR, (0, 1)), ('Guardian1', AgentClass.GUARDIAN, (1, 1))]
        for name, agent_class, position in agent_configs:
            agent = Agent(agent_id=name.lower(), name=name, agent_class=agent_class, initial_position=position, world=world, message_system=message_system)
            agents.append(agent)
        return agents

    @pytest.mark.asyncio
    async def test_agent_creation_and_initialization(self, agents):
        """Test agent creation and initialization."""
        assert len(agents) == 4
        for agent in agents:
            assert agent.agent_id is not None
            assert agent.name is not None
            assert agent.agent_class in AgentClass
            assert agent.position is not None
            assert agent.resources['energy'] > 0
            assert agent.knowledge_graph is not None
            assert agent.gnn_executor is not None

    @pytest.mark.asyncio
    async def test_agent_movement_and_pathfinding(self, agents, world):
        """Test agent movement and pathfinding."""
        explorer = agents[0]
        initial_pos = explorer.position
        success = await explorer.move('north')
        assert success
        assert explorer.position != initial_pos
        assert explorer.resources['energy'] < 100
        target = world.get_neighbors(explorer.position)[0]
        path = world.find_path(explorer.position, target)
        assert path is not None
        assert len(path) > 0
        assert path[0] == explorer.position
        assert path[-1] == target

    @pytest.mark.asyncio
    async def test_agent_perception_and_observation(self, agents, world):
        """Test agent perception and observation."""
        explorer = agents[0]
        observations = await explorer.perceive()
        assert 'surroundings' in observations
        assert 'nearby_agents' in observations
        assert 'resources' in observations
        assert 'terrain' in observations
        surroundings = observations['surroundings']
        assert len(surroundings) > 0
        for hex_id, info in surroundings.items():
            assert 'terrain' in info
            assert 'resources' in info
            assert 'agents' in info

    @pytest.mark.asyncio
    async def test_agent_communication(self, agents, message_system):
        """Test agent communication."""
        sender = agents[0]
        receiver = agents[1]
        message_content = 'Hello, would you like to trade?'
        success = await sender.send_message(receiver.agent_id, MessageType.TEXT, message_content)
        assert success
        await asyncio.sleep(0.1)
        messages = receiver.get_recent_messages(limit=1)
        assert len(messages) > 0
        assert messages[0].content == message_content
        assert messages[0].sender_id == sender.agent_id

    @pytest.mark.asyncio
    async def test_agent_trading(self, agents):
        """Test trading between agents."""
        merchant = agents[1]
        explorer = agents[0]
        merchant.resources['food'] = 20
        merchant.resources['water'] = 5
        explorer.resources['food'] = 5
        explorer.resources['water'] = 20
        offer = {'offered': {'food': 5}, 'requested': {'water': 5}}
        success = await merchant.send_message(explorer.agent_id, MessageType.TRADE_OFFER, offer)
        assert success
        if await explorer.evaluate_trade(offer):
            merchant.resources['food'] -= offer['offered']['food']
            merchant.resources['water'] += offer['requested']['water']
            explorer.resources['food'] += offer['offered']['food']
            explorer.resources['water'] -= offer['requested']['water']
        assert merchant.resources['food'] == 15
        assert merchant.resources['water'] == 10
        assert explorer.resources['food'] == 10
        assert explorer.resources['water'] == 15

    @pytest.mark.asyncio
    async def test_knowledge_sharing(self, agents):
        """Test knowledge sharing between agents."""
        scholar = agents[2]
        explorer = agents[0]
        knowledge_item = {'type': 'location', 'name': 'resource_rich_area', 'position': '8502a00ffffffff', 'resources': {'food': 50, 'water': 30}}
        scholar.knowledge_graph.add_node('location_1', node_type='location', **knowledge_item)
        shared_knowledge = scholar.prepare_knowledge_for_sharing(['location_1'], explorer.agent_id)
        success = await scholar.send_message(explorer.agent_id, MessageType.KNOWLEDGE_SHARE, shared_knowledge)
        assert success
        await asyncio.sleep(0.1)
        explorer_knowledge = explorer.knowledge_graph.get_node('location_1')
        assert explorer_knowledge is not None

    @pytest.mark.asyncio
    async def test_agent_learning_and_adaptation(self, agents, world):
        """Test agent learning and adaptation."""
        explorer = agents[0]
        initial_exploration_preference = explorer.get_behavior_metric('exploration_preference')
        successful_explorations = 0
        for _ in range(5):
            neighbors = world.get_neighbors(explorer.position)
            if neighbors:
                success = await explorer.move_to(neighbors[0])
                if success:
                    resources = world.get_cell_resources(explorer.position)
                    if resources:
                        successful_explorations += 1
                        explorer.record_experience('exploration_success', {'location': explorer.position, 'resources': resources})
        new_exploration_preference = explorer.get_behavior_metric('exploration_preference')
        if successful_explorations > 2:
            assert new_exploration_preference > initial_exploration_preference

    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, agents, world):
        """Test coordination between multiple agents."""
        target_location = '8502a00ffffffff'
        guardian = agents[3]
        threat_info = {'type': 'environmental_hazard', 'location': target_location, 'severity': 'high', 'required_agents': 3}
        success = await guardian.send_message('broadcast', MessageType.WARNING, threat_info)
        assert success
        responding_agents = []
        for agent in agents[:-1]:
            messages = agent.get_recent_messages(limit=1)
            if messages and messages[0].message_type == MessageType.WARNING:
                if agent.evaluate_threat_response(threat_info):
                    responding_agents.append(agent)
        assert len(responding_agents) >= 2
        coordination_success = 0
        for agent in responding_agents:
            path = world.find_path(agent.position, target_location)
            if path and len(path) <= 5:
                coordination_success += 1
        assert coordination_success >= 1

    @pytest.mark.asyncio
    async def test_resource_management_and_survival(self, agents, world):
        """Test agent resource management and survival mechanics."""
        explorer = agents[0]
        explorer.resources['energy'] = 10
        explorer.resources['food'] = 2
        explorer.resources['water'] = 3
        decision = await explorer.make_decision()
        assert decision['action'] in ['find_resources', 'trade', 'request_help']
        assert decision['priority'] == 'high'
        initial_resources = explorer.resources.copy()
        for _ in range(5):
            explorer.consume_resources()
        assert explorer.resources['food'] < initial_resources['food']
        assert explorer.resources['water'] < initial_resources['water']
        if explorer.resources['food'] < 1 or explorer.resources['water'] < 1:
            assert explorer.status == 'critical'

    @pytest.mark.asyncio
    async def test_knowledge_evolution_and_collective_intelligence(self, agents):
        """Test how knowledge evolves across the agent network."""
        discoveries = [(agents[0], 'pattern_1', {'type': 'resource_pattern', 'confidence': 0.6}), (agents[1], 'pattern_1', {'type': 'resource_pattern', 'confidence': 0.7}), (agents[2], 'pattern_1', {'type': 'resource_pattern', 'confidence': 0.8})]
        for agent, pattern_id, data in discoveries:
            agent.knowledge_graph.add_node(pattern_id, **data)
            for other_agent in agents:
                if other_agent != agent:
                    await agent.send_message(other_agent.agent_id, MessageType.KNOWLEDGE_SHARE, {pattern_id: data})
        await asyncio.sleep(0.2)
        collective_confidence = []
        for agent in agents:
            node = agent.knowledge_graph.get_node('pattern_1')
            if node:
                collective_confidence.append(node.get('confidence', 0))
        avg_confidence = sum(collective_confidence) / len(collective_confidence)
        assert avg_confidence > 0.7

    @pytest.mark.asyncio
    async def test_agent_specialization_and_role_optimization(self, agents):
        """Test how agents optimize for their specialized roles."""
        behaviors = {}
        for agent in agents:
            if agent.agent_class == AgentClass.EXPLORER:
                behaviors[agent.agent_id] = {'explored_cells': 0, 'resources_found': 0}
            elif agent.agent_class == AgentClass.MERCHANT:
                behaviors[agent.agent_id] = {'trades_initiated': 0, 'profit_earned': 0}
            elif agent.agent_class == AgentClass.SCHOLAR:
                behaviors[agent.agent_id] = {'patterns_discovered': 0, 'knowledge_shared': 0}
            elif agent.agent_class == AgentClass.GUARDIAN:
                behaviors[agent.agent_id] = {'threats_detected': 0, 'agents_protected': 0}
        for _ in range(10):
            for agent in agents:
                decision = await agent.make_decision()
                if agent.agent_class == AgentClass.EXPLORER and decision['action'] == 'explore':
                    behaviors[agent.agent_id]['explored_cells'] += 1
                elif agent.agent_class == AgentClass.MERCHANT and decision['action'] == 'trade':
                    behaviors[agent.agent_id]['trades_initiated'] += 1
        explorer_behavior = behaviors[agents[0].agent_id]
        merchant_behavior = behaviors[agents[1].agent_id]
        assert explorer_behavior['explored_cells'] > 5
        assert merchant_behavior['trades_initiated'] > 0

class TestSystemIntegration:
    """Test full system integration."""

    @pytest.mark.asyncio
    async def test_full_simulation_cycle(self):
        """Test a complete simulation cycle."""
        world = H3World(resolution=5)
        message_system = MessageSystem()
        agents = []
        for i in range(4):
            agent = Agent(agent_id=f'agent_{i}', name=f'Agent{i}', agent_class=list(AgentClass)[i % 4], initial_position=(i % 2, i // 2), world=world, message_system=message_system)
            agents.append(agent)
        for cycle in range(10):
            for agent in agents:
                observations = await agent.perceive()
                decision = await agent.make_decision()
                if decision['action'] == 'move':
                    await agent.move(decision['direction'])
                elif decision['action'] == 'communicate':
                    await agent.send_message(decision['recipient'], MessageType.TEXT, decision['message'])
                elif decision['action'] == 'trade':
                    await agent.initiate_trade(decision['partner'], decision['offer'])
                agent.update_knowledge(observations)
                agent.consume_resources()
            world.update(time_delta=1)
        for agent in agents:
            assert agent.is_alive()
            assert len(agent.knowledge_graph.nodes) > 0
            assert agent.experience_count() > 0

    @pytest.mark.asyncio
    async def test_emergent_behaviors(self):
        """Test for emergent behaviors in the system."""
        world = H3World(resolution=5)
        message_system = MessageSystem()
        agents = []
        for i in range(10):
            agent_class = [AgentClass.EXPLORER] * 4 + [AgentClass.MERCHANT] * 3 + [AgentClass.SCHOLAR] * 2 + [AgentClass.GUARDIAN] * 1
            agent = Agent(agent_id=f'agent_{i}', name=f'Agent{i}', agent_class=agent_class[i], initial_position=(i % 5, i // 5), world=world, message_system=message_system)
            agents.append(agent)
        trade_networks = {}
        knowledge_clusters = {}
        exploration_patterns = {}
        for cycle in range(50):
            for agent in agents:
                if agent.agent_class == AgentClass.MERCHANT:
                    trades = agent.get_trade_history()
                    for trade in trades:
                        partner = trade['partner']
                        if agent.agent_id not in trade_networks:
                            trade_networks[agent.agent_id] = set()
                        trade_networks[agent.agent_id].add(partner)
                elif agent.agent_class == AgentClass.SCHOLAR:
                    knowledge = agent.get_knowledge_topics()
                    for topic in knowledge:
                        if topic not in knowledge_clusters:
                            knowledge_clusters[topic] = set()
                        knowledge_clusters[topic].add(agent.agent_id)
                elif agent.agent_class == AgentClass.EXPLORER:
                    path = agent.get_movement_history()
                    if len(path) > 1:
                        pattern = tuple(path[-5:])
                        if pattern not in exploration_patterns:
                            exploration_patterns[pattern] = 0
                        exploration_patterns[pattern] += 1
                await agent.act()
        assert len(trade_networks) > 0
        assert len(knowledge_clusters) > 0
        assert len(exploration_patterns) > 0
        repeated_patterns = [p for p, count in exploration_patterns.items() if count > 2]
        assert len(repeated_patterns) > 0

class TestErrorHandlingAndRecovery:
    """Test error handling and recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_agent_recovery_from_critical_state(self, agents):
        """Test agent recovery from critical resource state."""
        agent = agents[0]
        agent.resources['food'] = 0
        agent.resources['water'] = 1
        agent.resources['energy'] = 5
        recovery_actions = []
        for _ in range(5):
            decision = await agent.make_decision()
            recovery_actions.append(decision['action'])
        resource_actions = ['find_resources', 'trade', 'request_help']
        assert any((action in resource_actions for action in recovery_actions))

    @pytest.mark.asyncio
    async def test_communication_failure_handling(self, agents, message_system):
        """Test handling of communication failures."""
        sender = agents[0]
        message_system.disable()
        success = await sender.send_message(agents[1].agent_id, MessageType.TEXT, 'Test message')
        assert not success
        assert sender.get_failed_communications_count() > 0
        message_system.enable()
        success = await sender.send_message(agents[1].agent_id, MessageType.TEXT, 'Test message retry')
        assert success

    @pytest.mark.asyncio
    async def test_knowledge_corruption_handling(self, agents):
        """Test handling of corrupted knowledge."""
        agent = agents[0]
        agent.knowledge_graph.add_node('corrupted_1', node_type='invalid_type', data={'invalid': None, 'confidence': -1})
        validation_result = agent.validate_knowledge()
        assert not validation_result['valid']
        assert 'corrupted_1' in validation_result['invalid_nodes']
        agent.clean_corrupted_knowledge()
        assert agent.knowledge_graph.get_node('corrupted_1') is None

def run_integration_tests():
    """Run all integration tests."""
    pytest.main([__file__, '-v', '--asyncio-mode=auto'])
