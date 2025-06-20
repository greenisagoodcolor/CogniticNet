#!/usr/bin/env python3
"""
Test Discovery Module for FreeAgentics Repository

This module implements comprehensive test discovery following expert committee
guidance from Kent Beck (TDD) and Gary Bernhardt (Testing Strategies).

Expert Committee Guidance:
- Kent Beck: "Tests should be easy to find and understand their purpose"
- Gary Bernhardt: "Test boundaries matter - unit vs integration vs E2E"
- Michael Feathers: "Tests are the safety net for refactoring"

Following Clean Code and SOLID principles with robust error handling.
"""

import logging
import re
import ast
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Tuple
from collections import defaultdict, Counter
import json
import sys
import subprocess


class TestType(Enum):
    """Test categorization following Gary Bernhardt's testing pyramid."""
    UNIT = "unit"                    # Fast, isolated tests
    INTEGRATION = "integration"      # Component interaction tests
    E2E = "e2e"                     # End-to-end system tests
    PERFORMANCE = "performance"      # Load/stress tests
    SMOKE = "smoke"                 # Basic functionality tests
    REGRESSION = "regression"        # Bug prevention tests
    UNKNOWN = "unknown"             # Cannot determine type


class TestFramework(Enum):
    """Supported test frameworks across languages."""
    PYTEST = "pytest"               # Python testing
    UNITTEST = "unittest"           # Python built-in
    JEST = "jest"                   # JavaScript/TypeScript
    MOCHA = "mocha"                 # JavaScript alternative
    CYPRESS = "cypress"             # E2E testing
    PLAYWRIGHT = "playwright"       # Modern E2E testing
    VITEST = "vitest"              # Vite-based testing
    UNKNOWN = "unknown"             # Cannot determine framework


class TestLanguage(Enum):
    """Programming languages with test support."""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    SHELL = "shell"
    UNKNOWN = "unknown"


@dataclass
class TestFile:
    """
    Represents a discovered test file with comprehensive metadata.

    Following Kent Beck's principle that tests should be self-documenting
    and provide clear understanding of their purpose and scope.
    """
    path: Path
    test_type: TestType
    framework: TestFramework
    language: TestLanguage

    # Test content analysis
    test_count: int = 0
    test_functions: List[str] = field(default_factory=list)
    test_classes: List[str] = field(default_factory=list)

    # Metadata
    file_size: int = 0
    line_count: int = 0
    last_modified: Optional[float] = None

    # Framework-specific data
    config_files: List[Path] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

    # Quality metrics
    has_assertions: bool = False
    has_mocks: bool = False
    has_fixtures: bool = False

    # Detection metadata
    detection_confidence: float = 0.8
    detection_method: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": str(self.path),
            "test_type": self.test_type.value,
            "framework": self.framework.value,
            "language": self.language.value,
            "test_count": self.test_count,
            "test_functions": self.test_functions,
            "test_classes": self.test_classes,
            "file_size": self.file_size,
            "line_count": self.line_count,
            "last_modified": self.last_modified,
            "config_files": [str(p) for p in self.config_files],
            "dependencies": self.dependencies,
            "has_assertions": self.has_assertions,
            "has_mocks": self.has_mocks,
            "has_fixtures": self.has_fixtures,
            "detection_confidence": self.detection_confidence,
            "detection_method": self.detection_method
        }


