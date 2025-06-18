"""
Spatial Computing Module for CogniticNet

This module provides comprehensive spatial operations using H3 hexagonal grid system.
Includes pathfinding, resource distribution, visibility calculations, and world modeling.
"""

from .spatial_api import (
    SpatialAPI,
    SpatialCoordinate,
    ResourceType,
    ResourceDistribution,
    ObservationModel
)

# For backward compatibility and convenience
from ..world.h3_world import (
    H3World,
    HexCell,
    Biome,
    TerrainType
)

__all__ = [
    # Core API
    'SpatialAPI',
    'SpatialCoordinate',

    # Resource Management
    'ResourceType',
    'ResourceDistribution',

    # Observation/Visibility
    'ObservationModel',

    # World Components
    'H3World',
    'HexCell',
    'Biome',
    'TerrainType'
]

# Module version
__version__ = '1.0.0'
