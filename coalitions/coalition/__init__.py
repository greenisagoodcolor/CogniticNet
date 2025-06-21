"""
Coalition Formation and Management System

This module provides functionality for multi-agent coalition formation,
shared goal alignment, and value distribution mechanisms.
"""
from .coalition_criteria import CoalitionFormationCriteria, CompatibilityMetric, FormationTrigger, DissolutionCondition
from .coalition_models import Coalition, CoalitionMember, CoalitionRole, CoalitionStatus, CoalitionGoal, CoalitionGoalStatus
from .business_opportunities import BusinessOpportunity, OpportunityDetector, OpportunityMetrics, OpportunityValidator

__all__ = [
    'CoalitionFormationCriteria', 'CompatibilityMetric', 'FormationTrigger', 'DissolutionCondition',
    'Coalition', 'CoalitionMember', 'CoalitionRole', 'CoalitionStatus', 'CoalitionGoal', 'CoalitionGoalStatus',
    'BusinessOpportunity', 'OpportunityDetector', 'OpportunityMetrics', 'OpportunityValidator'
]