@dataclass
class TestDiscoveryResult:
    """
    Complete test discovery results with comprehensive analysis.

    Provides actionable insights for test baseline establishment
    following expert committee guidance.
    """
    test_files: List[TestFile] = field(default_factory=list)
    total_tests: int = 0

    # Categorization statistics
    by_type: Dict[str, int] = field(default_factory=dict)
    by_framework: Dict[str, int] = field(default_factory=dict)
    by_language: Dict[str, int] = field(default_factory=dict)

    # Quality metrics
    coverage_estimate: float = 0.0
    test_to_code_ratio: float = 0.0

    # Framework configurations found
    config_files: Dict[str, List[Path]] = field(default_factory=dict)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)

    # Discovery metadata
    discovery_duration: float = 0.0
    files_scanned: int = 0
    errors_encountered: List[str] = field(default_factory=list)

    def add_test_file(self, test_file: TestFile) -> None:
        """Add a test file and update statistics."""
        self.test_files.append(test_file)
        self.total_tests += test_file.test_count

        # Update categorization
        self.by_type[test_file.test_type.value] = self.by_type.get(test_file.test_type.value, 0) + 1
        self.by_framework[test_file.framework.value] = self.by_framework.get(test_file.framework.value, 0) + 1
        self.by_language[test_file.language.value] = self.by_language.get(test_file.language.value, 0) + 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "test_files": [tf.to_dict() for tf in self.test_files],
            "total_tests": self.total_tests,
            "by_type": self.by_type,
            "by_framework": self.by_framework,
            "by_language": self.by_language,
            "coverage_estimate": self.coverage_estimate,
            "test_to_code_ratio": self.test_to_code_ratio,
            "config_files": {
                framework: [str(p) for p in paths]
                for framework, paths in self.config_files.items()
            },
            "recommendations": self.recommendations,
            "discovery_duration": self.discovery_duration,
            "files_scanned": self.files_scanned,
            "errors_encountered": self.errors_encountered
        }


