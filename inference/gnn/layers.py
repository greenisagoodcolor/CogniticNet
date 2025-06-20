"""
GNN Layer Implementations

This module implements various Graph Neural Network layer types including
GCN (Graph Convolutional Network), GAT (Graph Attention Network),
GraphSAGE, and other common architectures.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.nn import MessagePassing
from torch_geometric.utils import add_self_loops, degree, softmax
from torch_geometric.nn.inits import glorot, zeros
from typing import Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum


class AggregationType(Enum):
    """Types of aggregation functions for message passing"""

    MEAN = "mean"
    MAX = "max"
    ADD = "add"
    MIN = "min"
    MUL = "mul"


@dataclass
class LayerConfig:
    """Configuration for GNN layers"""

    in_channels: int
    out_channels: int
    heads: int = 1
    dropout: float = 0.0
    bias: bool = True
    normalize: bool = True
    activation: Optional[str] = "relu"
    aggregation: AggregationType = AggregationType.MEAN
    residual: bool = False


class GCNLayer(MessagePassing):
    """
    Graph Convolutional Network layer.

    Implements the GCN layer from Kipf & Welling (2017):
    "Semi-Supervised Classification with Graph Convolutional Networks"

    Args:
        in_channels: Number of input features
        out_channels: Number of output features
        improved: Use improved GCN formulation
        cached: Cache normalized edge weights
        add_self_loops: Add self-loops to adjacency matrix
        normalize: Apply symmetric normalization
        bias: Add learnable bias
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        improved: bool = False,
        cached: bool = False,
        add_self_loops: bool = True,
        normalize: bool = True,
        bias: bool = True,
        **kwargs,
    ):
        kwargs.setdefault("aggr", "add")
        super().__init__(**kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.improved = improved
        self.cached = cached
        self.add_self_loops = add_self_loops
        self.normalize = normalize

        self._cached_edge_index = None
        self._cached_adj_t = None

        self.lin = nn.Linear(in_channels, out_channels, bias=False)

        if bias:
            self.bias = nn.Parameter(torch.Tensor(out_channels))
        else:
            self.register_parameter("bias", None)

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize layer parameters"""
        self.lin.reset_parameters()
        zeros(self.bias)
        self._cached_edge_index = None
        self._cached_adj_t = None

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_weight: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """
        Forward pass of GCN layer.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_weight: Edge weights [num_edges]

        Returns:
            Updated node features [num_nodes, out_channels]
        """

        if self.normalize:
            if isinstance(edge_index, torch.Tensor):
                cache = self._cached_edge_index
                if cache is None:
                    edge_index, edge_weight = self.norm(
                        edge_index,
                        x.size(0),
                        edge_weight,
                        self.improved,
                        self.add_self_loops,
                    )
                    if self.cached:
                        self._cached_edge_index = (edge_index, edge_weight)
                else:
                    edge_index, edge_weight = cache[0], cache[1]

        x = self.lin(x)

        # Message passing
        out = self.propagate(edge_index, x=x, edge_weight=edge_weight, size=None)

        if self.bias is not None:
            out = out + self.bias

        return out

    def message(
        self, x_j: torch.Tensor, edge_weight: Optional[torch.Tensor]
    ) -> torch.Tensor:
        """Construct messages from source nodes"""
        return x_j if edge_weight is None else edge_weight.view(-1, 1) * x_j

    @staticmethod
    def norm(
        edge_index: torch.Tensor,
        num_nodes: int,
        edge_weight: Optional[torch.Tensor] = None,
        improved: bool = False,
        add_self_loops: bool = True,
        dtype: Optional[torch.dtype] = None,
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """Compute normalized edge weights"""

        if edge_weight is None:
            edge_weight = torch.ones(
                (edge_index.size(1),), dtype=dtype, device=edge_index.device
            )

        if add_self_loops:
            edge_index, edge_weight = add_self_loops(
                edge_index,
                edge_weight,
                fill_value=2.0 if improved else 1.0,
                num_nodes=num_nodes,
            )

        row, col = edge_index[0], edge_index[1]
        deg = degree(col, num_nodes, dtype=edge_weight.dtype)
        deg_inv_sqrt = deg.pow(-0.5)
        deg_inv_sqrt[deg_inv_sqrt == float("inf")] = 0

        edge_weight = deg_inv_sqrt[row] * edge_weight * deg_inv_sqrt[col]

        return edge_index, edge_weight


class GATLayer(MessagePassing):
    """
    Graph Attention Network layer.

    Implements the GAT layer from Veličković et al. (2018):
    "Graph Attention Networks"

    Args:
        in_channels: Number of input features
        out_channels: Number of output features per head
        heads: Number of attention heads
        concat: Concatenate or average attention heads
        negative_slope: LeakyReLU negative slope
        dropout: Dropout probability
        add_self_loops: Add self-loops
        bias: Add learnable bias
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        heads: int = 1,
        concat: bool = True,
        negative_slope: float = 0.2,
        dropout: float = 0.0,
        add_self_loops: bool = True,
        bias: bool = True,
        **kwargs,
    ):
        kwargs.setdefault("aggr", "add")
        super().__init__(node_dim=0, **kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.heads = heads
        self.concat = concat
        self.negative_slope = negative_slope
        self.dropout = dropout
        self.add_self_loops = add_self_loops

        self.lin_src = nn.Linear(in_channels, heads * out_channels, bias=False)
        self.lin_dst = nn.Linear(in_channels, heads * out_channels, bias=False)

        self.att_src = nn.Parameter(torch.Tensor(1, heads, out_channels))
        self.att_dst = nn.Parameter(torch.Tensor(1, heads, out_channels))

        if bias and concat:
            self.bias = nn.Parameter(torch.Tensor(heads * out_channels))
        elif bias and not concat:
            self.bias = nn.Parameter(torch.Tensor(out_channels))
        else:
            self.register_parameter("bias", None)

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize layer parameters"""
        self.lin_src.reset_parameters()
        self.lin_dst.reset_parameters()
        glorot(self.att_src)
        glorot(self.att_dst)
        zeros(self.bias)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        edge_attr: Optional[torch.Tensor] = None,
        return_attention_weights: bool = False,
    ) -> Union[torch.Tensor, Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]]:
        """
        Forward pass of GAT layer.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            edge_attr: Edge features (optional)
            return_attention_weights: Return attention weights

        Returns:
            Updated node features (and optionally attention weights)
        """

        H, C = self.heads, self.out_channels
        x_src = x_dst = x

        if self.add_self_loops:
            edge_index, edge_attr = add_self_loops(
                edge_index, edge_attr, num_nodes=x.size(0)
            )

        x_src = self.lin_src(x_src).view(-1, H, C)
        x_dst = self.lin_dst(x_dst).view(-1, H, C)

        # Compute attention coefficients
        alpha_src = (x_src * self.att_src).sum(dim=-1)
        alpha_dst = (x_dst * self.att_dst).sum(dim=-1)

        # Message passing
        out = self.propagate(
            edge_index, x=(x_src, x_dst), alpha=(alpha_src, alpha_dst), size=None
        )

        if self.concat:
            out = out.view(-1, self.heads * self.out_channels)
        else:
            out = out.mean(dim=1)

        if self.bias is not None:
            out = out + self.bias

        if return_attention_weights:
            alpha = self._alpha
            return out, (edge_index, alpha)
        else:
            return out

    def message(
        self,
        x_j: torch.Tensor,
        alpha_j: torch.Tensor,
        alpha_i: torch.Tensor,
        index: torch.Tensor,
        ptr: Optional[torch.Tensor],
        size_i: Optional[int],
    ) -> torch.Tensor:
        """Construct messages with attention"""
        alpha = alpha_j + alpha_i
        alpha = F.leaky_relu(alpha, self.negative_slope)
        alpha = softmax(alpha, index, ptr, size_i)
        self._alpha = alpha
        alpha = F.dropout(alpha, p=self.dropout, training=self.training)
        return x_j * alpha.unsqueeze(-1)


class SAGELayer(MessagePassing):
    """
    GraphSAGE layer.

    Implements the GraphSAGE layer from Hamilton et al. (2017):
    "Inductive Representation Learning on Large Graphs"

    Args:
        in_channels: Number of input features
        out_channels: Number of output features
        normalize: Apply L2 normalization
        root_weight: Apply linear transformation to central node
        bias: Add learnable bias
        aggr: Aggregation type ('mean', 'max', 'lstm')
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        normalize: bool = False,
        root_weight: bool = True,
        bias: bool = True,
        aggr: str = "mean",
        **kwargs,
    ):
        super().__init__(aggr=aggr, **kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.normalize = normalize
        self.root_weight = root_weight

        self.lin_l = nn.Linear(in_channels, out_channels, bias=bias)

        if self.root_weight:
            self.lin_r = nn.Linear(in_channels, out_channels, bias=False)

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize layer parameters"""
        self.lin_l.reset_parameters()
        if self.root_weight:
            self.lin_r.reset_parameters()

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        size: Optional[Tuple[int, int]] = None,
    ) -> torch.Tensor:
        """
        Forward pass of GraphSAGE layer.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            size: Number of nodes in source and target sets

        Returns:
            Updated node features [num_nodes, out_channels]
        """

        if isinstance(x, torch.Tensor):
            x = (x, x)

        # Neighbor aggregation
        out = self.propagate(edge_index, x=x, size=size)
        out = self.lin_l(out)

        # Self connection
        x_r = x[1]
        if self.root_weight and x_r is not None:
            out = out + self.lin_r(x_r)

        if self.normalize:
            out = F.normalize(out, p=2, dim=-1)

        return out

    def message(self, x_j: torch.Tensor) -> torch.Tensor:
        """Construct messages from source nodes"""
        return x_j


class GINLayer(MessagePassing):
    """
    Graph Isomorphism Network layer.

    Implements the GIN layer from Xu et al. (2019):
    "How Powerful are Graph Neural Networks?"

    Args:
        in_channels: Number of input features
        out_channels: Number of output features
        nn: Neural network for feature transformation
        eps: Initial value for self-loop weight
        train_eps: Make eps trainable
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        nn: Optional[nn.Module] = None,
        eps: float = 0.0,
        train_eps: bool = False,
        **kwargs,
    ):
        kwargs.setdefault("aggr", "add")
        super().__init__(**kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.initial_eps = eps

        if nn is None:
            nn = nn.Sequential(
                nn.Linear(in_channels, out_channels),
                nn.ReLU(),
                nn.Linear(out_channels, out_channels),
            )
        self.nn = nn

        if train_eps:
            self.eps = nn.Parameter(torch.Tensor([eps]))
        else:
            self.register_buffer("eps", torch.Tensor([eps]))

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize layer parameters"""
        if hasattr(self.nn, "reset_parameters"):
            self.nn.reset_parameters()
        self.eps.data.fill_(self.initial_eps)

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        size: Optional[Tuple[int, int]] = None,
    ) -> torch.Tensor:
        """
        Forward pass of GIN layer.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            size: Number of nodes in source and target sets

        Returns:
            Updated node features [num_nodes, out_channels]
        """

        if isinstance(x, torch.Tensor):
            x = (x, x)

        # Message passing
        out = self.propagate(edge_index, x=x, size=size)

        # Apply neural network
        x_r = x[1]
        if x_r is not None:
            out = out + (1 + self.eps) * x_r

        return self.nn(out)

    def message(self, x_j: torch.Tensor) -> torch.Tensor:
        """Construct messages from source nodes"""
        return x_j


class EdgeConvLayer(MessagePassing):
    """
    Edge Convolution layer.

    Implements the EdgeConv layer from Wang et al. (2019):
    "Dynamic Graph CNN for Learning on Point Clouds"

    Args:
        in_channels: Number of input features
        out_channels: Number of output features
        nn: Neural network for edge feature computation
        aggr: Aggregation type
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        nn: Optional[nn.Module] = None,
        aggr: str = "max",
        **kwargs,
    ):
        super().__init__(aggr=aggr, **kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels

        if nn is None:
            nn = nn.Sequential(
                nn.Linear(2 * in_channels, out_channels),
                nn.ReLU(),
                nn.Linear(out_channels, out_channels),
            )
        self.nn = nn

        self.reset_parameters()

    def reset_parameters(self):
        """Initialize layer parameters"""
        if hasattr(self.nn, "reset_parameters"):
            self.nn.reset_parameters()

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        size: Optional[Tuple[int, int]] = None,
    ) -> torch.Tensor:
        """
        Forward pass of EdgeConv layer.

        Args:
            x: Node features [num_nodes, in_channels]
            edge_index: Graph connectivity [2, num_edges]
            size: Number of nodes in source and target sets

        Returns:
            Updated node features [num_nodes, out_channels]
        """

        if isinstance(x, torch.Tensor):
            x = (x, x)

        # Message passing
        return self.propagate(edge_index, x=x, size=size)

    def message(self, x_i: torch.Tensor, x_j: torch.Tensor) -> torch.Tensor:
        """Construct messages using edge features"""
        return self.nn(torch.cat([x_i, x_j - x_i], dim=-1))


