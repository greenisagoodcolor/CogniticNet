"""
Integration tests for GNN Processing Pipeline

Tests the complete end-to-end functionality of the GNN processing system.
"""

import pytest
import torch
import numpy as np
import tempfile
import os
from pathlib import Path

from inference.gnn.parser import GNNParser
from inference.gnn.feature_extractor import NodeFeatureExtractor
from inference.gnn.edge_processor import EdgeProcessor
from inference.gnn.layers import GNNStack, GCNLayer, GATLayer
from inference.gnn.model_mapper import GraphToModelMapper
from inference.gnn.batch_processor import GraphBatchProcessor, GraphData
from inference.gnn.testing_framework import GNNValidator, GNNTestSuite, create_test_graphs


class TestGNNPipelineIntegration:
    """Test complete GNN processing pipeline"""

    def test_parser_to_model_pipeline(self):
        """Test parsing GNN model and creating architecture"""
        # Create sample GNN model file
        model_content = """
---
name: TestIntegrationModel
type: graph_neural_network
version: 1.0
task: node_classification
---

## Architecture

```yaml
layers:
  - type: GCN
    units: 64
    activation: relu
    dropout: 0.5
  - type: GCN
    units: 32
    activation: relu
    dropout: 0.5
  - type: GCN
    units: 10
    activation: softmax
```

## Training

```yaml
optimizer: adam
learning_rate: 0.01
epochs: 100
batch_size: 32
```
"""

        # Parse model
        parser = GNNParser()
        parsed_model = parser.parse(model_content)

        assert parsed_model is not None
        assert 'architecture' in parsed_model
        assert 'training' in parsed_model

        # Create model from parsed config
        architecture = parsed_model['architecture']
        layers = architecture.get('layers', [])

        assert len(layers) == 3
        assert layers[0]['type'] == 'GCN'
        assert layers[0]['units'] == 64

    def test_feature_extraction_pipeline(self):
        """Test feature extraction integration"""
        # Create feature extractor
        extractor = NodeFeatureExtractor(
            feature_types=['spatial', 'numerical', 'categorical']
        )

        # Create sample nodes with various features
        nodes = []
        for i in range(10):
            node = {
                'id': i,
                'position': {'lat': 40.7 + i * 0.01, 'lon': -74.0 + i * 0.01},
                'features': np.random.randn(5),
                'category': f'type_{i % 3}'
            }
            nodes.append(node)

        # Extract features
        result = extractor.extract_features(nodes)

        assert result.features.shape[0] == 10
        assert result.features.shape[1] > 5  # Should include spatial + numerical + categorical
        assert not torch.isnan(result.features).any()

    def test_edge_processing_pipeline(self):
        """Test edge processing integration"""
        processor = EdgeProcessor()

        # Create edges with various attributes
        edges = []
        for i in range(20):
            edge = {
                'source': i % 10,
                'target': (i + 1) % 10,
                'weight': np.random.rand(),
                'type': 'connection' if i % 2 == 0 else 'relation'
            }
            edges.append(edge)

        # Process edges
        edge_batch = processor.process_edges(edges)

        assert edge_batch.edge_index.shape == (2, 20)
        assert edge_batch.edge_weight.shape == (20,)
        assert edge_batch.edge_attr is not None

    def test_batch_processing_pipeline(self):
        """Test batch processing integration"""
        # Create batch processor
        batch_processor = GraphBatchProcessor(
            pad_node_features=True,
            max_nodes_per_graph=50
        )

        # Create multiple graphs
        graphs = create_test_graphs(
            num_graphs=5,
            min_nodes=10,
            max_nodes=30,
            feature_dim=16
        )

        # Create batch
        batch = batch_processor.create_batch(graphs)

        assert batch.num_graphs == 5
        assert batch.x.shape[2] == 16  # Feature dimension
        assert batch.mask is not None

        # Test unbatching
        unbatched = batch_processor.unbatch(batch)
        assert len(unbatched) == 5

        # Verify unbatched graphs match original sizes
        for orig, unbatched_graph in zip(graphs, unbatched):
            assert unbatched_graph.node_features.shape == orig.node_features.shape
            assert unbatched_graph.edge_index.shape == orig.edge_index.shape

    def test_model_mapping_pipeline(self):
        """Test graph to model mapping integration"""
        mapper = GraphToModelMapper()

        # Create test graphs with different properties
        graphs = [
            # Small dense graph
            GraphData(
                node_features=torch.randn(10, 32),
                edge_index=torch.randint(0, 10, (2, 45))
            ),
            # Large sparse graph
            GraphData(
                node_features=torch.randn(100, 32),
                edge_index=torch.randint(0, 100, (2, 150))
            ),
            # Medium graph with high connectivity
            GraphData(
                node_features=torch.randn(50, 32),
                edge_index=torch.randint(0, 50, (2, 500))
            )
        ]

        # Map each graph to architecture
        for graph in graphs:
            mapping_result = mapper.map_graph_to_model(
                graph,
                task_type='node_classification',
                num_classes=10
            )

            assert mapping_result['architecture'] is not None
            assert mapping_result['model'] is not None
            assert 'analysis' in mapping_result

            # Test forward pass
            model = mapping_result['model']
            model.eval()

            with torch.no_grad():
                batch = torch.zeros(graph.node_features.size(0), dtype=torch.long)
                output = model(graph.node_features, graph.edge_index, batch)

                assert output.shape[0] == graph.node_features.size(0)
                assert output.shape[1] == 10  # num_classes

    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        # Step 1: Parse model specification
        model_spec = """
---
name: EndToEndTest
type: graph_neural_network
version: 1.0
task: graph_classification
---

## Architecture

```yaml
layers:
  - type: GAT
    units: 64
    heads: 4
    dropout: 0.6
  - type: GAT
    units: 32
    heads: 4
    dropout: 0.6
pooling: global_mean
output_dim: 3
```
"""

        parser = GNNParser()
        parsed = parser.parse(model_spec)

        # Step 2: Create model
        model = GNNStack(
            input_dim=32,
            hidden_dims=[64, 32],
            output_dim=3,
            layer_type='GAT',
            dropout=0.6,
            num_heads=4,
            global_pooling='mean'
        )

        # Step 3: Create test data
        graphs = create_test_graphs(10, 5, 20, 32)

        # Step 4: Process batch
        batch_processor = GraphBatchProcessor()
        batch = batch_processor.create_batch(graphs)

        # Step 5: Forward pass
        model.eval()
        with torch.no_grad():
            output = model(batch.x, batch.edge_index, batch.batch)

        assert output.shape == (10, 3)  # num_graphs x num_classes

        # Step 6: Validate
        validator = GNNValidator()

        # Validate model architecture
        validation_results = validator.validate_model_architecture(
            model, graphs[0]
        )
        assert validation_results['valid']

        # Compute metrics (with dummy targets)
        targets = torch.tensor([g.target.item() for g in graphs])
        metrics = validator.compute_metrics(output, targets, 'classification')

        assert 'accuracy' in metrics.to_dict()
        assert 'f1_score' in metrics.to_dict()

    def test_validation_framework_integration(self):
        """Test validation framework integration"""
        # Create test suite
        test_suite = GNNTestSuite()

        # Run unit tests
        unit_results = test_suite.run_unit_tests()

        assert unit_results['total_tests'] > 0
        assert 'component_results' in unit_results
        assert 'parser' in unit_results['component_results']

        # Create model for integration tests
        model = GNNStack(
            input_dim=16,
            hidden_dims=[32, 16],
            output_dim=3,
            layer_type='GCN'
        )

        # Create test graphs
        test_graphs = create_test_graphs(5, 10, 20, 16)

        # Run integration tests
        integration_results = test_suite.run_integration_tests(model, test_graphs)

        assert 'passed' in integration_results
        assert 'performance' in integration_results
        assert 'inference_time' in integration_results['performance']

    def test_benchmark_integration(self):
        """Test benchmarking integration"""
        # Create model
        model = GNNStack(
            input_dim=32,
            hidden_dims=[64, 32],
            output_dim=5,
            layer_type='SAGE',
            aggregation='mean'
        )

        # Create benchmark datasets
        benchmark_datasets = {
            'tiny': create_test_graphs(10, 5, 10, 32),
            'small': create_test_graphs(50, 10, 20, 32),
            'medium': create_test_graphs(100, 20, 40, 32)
        }

        # Run benchmarks
        test_suite = GNNTestSuite()
        results = test_suite.benchmark_model(
            model,
            benchmark_datasets,
            num_runs=3
        )

        assert len(results) == 3

        for result in results:
            assert result.num_graphs > 0
            assert result.avg_nodes_per_graph > 0
            assert result.avg_edges_per_graph > 0
            assert result.processing_time > 0
            assert result.memory_usage > 0

    def test_error_handling_integration(self):
        """Test error handling across pipeline"""
        # Test invalid model architecture
        validator = GNNValidator()

        # Create model with potential issues
        model = torch.nn.Sequential(
            torch.nn.Linear(32, 64),
            torch.nn.ReLU(),
            torch.nn.Linear(64, 10)
        )

        # This should fail validation (not a proper GNN)
        test_graph = GraphData(
            node_features=torch.randn(10, 32),
            edge_index=torch.randint(0, 10, (2, 20))
        )

        results = validator.validate_model_architecture(model, test_graph)

        # Should have errors or warnings
        assert len(results['errors']) > 0 or len(results['warnings']) > 0

    def test_memory_efficiency(self):
        """Test memory efficiency of batch processing"""
        # Create large graphs
        large_graphs = []
        for i in range(10):
            num_nodes = np.random.randint(100, 200)
            num_edges = np.random.randint(num_nodes * 2, num_nodes * 4)

            graph = GraphData(
                node_features=torch.randn(num_nodes, 64),
                edge_index=torch.randint(0, num_nodes, (2, num_edges))
            )
            large_graphs.append(graph)

        # Test streaming batch processor
        from inference.gnn.batch_processor import StreamingBatchProcessor

        base_processor = GraphBatchProcessor()
        streaming_processor = StreamingBatchProcessor(
            base_processor,
            buffer_size=5
        )

        # Process in streaming fashion
        def graph_generator():
            for g in large_graphs:
                yield g

        batches_processed = 0
        for batch in streaming_processor.process_stream(
            graph_generator(),
            batch_size=3
        ):
            assert batch.num_graphs <= 3
            batches_processed += 1

        assert batches_processed == 4  # 10 graphs in batches of 3


