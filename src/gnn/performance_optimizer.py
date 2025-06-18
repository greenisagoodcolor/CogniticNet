"""
Performance Optimization Module for GNN Processing

This module provides various optimization techniques to improve the performance
of GNN processing operations including memory optimization, hardware acceleration,
caching, and parallel processing.
"""

import torch
import torch.nn as nn
import torch.cuda.amp as amp
from torch.utils.checkpoint import checkpoint
import numpy as np
from typing import Dict, List, Optional, Any, Callable, Union, Tuple
from dataclasses import dataclass, field
import threading
import multiprocessing as mp
from functools import lru_cache, wraps
import time
import psutil
import os
from pathlib import Path
import pickle
from collections import defaultdict

from .monitoring import get_monitor, monitor_performance, get_logger

# Configure logger
logger = get_logger().logger


@dataclass
class OptimizationConfig:
    """Configuration for performance optimizations"""
    enable_mixed_precision: bool = True
    enable_gradient_checkpointing: bool = False
    enable_graph_caching: bool = True
    enable_cuda_graphs: bool = False
    enable_memory_efficient_attention: bool = True
    num_workers: int = 4
    prefetch_factor: int = 2
    pin_memory: bool = True
    max_cache_size_mb: int = 1024
    enable_profiling: bool = False
    optimize_for_inference: bool = False


class MemoryOptimizer:
    """
    Optimizes memory usage for large graph processing.

    Features:
    - Dynamic memory allocation
    - Gradient checkpointing
    - Memory-efficient operations
    - Automatic garbage collection
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize memory optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self._memory_threshold_mb = 1024  # 1GB threshold for optimization

    def optimize_model(self, model: nn.Module) -> nn.Module:
        """
        Apply memory optimizations to model.

        Args:
            model: PyTorch model to optimize

        Returns:
            Optimized model
        """
        # Enable gradient checkpointing for deep models
        if self.config.enable_gradient_checkpointing:
            self._enable_gradient_checkpointing(model)

        # Convert to half precision if enabled
        if self.config.enable_mixed_precision and torch.cuda.is_available():
            model = model.half()

        # Enable memory efficient attention
        if self.config.enable_memory_efficient_attention:
            self._optimize_attention_layers(model)

        # Optimize for inference if specified
        if self.config.optimize_for_inference:
            model.eval()
            for param in model.parameters():
                param.requires_grad = False

        return model

    def _enable_gradient_checkpointing(self, model: nn.Module):
        """Enable gradient checkpointing for specific layers"""
        def checkpoint_wrapper(module, *args, **kwargs):
            if module.training:
                return checkpoint(module._forward_impl, *args, **kwargs)
            else:
                return module._forward_impl(*args, **kwargs)

        # Wrap forward methods of heavy layers
        for name, module in model.named_modules():
            if hasattr(module, '_forward_impl'):
                module.forward = lambda *args, m=module, **kwargs: checkpoint_wrapper(m, *args, **kwargs)

    def _optimize_attention_layers(self, model: nn.Module):
        """Optimize attention layers for memory efficiency"""
        for module in model.modules():
            if hasattr(module, 'attention_dropout'):
                # Use memory-efficient attention implementation
                module.use_flash_attention = True

    @staticmethod
    def optimize_batch_processing(
        batch_size: int,
        available_memory_mb: float,
        node_features_dim: int,
        avg_nodes_per_graph: int
    ) -> int:
        """
        Calculate optimal batch size based on available memory.

        Args:
            batch_size: Requested batch size
            available_memory_mb: Available memory in MB
            node_features_dim: Dimension of node features
            avg_nodes_per_graph: Average nodes per graph

        Returns:
            Optimized batch size
        """
        # Estimate memory per graph (rough estimation)
        bytes_per_float = 4  # float32
        memory_per_graph_mb = (
            avg_nodes_per_graph * node_features_dim * bytes_per_float / 1024 / 1024
        )

        # Add overhead for gradients and activations (3x multiplier)
        memory_per_graph_mb *= 3

        # Calculate maximum batch size
        max_batch_size = int(available_memory_mb / memory_per_graph_mb)

        # Return minimum of requested and maximum
        return min(batch_size, max(max_batch_size, 1))

    def clear_cache(self):
        """Clear GPU cache and run garbage collection"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()

        # Force garbage collection
        import gc
        gc.collect()


