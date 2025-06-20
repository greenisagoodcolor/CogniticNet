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
from .......inference.gnn.parser import GNNParser
from .......inference.gnn.feature-extractor import NodeFeatureExtractor
from .......inference.gnn.edge-processor import EdgeProcessor
from .......inference.gnn.layers import GNNStack, GCNLayer, GATLayer
from .......inference.gnn.model-mapper import GraphToModelMapper
from .......inference.gnn.batch-processor import GraphBatchProcessor, GraphData
from .......inference.gnn.testing-framework import GNNValidator, GNNTestSuite, create_test_graphs

class TestGNNPipelineIntegration:
    """Test complete GNN processing pipeline"""

    def test_parser_to_model_pipeline(self):
        """Test parsing GNN model and creating architecture"""
        model_content = '\n---\nname: TestIntegrationModel\ntype: graph_neural_network\nversion: 1.0\ntask: node_classification\n---\n\n## Architecture\n\n```yaml\nlayers:\n  - type: GCN\n    units: 64\n    activation: relu\n    dropout: 0.5\n  - type: GCN\n    units: 32\n    activation: relu\n    dropout: 0.5\n  - type: GCN\n    units: 10\n    activation: softmax\n```\n\n## Training\n\n```yaml\noptimizer: adam\nlearning_rate: 0.01\nepochs: 100\nbatch_size: 32\n```\n'
        parser = GNNParser()
        parsed_model = parser.parse(model_content)
        assert parsed_model is not None
        assert 'architecture' in parsed_model
        assert 'training' in parsed_model
        architecture = parsed_model['architecture']
        layers = architecture.get('layers', [])
        assert len(layers) == 3
        assert layers[0]['type'] == 'GCN'
        assert layers[0]['units'] == 64

    def test_feature_extraction_pipeline(self):
        """Test feature extraction integration"""
        extractor = NodeFeatureExtractor(feature_types=['spatial', 'numerical', 'categorical'])
        nodes = []
        for i in range(10):
            node = {'id': i, 'position': {'lat': 40.7 + i * 0.01, 'lon': -74.0 + i * 0.01}, 'features': np.random.randn(5), 'category': f'type_{i % 3}'}
            nodes.append(node)
        result = extractor.extract_features(nodes)
        assert result.features.shape[0] == 10
        assert result.features.shape[1] > 5
        assert not torch.isnan(result.features).any()

    def test_edge_processing_pipeline(self):
        """Test edge processing integration"""
        processor = EdgeProcessor()
        edges = []
        for i in range(20):
            edge = {'source': i % 10, 'target': (i + 1) % 10, 'weight': np.random.rand(), 'type': 'connection' if i % 2 == 0 else 'relation'}
            edges.append(edge)
        edge_batch = processor.process_edges(edges)
        assert edge_batch.edge_index.shape == (2, 20)
        assert edge_batch.edge_weight.shape == (20,)
        assert edge_batch.edge_attr is not None

    def test_batch_processing_pipeline(self):
        """Test batch processing integration"""
        batch_processor = GraphBatchProcessor(pad_node_features=True, max_nodes_per_graph=50)
        graphs = create_test_graphs(num_graphs=5, min_nodes=10, max_nodes=30, feature_dim=16)
        batch = batch_processor.create_batch(graphs)
        assert batch.num_graphs == 5
        assert batch.x.shape[2] == 16
        assert batch.mask is not None
        unbatched = batch_processor.unbatch(batch)
        assert len(unbatched) == 5
        for orig, unbatched_graph in zip(graphs, unbatched):
            assert unbatched_graph.node_features.shape == orig.node_features.shape
            assert unbatched_graph.edge_index.shape == orig.edge_index.shape

    def test_model_mapping_pipeline(self):
        """Test graph to model mapping integration"""
        mapper = GraphToModelMapper()
        graphs = [GraphData(node_features=torch.randn(10, 32), edge_index=torch.randint(0, 10, (2, 45))), GraphData(node_features=torch.randn(100, 32), edge_index=torch.randint(0, 100, (2, 150))), GraphData(node_features=torch.randn(50, 32), edge_index=torch.randint(0, 50, (2, 500)))]
        for graph in graphs:
            mapping_result = mapper.map_graph_to_model(graph, task_type='node_classification', num_classes=10)
            assert mapping_result['architecture'] is not None
            assert mapping_result['model'] is not None
            assert 'analysis' in mapping_result
            model = mapping_result['model']
            model.eval()
            with torch.no_grad():
                batch = torch.zeros(graph.node_features.size(0), dtype=torch.long)
                output = model(graph.node_features, graph.edge_index, batch)
                assert output.shape[0] == graph.node_features.size(0)
                assert output.shape[1] == 10

    def test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        model_spec = '\n---\nname: EndToEndTest\ntype: graph_neural_network\nversion: 1.0\ntask: graph_classification\n---\n\n## Architecture\n\n```yaml\nlayers:\n  - type: GAT\n    units: 64\n    heads: 4\n    dropout: 0.6\n  - type: GAT\n    units: 32\n    heads: 4\n    dropout: 0.6\npooling: global_mean\noutput_dim: 3\n```\n'
        parser = GNNParser()
        parsed = parser.parse(model_spec)
        model = GNNStack(input_dim=32, hidden_dims=[64, 32], output_dim=3, layer_type='GAT', dropout=0.6, num_heads=4, global_pooling='mean')
        graphs = create_test_graphs(10, 5, 20, 32)
        batch_processor = GraphBatchProcessor()
        batch = batch_processor.create_batch(graphs)
        model.eval()
        with torch.no_grad():
            output = model(batch.x, batch.edge_index, batch.batch)
        assert output.shape == (10, 3)
        validator = GNNValidator()
        validation_results = validator.validate_model_architecture(model, graphs[0])
        assert validation_results['valid']
        targets = torch.tensor([g.target.item() for g in graphs])
        metrics = validator.compute_metrics(output, targets, 'classification')
        assert 'accuracy' in metrics.to_dict()
        assert 'f1_score' in metrics.to_dict()

    def test_validation_framework_integration(self):
        """Test validation framework integration"""
        test_suite = GNNTestSuite()
        unit_results = test_suite.run_unit_tests()
        assert unit_results['total_tests'] > 0
        assert 'component_results' in unit_results
        assert 'parser' in unit_results['component_results']
        model = GNNStack(input_dim=16, hidden_dims=[32, 16], output_dim=3, layer_type='GCN')
        test_graphs = create_test_graphs(5, 10, 20, 16)
        integration_results = test_suite.run_integration_tests(model, test_graphs)
        assert 'passed' in integration_results
        assert 'performance' in integration_results
        assert 'inference_time' in integration_results['performance']

    def test_benchmark_integration(self):
        """Test benchmarking integration"""
        model = GNNStack(input_dim=32, hidden_dims=[64, 32], output_dim=5, layer_type='SAGE', aggregation='mean')
        benchmark_datasets = {'tiny': create_test_graphs(10, 5, 10, 32), 'small': create_test_graphs(50, 10, 20, 32), 'medium': create_test_graphs(100, 20, 40, 32)}
        test_suite = GNNTestSuite()
        results = test_suite.benchmark_model(model, benchmark_datasets, num_runs=3)
        assert len(results) == 3
        for result in results:
            assert result.num_graphs > 0
            assert result.avg_nodes_per_graph > 0
            assert result.avg_edges_per_graph > 0
            assert result.processing_time > 0
            assert result.memory_usage > 0

    def test_error_handling_integration(self):
        """Test error handling across pipeline"""
        validator = GNNValidator()
        model = torch.nn.Sequential(torch.nn.Linear(32, 64), torch.nn.ReLU(), torch.nn.Linear(64, 10))
        test_graph = GraphData(node_features=torch.randn(10, 32), edge_index=torch.randint(0, 10, (2, 20)))
        results = validator.validate_model_architecture(model, test_graph)
        assert len(results['errors']) > 0 or len(results['warnings']) > 0

    def test_memory_efficiency(self):
        """Test memory efficiency of batch processing"""
        large_graphs = []
        for i in range(10):
            num_nodes = np.random.randint(100, 200)
            num_edges = np.random.randint(num_nodes * 2, num_nodes * 4)
            graph = GraphData(node_features=torch.randn(num_nodes, 64), edge_index=torch.randint(0, num_nodes, (2, num_edges)))
            large_graphs.append(graph)
        from .......inference.gnn.batch-processor import StreamingBatchProcessor
        base_processor = GraphBatchProcessor()
        streaming_processor = StreamingBatchProcessor(base_processor, buffer_size=5)

        def graph_generator():
            for g in large_graphs:
                yield g
        batches_processed = 0
        for batch in streaming_processor.process_stream(graph_generator(), batch_size=3):
            assert batch.num_graphs <= 3
            batches_processed += 1
        assert batches_processed == 4

