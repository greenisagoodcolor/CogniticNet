"""
Coalition Formation and Management System

This module provides functionality for multi-agent coalition formation,
shared goal alignment, and value distribution mechanisms.
"""
from .coalition-criteria import CoalitionFormationCriteria, CompatibilityMetric, FormationTrigger, DissolutionCondition
from .coalition_models import Coalition, CoalitionMember, CoalitionRole, CoalitionStatus, CoalitionGoal
from .formation_algorithms import CoalitionFormationAlgorithm, ContractNetProtocol, AuctionBasedFormation, GreedyCoalitionFormation
from .business-opportunities import BusinessOpportunity, OpportunityDetector, OpportunityMetrics, OpportunityValidator
from .value_distribution import ValueDistributionModel, ShapleyValueCalculator, ProportionalDistribution, ContributionTracker
__all__ = ['CoalitionFormationCriteria', 'CompatibilityMetric', 'FormationTrigger', 'DissolutionCondition', 'Coalition', 'CoalitionMember', 'CoalitionRole', 'CoalitionStatus', 'CoalitionGoal', 'CoalitionFormationAlgorithm', 'ContractNetProtocol', 'AuctionBasedFormation', 'GreedyCoalitionFormation', 'BusinessOpportunity', 'OpportunityDetector', 'OpportunityMetrics', 'OpportunityValidator', 'ValueDistributionModel', 'ShapleyValueCalculator', 'ProportionalDistribution', 'ContributionTracker']
