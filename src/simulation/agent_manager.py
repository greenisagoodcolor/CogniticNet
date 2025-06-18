"""
Agent Manager - Manages agent lifecycle and operations
Enhanced with state management and advanced querying capabilities
"""
from typing import List, Optional, Dict, Set, Tuple, Any
from uuid import UUID
from datetime import datetime
import math
from ..models.agent import Agent, AgentCreate, AgentUpdate, Position, KnowledgeEntry
import logging

logger = logging.getLogger(__name__)


class SimulationState:
    """Manages the overall simulation state"""
    
    def __init__(self):
        self.agents: Dict[UUID, Agent] = {}
        self.resources: Dict[Tuple[int, int], int] = {}  # Position -> resource count
        self.tick: int = 0
        self.grid_width: int = 20
        self.grid_height: int = 20
        self.conversations: Set[UUID] = set()  # Track active conversations
    
    def add_agent(self, agent: Agent) -> Agent:
        """Add an agent to the simulation state"""
        self.agents[agent.id] = agent
        logger.info(f"Added agent {agent.name} (ID: {agent.id}) to simulation")
        return agent
    
    def remove_agent(self, agent_id: UUID) -> bool:
        """Remove an agent from the simulation state"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            del self.agents[agent_id]
            logger.info(f"Removed agent {agent.name} (ID: {agent_id}) from simulation")
            return True
        return False
    
    def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.agents.get(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents in the simulation"""
        return list(self.agents.values())
    
    def increment_tick(self) -> int:
        """Increment the simulation tick"""
        self.tick += 1
        return self.tick
    
    def add_resource(self, position: Tuple[int, int], amount: int = 1) -> None:
        """Add resources at a position"""
        if position in self.resources:
            self.resources[position] += amount
        else:
            self.resources[position] = amount
    
    def get_resources_at(self, position: Tuple[int, int]) -> int:
        """Get resource count at a position"""
        return self.resources.get(position, 0)


