"""
System Integration Tests

Tests the complete CogniticNet system including:
- Full simulation scenarios
- Multi-agent interactions
- Performance under load
- System stability
- Edge cases and error conditions
"""

import pytest
import asyncio
import json
import time
import psutil
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from simulation.engine import SimulationEngine
from simulation.agent_manager import AgentManager
from world.h3_world import H3World
from communication.message_system import MessageSystem
from monitoring.runtime_bug_detector import RuntimeBugDetector
from learning.pattern_extraction import PatternExtractor
from deployment.export_validator import ExportValidator

logger = logging.getLogger(__name__)


class TestFullSystemIntegration:
    """Test full system integration scenarios."""
    
    @pytest.fixture
    async def simulation_engine(self):
        """Create simulation engine."""
        config = {
            "world": {
                "resolution": 5,
                "size": 100
            },
            "agents": {
                "count": 10,
                "distribution": {
                    "explorer": 4,
                    "merchant": 3,
                    "scholar": 2,
                    "guardian": 1
                }
            },
            "simulation": {
                "max_cycles": 100,
                "time_step": 1.0
            }
        }
        
        engine = SimulationEngine(config)
        await engine.initialize()
        return engine
    
    @pytest.mark.asyncio
    async def test_complete_simulation_lifecycle(self, simulation_engine):
        """Test complete simulation lifecycle from start to finish."""
        # Start simulation
        await simulation_engine.start()
        
        # Run for specific number of cycles
        target_cycles = 50
        while simulation_engine.current_cycle < target_cycles:
            await simulation_engine.step()
            
            # Verify system health every 10 cycles
            if simulation_engine.current_cycle % 10 == 0:
                health = await simulation_engine.get_system_health()
                assert health["status"] == "healthy"
                assert health["agent_count"] == 10
                assert health["message_queue_size"] < 1000
        
        # Stop simulation
        await simulation_engine.stop()
        
        # Get final statistics
        stats = simulation_engine.get_statistics()
        
        # Verify simulation completed successfully
        assert stats["cycles_completed"] == target_cycles
        assert stats["agents_alive"] == 10
        assert stats["total_messages"] > 0
        assert stats["total_trades"] > 0
        assert stats["knowledge_nodes_created"] > 0
    
    @pytest.mark.asyncio
    async def test_multi_agent_ecosystem_dynamics(self, simulation_engine):
        """Test ecosystem dynamics with multiple agent types."""
        await simulation_engine.start()
        
        # Track ecosystem metrics
        ecosystem_metrics = {
            "resource_distribution": [],
            "agent_wealth": [],
            "knowledge_density": [],
            "trade_volume": [],
            "exploration_coverage": []
        }
        
        # Run simulation and collect metrics
        for cycle in range(30):
            await simulation_engine.step()
            
            # Collect metrics
            metrics = await simulation_engine.get_ecosystem_metrics()
            ecosystem_metrics["resource_distribution"].append(
                metrics["resource_gini_coefficient"]
            )
            ecosystem_metrics["agent_wealth"].append(
                metrics["average_agent_wealth"]
            )
            ecosystem_metrics["knowledge_density"].append(
                metrics["knowledge_nodes_per_agent"]
            )
            ecosystem_metrics["trade_volume"].append(
                metrics["trades_this_cycle"]
            )
            ecosystem_metrics["exploration_coverage"].append(
                metrics["explored_cells_percentage"]
            )
        
        # Analyze ecosystem dynamics
        # Resources should become more distributed over time
        resource_trend = np.polyfit(
            range(len(ecosystem_metrics["resource_distribution"])),
            ecosystem_metrics["resource_distribution"],
            1
        )[0]
        assert resource_trend < 0  # Gini coefficient should decrease
        
        # Knowledge should accumulate
        knowledge_trend = np.polyfit(
            range(len(ecosystem_metrics["knowledge_density"])),
            ecosystem_metrics["knowledge_density"],
            1
        )[0]
        assert knowledge_trend > 0  # Knowledge should increase
        
        # Exploration should expand
        final_coverage = ecosystem_metrics["exploration_coverage"][-1]
        assert final_coverage > ecosystem_metrics["exploration_coverage"][0]
    
    @pytest.mark.asyncio
    async def test_emergent_social_structures(self, simulation_engine):
        """Test emergence of social structures and relationships."""
        await simulation_engine.start()
        
        # Run simulation to allow relationships to form
        for _ in range(50):
            await simulation_engine.step()
        
        # Analyze social network
        social_network = await simulation_engine.get_social_network()
        
        # Check for emergent structures
        # 1. Trading partnerships
        trade_clusters = social_network.get_trade_clusters()
        assert len(trade_clusters) > 0
        
        # Merchants should be central to trade clusters
        merchant_centrality = []
        for agent_id, centrality in social_network.get_centrality_scores().items():
            agent = simulation_engine.get_agent(agent_id)
            if agent.agent_class == "merchant":
                merchant_centrality.append(centrality)
        
        avg_merchant_centrality = np.mean(merchant_centrality)
        avg_overall_centrality = np.mean(list(
            social_network.get_centrality_scores().values()
        ))
        assert avg_merchant_centrality > avg_overall_centrality
        
        # 2. Knowledge sharing networks
        knowledge_network = social_network.get_knowledge_sharing_network()
        
        # Scholars should have high knowledge sharing connections
        scholar_connections = []
        for agent_id, connections in knowledge_network.items():
            agent = simulation_engine.get_agent(agent_id)
            if agent.agent_class == "scholar":
                scholar_connections.append(len(connections))
        
        assert np.mean(scholar_connections) > 2
        
        # 3. Protection alliances
        protection_groups = social_network.get_protection_alliances()
        
        # Guardians should be part of protection groups
        guardian_in_alliance = False
        for group in protection_groups:
            for agent_id in group:
                agent = simulation_engine.get_agent(agent_id)
                if agent.agent_class == "guardian":
                    guardian_in_alliance = True
                    break
        
        assert guardian_in_alliance
    
    @pytest.mark.asyncio
    async def test_system_performance_under_load(self):
        """Test system performance with large number of agents."""
        # Create high-load configuration
        config = {
            "world": {
                "resolution": 6,  # Larger world
                "size": 500
            },
            "agents": {
                "count": 100,  # Many agents
                "distribution": {
                    "explorer": 40,
                    "merchant": 30,
                    "scholar": 20,
                    "guardian": 10
                }
            },
            "simulation": {
                "max_cycles": 20,
                "time_step": 1.0
            }
        }
        
        engine = SimulationEngine(config)
        await engine.initialize()
        
        # Track performance metrics
        performance_metrics = {
            "cycle_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "message_latency": []
        }
        
        process = psutil.Process()
        
        # Run simulation
        await engine.start()
        
        for cycle in range(10):
            start_time = time.time()
            
            # Record CPU before
            cpu_before = process.cpu_percent()
            
            # Step simulation
            await engine.step()
            
            # Record metrics
            cycle_time = time.time() - start_time
            performance_metrics["cycle_times"].append(cycle_time)
            
            memory_mb = process.memory_info().rss / 1024 / 1024
            performance_metrics["memory_usage"].append(memory_mb)
            
            cpu_after = process.cpu_percent()
            performance_metrics["cpu_usage"].append((cpu_before + cpu_after) / 2)
            
            # Get message latency
            latency = await engine.get_average_message_latency()
            performance_metrics["message_latency"].append(latency)
        
        # Verify performance is acceptable
        avg_cycle_time = np.mean(performance_metrics["cycle_times"])
        assert avg_cycle_time < 5.0  # Should complete cycle in < 5 seconds
        
        max_memory = max(performance_metrics["memory_usage"])
        assert max_memory < 2048  # Should use less than 2GB
        
        avg_latency = np.mean(performance_metrics["message_latency"])
        assert avg_latency < 100  # Message latency < 100ms
        
        # Check for memory leaks
        memory_growth = performance_metrics["memory_usage"][-1] - \
                       performance_metrics["memory_usage"][0]
        assert memory_growth < 100  # Less than 100MB growth
    
    @pytest.mark.asyncio
    async def test_fault_tolerance_and_recovery(self, simulation_engine):
        """Test system fault tolerance and recovery."""
        await simulation_engine.start()
        
        # Run normally
        for _ in range(10):
            await simulation_engine.step()
        
        initial_state = await simulation_engine.get_state_snapshot()
        
        # Simulate various failures
        
        # 1. Agent failure
        agent_to_fail = simulation_engine.get_agents()[0]
        agent_id = agent_to_fail.agent_id
        await simulation_engine.simulate_agent_failure(agent_id)
        
        # System should continue
        await simulation_engine.step()
        
        # Verify system adapted
        assert simulation_engine.get_agent_count() == 9
        assert simulation_engine.is_healthy()
        
        # 2. Communication failure
        await simulation_engine.simulate_communication_failure(duration=5)
        
        # Run with degraded communication
        for _ in range(5):
            await simulation_engine.step()
        
        # Communication should recover
        await simulation_engine.step()
        comm_health = await simulation_engine.get_communication_health()
        assert comm_health["status"] == "recovered"
        
        # 3. Resource depletion
        await simulation_engine.simulate_resource_depletion(severity=0.8)
        
        # Agents should adapt
        for _ in range(10):
            await simulation_engine.step()
        
        # Check adaptation
        survival_rate = simulation_engine.get_survival_rate()
        assert survival_rate > 0.5  # At least 50% should survive
        
        # Verify system resilience
        final_health = await simulation_engine.get_system_health()
        assert final_health["status"] in ["healthy", "degraded"]
    
    @pytest.mark.asyncio
    async def test_learning_and_adaptation(self, simulation_engine):
        """Test system-wide learning and adaptation."""
        await simulation_engine.start()
        
        # Enable learning systems
        pattern_extractor = PatternExtractor()
        simulation_engine.attach_pattern_extractor(pattern_extractor)
        
        # Track adaptation metrics
        adaptation_metrics = {
            "collective_knowledge": [],
            "behavior_diversity": [],
            "success_rates": [],
            "pattern_count": []
        }
        
        # Run simulation with learning
        for cycle in range(40):
            await simulation_engine.step()
            
            if cycle % 5 == 0:
                # Extract patterns
                patterns = pattern_extractor.extract_patterns(
                    simulation_engine.get_event_history()
                )
                
                # Measure adaptation
                metrics = await simulation_engine.get_adaptation_metrics()
                
                adaptation_metrics["collective_knowledge"].append(
                    metrics["total_knowledge_nodes"]
                )
                adaptation_metrics["behavior_diversity"].append(
                    metrics["behavior_entropy"]
                )
                adaptation_metrics["success_rates"].append(
                    metrics["average_goal_achievement"]
                )
                adaptation_metrics["pattern_count"].append(len(patterns))
        
        # Verify learning occurred
        # Knowledge should increase
        knowledge_growth = adaptation_metrics["collective_knowledge"][-1] - \
                          adaptation_metrics["collective_knowledge"][0]
        assert knowledge_growth > 0
        
        # Success rates should improve
        success_improvement = adaptation_metrics["success_rates"][-1] - \
                            adaptation_metrics["success_rates"][0]
        assert success_improvement > 0
        
        # Patterns should be discovered
        assert adaptation_metrics["pattern_count"][-1] > 5
    
    @pytest.mark.asyncio
    async def test_scalability_limits(self):
        """Test system scalability limits."""
        # Test increasing agent counts
        agent_counts = [10, 50, 100, 200]
        scalability_results = []
        
        for count in agent_counts:
            config = {
                "world": {"resolution": 6, "size": count * 10},
                "agents": {"count": count},
                "simulation": {"max_cycles": 5}
            }
            
            try:
                engine = SimulationEngine(config)
                await engine.initialize()
                
                start_time = time.time()
                await engine.start()
                
                # Run 5 cycles
                for _ in range(5):
                    await engine.step()
                
                total_time = time.time() - start_time
                
                scalability_results.append({
                    "agent_count": count,
                    "total_time": total_time,
                    "time_per_agent": total_time / count,
                    "success": True
                })
                
                await engine.stop()
                
            except Exception as e:
                scalability_results.append({
                    "agent_count": count,
                    "success": False,
                    "error": str(e)
                })
        
        # Analyze scalability
        successful_tests = [r for r in scalability_results if r["success"]]
        
        # Should handle at least 100 agents
        max_successful = max(r["agent_count"] for r in successful_tests)
        assert max_successful >= 100
        
        # Time per agent should not increase dramatically
        if len(successful_tests) >= 2:
            time_per_agent_small = successful_tests[0]["time_per_agent"]
            time_per_agent_large = successful_tests[-1]["time_per_agent"]
            
            # Should not be more than 2x slower per agent
            assert time_per_agent_large < time_per_agent_small * 2


