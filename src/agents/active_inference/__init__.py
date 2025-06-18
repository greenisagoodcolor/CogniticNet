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

from .inference import (
    InferenceConfig,
    InferenceAlgorithm,
    VariationalMessagePassing,
    BeliefPropagation,
    GradientDescentInference,
    NaturalGradientInference,
    ExpectationMaximization,
    ParticleFilterInference,
    create_inference_algorithm
)

__all__ = [
    # Generative models
    'ModelDimensions',
    'ModelParameters',
    'GenerativeModel',
    'DiscreteGenerativeModel',
    'ContinuousGenerativeModel',
    'HierarchicalGenerativeModel',
    'FactorizedGenerativeModel',
    'create_generative_model',
    # Inference algorithms
    'InferenceConfig',
    'InferenceAlgorithm',
    'VariationalMessagePassing',
    'BeliefPropagation',
    'GradientDescentInference',
    'NaturalGradientInference',
    'ExpectationMaximization',
    'ParticleFilterInference',
    'create_inference_algorithm'
]
