"""
Unit tests for GNN Integration Layer
"""
import pytest
import torch
import torch.nn as nn
import numpy as np
from unittest.mock import Mock, MagicMock
from .......inference.engine.gnn-integration import GNNIntegrationConfig, DirectGraphMapper, LearnedGraphMapper, GNNActiveInferenceAdapter, GraphFeatureAggregator, HierarchicalGraphIntegration, create_gnn_adapter
from .......inference.engine.generative-model import DiscreteGenerativeModel, ContinuousGenerativeModel, ModelDimensions, ModelParameters
from inference.engine.inference import VariationalMessagePassing, InferenceConfig

class DummyGNN(nn.Module):
    """Dummy GNN model for testing"""

    def __init__(self, input_dim, hidden_dim, output_dim):
        super().__init__()
        self.output_dim = output_dim
        self.linear = nn.Linear(input_dim, output_dim)

    def forward(self, x, edge_index, edge_features=None):
        return self.linear(x)

class TestGNNIntegrationConfig:

    def test_default_config(self):
        """Test default configuration values"""
        config = GNNIntegrationConfig()
        assert config.gnn_type == 'gcn'
        assert config.num_layers == 3
        assert config.hidden_dim == 64
        assert config.output_dim == 32
        assert config.aggregation_method == 'mean'
        assert config.state_mapping == 'direct'

    def test_custom_config(self):
        """Test custom configuration"""
        config = GNNIntegrationConfig(gnn_type='gat', num_layers=5, aggregation_method='attention', use_gpu=False)
        assert config.gnn_type == 'gat'
        assert config.num_layers == 5
        assert config.aggregation_method == 'attention'
        assert config.use_gpu == False

class TestDirectGraphMapper:

    def test_initialization(self):
        """Test mapper initialization"""
        config = GNNIntegrationConfig(use_gpu=False)
        mapper = DirectGraphMapper(config, state_dim=10, observation_dim=5)
        assert mapper.state_dim == 10
        assert mapper.observation_dim == 5
        assert mapper.state_projection is not None
        assert mapper.obs_projection is not None

    def test_map_to_states(self):
        """Test mapping graph features to states"""
        config = GNNIntegrationConfig(use_gpu=False, output_dim=8)
        mapper = DirectGraphMapper(config, state_dim=4, observation_dim=3)
        graph_features = torch.randn(5, 8)
        states = mapper.map_to_states(graph_features)
        assert states.shape == (5, 4)
        assert torch.allclose(states.sum(dim=-1), torch.ones(5), atol=1e-06)

    def test_map_with_node_indices(self):
        """Test mapping with specific node indices"""
        config = GNNIntegrationConfig(use_gpu=False, output_dim=8)
        mapper = DirectGraphMapper(config, state_dim=4, observation_dim=3)
        graph_features = torch.randn(10, 8)
        node_indices = torch.tensor([0, 2, 5])
        states = mapper.map_to_states(graph_features, node_indices)
        assert states.shape == (3, 4)

class TestLearnedGraphMapper:

    def test_initialization(self):
        """Test learned mapper initialization"""
        config = GNNIntegrationConfig(use_gpu=False)
        mapper = LearnedGraphMapper(config, state_dim=10, observation_dim=5)
        assert mapper.state_dim == 10
        assert mapper.observation_dim == 5
        assert isinstance(mapper.state_mapper, nn.Sequential)
        assert isinstance(mapper.obs_mapper, nn.Sequential)

    def test_map_to_states(self):
        """Test learned mapping to states"""
        config = GNNIntegrationConfig(use_gpu=False, output_dim=8)
        mapper = LearnedGraphMapper(config, state_dim=4, observation_dim=3)
        graph_features = torch.randn(5, 8)
        states = mapper.map_to_states(graph_features)
        assert states.shape == (5, 4)
        assert torch.allclose(states.sum(dim=-1), torch.ones(5), atol=1e-06)

    def test_map_to_observations(self):
        """Test learned mapping to observations"""
        config = GNNIntegrationConfig(use_gpu=False, output_dim=8)
        mapper = LearnedGraphMapper(config, state_dim=4, observation_dim=3)
        graph_features = torch.randn(5, 8)
        obs = mapper.map_to_observations(graph_features)
        assert obs.shape == (5, 3)