class TestDiscovery:
    """
    Comprehensive test discovery engine following expert committee guidance.

    Implements multi-strategy detection:
    1. Filename pattern matching (primary)
    2. Content analysis (secondary)
    3. Framework configuration detection (tertiary)
    4. Directory structure analysis (quaternary)

    Following SOLID principles:
    - Single Responsibility: Only discovers tests
    - Open/Closed: Extensible for new frameworks
    - Liskov Substitution: Framework detectors are interchangeable
    - Interface Segregation: Clear detection interfaces
    - Dependency Inversion: Depends on abstractions
    """

    # Test file patterns by language and framework
    TEST_PATTERNS = {
        TestLanguage.PYTHON: {
            'filename_patterns': [
                r'^test_.*\.py$',           # test_module.py
                r'^.*_test\.py$',           # module_test.py
                r'^test.*\.py$',            # testmodule.py
                r'^.*tests\.py$',           # moduletests.py
            ],
            'directory_patterns': [
                r'tests?',                  # tests/ or test/
                r'.*tests?',               # anything ending in test(s)
                r'spec',                   # spec/
            ],
            'content_patterns': [
                r'import\s+pytest',
                r'import\s+unittest',
                r'from\s+unittest',
                r'def\s+test_',
                r'class\s+Test\w+',
                r'@pytest\.',
                r'assert\s+',
            ]
        },
        TestLanguage.JAVASCRIPT: {
            'filename_patterns': [
                r'^.*\.test\.js$',          # module.test.js
                r'^.*\.spec\.js$',          # module.spec.js
                r'^test.*\.js$',            # testModule.js
            ],
            'directory_patterns': [
                r'__tests__',              # __tests__/
                r'tests?',                 # tests/ or test/
                r'spec',                   # spec/
                r'e2e',                    # e2e/
            ],
            'content_patterns': [
                r'describe\s*\(',
                r'it\s*\(',
                r'test\s*\(',
                r'expect\s*\(',
                r'jest\.',
                r'mocha',
                r'chai',
            ]
        },
        TestLanguage.TYPESCRIPT: {
            'filename_patterns': [
                r'^.*\.test\.ts$',          # module.test.ts
                r'^.*\.spec\.ts$',          # module.spec.ts
                r'^test.*\.ts$',            # testModule.ts
            ],
            'directory_patterns': [
                r'__tests__',
                r'tests?',
                r'spec',
                r'e2e',
            ],
            'content_patterns': [
                r'describe\s*\(',
                r'it\s*\(',
                r'test\s*\(',
                r'expect\s*\(',
                r'jest\.',
                r'vitest',
            ]
        }
    }

    # Framework configuration files
    FRAMEWORK_CONFIGS = {
        TestFramework.PYTEST: [
            'pytest.ini', 'pyproject.toml', 'setup.cfg', 'tox.ini'
        ],
        TestFramework.JEST: [
            'jest.config.js', 'jest.config.json', 'package.json'
        ],
        TestFramework.CYPRESS: [
            'cypress.config.js', 'cypress.json'
        ],
        TestFramework.PLAYWRIGHT: [
            'playwright.config.js', 'playwright.config.ts'
        ]
    }

    def __init__(
        self,
        project_root: Union[str, Path],
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None,
        max_file_size: int = 10 * 1024 * 1024  # 10MB
    ):
        """
        Initialize test discovery engine.

        Args:
            project_root: Root directory to search for tests
            include_patterns: Additional patterns to include
            exclude_patterns: Patterns to exclude from search
            max_file_size: Maximum file size to analyze (bytes)
        """
        self.project_root = Path(project_root).resolve()
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or [
            r'node_modules',
            r'\.git',
            r'__pycache__',
            r'\.pytest_cache',
            r'coverage',
            r'\.coverage',
            r'dist',
            r'build',
            r'\.venv',
            r'venv',
        ]
        self.max_file_size = max_file_size
        self.logger = logging.getLogger(__name__)

        # Detection statistics
        self._detection_stats = {
            'files_scanned': 0,
            'tests_found': 0,
            'errors': []
        }

    def discover_tests(self) -> TestDiscoveryResult:
        """
        Discover all tests in the project following expert committee guidance.

        Returns:
            TestDiscoveryResult: Comprehensive test discovery results
        """
        import time
        start_time = time.time()

        self.logger.info(f"Starting test discovery in {self.project_root}")

        result = TestDiscoveryResult()

        try:
            # Step 1: Find potential test files
            potential_files = self._find_potential_test_files()
            self.logger.info(f"Found {len(potential_files)} potential test files")

            # Step 2: Analyze each file
            for file_path in potential_files:
                try:
                    test_file = self._analyze_test_file(file_path)
                    if test_file:
                        result.add_test_file(test_file)
                        self._detection_stats['tests_found'] += 1

                    self._detection_stats['files_scanned'] += 1

                    # Log progress
                    if self._detection_stats['files_scanned'] % 50 == 0:
                        self.logger.info(f"Analyzed {self._detection_stats['files_scanned']} files")

                except Exception as e:
                    error_msg = f"Error analyzing {file_path}: {e}"
                    self.logger.warning(error_msg)
                    self._detection_stats['errors'].append(error_msg)
                    result.errors_encountered.append(error_msg)

            # Step 3: Find framework configurations
            result.config_files = self._find_framework_configs()

            # Step 4: Generate recommendations
            result.recommendations = self._generate_recommendations(result)

            # Step 5: Calculate metrics
            result.files_scanned = self._detection_stats['files_scanned']
            result.discovery_duration = time.time() - start_time

            self.logger.info(f"Test discovery complete: {len(result.test_files)} test files found")

        except Exception as e:
            self.logger.error(f"Test discovery failed: {e}")
            result.errors_encountered.append(str(e))

        return result

    def _find_potential_test_files(self) -> List[Path]:
        """Find files that might be tests using multiple strategies."""
        potential_files = set()

        # Strategy 1: Filename pattern matching
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file():
                continue

            if self._should_exclude_file(file_path):
                continue

            if self._matches_test_pattern(file_path):
                potential_files.add(file_path)

        # Strategy 2: Directory-based discovery
        test_directories = self._find_test_directories()
        for test_dir in test_directories:
            for file_path in test_dir.rglob('*'):
                if file_path.is_file() and not self._should_exclude_file(file_path):
                    potential_files.add(file_path)

        return sorted(potential_files)

    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from analysis."""
        relative_path = str(file_path.relative_to(self.project_root))

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if re.search(pattern, relative_path, re.IGNORECASE):
                return True

        # Check file size
        try:
            if file_path.stat().st_size > self.max_file_size:
                return True
        except OSError:
            return True

        return False

    def _matches_test_pattern(self, file_path: Path) -> bool:
        """Check if filename matches test patterns."""
        filename = file_path.name

        # Check each language's patterns
        for language, patterns in self.TEST_PATTERNS.items():
            for pattern in patterns['filename_patterns']:
                if re.match(pattern, filename, re.IGNORECASE):
                    return True

        return False

    def _find_test_directories(self) -> List[Path]:
        """Find directories likely to contain tests."""
        test_dirs = []

        for directory in self.project_root.rglob('*'):
            if not directory.is_dir():
                continue

            if self._should_exclude_file(directory):
                continue

            dir_name = directory.name.lower()

            # Check directory patterns
            for language, patterns in self.TEST_PATTERNS.items():
                for pattern in patterns['directory_patterns']:
                    if re.match(pattern, dir_name):
                        test_dirs.append(directory)
                        break

        return test_dirs

    def _analyze_test_file(self, file_path: Path) -> Optional[TestFile]:
        """Analyze a file to determine if it's a test and extract metadata."""
        try:
            # Basic file info
            stat = file_path.stat()
            file_size = stat.st_size
            last_modified = stat.st_mtime

            # Read content
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except UnicodeDecodeError:
                # Binary file, skip
                return None

            line_count = len(content.splitlines())

            # Determine language
            language = self._detect_language(file_path)
            if language == TestLanguage.UNKNOWN:
                return None

            # Determine framework
            framework = self._detect_framework(content, language)

            # Determine test type
            test_type = self._detect_test_type(file_path, content)

            # Extract test functions and classes
            test_functions, test_classes = self._extract_test_elements(content, language)

            # Quality analysis
            has_assertions = self._has_assertions(content, language)
            has_mocks = self._has_mocks(content, language)
            has_fixtures = self._has_fixtures(content, language)

            # Create test file object
            test_file = TestFile(
                path=file_path,
                test_type=test_type,
                framework=framework,
                language=language,
                test_count=len(test_functions) + len(test_classes),
                test_functions=test_functions,
                test_classes=test_classes,
                file_size=file_size,
                line_count=line_count,
                last_modified=last_modified,
                has_assertions=has_assertions,
                has_mocks=has_mocks,
                has_fixtures=has_fixtures,
                detection_confidence=self._calculate_confidence(file_path, content, language),
                detection_method="content_analysis"
            )

            return test_file

        except Exception as e:
            self.logger.warning(f"Error analyzing test file {file_path}: {e}")
            return None

    def _detect_language(self, file_path: Path) -> TestLanguage:
        """Detect programming language from file extension."""
        suffix = file_path.suffix.lower()

        if suffix == '.py':
            return TestLanguage.PYTHON
        elif suffix == '.js':
            return TestLanguage.JAVASCRIPT
        elif suffix == '.ts':
            return TestLanguage.TYPESCRIPT
        elif suffix in ['.sh', '.bash']:
            return TestLanguage.SHELL

        return TestLanguage.UNKNOWN

    def _detect_framework(self, content: str, language: TestLanguage) -> TestFramework:
        """Detect test framework from content analysis."""
        content_lower = content.lower()

        if language == TestLanguage.PYTHON:
            if 'pytest' in content_lower or '@pytest.' in content_lower:
                return TestFramework.PYTEST
            elif 'unittest' in content_lower or 'from unittest' in content_lower:
                return TestFramework.UNITTEST

        elif language in [TestLanguage.JAVASCRIPT, TestLanguage.TYPESCRIPT]:
            if 'jest' in content_lower:
                return TestFramework.JEST
            elif 'mocha' in content_lower:
                return TestFramework.MOCHA
            elif 'cypress' in content_lower:
                return TestFramework.CYPRESS
            elif 'playwright' in content_lower:
                return TestFramework.PLAYWRIGHT
            elif 'vitest' in content_lower:
                return TestFramework.VITEST

        return TestFramework.UNKNOWN

    def _detect_test_type(self, file_path: Path, content: str) -> TestType:
        """Detect test type based on path and content analysis."""
        path_str = str(file_path).lower()
        content_lower = content.lower()

        # E2E tests
        if any(keyword in path_str for keyword in ['e2e', 'integration', 'cypress', 'playwright']):
            return TestType.E2E

        # Integration tests
        if any(keyword in path_str for keyword in ['integration', 'api', 'database']):
            return TestType.INTEGRATION

        # Performance tests
        if any(keyword in path_str for keyword in ['performance', 'load', 'stress', 'benchmark']):
            return TestType.PERFORMANCE

        # Smoke tests
        if any(keyword in path_str for keyword in ['smoke', 'sanity']):
            return TestType.SMOKE

        # Default to unit tests
        return TestType.UNIT

    def _extract_test_elements(self, content: str, language: TestLanguage) -> Tuple[List[str], List[str]]:
        """Extract test function and class names."""
        functions = []
        classes = []

        if language == TestLanguage.PYTHON:
            functions, classes = self._extract_python_tests(content)
        elif language in [TestLanguage.JAVASCRIPT, TestLanguage.TYPESCRIPT]:
            functions = self._extract_js_tests(content)

        return functions, classes

    def _extract_python_tests(self, content: str) -> Tuple[List[str], List[str]]:
        """Extract Python test functions and classes using AST."""
        functions = []
        classes = []

        try:
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if node.name.startswith('test_') or node.name.endswith('_test'):
                        functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if node.name.startswith('Test') or node.name.endswith('Test'):
                        classes.append(node.name)

        except SyntaxError:
            # Fallback to regex
            func_pattern = r'def\s+(test_\w+|\w+_test)\s*\('
            class_pattern = r'class\s+(Test\w+|\w+Test)\s*[\(:]'

            functions = re.findall(func_pattern, content)
            classes = re.findall(class_pattern, content)

        return functions, classes

    def _extract_js_tests(self, content: str) -> List[str]:
        """Extract JavaScript/TypeScript test functions."""
        patterns = [
            r'describe\s*\(\s*["\']([^"\']+)["\']',
            r'it\s*\(\s*["\']([^"\']+)["\']',
            r'test\s*\(\s*["\']([^"\']+)["\']',
        ]

        functions = []
        for pattern in patterns:
            matches = re.findall(pattern, content)
            functions.extend(matches)

        return functions

    def _has_assertions(self, content: str, language: TestLanguage) -> bool:
        """Check if content has assertion statements."""
        if language == TestLanguage.PYTHON:
            return bool(re.search(r'\bassert\s+', content))
        elif language in [TestLanguage.JAVASCRIPT, TestLanguage.TYPESCRIPT]:
            return bool(re.search(r'\bexpect\s*\(', content))

        return False

    def _has_mocks(self, content: str, language: TestLanguage) -> bool:
        """Check if content uses mocking."""
        mock_patterns = {
            TestLanguage.PYTHON: [r'\bmock\b', r'@patch', r'MagicMock', r'Mock\('],
            TestLanguage.JAVASCRIPT: [r'jest\.mock', r'sinon', r'\.mockImplementation'],
            TestLanguage.TYPESCRIPT: [r'jest\.mock', r'sinon', r'\.mockImplementation']
        }

        patterns = mock_patterns.get(language, [])
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns)

    def _has_fixtures(self, content: str, language: TestLanguage) -> bool:
        """Check if content uses test fixtures."""
        fixture_patterns = {
            TestLanguage.PYTHON: [r'@pytest\.fixture', r'setUp\s*\(', r'tearDown\s*\('],
            TestLanguage.JAVASCRIPT: [r'beforeEach\s*\(', r'afterEach\s*\(', r'beforeAll\s*\('],
            TestLanguage.TYPESCRIPT: [r'beforeEach\s*\(', r'afterEach\s*\(', r'beforeAll\s*\(']
        }

        patterns = fixture_patterns.get(language, [])
        return any(re.search(pattern, content) for pattern in patterns)

    def _calculate_confidence(self, file_path: Path, content: str, language: TestLanguage) -> float:
        """Calculate confidence score for test detection."""
        confidence = 0.0

        # Filename pattern match
        if self._matches_test_pattern(file_path):
            confidence += 0.4

        # Content patterns
        if language in self.TEST_PATTERNS:
            patterns = self.TEST_PATTERNS[language]['content_patterns']
            matches = sum(1 for pattern in patterns if re.search(pattern, content, re.IGNORECASE))
            confidence += min(0.5, matches * 0.1)

        # Directory location
        path_str = str(file_path).lower()
        if any(test_dir in path_str for test_dir in ['test', 'spec', '__tests__']):
            confidence += 0.1

        return min(1.0, confidence)

    def _find_framework_configs(self) -> Dict[str, List[Path]]:
        """Find framework configuration files."""
        configs = defaultdict(list)

        for framework, config_files in self.FRAMEWORK_CONFIGS.items():
            for config_name in config_files:
                for config_path in self.project_root.rglob(config_name):
                    if config_path.is_file():
                        configs[framework.value].append(config_path)

        return dict(configs)

    def _generate_recommendations(self, result: TestDiscoveryResult) -> List[str]:
        """Generate actionable recommendations based on discovery results."""
        recommendations = []

        # Test coverage recommendations
        if result.total_tests == 0:
            recommendations.append("❌ No tests found! Implement basic test suite for critical functionality")
        elif result.total_tests < 10:
            recommendations.append("⚠️ Very few tests found. Consider expanding test coverage")

        # Framework recommendations
        if len(result.by_framework) > 2:
            recommendations.append("🔧 Multiple test frameworks detected. Consider standardizing on one framework")

        # Test type balance
        unit_tests = result.by_type.get('unit', 0)
        integration_tests = result.by_type.get('integration', 0)
        e2e_tests = result.by_type.get('e2e', 0)

        if unit_tests == 0:
            recommendations.append("🧪 No unit tests found. Add fast, isolated unit tests for core logic")

        if integration_tests == 0 and result.total_tests > 5:
            recommendations.append("🔗 Consider adding integration tests for component interactions")

        if e2e_tests == 0 and result.total_tests > 10:
            recommendations.append("🎯 Consider adding end-to-end tests for critical user workflows")

        # Configuration recommendations
        if not result.config_files:
            recommendations.append("⚙️ No test configuration files found. Add framework config for better test management")

        return recommendations


def create_test_discovery(
    project_root: str,
    **kwargs: Any
) -> TestDiscovery:
    """
    Factory function to create a TestDiscovery instance.

    Args:
        project_root: Root directory to search for tests
        **kwargs: Additional configuration options

    Returns:
        TestDiscovery: Configured test discovery instance
    """
    return TestDiscovery(project_root, **kwargs)


def main():
    """Main function for command-line usage."""
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Discover tests in a project")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--output", "-o", help="Output JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Discover tests
    discovery = create_test_discovery(args.project_root)
    result = discovery.discover_tests()

    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result.to_dict(), indent=2))

    # Summary
    print(f"\n📊 Test Discovery Summary:")
    print(f"  📁 Files scanned: {result.files_scanned}")
    print(f"  🧪 Test files found: {len(result.test_files)}")
    print(f"  📝 Total tests: {result.total_tests}")
    print(f"  ⏱️ Discovery time: {result.discovery_duration:.2f}s")

    if result.by_type:
        print(f"  📋 By type: {dict(result.by_type)}")

    if result.by_framework:
        print(f"  🔧 By framework: {dict(result.by_framework)}")

    if result.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in result.recommendations:
            print(f"  {rec}")


if __name__ == "__main__":
    main()