class AgentManager:
    """Enhanced agent manager with state management"""
    
    def __init__(self):
        self.state = SimulationState()
    
    def create_agent(self, **kwargs) -> Agent:
        """Create a new agent from keyword arguments or AgentCreate model"""
        if isinstance(kwargs.get('agent_data'), AgentCreate):
            # Handle legacy call with agent_data parameter
            agent_create = kwargs['agent_data']
            agent_dict = agent_create.dict(exclude_unset=True)
        else:
            # Direct keyword arguments
            agent_dict = kwargs
        
        # Create agent with defaults
        agent = Agent(**agent_dict)
        
        # Ensure position is within grid bounds
        if agent.position.x >= self.state.grid_width:
            agent.position.x = self.state.grid_width - 1
        if agent.position.y >= self.state.grid_height:
            agent.position.y = self.state.grid_height - 1
        
        self.state.add_agent(agent)
        return agent
    
    def get_agent(self, agent_id: UUID) -> Optional[Agent]:
        """Get an agent by ID"""
        return self.state.get_agent(agent_id)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all agents"""
        return self.state.get_all_agents()
    
    def update_agent(self, agent_id: UUID, agent_update: AgentUpdate) -> Optional[Agent]:
        """Update an agent"""
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None
        
        update_data = agent_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.utcnow()
        logger.info(f"Updated agent {agent.name} (ID: {agent_id})")
        return agent
    
    def delete_agent(self, agent_id: UUID) -> bool:
        """Delete an agent"""
        return self.state.remove_agent(agent_id)
    
    def update_agent_position(self, agent_id: UUID, position: Dict[str, int]) -> Optional[Agent]:
        """Update an agent's position"""
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None
        
        x, y = position.get('x', 0), position.get('y', 0)
        
        # Validate bounds
        if x >= self.state.grid_width or y >= self.state.grid_height or x < 0 or y < 0:
            raise ValueError(f"Position ({x}, {y}) is outside grid bounds")
        
        agent.position = Position(x=x, y=y)
        agent.updated_at = datetime.utcnow()
        return agent
    
    def get_agents_at_position(self, position: Dict[str, int]) -> List[Agent]:
        """Get all agents at a specific position"""
        x, y = position.get('x', 0), position.get('y', 0)
        return [
            agent for agent in self.state.get_all_agents()
            if agent.position.x == x and agent.position.y == y
        ]
    
    def get_agents_in_radius(self, center: Dict[str, int], radius: float) -> List[Agent]:
        """Get all agents within a radius of a position"""
        cx, cy = center.get('x', 0), center.get('y', 0)
        agents_in_radius = []
        
        for agent in self.state.get_all_agents():
            distance = math.sqrt(
                (agent.position.x - cx) ** 2 + 
                (agent.position.y - cy) ** 2
            )
            if distance <= radius:
                agents_in_radius.append(agent)
        
        return agents_in_radius
    
    def get_autonomous_agents(self) -> List[Agent]:
        """Get all agents with autonomy enabled"""
        return [
            agent for agent in self.state.get_all_agents()
            if agent.autonomy_enabled
        ]
    
    def update_agent_energy(self, agent_id: UUID, delta: int) -> Optional[Agent]:
        """Update an agent's energy by a delta amount"""
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None
        
        new_energy = max(0, min(100, agent.energy + delta))
        agent.energy = new_energy
        agent.updated_at = datetime.utcnow()
        return agent
    
    def update_agent_resources(self, agent_id: UUID, delta: int) -> Optional[Agent]:
        """Update an agent's resources by a delta amount"""
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None
        
        new_resources = max(0, agent.resources + delta)
        agent.resources = new_resources
        agent.updated_at = datetime.utcnow()
        return agent
    
    def add_knowledge_to_agent(self, agent_id: UUID, knowledge: KnowledgeEntry) -> Optional[Agent]:
        """Add a knowledge entry to an agent"""
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None
        
        agent.knowledge.append(knowledge)
        agent.updated_at = datetime.utcnow()
        logger.info(f"Added knowledge '{knowledge.title}' to agent {agent.name}")
        return agent
    
    def get_agents_by_knowledge_tag(self, tag: str) -> List[Agent]:
        """Get all agents that have knowledge with a specific tag"""
        agents_with_tag = []
        for agent in self.state.get_all_agents():
            for knowledge in agent.knowledge:
                if tag in knowledge.tags:
                    agents_with_tag.append(agent)
                    break
        return agents_with_tag
    
    def set_agents.base.communication_status(self, agent_id: UUID, in_conversation: bool) -> Optional[Agent]:
        """Update an agent's conversation status"""
        agent = self.state.get_agent(agent_id)
        if not agent:
            return None
        
        agent.in_conversation = in_conversation
        agent.updated_at = datetime.utcnow()
        
        if in_conversation:
            self.state.conversations.add(agent_id)
        else:
            self.state.conversations.discard(agent_id)
        
        return agent
    
    def get_agents_in_conversation(self) -> List[Agent]:
        """Get all agents currently in conversation"""
        return [
            agent for agent in self.state.get_all_agents()
            if agent.in_conversation
        ]
    
    def find_nearest_agent(self, from_agent_id: UUID, filter_func=None) -> Optional[Agent]:
        """Find the nearest agent to a given agent, optionally filtered"""
        from_agent = self.state.get_agent(from_agent_id)
        if not from_agent:
            return None
        
        nearest_agent = None
        min_distance = float('inf')
        
        for agent in self.state.get_all_agents():
            if agent.id == from_agent_id:
                continue
            
            if filter_func and not filter_func(agent):
                continue
            
            distance = math.sqrt(
                (agent.position.x - from_agent.position.x) ** 2 + 
                (agent.position.y - from_agent.position.y) ** 2
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest_agent = agent
        
        return nearest_agent
    
    def get_simulation_metrics(self) -> Dict[str, Any]:
        """Get metrics about the current simulation state"""
        agents = self.state.get_all_agents()
        
        if not agents:
            return {
                "agent_count": 0,
                "average_energy": 0,
                "average_resources": 0,
                "autonomous_count": 0,
                "conversation_count": 0,
                "knowledge_entries": 0
            }
        
        total_energy = sum(agent.energy for agent in agents)
        total_resources = sum(agent.resources for agent in agents)
        autonomous_count = sum(1 for agent in agents if agent.autonomy_enabled)
        conversation_count = len(self.state.conversations)
        total_knowledge = sum(len(agent.knowledge) for agent in agents)
        
        return {
            "agent_count": len(agents),
            "average_energy": total_energy / len(agents),
            "average_resources": total_resources / len(agents),
            "autonomous_count": autonomous_count,
            "conversation_count": conversation_count,
            "knowledge_entries": total_knowledge,
            "tick": self.state.tick
        } 