class TestEdgeCasesAndStress:
    """Test edge cases and stress scenarios."""
    
    @pytest.mark.asyncio
    async def test_resource_scarcity_scenario(self):
        """Test system behavior under extreme resource scarcity."""
        config = {
            "world": {
                "resolution": 5,
                "size": 50,
                "resource_density": 0.1  # Very low resources
            },
            "agents": {"count": 20},
            "simulation": {"max_cycles": 50}
        }
        
        engine = SimulationEngine(config)
        await engine.initialize()
        await engine.start()
        
        # Track survival and cooperation
        survival_timeline = []
        cooperation_events = []
        
        for cycle in range(30):
            await engine.step()
            
            alive_count = engine.get_alive_agent_count()
            survival_timeline.append(alive_count)
            
            # Check for cooperation
            events = engine.get_events_this_cycle()
            cooperation_count = sum(
                1 for e in events 
                if e["type"] in ["trade", "resource_share", "alliance_formed"]
            )
            cooperation_events.append(cooperation_count)
        
        # In scarcity, cooperation should increase
        early_cooperation = np.mean(cooperation_events[:10])
        late_cooperation = np.mean(cooperation_events[-10:])
        assert late_cooperation > early_cooperation
        
        # Some agents should survive through cooperation
        final_survival = survival_timeline[-1]
        assert final_survival > 5
    
    @pytest.mark.asyncio
    async def test_information_overload(self):
        """Test system behavior with information overload."""
        config = {
            "world": {"resolution": 5, "size": 50},
            "agents": {
                "count": 10,
                "communication_rate": 10.0  # Very high communication
            },
            "simulation": {"max_cycles": 20}
        }
        
        engine = SimulationEngine(config)
        await engine.initialize()
        await engine.start()
        
        # Monitor message processing
        message_stats = {
            "dropped_messages": 0,
            "processing_delays": [],
            "queue_sizes": []
        }
        
        for _ in range(10):
            await engine.step()
            
            stats = await engine.get_message_system_stats()
            message_stats["dropped_messages"] += stats["dropped_count"]
            message_stats["processing_delays"].append(stats["avg_delay"])
            message_stats["queue_sizes"].append(stats["queue_size"])
        
        # System should handle overload gracefully
        # Some message dropping is acceptable
        drop_rate = message_stats["dropped_messages"] / \
                   (sum(message_stats["queue_sizes"]) + message_stats["dropped_messages"])
        assert drop_rate < 0.1  # Less than 10% drop rate
        
        # Delays should stabilize
        late_delays = message_stats["processing_delays"][-5:]
        assert np.std(late_delays) < np.mean(late_delays) * 0.5
    
    @pytest.mark.asyncio
    async def test_rapid_environmental_changes(self):
        """Test adaptation to rapid environmental changes."""
        engine = SimulationEngine({
            "world": {"resolution": 5, "size": 100},
            "agents": {"count": 20},
            "simulation": {"max_cycles": 50}
        })
        
        await engine.initialize()
        await engine.start()
        
        adaptation_scores = []
        
        # Cycle through different environmental conditions
        conditions = [
            {"resource_multiplier": 1.0, "hazard_level": 0.1},
            {"resource_multiplier": 0.3, "hazard_level": 0.5},
            {"resource_multiplier": 2.0, "hazard_level": 0.2},
            {"resource_multiplier": 0.5, "hazard_level": 0.8}
        ]
        
        for condition in conditions:
            # Apply environmental change
            await engine.set_environmental_conditions(condition)
            
            # Let agents adapt
            pre_change_performance = await engine.get_average_agent_performance()
            
            for _ in range(10):
                await engine.step()
            
            post_change_performance = await engine.get_average_agent_performance()
            
            # Calculate adaptation score
            adaptation = post_change_performance / pre_change_performance
            adaptation_scores.append(adaptation)
        
        # Agents should show adaptation
        avg_adaptation = np.mean(adaptation_scores)
        assert avg_adaptation > 0.7  # Maintain at least 70% performance
        
        # Later adaptations should be better
        assert adaptation_scores[-1] > adaptation_scores[0]


