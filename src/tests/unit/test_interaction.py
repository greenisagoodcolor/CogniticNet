"""
Unit tests for Agent Interaction System
"""

import pytest
from datetime import datetime, timedelta
import time
import threading

from src.agents.basic_agent.data_model import Agent, Position, AgentPersonality, AgentResources
from src.agents.basic_agent.interaction import (
    InteractionType, MessageType, ResourceType, Message, InteractionRequest,
    InteractionResult, ResourceExchange, CommunicationProtocol, ResourceManager,
    ConflictResolver, InteractionSystem
)


class TestMessage:
    """Test Message class"""

    def test_message_creation(self):
        msg = Message(
            sender_id="agent1",
            receiver_id="agent2",
            message_type=MessageType.REQUEST,
            content={"request": "help"}
        )
        assert msg.sender_id == "agent1"
        assert msg.receiver_id == "agent2"
        assert msg.message_type == MessageType.REQUEST
        assert msg.content == {"request": "help"}
        assert not msg.is_broadcast()

    def test_broadcast_message(self):
        msg = Message(
            sender_id="agent1",
            receiver_id=None,
            message_type=MessageType.INFORM,
            content={"info": "global update"}
        )
        assert msg.is_broadcast()

    def test_message_with_response_deadline(self):
        deadline = datetime.now() + timedelta(seconds=10)
        msg = Message(
            sender_id="agent1",
            receiver_id="agent2",
            requires_response=True,
            response_deadline=deadline
        )
        assert msg.requires_response
        assert msg.response_deadline == deadline


class TestInteractionRequest:
    """Test InteractionRequest class"""

    def test_request_creation(self):
        req = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            interaction_type=InteractionType.COMMUNICATION,
            parameters={"message": "hello"}
        )
        assert req.initiator_id == "agent1"
        assert req.target_id == "agent2"
        assert req.interaction_type == InteractionType.COMMUNICATION
        assert req.parameters == {"message": "hello"}
        assert not req.is_expired()

    def test_request_expiration(self):
        req = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            timeout=0.1
        )
        assert not req.is_expired()
        time.sleep(0.2)
        assert req.is_expired()


class TestResourceExchange:
    """Test ResourceExchange class"""

    def test_exchange_creation(self):
        exchange = ResourceExchange(
            from_agent_id="agent1",
            to_agent_id="agent2",
            resource_type=ResourceType.ENERGY,
            amount=10.0
        )
        assert exchange.from_agent_id == "agent1"
        assert exchange.to_agent_id == "agent2"
        assert exchange.resource_type == ResourceType.ENERGY
        assert exchange.amount == 10.0
        assert not exchange.completed

    def test_exchange_execution_success(self):
        agent1 = Agent(
            id="agent1",
            position=Position(0, 0),
            resources=AgentResources(energy=50.0)
        )
        agent2 = Agent(
            id="agent2",
            position=Position(1, 1),
            resources=AgentResources(energy=30.0)
        )

        exchange = ResourceExchange(
            from_agent_id=agent1.id,
            to_agent_id=agent2.id,
            resource_type=ResourceType.ENERGY,
            amount=20.0
        )

        success = exchange.execute(agent1, agent2)
        assert success
        assert exchange.completed
        assert agent1.resources.energy == 30.0
        assert agent2.resources.energy == 50.0

    def test_exchange_execution_failure(self):
        agent1 = Agent(
            id="agent1",
            position=Position(0, 0),
            resources=AgentResources(energy=10.0)
        )
        agent2 = Agent(
            id="agent2",
            position=Position(1, 1),
            resources=AgentResources(energy=30.0)
        )

        exchange = ResourceExchange(
            from_agent_id=agent1.id,
            to_agent_id=agent2.id,
            resource_type=ResourceType.ENERGY,
            amount=20.0  # More than agent1 has
        )

        success = exchange.execute(agent1, agent2)
        assert not success
        assert not exchange.completed
        assert agent1.resources.energy == 10.0  # Unchanged
        assert agent2.resources.energy == 30.0  # Unchanged


