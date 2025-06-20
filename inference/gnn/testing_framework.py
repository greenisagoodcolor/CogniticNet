"""
Validation and Testing Framework for GNN Processing

This module provides comprehensive validation mechanisms and testing utilities
to ensure correctness of GNN processing operations.
"""
import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Callable, Union
from dataclasses import dataclass, field
import time
import logging
from collections import defaultdict
import json
import os
from pathlib import Path
from .parser import GNNParser
from .feature-extractor import NodeFeatureExtractor
from .edge-processor import EdgeProcessor
from .layers import GNNStack
from .model-mapper import GraphToModelMapper
from .batch-processor import GraphBatchProcessor, GraphData, BatchedGraphData
logger = logging.getLogger(__name__)

@dataclass
class ValidationMetrics:
    """Container for validation metrics"""
    accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    loss: float = 0.0
    node_accuracy: Optional[float] = None
    edge_accuracy: Optional[float] = None
    graph_accuracy: Optional[float] = None
    custom_metrics: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        result = {'accuracy': self.accuracy, 'precision': self.precision, 'recall': self.recall, 'f1_score': self.f1_score, 'loss': self.loss}
        if self.node_accuracy is not None:
            result['node_accuracy'] = self.node_accuracy
        if self.edge_accuracy is not None:
            result['edge_accuracy'] = self.edge_accuracy
        if self.graph_accuracy is not None:
            result['graph_accuracy'] = self.graph_accuracy
        result.update(self.custom_metrics)
        return result

@dataclass
class BenchmarkResult:
    """Container for benchmark results"""
    dataset_name: str
    num_graphs: int
    avg_nodes_per_graph: float
    avg_edges_per_graph: float
    processing_time: float
    memory_usage: float
    metrics: ValidationMetrics
    metadata: Dict[str, Any] = field(default_factory=dict)