class HardwareAccelerator:
    """
    Manages hardware acceleration for GNN processing.

    Features:
    - GPU/TPU detection and setup
    - Mixed precision training
    - CUDA graphs for inference
    - Multi-GPU support
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize hardware accelerator.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.device = self._detect_device()
        self.scaler = None

        if self.config.enable_mixed_precision and self.device.type == 'cuda':
            self.scaler = amp.GradScaler()

    def _detect_device(self) -> torch.device:
        """Detect and return best available device"""
        if torch.cuda.is_available():
            # Get GPU with most free memory
            if torch.cuda.device_count() > 1:
                free_memory = []
                for i in range(torch.cuda.device_count()):
                    torch.cuda.set_device(i)
                    free_memory.append(
                        torch.cuda.get_device_properties(i).total_memory -
                        torch.cuda.memory_allocated(i)
                    )
                best_gpu = np.argmax(free_memory)
                return torch.device(f'cuda:{best_gpu}')
            else:
                return torch.device('cuda:0')
        else:
            return torch.device('cpu')

    def accelerate_forward(
        self,
        model: nn.Module,
        forward_fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Accelerate forward pass with mixed precision.

        Args:
            model: Model to run
            forward_fn: Forward function
            *args: Forward function arguments
            **kwargs: Forward function keyword arguments

        Returns:
            Forward pass output
        """
        if self.config.enable_mixed_precision and self.device.type == 'cuda':
            with amp.autocast():
                return forward_fn(*args, **kwargs)
        else:
            return forward_fn(*args, **kwargs)

    def accelerate_backward(self, loss: torch.Tensor, optimizer: torch.optim.Optimizer):
        """
        Accelerate backward pass with mixed precision.

        Args:
            loss: Loss tensor
            optimizer: Optimizer
        """
        if self.scaler is not None:
            self.scaler.scale(loss).backward()
            self.scaler.step(optimizer)
            self.scaler.update()
        else:
            loss.backward()
            optimizer.step()

    def create_cuda_graph(self, model: nn.Module, sample_input: torch.Tensor) -> Callable:
        """
        Create CUDA graph for faster inference.

        Args:
            model: Model to create graph for
            sample_input: Sample input tensor

        Returns:
            CUDA graph callable
        """
        if not (self.config.enable_cuda_graphs and self.device.type == 'cuda'):
            return lambda x: model(x)

        # Warmup
        static_input = sample_input.clone()
        static_output = model(static_input)

        # Create graph
        graph = torch.cuda.CUDAGraph()
        with torch.cuda.graph(graph):
            static_output = model(static_input)

        def cuda_graph_forward(input_tensor):
            static_input.copy_(input_tensor)
            graph.replay()
            return static_output.clone()

        return cuda_graph_forward

    def setup_distributed(self, rank: int, world_size: int):
        """Setup distributed training"""
        if self.device.type == 'cuda':
            torch.cuda.set_device(rank)
            torch.distributed.init_process_group(
                backend='nccl',
                rank=rank,
                world_size=world_size
            )


