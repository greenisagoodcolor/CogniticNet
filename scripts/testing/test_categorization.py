#!/usr/bin/env python3
"""
Test Categorization and Tagging Module for FreeAgentics Repository

This module implements comprehensive test categorization and tagging following
expert committee guidance from Kent Beck (TDD) and Gary Bernhardt (Testing Strategies).

Expert Committee Guidance:
- Kent Beck: "Tests should clearly communicate their intent and scope"
- Gary Bernhardt: "Test boundaries define system architecture"
- Michael Feathers: "Test categories guide refactoring safety"
- Robert Martin: "Clean test organization reflects clean architecture"

Following Clean Code and SOLID principles with extensible tagging system.
"""

import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union
from collections import defaultdict
import json
import yaml
from test_discovery import (
    TestFile,
    TestDiscoveryResult,
    TestType,
    TestFramework,
    TestLanguage,
)


class TestPriority(Enum):
    """Test priority levels for execution order and resource allocation."""

    CRITICAL = "critical"  # Must pass for release
    HIGH = "high"  # Important functionality
    MEDIUM = "medium"  # Standard test coverage
    LOW = "low"  # Nice-to-have coverage
    UNKNOWN = "unknown"  # Cannot determine priority


class TestCategory(Enum):
    """Functional area categories for test organization."""

    CORE_LOGIC = "core_logic"  # Business logic tests
    API = "api"  # API endpoint tests
    DATABASE = "database"  # Data persistence tests
    UI = "ui"  # User interface tests
    AUTHENTICATION = "authentication"  # Auth/security tests
    INTEGRATION = "integration"  # System integration
    PERFORMANCE = "performance"  # Performance/load tests
    SECURITY = "security"  # Security-specific tests
    UTILITY = "utility"  # Helper/utility tests
    CONFIGURATION = "configuration"  # Config/setup tests
    DEPLOYMENT = "deployment"  # Deployment/infrastructure
    UNKNOWN = "unknown"  # Cannot categorize


class TestStability(Enum):
    """Test stability classification for CI/CD strategy."""

    STABLE = "stable"  # Reliable, rarely flaky
    FLAKY = "flaky"  # Occasionally fails
    UNSTABLE = "unstable"  # Frequently fails
    NEW = "new"  # Recently added
    UNKNOWN = "unknown"  # Stability not assessed


class TestExecutionTier(Enum):
    """Execution tier for CI/CD pipeline optimization."""

    SMOKE = "smoke"  # Quick sanity checks
    FAST = "fast"  # < 1 second per test
    MEDIUM = "medium"  # 1-10 seconds per test
    SLOW = "slow"  # 10+ seconds per test
    MANUAL = "manual"  # Requires manual intervention
    UNKNOWN = "unknown"  # Execution time not measured


@dataclass
class TestTag:
    """
    Represents a test tag with metadata.

    Following Kent Beck's principle that tags should be meaningful
    and provide clear context for test organization.
    """

    name: str
    category: str
    description: str
    color: str = "#666666"
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "color": self.color,
            "priority": self.priority,
        }


@dataclass
class CategorizedTestFile:
    """
    Enhanced test file with categorization and tagging information.

    Extends TestFile with expert committee guidance for comprehensive
    test organization and management.
    """

    test_file: TestFile

    # Categorization
    priority: TestPriority = TestPriority.UNKNOWN
    category: TestCategory = TestCategory.UNKNOWN
    stability: TestStability = TestStability.UNKNOWN
    execution_tier: TestExecutionTier = TestExecutionTier.UNKNOWN

    # Tagging
    tags: Set[str] = field(default_factory=set)
    functional_areas: Set[str] = field(default_factory=set)

    # Metadata
    estimated_duration: float = 0.0  # seconds
    last_failure_date: Optional[str] = None
    failure_rate: float = 0.0  # percentage

    # Dependencies and relationships
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    related_features: List[str] = field(default_factory=list)

    # CI/CD configuration
    required_for_merge: bool = False
    runs_in_parallel: bool = True
    requires_docker: bool = False
    requires_database: bool = False

    # Documentation
    purpose: str = ""
    owner: str = ""
    documentation_url: str = ""

    def add_tag(self, tag: str) -> None:
        """Add a tag to the test file."""
        self.tags.add(tag)

    def add_functional_area(self, area: str) -> None:
        """Add a functional area to the test file."""
        self.functional_areas.add(area)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_file": self.test_file.to_dict(),
            "priority": self.priority.value,
            "category": self.category.value,
            "stability": self.stability.value,
            "execution_tier": self.execution_tier.value,
            "tags": list(self.tags),
            "functional_areas": list(self.functional_areas),
            "estimated_duration": self.estimated_duration,
            "last_failure_date": self.last_failure_date,
            "failure_rate": self.failure_rate,
            "depends_on": self.depends_on,
            "blocks": self.blocks,
            "related_features": self.related_features,
            "required_for_merge": self.required_for_merge,
            "runs_in_parallel": self.runs_in_parallel,
            "requires_docker": self.requires_docker,
            "requires_database": self.requires_database,
            "purpose": self.purpose,
            "owner": self.owner,
            "documentation_url": self.documentation_url,
        }