class TestGNNComponentInteraction:
    """Test interactions between GNN components"""

    def test_parser_validator_interaction(self):
        """Test parser and validator working together"""
        # Parse model
        parser = GNNParser()
        model_content = """
---
name: InteractionTest
type: graph_neural_network
---

## Architecture

```yaml
layers:
  - type: GIN
    units: 64
    epsilon: 0.1
```
"""
        parsed = parser.parse(model_content)

        # Validate parsed structure
        validator = GNNValidator()

        # Check parsed model has required fields
        assert 'metadata' in parsed
        assert 'architecture' in parsed

    def test_feature_extractor_batch_processor_interaction(self):
        """Test feature extractor with batch processor"""
        # Extract features
        extractor = NodeFeatureExtractor()

        graphs = []
        for i in range(5):
            nodes = [
                {'id': j, 'features': np.random.randn(10)}
                for j in range(np.random.randint(5, 15))
            ]

            result = extractor.extract_features(nodes)

            # Create graph
            num_nodes = len(nodes)
            num_edges = np.random.randint(num_nodes, num_nodes * 3)

            graph = GraphData(
                node_features=result.features,
                edge_index=torch.randint(0, num_nodes, (2, num_edges))
            )
            graphs.append(graph)

        # Batch process
        processor = GraphBatchProcessor()
        batch = processor.create_batch(graphs)

        assert batch.num_graphs == 5
        assert not torch.isnan(batch.x).any()

    def test_model_mapper_validator_interaction(self):
        """Test model mapper with validator"""
        # Create graph
        graph = GraphData(
            node_features=torch.randn(20, 32),
            edge_index=torch.randint(0, 20, (2, 40))
        )

        # Map to model
        mapper = GraphToModelMapper()
        result = mapper.map_graph_to_model(
            graph,
            task_type='node_classification',
            num_classes=5
        )

        # Validate mapped model
        validator = GNNValidator()
        validation = validator.validate_model_architecture(
            result['model'],
            graph
        )

        assert validation['valid']
        assert result['architecture'] in ['GCN', 'GAT', 'SAGE', 'GIN']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
