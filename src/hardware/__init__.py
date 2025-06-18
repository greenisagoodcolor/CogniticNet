"""
Hardware Abstraction Layer (HAL) for CogniticNet

This module provides a unified interface for hardware operations across different
platforms and devices, enabling deployment on edge devices with resource constraints.
"""

from .hal_core import (
    HardwareAbstractionLayer,
    DeviceCapabilities,
    ResourceConstraints,
    HardwareInterface
)

from .device_discovery import (
    DeviceDiscovery,
    DeviceInfo,
    DeviceType,
    DeviceStatus
)

from .resource_manager import (
    ResourceManager,
    ResourceAllocation,
    ResourcePriority,
    ResourceMonitor
)

from .offline_capabilities import (
    OfflineManager,
    StatePersistence,
    WorkQueue,
    SyncManager
)

__all__ = [
    # Core HAL
    'HardwareAbstractionLayer',
    'DeviceCapabilities',
    'ResourceConstraints',
    'HardwareInterface',

    # Device Discovery
    'DeviceDiscovery',
    'DeviceInfo',
    'DeviceType',
    'DeviceStatus',

    # Resource Management
    'ResourceManager',
    'ResourceAllocation',
    'ResourcePriority',
    'ResourceMonitor',

    # Offline Operations
    'OfflineManager',
    'StatePersistence',
    'WorkQueue',
    'SyncManager'
]

# Module version
__version__ = '1.0.0'