class TestExportAndDeployment:
    """Test export and deployment functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_export_validation(self):
        """Test agent export and validation."""
        # Create and train an agent
        engine = SimulationEngine({
            "world": {"resolution": 5, "size": 50},
            "agents": {"count": 1},
            "simulation": {"max_cycles": 20}
        })
        
        await engine.initialize()
        await engine.start()
        
        # Train agent
        for _ in range(20):
            await engine.step()
        
        # Export agent
        agent = engine.get_agents()[0]
        export_path = Path("/tmp/test_agent_export")
        
        success = await engine.export_agent(agent.agent_id, export_path)
        assert success
        
        # Validate export
        validator = ExportValidator()
        results = validator.validate_package(export_path)
        
        # Check validation passed
        summary = next(r for r in results if r.check_name == "validation_summary")
        assert summary.status.value == "passed"
        
        # Verify exported files
        assert (export_path / "manifest.json").exists()
        assert (export_path / "agent_config.json").exists()
        assert (export_path / "gnn_model.json").exists()
        assert (export_path / "knowledge_graph.json").exists()
        assert (export_path / "run.sh").exists()
    
    @pytest.mark.asyncio
    async def test_multi_agent_deployment_package(self):
        """Test creating deployment package for multiple agents."""
        engine = SimulationEngine({
            "world": {"resolution": 5, "size": 100},
            "agents": {"count": 4},
            "simulation": {"max_cycles": 30}
        })
        
        await engine.initialize()
        await engine.start()
        
        # Run simulation
        for _ in range(30):
            await engine.step()
        
        # Export all agents as a deployment
        deployment_path = Path("/tmp/test_deployment")
        
        success = await engine.export_deployment(
            deployment_path,
            include_world=True,
            include_history=True
        )
        
        assert success
        
        # Verify deployment structure
        assert (deployment_path / "deployment.json").exists()
        assert (deployment_path / "agents").is_dir()
        assert (deployment_path / "world").is_dir()
        assert (deployment_path / "configs").is_dir()
        assert (deployment_path / "docker-compose.yml").exists()
        
        # Check each agent was exported
        agent_exports = list((deployment_path / "agents").glob("*/"))
        assert len(agent_exports) == 4


def run_system_integration_tests():
    """Run all system integration tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-s"]) 