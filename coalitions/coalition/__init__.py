"""
Coalition Formation and Management System

This module provides functionality for multi-agent coalition formation,
shared goal alignment, and value distribution mechanisms.
"""

from .coalition_criteria import (
    CoalitionFormationCriteria,
    CompatibilityMetric,
    FormationTrigger,
    DissolutionCondition
)

from .coalition_models import (
    Coalition,
    CoalitionMember,
    CoalitionRole,
    CoalitionStatus,
    CoalitionGoal
)

from .formation_algorithms import (
    CoalitionFormationAlgorithm,
    ContractNetProtocol,
    AuctionBasedFormation,
    GreedyCoalitionFormation
)

from .business_opportunities import (
    BusinessOpportunity,
    OpportunityDetector,
    OpportunityMetrics,
    OpportunityValidator
)

from .value_distribution import (
    ValueDistributionModel,
    ShapleyValueCalculator,
    ProportionalDistribution,
    ContributionTracker
)

__all__ = [
    # Criteria
    'CoalitionFormationCriteria',
    'CompatibilityMetric',
    'FormationTrigger',
    'DissolutionCondition',

    # Models
    'Coalition',
    'CoalitionMember',
    'CoalitionRole',
    'CoalitionStatus',
    'CoalitionGoal',

    # Formation
    'CoalitionFormationAlgorithm',
    'ContractNetProtocol',
    'AuctionBasedFormation',
    'GreedyCoalitionFormation',

    # Business
    'BusinessOpportunity',
    'OpportunityDetector',
    'OpportunityMetrics',
    'OpportunityValidator',

    # Value
    'ValueDistributionModel',
    'ShapleyValueCalculator',
    'ProportionalDistribution',
    'ContributionTracker'
]
