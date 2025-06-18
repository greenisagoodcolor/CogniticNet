"""
Active Inference Engine for FreeAgentics

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

# GNN integration
from .gnn_integration import (
    GNNIntegrationConfig,
    DirectGraphMapper,
    LearnedGraphMapper,
    GNNActiveInferenceAdapter,
    GraphFeatureAggregator,
    HierarchicalGraphIntegration,
    create_gnn_adapter
)

# Belief update
from .belief_update import (
    BeliefUpdateConfig,
    DirectGraphObservationModel,
    LearnedGraphObservationModel,
    GNNBeliefUpdater,
    AttentionGraphBeliefUpdater,
    HierarchicalBeliefUpdater,
    create_belief_updater
)

# Hierarchical inference
from .hierarchical_inference import (
    HierarchicalConfig,
    HierarchicalState,
    HierarchicalLevel,
    HierarchicalInference,
    TemporalHierarchicalInference,
    create_hierarchical_inference
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
    'create_temporal_planner',
    # GNN integration
    'GNNIntegrationConfig',
    'DirectGraphMapper',
    'LearnedGraphMapper',
    'GNNActiveInferenceAdapter',
    'GraphFeatureAggregator',
    'HierarchicalGraphIntegration',
    'create_gnn_adapter',
    # Belief update
    'BeliefUpdateConfig',
    'DirectGraphObservationModel',
    'LearnedGraphObservationModel',
    'GNNBeliefUpdater',
    'AttentionGraphBeliefUpdater',
    'HierarchicalBeliefUpdater',
    'create_belief_updater',
    # Hierarchical inference
    'HierarchicalConfig',
    'HierarchicalState',
    'HierarchicalLevel',
    'HierarchicalInference',
    'TemporalHierarchicalInference',
    'create_hierarchical_inference'
]
