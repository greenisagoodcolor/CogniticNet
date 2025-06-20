"""
Bug-Checked Simulation System
Wraps simulation with comprehensive verification after each step.
"""

import copy
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import json

from .engine import SimulationEngine
from ..validation.runtime_validation import RuntimeValidationSystem
from ..world.h3_world import H3World

logger = logging.getLogger(__name__)


@dataclass
class SimulationState:
    """Captures simulation state at a point in time."""

    timestamp: datetime
    step_number: int
    agent_states: Dict[str, Dict[str, Any]]
    world_state: Dict[str, Any]
    total_energy: float
    resource_totals: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "step_number": self.step_number,
            "agent_states": self.agent_states,
            "world_state": self.world_state,
            "total_energy": self.total_energy,
            "resource_totals": self.resource_totals,
        }


@dataclass
class BugReport:
    """Report of a detected bug."""

    bug_type: str
    severity: str  # "critical", "high", "medium", "low"
    description: str
    step_number: int
    agent_id: Optional[str]
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging."""
        return {
            "bug_type": self.bug_type,
            "severity": self.severity,
            "description": self.description,
            "step_number": self.step_number,
            "agent_id": self.agent_id,
            "details": self.details,
            "timestamp": datetime.utcnow().isoformat(),
        }


class StateVerifier:
    """Verifies simulation state consistency."""

    ENERGY_TOLERANCE = 0.01  # 1% tolerance for floating point errors

    def __init__(self):
        """Initialize state verifier."""
        self.verification_checks = {
            "energy_conservation": self.verify_energy_conservation,
            "valid_positions": self.verify_valid_positions,
            "resource_consistency": self.verify_resource_consistency,
            "movement_validity": self.verify_movement_validity,
            "no_teleportation": self.verify_no_teleportation,
            "no_resource_duplication": self.verify_no_resource_duplication,
        }

    def verify_state_transition(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """
        Verify state transition is valid.

        Args:
            pre_state: State before step
            post_state: State after step
            world: World instance for validation

        Returns:
            List of bug reports
        """
        bugs = []

        for check_name, check_func in self.verification_checks.items():
            try:
                check_bugs = check_func(pre_state, post_state, world)
                bugs.extend(check_bugs)
            except Exception as e:
                logger.error(f"Error in verification check {check_name}: {e}")
                bugs.append(
                    BugReport(
                        bug_type="verification_error",
                        severity="high",
                        description=f"Verification check {check_name} failed: {str(e)}",
                        step_number=post_state.step_number,
                        agent_id=None,
                        details={"check": check_name, "error": str(e)},
                    )
                )

        return bugs

    def verify_energy_conservation(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """Verify total energy is conserved."""
        bugs = []

        pre_total = pre_state.total_energy
        post_total = post_state.total_energy

        # Check within tolerance
        if abs(post_total - pre_total) > self.ENERGY_TOLERANCE:
            bugs.append(
                BugReport(
                    bug_type="energy_violation",
                    severity="critical",
                    description=f"Energy not conserved: {pre_total:.2f} -> {post_total:.2f}",
                    step_number=post_state.step_number,
                    agent_id=None,
                    details={
                        "pre_total": pre_total,
                        "post_total": post_total,
                        "difference": post_total - pre_total,
                    },
                )
            )

        return bugs

    def verify_valid_positions(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """Verify all agents are in valid positions."""
        bugs = []
        valid_hexes = set(world.hexagons.keys())

        for agent_id, agent_state in post_state.agent_states.items():
            position = agent_state.get("position")

            if position not in valid_hexes:
                bugs.append(
                    BugReport(
                        bug_type="invalid_position",
                        severity="critical",
                        description=f"Agent {agent_id} at invalid position: {position}",
                        step_number=post_state.step_number,
                        agent_id=agent_id,
                        details={"position": position},
                    )
                )

        return bugs

    def verify_resource_consistency(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """Verify resource totals are consistent."""
        bugs = []

        # Compare resource totals
        for resource, pre_total in pre_state.resource_totals.items():
            post_total = post_state.resource_totals.get(resource, 0)

            # Resources can be consumed but not created from nothing
            if post_total > pre_total:
                bugs.append(
                    BugReport(
                        bug_type="resource_creation",
                        severity="high",
                        description=f"Resource {resource} increased: {pre_total} -> {post_total}",
                        step_number=post_state.step_number,
                        agent_id=None,
                        details={
                            "resource": resource,
                            "pre_total": pre_total,
                            "post_total": post_total,
                        },
                    )
                )

        return bugs

    def verify_movement_validity(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """Verify all movements are valid."""
        bugs = []

        for agent_id in pre_state.agent_states:
            if agent_id not in post_state.agent_states:
                continue

            pre_pos = pre_state.agent_states[agent_id].get("position")
            post_pos = post_state.agent_states[agent_id].get("position")

            if pre_pos != post_pos:
                # Check if movement is valid
                neighbors = world.get_neighbors(pre_pos)

                if post_pos not in neighbors:
                    bugs.append(
                        BugReport(
                            bug_type="invalid_movement",
                            severity="high",
                            description=f"Agent {agent_id} invalid move: {pre_pos} -> {post_pos}",
                            step_number=post_state.step_number,
                            agent_id=agent_id,
                            details={
                                "from": pre_pos,
                                "to": post_pos,
                                "valid_neighbors": neighbors,
                            },
                        )
                    )

        return bugs

    def verify_no_teleportation(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """Verify agents don't teleport (move more than 1 hex)."""
        bugs = []

        for agent_id in pre_state.agent_states:
            if agent_id not in post_state.agent_states:
                continue

            pre_pos = pre_state.agent_states[agent_id].get("position")
            post_pos = post_state.agent_states[agent_id].get("position")

            if pre_pos != post_pos:
                # Calculate hex distance
                distance = world.get_hex_distance(pre_pos, post_pos)

                if distance > 1:
                    bugs.append(
                        BugReport(
                            bug_type="teleportation",
                            severity="critical",
                            description=f"Agent {agent_id} teleported {distance} hexes",
                            step_number=post_state.step_number,
                            agent_id=agent_id,
                            details={
                                "from": pre_pos,
                                "to": post_pos,
                                "distance": distance,
                            },
                        )
                    )

        return bugs

    def verify_no_resource_duplication(
        self, pre_state: SimulationState, post_state: SimulationState, world: H3World
    ) -> List[BugReport]:
        """Verify resources aren't duplicated."""
        bugs = []

        # Track resource changes per agent
        for agent_id in pre_state.agent_states:
            if agent_id not in post_state.agent_states:
                continue

            pre_resources = pre_state.agent_states[agent_id].get("resources", {})
            post_resources = post_state.agent_states[agent_id].get("resources", {})

            for resource, post_amount in post_resources.items():
                pre_amount = pre_resources.get(resource, 0)

                # Check for suspicious increases
                if post_amount > pre_amount * 1.5 and post_amount - pre_amount > 50:
                    bugs.append(
                        BugReport(
                            bug_type="resource_duplication",
                            severity="high",
                            description=f"Agent {agent_id} suspicious {resource} increase",
                            step_number=post_state.step_number,
                            agent_id=agent_id,
                            details={
                                "resource": resource,
                                "pre_amount": pre_amount,
                                "post_amount": post_amount,
                                "increase": post_amount - pre_amount,
                            },
                        )
                    )

        return bugs