class TestCommunicationProtocol:
    """Test CommunicationProtocol class"""

    def test_send_and_receive_message(self):
        protocol = CommunicationProtocol()

        msg = Message(
            sender_id="agent1",
            receiver_id="agent2",
            content={"text": "hello"}
        )

        success = protocol.send_message(msg)
        assert success

        # Receive for agent2
        messages = protocol.receive_messages("agent2")
        assert len(messages) == 1
        assert messages[0].content == {"text": "hello"}

        # Receive for agent3 (should be empty)
        messages = protocol.receive_messages("agent3")
        assert len(messages) == 0

    def test_broadcast_message(self):
        protocol = CommunicationProtocol()

        broadcast = Message(
            sender_id="agent1",
            receiver_id=None,
            content={"announcement": "global"}
        )

        protocol.send_message(broadcast)

        # All agents should receive broadcast
        messages1 = protocol.receive_messages("agent2")
        messages2 = protocol.receive_messages("agent3")

        assert len(messages1) == 1
        assert len(messages2) == 1
        assert messages1[0].content == {"announcement": "global"}

    def test_conversation_history(self):
        protocol = CommunicationProtocol()

        # Send messages between agent1 and agent2
        msg1 = Message(sender_id="agent1", receiver_id="agent2", content={"text": "hi"})
        msg2 = Message(sender_id="agent2", receiver_id="agent1", content={"text": "hello"})

        protocol.send_message(msg1)
        protocol.send_message(msg2)

        history = protocol.get_conversation_history("agent1", "agent2")
        assert len(history) == 2
        assert history[0].content == {"text": "hi"}
        assert history[1].content == {"text": "hello"}

    def test_pending_responses(self):
        protocol = CommunicationProtocol()

        deadline = datetime.now() + timedelta(seconds=0.1)
        msg = Message(
            sender_id="agent1",
            receiver_id="agent2",
            requires_response=True,
            response_deadline=deadline
        )

        protocol.send_message(msg)

        # Check before timeout
        timed_out = protocol.check_pending_responses()
        assert len(timed_out) == 0

        # Wait for timeout
        time.sleep(0.2)

        # Check after timeout
        timed_out = protocol.check_pending_responses()
        assert len(timed_out) == 1
        assert timed_out[0].id == msg.id


class TestResourceManager:
    """Test ResourceManager class"""

    def test_propose_exchange(self):
        manager = ResourceManager()

        exchange = ResourceExchange(
            from_agent_id="agent1",
            to_agent_id="agent2",
            resource_type=ResourceType.ENERGY,
            amount=10.0
        )

        exchange_id = manager.propose_exchange(exchange)
        assert exchange_id == exchange.id
        assert exchange_id in manager.pending_exchanges

    def test_execute_exchange(self):
        manager = ResourceManager()

        agent1 = Agent(id="agent1", position=Position(0, 0), resources=AgentResources(energy=50.0))
        agent2 = Agent(id="agent2", position=Position(1, 1), resources=AgentResources(energy=30.0))

        exchange = ResourceExchange(
            from_agent_id=agent1.id,
            to_agent_id=agent2.id,
            resource_type=ResourceType.ENERGY,
            amount=20.0
        )

        exchange_id = manager.propose_exchange(exchange)
        success = manager.execute_exchange(exchange_id, agent1, agent2)

        assert success
        assert exchange_id not in manager.pending_exchanges
        assert len(manager.exchange_history) == 1
        assert agent1.resources.energy == 30.0
        assert agent2.resources.energy == 50.0

    def test_cancel_exchange(self):
        manager = ResourceManager()

        exchange = ResourceExchange(
            from_agent_id="agent1",
            to_agent_id="agent2",
            amount=10.0
        )

        exchange_id = manager.propose_exchange(exchange)
        success = manager.cancel_exchange(exchange_id)

        assert success
        assert exchange_id not in manager.pending_exchanges
        assert len(manager.exchange_history) == 0

    def test_exchange_history(self):
        manager = ResourceManager()

        agent1 = Agent(id="agent1", position=Position(0, 0), resources=AgentResources(energy=100.0))
        agent2 = Agent(id="agent2", position=Position(1, 1), resources=AgentResources(energy=50.0))
        agent3 = Agent(id="agent3", position=Position(2, 2), resources=AgentResources(energy=50.0))

        # Exchange 1: agent1 -> agent2
        exchange1 = ResourceExchange(from_agent_id=agent1.id, to_agent_id=agent2.id, amount=10.0)
        id1 = manager.propose_exchange(exchange1)
        manager.execute_exchange(id1, agent1, agent2)

        # Exchange 2: agent2 -> agent3
        exchange2 = ResourceExchange(from_agent_id=agent2.id, to_agent_id=agent3.id, amount=5.0)
        id2 = manager.propose_exchange(exchange2)
        manager.execute_exchange(id2, agent2, agent3)

        # Check histories
        history1 = manager.get_exchange_history("agent1")
        history2 = manager.get_exchange_history("agent2")
        history3 = manager.get_exchange_history("agent3")

        assert len(history1) == 1
        assert len(history2) == 2
        assert len(history3) == 1


class TestConflictResolver:
    """Test ConflictResolver class"""

    def test_resource_conflict_resolution(self):
        resolver = ConflictResolver()

        agent1 = Agent(
            id="agent1",
            position=Position(0, 0),
            priority=2,
            resources=AgentResources(energy=30.0)
        )
        agent2 = Agent(
            id="agent2",
            position=Position(1, 1),
            priority=1,
            resources=AgentResources(energy=50.0)
        )

        resolution = resolver.resolve_resource_conflict(
            agent1, agent2,
            ResourceType.ENERGY,
            100.0
        )

        assert agent1.id in resolution
        assert agent2.id in resolution
        assert resolution[agent1.id] + resolution[agent2.id] == pytest.approx(100.0)

        # Check conflict history
        assert len(resolver.conflict_history) == 1
        assert resolver.conflict_history[0]['type'] == 'resource_conflict'

    def test_spatial_conflict_resolution(self):
        resolver = ConflictResolver()

        disputed_pos = Position(5, 5)

        agent1 = Agent(
            id="agent1",
            position=Position(3, 3),  # Closer
            priority=1,
            resources=AgentResources(energy=50.0)
        )
        agent2 = Agent(
            id="agent2",
            position=Position(8, 8),  # Farther
            priority=2,
            resources=AgentResources(energy=30.0)
        )

        winner = resolver.resolve_spatial_conflict(agent1, agent2, disputed_pos)

        # Agent1 should win (closer + more energy)
        assert winner == agent1.id

        # Check conflict history
        assert len(resolver.conflict_history) == 1
        assert resolver.conflict_history[0]['type'] == 'spatial_conflict'
        assert resolver.conflict_history[0]['winner'] == winner