class TestGraphFeatureAggregator:

    def test_mean_aggregation(self):
        """Test mean aggregation"""
        config = GNNIntegrationConfig(use_gpu=False, aggregation_method='mean')
        aggregator = GraphFeatureAggregator(config)
        node_features = torch.randn(10, 8)
        batch = torch.tensor([0, 0, 0, 1, 1, 2, 2, 2, 2, 2])
        aggregated = aggregator.aggregate(node_features, batch)
        assert aggregated.shape == (3, 8)
        expected_mean = node_features[:3].mean(dim=0)
        assert torch.allclose(aggregated[0], expected_mean, atol=1e-06)

    def test_max_aggregation(self):
        """Test max aggregation"""
        config = GNNIntegrationConfig(use_gpu=False, aggregation_method='max')
        aggregator = GraphFeatureAggregator(config)
        node_features = torch.randn(10, 8)
        batch = torch.tensor([0, 0, 0, 1, 1, 2, 2, 2, 2, 2])
        aggregated = aggregator.aggregate(node_features, batch)
        assert aggregated.shape == (3, 8)
        expected_max = node_features[:3].max(dim=0)[0]
        assert torch.allclose(aggregated[0], expected_max, atol=1e-06)

    def test_single_graph_aggregation(self):
        """Test aggregation for single graph"""
        config = GNNIntegrationConfig(use_gpu=False, aggregation_method='mean')
        aggregator = GraphFeatureAggregator(config)
        node_features = torch.randn(5, 8)
        aggregated = aggregator.aggregate_single(node_features)
        assert aggregated.shape == (1, 8)
        expected = node_features.mean(dim=0, keepdim=True)
        assert torch.allclose(aggregated, expected, atol=1e-06)

class TestGNNActiveInferenceAdapter:

    @pytest.fixture
    def setup_adapter(self):
        """Setup adapter with mock components"""
        config = GNNIntegrationConfig(use_gpu=False, output_dim=8)
        gnn_model = DummyGNN(10, 32, 8)
        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)
        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)
        adapter = GNNActiveInferenceAdapter(config, gnn_model, gen_model, inference)
        return (adapter, config, gnn_model, gen_model, inference)

    def test_initialization(self, setup_adapter):
        """Test adapter initialization"""
        adapter, config, gnn_model, gen_model, inference = setup_adapter
        assert adapter.config == config
        assert adapter.gnn_model == gnn_model
        assert adapter.generative_model == gen_model
        assert adapter.inference == inference
        assert adapter.state_dim == 4
        assert adapter.obs_dim == 3
        assert isinstance(adapter.mapper, DirectGraphMapper)
        assert isinstance(adapter.aggregator, GraphFeatureAggregator)

    def test_process_graph(self, setup_adapter):
        """Test graph processing"""
        adapter, _, _, _, _ = setup_adapter
        node_features = torch.randn(5, 10)
        edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]])
        result = adapter.process_graph(node_features, edge_index)
        assert 'node_features' in result
        assert 'graph_features' in result
        assert 'edge_index' in result
        assert result['node_features'].shape == (5, 8)
        assert result['graph_features'].shape == (1, 8)

    def test_graph_to_beliefs(self, setup_adapter):
        """Test converting graph features to beliefs"""
        adapter, _, _, _, _ = setup_adapter
        node_features = torch.randn(5, 10)
        edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]])
        graph_data = adapter.process_graph(node_features, edge_index)
        beliefs = adapter.graph_to_beliefs(graph_data)
        assert beliefs.shape == (1, 4)
        assert torch.allclose(beliefs.sum(dim=-1), torch.ones(1), atol=1e-06)
        agent_indices = torch.tensor([0, 2])
        beliefs = adapter.graph_to_beliefs(graph_data, agent_indices)
        assert beliefs.shape == (2, 4)

    def test_update_beliefs_with_graph(self, setup_adapter):
        """Test belief update with graph information"""
        adapter, _, _, _, _ = setup_adapter
        current_beliefs = torch.tensor([[0.25, 0.25, 0.25, 0.25]])
        node_features = torch.randn(5, 10)
        edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]])
        graph_data = adapter.process_graph(node_features, edge_index)
        updated_beliefs = adapter.update_beliefs_with_graph(current_beliefs, graph_data)
        assert updated_beliefs.shape == (1, 4)
        assert torch.allclose(updated_beliefs.sum(dim=-1), torch.ones(1), atol=1e-06)