class ResGNNLayer(nn.Module):
    """
    Residual GNN layer wrapper.

    Adds residual connections to any GNN layer for improved gradient flow.

    Args:
        layer: Base GNN layer
        in_channels: Number of input features
        out_channels: Number of output features
        dropout: Dropout probability
    """

    def __init__(
        self,
        layer: nn.Module,
        in_channels: int,
        out_channels: int,
        dropout: float = 0.0,
    ):
        super().__init__()

        self.layer = layer
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.dropout = nn.Dropout(dropout)

        # Residual connection
        if in_channels != out_channels:
            self.residual = nn.Linear(in_channels, out_channels, bias=False)
        else:
            self.residual = nn.Identity()

    def forward(self, x: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        """
        Forward pass with residual connection.

        Args:
            x: Node features
            *args, **kwargs: Additional arguments for base layer

        Returns:
            Updated node features with residual
        """
        identity = self.residual(x)
        out = self.layer(x, *args, **kwargs)
        out = self.dropout(out)
        return out + identity


class GNNStack(nn.Module):
    """
    Stack of GNN layers with flexible configuration.

    Args:
        layer_configs: List of layer configurations
        layer_type: Type of GNN layer ('gcn', 'gat', 'sage', 'gin', 'edgeconv')
        global_pool: Global pooling type ('mean', 'max', 'add')
    """

    def __init__(
        self,
        layer_configs: list,
        layer_type: str = "gcn",
        global_pool: Optional[str] = None,
    ):
        super().__init__()

        self.layers = nn.ModuleList()
        self.layer_type = layer_type
        self.global_pool = global_pool

        for config in layer_configs:
            layer = self._create_layer(layer_type, config)

            # Add residual connection if specified
            if hasattr(config, "residual") and config.residual:
                layer = ResGNNLayer(
                    layer,
                    config.in_channels,
                    config.out_channels,
                    getattr(config, "dropout", 0.0),
                )

            self.layers.append(layer)

    def _create_layer(self, layer_type: str, config: LayerConfig) -> nn.Module:
        """Create a GNN layer based on type and configuration"""
        if layer_type == "gcn":
            return GCNLayer(
                config.in_channels,
                config.out_channels,
                bias=config.bias,
                normalize=config.normalize,
            )
        elif layer_type == "gat":
            return GATLayer(
                config.in_channels,
                config.out_channels,
                heads=config.heads,
                dropout=config.dropout,
                bias=config.bias,
            )
        elif layer_type == "sage":
            return SAGELayer(
                config.in_channels,
                config.out_channels,
                normalize=config.normalize,
                bias=config.bias,
                aggr=config.aggregation.value,
            )
        elif layer_type == "gin":
            return GINLayer(config.in_channels, config.out_channels)
        elif layer_type == "edgeconv":
            return EdgeConvLayer(
                config.in_channels, config.out_channels, aggr=config.aggregation.value
            )
        else:
            raise ValueError(f"Unknown layer type: {layer_type}")

    def forward(
        self,
        x: torch.Tensor,
        edge_index: torch.Tensor,
        batch: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        """
        Forward pass through GNN stack.

        Args:
            x: Node features
            edge_index: Graph connectivity
            batch: Batch assignment vector for graph-level tasks
            **kwargs: Additional layer-specific arguments

        Returns:
            Node or graph-level features
        """
        for i, layer in enumerate(self.layers):
            x = layer(x, edge_index, **kwargs)

            # Apply activation if not last layer
            if i < len(self.layers) - 1:
                x = F.relu(x)
                x = F.dropout(x, p=0.5, training=self.training)

        # Global pooling for graph-level tasks
        if self.global_pool is not None and batch is not None:
            if self.global_pool == "mean":
                x = global_mean_pool(x, batch)
            elif self.global_pool == "max":
                x = global_max_pool(x, batch)
            elif self.global_pool == "add":
                x = global_add_pool(x, batch)

        return x


def global_add_pool(x: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
    """Global add pooling"""
    size = int(batch.max().item() + 1)
    return scatter_add(x, batch, dim=0, dim_size=size)


def global_mean_pool(x: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
    """Global mean pooling"""
    size = int(batch.max().item() + 1)
    return scatter_mean(x, batch, dim=0, dim_size=size)


def global_max_pool(x: torch.Tensor, batch: torch.Tensor) -> torch.Tensor:
    """Global max pooling"""
    size = int(batch.max().item() + 1)
    return scatter_max(x, batch, dim=0, dim_size=size)[0]


def scatter_add(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    dim_size: Optional[int] = None,
) -> torch.Tensor:
    """Scatter add operation"""
    size = list(src.size())
    if dim_size is not None:
        size[dim] = dim_size
    elif index.numel() == 0:
        size[dim] = 0
    else:
        size[dim] = int(index.max()) + 1
    out = torch.zeros(size, dtype=src.dtype, device=src.device)
    return out.scatter_add_(dim, index.expand_as(src), src)


def scatter_mean(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    dim_size: Optional[int] = None,
) -> torch.Tensor:
    """Scatter mean operation"""
    out = scatter_add(src, index, dim, dim_size)
    count = scatter_add(torch.ones_like(src), index, dim, dim_size)
    return out / count.clamp(min=1)


def scatter_max(
    src: torch.Tensor,
    index: torch.Tensor,
    dim: int = -1,
    dim_size: Optional[int] = None,
) -> Tuple[torch.Tensor, torch.Tensor]:
    """Scatter max operation"""
    size = list(src.size())
    if dim_size is not None:
        size[dim] = dim_size
    elif index.numel() == 0:
        size[dim] = 0
    else:
        size[dim] = int(index.max()) + 1
    out = torch.zeros(size, dtype=src.dtype, device=src.device)
    arg_out = torch.zeros(size, dtype=torch.long, device=src.device)
    return out.scatter_reduce_(dim, index.expand_as(src), src, "amax"), arg_out


# Example usage
if __name__ == "__main__":
    # Example configuration
    configs = [
        LayerConfig(in_channels=32, out_channels=64),
        LayerConfig(in_channels=64, out_channels=128),
        LayerConfig(in_channels=128, out_channels=64),
    ]

    # Create GNN stack
    model = GNNStack(configs, layer_type="gcn")

    # Example data
    x = torch.randn(100, 32)  # 100 nodes, 32 features
    edge_index = torch.randint(0, 100, (2, 300))  # 300 edges

    # Forward pass
    out = model(x, edge_index)
    print(f"Output shape: {out.shape}")
