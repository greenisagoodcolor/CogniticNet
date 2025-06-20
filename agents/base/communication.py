"""
Agent Conversation System
Inter-agent communication with Active Inference goals.
"""

import uuid
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging
import json

from ..knowledge.knowledge_graph import AgentKnowledgeGraph, BeliefNode
from ..models.validated_models import MessageType

logger = logging.getLogger(__name__)


class ConversationIntent(Enum):
    """Intent behind agent communication."""
    SHARE_DISCOVERY = "share_discovery"
    PROPOSE_TRADE = "propose_trade"
    FORM_ALLIANCE = "form_alliance"
    SEEK_INFORMATION = "seek_information"
    WARN_DANGER = "warn_danger"
    CASUAL_GREETING = "casual_greeting"


@dataclass
class ConversationMessage:
    """Single message in a conversation."""
    id: str
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    content: str
    intent: ConversationIntent
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content,
            "intent": self.intent.value,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ConversationTurn:
    """Represents a turn in the conversation."""
    agent_id: str
    action: str  # "speak", "listen", "think"
    message: Optional[ConversationMessage] = None
    internal_state: Dict[str, Any] = field(default_factory=dict)


class AgentConversation:
    """
    Manages goal-driven conversations between agents.

    Conversations are driven by Active Inference goals where
    agents communicate to reduce uncertainty and achieve objectives.
    """

    def __init__(self,
                 conversation_id: Optional[str] = None,
                 max_turns: int = 10):
        """
        Initialize a conversation.

        Args:
            conversation_id: Unique identifier for the conversation
            max_turns: Maximum number of turns before ending
        """
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.max_turns = max_turns

        self.participants: List[str] = []
        self.messages: List[ConversationMessage] = []
        self.turns: List[ConversationTurn] = []
        self.active = True
        self.start_time = datetime.utcnow()
        self.end_time: Optional[datetime] = None

        # Conversation state
        self.current_speaker: Optional[str] = None
        self.turn_count = 0
        self.conversation_goals: Dict[str, List[str]] = {}  # agent_id -> goals

        logger.info(f"Created conversation {self.conversation_id}")

    def add_participant(self, agent_id: str, goals: List[str] = None):
        """Add an agent to the conversation with their goals."""
        if agent_id not in self.participants:
            self.participants.append(agent_id)
            self.conversation_goals[agent_id] = goals or []
            logger.debug(f"Added participant {agent_id} to conversation")

    def generate_message(self,
                        speaker_id: str,
                        speaker_state: Dict[str, Any],
                        conversation_context: List[ConversationMessage],
                        llm_client = None) -> ConversationMessage:
        """
        Generate a message based on speaker's goals and state.

        Args:
            speaker_id: ID of the speaking agent
            speaker_state: Agent's current state including beliefs and goals
            conversation_context: Recent messages for context
            llm_client: LLM client for natural language generation

        Returns:
            Generated message
        """
        # Determine intent based on speaker's goals
        intent = self._determine_intent(speaker_state)

        # Create message metadata
        metadata = {
            "speaker_goals": self.conversation_goals.get(speaker_id, []),
            "free_energy": speaker_state.get("free_energy", 0),
            "confidence": speaker_state.get("confidence", 0.5)
        }

        # Generate content based on intent
        if llm_client:
            content = self._generate_with_llm(
                speaker_id,
                speaker_state,
                intent,
                conversation_context,
                llm_client
            )
        else:
            content = self._generate_template_message(
                speaker_id,
                speaker_state,
                intent
            )

        # Create message
        message = ConversationMessage(
            id=str(uuid.uuid4()),
            sender_id=speaker_id,
            recipient_id=self._select_recipient(speaker_id, intent),
            content=content,
            intent=intent,
            metadata=metadata
        )

        return message

    def _determine_intent(self, speaker_state: Dict[str, Any]) -> ConversationIntent:
        """Determine conversation intent based on agent state."""
        # Check for urgent needs
        if speaker_state.get("danger_detected", False):
            return ConversationIntent.WARN_DANGER

        # Check resources
        resources = speaker_state.get("resources", {})
        if any(amount < 20 for amount in resources.values()):
            return ConversationIntent.PROPOSE_TRADE

        # Check for discoveries
        recent_discoveries = speaker_state.get("recent_discoveries", [])
        if recent_discoveries:
            return ConversationIntent.SHARE_DISCOVERY

        # Check uncertainty
        uncertainty = speaker_state.get("uncertainty", 0)
        if uncertainty > 0.7:
            return ConversationIntent.SEEK_INFORMATION

        # Check for cooperation needs
        if speaker_state.get("seeking_allies", False):
            return ConversationIntent.FORM_ALLIANCE

        # Default to casual
        return ConversationIntent.CASUAL_GREETING

    def _select_recipient(self,
                         speaker_id: str,
                         intent: ConversationIntent) -> Optional[str]:
        """Select recipient based on intent."""
        other_participants = [p for p in self.participants if p != speaker_id]

        if not other_participants:
            return None

        # For warnings, broadcast to all
        if intent == ConversationIntent.WARN_DANGER:
            return None  # Broadcast

        # For now, select first other participant
        # In full implementation, would use more sophisticated selection
        return other_participants[0]

    def _generate_template_message(self,
                                  speaker_id: str,
                                  speaker_state: Dict[str, Any],
                                  intent: ConversationIntent) -> str:
        """Generate message using templates."""
        templates = {
            ConversationIntent.SHARE_DISCOVERY: [
                "I've discovered something interesting: {discovery}",
                "You might want to know about {discovery}",
                "I found {discovery} at {location}"
            ],
            ConversationIntent.PROPOSE_TRADE: [
                "I need {need}. Would you trade for {offer}?",
                "Looking to exchange {offer} for {need}",
                "Anyone interested in trading? I have {offer}"
            ],
            ConversationIntent.FORM_ALLIANCE: [
                "We should work together",
                "Want to form an alliance?",
                "Together we could achieve more"
            ],
            ConversationIntent.SEEK_INFORMATION: [
                "Do you know anything about {topic}?",
                "I'm looking for information on {topic}",
                "Has anyone seen {topic}?"
            ],
            ConversationIntent.WARN_DANGER: [
                "Warning! {danger} detected at {location}!",
                "Everyone be careful - {danger}!",
                "Danger alert: {danger}"
            ],
            ConversationIntent.CASUAL_GREETING: [
                "Hello there!",
                "How's everyone doing?",
                "Nice to meet you all"
            ]
        }

        # Select template
        import random
        template = random.choice(templates.get(intent, ["Hello"]))

        # Fill in template
        if intent == ConversationIntent.SHARE_DISCOVERY:
            discoveries = speaker_state.get("recent_discoveries", ["something"])
            discovery = discoveries[0] if discoveries else "something"
            location = speaker_state.get("location", "nearby")
            return template.format(discovery=discovery, location=location)
        elif intent == ConversationIntent.PROPOSE_TRADE:
            resources = speaker_state.get("resources", {})
            # Find what's needed and what can be offered
            need = min(resources.items(), key=lambda x: x[1])[0] if resources else "resources"
            offer = max(resources.items(), key=lambda x: x[1])[0] if resources else "items"
            return template.format(need=need, offer=offer)
        elif intent == ConversationIntent.SEEK_INFORMATION:
            topic = speaker_state.get("uncertainty_topics", ["the area"])[0]
            return template.format(topic=topic)
        elif intent == ConversationIntent.WARN_DANGER:
            danger = speaker_state.get("danger_type", "threat")
            location = speaker_state.get("danger_location", "nearby")
            return template.format(danger=danger, location=location)
        else:
            return template

    def _generate_with_llm(self,
                          speaker_id: str,
                          speaker_state: Dict[str, Any],
                          intent: ConversationIntent,
                          conversation_context: List[ConversationMessage],
                          llm_client) -> str:
        """Generate natural language using LLM."""
        # Build prompt
        prompt = self._build_llm_prompt(
            speaker_id,
            speaker_state,
            intent,
            conversation_context
        )

        # Generate response
        try:
            response = llm_client.generate(prompt, max_tokens=100)
            return response.strip()
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Fall back to template
            return self._generate_template_message(speaker_id, speaker_state, intent)

    def _build_llm_prompt(self,
                         speaker_id: str,
                         speaker_state: Dict[str, Any],
                         intent: ConversationIntent,
                         conversation_context: List[ConversationMessage]) -> str:
        """Build prompt for LLM generation."""
        # Agent personality
        personality = speaker_state.get("personality", {})
        traits = ", ".join([f"{k}: {v}" for k, v in personality.items()])

        # Recent context
        context_str = ""
        for msg in conversation_context[-3:]:  # Last 3 messages
            context_str += f"{msg.sender_id}: {msg.content}\n"

        prompt = f"""You are agent {speaker_id} with personality traits: {traits}.

Your current intent is: {intent.value}
Your goals: {', '.join(self.conversation_goals.get(speaker_id, []))}

Recent conversation:
{context_str}

Generate a natural response that:
1. Matches your personality
2. Achieves your intent ({intent.value})
3. Is concise (1-2 sentences)
4. Continues the conversation naturally

Response:"""

        return prompt

    def process_turn(self,
                    agent_id: str,
                    agent_state: Dict[str, Any],
                    llm_client = None) -> ConversationTurn:
        """
        Process a conversation turn for an agent.

        Args:
            agent_id: ID of the agent taking turn
            agent_state: Agent's current state
            llm_client: Optional LLM client

        Returns:
            ConversationTurn with action taken
        """
        if not self.active:
            raise ValueError("Conversation has ended")

        # Determine action (speak, listen, think)
        action = self._determine_action(agent_id, agent_state)

        turn = ConversationTurn(
            agent_id=agent_id,
            action=action,
            internal_state={"free_energy": agent_state.get("free_energy", 0)}
        )

        if action == "speak":
            # Generate and add message
            message = self.generate_message(
                agent_id,
                agent_state,
                self.messages[-5:],  # Last 5 messages for context
                llm_client
            )
            self.add_message(message)
            turn.message = message
            self.current_speaker = agent_id
        elif action == "listen":
            # Record listening state
            turn.internal_state["listening_to"] = self.current_speaker

        self.turns.append(turn)
        self.turn_count += 1

        # Check if conversation should end
        if self.turn_count >= self.max_turns:
            self.end_conversation()

        return turn

    def _determine_action(self,
                         agent_id: str,
                         agent_state: Dict[str, Any]) -> str:
        """Determine what action agent should take."""
        # Simple turn-taking logic
        # In full implementation, would use more sophisticated decision-making

        # If no one has spoken yet, speak
        if not self.messages:
            return "speak"

        # If agent just spoke, listen
        if self.messages and self.messages[-1].sender_id == agent_id:
            return "listen"

        # If agent has something urgent, speak
        if agent_state.get("urgent_message", False):
            return "speak"

        # Otherwise, probabilistically decide
        import random
        return random.choice(["speak", "listen", "think"])

    def add_message(self, message: ConversationMessage):
        """Add a message to the conversation."""
        self.messages.append(message)
        logger.debug(f"Added message from {message.sender_id}: {message.content[:50]}...")

    def update_beliefs_from_message(self,
                                   recipient_id: str,
                                   message: ConversationMessage,
                                   knowledge_graph: AgentKnowledgeGraph) -> List[BeliefNode]:
        """
        Update recipient's beliefs based on received message.

        Args:
            recipient_id: ID of the recipient agent
            message: Received message
            knowledge_graph: Recipient's knowledge graph

        Returns:
            List of updated or new beliefs
        """
        updated_beliefs = []

        # Extract information based on intent
        if message.intent == ConversationIntent.SHARE_DISCOVERY:
            # Create belief about shared discovery
            belief = BeliefNode(
                id="",
                statement=f"Agent {message.sender_id} discovered: {message.content}",
                confidence=0.7,  # Moderate confidence in shared info
                supporting_patterns=[],
                contradicting_patterns=[]
            )
            belief_id = knowledge_graph.add_belief(belief)
            updated_beliefs.append(belief)

        elif message.intent == ConversationIntent.WARN_DANGER:
            # Create high-confidence belief about danger
            belief = BeliefNode(
                id="",
                statement=f"Danger warning: {message.content}",
                confidence=0.9,  # High confidence in warnings
                supporting_patterns=[],
                contradicting_patterns=[]
            )
            belief_id = knowledge_graph.add_belief(belief)
            updated_beliefs.append(belief)

        elif message.intent == ConversationIntent.PROPOSE_TRADE:
            # Create belief about trade opportunity
            belief = BeliefNode(
                id="",
                statement=f"Trade opportunity with {message.sender_id}: {message.content}",
                confidence=0.6,
                supporting_patterns=[],
                contradicting_patterns=[]
            )
            belief_id = knowledge_graph.add_belief(belief)
            updated_beliefs.append(belief)

        # Update trust/relationship beliefs
        trust_belief = BeliefNode(
            id="",
            statement=f"Agent {message.sender_id} communicated with intent {message.intent.value}",
            confidence=0.8,
            supporting_patterns=[],
            contradicting_patterns=[]
        )
        knowledge_graph.add_belief(trust_belief)
        updated_beliefs.append(trust_belief)

        return updated_beliefs

    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the conversation."""
        intent_counts = {}
        for msg in self.messages:
            intent = msg.intent.value
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "message_count": len(self.messages),
            "turn_count": self.turn_count,
            "duration": (self.end_time or datetime.utcnow() - self.start_time).total_seconds(),
            "active": self.active,
            "intent_distribution": intent_counts,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None
        }

    def end_conversation(self):
        """End the conversation."""
        self.active = False
        self.end_time = datetime.utcnow()
        logger.info(f"Ended conversation {self.conversation_id}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary."""
        return {
            "conversation_id": self.conversation_id,
            "participants": self.participants,
            "messages": [msg.to_dict() for msg in self.messages],
            "summary": self.get_conversation_summary()
        }


