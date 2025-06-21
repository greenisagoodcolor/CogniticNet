"""
Graph-to-Model Mapping Logic

This module implements the mapping system that connects input graph structures
to appropriate GNN model architectures based on graph properties and heuristics.
"""
import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import networkx as nx
from collections import defaultdict
import logging
from .layers import GCNLayer, GATLayer, SAGELayer, GINLayer, EdgeConvLayer, GNNStack, LayerConfig, AggregationType
from .feature_extractor import NodeFeatureExtractor, FeatureConfig, FeatureType
from .edge_processor import EdgeProcessor, EdgeConfig, EdgeType, EdgeFeatureType
logger = logging.getLogger(__name__)

class GraphTaskType(Enum):
    """Types of graph learning tasks"""
    NODE_CLASSIFICATION = 'node_classification'
    NODE_REGRESSION = 'node_regression'
    EDGE_PREDICTION = 'edge_prediction'
    EDGE_CLASSIFICATION = 'edge_classification'
    GRAPH_CLASSIFICATION = 'graph_classification'
    GRAPH_REGRESSION = 'graph_regression'
    NODE_CLUSTERING = 'node_clustering'
    GRAPH_GENERATION = 'graph_generation'

class ModelArchitecture(Enum):
    """Available GNN architectures"""
    GCN = 'gcn'
    GAT = 'gat'
    SAGE = 'sage'
    GIN = 'gin'
    EDGECONV = 'edgeconv'
    HYBRID = 'hybrid'

@dataclass
class GraphProperties:
    """Properties of a graph for architecture selection"""
    num_nodes: int
    num_edges: int
    density: float
    avg_degree: float
    max_degree: int
    is_directed: bool
    is_weighted: bool
    has_self_loops: bool
    has_node_features: bool
    has_edge_features: bool
    node_feature_dim: int
    edge_feature_dim: int
    num_connected_components: int
    avg_clustering_coefficient: float
    is_bipartite: bool
    has_cycles: bool
    diameter: Optional[int] = None
    spectral_gap: Optional[float] = None

@dataclass
class ModelConfig:
    """Configuration for GNN model"""
    architecture: ModelArchitecture
    num_layers: int
    hidden_channels: List[int]
    output_channels: int
    heads: Optional[int] = None
    dropout: float = 0.0
    activation: str = 'relu'
    aggregation: AggregationType = AggregationType.MEAN
    residual: bool = False
    batch_norm: bool = False
    layer_norm: bool = False
    global_pool: Optional[str] = None
    edge_dim: Optional[int] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MappingConfig:
    """Configuration for graph-to-model mapping"""
    task_type: GraphTaskType
    auto_select: bool = True
    prefer_attention: bool = False
    max_layers: int = 10
    min_layers: int = 2
    hidden_multiplier: float = 2.0
    complexity_threshold: float = 0.7
    performance_priority: str = 'balanced'
    manual_overrides: Dict[str, Any] = field(default_factory=dict)