class TestGNNComponentInteraction:
    """Test interactions between GNN components"""

    def test_parser_validator_interaction(self):
        """Test parser and validator working together"""
        parser = GNNParser()
        model_content = '\n---\nname: InteractionTest\ntype: graph_neural_network\n---\n\n## Architecture\n\n```yaml\nlayers:\n  - type: GIN\n    units: 64\n    epsilon: 0.1\n```\n'
        parsed = parser.parse(model_content)
        validator = GNNValidator()
        assert 'metadata' in parsed
        assert 'architecture' in parsed

    def test_feature_extractor_batch_processor_interaction(self):
        """Test feature extractor with batch processor"""
        extractor = NodeFeatureExtractor()
        graphs = []
        for i in range(5):
            nodes = [{'id': j, 'features': np.random.randn(10)} for j in range(np.random.randint(5, 15))]
            result = extractor.extract_features(nodes)
            num_nodes = len(nodes)
            num_edges = np.random.randint(num_nodes, num_nodes * 3)
            graph = GraphData(node_features=result.features, edge_index=torch.randint(0, num_nodes, (2, num_edges)))
            graphs.append(graph)
        processor = GraphBatchProcessor()
        batch = processor.create_batch(graphs)
        assert batch.num_graphs == 5
        assert not torch.isnan(batch.x).any()

    def test_model_mapper_validator_interaction(self):
        """Test model mapper with validator"""
        graph = GraphData(node_features=torch.randn(20, 32), edge_index=torch.randint(0, 20, (2, 40)))
        mapper = GraphToModelMapper()
        result = mapper.map_graph_to_model(graph, task_type='node_classification', num_classes=5)
        validator = GNNValidator()
        validation = validator.validate_model_architecture(result['model'], graph)
        assert validation['valid']
        assert result['architecture'] in ['GCN', 'GAT', 'SAGE', 'GIN']
if __name__ == '__main__':
    pytest.main([__file__, '-v'])