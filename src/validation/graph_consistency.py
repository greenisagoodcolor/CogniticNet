"""
Graph Consistency Validation Module
Ensures knowledge graphs remain valid and consistent throughout operations.

Following Robert C. Martin's principle: 
'The architecture must scream Active Inference Platform from every module.'
"""

import networkx as nx
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConsistencyReport:
    """Report of graph consistency check results."""
    is_consistent: bool
    errors: List[str]
    warnings: List[str]
    metrics: Dict[str, Any]
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class GraphConsistencyValidator:
    """
    Validates structural consistency of knowledge graphs.
    
    Ensures:
    - Graph connectivity requirements
    - Node and edge validity
    - Embedding consistency
    - Reference integrity
    """
    
    def __init__(self, max_graph_size: int = 10000):
        self.max_graph_size = max_graph_size
        self.required_node_attrs = {'type', 'data', 'timestamp'}
        self.required_edge_attrs = {'type', 'weight', 'confidence'}
        self.valid_node_types = {'experience', 'pattern', 'belief', 'concept'}
        self.valid_edge_types = {'causes', 'correlates', 'precedes', 'contradicts', 'supports'}
    
    def validate_graph(self, graph: nx.DiGraph) -> ConsistencyReport:
        """
        Perform comprehensive consistency validation on a knowledge graph.
        
        Args:
            graph: NetworkX directed graph to validate
            
        Returns:
            ConsistencyReport with validation results
        """
        errors = []
        warnings = []
        metrics = {}
        
        # Basic graph properties
        metrics['node_count'] = graph.number_of_nodes()
        metrics['edge_count'] = graph.number_of_edges()
        
        # Size check
        if metrics['node_count'] > self.max_graph_size:
            errors.append(f"Graph exceeds maximum size: {metrics['node_count']} > {self.max_graph_size}")
        
        # Connectivity checks
        connectivity_errors = self._check_connectivity(graph)
        errors.extend(connectivity_errors)
        
        # Node validity
        node_errors, node_warnings = self._check_nodes(graph)
        errors.extend(node_errors)
        warnings.extend(node_warnings)
        
        # Edge validity
        edge_errors, edge_warnings = self._check_edges(graph)
        errors.extend(edge_errors)
        warnings.extend(edge_warnings)
        
        # Structural consistency
        structural_errors = self._check_structural_consistency(graph)
        errors.extend(structural_errors)
        
        # Embedding consistency (if embeddings exist)
        if self._has_embeddings(graph):
            embedding_errors = self._check_embedding_consistency(graph)
            errors.extend(embedding_errors)
        
        # Calculate additional metrics
        metrics.update(self._calculate_graph_metrics(graph))
        
        return ConsistencyReport(
            is_consistent=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            metrics=metrics
        )
    
    def _check_connectivity(self, graph: nx.DiGraph) -> List[str]:
        """Check graph connectivity requirements."""
        errors = []
        
        # Check for isolated nodes
        isolated = list(nx.isolates(graph))
        if isolated:
            errors.append(f"Found {len(isolated)} isolated nodes: {isolated[:5]}...")
        
        # Check for disconnected components
        if not nx.is_weakly_connected(graph):
            components = list(nx.weakly_connected_components(graph))
            errors.append(f"Graph has {len(components)} disconnected components")
        
        # Check for self-loops
        self_loops = list(nx.selfloop_edges(graph))
        if self_loops:
            errors.append(f"Found {len(self_loops)} self-loops")
        
        return errors
    
    def _check_nodes(self, graph: nx.DiGraph) -> Tuple[List[str], List[str]]:
        """Validate all nodes in the graph."""
        errors = []
        warnings = []
        
        for node_id, attrs in graph.nodes(data=True):
            # Check required attributes
            missing_attrs = self.required_node_attrs - set(attrs.keys())
            if missing_attrs:
                errors.append(f"Node {node_id} missing attributes: {missing_attrs}")
            
            # Validate node type
            if 'type' in attrs and attrs['type'] not in self.valid_node_types:
                errors.append(f"Node {node_id} has invalid type: {attrs['type']}")
            
            # Check timestamp validity
            if 'timestamp' in attrs:
                try:
                    if isinstance(attrs['timestamp'], str):
                        datetime.fromisoformat(attrs['timestamp'])
                except:
                    warnings.append(f"Node {node_id} has invalid timestamp format")
            
            # Check for empty data
            if 'data' in attrs and not attrs['data']:
                warnings.append(f"Node {node_id} has empty data")
        
        return errors, warnings
    
    def _check_edges(self, graph: nx.DiGraph) -> Tuple[List[str], List[str]]:
        """Validate all edges in the graph."""
        errors = []
        warnings = []
        
        for u, v, attrs in graph.edges(data=True):
            # Check required attributes
            missing_attrs = self.required_edge_attrs - set(attrs.keys())
            if missing_attrs:
                errors.append(f"Edge ({u}, {v}) missing attributes: {missing_attrs}")
            
            # Validate edge type
            if 'type' in attrs and attrs['type'] not in self.valid_edge_types:
                errors.append(f"Edge ({u}, {v}) has invalid type: {attrs['type']}")
            
            # Validate weight
            if 'weight' in attrs:
                weight = attrs['weight']
                if not isinstance(weight, (int, float)) or weight < 0 or weight > 1:
                    errors.append(f"Edge ({u}, {v}) has invalid weight: {weight}")
            
            # Validate confidence
            if 'confidence' in attrs:
                conf = attrs['confidence']
                if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
                    errors.append(f"Edge ({u}, {v}) has invalid confidence: {conf}")
        
        return errors, warnings
    
    def _check_structural_consistency(self, graph: nx.DiGraph) -> List[str]:
        """Check for structural inconsistencies."""
        errors = []
        
        # Check for cycles in certain edge types
        for edge_type in ['precedes']:  # Temporal edges should not have cycles
            subgraph = nx.DiGraph()
            for u, v, attrs in graph.edges(data=True):
                if attrs.get('type') == edge_type:
                    subgraph.add_edge(u, v)
            
            if subgraph.number_of_edges() > 0:
                try:
                    cycles = list(nx.simple_cycles(subgraph))
                    if cycles:
                        errors.append(f"Found {len(cycles)} cycles in {edge_type} relationships")
                except:
                    pass  # Graph might be too large for cycle detection
        
        # Check for contradictory relationships
        for u, v, attrs in graph.edges(data=True):
            if attrs.get('type') == 'supports':
                # Check if there's also a contradicts edge
                if graph.has_edge(u, v):
                    reverse_attrs = graph[u][v]
                    if reverse_attrs.get('type') == 'contradicts':
                        errors.append(f"Nodes {u} and {v} have both 'supports' and 'contradicts' relationships")
        
        return errors
    
    def _has_embeddings(self, graph: nx.DiGraph) -> bool:
        """Check if graph nodes have embeddings."""
        for _, attrs in graph.nodes(data=True):
            if 'embedding' in attrs:
                return True
        return False
    
    def _check_embedding_consistency(self, graph: nx.DiGraph) -> List[str]:
        """Validate embedding consistency."""
        errors = []
        embedding_dims = set()
        
        for node_id, attrs in graph.nodes(data=True):
            if 'embedding' in attrs:
                embedding = attrs['embedding']
                
                # Check if embedding is valid array
                try:
                    emb_array = np.array(embedding)
                    if emb_array.ndim != 1:
                        errors.append(f"Node {node_id} has invalid embedding dimensionality")
                    else:
                        embedding_dims.add(emb_array.shape[0])
                    
                    # Check for NaN or inf values
                    if np.any(np.isnan(emb_array)) or np.any(np.isinf(emb_array)):
                        errors.append(f"Node {node_id} has NaN or inf values in embedding")
                    
                except:
                    errors.append(f"Node {node_id} has invalid embedding format")
        
        # Check dimension consistency
        if len(embedding_dims) > 1:
            errors.append(f"Inconsistent embedding dimensions: {embedding_dims}")
        
        return errors
    
    def _calculate_graph_metrics(self, graph: nx.DiGraph) -> Dict[str, Any]:
        """Calculate additional graph metrics."""
        metrics = {}
        
        # Density
        metrics['density'] = nx.density(graph)
        
        # Average degree
        metrics['avg_degree'] = sum(dict(graph.degree()).values()) / graph.number_of_nodes() if graph.number_of_nodes() > 0 else 0
        
        # Component count
        metrics['num_components'] = nx.number_weakly_connected_components(graph)
        
        # Node type distribution
        type_counts = defaultdict(int)
        for _, attrs in graph.nodes(data=True):
            node_type = attrs.get('type', 'unknown')
            type_counts[node_type] += 1
        metrics['node_type_distribution'] = dict(type_counts)
        
        # Edge type distribution
        edge_type_counts = defaultdict(int)
        for _, _, attrs in graph.edges(data=True):
            edge_type = attrs.get('type', 'unknown')
            edge_type_counts[edge_type] += 1
        metrics['edge_type_distribution'] = dict(edge_type_counts)
        
        return metrics
    
    def repair_graph(self, graph: nx.DiGraph, report: ConsistencyReport) -> nx.DiGraph:
        """
        Attempt to repair common graph inconsistencies.
        
        Args:
            graph: Graph to repair
            report: Consistency report identifying issues
            
        Returns:
            Repaired graph (modifies in place)
        """
        logger.info(f"Attempting to repair {len(report.errors)} errors")
        
        # Remove self-loops
        graph.remove_edges_from(nx.selfloop_edges(graph))
        
        # Remove isolated nodes
        isolated = list(nx.isolates(graph))
        graph.remove_nodes_from(isolated)
        logger.info(f"Removed {len(isolated)} isolated nodes")
        
        # Add missing attributes with defaults
        for node_id, attrs in graph.nodes(data=True):
            for required_attr in self.required_node_attrs:
                if required_attr not in attrs:
                    if required_attr == 'type':
                        attrs[required_attr] = 'concept'
                    elif required_attr == 'timestamp':
                        attrs[required_attr] = datetime.utcnow().isoformat()
                    elif required_attr == 'data':
                        attrs[required_attr] = {}
        
        for u, v, attrs in graph.edges(data=True):
            for required_attr in self.required_edge_attrs:
                if required_attr not in attrs:
                    if required_attr == 'type':
                        attrs[required_attr] = 'correlates'
                    elif required_attr == 'weight':
                        attrs[required_attr] = 0.5
                    elif required_attr == 'confidence':
                        attrs[required_attr] = 0.5
        
        return graph


