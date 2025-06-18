"""
Runtime Validation System
Second layer of bug prevention with runtime checks for boundaries and message delivery.
"""

import asyncio
from typing import Dict, List, Optional, Tuple, Any, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import logging
from enum import Enum
import uuid
from collections import deque

logger = logging.getLogger(__name__)


class MessageStatus(Enum):
    """Status of a message in the delivery system."""
    PENDING = "pending"
    SENT = "sent"
    ACKNOWLEDGED = "acknowledged"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class QueuedMessage:
    """A message in the delivery queue."""
    id: str
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]
    status: MessageStatus
    created_at: datetime
    attempts: int = 0
    max_attempts: int = 3
    acknowledgment_timeout: timedelta = field(default_factory=lambda: timedelta(seconds=5))
    last_attempt_at: Optional[datetime] = None
    
    def is_expired(self) -> bool:
        """Check if message has expired."""
        if self.last_attempt_at:
            return datetime.utcnow() - self.last_attempt_at > self.acknowledgment_timeout
        return False
        
    def can_retry(self) -> bool:
        """Check if message can be retried."""
        return self.attempts < self.max_attempts and self.status != MessageStatus.ACKNOWLEDGED


class BoundaryValidator:
    """Validates hex boundaries and movement paths."""
    
    def __init__(self, world):
        """
        Initialize boundary validator.
        
        Args:
            world: H3World instance
        """
        self.world = world
        self.valid_hexagons: Set[str] = set(world.hexagons.keys())
        
    def validate_hex_position(self, hex_id: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a hex position is within world boundaries.
        
        Args:
            hex_id: Hex ID to validate
            
        Returns:
            (is_valid, error_message)
        """
        if not hex_id:
            return False, "Hex ID cannot be empty"
            
        if hex_id not in self.valid_hexagons:
            return False, f"Hex {hex_id} is outside world boundaries"
            
        return True, None
        
    def validate_movement_path(self, 
                             path: List[str],
                             check_adjacency: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate a movement path.
        
        Args:
            path: List of hex IDs representing the path
            check_adjacency: Whether to check if consecutive hexes are adjacent
            
        Returns:
            (is_valid, error_message)
        """
        if not path:
            return False, "Path cannot be empty"
            
        # Check all hexes are valid
        for hex_id in path:
            is_valid, error = self.validate_hex_position(hex_id)
            if not is_valid:
                return False, f"Invalid hex in path: {error}"
                
        # Check adjacency if requested
        if check_adjacency and len(path) > 1:
            for i in range(len(path) - 1):
                current = path[i]
                next_hex = path[i + 1]
                
                if not self.is_adjacent(current, next_hex):
                    return False, f"Hexes {current} and {next_hex} are not adjacent"
                    
        return True, None
        
    def is_adjacent(self, hex1: str, hex2: str) -> bool:
        """Check if two hexes are adjacent."""
        neighbors = self.world.get_neighbors(hex1)
        return hex2 in neighbors
        
    def get_valid_moves(self, current_hex: str) -> List[str]:
        """Get list of valid moves from current position."""
        neighbors = self.world.get_neighbors(current_hex)
        return [n for n in neighbors if n in self.valid_hexagons]


class MessageDeliverySystem:
    """
    Reliable message delivery system with queuing and acknowledgments.
    """
    
    def __init__(self):
        """Initialize message delivery system."""
        self.message_queue: deque[QueuedMessage] = deque()
        self.pending_messages: Dict[str, QueuedMessage] = {}
        self.message_handlers: Dict[str, Callable] = {}
        self.acknowledgments: Set[str] = set()
        self.delivery_stats = {
            "total_sent": 0,
            "total_acknowledged": 0,
            "total_failed": 0,
            "total_retries": 0
        }
        
    def register_handler(self, agent_id: str, handler: Callable):
        """Register a message handler for an agent."""
        self.message_handlers[agent_id] = handler
        
    def send_message(self, 
                    sender_id: str,
                    recipient_id: str,
                    content: Dict[str, Any],
                    priority: bool = False) -> str:
        """
        Queue a message for delivery.
        
        Args:
            sender_id: ID of sending agent
            recipient_id: ID of recipient agent
            content: Message content
            priority: Whether this is a priority message
            
        Returns:
            Message ID
        """
        message = QueuedMessage(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            status=MessageStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        if priority:
            self.message_queue.appendleft(message)
        else:
            self.message_queue.append(message)
            
        self.pending_messages[message.id] = message
        
        logger.info(f"Queued message {message.id} from {sender_id} to {recipient_id}")
        return message.id
        
    async def process_messages(self):
        """Process messages in the queue."""
        while self.message_queue:
            message = self.message_queue.popleft()
            
            if message.status == MessageStatus.ACKNOWLEDGED:
                continue
                
            if message.is_expired() and message.can_retry():
                # Retry expired messages
                await self._retry_message(message)
            elif message.status == MessageStatus.PENDING:
                # Attempt delivery
                await self._deliver_message(message)
            elif not message.can_retry():
                # Mark as failed
                message.status = MessageStatus.FAILED
                self.delivery_stats["total_failed"] += 1
                logger.warning(f"Message {message.id} failed after {message.attempts} attempts")
                
    async def _deliver_message(self, message: QueuedMessage):
        """Attempt to deliver a message."""
        try:
            # Check if recipient has a handler
            if message.recipient_id not in self.message_handlers:
                logger.warning(f"No handler for recipient {message.recipient_id}")
                message.status = MessageStatus.FAILED
                self.delivery_stats["total_failed"] += 1
                return
                
            # Deliver message
            handler = self.message_handlers[message.recipient_id]
            message.status = MessageStatus.SENT
            message.last_attempt_at = datetime.utcnow()
            message.attempts += 1
            
            # Call handler (simulating async delivery)
            await asyncio.create_task(handler(message.sender_id, message.content))
            
            self.delivery_stats["total_sent"] += 1
            
            # Wait for acknowledgment (with timeout)
            try:
                await asyncio.wait_for(
                    self._wait_for_acknowledgment(message.id),
                    timeout=message.acknowledgment_timeout.total_seconds()
                )
                message.status = MessageStatus.ACKNOWLEDGED
                self.delivery_stats["total_acknowledged"] += 1
                logger.info(f"Message {message.id} acknowledged")
                
            except asyncio.TimeoutError:
                logger.warning(f"Message {message.id} not acknowledged within timeout")
                if message.can_retry():
                    self.message_queue.append(message)  # Re-queue for retry
                    
        except Exception as e:
            logger.error(f"Error delivering message {message.id}: {e}")
            if message.can_retry():
                self.message_queue.append(message)
            else:
                message.status = MessageStatus.FAILED
                self.delivery_stats["total_failed"] += 1
                
    async def _retry_message(self, message: QueuedMessage):
        """Retry delivering a message."""
        logger.info(f"Retrying message {message.id} (attempt {message.attempts + 1})")
        self.delivery_stats["total_retries"] += 1
        await self._deliver_message(message)
        
    async def _wait_for_acknowledgment(self, message_id: str):
        """Wait for message acknowledgment."""
        while message_id not in self.acknowledgments:
            await asyncio.sleep(0.1)
        self.acknowledgments.remove(message_id)
        
    def acknowledge_message(self, message_id: str):
        """Acknowledge receipt of a message."""
        self.acknowledgments.add(message_id)
        if message_id in self.pending_messages:
            self.pending_messages[message_id].status = MessageStatus.ACKNOWLEDGED
            
    def get_delivery_stats(self) -> Dict[str, Any]:
        """Get message delivery statistics."""
        return {
            **self.delivery_stats,
            "pending_count": len([m for m in self.pending_messages.values() 
                                if m.status == MessageStatus.PENDING]),
            "queue_size": len(self.message_queue)
        }


class EnergyConservationValidator:
    """Validates energy conservation in the system."""
    
    def __init__(self):
        """Initialize energy conservation validator."""
        self.total_system_energy = 0.0
        self.agent_energies: Dict[str, float] = {}
        self.energy_transactions: List[Dict[str, Any]] = []
        
    def register_agent(self, agent_id: str, initial_energy: float):
        """Register an agent with initial energy."""
        self.agent_energies[agent_id] = initial_energy
        self.total_system_energy += initial_energy
        
    def validate_energy_transaction(self,
                                  from_agent: Optional[str],
                                  to_agent: Optional[str],
                                  amount: float) -> Tuple[bool, Optional[str]]:
        """
        Validate an energy transaction.
        
        Args:
            from_agent: Agent losing energy (None for environment)
            to_agent: Agent gaining energy (None for environment)
            amount: Energy amount
            
        Returns:
            (is_valid, error_message)
        """
        # Check agents exist
        if from_agent and from_agent not in self.agent_energies:
            return False, f"Unknown agent: {from_agent}"
        if to_agent and to_agent not in self.agent_energies:
            return False, f"Unknown agent: {to_agent}"
            
        # Check sufficient energy
        if from_agent:
            current_energy = self.agent_energies[from_agent]
            if current_energy < amount:
                return False, f"Insufficient energy: {current_energy} < {amount}"
                
        return True, None
        
    def execute_energy_transaction(self,
                                 from_agent: Optional[str],
                                 to_agent: Optional[str],
                                 amount: float,
                                 reason: str = ""):
        """Execute a validated energy transaction."""
        # Validate first
        is_valid, error = self.validate_energy_transaction(from_agent, to_agent, amount)
        if not is_valid:
            raise ValueError(f"Invalid transaction: {error}")
            
        # Execute transaction
        if from_agent:
            self.agent_energies[from_agent] -= amount
        else:
            self.total_system_energy -= amount
            
        if to_agent:
            self.agent_energies[to_agent] += amount
        else:
            self.total_system_energy += amount
            
        # Record transaction
        self.energy_transactions.append({
            "timestamp": datetime.utcnow(),
            "from": from_agent,
            "to": to_agent,
            "amount": amount,
            "reason": reason
        })
        
    def verify_conservation(self) -> Tuple[bool, Optional[str]]:
        """Verify total energy is conserved."""
        agent_total = sum(self.agent_energies.values())
        expected_total = self.total_system_energy
        
        # Allow small floating point errors
        epsilon = 1e-6
        if abs(agent_total - expected_total) > epsilon:
            return False, f"Energy not conserved: {agent_total} != {expected_total}"
            
        return True, None
        
    def get_energy_report(self) -> Dict[str, Any]:
        """Get energy conservation report."""
        return {
            "total_system_energy": self.total_system_energy,
            "agent_energies": self.agent_energies.copy(),
            "total_transactions": len(self.energy_transactions),
            "conservation_valid": self.verify_conservation()[0]
        }


class RuntimeValidationSystem:
    """
    Integrated runtime validation system.
    """
    
    def __init__(self, world):
        """
        Initialize runtime validation system.
        
        Args:
            world: H3World instance
        """
        self.boundary_validator = BoundaryValidator(world)
        self.message_system = MessageDeliverySystem()
        self.energy_validator = EnergyConservationValidator()
        
        self.validation_stats = {
            "boundary_checks": 0,
            "boundary_violations": 0,
            "movement_validations": 0,
            "movement_violations": 0,
            "energy_checks": 0,
            "energy_violations": 0
        }
        
    def validate_agent_position(self, agent_id: str, position: str) -> Tuple[bool, Optional[str]]:
        """Validate agent position."""
        self.validation_stats["boundary_checks"] += 1
        is_valid, error = self.boundary_validator.validate_hex_position(position)
        
        if not is_valid:
            self.validation_stats["boundary_violations"] += 1
            logger.warning(f"Agent {agent_id} boundary violation: {error}")
            
        return is_valid, error
        
    def validate_agent_movement(self,
                              agent_id: str,
                              from_hex: str,
                              to_hex: str) -> Tuple[bool, Optional[str]]:
        """Validate agent movement."""
        self.validation_stats["movement_validations"] += 1
        
        # Check both positions are valid
        is_valid, error = self.boundary_validator.validate_hex_position(from_hex)
        if not is_valid:
            self.validation_stats["movement_violations"] += 1
            return False, f"Invalid source position: {error}"
            
        is_valid, error = self.boundary_validator.validate_hex_position(to_hex)
        if not is_valid:
            self.validation_stats["movement_violations"] += 1
            return False, f"Invalid destination position: {error}"
            
        # Check adjacency
        if not self.boundary_validator.is_adjacent(from_hex, to_hex):
            self.validation_stats["movement_violations"] += 1
            return False, f"Hexes {from_hex} and {to_hex} are not adjacent"
            
        return True, None
        
    def validate_energy_change(self,
                             agent_id: str,
                             old_energy: float,
                             new_energy: float,
                             expected_change: float) -> Tuple[bool, Optional[str]]:
        """Validate energy change matches expectation."""
        self.validation_stats["energy_checks"] += 1
        
        actual_change = new_energy - old_energy
        epsilon = 1e-6
        
        if abs(actual_change - expected_change) > epsilon:
            self.validation_stats["energy_violations"] += 1
            error = f"Energy change mismatch: expected {expected_change}, got {actual_change}"
            logger.warning(f"Agent {agent_id} {error}")
            return False, error
            
        return True, None
        
    def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report."""
        return {
            "validation_stats": self.validation_stats.copy(),
            "message_delivery": self.message_system.get_delivery_stats(),
            "energy_conservation": self.energy_validator.get_energy_report()
        }


# Test functions for validation
async def test_message_delivery():
    """Test message delivery system."""
    system = MessageDeliverySystem()
    
    # Register handlers
    async def handler1(sender, content):
        print(f"Agent1 received from {sender}: {content}")
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
    async def handler2(sender, content):
        print(f"Agent2 received from {sender}: {content}")
        
    system.register_handler("agent1", handler1)
    system.register_handler("agent2", handler2)
    
    # Send messages
    msg1 = system.send_message("agent2", "agent1", {"text": "Hello Agent 1"})
    msg2 = system.send_message("agent1", "agent2", {"text": "Hello Agent 2"})
    
    # Process messages
    await system.process_messages()
    
    # Check stats
    stats = system.get_delivery_stats()
    print(f"Delivery stats: {stats}")


if __name__ == "__main__":
    # Run async test
    asyncio.run(test_message_delivery()) 