@dataclass
class TestCategorizationResult:
    """
    Complete test categorization results with comprehensive analysis.

    Provides actionable insights for CI/CD pipeline configuration
    and test management following expert committee guidance.
    """

    categorized_tests: List[CategorizedTestFile] = field(default_factory=list)

    # Statistics
    total_tests: int = 0
    by_priority: Dict[str, int] = field(default_factory=dict)
    by_category: Dict[str, int] = field(default_factory=dict)
    by_stability: Dict[str, int] = field(default_factory=dict)
    by_execution_tier: Dict[str, int] = field(default_factory=dict)

    # Tagging statistics
    tag_usage: Dict[str, int] = field(default_factory=dict)
    functional_area_coverage: Dict[str, int] = field(default_factory=dict)

    # CI/CD insights
    critical_path_tests: List[str] = field(default_factory=list)
    parallel_execution_groups: Dict[str, List[str]] = field(default_factory=dict)
    estimated_total_duration: float = 0.0

    # Quality metrics
    test_coverage_gaps: List[str] = field(default_factory=list)
    recommended_tags: List[TestTag] = field(default_factory=list)

    # Categorization metadata
    categorization_duration: float = 0.0
    errors_encountered: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def add_categorized_test(self, categorized_test: CategorizedTestFile) -> None:
        """Add a categorized test and update statistics."""
        self.categorized_tests.append(categorized_test)
        self.total_tests += 1

        # Update statistics
        self.by_priority[categorized_test.priority.value] = (
            self.by_priority.get(categorized_test.priority.value, 0) + 1
        )
        self.by_category[categorized_test.category.value] = (
            self.by_category.get(categorized_test.category.value, 0) + 1
        )
        self.by_stability[categorized_test.stability.value] = (
            self.by_stability.get(categorized_test.stability.value, 0) + 1
        )
        self.by_execution_tier[categorized_test.execution_tier.value] = (
            self.by_execution_tier.get(categorized_test.execution_tier.value, 0) + 1
        )

        # Update tag statistics
        for tag in categorized_test.tags:
            self.tag_usage[tag] = self.tag_usage.get(tag, 0) + 1

        for area in categorized_test.functional_areas:
            self.functional_area_coverage[area] = (
                self.functional_area_coverage.get(area, 0) + 1
            )

        # Update duration estimate
        self.estimated_total_duration += categorized_test.estimated_duration

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "categorized_tests": [ct.to_dict() for ct in self.categorized_tests],
            "total_tests": self.total_tests,
            "by_priority": self.by_priority,
            "by_category": self.by_category,
            "by_stability": self.by_stability,
            "by_execution_tier": self.by_execution_tier,
            "tag_usage": self.tag_usage,
            "functional_area_coverage": self.functional_area_coverage,
            "critical_path_tests": self.critical_path_tests,
            "parallel_execution_groups": self.parallel_execution_groups,
            "estimated_total_duration": self.estimated_total_duration,
            "test_coverage_gaps": self.test_coverage_gaps,
            "recommended_tags": [tag.to_dict() for tag in self.recommended_tags],
            "categorization_duration": self.categorization_duration,
            "errors_encountered": self.errors_encountered,
            "recommendations": self.recommendations,
        }