class GraphIntegrityMonitor:
    """
    Monitors graph integrity over time and detects degradation.
    """
    
    def __init__(self, validator: GraphConsistencyValidator):
        self.validator = validator
        self.history: List[ConsistencyReport] = []
        self.alert_threshold = 0.1  # 10% error rate triggers alert
    
    def check_integrity(self, graph: nx.DiGraph) -> Tuple[bool, Optional[str]]:
        """
        Check graph integrity and return status.
        
        Returns:
            (is_healthy, alert_message)
        """
        report = self.validator.validate_graph(graph)
        self.history.append(report)
        
        # Calculate error rate
        total_checks = report.metrics['node_count'] + report.metrics['edge_count']
        error_rate = len(report.errors) / max(total_checks, 1)
        
        if error_rate > self.alert_threshold:
            alert_msg = f"Graph integrity degraded: {len(report.errors)} errors ({error_rate:.1%} error rate)"
            return False, alert_msg
        
        # Check for trend
        if len(self.history) >= 5:
            recent_errors = [len(r.errors) for r in self.history[-5:]]
            if all(recent_errors[i] <= recent_errors[i+1] for i in range(4)):
                alert_msg = "Graph integrity degrading over time"
                return False, alert_msg
        
        return True, None
    
    def get_integrity_metrics(self) -> Dict[str, Any]:
        """Get integrity metrics over time."""
        if not self.history:
            return {}
        
        return {
            'total_checks': len(self.history),
            'avg_errors': np.mean([len(r.errors) for r in self.history]),
            'avg_warnings': np.mean([len(r.warnings) for r in self.history]),
            'last_check': self.history[-1].timestamp,
            'trend': self._calculate_trend()
        }
    
    def _calculate_trend(self) -> str:
        """Calculate error trend."""
        if len(self.history) < 2:
            return 'insufficient_data'
        
        recent = [len(r.errors) for r in self.history[-10:]]
        if len(set(recent)) == 1:
            return 'stable'
        
        # Simple linear regression
        x = np.arange(len(recent))
        slope = np.polyfit(x, recent, 1)[0]
        
        if slope > 0.1:
            return 'degrading'
        elif slope < -0.1:
            return 'improving'
        else:
            return 'stable' 