"""
Runtime Bug Detection System
Continuous monitoring and automatic bug detection with auto-healing.
"""

import asyncio
import logging
from typing import Dict, List, Callable, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import traceback
import json
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Severity levels for invariant violations."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HealingStatus(Enum):
    """Status of auto-healing attempts."""

    NOT_ATTEMPTED = "not_attempted"
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class InvariantViolation:
    """Details of an invariant violation."""

    invariant_name: str
    message: str
    severity: ViolationSeverity
    timestamp: datetime = field(default_factory=datetime.utcnow)
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    healing_attempted: bool = False
    healing_status: HealingStatus = HealingStatus.NOT_ATTEMPTED
    healing_details: Optional[str] = None


@dataclass
class Invariant:
    """Represents a system invariant that must hold."""

    name: str
    check_function: Callable[[], Tuple[bool, Optional[str]]]
    healing_function: Optional[Callable[[InvariantViolation], bool]] = None
    severity: ViolationSeverity = ViolationSeverity.ERROR
    enabled: bool = True
    check_interval_seconds: float = 5.0
    last_check: Optional[datetime] = None
    consecutive_failures: int = 0
    max_consecutive_failures: int = 3


class RuntimeBugDetector:
    """
    Continuous runtime monitoring with invariant checking and auto-healing.

    Monitors system health by checking registered invariants and
    attempts to heal violations when possible.
    """

    def __init__(
        self, check_interval: float = 5.0, max_violations_per_minute: int = 10
    ):
        """
        Initialize the runtime bug detector.

        Args:
            check_interval: Default seconds between invariant checks
            max_violations_per_minute: Circuit breaker threshold
        """
        self.check_interval = check_interval
        self.max_violations_per_minute = max_violations_per_minute

        self.invariants: Dict[str, Invariant] = {}
        self.violations: List[InvariantViolation] = []
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None

        # Circuit breaker
        self.violations_in_window: List[datetime] = []
        self.circuit_breaker_open = False

        # Statistics
        self.total_checks = 0
        self.total_violations = 0
        self.total_healings = 0
        self.successful_healings = 0

        logger.info("RuntimeBugDetector initialized")

    def register_invariant(
        self,
        name: str,
        check_function: Callable[[], Tuple[bool, Optional[str]]],
        healing_function: Optional[Callable[[InvariantViolation], bool]] = None,
        severity: ViolationSeverity = ViolationSeverity.ERROR,
        check_interval: Optional[float] = None,
    ):
        """
        Register an invariant to monitor.

        Args:
            name: Unique name for the invariant
            check_function: Function that returns (is_valid, error_message)
            healing_function: Optional function to heal violations
            severity: Severity level of violations
            check_interval: Custom check interval (uses default if None)
        """
        if name in self.invariants:
            logger.warning(f"Overwriting existing invariant: {name}")

        self.invariants[name] = Invariant(
            name=name,
            check_function=check_function,
            healing_function=healing_function,
            severity=severity,
            check_interval_seconds=check_interval or self.check_interval,
        )

        logger.info(f"Registered invariant: {name} (severity: {severity.value})")

    def unregister_invariant(self, name: str):
        """Remove an invariant from monitoring."""
        if name in self.invariants:
            del self.invariants[name]
            logger.info(f"Unregistered invariant: {name}")

    def enable_invariant(self, name: str):
        """Enable checking of a specific invariant."""
        if name in self.invariants:
            self.invariants[name].enabled = True

    def disable_invariant(self, name: str):
        """Disable checking of a specific invariant."""
        if name in self.invariants:
            self.invariants[name].enabled = False

    async def check_invariant(
        self, invariant: Invariant
    ) -> Optional[InvariantViolation]:
        """Check a single invariant and return violation if any."""
        if not invariant.enabled:
            return None

        try:
            # Check if it's time to check this invariant
            now = datetime.utcnow()
            if invariant.last_check:
                elapsed = (now - invariant.last_check).total_seconds()
                if elapsed < invariant.check_interval_seconds:
                    return None

            invariant.last_check = now
            self.total_checks += 1

            # Run the check
            is_valid, error_message = invariant.check_function()

            if is_valid:
                # Reset consecutive failures on success
                invariant.consecutive_failures = 0
                return None

            # Invariant violated
            invariant.consecutive_failures += 1

            violation = InvariantViolation(
                invariant_name=invariant.name,
                message=error_message or f"Invariant {invariant.name} violated",
                severity=invariant.severity,
                context={
                    "consecutive_failures": invariant.consecutive_failures,
                    "check_interval": invariant.check_interval_seconds,
                },
            )

            # Disable invariant if too many consecutive failures
            if invariant.consecutive_failures >= invariant.max_consecutive_failures:
                logger.error(
                    f"Disabling invariant {invariant.name} after {invariant.consecutive_failures} failures"
                )
                invariant.enabled = False
                violation.context["auto_disabled"] = True

            return violation

        except Exception as e:
            # Error in check function itself
            logger.error(f"Error checking invariant {invariant.name}: {e}")
            return InvariantViolation(
                invariant_name=invariant.name,
                message=f"Check function error: {str(e)}",
                severity=ViolationSeverity.CRITICAL,
                stack_trace=traceback.format_exc(),
            )

    async def attempt_healing(self, violation: InvariantViolation) -> bool:
        """Attempt to heal an invariant violation."""
        invariant = self.invariants.get(violation.invariant_name)

        if not invariant or not invariant.healing_function:
            violation.healing_status = HealingStatus.NOT_ATTEMPTED
            return False

        try:
            logger.info(f"Attempting to heal violation: {violation.invariant_name}")
            violation.healing_attempted = True
            self.total_healings += 1

            # Run healing function
            success = invariant.healing_function(violation)

            if success:
                violation.healing_status = HealingStatus.SUCCESS
                violation.healing_details = "Healing successful"
                self.successful_healings += 1

                # Re-enable invariant if it was auto-disabled
                if violation.context.get("auto_disabled"):
                    invariant.enabled = True
                    invariant.consecutive_failures = 0

                logger.info(
                    f"Successfully healed violation: {violation.invariant_name}"
                )
                return True
            else:
                violation.healing_status = HealingStatus.FAILED
                violation.healing_details = "Healing function returned False"
                logger.warning(f"Failed to heal violation: {violation.invariant_name}")
                return False

        except Exception as e:
            violation.healing_status = HealingStatus.FAILED
            violation.healing_details = f"Healing error: {str(e)}"
            logger.error(f"Error during healing of {violation.invariant_name}: {e}")
            return False

    async def continuous_monitoring(self):
        """Main monitoring loop that continuously checks invariants."""
        logger.info("Starting continuous monitoring")

        while self.monitoring_active:
            try:
                # Check circuit breaker
                if self.circuit_breaker_open:
                    await asyncio.sleep(60)  # Wait longer if circuit breaker is open
                    self._check_circuit_breaker()
                    continue

                # Check all invariants
                violations = []

                for invariant in self.invariants.values():
                    violation = await self.check_invariant(invariant)
                    if violation:
                        violations.append(violation)

                # Process violations
                for violation in violations:
                    await self._process_violation(violation)

                # Update circuit breaker
                self._update_circuit_breaker()

                # Sleep before next check cycle
                await asyncio.sleep(self.check_interval)

            except asyncio.CancelledError:
                logger.info("Monitoring cancelled")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(self.check_interval)

        logger.info("Continuous monitoring stopped")

    async def _process_violation(self, violation: InvariantViolation):
        """Process a single violation."""
        self.total_violations += 1
        self.violations.append(violation)
        self.violations_in_window.append(violation.timestamp)

        # Log based on severity
        if violation.severity == ViolationSeverity.CRITICAL:
            logger.critical(
                f"CRITICAL violation: {violation.invariant_name} - {violation.message}"
            )
        elif violation.severity == ViolationSeverity.ERROR:
            logger.error(
                f"ERROR violation: {violation.invariant_name} - {violation.message}"
            )
        elif violation.severity == ViolationSeverity.WARNING:
            logger.warning(
                f"WARNING violation: {violation.invariant_name} - {violation.message}"
            )
        else:
            logger.info(
                f"INFO violation: {violation.invariant_name} - {violation.message}"
            )

        # Attempt healing for ERROR and CRITICAL violations
        if violation.severity in [ViolationSeverity.ERROR, ViolationSeverity.CRITICAL]:
            await self.attempt_healing(violation)

    def _update_circuit_breaker(self):
        """Update circuit breaker based on violation rate."""
        now = datetime.utcnow()

        # Remove old violations from window
        self.violations_in_window = [
            ts for ts in self.violations_in_window if (now - ts).total_seconds() < 60
        ]

        # Check if we should open circuit breaker
        if len(self.violations_in_window) > self.max_violations_per_minute:
            if not self.circuit_breaker_open:
                logger.error(
                    f"Circuit breaker opened: {len(self.violations_in_window)} violations in last minute"
                )
                self.circuit_breaker_open = True

    def _check_circuit_breaker(self):
        """Check if circuit breaker can be closed."""
        if (
            self.circuit_breaker_open
            and len(self.violations_in_window) < self.max_violations_per_minute / 2
        ):
            logger.info("Circuit breaker closed")
            self.circuit_breaker_open = False

    async def start_monitoring(self):
        """Start the continuous monitoring task."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self.continuous_monitoring())
        logger.info("Monitoring started")

    async def stop_monitoring(self):
        """Stop the continuous monitoring task."""
        if not self.monitoring_active:
            return

        self.monitoring_active = False

        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Monitoring stopped")

    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        recent_violations = [
            v
            for v in self.violations
            if (datetime.utcnow() - v.timestamp).total_seconds() < 3600
        ]

        return {
            "total_checks": self.total_checks,
            "total_violations": self.total_violations,
            "total_healings": self.total_healings,
            "successful_healings": self.successful_healings,
            "healing_success_rate": (
                self.successful_healings / self.total_healings
                if self.total_healings > 0
                else 0
            ),
            "violations_last_hour": len(recent_violations),
            "circuit_breaker_open": self.circuit_breaker_open,
            "active_invariants": sum(
                1 for inv in self.invariants.values() if inv.enabled
            ),
            "disabled_invariants": sum(
                1 for inv in self.invariants.values() if not inv.enabled
            ),
        }

    def get_recent_violations(self, count: int = 10) -> List[InvariantViolation]:
        """Get the most recent violations."""
        return self.violations[-count:]

    def clear_violations(self):
        """Clear violation history."""
        self.violations.clear()
        self.violations_in_window.clear()

    @asynccontextmanager
    async def monitored_context(self):
        """Context manager for temporary monitoring."""
        await self.start_monitoring()
        try:
            yield self
        finally:
            await self.stop_monitoring()


# Pre-defined invariants for common checks
class CommonInvariants:
    """Collection of common invariant check functions."""

    @staticmethod
    def create_agent_positions_valid(world, agents):
        """Create invariant for valid agent positions."""

        def check():
            try:
                for agent in agents:
                    if not world.get_cell(agent.position.hex_id):
                        return (
                            False,
                            f"Agent {agent.id} at invalid position {agent.position.hex_id}",
                        )
                return True, None
            except Exception as e:
                return False, f"Error checking agent positions: {e}"

        def heal(violation):
            # Move agents to nearest valid cell
            try:
                for agent in agents:
                    if not world.get_cell(agent.position.hex_id):
                        # Find nearest valid cell (simplified)
                        agent.position.hex_id = world.center_hex
                        logger.info(f"Moved agent {agent.id} to center hex")
                return True
            except:
                return False

        return check, heal

    @staticmethod
    def create_knowledge_graphs_consistent(knowledge_graphs):
        """Create invariant for knowledge graph consistency."""

        def check():
            try:
                for agent_id, kg in knowledge_graphs.items():
                    # Check graph connectivity
                    if not kg.graph.is_directed():
                        return False, f"Knowledge graph for {agent_id} is not directed"

                    # Check for orphaned nodes
                    for node in kg.graph.nodes():
                        if (
                            kg.graph.in_degree(node) == 0
                            and kg.graph.out_degree(node) == 0
                            and len(kg.graph.nodes()) > 1
                        ):
                            return (
                                False,
                                f"Orphaned node {node} in {agent_id}'s knowledge graph",
                            )

                return True, None
            except Exception as e:
                return False, f"Error checking knowledge graphs: {e}"

        return check, None  # No auto-healing for this

    @staticmethod
    def create_energy_conservation(agents, initial_total_energy):
        """Create invariant for energy conservation."""

        def check():
            try:
                total_energy = sum(agent.energy for agent in agents)
                # Allow small floating point differences
                if abs(total_energy - initial_total_energy) > 0.01:
                    return (
                        False,
                        f"Energy not conserved: {total_energy} != {initial_total_energy}",
                    )
                return True, None
            except Exception as e:
                return False, f"Error checking energy conservation: {e}"

        return check, None

    @staticmethod
    def create_gnn_models_valid(agents, validator):
        """Create invariant for GNN model validity."""

        def check():
            try:
                for agent in agents:
                    if agent.gnn_model_path:
                        # Simplified check - in reality would load and validate model
                        if not agent.gnn_model_path.endswith(".gnn.md"):
                            return False, f"Invalid GNN model path for agent {agent.id}"
                return True, None
            except Exception as e:
                return False, f"Error checking GNN models: {e}"

        return check, None


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test_monitoring():
        # Create detector
        detector = RuntimeBugDetector(check_interval=2.0)

        # Register some test invariants
        test_value = 10

        def check_test_value():
            return test_value > 0, f"Test value is {test_value}"

        def heal_test_value(violation):
            nonlocal test_value
            test_value = 10
            return True

        detector.register_invariant(
            "test_value_positive",
            check_test_value,
            heal_test_value,
            ViolationSeverity.ERROR,
        )

        # Start monitoring
        async with detector.monitored_context():
            # Simulate normal operation
            await asyncio.sleep(3)

            # Introduce a bug
            test_value = -5

            # Wait for detection and healing
            await asyncio.sleep(5)

            # Check statistics
            stats = detector.get_statistics()
            print(f"Statistics: {json.dumps(stats, indent=2)}")

            # Check recent violations
            violations = detector.get_recent_violations()
            for v in violations:
                print(
                    f"Violation: {v.invariant_name} - {v.message} (healed: {v.healing_status.value})"
                )

    # Run test
    asyncio.run(test_monitoring())