class BugCheckedSimulation:
    """
    Simulation wrapper with comprehensive bug checking.
    """

    def __init__(self, simulation_engine: SimulationEngine):
        """
        Initialize bug-checked simulation.

        Args:
            simulation_engine: Core simulation engine to wrap
        """
        self.engine = simulation_engine
        self.world = simulation_engine.world
        self.validation_system = RuntimeValidationSystem(self.world)
        self.state_verifier = StateVerifier()

        # State tracking
        self.state_history: List[SimulationState] = []
        self.bug_history: List[BugReport] = []
        self.rollback_enabled = True
        self.max_history_size = 100

        # Statistics
        self.stats = {
            "total_steps": 0,
            "bugs_detected": 0,
            "rollbacks_performed": 0,
            "critical_bugs": 0,
        }

        logger.info("Initialized bug-checked simulation")

    def capture_state(self) -> SimulationState:
        """Capture current simulation state."""
        # Capture agent states
        agent_states = {}
        total_energy = 0.0
        resource_totals = {}

        for agent_id, agent in self.engine.agents.items():
            agent_state = {
                "position": agent.position,
                "energy": agent.energy,
                "resources": copy.deepcopy(agent.resources),
                "beliefs": (
                    len(agent.knowledge_graph.graph.nodes())
                    if hasattr(agent, "knowledge_graph")
                    else 0
                ),
            }
            agent_states[agent_id] = agent_state

            total_energy += agent.energy

            for resource, amount in agent.resources.items():
                resource_totals[resource] = resource_totals.get(resource, 0) + amount

        # Capture world state
        world_resources = {}
        for hex_id, hex_data in self.world.hexagons.items():
            hex_resources = hex_data.get("resources", {})
            for resource, amount in hex_resources.items():
                world_resources[resource] = world_resources.get(resource, 0) + amount
                resource_totals[resource] = resource_totals.get(resource, 0) + amount

        world_state = {
            "hex_count": len(self.world.hexagons),
            "world_resources": world_resources,
        }

        return SimulationState(
            timestamp=datetime.utcnow(),
            step_number=self.engine.current_step,
            agent_states=agent_states,
            world_state=world_state,
            total_energy=total_energy,
            resource_totals=resource_totals,
        )

    def step(self) -> Tuple[bool, List[BugReport]]:
        """
        Execute one simulation step with verification.

        Returns:
            (success, bugs_found)
        """
        # Capture pre-state
        pre_state = self.capture_state()

        try:
            # Execute simulation step
            self.engine.step()

            # Capture post-state
            post_state = self.capture_state()

            # Verify state transition
            bugs = self.state_verifier.verify_state_transition(
                pre_state, post_state, self.world
            )

            # Handle bugs
            if bugs:
                self._handle_bugs(bugs, pre_state)

                # Rollback if critical bugs
                critical_bugs = [b for b in bugs if b.severity == "critical"]
                if critical_bugs and self.rollback_enabled:
                    self._rollback_to_state(pre_state)
                    return False, bugs

            # Update history
            self._update_history(post_state)

            # Update stats
            self.stats["total_steps"] += 1
            self.stats["bugs_detected"] += len(bugs)

            return True, bugs

        except Exception as e:
            logger.error(f"Error during simulation step: {e}")

            # Create error bug report
            error_bug = BugReport(
                bug_type="simulation_error",
                severity="critical",
                description=f"Simulation step failed: {str(e)}",
                step_number=self.engine.current_step,
                agent_id=None,
                details={"error": str(e)},
            )

            # Rollback on error
            if self.rollback_enabled:
                self._rollback_to_state(pre_state)

            return False, [error_bug]

    def _handle_bugs(self, bugs: List[BugReport], pre_state: SimulationState):
        """Handle detected bugs."""
        for bug in bugs:
            self.bug_history.append(bug)

            if bug.severity == "critical":
                self.stats["critical_bugs"] += 1
                logger.error(f"CRITICAL BUG: {bug.description}")
            else:
                logger.warning(f"Bug detected: {bug.description}")

            # Log bug details
            logger.debug(f"Bug details: {json.dumps(bug.to_dict(), indent=2)}")

    def _rollback_to_state(self, state: SimulationState):
        """Rollback simulation to a previous state."""
        logger.info(f"Rolling back to step {state.step_number}")

        try:
            # Restore agent states
            for agent_id, agent_state in state.agent_states.items():
                if agent_id in self.engine.agents:
                    agent = self.engine.agents[agent_id]
                    agent.position = agent_state["position"]
                    agent.energy = agent_state["energy"]
                    agent.resources = copy.deepcopy(agent_state["resources"])

            # Restore step number
            self.engine.current_step = state.step_number

            # Update stats
            self.stats["rollbacks_performed"] += 1

            logger.info("Rollback completed successfully")

        except Exception as e:
            logger.error(f"Rollback failed: {e}")

    def _update_history(self, state: SimulationState):
        """Update state history."""
        self.state_history.append(state)

        # Limit history size
        if len(self.state_history) > self.max_history_size:
            self.state_history.pop(0)

    def run(self, steps: int) -> Dict[str, Any]:
        """
        Run simulation for specified steps.

        Args:
            steps: Number of steps to run

        Returns:
            Simulation results and statistics
        """
        logger.info(f"Starting bug-checked simulation for {steps} steps")

        successful_steps = 0
        total_bugs = []

        for i in range(steps):
            success, bugs = self.step()
            total_bugs.extend(bugs)

            if success:
                successful_steps += 1
            else:
                logger.warning(f"Step {i} failed with {len(bugs)} bugs")

                # Stop on critical bugs
                if any(b.severity == "critical" for b in bugs):
                    logger.error("Stopping simulation due to critical bugs")
                    break

        # Generate report
        report = {
            "total_steps_attempted": steps,
            "successful_steps": successful_steps,
            "total_bugs": len(total_bugs),
            "bugs_by_type": self._count_bugs_by_type(total_bugs),
            "bugs_by_severity": self._count_bugs_by_severity(total_bugs),
            "statistics": self.stats,
            "final_state": (
                self.state_history[-1].to_dict() if self.state_history else None
            ),
        }

        logger.info(
            f"Simulation completed: {successful_steps}/{steps} successful steps"
        )

        return report

    def _count_bugs_by_type(self, bugs: List[BugReport]) -> Dict[str, int]:
        """Count bugs by type."""
        counts = {}
        for bug in bugs:
            counts[bug.bug_type] = counts.get(bug.bug_type, 0) + 1
        return counts

    def _count_bugs_by_severity(self, bugs: List[BugReport]) -> Dict[str, int]:
        """Count bugs by severity."""
        counts = {}
        for bug in bugs:
            counts[bug.severity] = counts.get(bug.severity, 0) + 1
        return counts

    def get_bug_report(self) -> List[Dict[str, Any]]:
        """Get detailed bug report."""
        return [bug.to_dict() for bug in self.bug_history]

    def get_state_history(self) -> List[Dict[str, Any]]:
        """Get state history."""
        return [state.to_dict() for state in self.state_history]

    def enable_rollback(self, enabled: bool = True):
        """Enable or disable rollback on critical bugs."""
        self.rollback_enabled = enabled
        logger.info(f"Rollback {'enabled' if enabled else 'disabled'}")


# Example usage
if __name__ == "__main__":
    from ..world.h3_world import H3World
    from .engine import SimulationEngine

    # Create world and simulation
    world = H3World(resolution=7, rings=2)
    world.generate()

    engine = SimulationEngine(world)

    # Wrap with bug checking
    bug_checked = BugCheckedSimulation(engine)

    # Run simulation
    results = bug_checked.run(100)

    print(f"Simulation results: {json.dumps(results, indent=2)}")

    # Get bug report
    bugs = bug_checked.get_bug_report()
    if bugs:
        print(f"\nDetected {len(bugs)} bugs:")
        for bug in bugs[:5]:  # Show first 5
            print(f"  - {bug['bug_type']}: {bug['description']}")
    else:
        print("\nNo bugs detected!")
