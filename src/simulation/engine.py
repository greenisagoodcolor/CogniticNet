"""
Simulation Engine - Core simulation loop and state management
Enhanced with H3 GridWorld integration
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging
from ..simulation.agent_manager import AgentManager
from ..world.h3_world import H3World
from ..models.simulation import SimulationConfig, SimulationStatus

logger = logging.getLogger(__name__)


class SimulationEngine:
    """Core simulation engine that manages the simulation loop"""
    
    def __init__(self):
        self.config = SimulationConfig()
        self.agent_manager = AgentManager()
        self.grid_world = GridWorld(
            center_lat=37.7749,
            center_lng=-122.4194,
            resolution=9,
            radius=3  # Larger grid for more space
        )
        
        self.is_running = False
        self.is_paused = False
        self.tick = 0
        self.start_time: Optional[datetime] = None
        self.last_tick_time: Optional[datetime] = None
        
        # Simulation loop task
        self._simulation_task: Optional[asyncio.Task] = None
        
        logger.info("Simulation engine initialized")
    
    def configure(self, config: SimulationConfig) -> None:
        """Update simulation configuration"""
        self.config = config
        logger.info(f"Simulation configured: tick_interval={config.tick_interval}s")
    
    async def start(self) -> Dict[str, Any]:
        """Start the simulation"""
        if self.is_running:
            return {"status": "already_running", "tick": self.tick}
        
        self.is_running = True
        self.is_paused = False
        self.start_time = datetime.utcnow()
        
        # Start the simulation loop
        self._simulation_task = asyncio.create_task(self._simulation_loop())
        
        logger.info("Simulation started")
        return {
            "status": "started",
            "tick": self.tick,
            "start_time": self.start_time.isoformat()
        }
    
    async def stop(self) -> Dict[str, Any]:
        """Stop the simulation"""
        if not self.is_running:
            return {"status": "not_running"}
        
        self.is_running = False
        
        # Cancel the simulation task
        if self._simulation_task:
            self._simulation_task.cancel()
            try:
                await self._simulation_task
            except asyncio.CancelledError:
                pass
        
        logger.info(f"Simulation stopped at tick {self.tick}")
        return {
            "status": "stopped",
            "tick": self.tick,
            "duration": (datetime.utcnow() - self.start_time).total_seconds() if self.start_time else 0
        }
    
    def pause(self) -> Dict[str, Any]:
        """Pause the simulation"""
        if not self.is_running or self.is_paused:
            return {"status": "cannot_pause", "is_running": self.is_running, "is_paused": self.is_paused}
        
        self.is_paused = True
        logger.info(f"Simulation paused at tick {self.tick}")
        return {"status": "paused", "tick": self.tick}
    
    def resume(self) -> Dict[str, Any]:
        """Resume the simulation"""
        if not self.is_running or not self.is_paused:
            return {"status": "cannot_resume", "is_running": self.is_running, "is_paused": self.is_paused}
        
        self.is_paused = False
        logger.info(f"Simulation resumed at tick {self.tick}")
        return {"status": "resumed", "tick": self.tick}
    
    def get_status(self) -> SimulationStatus:
        """Get current simulation status"""
        from app.models.simulation import SimulationState
        
        # Determine state
        if not self.is_running:
            state = SimulationState.STOPPED
        elif self.is_paused:
            state = SimulationState.PAUSED
        else:
            state = SimulationState.RUNNING
        
        # Calculate total resources
        total_resources = sum(cell.resources for cell in self.grid_world.cells.values())
        
        # Calculate elapsed time
        elapsed_time = 0.0
        if self.start_time:
            elapsed_time = (datetime.utcnow() - self.start_time).total_seconds()
        
        return SimulationStatus(
            state=state,
            tick=self.tick,
            agent_count=self.get_agent_count(),
            total_resources=total_resources,
            start_time=self.start_time,
            elapsed_time=elapsed_time,
            config=self.config
        )
    
    def get_agent_count(self) -> int:
        """Get the number of agents in the simulation"""
        return len(self.agent_manager.get_all_agents())
    
    async def _simulation_loop(self) -> None:
        """Main simulation loop"""
        tick_interval = self.config.tick_interval
        
        while self.is_running:
            if not self.is_paused:
                try:
                    # Process tick
                    await self._process_tick()
                    self.tick += 1
                    self.last_tick_time = datetime.utcnow()
                except Exception as e:
                    logger.error(f"Error in simulation tick {self.tick}: {e}")
            
            # Wait for next tick
            await asyncio.sleep(tick_interval)
    
    async def _process_tick(self) -> None:
        """Process a single simulation tick"""
        # Update grid world
        grid_updates = self.grid_world.update_tick()
        
        # Process agent behaviors
        agents = self.agent_manager.get_all_agents()
        
        for agent in agents:
            # Skip agents in conversation
            if agent.in_conversation:
                continue
            
            # Basic agent behavior
            await self._process_agent_behavior(agent)
        
        # Log tick info periodically
        if self.tick % 10 == 0:
            metrics = self.agent_manager.get_simulation_metrics()
            logger.debug(
                f"Tick {self.tick}: {metrics['agent_count']} agents, "
                f"avg energy: {metrics['average_energy']:.1f}, "
                f"resources initializeed: {grid_updates['resources_initializeed']}"
            )
    
    async def _process_agent_behavior(self, agent) -> None:
        """Process behavior for a single agent"""
        # Energy decay
        if agent.energy > 0:
            self.agent_manager.update_agent_energy(agent.id, -1)
        
        # If agent has location, try to gather resources
        if agent.location and agent.energy > 20:  # Need energy to gather
            cell = self.grid_world.get_cell(agent.location)
            if cell and cell.resources > 0:
                # Consume resource from cell
                consumed = self.grid_world.consume_resource(agent.location)
                if consumed > 0:
                    # Convert to energy based on resource type
                    energy_gain = {
                        "energy": 10,
                        "food": 8,
                        "water": 5,
                        "minerals": 3
                    }.get(cell.resource_type, 5)
                    
                    self.agent_manager.update_agent_energy(agent.id, energy_gain)
                    self.agent_manager.update_agent_resources(agent.id, consumed)
                    
                    logger.debug(
                        f"Agent {agent.name} consumed {consumed} {cell.resource_type} "
                        f"at {agent.location}, gained {energy_gain} energy"
                    )
        
        # Simple movement behavior
        if agent.location and agent.energy > 10:
            # Random chance to move
            import random
            if random.random() < 0.1:  # 10% chance to move each tick
                neighbors = self.grid_world.get_neighbors(agent.location)
                if neighbors:
                    new_location = random.choice(neighbors)
                    agent.location = new_location
                    agent.updated_at = datetime.utcnow()
                    logger.debug(f"Agent {agent.name} moved to {new_location}")
    
    def reset(self) -> Dict[str, Any]:
        """Reset the simulation to initial state"""
        was_running = self.is_running
        
        # Stop if running
        if was_running:
            asyncio.create_task(self.stop())
        
        # Reset state
        self.tick = 0
        self.start_time = None
        self.last_tick_time = None
        self.is_paused = False
        
        # Reset managers
        self.agent_manager = AgentManager()
        self.grid_world = GridWorld(
            center_lat=self.grid_world.center_lat,
            center_lng=self.grid_world.center_lng,
            resolution=self.grid_world.resolution,
            radius=self.grid_world.radius
        )
        
        logger.info("Simulation reset to initial state")
        return {"status": "reset", "tick": 0}
    
    def get_grid_data(self) -> Dict[str, Any]:
        """Get current grid world data"""
        return self.grid_world.get_grid_data()
    
    def get_visualization_data(self) -> Dict[str, Any]:
        """Get combined data for visualization"""
        grid_viz = self.grid_world.get_visualization_data()
        
        # Add agent positions to visualization
        agents_by_cell = {}
        for agent in self.agent_manager.get_all_agents():
            if agent.location:
                if agent.location not in agents_by_cell:
                    agents_by_cell[agent.location] = []
                agents_by_cell[agent.location].append({
                    "id": str(agent.id),
                    "name": agent.name,
                    "energy": agent.energy,
                    "resources": agent.resources,
                    "color": agent.color,
                    "inConversation": agent.in_conversation
                })
        
        # Merge agent data into cells
        for cell in grid_viz["cells"]:
            cell["agents"] = agents_by_cell.get(cell["id"], [])
        
        return {
            **grid_viz,
            "simulation": {
                "tick": self.tick,
                "isRunning": self.is_running,
                "isPaused": self.is_paused
            }
        } 