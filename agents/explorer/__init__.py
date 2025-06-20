"""
Explorer Agent Module for FreeAgentics

This module provides the Explorer agent type and related exploration functionality,
including mapping, discovery systems, and specialized exploration behaviors.
"""

from .explorer import (
    # Main agent class
    ExplorerAgent,
    
    # Explorer-specific enums and data classes
    ExplorationStatus,
    DiscoveryType,
    Discovery,
    ExplorationMap,
    
    # Specialized behaviors
    AdvancedExplorationBehavior,
    PathfindingBehavior,
    
    # Factory functions
    create_explorer_agent,
    register_explorer_type
)

__all__ = [
    # Main classes
    'ExplorerAgent',
    'ExplorationMap',
    'Discovery',
    
    # Enums
    'ExplorationStatus',
    'DiscoveryType',
    
    # Behaviors
    'AdvancedExplorationBehavior',
    'PathfindingBehavior',
    
    # Factory functions
    'create_explorer_agent',
    'register_explorer_type'
]

# Version information
__version__ = '0.1.0'