class GraphAnalyzer:
    """Analyzes graph properties for architecture selection"""

    def __init__(self):
        self.property_cache = {}

    def analyze_graph(self, edge_index: torch.Tensor, num_nodes: int, node_features: Optional[torch.Tensor]=None, edge_features: Optional[torch.Tensor]=None, edge_weight: Optional[torch.Tensor]=None) -> GraphProperties:
        """
        Analyze graph structure and extract properties.

        Args:
            edge_index: Graph connectivity
            num_nodes: Number of nodes
            node_features: Optional node features
            edge_features: Optional edge features
            edge_weight: Optional edge weights

        Returns:
            GraphProperties object with analyzed properties
        """
        G = self._to_networkx(edge_index, num_nodes, edge_weight)
        num_edges = edge_index.shape[1]
        density = num_edges / (num_nodes * (num_nodes - 1))
        degrees = [G.degree(n) for n in G.nodes()]
        avg_degree = np.mean(degrees) if degrees else 0
        max_degree = max(degrees) if degrees else 0
        is_directed = isinstance(G, nx.DiGraph)
        is_weighted = edge_weight is not None
        has_self_loops = any((u == v for u, v in G.edges()))
        has_node_features = node_features is not None
        has_edge_features = edge_features is not None
        node_feature_dim = node_features.shape[1] if has_node_features else 0
        edge_feature_dim = edge_features.shape[1] if has_edge_features else 0
        if is_directed:
            num_components = nx.number_weakly_connected_components(G)
        else:
            num_components = nx.number_connected_components(G)
        try:
            avg_clustering = nx.average_clustering(G)
        except:
            avg_clustering = 0.0
        is_bipartite = nx.is_bipartite(G)
        has_cycles = not nx.is_forest(G)
        diameter = None
        if num_nodes < 1000 and nx.is_connected(G):
            try:
                diameter = nx.diameter(G)
            except:
                pass
        spectral_gap = None
        if num_nodes < 500:
            try:
                eigenvalues = nx.laplacian_spectrum(G)
                if len(eigenvalues) > 1:
                    eigenvalues = sorted(eigenvalues)
                    spectral_gap = eigenvalues[1]
            except:
                pass
        return GraphProperties(num_nodes=num_nodes, num_edges=num_edges, density=density, avg_degree=avg_degree, max_degree=max_degree, is_directed=is_directed, is_weighted=is_weighted, has_self_loops=has_self_loops, has_node_features=has_node_features, has_edge_features=has_edge_features, node_feature_dim=node_feature_dim, edge_feature_dim=edge_feature_dim, num_connected_components=num_components, avg_clustering_coefficient=avg_clustering, is_bipartite=is_bipartite, has_cycles=has_cycles, diameter=diameter, spectral_gap=spectral_gap)

    def _to_networkx(self, edge_index: torch.Tensor, num_nodes: int, edge_weight: Optional[torch.Tensor]=None) -> Union[nx.Graph, nx.DiGraph]:
        """Convert edge index to NetworkX graph"""
        edge_set = set()
        for i in range(edge_index.shape[1]):
            edge_set.add((edge_index[0, i].item(), edge_index[1, i].item()))
        is_directed = False
        for u, v in edge_set:
            if u != v and (v, u) not in edge_set:
                is_directed = True
                break
        G = nx.DiGraph() if is_directed else nx.Graph()
        G.add_nodes_from(range(num_nodes))
        if edge_weight is not None:
            for i in range(edge_index.shape[1]):
                u, v = (edge_index[0, i].item(), edge_index[1, i].item())
                w = edge_weight[i].item()
                G.add_edge(u, v, weight=w)
        else:
            edges = [(edge_index[0, i].item(), edge_index[1, i].item()) for i in range(edge_index.shape[1])]
            G.add_edges_from(edges)
        return G

