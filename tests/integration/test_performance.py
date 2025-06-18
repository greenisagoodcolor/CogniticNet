"""
Performance Tests

Tests system performance, scalability, and resource usage.
"""

import pytest
import asyncio
import time
import psutil
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any
import concurrent.futures
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from simulation.engine import SimulationEngine
from world.h3_world import H3World
from agents.agent import Agent, AgentClass
from knowledge.knowledge_graph import KnowledgeGraph


class TestPerformanceMetrics:
    """Test performance metrics and benchmarks."""
    
    @pytest.fixture
    def performance_logger(self):
        """Create performance logger."""
        return PerformanceLogger()
    
    @pytest.mark.asyncio
    async def test_agent_creation_performance(self, performance_logger):
        """Test agent creation performance."""
        agent_counts = [10, 50, 100, 500, 1000]
        creation_times = []
        
        for count in agent_counts:
            start_time = time.time()
            
            agents = []
            for i in range(count):
                agent = Agent(
                    agent_id=f"agent_{i}",
                    name=f"Agent{i}",
                    agent_class=AgentClass.EXPLORER,
                    initial_position=(i % 10, i // 10)
                )
                agents.append(agent)
            
            creation_time = time.time() - start_time
            creation_times.append(creation_time)
            
            performance_logger.log(
                "agent_creation",
                {
                    "count": count,
                    "total_time": creation_time,
                    "time_per_agent": creation_time / count
                }
            )
        
        # Verify linear or better scaling
        # Time per agent should not increase significantly
        time_per_agent = [t / c for t, c in zip(creation_times, agent_counts)]
        
        # Check that time per agent doesn't double
        assert time_per_agent[-1] < time_per_agent[0] * 2
    
    @pytest.mark.asyncio
    async def test_world_generation_performance(self, performance_logger):
        """Test world generation performance."""
        resolutions = [4, 5, 6, 7]
        generation_times = []
        cell_counts = []
        
        for resolution in resolutions:
            start_time = time.time()
            
            world = H3World(resolution=resolution)
            
            # Generate terrain and resources
            cells = world.get_all_cells()
            cell_counts.append(len(cells))
            
            for cell in cells[:1000]:  # Test first 1000 cells
                world.set_terrain(cell, np.random.choice(list(TerrainType)))
                if np.random.random() < 0.3:
                    world.add_resource(
                        cell,
                        np.random.choice(["food", "water", "materials"]),
                        np.random.randint(1, 20)
                    )
            
            generation_time = time.time() - start_time
            generation_times.append(generation_time)
            
            performance_logger.log(
                "world_generation",
                {
                    "resolution": resolution,
                    "cell_count": len(cells),
                    "generation_time": generation_time,
                    "time_per_cell": generation_time / min(1000, len(cells))
                }
            )
        
        # Verify reasonable scaling
        # Higher resolution means more cells, but time per cell should be stable
        time_per_cell = [t / min(1000, c) for t, c in zip(generation_times, cell_counts)]
        assert max(time_per_cell) < min(time_per_cell) * 3
    
    @pytest.mark.asyncio
    async def test_pathfinding_performance(self, performance_logger):
        """Test pathfinding algorithm performance."""
        world = H3World(resolution=6)
        
        # Test different path lengths
        path_test_cases = [
            (5, "short"),    # 5 steps
            (20, "medium"),  # 20 steps
            (50, "long"),    # 50 steps
            (100, "very_long")  # 100 steps
        ]
        
        results = []
        
        for target_length, category in path_test_cases:
            times = []
            
            for _ in range(10):  # 10 trials each
                # Random start and roughly estimated end
                start = world.get_random_cell()
                
                # Find a cell approximately target_length away
                candidates = []
                for _ in range(100):
                    end = world.get_random_cell()
                    estimate = world.estimate_distance(start, end)
                    if abs(estimate - target_length) < 5:
                        candidates.append(end)
                
                if not candidates:
                    continue
                
                end = np.random.choice(candidates)
                
                start_time = time.time()
                path = world.find_path(start, end)
                path_time = time.time() - start_time
                
                if path:
                    times.append(path_time)
            
            if times:
                avg_time = np.mean(times)
                results.append({
                    "category": category,
                    "target_length": target_length,
                    "avg_time": avg_time,
                    "trials": len(times)
                })
                
                performance_logger.log(
                    "pathfinding",
                    {
                        "category": category,
                        "avg_time": avg_time,
                        "max_time": max(times),
                        "min_time": min(times)
                    }
                )
        
        # Verify pathfinding scales reasonably
        if len(results) >= 2:
            short_time = results[0]["avg_time"]
            long_time = results[-1]["avg_time"]
            
            # Long paths shouldn't take more than 10x the time of short paths
            assert long_time < short_time * 10
    
    @pytest.mark.asyncio
    async def test_message_system_throughput(self, performance_logger):
        """Test message system throughput."""
        from communication.message_system import MessageSystem, MessageType
        
        message_system = MessageSystem()
        
        # Create test agents
        agents = []
        for i in range(20):
            agent = Agent(
                agent_id=f"agent_{i}",
                name=f"Agent{i}",
                agent_class=AgentClass.EXPLORER,
                initial_position=(i % 5, i // 5),
                message_system=message_system
            )
            agents.append(agent)
        
        # Test different message rates
        message_rates = [10, 50, 100, 500]  # messages per second
        
        for rate in message_rates:
            messages_sent = 0
            messages_received = 0
            
            start_time = time.time()
            duration = 5  # 5 second test
            
            # Send messages at specified rate
            while time.time() - start_time < duration:
                sender = np.random.choice(agents)
                receiver = np.random.choice(agents)
                
                if sender != receiver:
                    await sender.send_message(
                        receiver.agent_id,
                        MessageType.TEXT,
                        f"Test message {messages_sent}"
                    )
                    messages_sent += 1
                
                # Control rate
                await asyncio.sleep(1.0 / rate)
            
            # Allow processing
            await asyncio.sleep(0.5)
            
            # Count received messages
            for agent in agents:
                messages_received += len(agent.get_recent_messages(limit=1000))
            
            throughput = messages_received / duration
            delivery_rate = messages_received / messages_sent if messages_sent > 0 else 0
            
            performance_logger.log(
                "message_throughput",
                {
                    "target_rate": rate,
                    "messages_sent": messages_sent,
                    "messages_received": messages_received,
                    "actual_throughput": throughput,
                    "delivery_rate": delivery_rate
                }
            )
        
        # Verify high delivery rate
        assert delivery_rate > 0.95  # 95% delivery rate
    
    @pytest.mark.asyncio
    async def test_knowledge_graph_operations(self, performance_logger):
        """Test knowledge graph operation performance."""
        knowledge_graph = KnowledgeGraph()
        
        # Test node insertion
        node_counts = [100, 1000, 10000]
        
        for count in node_counts:
            # Node insertion
            start_time = time.time()
            
            for i in range(count):
                knowledge_graph.add_node(
                    f"node_{i}",
                    node_type="concept",
                    data={"value": i, "timestamp": time.time()}
                )
            
            insertion_time = time.time() - start_time
            
            # Edge creation (connect random nodes)
            edge_start_time = time.time()
            
            for i in range(count // 10):  # Create 10% as many edges
                node1 = f"node_{np.random.randint(count)}"
                node2 = f"node_{np.random.randint(count)}"
                
                if node1 != node2:
                    knowledge_graph.add_edge(
                        node1, node2,
                        edge_type="related",
                        weight=np.random.random()
                    )
            
            edge_time = time.time() - edge_start_time
            
            # Query performance
            query_times = []
            
            for _ in range(100):  # 100 random queries
                node = f"node_{np.random.randint(count)}"
                
                query_start = time.time()
                neighbors = knowledge_graph.get_neighbors(node)
                query_time = time.time() - query_start
                
                query_times.append(query_time)
            
            avg_query_time = np.mean(query_times)
            
            performance_logger.log(
                "knowledge_graph",
                {
                    "node_count": count,
                    "insertion_time": insertion_time,
                    "insertion_per_node": insertion_time / count,
                    "edge_creation_time": edge_time,
                    "avg_query_time": avg_query_time
                }
            )
            
            # Clear graph for next test
            knowledge_graph = KnowledgeGraph()
        
        # Verify query performance doesn't degrade too much
        # Even with 10k nodes, queries should be fast
        assert avg_query_time < 0.01  # Less than 10ms per query
    
    @pytest.mark.asyncio
    async def test_simulation_cycle_performance(self, performance_logger):
        """Test full simulation cycle performance."""
        configurations = [
            {"agents": 10, "world_size": 50},
            {"agents": 50, "world_size": 100},
            {"agents": 100, "world_size": 200}
        ]
        
        for config in configurations:
            engine = SimulationEngine({
                "world": {
                    "resolution": 5,
                    "size": config["world_size"]
                },
                "agents": {
                    "count": config["agents"]
                },
                "simulation": {
                    "max_cycles": 10
                }
            })
            
            await engine.initialize()
            await engine.start()
            
            cycle_times = []
            memory_usage = []
            
            process = psutil.Process()
            
            for _ in range(10):
                # Record memory before
                mem_before = process.memory_info().rss / 1024 / 1024
                
                start_time = time.time()
                await engine.step()
                cycle_time = time.time() - start_time
                
                # Record memory after
                mem_after = process.memory_info().rss / 1024 / 1024
                
                cycle_times.append(cycle_time)
                memory_usage.append(mem_after)
            
            avg_cycle_time = np.mean(cycle_times)
            max_memory = max(memory_usage)
            memory_growth = memory_usage[-1] - memory_usage[0]
            
            performance_logger.log(
                "simulation_cycle",
                {
                    "agent_count": config["agents"],
                    "world_size": config["world_size"],
                    "avg_cycle_time": avg_cycle_time,
                    "max_cycle_time": max(cycle_times),
                    "min_cycle_time": min(cycle_times),
                    "max_memory_mb": max_memory,
                    "memory_growth_mb": memory_growth
                }
            )
            
            await engine.stop()
        
        # Verify acceptable performance
        # 100 agents should complete cycle in reasonable time
        assert avg_cycle_time < 2.0  # Less than 2 seconds per cycle


class TestScalabilityLimits:
    """Test system scalability limits."""
    
    @pytest.mark.asyncio
    async def test_maximum_agent_capacity(self):
        """Test maximum number of agents system can handle."""
        max_agents_found = 0
        test_counts = [100, 500, 1000, 2000, 5000]
        
        for count in test_counts:
            try:
                config = {
                    "world": {
                        "resolution": 6,
                        "size": count * 2
                    },
                    "agents": {
                        "count": count
                    },
                    "simulation": {
                        "max_cycles": 5
                    }
                }
                
                engine = SimulationEngine(config)
                await engine.initialize()
                
                # Try to run a few cycles
                await engine.start()
                
                start_time = time.time()
                for _ in range(3):
                    await engine.step()
                    
                    # Check if taking too long
                    if time.time() - start_time > 30:
                        break
                
                await engine.stop()
                
                # If we got here, this count works
                max_agents_found = count
                
            except Exception as e:
                print(f"Failed at {count} agents: {e}")
                break
        
        # Should handle at least 500 agents
        assert max_agents_found >= 500
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test system under concurrent load."""
        engine = SimulationEngine({
            "world": {"resolution": 5, "size": 100},
            "agents": {"count": 50},
            "simulation": {"max_cycles": 20}
        })
        
        await engine.initialize()
        await engine.start()
        
        # Run simulation while performing concurrent operations
        async def simulation_task():
            for _ in range(10):
                await engine.step()
                await asyncio.sleep(0.1)
        
        async def query_task():
            for _ in range(50):
                # Random queries
                agents = engine.get_agents()
                if agents:
                    agent = np.random.choice(agents)
                    _ = agent.get_status()
                    _ = agent.knowledge_graph.get_all_nodes()
                await asyncio.sleep(0.05)
        
        async def analysis_task():
            for _ in range(20):
                # Analysis operations
                _ = await engine.get_system_health()
                _ = await engine.get_ecosystem_metrics()
                await asyncio.sleep(0.25)
        
        # Run all tasks concurrently
        tasks = [
            simulation_task(),
            query_task(),
            analysis_task()
        ]
        
        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time
        
        # Should complete in reasonable time without errors
        assert total_time < 30  # 30 seconds max
        
        # System should still be healthy
        health = await engine.get_system_health()
        assert health["status"] == "healthy"


class TestMemoryAndResourceUsage:
    """Test memory and resource usage patterns."""
    
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self):
        """Test for memory leaks during extended operation."""
        engine = SimulationEngine({
            "world": {"resolution": 5, "size": 50},
            "agents": {"count": 20},
            "simulation": {"max_cycles": 100}
        })
        
        await engine.initialize()
        await engine.start()
        
        process = psutil.Process()
        memory_samples = []
        
        # Run for extended period
        for i in range(50):
            await engine.step()
            
            if i % 5 == 0:
                # Sample memory usage
                memory_mb = process.memory_info().rss / 1024 / 1024
                memory_samples.append(memory_mb)
        
        # Analyze memory growth
        memory_growth_rate = np.polyfit(
            range(len(memory_samples)),
            memory_samples,
            1
        )[0]
        
        # Memory growth should be minimal (less than 1MB per 5 cycles)
        assert memory_growth_rate < 1.0
        
        # Total growth should be reasonable
        total_growth = memory_samples[-1] - memory_samples[0]
        assert total_growth < 50  # Less than 50MB growth
    
    @pytest.mark.asyncio
    async def test_resource_cleanup(self):
        """Test proper resource cleanup."""
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Create and destroy multiple simulations
        for _ in range(5):
            engine = SimulationEngine({
                "world": {"resolution": 5, "size": 50},
                "agents": {"count": 10},
                "simulation": {"max_cycles": 10}
            })
            
            await engine.initialize()
            await engine.start()
            
            for _ in range(10):
                await engine.step()
            
            await engine.stop()
            await engine.cleanup()
            
            # Force garbage collection
            import gc
            gc.collect()
        
        # Check final memory
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be minimal after cleanup
        assert memory_increase < 20  # Less than 20MB increase


class PerformanceLogger:
    """Logger for performance metrics."""
    
    def __init__(self):
        self.metrics = {}
        self.output_dir = Path("performance_results")
        self.output_dir.mkdir(exist_ok=True)
    
    def log(self, category: str, data: Dict[str, Any]):
        """Log performance metrics."""
        if category not in self.metrics:
            self.metrics[category] = []
        
        data["timestamp"] = time.time()
        self.metrics[category].append(data)
    
    def save_results(self):
        """Save performance results."""
        import json
        
        output_file = self.output_dir / f"performance_{int(time.time())}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        print(f"Performance results saved to: {output_file}")
    
    def generate_report(self):
        """Generate performance report with visualizations."""
        # Create performance plots
        for category, data in self.metrics.items():
            if not data:
                continue
            
            plt.figure(figsize=(10, 6))
            
            if category == "agent_creation":
                counts = [d["count"] for d in data]
                times = [d["time_per_agent"] * 1000 for d in data]  # Convert to ms
                
                plt.plot(counts, times, 'o-')
                plt.xlabel("Number of Agents")
                plt.ylabel("Time per Agent (ms)")
                plt.title("Agent Creation Performance")
                plt.grid(True)
                
            elif category == "simulation_cycle":
                agent_counts = [d["agent_count"] for d in data]
                cycle_times = [d["avg_cycle_time"] for d in data]
                
                plt.plot(agent_counts, cycle_times, 'o-')
                plt.xlabel("Number of Agents")
                plt.ylabel("Average Cycle Time (s)")
                plt.title("Simulation Cycle Performance")
                plt.grid(True)
            
            plot_file = self.output_dir / f"{category}_performance.png"
            plt.savefig(plot_file)
            plt.close()
            
            print(f"Generated plot: {plot_file}")


def run_performance_tests():
    """Run all performance tests."""
    pytest.main([__file__, "-v", "--asyncio-mode=auto", "-k", "performance"]) 