class TestInteractionSystem:
    """Test InteractionSystem class"""

    def test_agent_registration(self):
        system = InteractionSystem()
        agent = Agent(id="agent1", position=Position(0, 0))

        system.register_agent(agent)
        assert "agent1" in system.registered_agents

        system.unregister_agent("agent1")
        assert "agent1" not in system.registered_agents

    def test_communication_interaction(self):
        system = InteractionSystem()

        request = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            interaction_type=InteractionType.COMMUNICATION,
            parameters={
                'message_type': MessageType.REQUEST,
                'content': {'text': 'help needed'},
                'requires_response': True
            }
        )

        interaction_id = system.initiate_interaction(request)
        result = system.process_interaction(interaction_id)

        assert result.success
        assert 'message_id' in result.outcome

        # Check message was sent
        messages = system.communication.receive_messages("agent2")
        assert len(messages) == 1
        assert messages[0].content == {'text': 'help needed'}

    def test_resource_exchange_interaction(self):
        system = InteractionSystem()

        agent1 = Agent(id="agent1", position=Position(0, 0), resources=AgentResources(energy=100.0))
        agent2 = Agent(id="agent2", position=Position(1, 1), resources=AgentResources(energy=50.0))

        system.register_agent(agent1)
        system.register_agent(agent2)

        request = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            interaction_type=InteractionType.RESOURCE_EXCHANGE,
            parameters={
                'resource_type': ResourceType.ENERGY,
                'amount': 25.0
            }
        )

        interaction_id = system.initiate_interaction(request)
        result = system.process_interaction(interaction_id)

        assert result.success
        assert 'exchange_id' in result.outcome

        # Execute the exchange
        exchange_id = result.outcome['exchange_id']
        success = system.resource_manager.execute_exchange(exchange_id, agent1, agent2)
        assert success
        assert agent1.resources.energy == 75.0
        assert agent2.resources.energy == 75.0

    def test_conflict_interaction(self):
        system = InteractionSystem()

        agent1 = Agent(id="agent1", position=Position(0, 0), priority=2)
        agent2 = Agent(id="agent2", position=Position(1, 1), priority=1)

        system.register_agent(agent1)
        system.register_agent(agent2)

        request = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            interaction_type=InteractionType.CONFLICT,
            parameters={
                'conflict_type': 'resource',
                'resource_type': ResourceType.ENERGY,
                'disputed_amount': 50.0
            }
        )

        interaction_id = system.initiate_interaction(request)
        result = system.process_interaction(interaction_id)

        assert result.success
        assert agent1.id in result.outcome
        assert agent2.id in result.outcome

    def test_interaction_timeout(self):
        system = InteractionSystem()

        request = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            interaction_type=InteractionType.COMMUNICATION,
            timeout=0.1
        )

        interaction_id = system.initiate_interaction(request)
        time.sleep(0.2)

        result = system.process_interaction(interaction_id)
        assert not result.success
        assert result.error_message == "Interaction timed out"

    def test_cleanup_expired_interactions(self):
        system = InteractionSystem()

        # Create multiple interactions with short timeout
        for i in range(3):
            request = InteractionRequest(
                initiator_id=f"agent{i}",
                target_id="target",
                timeout=0.1
            )
            system.initiate_interaction(request)

        assert len(system.active_interactions) == 3

        time.sleep(0.2)
        cleaned = system.cleanup_expired_interactions()

        assert cleaned == 3
        assert len(system.active_interactions) == 0
        assert len(system.interaction_history) == 3

    def test_interaction_callbacks(self):
        system = InteractionSystem()
        callback_called = []

        def test_callback(request):
            callback_called.append(request.id)

        system.register_interaction_callback(InteractionType.COMMUNICATION, test_callback)

        request = InteractionRequest(
            initiator_id="agent1",
            target_id="agent2",
            interaction_type=InteractionType.COMMUNICATION
        )

        system.initiate_interaction(request)

        assert len(callback_called) == 1
        assert callback_called[0] == request.id

    def test_concurrent_interactions(self):
        system = InteractionSystem()
        results = []

        def run_interaction(agent_id):
            request = InteractionRequest(
                initiator_id=agent_id,
                target_id="target",
                interaction_type=InteractionType.COMMUNICATION,
                parameters={'content': {'from': agent_id}}
            )

            interaction_id = system.initiate_interaction(request)
            result = system.process_interaction(interaction_id)
            results.append(result)

        # Run multiple interactions concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=run_interaction, args=(f"agent{i}",))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 10
        assert all(r.success for r in results)