class GraphCache:
    """
    Caching mechanism for graph processing results.

    Features:
    - LRU cache for processed features
    - Persistent cache storage
    - Memory-aware caching
    - Thread-safe operations
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize graph cache.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.cache_dir = Path('.cache/gnn')
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache
        self._memory_cache = {}
        self._cache_size_mb = 0
        self._lock = threading.Lock()

        # Cache statistics
        self.hits = 0
        self.misses = 0

    def cache_key(self, graph_id: str, operation: str) -> str:
        """Generate cache key"""
        return f"{graph_id}_{operation}"

    def get(self, graph_id: str, operation: str) -> Optional[Any]:
        """
        Get cached result.

        Args:
            graph_id: Graph identifier
            operation: Operation identifier

        Returns:
            Cached result or None
        """
        if not self.config.enable_graph_caching:
            return None

        key = self.cache_key(graph_id, operation)

        with self._lock:
            # Check memory cache
            if key in self._memory_cache:
                self.hits += 1
                return self._memory_cache[key]

            # Check disk cache
            cache_file = self.cache_dir / f"{key}.pkl"
            if cache_file.exists():
                try:
                    with open(cache_file, 'rb') as f:
                        data = pickle.load(f)

                    # Add to memory cache if space available
                    self._add_to_memory_cache(key, data)
                    self.hits += 1
                    return data
                except Exception as e:
                    logger.error(f"Failed to load cache: {e}")

            self.misses += 1
            return None

    def set(self, graph_id: str, operation: str, data: Any):
        """
        Cache result.

        Args:
            graph_id: Graph identifier
            operation: Operation identifier
            data: Data to cache
        """
        if not self.config.enable_graph_caching:
            return

        key = self.cache_key(graph_id, operation)

        with self._lock:
            # Add to memory cache
            self._add_to_memory_cache(key, data)

            # Save to disk
            cache_file = self.cache_dir / f"{key}.pkl"
            try:
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            except Exception as e:
                logger.error(f"Failed to save cache: {e}")

    def _add_to_memory_cache(self, key: str, data: Any):
        """Add data to memory cache with size management"""
        # Estimate size (rough)
        size_mb = self._estimate_size_mb(data)

        # Check if we need to evict
        while (self._cache_size_mb + size_mb > self.config.max_cache_size_mb and
               len(self._memory_cache) > 0):
            # Evict oldest entry (simple FIFO for now)
            evict_key = next(iter(self._memory_cache))
            evicted_data = self._memory_cache.pop(evict_key)
            self._cache_size_mb -= self._estimate_size_mb(evicted_data)

        # Add to cache
        self._memory_cache[key] = data
        self._cache_size_mb += size_mb

    def _estimate_size_mb(self, data: Any) -> float:
        """Estimate size of data in MB"""
        if isinstance(data, torch.Tensor):
            return data.element_size() * data.nelement() / 1024 / 1024
        elif isinstance(data, np.ndarray):
            return data.nbytes / 1024 / 1024
        else:
            # Rough estimate for other types
            return 1.0

    def clear(self):
        """Clear all caches"""
        with self._lock:
            self._memory_cache.clear()
            self._cache_size_mb = 0

            # Clear disk cache
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0

        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'memory_size_mb': self._cache_size_mb,
            'memory_items': len(self._memory_cache)
        }


class ParallelProcessor:
    """
    Implements parallel processing for graph operations.

    Features:
    - Multi-threaded data loading
    - Parallel feature extraction
    - Distributed graph processing
    - Asynchronous operations
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize parallel processor.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.num_workers = min(config.num_workers, mp.cpu_count())

    def parallel_feature_extraction(
        self,
        graphs: List[Dict[str, Any]],
        extractor_fn: Callable
    ) -> List[Any]:
        """
        Extract features from multiple graphs in parallel.

        Args:
            graphs: List of graphs
            extractor_fn: Feature extraction function

        Returns:
            List of extracted features
        """
        if len(graphs) < self.num_workers * 2:
            # Not worth parallelizing for small datasets
            return [extractor_fn(g) for g in graphs]

        with mp.Pool(processes=self.num_workers) as pool:
            results = pool.map(extractor_fn, graphs)

        return results

    def create_data_loader(
        self,
        dataset: Any,
        batch_size: int,
        shuffle: bool = True
    ) -> torch.utils.data.DataLoader:
        """
        Create optimized data loader.

        Args:
            dataset: PyTorch dataset
            batch_size: Batch size
            shuffle: Whether to shuffle data

        Returns:
            Optimized DataLoader
        """
        return torch.utils.data.DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=shuffle,
            num_workers=self.num_workers,
            pin_memory=self.config.pin_memory,
            prefetch_factor=self.config.prefetch_factor,
            persistent_workers=self.num_workers > 0
        )

    def parallel_graph_processing(
        self,
        graphs: List[Any],
        process_fn: Callable,
        chunk_size: Optional[int] = None
    ) -> List[Any]:
        """
        Process multiple graphs in parallel chunks.

        Args:
            graphs: List of graphs to process
            process_fn: Processing function
            chunk_size: Size of chunks for processing

        Returns:
            List of processed results
        """
        if chunk_size is None:
            chunk_size = max(1, len(graphs) // (self.num_workers * 4))

        # Split into chunks
        chunks = [graphs[i:i + chunk_size] for i in range(0, len(graphs), chunk_size)]

        # Process chunks in parallel
        with mp.Pool(processes=self.num_workers) as pool:
            chunk_results = pool.map(
                lambda chunk: [process_fn(g) for g in chunk],
                chunks
            )

        # Flatten results
        results = []
        for chunk_result in chunk_results:
            results.extend(chunk_result)

        return results


class PerformanceProfiler:
    """
    Profile GNN operations to identify bottlenecks.

    Features:
    - Operation timing
    - Memory profiling
    - GPU utilization tracking
    - Bottleneck identification
    """

    def __init__(self, config: OptimizationConfig):
        """
        Initialize profiler.

        Args:
            config: Optimization configuration
        """
        self.config = config
        self.profiles = defaultdict(list)
        self._profiler = None

    def start_profiling(self):
        """Start profiling session"""
        if not self.config.enable_profiling:
            return

        if torch.cuda.is_available():
            self._profiler = torch.profiler.profile(
                activities=[
                    torch.profiler.ProfilerActivity.CPU,
                    torch.profiler.ProfilerActivity.CUDA
                ],
                record_shapes=True,
                profile_memory=True,
                with_stack=True
            )
            self._profiler.__enter__()

    def stop_profiling(self) -> Optional[str]:
        """
        Stop profiling and return report.

        Returns:
            Profiling report or None
        """
        if self._profiler is None:
            return None

        self._profiler.__exit__(None, None, None)

        # Generate report
        report = self._profiler.key_averages().table(
            sort_by="cpu_time_total", row_limit=20
        )

        # Save trace
        trace_file = f"gnn_profile_{int(time.time())}.json"
        self._profiler.export_chrome_trace(trace_file)

        self._profiler = None

        return report

    @monitor_performance("profiled_operation")
    def profile_operation(self, operation_name: str, operation_fn: Callable, *args, **kwargs) -> Any:
        """
        Profile a specific operation.

        Args:
            operation_name: Name of operation
            operation_fn: Operation function
            *args: Operation arguments
            **kwargs: Operation keyword arguments

        Returns:
            Operation result
        """
        start_time = time.time()
        start_memory = 0

        if torch.cuda.is_available():
            torch.cuda.synchronize()
            start_memory = torch.cuda.memory_allocated()

        # Run operation
        result = operation_fn(*args, **kwargs)

        if torch.cuda.is_available():
            torch.cuda.synchronize()
            end_memory = torch.cuda.memory_allocated()
            memory_used = (end_memory - start_memory) / 1024 / 1024  # MB
        else:
            memory_used = 0

        end_time = time.time()
        duration = end_time - start_time

        # Store profile
        self.profiles[operation_name].append({
            'duration': duration,
            'memory_mb': memory_used,
            'timestamp': start_time
        })

        return result

    def get_bottlenecks(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Identify top bottlenecks.

        Args:
            top_k: Number of top bottlenecks to return

        Returns:
            List of bottleneck operations
        """
        bottlenecks = []

        for operation, profiles in self.profiles.items():
            if not profiles:
                continue

            avg_duration = np.mean([p['duration'] for p in profiles])
            avg_memory = np.mean([p['memory_mb'] for p in profiles])
            total_time = sum(p['duration'] for p in profiles)

            bottlenecks.append({
                'operation': operation,
                'avg_duration': avg_duration,
                'total_time': total_time,
                'avg_memory_mb': avg_memory,
                'call_count': len(profiles)
            })

        # Sort by total time
        bottlenecks.sort(key=lambda x: x['total_time'], reverse=True)

        return bottlenecks[:top_k]


class PerformanceOptimizer:
    """
    Main performance optimization orchestrator.

    Combines all optimization techniques for maximum performance.
    """

    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize performance optimizer.

        Args:
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()

        # Initialize components
        self.memory_optimizer = MemoryOptimizer(self.config)
        self.hardware_accelerator = HardwareAccelerator(self.config)
        self.cache = GraphCache(self.config)
        self.parallel_processor = ParallelProcessor(self.config)
        self.profiler = PerformanceProfiler(self.config)

        logger.info("Performance optimizer initialized")

    def optimize_model(self, model: nn.Module) -> nn.Module:
        """
        Apply all optimizations to model.

        Args:
            model: Model to optimize

        Returns:
            Optimized model
        """
        # Memory optimizations
        model = self.memory_optimizer.optimize_model(model)

        # Move to accelerator device
        model = model.to(self.hardware_accelerator.device)

        return model

    def optimize_batch_size(
        self,
        requested_batch_size: int,
        node_features_dim: int,
        avg_nodes_per_graph: int
    ) -> int:
        """
        Calculate optimal batch size.

        Args:
            requested_batch_size: Requested batch size
            node_features_dim: Node feature dimension
            avg_nodes_per_graph: Average nodes per graph

        Returns:
            Optimized batch size
        """
        if self.hardware_accelerator.device.type == 'cuda':
            # Get available GPU memory
            available_memory = (
                torch.cuda.get_device_properties(0).total_memory -
                torch.cuda.memory_allocated()
            ) / 1024 / 1024  # MB
        else:
            # Get available system memory
            available_memory = psutil.virtual_memory().available / 1024 / 1024

        return self.memory_optimizer.optimize_batch_processing(
            requested_batch_size,
            available_memory * 0.8,  # Use 80% of available memory
            node_features_dim,
            avg_nodes_per_graph
        )

    def cached_forward(
        self,
        graph_id: str,
        forward_fn: Callable,
        *args,
        **kwargs
    ) -> Any:
        """
        Forward pass with caching.

        Args:
            graph_id: Graph identifier
            forward_fn: Forward function
            *args: Forward arguments
            **kwargs: Forward keyword arguments

        Returns:
            Forward result
        """
        # Check cache
        cached_result = self.cache.get(graph_id, 'forward')
        if cached_result is not None:
            return cached_result

        # Run forward pass
        result = forward_fn(*args, **kwargs)

        # Cache result
        self.cache.set(graph_id, 'forward', result)

        return result

    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        stats = {
            'device': str(self.hardware_accelerator.device),
            'mixed_precision': self.config.enable_mixed_precision,
            'cache_stats': self.cache.get_stats(),
            'parallel_workers': self.parallel_processor.num_workers
        }

        if self.config.enable_profiling:
            stats['bottlenecks'] = self.profiler.get_bottlenecks()

        return stats


# Optimization decorators
def optimize_for_inference(func):
    """Decorator to optimize function for inference"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with torch.no_grad():
            with torch.cuda.amp.autocast(enabled=torch.cuda.is_available()):
                return func(*args, **kwargs)
    return wrapper


def cache_result(cache_key_fn: Callable):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if hasattr(self, 'cache'):
                key = cache_key_fn(*args, **kwargs)
                cached = self.cache.get(key, func.__name__)
                if cached is not None:
                    return cached

                result = func(self, *args, **kwargs)
                self.cache.set(key, func.__name__, result)
                return result
            else:
                return func(self, *args, **kwargs)
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Create optimizer
    config = OptimizationConfig(
        enable_mixed_precision=True,
        enable_gradient_checkpointing=True,
        enable_graph_caching=True,
        num_workers=4
    )

    optimizer = PerformanceOptimizer(config)

    # Example model optimization
    from .layers import GNNStack

    model = GNNStack(
        input_dim=32,
        hidden_dims=[64, 64, 32],
        output_dim=10,
        architecture='gcn'
    )

    # Optimize model
    model = optimizer.optimize_model(model)

    print(f"Model device: {next(model.parameters()).device}")
    print(f"Optimization stats: {optimizer.get_optimization_stats()}")

    # Profile an operation
    optimizer.profiler.start_profiling()

    x = torch.randn(100, 32).to(optimizer.hardware_accelerator.device)
    edge_index = torch.randint(0, 100, (2, 300)).to(optimizer.hardware_accelerator.device)

    output = optimizer.profiler.profile_operation(
        "forward_pass",
        model,
        x,
        edge_index
    )

    report = optimizer.profiler.stop_profiling()
    if report:
        print("\nProfiling Report:")
        print(report)