class TestCategorizer:
    """
    Comprehensive test categorization engine following expert committee guidance.

    Implements intelligent categorization using:
    1. Path-based analysis (primary)
    2. Content analysis (secondary)
    3. Framework patterns (tertiary)
    4. Naming conventions (quaternary)
    5. Historical data (if available)

    Following SOLID principles:
    - Single Responsibility: Only categorizes and tags tests
    - Open/Closed: Extensible for new categorization rules
    - Liskov Substitution: Categorization strategies are interchangeable
    - Interface Segregation: Clear categorization interfaces
    - Dependency Inversion: Depends on abstractions
    """

    # Path-based categorization patterns
    CATEGORY_PATTERNS = {
        TestCategory.API: [r"api", r"endpoint", r"rest", r"graphql", r"route"],
        TestCategory.DATABASE: [
            r"database",
            r"db",
            r"model",
            r"repository",
            r"migration",
            r"schema",
        ],
        TestCategory.UI: [
            r"ui",
            r"component",
            r"frontend",
            r"view",
            r"template",
            r"jsx",
            r"tsx",
        ],
        TestCategory.AUTHENTICATION: [
            r"auth",
            r"login",
            r"security",
            r"permission",
            r"token",
            r"oauth",
        ],
        TestCategory.INTEGRATION: [r"integration", r"e2e", r"end.?to.?end", r"system"],
        TestCategory.PERFORMANCE: [
            r"performance",
            r"load",
            r"stress",
            r"benchmark",
            r"speed",
        ],
        TestCategory.CONFIGURATION: [r"config", r"setting", r"environment", r"setup"],
        TestCategory.DEPLOYMENT: [
            r"deploy",
            r"docker",
            r"kubernetes",
            r"k8s",
            r"infrastructure",
        ],
        TestCategory.UTILITY: [r"util", r"helper", r"common", r"shared", r"tool"],
    }

    # Priority determination patterns
    PRIORITY_PATTERNS = {
        TestPriority.CRITICAL: [
            r"critical",
            r"core",
            r"essential",
            r"main",
            r"primary",
        ],
        TestPriority.HIGH: [r"important", r"key", r"major", r"significant"],
        TestPriority.LOW: [r"minor", r"optional", r"nice.?to.?have", r"edge.?case"],
    }

    # Execution tier estimation patterns
    EXECUTION_TIER_PATTERNS = {
        TestExecutionTier.SMOKE: [r"smoke", r"sanity", r"basic", r"quick"],
        TestExecutionTier.SLOW: [
            r"slow",
            r"long",
            r"heavy",
            r"database",
            r"integration",
            r"e2e",
        ],
        TestExecutionTier.MANUAL: [r"manual", r"interactive", r"user"],
    }

    def __init__(
        self,
        project_root: Union[str, Path],
        custom_rules: Optional[Dict[str, Any]] = None,
        tag_config_file: Optional[str] = None,
    ):
        """
        Initialize test categorization engine.

        Args:
            project_root: Root directory of the project
            custom_rules: Custom categorization rules
            tag_config_file: YAML file with tag definitions
        """
        self.project_root = Path(project_root).resolve()
        self.custom_rules = custom_rules or {}
        self.logger = logging.getLogger(__name__)

        # Load tag configuration
        self.tag_definitions = self._load_tag_definitions(tag_config_file)

        # Categorization statistics
        self._categorization_stats = {"tests_categorized": 0, "errors": []}

    def categorize_tests(
        self, discovery_result: TestDiscoveryResult
    ) -> TestCategorizationResult:
        """
        Categorize all discovered tests following expert committee guidance.

        Args:
            discovery_result: Results from test discovery

        Returns:
            TestCategorizationResult: Comprehensive categorization results
        """
        import time

        start_time = time.time()

        self.logger.info(
            f"Starting test categorization for {len(discovery_result.test_files)} test files"
        )

        result = TestCategorizationResult()

        try:
            # Step 1: Categorize each test file
            for test_file in discovery_result.test_files:
                try:
                    categorized_test = self._categorize_test_file(test_file)
                    result.add_categorized_test(categorized_test)
                    self._categorization_stats["tests_categorized"] += 1

                    # Log progress
                    if self._categorization_stats["tests_categorized"] % 25 == 0:
                        self.logger.info(
                            f"Categorized {self._categorization_stats['tests_categorized']} tests"
                        )

                except Exception as e:
                    error_msg = f"Error categorizing {test_file.path}: {e}"
                    self.logger.warning(error_msg)
                    self._categorization_stats["errors"].append(error_msg)
                    result.errors_encountered.append(error_msg)

            # Step 2: Analyze critical path
            result.critical_path_tests = self._identify_critical_path(result)

            # Step 3: Group for parallel execution
            result.parallel_execution_groups = self._group_for_parallel_execution(
                result
            )

            # Step 4: Identify coverage gaps
            result.test_coverage_gaps = self._identify_coverage_gaps(result)

            # Step 5: Generate recommended tags
            result.recommended_tags = self._generate_recommended_tags(result)

            # Step 6: Generate recommendations
            result.recommendations = self._generate_recommendations(result)

            # Step 7: Calculate final metrics
            result.categorization_duration = time.time() - start_time

            self.logger.info(
                f"Test categorization complete: {len(result.categorized_tests)} tests categorized"
            )

        except Exception as e:
            self.logger.error(f"Test categorization failed: {e}")
            result.errors_encountered.append(str(e))

        return result

    def _categorize_test_file(self, test_file: TestFile) -> CategorizedTestFile:
        """Categorize a single test file with comprehensive analysis."""
        categorized = CategorizedTestFile(test_file=test_file)

        # Determine category
        categorized.category = self._determine_category(test_file)

        # Determine priority
        categorized.priority = self._determine_priority(test_file)

        # Determine stability (heuristic-based for now)
        categorized.stability = self._determine_stability(test_file)

        # Determine execution tier
        categorized.execution_tier = self._determine_execution_tier(test_file)

        # Generate tags
        categorized.tags = self._generate_tags(test_file, categorized)

        # Identify functional areas
        categorized.functional_areas = self._identify_functional_areas(test_file)

        # Estimate duration
        categorized.estimated_duration = self._estimate_duration(test_file, categorized)

        # Analyze dependencies
        categorized.requires_docker = self._requires_docker(test_file)
        categorized.requires_database = self._requires_database(test_file)

        # Determine if required for merge
        categorized.required_for_merge = self._is_required_for_merge(categorized)

        # Generate purpose description
        categorized.purpose = self._generate_purpose(test_file, categorized)

        return categorized

    def _determine_category(self, test_file: TestFile) -> TestCategory:
        """Determine the functional category of a test file."""
        path_str = str(test_file.path).lower()

        # Check path patterns
        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, path_str):
                    return category

        # Check content patterns for Python files
        if test_file.language == TestLanguage.PYTHON:
            try:
                content = test_file.path.read_text(
                    encoding="utf-8", errors="ignore"
                ).lower()

                # API patterns
                if any(
                    keyword in content
                    for keyword in ["fastapi", "flask", "django", "request", "response"]
                ):
                    return TestCategory.API

                # Database patterns
                if any(
                    keyword in content
                    for keyword in ["sqlalchemy", "database", "db", "query", "model"]
                ):
                    return TestCategory.DATABASE

                # Authentication patterns
                if any(
                    keyword in content
                    for keyword in ["auth", "login", "token", "permission"]
                ):
                    return TestCategory.AUTHENTICATION

            except Exception:
                pass

        # Default based on test type
        if test_file.test_type == TestType.E2E:
            return TestCategory.INTEGRATION
        elif test_file.test_type == TestType.PERFORMANCE:
            return TestCategory.PERFORMANCE

        return TestCategory.CORE_LOGIC

    def _determine_priority(self, test_file: TestFile) -> TestPriority:
        """Determine the priority level of a test file."""
        path_str = str(test_file.path).lower()

        # Check priority patterns
        for priority, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, path_str):
                    return priority

        # Priority based on test type
        if test_file.test_type == TestType.SMOKE:
            return TestPriority.CRITICAL
        elif test_file.test_type == TestType.E2E:
            return TestPriority.HIGH
        elif test_file.test_type == TestType.UNIT:
            return TestPriority.MEDIUM

        # Priority based on framework
        if test_file.framework in [TestFramework.PYTEST, TestFramework.JEST]:
            return TestPriority.MEDIUM

        return TestPriority.MEDIUM

    def _determine_stability(self, test_file: TestFile) -> TestStability:
        """Determine the stability classification of a test file."""
        # Heuristic-based stability assessment

        # E2E tests are typically less stable
        if test_file.test_type == TestType.E2E:
            return TestStability.FLAKY

        # Unit tests are typically stable
        if test_file.test_type == TestType.UNIT:
            return TestStability.STABLE

        # Performance tests can be unstable
        if test_file.test_type == TestType.PERFORMANCE:
            return TestStability.UNSTABLE

        # New tests (heuristic: small file size, few tests)
        if test_file.test_count <= 2 and test_file.file_size < 1000:
            return TestStability.NEW

        return TestStability.STABLE

    def _determine_execution_tier(self, test_file: TestFile) -> TestExecutionTier:
        """Determine the execution tier based on expected runtime."""
        path_str = str(test_file.path).lower()

        # Check execution tier patterns
        for tier, patterns in self.EXECUTION_TIER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, path_str):
                    return tier

        # Tier based on test type
        if test_file.test_type == TestType.SMOKE:
            return TestExecutionTier.SMOKE
        elif test_file.test_type == TestType.UNIT:
            return TestExecutionTier.FAST
        elif test_file.test_type == TestType.INTEGRATION:
            return TestExecutionTier.MEDIUM
        elif test_file.test_type == TestType.E2E:
            return TestExecutionTier.SLOW
        elif test_file.test_type == TestType.PERFORMANCE:
            return TestExecutionTier.SLOW

        return TestExecutionTier.MEDIUM

    def _generate_tags(
        self, test_file: TestFile, categorized: CategorizedTestFile
    ) -> Set[str]:
        """Generate appropriate tags for a test file."""
        tags = set()

        # Framework tag
        if test_file.framework != TestFramework.UNKNOWN:
            tags.add(test_file.framework.value)

        # Language tag
        if test_file.language != TestLanguage.UNKNOWN:
            tags.add(test_file.language.value)

        # Test type tag
        if test_file.test_type != TestType.UNKNOWN:
            tags.add(test_file.test_type.value)

        # Category tag
        if categorized.category != TestCategory.UNKNOWN:
            tags.add(categorized.category.value)

        # Priority tag
        if categorized.priority != TestPriority.UNKNOWN:
            tags.add(categorized.priority.value)

        # Quality tags
        if test_file.has_assertions:
            tags.add("assertions")
        if test_file.has_mocks:
            tags.add("mocks")
        if test_file.has_fixtures:
            tags.add("fixtures")

        # Path-based tags
        path_parts = test_file.path.parts
        for part in path_parts:
            part_lower = part.lower()
            if part_lower in ["integration", "unit", "e2e", "api", "database", "ui"]:
                tags.add(part_lower)

        return tags

    def _identify_functional_areas(self, test_file: TestFile) -> Set[str]:
        """Identify functional areas covered by the test file."""
        areas = set()
        path_str = str(test_file.path).lower()

        # Common functional areas
        functional_patterns = {
            "agents": r"agent",
            "inference": r"inference|ai|ml",
            "coalition": r"coalition|group",
            "world": r"world|environment|simulation",
            "api": r"api|endpoint|route",
            "database": r"database|db|model",
            "authentication": r"auth|login|security",
            "frontend": r"frontend|ui|component",
            "backend": r"backend|server|service",
            "deployment": r"deploy|docker|k8s",
        }

        for area, pattern in functional_patterns.items():
            if re.search(pattern, path_str):
                areas.add(area)

        # Extract from path components
        for part in test_file.path.parts:
            part_clean = re.sub(r"[^a-zA-Z0-9]", "", part.lower())
            if len(part_clean) > 3 and part_clean not in ["test", "tests", "spec"]:
                areas.add(part_clean)

        return areas

    def _estimate_duration(
        self, test_file: TestFile, categorized: CategorizedTestFile
    ) -> float:
        """Estimate test execution duration in seconds."""
        base_duration = 0.1  # Base duration per test

        # Duration multipliers by execution tier
        tier_multipliers = {
            TestExecutionTier.SMOKE: 0.5,
            TestExecutionTier.FAST: 1.0,
            TestExecutionTier.MEDIUM: 5.0,
            TestExecutionTier.SLOW: 30.0,
            TestExecutionTier.MANUAL: 300.0,
            TestExecutionTier.UNKNOWN: 2.0,
        }

        # Duration multipliers by test type
        type_multipliers = {
            TestType.UNIT: 1.0,
            TestType.INTEGRATION: 10.0,
            TestType.E2E: 60.0,
            TestType.PERFORMANCE: 120.0,
            TestType.SMOKE: 0.5,
            TestType.REGRESSION: 5.0,
            TestType.UNKNOWN: 2.0,
        }

        tier_mult = tier_multipliers.get(categorized.execution_tier, 2.0)
        type_mult = type_multipliers.get(test_file.test_type, 2.0)

        estimated = base_duration * test_file.test_count * tier_mult * type_mult

        # Additional factors
        if categorized.requires_database:
            estimated *= 2.0
        if categorized.requires_docker:
            estimated *= 1.5

        return round(estimated, 2)

    def _requires_docker(self, test_file: TestFile) -> bool:
        """Check if test requires Docker."""
        try:
            content = test_file.path.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()
            return any(
                keyword in content
                for keyword in ["docker", "container", "testcontainer"]
            )
        except Exception:
            return False

    def _requires_database(self, test_file: TestFile) -> bool:
        """Check if test requires database."""
        try:
            content = test_file.path.read_text(
                encoding="utf-8", errors="ignore"
            ).lower()
            return any(
                keyword in content
                for keyword in [
                    "database",
                    "db",
                    "sqlalchemy",
                    "postgresql",
                    "mysql",
                    "sqlite",
                    "model",
                    "query",
                    "transaction",
                    "migration",
                ]
            )
        except Exception:
            return False

    def _is_required_for_merge(self, categorized: CategorizedTestFile) -> bool:
        """Determine if test is required for merge."""
        # Critical and high priority tests are required
        if categorized.priority in [TestPriority.CRITICAL, TestPriority.HIGH]:
            return True

        # Smoke tests are required
        if categorized.test_file.test_type == TestType.SMOKE:
            return True

        # Core logic tests are required
        if categorized.category == TestCategory.CORE_LOGIC:
            return True

        return False

    def _generate_purpose(
        self, test_file: TestFile, categorized: CategorizedTestFile
    ) -> str:
        """Generate a purpose description for the test."""
        purpose_parts = []

        # Test type description
        type_descriptions = {
            TestType.UNIT: "Verifies individual component functionality",
            TestType.INTEGRATION: "Tests component interactions",
            TestType.E2E: "Validates complete user workflows",
            TestType.PERFORMANCE: "Measures system performance",
            TestType.SMOKE: "Provides basic functionality validation",
            TestType.REGRESSION: "Prevents known bugs from reoccurring",
        }

        if test_file.test_type in type_descriptions:
            purpose_parts.append(type_descriptions[test_file.test_type])

        # Category description
        category_descriptions = {
            TestCategory.API: "for API endpoints",
            TestCategory.DATABASE: "for data persistence",
            TestCategory.UI: "for user interface",
            TestCategory.AUTHENTICATION: "for authentication and security",
            TestCategory.CORE_LOGIC: "for business logic",
        }

        if categorized.category in category_descriptions:
            purpose_parts.append(category_descriptions[categorized.category])

        # Functional areas
        if categorized.functional_areas:
            areas = ", ".join(sorted(categorized.functional_areas)[:3])
            purpose_parts.append(f"in {areas}")

        return " ".join(purpose_parts) or "Test file purpose not determined"

    def _identify_critical_path(self, result: TestCategorizationResult) -> List[str]:
        """Identify tests on the critical path for releases."""
        critical_tests = []

        for categorized in result.categorized_tests:
            if (
                categorized.priority == TestPriority.CRITICAL
                or categorized.test_file.test_type == TestType.SMOKE
                or categorized.required_for_merge
            ):
                critical_tests.append(str(categorized.test_file.path))

        return critical_tests

    def _group_for_parallel_execution(
        self, result: TestCategorizationResult
    ) -> Dict[str, List[str]]:
        """Group tests for optimal parallel execution."""
        groups = defaultdict(list)

        for categorized in result.categorized_tests:
            # Group by execution tier and requirements
            group_key = f"{categorized.execution_tier.value}"

            if categorized.requires_database:
                group_key += "_db"
            if categorized.requires_docker:
                group_key += "_docker"
            if not categorized.runs_in_parallel:
                group_key = f"sequential_{group_key}"

            groups[group_key].append(str(categorized.test_file.path))

        return dict(groups)

    def _identify_coverage_gaps(self, result: TestCategorizationResult) -> List[str]:
        """Identify potential test coverage gaps."""
        gaps = []

        # Check category coverage
        category_counts = result.by_category
        if category_counts.get("api", 0) == 0:
            gaps.append("No API tests found - consider adding endpoint tests")
        if category_counts.get("integration", 0) == 0:
            gaps.append(
                "No integration tests found - consider adding component interaction tests"
            )
        if category_counts.get("security", 0) == 0:
            gaps.append(
                "No security tests found - consider adding authentication/authorization tests"
            )

        # Check priority distribution
        priority_counts = result.by_priority
        total_tests = sum(priority_counts.values())
        if total_tests > 0:
            critical_ratio = priority_counts.get("critical", 0) / total_tests
            if critical_ratio < 0.1:
                gaps.append(
                    "Low critical test coverage - consider marking more tests as critical"
                )

        # Check execution tier balance
        tier_counts = result.by_execution_tier
        if tier_counts.get("fast", 0) < tier_counts.get("slow", 0):
            gaps.append(
                "More slow tests than fast tests - consider optimizing test performance"
            )

        return gaps

    def _generate_recommended_tags(
        self, result: TestCategorizationResult
    ) -> List[TestTag]:
        """Generate recommended tags based on analysis."""
        recommended = []

        # Standard recommended tags
        standard_tags = [
            TestTag("smoke", "execution", "Quick sanity check tests", "#28a745"),
            TestTag(
                "critical", "priority", "Critical path tests for releases", "#dc3545"
            ),
            TestTag(
                "fast", "performance", "Tests that run in under 1 second", "#17a2b8"
            ),
            TestTag(
                "slow", "performance", "Tests that take more than 10 seconds", "#ffc107"
            ),
            TestTag("flaky", "stability", "Tests that occasionally fail", "#fd7e14"),
            TestTag(
                "requires-db", "infrastructure", "Tests requiring database", "#6f42c1"
            ),
            TestTag(
                "requires-docker", "infrastructure", "Tests requiring Docker", "#20c997"
            ),
            TestTag(
                "parallel-safe", "execution", "Safe for parallel execution", "#28a745"
            ),
            TestTag("sequential-only", "execution", "Must run sequentially", "#dc3545"),
        ]

        recommended.extend(standard_tags)

        # Dynamic tags based on functional areas
        for area in result.functional_area_coverage.keys():
            if result.functional_area_coverage[area] >= 3:  # At least 3 tests
                recommended.append(
                    TestTag(
                        area, "functional", f"Tests for {area} functionality", "#6c757d"
                    )
                )

        return recommended

    def _generate_recommendations(self, result: TestCategorizationResult) -> List[str]:
        """Generate actionable recommendations based on categorization."""
        recommendations = []

        # Test distribution recommendations
        total_tests = result.total_tests
        if total_tests == 0:
            return ["❌ No tests categorized - ensure test discovery is working"]

        # Priority distribution
        critical_count = result.by_priority.get("critical", 0)
        if critical_count == 0:
            recommendations.append(
                "⚠️ No critical tests identified - mark essential tests as critical"
            )
        elif critical_count / total_tests > 0.5:
            recommendations.append(
                "📊 High ratio of critical tests - consider if all are truly critical"
            )

        # Execution tier recommendations
        slow_count = result.by_execution_tier.get("slow", 0)
        fast_count = result.by_execution_tier.get("fast", 0)

        if slow_count > fast_count:
            recommendations.append(
                "🐌 More slow tests than fast tests - optimize for CI/CD performance"
            )

        if result.estimated_total_duration > 300:  # 5 minutes
            recommendations.append(
                f"⏱️ Total execution time: {result.estimated_total_duration:.1f}s - consider parallel execution"
            )

        # Coverage recommendations
        category_counts = result.by_category
        if len(category_counts) < 3:
            recommendations.append(
                "📋 Limited test category diversity - expand test coverage areas"
            )

        # Tagging recommendations
        if len(result.tag_usage) < 5:
            recommendations.append(
                "🏷️ Limited tag usage - improve test organization with more tags"
            )

        # Stability recommendations
        flaky_count = result.by_stability.get("flaky", 0)
        unstable_count = result.by_stability.get("unstable", 0)

        if (flaky_count + unstable_count) / total_tests > 0.2:
            recommendations.append(
                "🔧 High ratio of unstable tests - investigate and fix flaky tests"
            )

        return recommendations

    def _load_tag_definitions(self, config_file: Optional[str]) -> Dict[str, TestTag]:
        """Load tag definitions from configuration file."""
        if not config_file or not Path(config_file).exists():
            return {}

        try:
            with open(config_file, "r") as f:
                config = yaml.safe_load(f)

            tags = {}
            for tag_data in config.get("tags", []):
                tag = TestTag(**tag_data)
                tags[tag.name] = tag

            return tags

        except Exception as e:
            self.logger.warning(f"Error loading tag definitions: {e}")
            return {}

    def export_categorization_config(
        self, result: TestCategorizationResult, output_file: str
    ) -> None:
        """Export categorization results as configuration for CI/CD."""
        config = {
            "test_categories": {
                "critical_path": result.critical_path_tests,
                "parallel_groups": result.parallel_execution_groups,
                "estimated_duration": result.estimated_total_duration,
            },
            "tags": [tag.to_dict() for tag in result.recommended_tags],
            "statistics": {
                "total_tests": result.total_tests,
                "by_priority": result.by_priority,
                "by_category": result.by_category,
                "by_execution_tier": result.by_execution_tier,
            },
        }

        with open(output_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def create_test_categorizer(project_root: str, **kwargs: Any) -> TestCategorizer:
    """
    Factory function to create a TestCategorizer instance.

    Args:
        project_root: Root directory of the project
        **kwargs: Additional configuration options

    Returns:
        TestCategorizer: Configured test categorization instance
    """
    return TestCategorizer(project_root, **kwargs)


def main():
    """Main function for command-line usage."""
    import argparse
    from test_discovery import create_test_discovery

    parser = argparse.ArgumentParser(description="Categorize and tag tests")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--config", "-c", help="YAML configuration file")
    parser.add_argument("--export-config", help="Export CI/CD configuration")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Discover tests first
    discovery = create_test_discovery(args.project_root)
    discovery_result = discovery.discover_tests()

    print(f"Discovered {len(discovery_result.test_files)} test files")

    # Categorize tests
    categorizer = create_test_categorizer(
        args.project_root, tag_config_file=args.config
    )
    result = categorizer.categorize_tests(discovery_result)

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"Results saved to {args.output}")

    # Export CI/CD configuration
    if args.export_config:
        categorizer.export_categorization_config(result, args.export_config)
        print(f"CI/CD configuration exported to {args.export_config}")

    # Summary
    print("\n📊 Test Categorization Summary:")
    print(f"  🧪 Tests categorized: {result.total_tests}")
    print(f"  ⏱️ Estimated duration: {result.estimated_total_duration:.1f}s")
    print(f"  🏷️ Tags used: {len(result.tag_usage)}")
    print(f"  📋 Categories: {len(result.by_category)}")
    print(f"  🎯 Critical path tests: {len(result.critical_path_tests)}")

    if result.by_priority:
        print(f"  📊 By priority: {dict(result.by_priority)}")

    if result.by_category:
        print(f"  📂 By category: {dict(result.by_category)}")

    if result.parallel_execution_groups:
        print(f"  ⚡ Parallel groups: {len(result.parallel_execution_groups)}")

    if result.recommendations:
        print("\n💡 Recommendations:")
        for rec in result.recommendations:
            print(f"  {rec}")


if __name__ == "__main__":
    main()
