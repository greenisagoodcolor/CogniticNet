"""
Node Feature Extraction Module

This module implements feature extraction and normalization for nodes in graph structures,
preparing them for GNN processing. It handles various feature types including spatial,
temporal, categorical, numerical, and embeddings.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
import torch
import torch.nn.functional as F
from datetime import datetime
import h3

# Configure logging
logger = logging.getLogger(__name__)


class FeatureType(Enum):
    """Types of node features"""
    SPATIAL = "spatial"
    TEMPORAL = "temporal"
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    EMBEDDING = "embedding"
    TEXT = "text"
    GRAPH_STRUCTURAL = "graph_structural"


class NormalizationType(Enum):
    """Types of normalization methods"""
    STANDARD = "standard"  # Zero mean, unit variance
    MINMAX = "minmax"     # Scale to [0, 1]
    ROBUST = "robust"     # Robust to outliers
    LOG = "log"           # Log transformation
    NONE = "none"         # No normalization


@dataclass
class FeatureConfig:
    """Configuration for a feature"""
    name: str
    type: FeatureType
    dimension: Optional[int] = None
    normalization: NormalizationType = NormalizationType.STANDARD
    default_value: Any = None
    constraints: Dict[str, Any] = field(default_factory=dict)
    preprocessing_fn: Optional[Callable] = None


@dataclass
class ExtractionResult:
    """Result of feature extraction"""
    features: np.ndarray
    feature_names: List[str]
    feature_dims: Dict[str, Tuple[int, int]]  # name -> (start_idx, end_idx)
    metadata: Dict[str, Any] = field(default_factory=dict)
    missing_mask: Optional[np.ndarray] = None


class NodeFeatureExtractor:
    """
    Extracts and normalizes node features for GNN processing.

    Handles:
    - Multiple feature types (spatial, temporal, categorical, numerical)
    - Missing data imputation
    - Feature normalization and scaling
    - Embedding generation
    - Graph structural features
    """

    def __init__(self, feature_configs: List[FeatureConfig]):
        """
        Initialize the feature extractor.

        Args:
            feature_configs: List of feature configurations
        """
        self.feature_configs = {config.name: config for config in feature_configs}
        self.scalers = {}
        self.encoders = {}
        self.vectorizers = {}
        self._initialize_processors()

    def _initialize_processors(self):
        """Initialize feature processors based on configurations"""
        for name, config in self.feature_configs.items():
            if config.type == FeatureType.NUMERICAL:
                if config.normalization == NormalizationType.STANDARD:
                    self.scalers[name] = StandardScaler()
                elif config.normalization == NormalizationType.MINMAX:
                    self.scalers[name] = MinMaxScaler()
                elif config.normalization == NormalizationType.ROBUST:
                    self.scalers[name] = RobustScaler()

            elif config.type == FeatureType.CATEGORICAL:
                self.encoders[name] = LabelEncoder()

            elif config.type == FeatureType.TEXT:
                self.vectorizers[name] = TfidfVectorizer(max_features=config.dimension or 100)

    def extract_features(self, nodes: List[Dict[str, Any]],
                        graph: Optional[Any] = None) -> ExtractionResult:
        """
        Extract features from a list of nodes.

        Args:
            nodes: List of node dictionaries with feature values
            graph: Optional graph structure for structural features

        Returns:
            ExtractionResult with extracted and normalized features
        """
        if not nodes:
            return ExtractionResult(
                features=np.array([]),
                feature_names=[],
                feature_dims={}
            )

        feature_arrays = []
        feature_names = []
        feature_dims = {}
        current_idx = 0
        missing_mask = np.zeros((len(nodes), len(self.feature_configs)), dtype=bool)

        # Extract each feature type
        for feature_idx, (name, config) in enumerate(self.feature_configs.items()):
            logger.debug(f"Extracting feature: {name}")

            if config.type == FeatureType.SPATIAL:
                features, names = self._extract_spatial_features(nodes, config)
            elif config.type == FeatureType.TEMPORAL:
                features, names = self._extract_temporal_features(nodes, config)
            elif config.type == FeatureType.CATEGORICAL:
                features, names = self._extract_categorical_features(nodes, config)
            elif config.type == FeatureType.NUMERICAL:
                features, names = self._extract_numerical_features(nodes, config)
            elif config.type == FeatureType.EMBEDDING:
                features, names = self._extract_embedding_features(nodes, config)
            elif config.type == FeatureType.TEXT:
                features, names = self._extract_text_features(nodes, config)
            elif config.type == FeatureType.GRAPH_STRUCTURAL:
                features, names = self._extract_structural_features(nodes, config, graph)
            else:
                logger.warning(f"Unknown feature type: {config.type}")
                continue

            # Track missing values
            for i, node in enumerate(nodes):
                if name not in node or node[name] is None:
                    missing_mask[i, feature_idx] = True

            # Record feature dimensions
            feature_dims[name] = (current_idx, current_idx + features.shape[1])
            current_idx += features.shape[1]

            feature_arrays.append(features)
            feature_names.extend(names)

        # Concatenate all features
        if feature_arrays:
            all_features = np.concatenate(feature_arrays, axis=1)
        else:
            all_features = np.zeros((len(nodes), 0))

        return ExtractionResult(
            features=all_features,
            feature_names=feature_names,
            feature_dims=feature_dims,
            missing_mask=missing_mask,
            metadata={
                'num_nodes': len(nodes),
                'num_features': len(feature_names),
                'extraction_time': datetime.now().isoformat()
            }
        )

    def _extract_spatial_features(self, nodes: List[Dict[str, Any]],
                                 config: FeatureConfig) -> Tuple[np.ndarray, List[str]]:
        """Extract spatial features like coordinates, H3 cells, regions"""
        feature_values = []

        for node in nodes:
            value = node.get(config.name, config.default_value)

            if value is None:
                # Handle missing spatial data
                if config.name in ['x', 'y', 'z']:
                    feature_values.append([0.0] * (3 if config.name == 'z' else 2))
                elif 'h3' in config.name.lower():
                    feature_values.append([0.0] * 7)  # H3 cell features
                else:
                    feature_values.append([0.0])
            else:
                if isinstance(value, (list, tuple)):
                    feature_values.append(value)
                elif 'h3' in config.name.lower() and isinstance(value, str):
                    # Extract H3 cell features
                    h3_features = self._extract_h3_features(value)
                    feature_values.append(h3_features)
                else:
                    feature_values.append([float(value)])

        features = np.array(feature_values, dtype=np.float32)

        # Apply normalization
        if config.normalization != NormalizationType.NONE:
            features = self._normalize_features(features, config.name, config.normalization)

        # Generate feature names
        if features.shape[1] == 1:
            names = [config.name]
        else:
            names = [f"{config.name}_{i}" for i in range(features.shape[1])]

        return features, names

    def _extract_h3_features(self, h3_cell: str) -> List[float]:
        """Extract features from H3 cell identifier"""
        try:
            # Get H3 resolution
            resolution = h3.h3_get_resolution(h3_cell)

            # Get center coordinates
            lat, lng = h3.h3_to_geo(h3_cell)

            # Get parent cells at different resolutions
            parent_cells = []
            for res in range(max(0, resolution - 2), resolution):
                parent = h3.h3_to_parent(h3_cell, res)
                parent_lat, parent_lng = h3.h3_to_geo(parent)
                parent_cells.extend([parent_lat, parent_lng])

            features = [resolution, lat, lng] + parent_cells

            # Pad to fixed size
            while len(features) < 7:
                features.append(0.0)

            return features[:7]
        except:
            logger.warning(f"Invalid H3 cell: {h3_cell}")
            return [0.0] * 7

    def _extract_temporal_features(self, nodes: List[Dict[str, Any]],
                                  config: FeatureConfig) -> Tuple[np.ndarray, List[str]]:
        """Extract temporal features like timestamps, durations, ages"""
        feature_values = []

        for node in nodes:
            value = node.get(config.name, config.default_value)

            if value is None:
                feature_values.append([0.0] * 7)  # Default temporal features
            else:
                if isinstance(value, (int, float)):
                    # Assume Unix timestamp
                    temporal_features = self._extract_timestamp_features(value)
                elif isinstance(value, str):
                    # Parse datetime string
                    try:
                        dt = datetime.fromisoformat(value)
                        timestamp = dt.timestamp()
                        temporal_features = self._extract_timestamp_features(timestamp)
                    except:
                        temporal_features = [0.0] * 7
                elif isinstance(value, datetime):
                    timestamp = value.timestamp()
                    temporal_features = self._extract_timestamp_features(timestamp)
                else:
                    temporal_features = [0.0] * 7

                feature_values.append(temporal_features)

        features = np.array(feature_values, dtype=np.float32)

        # Apply normalization
        if config.normalization != NormalizationType.NONE:
            features = self._normalize_features(features, config.name, config.normalization)

        # Generate feature names
        names = [
            f"{config.name}_hour",
            f"{config.name}_day_of_week",
            f"{config.name}_day_of_month",
            f"{config.name}_month",
            f"{config.name}_year",
            f"{config.name}_is_weekend",
            f"{config.name}_timestamp_normalized"
        ]

        return features, names[:features.shape[1]]

    def _extract_timestamp_features(self, timestamp: float) -> List[float]:
        """Extract multiple features from a timestamp"""
        dt = datetime.fromtimestamp(timestamp)

        features = [
            dt.hour / 24.0,  # Normalized hour
            dt.weekday() / 6.0,  # Normalized day of week
            dt.day / 31.0,  # Normalized day of month
            dt.month / 12.0,  # Normalized month
            (dt.year - 2000) / 100.0,  # Normalized year
            float(dt.weekday() >= 5),  # Is weekend
            timestamp / 1e10  # Normalized timestamp
        ]

        return features

    def _extract_categorical_features(self, nodes: List[Dict[str, Any]],
                                     config: FeatureConfig) -> Tuple[np.ndarray, List[str]]:
        """Extract categorical features with one-hot or label encoding"""
        values = []

        for node in nodes:
            value = node.get(config.name, config.default_value)
            if value is None:
                value = "unknown"
            values.append(str(value))

        # Fit encoder if not already fitted
        if config.name not in self.encoders:
            self.encoders[config.name] = LabelEncoder()

        try:
            # Try to transform with existing encoder
            encoded = self.encoders[config.name].transform(values)
        except ValueError:
            # Refit if new categories found
            self.encoders[config.name].fit(values)
            encoded = self.encoders[config.name].transform(values)

        # One-hot encode
        num_classes = len(self.encoders[config.name].classes_)
        one_hot = np.zeros((len(nodes), num_classes), dtype=np.float32)
        one_hot[np.arange(len(nodes)), encoded] = 1.0

        # Generate feature names
        names = [f"{config.name}_{cls}" for cls in self.encoders[config.name].classes_]

        return one_hot, names

    def _extract_numerical_features(self, nodes: List[Dict[str, Any]],
                                   config: FeatureConfig) -> Tuple[np.ndarray, List[str]]:
        """Extract numerical features with appropriate scaling"""
        values = []

        for node in nodes:
            value = node.get(config.name, config.default_value)

            if value is None:
                value = 0.0 if config.default_value is None else config.default_value

            # Handle different numerical formats
            if isinstance(value, (list, tuple)):
                values.append(list(value))
            else:
                values.append([float(value)])

        features = np.array(values, dtype=np.float32)

        # Apply constraints if specified
        if 'min' in config.constraints:
            features = np.maximum(features, config.constraints['min'])
        if 'max' in config.constraints:
            features = np.minimum(features, config.constraints['max'])

        # Apply normalization
        if config.normalization != NormalizationType.NONE:
            features = self._normalize_features(features, config.name, config.normalization)

        # Generate feature names
        if features.shape[1] == 1:
            names = [config.name]
        else:
            names = [f"{config.name}_{i}" for i in range(features.shape[1])]

        return features, names

    def _extract_embedding_features(self, nodes: List[Dict[str, Any]],
                                   config: FeatureConfig) -> Tuple[np.ndarray, List[str]]:
        """Extract pre-computed embeddings or generate new ones"""
        embeddings = []
        embedding_dim = config.dimension or 16

        for node in nodes:
            value = node.get(config.name, None)

            if value is None:
                # Generate random embedding or use zero embedding
                if config.default_value == "random":
                    embedding = np.random.randn(embedding_dim) * 0.1
                else:
                    embedding = np.zeros(embedding_dim)
            elif isinstance(value, (list, np.ndarray)):
                embedding = np.array(value)
                if len(embedding) != embedding_dim:
                    # Resize embedding if needed
                    if len(embedding) > embedding_dim:
                        embedding = embedding[:embedding_dim]
                    else:
                        padding = np.zeros(embedding_dim - len(embedding))
                        embedding = np.concatenate([embedding, padding])
            else:
                # Generate embedding from value (e.g., using hash)
                embedding = self._generate_embedding_from_value(value, embedding_dim)

            embeddings.append(embedding)

        features = np.array(embeddings, dtype=np.float32)

        # Normalize embeddings
        if config.normalization != NormalizationType.NONE:
            features = F.normalize(torch.from_numpy(features), p=2, dim=1).numpy()

        # Generate feature names
        names = [f"{config.name}_{i}" for i in range(embedding_dim)]

        return features, names

    def _generate_embedding_from_value(self, value: Any, dim: int) -> np.ndarray:
        """Generate embedding from arbitrary value using hashing"""
        # Convert value to string and hash
        str_value = str(value)
        hash_value = hash(str_value)

        # Use hash as seed for reproducible random embedding
        np.random.seed(abs(hash_value) % (2**32))
        embedding = np.random.randn(dim) * 0.1
        np.random.seed()  # Reset seed

        return embedding

    def _extract_text_features(self, nodes: List[Dict[str, Any]],
                              config: FeatureConfig) -> Tuple[np.ndarray, List[str]]:
        """Extract features from text using TF-IDF or other methods"""
        texts = []

        for node in nodes:
            value = node.get(config.name, config.default_value)
            if value is None:
                texts.append("")
            else:
                texts.append(str(value))

        # Get or create vectorizer
        if config.name not in self.vectorizers:
            self.vectorizers[config.name] = TfidfVectorizer(
                max_features=config.dimension or 100,
                stop_words='english'
            )

        try:
            # Transform texts
            features = self.vectorizers[config.name].fit_transform(texts).toarray()
        except:
            # Fallback to zero features
            features = np.zeros((len(nodes), config.dimension or 100))

        # Generate feature names
        try:
            vocab = self.vectorizers[config.name].get_feature_names_out()
            names = [f"{config.name}_{word}" for word in vocab]
        except:
            names = [f"{config.name}_{i}" for i in range(features.shape[1])]

        return features.astype(np.float32), names

    def _extract_structural_features(self, nodes: List[Dict[str, Any]],
                                    config: FeatureConfig,
                                    graph: Optional[Any]) -> Tuple[np.ndarray, List[str]]:
        """Extract graph structural features like degree, centrality, etc."""
        if graph is None:
            # Return default features if no graph provided
            num_features = 5  # degree, in_degree, out_degree, clustering, pagerank
            features = np.zeros((len(nodes), num_features), dtype=np.float32)
            names = [
                f"{config.name}_degree",
                f"{config.name}_in_degree",
                f"{config.name}_out_degree",
                f"{config.name}_clustering",
                f"{config.name}_pagerank"
            ]
            return features, names

        # Extract structural features from graph
        # This is a placeholder - actual implementation would depend on graph library
        features = []

        for i, node in enumerate(nodes):
            node_id = node.get('id', i)

            # Example structural features
            structural_feats = [
                graph.degree(node_id) if hasattr(graph, 'degree') else 0,
                graph.in_degree(node_id) if hasattr(graph, 'in_degree') else 0,
                graph.out_degree(node_id) if hasattr(graph, 'out_degree') else 0,
                0.0,  # Clustering coefficient placeholder
                0.0   # PageRank placeholder
            ]

            features.append(structural_feats)

        features = np.array(features, dtype=np.float32)

        # Normalize
        if config.normalization != NormalizationType.NONE:
            features = self._normalize_features(features, config.name, config.normalization)

        names = [
            f"{config.name}_degree",
            f"{config.name}_in_degree",
            f"{config.name}_out_degree",
            f"{config.name}_clustering",
            f"{config.name}_pagerank"
        ]

        return features, names

    def _normalize_features(self, features: np.ndarray, name: str,
                           normalization: NormalizationType) -> np.ndarray:
        """Apply normalization to features"""
        if normalization == NormalizationType.NONE:
            return features

        # Handle single feature vs multiple features
        if features.ndim == 1:
            features = features.reshape(-1, 1)
            single_feature = True
        else:
            single_feature = False

        # Apply normalization
        if normalization == NormalizationType.LOG:
            # Log transformation (add small epsilon to avoid log(0))
            features = np.log1p(np.abs(features))
        else:
            # Use scikit-learn scalers
            if name not in self.scalers:
                if normalization == NormalizationType.STANDARD:
                    self.scalers[name] = StandardScaler()
                elif normalization == NormalizationType.MINMAX:
                    self.scalers[name] = MinMaxScaler()
                elif normalization == NormalizationType.ROBUST:
                    self.scalers[name] = RobustScaler()

            try:
                features = self.scalers[name].fit_transform(features)
            except:
                logger.warning(f"Failed to normalize {name}, using raw values")

        if single_feature:
            features = features.ravel()

        return features

    def handle_missing_data(self, features: np.ndarray,
                           missing_mask: np.ndarray,
                           strategy: str = "mean") -> np.ndarray:
        """
        Handle missing data in features.

        Args:
            features: Feature array with missing values
            missing_mask: Boolean mask indicating missing values
            strategy: Imputation strategy ("mean", "median", "zero", "forward_fill")

        Returns:
            Features with missing values imputed
        """
        if not np.any(missing_mask):
            return features

        features_imputed = features.copy()

        for feature_idx in range(features.shape[1]):
            missing_in_feature = missing_mask[:, feature_idx]

            if not np.any(missing_in_feature):
                continue

            if strategy == "mean":
                fill_value = np.mean(features[~missing_in_feature, feature_idx])
            elif strategy == "median":
                fill_value = np.median(features[~missing_in_feature, feature_idx])
            elif strategy == "zero":
                fill_value = 0.0
            elif strategy == "forward_fill":
                # Forward fill missing values
                last_valid = 0.0
                for i in range(len(features)):
                    if missing_in_feature[i]:
                        features_imputed[i, feature_idx] = last_valid
                    else:
                        last_valid = features_imputed[i, feature_idx]
                continue
            else:
                fill_value = 0.0

            features_imputed[missing_in_feature, feature_idx] = fill_value

        return features_imputed


# Example usage
if __name__ == "__main__":
    # Define feature configurations
    feature_configs = [
        FeatureConfig(
            name="position",
            type=FeatureType.SPATIAL,
            dimension=2,
            normalization=NormalizationType.MINMAX
        ),
        FeatureConfig(
            name="timestamp",
            type=FeatureType.TEMPORAL,
            normalization=NormalizationType.STANDARD
        ),
        FeatureConfig(
            name="status",
            type=FeatureType.CATEGORICAL
        ),
        FeatureConfig(
            name="energy",
            type=FeatureType.NUMERICAL,
            normalization=NormalizationType.MINMAX,
            constraints={"min": 0, "max": 1}
        ),
        FeatureConfig(
            name="embedding",
            type=FeatureType.EMBEDDING,
            dimension=16,
            normalization=NormalizationType.NONE
        )
    ]

    # Create extractor
    extractor = NodeFeatureExtractor(feature_configs)

    # Example nodes
    nodes = [
        {
            "id": 1,
            "position": [0.5, 0.3],
            "timestamp": 1642000000,
            "status": "active",
            "energy": 0.8
        },
        {
            "id": 2,
            "position": [0.7, 0.9],
            "timestamp": 1642001000,
            "status": "idle",
            "energy": 0.3
        }
    ]

    # Extract features
    result = extractor.extract_features(nodes)

    print(f"Features shape: {result.features.shape}")
    print(f"Feature names: {result.feature_names[:10]}...")  # First 10
    print(f"Feature dimensions: {result.feature_dims}")
