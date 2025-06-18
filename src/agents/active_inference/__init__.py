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

from .precision import (
    PrecisionConfig,
    PrecisionOptimizer,
    GradientPrecisionOptimizer,
    HierarchicalPrecisionOptimizer,
    MetaLearningPrecisionOptimizer,
    AdaptivePrecisionController,
    create_precision_optimizer
)

from .policy_selection import (
    PolicyConfig,
    Policy,
    PolicySelector,
    DiscreteExpectedFreeEnergy,
    ContinuousExpectedFreeEnergy,
    HierarchicalPolicySelector,
    SophisticatedInference,
    create_policy_selector
)

from .temporal_planning import (
    PlanningConfig,
    TreeNode,
    TemporalPlanner,
    MonteCarloTreeSearch,
    BeamSearchPlanner,
    AStarPlanner,
    TrajectorySampling,
    AdaptiveHorizonPlanner,
    create_temporal_planner
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
    'create_inference_algorithm',
    # Precision optimization
    'PrecisionConfig',
    'PrecisionOptimizer',
    'GradientPrecisionOptimizer',
    'HierarchicalPrecisionOptimizer',
    'MetaLearningPrecisionOptimizer',
    'AdaptivePrecisionController',
    'create_precision_optimizer',
    # Policy selection
    'PolicyConfig',
    'Policy',
    'PolicySelector',
    'DiscreteExpectedFreeEnergy',
    'ContinuousExpectedFreeEnergy',
    'HierarchicalPolicySelector',
    'SophisticatedInference',
    'create_policy_selector',
    # Temporal planning
    'PlanningConfig',
    'TreeNode',
    'TemporalPlanner',
    'MonteCarloTreeSearch',
    'BeamSearchPlanner',
    'AStarPlanner',
    'TrajectorySampling',
    'AdaptiveHorizonPlanner',
    'create_temporal_planner'
]
