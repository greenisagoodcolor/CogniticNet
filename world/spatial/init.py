"""
Spatial Computing Module for FreeAgentics

This module provides comprehensive spatial operations using H3 hexagonal grid system.
Includes pathfinding, resource distribution, visibility calculations, and world modeling.
"""
from .spatial_api import SpatialAPI, SpatialCoordinate, ResourceType, ResourceDistribution, ObservationModel
from ..world.h3_world import H3World, HexCell, Biome, TerrainType
__all__ = ['SpatialAPI', 'SpatialCoordinate', 'ResourceType', 'ResourceDistribution', 'ObservationModel', 'H3World', 'HexCell', 'Biome', 'TerrainType']
__version__ = '1.0.0'
