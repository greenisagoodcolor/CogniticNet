"""
Active Inference Engine for CogniticNet

This module implements the Active Inference framework for agent cognition,
including generative models, inference algorithms, and action selection.
"""

from .generative_model import (
    ModelDimensions,
    ModelParameters,
    GenerativeModel,
    DiscreteGenerativeModel,
    ContinuousGenerativeModel,
    HierarchicalGenerativeModel,
    FactorizedGenerativeModel,
    create_generative_model
)

__all__ = [
    'ModelDimensions',
    'ModelParameters',
    'GenerativeModel',
    'DiscreteGenerativeModel',
    'ContinuousGenerativeModel',
    'HierarchicalGenerativeModel',
    'FactorizedGenerativeModel',
    'create_generative_model'
]