class GNNValidator:
    """
    Validates GNN models and processing operations.

    Provides comprehensive validation for:
    - Model architecture correctness
    - Processing pipeline integrity
    - Output validity
    - Performance metrics
    """

    def __init__(self, tolerance: float=1e-06):
        """
        Initialize validator.

        Args:
            tolerance: Numerical tolerance for comparisons
        """
        self.tolerance = tolerance
        self.validation_history = []

    def validate_model_architecture(self, model: torch.nn.Module, sample_input: GraphData) -> Dict[str, Any]:
        """
        Validate model architecture.

        Args:
            model: GNN model to validate
            sample_input: Sample graph input

        Returns:
            Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': [], 'info': {}}
        try:
            model.eval()
            with torch.no_grad():
                batch_processor = GraphBatchProcessor()
                batch = batch_processor.create_batch([sample_input])
                output = model(batch.x, batch.edge_index, batch.batch)
                if output.dim() == 0:
                    results['errors'].append('Model output is scalar, expected tensor')
                    results['valid'] = False
                results['info']['output_shape'] = list(output.shape)
                results['info']['output_dtype'] = str(output.dtype)
        except Exception as e:
            results['errors'].append(f'Forward pass failed: {str(e)}')
            results['valid'] = False
        self._check_gradient_flow(model, results)
        self._check_parameter_initialization(model, results)
        return results

    def _check_gradient_flow(self, model: torch.nn.Module, results: Dict):
        """Check if gradients can flow through the model"""
        model.train()
        for param in model.parameters():
            if param.requires_grad:
                param.grad = None
        try:
            x = torch.randn(10, 32, requires_grad=True)
            edge_index = torch.randint(0, 10, (2, 20))
            batch = torch.zeros(10, dtype=torch.long)
            output = model(x, edge_index, batch)
            loss = output.sum()
            loss.backward()
            has_grad = False
            for param in model.parameters():
                if param.requires_grad and param.grad is not None:
                    has_grad = True
                    if torch.isnan(param.grad).any():
                        results['warnings'].append(f'NaN gradients detected')
                    if torch.isinf(param.grad).any():
                        results['warnings'].append(f'Inf gradients detected')
            if not has_grad:
                results['warnings'].append('No gradients computed')
        except Exception as e:
            results['warnings'].append(f'Gradient check failed: {str(e)}')

    def _check_parameter_initialization(self, model: torch.nn.Module, results: Dict):
        """Check parameter initialization"""
        for name, param in model.named_parameters():
            if torch.isnan(param).any():
                results['errors'].append(f'NaN values in parameter: {name}')
                results['valid'] = False
            if torch.isinf(param).any():
                results['errors'].append(f'Inf values in parameter: {name}')
                results['valid'] = False
            if param.abs().max() < 1e-08:
                results['warnings'].append(f'Parameter might be zero-initialized: {name}')

    def validate_processing_pipeline(self, pipeline_components: Dict[str, Any], test_graphs: List[GraphData]) -> Dict[str, Any]:
        """
        Validate complete processing pipeline.

        Args:
            pipeline_components: Dictionary of pipeline components
            test_graphs: Test graphs for validation

        Returns:
            Validation results
        """
        results = {'valid': True, 'component_results': {}, 'errors': [], 'warnings': []}
        if 'feature_extractor' in pipeline_components:
            self._validate_feature_extractor(pipeline_components['feature_extractor'], test_graphs, results)
        if 'edge_processor' in pipeline_components:
            self._validate_edge_processor(pipeline_components['edge_processor'], test_graphs, results)
        if 'batch_processor' in pipeline_components:
            self._validate_batch_processor(pipeline_components['batch_processor'], test_graphs, results)
        return results

    def _validate_feature_extractor(self, extractor: NodeFeatureExtractor, graphs: List[GraphData], results: Dict):
        """Validate feature extractor"""
        component_results = {'valid': True, 'errors': [], 'warnings': []}
        for i, graph in enumerate(graphs[:5]):
            try:
                nodes = [{'id': j, 'features': np.random.randn(10)} for j in range(graph.node_features.size(0))]
                result = extractor.extract_features(nodes)
                if result.features.shape[0] != len(nodes):
                    component_results['errors'].append(f'Graph {i}: Feature count mismatch')
                    component_results['valid'] = False
            except Exception as e:
                component_results['errors'].append(f'Graph {i}: Extraction failed - {str(e)}')
                component_results['valid'] = False
        results['component_results']['feature_extractor'] = component_results
        if not component_results['valid']:
            results['valid'] = False

    def _validate_edge_processor(self, processor: EdgeProcessor, graphs: List[GraphData], results: Dict):
        """Validate edge processor"""
        component_results = {'valid': True, 'errors': [], 'warnings': []}
        for i, graph in enumerate(graphs[:5]):
            try:
                if graph.edge_index.size(1) > 0:
                    max_idx = graph.edge_index.max().item()
                    num_nodes = graph.node_features.size(0)
                    if max_idx >= num_nodes:
                        component_results['errors'].append(f'Graph {i}: Invalid edge indices')
                        component_results['valid'] = False
            except Exception as e:
                component_results['errors'].append(f'Graph {i}: Edge processing failed - {str(e)}')
                component_results['valid'] = False
        results['component_results']['edge_processor'] = component_results
        if not component_results['valid']:
            results['valid'] = False

    def _validate_batch_processor(self, processor: GraphBatchProcessor, graphs: List[GraphData], results: Dict):
        """Validate batch processor"""
        component_results = {'valid': True, 'errors': [], 'warnings': []}
        try:
            batch = processor.create_batch(graphs)
            expected_nodes = sum((g.node_features.size(0) for g in graphs))
            if processor.pad_node_features:
                if batch.x.dim() != 3:
                    component_results['errors'].append('Padded batch should have 3 dimensions')
                    component_results['valid'] = False
            elif batch.x.size(0) != expected_nodes:
                component_results['errors'].append(f'Node count mismatch: {batch.x.size(0)} vs {expected_nodes}')
                component_results['valid'] = False
            unbatched = processor.unbatch(batch)
            if len(unbatched) != len(graphs):
                component_results['errors'].append(f'Unbatch count mismatch: {len(unbatched)} vs {len(graphs)}')
                component_results['valid'] = False
        except Exception as e:
            component_results['errors'].append(f'Batch processing failed: {str(e)}')
            component_results['valid'] = False
        results['component_results']['batch_processor'] = component_results
        if not component_results['valid']:
            results['valid'] = False

    def compute_metrics(self, predictions: torch.Tensor, targets: torch.Tensor, task_type: str='classification') -> ValidationMetrics:
        """
        Compute validation metrics.

        Args:
            predictions: Model predictions
            targets: Ground truth targets
            task_type: Type of task (classification/regression)

        Returns:
            Validation metrics
        """
        metrics = ValidationMetrics()
        if task_type == 'classification':
            if predictions.dim() > 1:
                pred_classes = predictions.argmax(dim=-1)
            else:
                pred_classes = (predictions > 0).long()
            correct = (pred_classes == targets).float()
            metrics.accuracy = correct.mean().item()
            num_classes = max(targets.max().item() + 1, pred_classes.max().item() + 1)
            if num_classes == 2:
                tp = ((pred_classes == 1) & (targets == 1)).sum().float()
                fp = ((pred_classes == 1) & (targets == 0)).sum().float()
                fn = ((pred_classes == 0) & (targets == 1)).sum().float()
                metrics.precision = (tp / (tp + fp + 1e-08)).item()
                metrics.recall = (tp / (tp + fn + 1e-08)).item()
                metrics.f1_score = 2 * metrics.precision * metrics.recall / (metrics.precision + metrics.recall + 1e-08)
            else:
                precisions = []
                recalls = []
                for c in range(num_classes):
                    tp = ((pred_classes == c) & (targets == c)).sum().float()
                    fp = ((pred_classes == c) & (targets != c)).sum().float()
                    fn = ((pred_classes != c) & (targets == c)).sum().float()
                    prec = (tp / (tp + fp + 1e-08)).item()
                    rec = (tp / (tp + fn + 1e-08)).item()
                    precisions.append(prec)
                    recalls.append(rec)
                metrics.precision = np.mean(precisions)
                metrics.recall = np.mean(recalls)
                metrics.f1_score = 2 * metrics.precision * metrics.recall / (metrics.precision + metrics.recall + 1e-08)
        elif task_type == 'regression':
            mse = ((predictions - targets) ** 2).mean()
            metrics.loss = mse.item()
            ss_res = ((targets - predictions) ** 2).sum()
            ss_tot = ((targets - targets.mean()) ** 2).sum()
            r2 = 1 - ss_res / (ss_tot + 1e-08)
            metrics.custom_metrics['r_squared'] = r2.item()
            mae = (predictions - targets).abs().mean()
            metrics.custom_metrics['mae'] = mae.item()
        return metrics

class GNNTestSuite:
    """
    Comprehensive test suite for GNN components.

    Provides utilities for:
    - Unit testing individual components
    - Integration testing
    - Performance benchmarking
    - Regression testing
    """

    def __init__(self, test_data_dir: Optional[str]=None):
        """
        Initialize test suite.

        Args:
            test_data_dir: Directory containing test data
        """
        self.test_data_dir = Path(test_data_dir) if test_data_dir else None
        self.test_results = []
        self.validator = GNNValidator()

    def run_unit_tests(self) -> Dict[str, Any]:
        """
        Run unit tests for all components.

        Returns:
            Test results
        """
        results = {'total_tests': 0, 'passed': 0, 'failed': 0, 'errors': [], 'component_results': {}}
        self._test_parser(results)
        self._test_feature_extractor(results)
        self._test_edge_processor(results)
        self._test_layers(results)
        self._test_batch_processor(results)
        return results

    def _test_parser(self, results: Dict):
        """Test GNN parser"""
        component_results = {'passed': 0, 'failed': 0, 'errors': []}
        parser = GNNParser()
        try:
            valid_model = '\n---\nname: TestModel\ntype: graph_neural_network\nversion: 1.0\n---\n\n## Architecture\n\n```yaml\nlayers:\n  - type: GCN\n    units: 64\n```\n'
            parsed = parser.parse(valid_model)
            if parsed and 'architecture' in parsed:
                component_results['passed'] += 1
            else:
                component_results['failed'] += 1
                component_results['errors'].append('Failed to parse valid model')
        except Exception as e:
            component_results['failed'] += 1
            component_results['errors'].append(f'Parser error: {str(e)}')
        results['total_tests'] += 1
        results['passed'] += component_results['passed']
        results['failed'] += component_results['failed']
        results['component_results']['parser'] = component_results

    def _test_feature_extractor(self, results: Dict):
        """Test feature extractor"""
        component_results = {'passed': 0, 'failed': 0, 'errors': []}
        extractor = NodeFeatureExtractor()
        try:
            nodes = [{'id': 0, 'features': [1.0, 2.0, 3.0]}, {'id': 1, 'features': [4.0, 5.0, 6.0]}]
            result = extractor.extract_features(nodes)
            if result.features.shape == (2, 3):
                component_results['passed'] += 1
            else:
                component_results['failed'] += 1
                component_results['errors'].append('Incorrect feature shape')
        except Exception as e:
            component_results['failed'] += 1
            component_results['errors'].append(f'Extraction error: {str(e)}')
        results['total_tests'] += 1
        results['passed'] += component_results['passed']
        results['failed'] += component_results['failed']
        results['component_results']['feature_extractor'] = component_results

    def _test_edge_processor(self, results: Dict):
        """Test edge processor"""
        component_results = {'passed': 0, 'failed': 0, 'errors': []}
        processor = EdgeProcessor()
        try:
            edges = [(0, 1), (1, 2), (2, 0)]
            edge_index = processor.edge_list_to_tensor(edges)
            if edge_index.shape == (2, 3):
                component_results['passed'] += 1
            else:
                component_results['failed'] += 1
                component_results['errors'].append('Incorrect edge tensor shape')
        except Exception as e:
            component_results['failed'] += 1
            component_results['errors'].append(f'Edge processing error: {str(e)}')
        results['total_tests'] += 1
        results['passed'] += component_results['passed']
        results['failed'] += component_results['failed']
        results['component_results']['edge_processor'] = component_results

    def _test_layers(self, results: Dict):
        """Test GNN layers"""
        component_results = {'passed': 0, 'failed': 0, 'errors': []}
        try:
            from .layers import GCNLayer
            layer = GCNLayer(32, 64)
            x = torch.randn(10, 32)
            edge_index = torch.randint(0, 10, (2, 20))
            output = layer(x, edge_index)
            if output.shape == (10, 64):
                component_results['passed'] += 1
            else:
                component_results['failed'] += 1
                component_results['errors'].append('GCN output shape incorrect')
        except Exception as e:
            component_results['failed'] += 1
            component_results['errors'].append(f'GCN layer error: {str(e)}')
        results['total_tests'] += 1
        results['passed'] += component_results['passed']
        results['failed'] += component_results['failed']
        results['component_results']['layers'] = component_results

    def _test_batch_processor(self, results: Dict):
        """Test batch processor"""
        component_results = {'passed': 0, 'failed': 0, 'errors': []}
        processor = GraphBatchProcessor()
        try:
            graphs = [GraphData(node_features=torch.randn(5, 16), edge_index=torch.randint(0, 5, (2, 10))) for _ in range(3)]
            batch = processor.create_batch(graphs)
            if batch.num_graphs == 3:
                component_results['passed'] += 1
            else:
                component_results['failed'] += 1
                component_results['errors'].append('Incorrect batch size')
        except Exception as e:
            component_results['failed'] += 1
            component_results['errors'].append(f'Batching error: {str(e)}')
        results['total_tests'] += 1
        results['passed'] += component_results['passed']
        results['failed'] += component_results['failed']
        results['component_results']['batch_processor'] = component_results

    def run_integration_tests(self, model: torch.nn.Module, test_graphs: List[GraphData]) -> Dict[str, Any]:
        """
        Run integration tests.

        Args:
            model: GNN model to test
            test_graphs: Test graphs

        Returns:
            Test results
        """
        results = {'passed': True, 'errors': [], 'warnings': [], 'performance': {}}
        try:
            processor = GraphBatchProcessor()
            batch = processor.create_batch(test_graphs)
            start_time = time.time()
            with torch.no_grad():
                output = model(batch.x, batch.edge_index, batch.batch)
            results['performance']['inference_time'] = time.time() - start_time
            results['performance']['graphs_per_second'] = len(test_graphs) / results['performance']['inference_time']
        except Exception as e:
            results['passed'] = False
            results['errors'].append(f'Integration test failed: {str(e)}')
        return results

    def benchmark_model(self, model: torch.nn.Module, benchmark_datasets: Dict[str, List[GraphData]], num_runs: int=10) -> List[BenchmarkResult]:
        """
        Benchmark model on standard datasets.

        Args:
            model: Model to benchmark
            benchmark_datasets: Dictionary of dataset name to graphs
            num_runs: Number of runs for timing

        Returns:
            List of benchmark results
        """
        results = []
        for dataset_name, graphs in benchmark_datasets.items():
            logger.info(f'Benchmarking on {dataset_name}...')
            num_nodes = [g.node_features.size(0) for g in graphs]
            num_edges = [g.edge_index.size(1) for g in graphs]
            avg_nodes = np.mean(num_nodes)
            avg_edges = np.mean(num_edges)
            processor = GraphBatchProcessor()
            batch = processor.create_batch(graphs)
            times = []
            model.eval()
            for _ in range(num_runs):
                start_time = time.time()
                with torch.no_grad():
                    output = model(batch.x, batch.edge_index, batch.batch)
                times.append(time.time() - start_time)
            avg_time = np.mean(times[1:])
            memory_usage = (batch.x.element_size() * batch.x.nelement() + batch.edge_index.element_size() * batch.edge_index.nelement()) / 1024 / 1024
            metrics = ValidationMetrics(accuracy=0.0, loss=0.0)
            result = BenchmarkResult(dataset_name=dataset_name, num_graphs=len(graphs), avg_nodes_per_graph=avg_nodes, avg_edges_per_graph=avg_edges, processing_time=avg_time, memory_usage=memory_usage, metrics=metrics)
            results.append(result)
        return results

def create_test_graphs(num_graphs: int=10, min_nodes: int=5, max_nodes: int=20, feature_dim: int=32) -> List[GraphData]:
    """
    Create synthetic test graphs.

    Args:
        num_graphs: Number of graphs to create
        min_nodes: Minimum nodes per graph
        max_nodes: Maximum nodes per graph
        feature_dim: Node feature dimension

    Returns:
        List of test graphs
    """
    graphs = []
    for i in range(num_graphs):
        num_nodes = np.random.randint(min_nodes, max_nodes + 1)
        num_edges = np.random.randint(num_nodes, num_nodes * 3)
        node_features = torch.randn(num_nodes, feature_dim)
        edge_index = torch.randint(0, num_nodes, (2, num_edges))
        edge_attr = torch.randn(num_edges, 8) if np.random.rand() > 0.5 else None
        target = torch.tensor([i % 3])
        graph = GraphData(node_features=node_features, edge_index=edge_index, edge_attr=edge_attr, target=target)
        graphs.append(graph)
    return graphs
if __name__ == '__main__':
    test_suite = GNNTestSuite()
    print('Running unit tests...')
    unit_results = test_suite.run_unit_tests()
    print(f"Unit tests: {unit_results['passed']}/{unit_results['total_tests']} passed")
    from .layers import GNNStack
    model = GNNStack(input_dim=32, hidden_dims=[64, 64], output_dim=3, layer_type='GCN', dropout=0.5)
    test_graphs = create_test_graphs(20)
    print('\nRunning integration tests...')
    integration_results = test_suite.run_integration_tests(model, test_graphs)
    print(f"Integration tests passed: {integration_results['passed']}")
    print('\nRunning benchmarks...')
    benchmark_datasets = {'small': create_test_graphs(100, 5, 10), 'medium': create_test_graphs(100, 20, 50), 'large': create_test_graphs(100, 100, 200)}
    benchmark_results = test_suite.benchmark_model(model, benchmark_datasets)
    for result in benchmark_results:
        print(f'\n{result.dataset_name}:')
        print(f'  Graphs: {result.num_graphs}')
        print(f'  Avg nodes: {result.avg_nodes_per_graph:.1f}')
        print(f'  Avg edges: {result.avg_edges_per_graph:.1f}')
        print(f'  Processing time: {result.processing_time:.3f}s')
        print(f'  Memory usage: {result.memory_usage:.1f} MB')