class ConversationManager:
    """Manages multiple ongoing conversations."""

    def __init__(self):
        self.conversations: Dict[str, AgentConversation] = {}
        self.agents.base.communications: Dict[str, List[str]] = {}  # agent_id -> conversation_ids

    def create_conversation(self,
                           participants: List[str],
                           goals: Dict[str, List[str]] = None) -> AgentConversation:
        """Create a new conversation."""
        conversation = AgentConversation()

        for participant in participants:
            conversation.add_participant(
                participant,
                goals.get(participant, []) if goals else []
            )

            # Track agent's conversations
            if participant not in self.agents.base.communications:
                self.agents.base.communications[participant] = []
            self.agents.base.communications[participant].append(conversation.conversation_id)

        self.conversations[conversation.conversation_id] = conversation
        return conversation

    def get_agents.base.communications(self, agent_id: str) -> List[AgentConversation]:
        """Get all conversations an agent is participating in."""
        conversation_ids = self.agents.base.communications.get(agent_id, [])
        return [
            self.conversations[cid]
            for cid in conversation_ids
            if cid in self.conversations
        ]

    def get_active_conversations(self) -> List[AgentConversation]:
        """Get all active conversations."""
        return [
            conv for conv in self.conversations.values()
            if conv.active
        ]


# Example usage
if __name__ == "__main__":
    # Create conversation manager
    manager = ConversationManager()

    # Create a conversation between two agents
    conversation = manager.create_conversation(
        participants=["agent_1", "agent_2"],
        goals={
            "agent_1": ["find_food", "share_knowledge"],
            "agent_2": ["find_water", "form_alliance"]
        }
    )

    # Simulate conversation turns
    agent1_state = {
        "resources": {"food": 80, "water": 20},
        "recent_discoveries": ["berry_bush_location"],
        "personality": {"openness": 0.8, "agreeableness": 0.7}
    }

    agent2_state = {
        "resources": {"food": 30, "water": 70},
        "seeking_allies": True,
        "personality": {"openness": 0.6, "agreeableness": 0.8}
    }

    # Process turns
    for i in range(6):
        if i % 2 == 0:
            turn = conversation.process_turn("agent_1", agent1_state)
        else:
            turn = conversation.process_turn("agent_2", agent2_state)

        if turn.message:
            print(f"{turn.agent_id}: {turn.message.content}")

    # Get summary
    summary = conversation.get_conversation_summary()
    print(f"\nConversation summary: {json.dumps(summary, indent=2)}")
