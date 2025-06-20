#!/usr/bin/env python3
"""
Critical Entry Points Detection Module

This module identifies critical entry points in the codebase following expert committee
guidance from Martin Fowler in the PRD. Entry points are the roots of dependency trees
and require special protection during reorganization.

Key principles:
- Comprehensive Detection: Multiple heuristics for finding entry points
- Risk Assessment: Classify entry points by criticality and risk
- Dependency Analysis: Integration with dependency graph analysis
- Framework Awareness: Understand common patterns across frameworks
"""

import ast
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from enum import Enum

try:
    from .traversal import FileInfo, FileType
    from .metadata_extractor import ExtendedMetadata
    from .dependency_analyzer import DependencyGraph, DependencyAnalyzer
except ImportError:
    from traversal import FileInfo, FileType
    from metadata_extractor import ExtendedMetadata
    from dependency_analyzer import DependencyGraph, DependencyAnalyzer


class EntryPointType(Enum):
    """Types of entry points that can be detected"""
    MAIN_APPLICATION = "main_application"      # Primary application entry
    CLI_SCRIPT = "cli_script"                 # Command-line interface
    WEB_SERVER = "web_server"                 # Web application server
    API_ENDPOINT = "api_endpoint"             # API route handler
    TEST_RUNNER = "test_runner"               # Test execution entry
    BUILD_SCRIPT = "build_script"             # Build/deployment script
    CONFIGURATION = "configuration"           # Configuration file
    DATABASE_MIGRATION = "database_migration" # Database schema changes
    PACKAGE_INIT = "package_init"            # Python package initialization
    MODULE_ENTRY = "module_entry"            # Module-level entry point
    FRAMEWORK_HOOK = "framework_hook"        # Framework-specific hooks
    UNKNOWN = "unknown"                      # Unclassified entry point


class CriticalityLevel(Enum):
    """Criticality levels for entry points"""
    CRITICAL = "critical"      # Breaking this stops the entire system
    HIGH = "high"             # Breaking this stops major functionality
    MEDIUM = "medium"         # Breaking this affects some features
    LOW = "low"              # Breaking this has minimal impact
    INFORMATIONAL = "info"    # Nice to know but not critical