class TestHierarchicalGraphIntegration:

    def test_initialization(self):
        """Test hierarchical integration initialization"""
        config = GNNIntegrationConfig(use_gpu=False)
        level_configs = [{'input_dim': 10, 'hidden_dim': 32, 'output_dim': 16}, {'input_dim': 16, 'hidden_dim': 64, 'output_dim': 32}, {'input_dim': 32, 'hidden_dim': 128, 'output_dim': 64}]
        hier_integration = HierarchicalGraphIntegration(config, level_configs)
        assert hier_integration.num_levels == 3
        assert len(hier_integration.level_gnns) == 3
        assert len(hier_integration.level_adapters) == 3
        assert all((adapter is None for adapter in hier_integration.level_adapters))

    def test_set_generative_models(self):
        """Test setting generative models"""
        config = GNNIntegrationConfig(use_gpu=False)
        level_configs = [{'input_dim': 10, 'hidden_dim': 32, 'output_dim': 16}, {'input_dim': 16, 'hidden_dim': 64, 'output_dim': 32}]
        hier_integration = HierarchicalGraphIntegration(config, level_configs)
        gen_models = []
        inf_algorithms = []
        for i in range(2):
            dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
            params = ModelParameters(use_gpu=False)
            gen_models.append(DiscreteGenerativeModel(dims, params))
            inf_algorithms.append(VariationalMessagePassing(InferenceConfig(use_gpu=False)))
        hier_integration.set_generative_models(gen_models, inf_algorithms)
        assert all((adapter is not None for adapter in hier_integration.level_adapters))

    def test_process_hierarchical_graph(self):
        """Test processing hierarchical graphs"""
        config = GNNIntegrationConfig(use_gpu=False)
        level_configs = [{'input_dim': 10, 'hidden_dim': 32, 'output_dim': 16}]
        hier_integration = HierarchicalGraphIntegration(config, level_configs)
        graph_data_per_level = [{'node_features': torch.randn(5, 10), 'edge_index': torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]])}]
        processed = hier_integration.process_hierarchical_graph(graph_data_per_level)
        assert len(processed) == 1
        assert processed[0] == graph_data_per_level[0]

class TestFactoryFunction:

    def test_create_standard_adapter(self):
        """Test creating standard adapter"""
        config = GNNIntegrationConfig(use_gpu=False)
        gnn_model = DummyGNN(10, 32, 8)
        dims = ModelDimensions(num_states=4, num_observations=3, num_actions=2)
        params = ModelParameters(use_gpu=False)
        gen_model = DiscreteGenerativeModel(dims, params)
        inf_config = InferenceConfig(use_gpu=False)
        inference = VariationalMessagePassing(inf_config)
        adapter = create_gnn_adapter('standard', config, gnn_model=gnn_model, generative_model=gen_model, inference_algorithm=inference)
        assert isinstance(adapter, GNNActiveInferenceAdapter)

    def test_create_hierarchical_adapter(self):
        """Test creating hierarchical adapter"""
        config = GNNIntegrationConfig(use_gpu=False)
        level_configs = [{'input_dim': 10, 'hidden_dim': 32, 'output_dim': 16}, {'input_dim': 16, 'hidden_dim': 64, 'output_dim': 32}]
        adapter = create_gnn_adapter('hierarchical', config, level_configs=level_configs)
        assert isinstance(adapter, HierarchicalGraphIntegration)
        assert adapter.num_levels == 2

    def test_invalid_adapter_type(self):
        """Test invalid adapter type"""
        with pytest.raises(ValueError, match='Unknown adapter type'):
            create_gnn_adapter('invalid')

    def test_missing_required_params(self):
        """Test missing required parameters"""
        config = GNNIntegrationConfig(use_gpu=False)
        with pytest.raises(ValueError, match='Standard adapter requires'):
            create_gnn_adapter('standard', config)
        with pytest.raises(ValueError, match='Hierarchical adapter requires'):
            create_gnn_adapter('hierarchical', config)