class ModelSelector:
    """Selects appropriate GNN architecture based on graph properties"""

    def __init__(self, config: MappingConfig):
        self.config = config
        self.selection_rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize architecture selection rules"""
        return {'gcn': {'conditions': [lambda p: p.density > 0.1, lambda p: not p.has_edge_features, lambda p: p.avg_clustering_coefficient < 0.3], 'score_factors': {'density': lambda p: p.density, 'homophily': lambda p: 1.0 - p.avg_clustering_coefficient, 'size': lambda p: 1.0 / (1 + np.log(p.num_nodes))}}, 'gat': {'conditions': [lambda p: p.has_node_features, lambda p: p.avg_degree > 5, lambda p: self.config.prefer_attention], 'score_factors': {'degree_variance': lambda p: p.max_degree / (p.avg_degree + 1), 'features': lambda p: min(1.0, p.node_feature_dim / 100), 'attention_pref': lambda p: 1.5 if self.config.prefer_attention else 1.0}}, 'sage': {'conditions': [lambda p: p.num_nodes > 1000, lambda p: p.density < 0.1, lambda p: p.avg_degree < 50], 'score_factors': {'scalability': lambda p: 1.0 if p.num_nodes > 10000 else 0.5, 'sampling_efficiency': lambda p: 1.0 - p.density, 'inductive': lambda p: 1.2}}, 'gin': {'conditions': [lambda p: self.config.task_type == GraphTaskType.GRAPH_CLASSIFICATION, lambda p: p.has_cycles, lambda p: not p.is_bipartite], 'score_factors': {'expressiveness': lambda p: 1.5, 'graph_level': lambda p: 2.0 if 'graph' in self.config.task_type.value else 0.5, 'structural': lambda p: p.avg_clustering_coefficient}}, 'edgeconv': {'conditions': [lambda p: p.has_edge_features or p.is_weighted, lambda p: p.density < 0.05, lambda p: p.max_degree < 100], 'score_factors': {'edge_importance': lambda p: 1.5 if p.has_edge_features else 0.8, 'dynamic': lambda p: 1.3, 'sparsity': lambda p: 1.0 - p.density}}}

    def select_architecture(self, graph_properties: GraphProperties) -> ModelArchitecture:
        """
        Select the best architecture for given graph properties.

        Args:
            graph_properties: Analyzed graph properties

        Returns:
            Selected model architecture
        """
        if not self.config.auto_select and 'architecture' in self.config.manual_overrides:
            return ModelArchitecture(self.config.manual_overrides['architecture'])
        scores = {}
        for arch_name, rules in self.selection_rules.items():
            score = 0.0
            conditions_met = sum((1 for cond in rules['conditions'] if cond(graph_properties)))
            condition_ratio = conditions_met / len(rules['conditions'])
            for factor_name, factor_func in rules['score_factors'].items():
                factor_score = factor_func(graph_properties)
                score += factor_score
            scores[arch_name] = condition_ratio * score
        if self.config.performance_priority == 'speed':
            scores['gcn'] *= 1.5
            scores['gat'] *= 0.8
        elif self.config.performance_priority == 'accuracy':
            scores['gin'] *= 1.3
            scores['gat'] *= 1.2
        best_arch = max(scores, key=scores.get)
        logger.info(f'Architecture scores: {scores}')
        logger.info(f'Selected architecture: {best_arch}')
        return ModelArchitecture(best_arch)

    def determine_layer_config(self, architecture: ModelArchitecture, graph_properties: GraphProperties, input_dim: int, output_dim: int) -> ModelConfig:
        """
        Determine layer configuration for selected architecture.

        Args:
            architecture: Selected architecture
            graph_properties: Graph properties
            input_dim: Input feature dimension
            output_dim: Output dimension

        Returns:
            Complete model configuration
        """
        num_layers = self._determine_num_layers(graph_properties)
        hidden_channels = self._determine_hidden_dims(input_dim, output_dim, num_layers, graph_properties)
        config = ModelConfig(architecture=architecture, num_layers=num_layers, hidden_channels=hidden_channels, output_channels=output_dim)
        if architecture == ModelArchitecture.GAT:
            config.heads = min(8, max(1, graph_properties.avg_degree // 5))
            config.dropout = 0.6 if graph_properties.density > 0.1 else 0.3
        elif architecture == ModelArchitecture.SAGE:
            config.aggregation = AggregationType.MEAN
            if graph_properties.max_degree > 100:
                config.aggregation = AggregationType.MAX
        elif architecture == ModelArchitecture.GIN:
            config.aggregation = AggregationType.ADD
            config.additional_params['train_eps'] = True
        elif architecture == ModelArchitecture.EDGECONV:
            config.aggregation = AggregationType.MAX
            config.edge_dim = graph_properties.edge_feature_dim
        config.dropout = self._determine_dropout(graph_properties, num_layers)
        config.residual = num_layers > 4
        config.batch_norm = graph_properties.num_nodes > 10000
        if 'graph' in self.config.task_type.value:
            config.global_pool = 'mean'
            if architecture == ModelArchitecture.GIN:
                config.global_pool = 'add'
        return config

    def _determine_num_layers(self, graph_properties: GraphProperties) -> int:
        """Determine optimal number of layers"""
        if graph_properties.diameter is not None:
            num_layers = min(graph_properties.diameter, self.config.max_layers)
        else:
            num_layers = int(np.log2(graph_properties.num_nodes))
        num_layers = max(self.config.min_layers, min(num_layers, self.config.max_layers))
        if graph_properties.density > 0.5:
            num_layers = min(num_layers, 3)
        return num_layers

    def _determine_hidden_dims(self, input_dim: int, output_dim: int, num_layers: int, graph_properties: GraphProperties) -> List[int]:
        """Determine hidden layer dimensions"""
        hidden_dims = []
        current_dim = int(input_dim * self.config.hidden_multiplier)
        max_dim = min(512, graph_properties.num_nodes // 2)
        current_dim = min(current_dim, max_dim)
        for i in range(num_layers - 1):
            hidden_dims.append(current_dim)
            if i >= num_layers // 2:
                reduction_factor = 0.75
                current_dim = max(output_dim, int(current_dim * reduction_factor))
        return hidden_dims

    def _determine_dropout(self, graph_properties: GraphProperties, num_layers: int) -> float:
        """Determine appropriate dropout rate"""
        base_dropout = 0.5
        if graph_properties.density > 0.3:
            base_dropout += 0.1
        if num_layers > 6:
            base_dropout += 0.1
        if graph_properties.num_nodes < 100:
            base_dropout -= 0.2
        return max(0.0, min(0.8, base_dropout))

class GraphToModelMapper:
    """Main class for mapping graphs to GNN models"""

    def __init__(self, mapping_config: MappingConfig):
        self.config = mapping_config
        self.analyzer = GraphAnalyzer()
        self.selector = ModelSelector(mapping_config)
        self.model_cache = {}

    def map_graph_to_model(self, edge_index: torch.Tensor, num_nodes: int, input_dim: int, output_dim: int, node_features: Optional[torch.Tensor]=None, edge_features: Optional[torch.Tensor]=None, edge_weight: Optional[torch.Tensor]=None) -> Tuple[nn.Module, ModelConfig]:
        """
        Map a graph to an appropriate GNN model.

        Args:
            edge_index: Graph connectivity
            num_nodes: Number of nodes
            input_dim: Input feature dimension
            output_dim: Output dimension
            node_features: Optional node features
            edge_features: Optional edge features
            edge_weight: Optional edge weights

        Returns:
            Tuple of (model, config)
        """
        graph_properties = self.analyzer.analyze_graph(edge_index, num_nodes, node_features, edge_features, edge_weight)
        architecture = self.selector.select_architecture(graph_properties)
        model_config = self.selector.determine_layer_config(architecture, graph_properties, input_dim, output_dim)
        model = self._create_model(model_config, input_dim)
        return (model, model_config)

    def _create_model(self, config: ModelConfig, input_dim: int) -> nn.Module:
        """Create GNN model from configuration"""
        layer_configs = []
        current_in = input_dim
        for i, hidden_dim in enumerate(config.hidden_channels):
            layer_config = LayerConfig(in_channels=current_in, out_channels=hidden_dim, heads=config.heads if config.heads else 1, dropout=config.dropout if i < len(config.hidden_channels) - 1 else 0.0, bias=True, normalize=True, activation=config.activation, aggregation=config.aggregation, residual=config.residual and current_in == hidden_dim)
            layer_configs.append(layer_config)
            if config.architecture == ModelArchitecture.GAT and config.heads and (config.heads > 1):
                current_in = hidden_dim * config.heads
            else:
                current_in = hidden_dim
        final_config = LayerConfig(in_channels=current_in, out_channels=config.output_channels, heads=1, dropout=0.0, bias=True, normalize=False, activation=None, aggregation=config.aggregation, residual=False)
        layer_configs.append(final_config)
        model = GNNStack(layer_configs, layer_type=config.architecture.value, global_pool=config.global_pool)
        if config.batch_norm:
            model = self._add_batch_norm(model, config)
        if config.layer_norm:
            model = self._add_layer_norm(model, config)
        return model

    def _add_batch_norm(self, model: nn.Module, config: ModelConfig) -> nn.Module:
        """Add batch normalization to model"""

        class BatchNormGNN(nn.Module):

            def __init__(self, base_model, hidden_dims):
                super().__init__()
                self.model = base_model
                self.batch_norms = nn.ModuleList([nn.BatchNorm1d(dim) for dim in hidden_dims])

            def forward(self, x, edge_index, batch=None, **kwargs):
                for i, (layer, bn) in enumerate(zip(self.model.layers[:-1], self.batch_norms)):
                    x = layer(x, edge_index, **kwargs)
                    x = bn(x)
                    x = F.relu(x)
                    x = F.dropout(x, p=0.5, training=self.training)
                x = self.model.layers[-1](x, edge_index, **kwargs)
                if self.model.global_pool is not None and batch is not None:
                    x = self.model._global_pool(x, batch)
                return x
        return BatchNormGNN(model, config.hidden_channels)

    def _add_layer_norm(self, model: nn.Module, config: ModelConfig) -> nn.Module:
        """Add layer normalization to model"""

        class LayerNormGNN(nn.Module):

            def __init__(self, base_model, hidden_dims):
                super().__init__()
                self.model = base_model
                self.layer_norms = nn.ModuleList([nn.LayerNorm(dim) for dim in hidden_dims])

            def forward(self, x, edge_index, batch=None, **kwargs):
                for i, (layer, ln) in enumerate(zip(self.model.layers[:-1], self.layer_norms)):
                    x = layer(x, edge_index, **kwargs)
                    x = ln(x)
                    x = F.relu(x)
                    x = F.dropout(x, p=0.5, training=self.training)
                x = self.model.layers[-1](x, edge_index, **kwargs)
                if self.model.global_pool is not None and batch is not None:
                    x = self.model._global_pool(x, batch)
                return x
        return LayerNormGNN(model, config.hidden_channels)

    def validate_model_compatibility(self, model: nn.Module, edge_index: torch.Tensor, node_features: torch.Tensor, edge_features: Optional[torch.Tensor]=None) -> bool:
        """
        Validate that a model is compatible with given graph.

        Args:
            model: GNN model
            edge_index: Graph connectivity
            node_features: Node features
            edge_features: Optional edge features

        Returns:
            True if compatible, False otherwise
        """
        try:
            model.eval()
            with torch.no_grad():
                output = model(node_features, edge_index)
            if output.shape[0] != node_features.shape[0]:
                logger.warning('Output shape mismatch')
                return False
            return True
        except Exception as e:
            logger.error(f'Model validation failed: {e}')
            return False
if __name__ == '__main__':
    mapping_config = MappingConfig(task_type=GraphTaskType.NODE_CLASSIFICATION, auto_select=True, prefer_attention=True, max_layers=6)
    mapper = GraphToModelMapper(mapping_config)
    edge_index = torch.tensor([[0, 1, 2, 3, 4], [1, 2, 3, 4, 0]], dtype=torch.long)
    num_nodes = 5
    input_dim = 32
    output_dim = 10
    node_features = torch.randn(num_nodes, input_dim)
    model, config = mapper.map_graph_to_model(edge_index, num_nodes, input_dim, output_dim, node_features=node_features)
    print(f'Selected architecture: {config.architecture}')
    print(f'Model layers: {config.num_layers}')
    print(f'Hidden dimensions: {config.hidden_channels}')
    output = model(node_features, edge_index)
    print(f'Output shape: {output.shape}')