@dataclass
class EntryPoint:
    """
    Represents a critical entry point in the codebase.

    Following Clean Code principles - comprehensive data structure
    with all necessary information for analysis and protection.
    """
    file_path: Path
    entry_type: EntryPointType
    criticality: CriticalityLevel
    description: str
    confidence: float = 1.0

    # Framework and context information
    framework: Optional[str] = None
    language: Optional[str] = None

    # Dependency information
    incoming_dependencies: Set[str] = field(default_factory=set)
    outgoing_dependencies: Set[str] = field(default_factory=set)

    # Detection metadata
    detection_method: str = ""
    line_numbers: List[int] = field(default_factory=list)
    code_patterns: List[str] = field(default_factory=list)

    # Risk assessment
    risk_factors: List[str] = field(default_factory=list)
    protection_recommendations: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate entry point after initialization"""
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Confidence must be between 0.0 and 1.0")

        # Auto-generate protection recommendations based on type
        self._generate_protection_recommendations()

    def _generate_protection_recommendations(self) -> None:
        """Generate protection recommendations based on entry point type"""
        base_recommendations = [
            "Create comprehensive tests before moving",
            "Update all import paths referencing this file",
            "Verify functionality after relocation"
        ]

        type_specific = {
            EntryPointType.MAIN_APPLICATION: [
                "Test complete application startup",
                "Verify command-line arguments parsing",
                "Check environment variable handling"
            ],
            EntryPointType.WEB_SERVER: [
                "Test all HTTP endpoints",
                "Verify middleware chain",
                "Check static file serving"
            ],
            EntryPointType.API_ENDPOINT: [
                "Test all API routes",
                "Verify authentication/authorization",
                "Check request/response schemas"
            ],
            EntryPointType.DATABASE_MIGRATION: [
                "Test migration rollback",
                "Verify data integrity",
                "Check schema consistency"
            ],
            EntryPointType.CONFIGURATION: [
                "Validate all configuration values",
                "Test environment-specific configs",
                "Verify secret/credential handling"
            ]
        }

        self.protection_recommendations.extend(base_recommendations)
        if self.entry_type in type_specific:
            self.protection_recommendations.extend(type_specific[self.entry_type])

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "file_path": str(self.file_path),
            "entry_type": self.entry_type.value,
            "criticality": self.criticality.value,
            "description": self.description,
            "confidence": self.confidence,
            "framework": self.framework,
            "language": self.language,
            "incoming_dependencies": list(self.incoming_dependencies),
            "outgoing_dependencies": list(self.outgoing_dependencies),
            "detection_method": self.detection_method,
            "line_numbers": self.line_numbers,
            "code_patterns": self.code_patterns,
            "risk_factors": self.risk_factors,
            "protection_recommendations": self.protection_recommendations
        }


@dataclass
class EntryPointAnalysis:
    """
    Complete entry point analysis results.

    Provides comprehensive view of all entry points with
    risk assessment and protection strategies.
    """
    entry_points: List[EntryPoint] = field(default_factory=list)
    criticality_summary: Dict[str, int] = field(default_factory=dict)
    framework_summary: Dict[str, int] = field(default_factory=dict)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)

    def add_entry_point(self, entry_point: EntryPoint) -> None:
        """Add an entry point to the analysis"""
        self.entry_points.append(entry_point)
        self._update_summaries(entry_point)

    def _update_summaries(self, entry_point: EntryPoint) -> None:
        """Update summary statistics"""
        # Update criticality summary
        crit_key = entry_point.criticality.value
        self.criticality_summary[crit_key] = self.criticality_summary.get(crit_key, 0) + 1

        # Update framework summary
        if entry_point.framework:
            fw_key = entry_point.framework
            self.framework_summary[fw_key] = self.framework_summary.get(fw_key, 0) + 1

    def get_critical_entry_points(self) -> List[EntryPoint]:
        """Get all critical and high-priority entry points"""
        return [
            ep for ep in self.entry_points
            if ep.criticality in [CriticalityLevel.CRITICAL, CriticalityLevel.HIGH]
        ]

    def get_entry_points_by_type(self, entry_type: EntryPointType) -> List[EntryPoint]:
        """Get all entry points of a specific type"""
        return [ep for ep in self.entry_points if ep.entry_type == entry_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "entry_points": [ep.to_dict() for ep in self.entry_points],
            "criticality_summary": self.criticality_summary,
            "framework_summary": self.framework_summary,
            "risk_assessment": self.risk_assessment,
            "total_entry_points": len(self.entry_points),
            "critical_count": len(self.get_critical_entry_points())
        }


class EntryPointDetector:
    """
    Entry point detector following Martin Fowler's guidance.

    This class identifies critical entry points using multiple detection
    strategies and provides comprehensive risk assessment.

    Following expert committee guidance:
    - Comprehensive Detection: Multiple heuristics and patterns
    - Framework Awareness: Understands common patterns
    - Risk Assessment: Evaluates impact and protection needs
    """

    # Python entry point patterns
    PYTHON_MAIN_PATTERNS = [
        r'if\s+__name__\s*==\s*["\']__main__["\']',
        r'def\s+main\s*\(',
        r'app\.run\s*\(',
        r'uvicorn\.run\s*\(',
        r'gunicorn',
        r'manage\.py',
        r'wsgi\.py',
        r'asgi\.py'
    ]

    # JavaScript/TypeScript entry patterns
    JS_MAIN_PATTERNS = [
        r'app\.listen\s*\(',
        r'server\.listen\s*\(',
        r'express\s*\(\)',
        r'fastify\s*\(\)',
        r'process\.argv',
        r'commander\.program',
        r'yargs\.argv'
    ]

    # Configuration file patterns
    CONFIG_PATTERNS = {
        'requirements.txt': EntryPointType.CONFIGURATION,
        'package.json': EntryPointType.CONFIGURATION,
        'pyproject.toml': EntryPointType.CONFIGURATION,
        'setup.py': EntryPointType.CONFIGURATION,
        'Dockerfile': EntryPointType.BUILD_SCRIPT,
        'docker-compose.yml': EntryPointType.BUILD_SCRIPT,
        'Makefile': EntryPointType.BUILD_SCRIPT,
        '.env': EntryPointType.CONFIGURATION,
        'settings.py': EntryPointType.CONFIGURATION,
        'config.py': EntryPointType.CONFIGURATION,
        'alembic.ini': EntryPointType.DATABASE_MIGRATION
    }

    # Framework-specific patterns
    FRAMEWORK_PATTERNS = {
        'django': {
            'patterns': [r'django\.', r'DJANGO_SETTINGS_MODULE', r'manage\.py'],
            'entry_files': ['manage.py', 'wsgi.py', 'asgi.py', 'settings.py'],
            'criticality': CriticalityLevel.CRITICAL
        },
        'flask': {
            'patterns': [r'from\s+flask\s+import', r'Flask\s*\(', r'app\.run\s*\('],
            'entry_files': ['app.py', 'main.py', 'wsgi.py'],
            'criticality': CriticalityLevel.CRITICAL
        },
        'fastapi': {
            'patterns': [r'from\s+fastapi\s+import', r'FastAPI\s*\(', r'uvicorn\.run'],
            'entry_files': ['main.py', 'app.py', 'asgi.py'],
            'criticality': CriticalityLevel.CRITICAL
        },
        'express': {
            'patterns': [r'express\s*\(\)', r'app\.listen', r'require\s*\(\s*["\']express["\']'],
            'entry_files': ['app.js', 'server.js', 'index.js', 'main.js'],
            'criticality': CriticalityLevel.CRITICAL
        },
        'react': {
            'patterns': [r'React\.', r'from\s+["\']react["\']', r'ReactDOM\.render'],
            'entry_files': ['index.js', 'App.js', 'main.js'],
            'criticality': CriticalityLevel.HIGH
        },
        'pytest': {
            'patterns': [r'import\s+pytest', r'@pytest\.', r'conftest\.py'],
            'entry_files': ['conftest.py', 'pytest.ini'],
            'criticality': CriticalityLevel.MEDIUM
        }
    }

    def __init__(
        self,
        project_root: Path,
        confidence_threshold: float = 0.6
    ):
        """
        Initialize entry point detector.

        Args:
            project_root: Root directory of the project
            confidence_threshold: Minimum confidence for including entry points
        """
        self.project_root = Path(project_root).resolve()
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(__name__)

        # Cache for analysis results
        self._framework_cache: Dict[str, Optional[str]] = {}
        self._content_cache: Dict[Path, str] = {}

    def detect_entry_points(
        self,
        metadata_list: List[ExtendedMetadata],
        dependency_graph: Optional[DependencyGraph] = None
    ) -> EntryPointAnalysis:
        """
        Detect all entry points in the codebase.

        Args:
            metadata_list: List of file metadata objects
            dependency_graph: Optional dependency graph for enhanced analysis

        Returns:
            EntryPointAnalysis: Complete analysis of entry points
        """
        analysis = EntryPointAnalysis()

        self.logger.info(f"Detecting entry points for {len(metadata_list)} files")

        # Process each file
        for i, metadata in enumerate(metadata_list):
            try:
                entry_points = self._analyze_file_for_entry_points(metadata)

                # Enhance with dependency information if available
                if dependency_graph:
                    entry_points = self._enhance_with_dependencies(entry_points, dependency_graph)

                # Add to analysis
                for ep in entry_points:
                    if ep.confidence >= self.confidence_threshold:
                        analysis.add_entry_point(ep)

                # Log progress
                if (i + 1) % 100 == 0 or (i + 1) == len(metadata_list):
                    self.logger.info(f"Processed {i + 1}/{len(metadata_list)} files")

            except Exception as e:
                self.logger.error(f"Error analyzing entry points for {metadata.file_path}: {e}")

        # Generate risk assessment
        analysis.risk_assessment = self._generate_risk_assessment(analysis)

        self.logger.info(f"Found {len(analysis.entry_points)} entry points")

        return analysis

    def _analyze_file_for_entry_points(self, metadata: ExtendedMetadata) -> List[EntryPoint]:
        """
        Analyze a single file for entry points.

        Args:
            metadata: File metadata object

        Returns:
            List[EntryPoint]: Entry points found in the file
        """
        entry_points = []

        # Check filename patterns first
        filename_entries = self._check_filename_patterns(metadata)
        entry_points.extend(filename_entries)

        # Check content patterns for code files
        if not metadata.is_binary and metadata.size_bytes < 10 * 1024 * 1024:
            content_entries = self._check_content_patterns(metadata)
            entry_points.extend(content_entries)

        # Framework-specific detection
        framework_entries = self._check_framework_patterns(metadata)
        entry_points.extend(framework_entries)

        # Remove duplicates (same file, same type)
        unique_entries = self._deduplicate_entry_points(entry_points)

        return unique_entries

    def _check_filename_patterns(self, metadata: ExtendedMetadata) -> List[EntryPoint]:
        """Check filename patterns for entry points."""
        entry_points = []
        filename = metadata.file_path.name.lower()

        # Configuration and build files
        if filename in self.CONFIG_PATTERNS:
            entry_type = self.CONFIG_PATTERNS[filename]
            criticality = CriticalityLevel.HIGH if entry_type == EntryPointType.CONFIGURATION else CriticalityLevel.MEDIUM

            entry_points.append(EntryPoint(
                file_path=metadata.file_path,
                entry_type=entry_type,
                criticality=criticality,
                description=f"Configuration/build file: {filename}",
                confidence=0.9,
                language=metadata.language,
                detection_method="filename_pattern"
            ))

        # Common entry point names
        entry_names = {
            'main.py': (EntryPointType.MAIN_APPLICATION, CriticalityLevel.CRITICAL),
            'app.py': (EntryPointType.WEB_SERVER, CriticalityLevel.CRITICAL),
            'manage.py': (EntryPointType.CLI_SCRIPT, CriticalityLevel.CRITICAL),
            'wsgi.py': (EntryPointType.WEB_SERVER, CriticalityLevel.CRITICAL),
            'asgi.py': (EntryPointType.WEB_SERVER, CriticalityLevel.CRITICAL),
            'index.js': (EntryPointType.MAIN_APPLICATION, CriticalityLevel.HIGH),
            'server.js': (EntryPointType.WEB_SERVER, CriticalityLevel.CRITICAL),
            'app.js': (EntryPointType.WEB_SERVER, CriticalityLevel.HIGH),
            '__init__.py': (EntryPointType.PACKAGE_INIT, CriticalityLevel.MEDIUM),
            'conftest.py': (EntryPointType.TEST_RUNNER, CriticalityLevel.MEDIUM)
        }

        if filename in entry_names:
            entry_type, criticality = entry_names[filename]
            entry_points.append(EntryPoint(
                file_path=metadata.file_path,
                entry_type=entry_type,
                criticality=criticality,
                description=f"Entry point file: {filename}",
                confidence=0.8,
                language=metadata.language,
                detection_method="filename_pattern"
            ))

        return entry_points

    def _check_content_patterns(self, metadata: ExtendedMetadata) -> List[EntryPoint]:
        """Check file content for entry point patterns."""
        entry_points = []

        try:
            content = self._get_file_content(metadata.file_path)

            if metadata.language == 'Python':
                entry_points.extend(self._check_python_patterns(metadata, content))
            elif metadata.language in ['JavaScript', 'TypeScript']:
                entry_points.extend(self._check_js_patterns(metadata, content))

        except Exception as e:
            self.logger.warning(f"Error reading content for {metadata.file_path}: {e}")

        return entry_points

    def _check_python_patterns(self, metadata: ExtendedMetadata, content: str) -> List[EntryPoint]:
        """Check Python-specific entry point patterns."""
        entry_points = []
        lines = content.splitlines()

        # Check for __main__ guard
        for line_num, line in enumerate(lines, 1):
            if re.search(self.PYTHON_MAIN_PATTERNS[0], line):
                entry_points.append(EntryPoint(
                    file_path=metadata.file_path,
                    entry_type=EntryPointType.MAIN_APPLICATION,
                    criticality=CriticalityLevel.CRITICAL,
                    description="Python main entry point with __name__ == '__main__' guard",
                    confidence=0.95,
                    language='Python',
                    detection_method="content_pattern",
                    line_numbers=[line_num],
                    code_patterns=[line.strip()]
                ))

        # Check for main function definition
        main_func_pattern = r'def\s+main\s*\('
        for line_num, line in enumerate(lines, 1):
            if re.search(main_func_pattern, line):
                entry_points.append(EntryPoint(
                    file_path=metadata.file_path,
                    entry_type=EntryPointType.MAIN_APPLICATION,
                    criticality=CriticalityLevel.HIGH,
                    description="Python main function definition",
                    confidence=0.8,
                    language='Python',
                    detection_method="content_pattern",
                    line_numbers=[line_num],
                    code_patterns=[line.strip()]
                ))

        # Check for web framework patterns
        web_patterns = [
            (r'app\.run\s*\(', EntryPointType.WEB_SERVER, "Flask app.run()"),
            (r'uvicorn\.run\s*\(', EntryPointType.WEB_SERVER, "Uvicorn server run"),
            (r'gunicorn', EntryPointType.WEB_SERVER, "Gunicorn WSGI server")
        ]

        for pattern, entry_type, description in web_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    entry_points.append(EntryPoint(
                        file_path=metadata.file_path,
                        entry_type=entry_type,
                        criticality=CriticalityLevel.CRITICAL,
                        description=description,
                        confidence=0.9,
                        language='Python',
                        detection_method="content_pattern",
                        line_numbers=[line_num],
                        code_patterns=[line.strip()]
                    ))

        return entry_points

    def _check_js_patterns(self, metadata: ExtendedMetadata, content: str) -> List[EntryPoint]:
        """Check JavaScript/TypeScript entry point patterns."""
        entry_points = []
        lines = content.splitlines()

        # Check for server startup patterns
        server_patterns = [
            (r'app\.listen\s*\(', EntryPointType.WEB_SERVER, "Express app.listen()"),
            (r'server\.listen\s*\(', EntryPointType.WEB_SERVER, "Server listen()"),
            (r'express\s*\(\)', EntryPointType.WEB_SERVER, "Express application"),
            (r'fastify\s*\(\)', EntryPointType.WEB_SERVER, "Fastify application")
        ]

        for pattern, entry_type, description in server_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    entry_points.append(EntryPoint(
                        file_path=metadata.file_path,
                        entry_type=entry_type,
                        criticality=CriticalityLevel.CRITICAL,
                        description=description,
                        confidence=0.9,
                        language=metadata.language,
                        detection_method="content_pattern",
                        line_numbers=[line_num],
                        code_patterns=[line.strip()]
                    ))

        # Check for CLI patterns
        cli_patterns = [
            (r'process\.argv', EntryPointType.CLI_SCRIPT, "Command-line argument processing"),
            (r'commander\.program', EntryPointType.CLI_SCRIPT, "Commander.js CLI"),
            (r'yargs\.argv', EntryPointType.CLI_SCRIPT, "Yargs CLI")
        ]

        for pattern, entry_type, description in cli_patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    entry_points.append(EntryPoint(
                        file_path=metadata.file_path,
                        entry_type=entry_type,
                        criticality=CriticalityLevel.HIGH,
                        description=description,
                        confidence=0.8,
                        language=metadata.language,
                        detection_method="content_pattern",
                        line_numbers=[line_num],
                        code_patterns=[line.strip()]
                    ))

        return entry_points

    def _check_framework_patterns(self, metadata: ExtendedMetadata) -> List[EntryPoint]:
        """Check for framework-specific entry points."""
        entry_points = []

        try:
            content = self._get_file_content(metadata.file_path)

            for framework, config in self.FRAMEWORK_PATTERNS.items():
                # Check if file matches framework patterns
                framework_score = 0
                matched_patterns = []

                for pattern in config['patterns']:
                    if re.search(pattern, content):
                        framework_score += 1
                        matched_patterns.append(pattern)

                # Check if filename matches framework entry files
                filename = metadata.file_path.name
                if filename in config['entry_files']:
                    framework_score += 2

                # If we have evidence of this framework
                if framework_score > 0:
                    confidence = min(0.6 + (framework_score * 0.1), 1.0)

                    entry_points.append(EntryPoint(
                        file_path=metadata.file_path,
                        entry_type=EntryPointType.FRAMEWORK_HOOK,
                        criticality=config['criticality'],
                        description=f"{framework.title()} framework entry point",
                        confidence=confidence,
                        framework=framework,
                        language=metadata.language,
                        detection_method="framework_pattern",
                        code_patterns=matched_patterns
                    ))

        except Exception as e:
            self.logger.warning(f"Error checking framework patterns for {metadata.file_path}: {e}")

        return entry_points

    def _enhance_with_dependencies(
        self,
        entry_points: List[EntryPoint],
        dependency_graph: DependencyGraph
    ) -> List[EntryPoint]:
        """Enhance entry points with dependency information."""
        for entry_point in entry_points:
            file_str = str(entry_point.file_path)

            # Find incoming dependencies (files that import this one)
            for edge in dependency_graph.edges:
                if edge.target_module == file_str:
                    entry_point.incoming_dependencies.add(str(edge.source_file))
                elif str(edge.source_file) == file_str:
                    entry_point.outgoing_dependencies.add(edge.target_module)

            # Adjust criticality based on dependency count
            incoming_count = len(entry_point.incoming_dependencies)
            if incoming_count > 10:
                # Many files depend on this - very critical
                if entry_point.criticality == CriticalityLevel.HIGH:
                    entry_point.criticality = CriticalityLevel.CRITICAL
                entry_point.risk_factors.append(f"High incoming dependency count: {incoming_count}")

            # Check if it's truly an entry point (no incoming dependencies)
            if incoming_count == 0 and file_str in dependency_graph.entry_points:
                entry_point.risk_factors.append("True entry point - no incoming dependencies")

        return entry_points

    def _deduplicate_entry_points(self, entry_points: List[EntryPoint]) -> List[EntryPoint]:
        """Remove duplicate entry points for the same file."""
        seen = set()
        unique_entries = []

        for entry_point in entry_points:
            key = (entry_point.file_path, entry_point.entry_type)
            if key not in seen:
                seen.add(key)
                unique_entries.append(entry_point)
            else:
                # Merge with existing entry (keep higher confidence)
                for existing in unique_entries:
                    if (existing.file_path == entry_point.file_path and
                        existing.entry_type == entry_point.entry_type):
                        if entry_point.confidence > existing.confidence:
                            existing.confidence = entry_point.confidence
                            existing.detection_method += f", {entry_point.detection_method}"
                        break

        return unique_entries

    def _generate_risk_assessment(self, analysis: EntryPointAnalysis) -> Dict[str, Any]:
        """Generate comprehensive risk assessment."""
        critical_points = analysis.get_critical_entry_points()

        return {
            "total_entry_points": len(analysis.entry_points),
            "critical_entry_points": len(critical_points),
            "risk_level": self._calculate_overall_risk(analysis),
            "highest_risk_files": [
                str(ep.file_path) for ep in critical_points[:5]
            ],
            "framework_dependencies": analysis.framework_summary,
            "recommendations": self._generate_recommendations(analysis)
        }

    def _calculate_overall_risk(self, analysis: EntryPointAnalysis) -> str:
        """Calculate overall risk level for the repository reorganization."""
        critical_count = analysis.criticality_summary.get('critical', 0)
        high_count = analysis.criticality_summary.get('high', 0)
        total_count = len(analysis.entry_points)

        if critical_count > 10 or (critical_count + high_count) > total_count * 0.5:
            return "HIGH"
        elif critical_count > 5 or (critical_count + high_count) > total_count * 0.3:
            return "MEDIUM"
        else:
            return "LOW"

    def _generate_recommendations(self, analysis: EntryPointAnalysis) -> List[str]:
        """Generate recommendations for safe reorganization."""
        recommendations = [
            "Create comprehensive backup before reorganization",
            "Test all entry points before and after moves",
            "Update documentation with new file locations"
        ]

        critical_points = analysis.get_critical_entry_points()
        if len(critical_points) > 5:
            recommendations.append(
                f"Special attention needed: {len(critical_points)} critical entry points detected"
            )

        if 'django' in analysis.framework_summary:
            recommendations.append("Django detected - test manage.py commands after reorganization")

        if 'flask' in analysis.framework_summary:
            recommendations.append("Flask detected - verify WSGI configuration after moves")

        return recommendations

    def _get_file_content(self, file_path: Path) -> str:
        """Get file content with caching."""
        if file_path not in self._content_cache:
            try:
                self._content_cache[file_path] = file_path.read_text(
                    encoding='utf-8', errors='ignore'
                )
            except Exception as e:
                self.logger.warning(f"Error reading {file_path}: {e}")
                self._content_cache[file_path] = ""

        return self._content_cache[file_path]

    def get_statistics(self, analysis: EntryPointAnalysis) -> Dict[str, Any]:
        """Generate statistics about the entry point analysis."""
        return {
            "total_entry_points": len(analysis.entry_points),
            "by_type": {
                entry_type.value: len(analysis.get_entry_points_by_type(entry_type))
                for entry_type in EntryPointType
            },
            "by_criticality": analysis.criticality_summary,
            "by_framework": analysis.framework_summary,
            "risk_level": analysis.risk_assessment.get("risk_level", "UNKNOWN"),
            "average_confidence": sum(ep.confidence for ep in analysis.entry_points) / max(len(analysis.entry_points), 1)
        }


def create_detector(
    project_root: str,
    confidence_threshold: float = 0.6,
    **kwargs: Any
) -> EntryPointDetector:
    """
    Factory function to create an entry point detector.

    Args:
        project_root: Root directory of the project
        confidence_threshold: Minimum confidence for including entry points
        **kwargs: Additional arguments for EntryPointDetector

    Returns:
        EntryPointDetector: Configured detector instance
    """
    return EntryPointDetector(
        project_root=Path(project_root),
        confidence_threshold=confidence_threshold,
        **kwargs
    )


if __name__ == "__main__":
    # Example usage and testing
    import sys

    if len(sys.argv) != 2:
        print("Usage: python entry_point_detector.py <project_root>")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Import required modules
    from traversal import create_traverser
    from metadata_extractor import create_extractor
    from dependency_analyzer import create_analyzer

    project_root = Path(sys.argv[1])

    print(f"Detecting entry points for project: {project_root}")

    # Get file metadata
    traverser = create_traverser(str(project_root))
    files = list(traverser.traverse())

    extractor = create_extractor()
    metadata_list = extractor.extract_batch_metadata(files)

    # Analyze dependencies
    analyzer = create_analyzer(str(project_root))
    dependency_graph = analyzer.analyze_dependencies(metadata_list)

    # Detect entry points
    detector = create_detector(str(project_root))
    analysis = detector.detect_entry_points(metadata_list, dependency_graph)

    # Generate statistics
    stats = detector.get_statistics(analysis)

    # Print results
    print(f"\nEntry Point Detection Complete:")
    print(f"  Total entry points: {stats['total_entry_points']}")
    print(f"  By criticality: {stats['by_criticality']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Risk level: {stats['risk_level']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")

    # Show critical entry points
    critical_points = analysis.get_critical_entry_points()
    if critical_points:
        print(f"\nCritical Entry Points:")
        for ep in critical_points[:10]:  # Show first 10
            print(f"  - {ep.file_path} ({ep.entry_type.value})")
            print(f"    Description: {ep.description}")
            print(f"    Confidence: {ep.confidence:.2f}")
            if ep.risk_factors:
                print(f"    Risk factors: {', '.join(ep.risk_factors)}")
            print()

    # Show recommendations
    if analysis.risk_assessment.get('recommendations'):
        print(f"Recommendations:")
        for rec in analysis.risk_assessment['recommendations']:
            print(f"  - {rec}")
