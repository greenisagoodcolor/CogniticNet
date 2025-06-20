#!/usr/bin/env python3
"""
Complete Repository Inventory Generator

This module integrates all repository analysis components to generate a comprehensive
inventory following expert committee guidance. Creates structured JSON output with
all analysis results for safe reorganization planning.

Key principles:
- Comprehensive Integration: Combines all analysis modules
- Structured Output: Well-defined JSON schema for tools consumption
- Data Integrity: Validates and cross-references all analysis results
- Actionable Intelligence: Provides clear reorganization recommendations
"""

import json
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Any, Union
from dataclasses import dataclass, field, asdict

try:
    from .traversal import RepositoryTraverser, FileInfo, create_traverser
    from .hash_calculator import MD5Calculator, create_calculator
    from .metadata_extractor import MetadataExtractor, ExtendedMetadata, create_extractor
    from .dependency_analyzer import DependencyAnalyzer, DependencyGraph, create_analyzer
    from .entry_point_detector import EntryPointDetector, EntryPointAnalysis, create_detector
    from .naming_analyzer import NamingAnalyzer, NamingAnalysis, create_analyzer as create_naming_analyzer
except ImportError:
    from traversal import RepositoryTraverser, FileInfo, create_traverser
    from hash_calculator import MD5Calculator, create_calculator
    from metadata_extractor import MetadataExtractor, ExtendedMetadata, create_extractor
    from dependency_analyzer import DependencyAnalyzer, DependencyGraph, create_analyzer
    from entry_point_detector import EntryPointDetector, EntryPointAnalysis, create_detector
    from naming_analyzer import NamingAnalyzer, NamingAnalysis, create_analyzer as create_naming_analyzer


@dataclass
class InventoryMetadata:
    """
    Metadata about the inventory generation process.

    Provides comprehensive information about when, how, and what
    was analyzed during inventory generation.
    """
    generation_timestamp: str
    project_root: str
    total_files_analyzed: int
    total_size_bytes: int
    analysis_duration_seconds: float

    # Tool versions and configuration
    analyzer_version: str = "1.0.0"
    python_version: str = ""

    # Analysis scope
    included_extensions: List[str] = field(default_factory=list)
    excluded_patterns: List[str] = field(default_factory=list)

    # Quality metrics
    analysis_completeness: float = 1.0  # 0.0 to 1.0
    error_count: int = 0
    warning_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


@dataclass
class RepositoryInventory:
    """
    Complete repository inventory with all analysis results.

    This is the master data structure that contains all repository
    analysis results in a structured, queryable format.
    """
    metadata: InventoryMetadata

    # Core file information
    files: List[Dict[str, Any]] = field(default_factory=list)
    file_hashes: Dict[str, str] = field(default_factory=dict)

    # Extended analysis results
    dependency_graph: Optional[Dict[str, Any]] = None
    entry_points: Optional[Dict[str, Any]] = None
    naming_analysis: Optional[Dict[str, Any]] = None

    # Summary statistics
    file_type_summary: Dict[str, int] = field(default_factory=dict)
    language_summary: Dict[str, int] = field(default_factory=dict)
    size_distribution: Dict[str, int] = field(default_factory=dict)

    # Risk assessment
    reorganization_risk: str = "UNKNOWN"  # LOW, MEDIUM, HIGH, CRITICAL
    critical_files: List[str] = field(default_factory=list)
    protected_files: List[str] = field(default_factory=list)

    # Recommendations
    recommendations: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    def save_to_file(self, output_path: Path) -> None:
        """Save inventory to JSON file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_from_file(cls, input_path: Path) -> 'RepositoryInventory':
        """Load inventory from JSON file"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Reconstruct the dataclass from dictionary
        # Note: This is a simplified reconstruction
        metadata = InventoryMetadata(**data['metadata'])
        inventory = cls(metadata=metadata)

        # Copy all other fields
        for key, value in data.items():
            if key != 'metadata' and hasattr(inventory, key):
                setattr(inventory, key, value)

        return inventory


class InventoryGenerator:
    """
    Complete repository inventory generator.

    This class orchestrates all analysis modules to create a comprehensive
    repository inventory following expert committee guidance.

    Following expert committee guidance:
    - Comprehensive Analysis: Uses all available analysis modules
    - Data Integration: Cross-references and validates analysis results
    - Risk Assessment: Evaluates reorganization risks and impacts
    - Actionable Output: Provides clear recommendations and action items
    """

    def __init__(
        self,
        project_root: Path,
        output_dir: Optional[Path] = None,
        include_external_deps: bool = True,
        strict_naming: bool = False
    ):
        """
        Initialize inventory generator.

        Args:
            project_root: Root directory of the project
            output_dir: Directory to save analysis results
            include_external_deps: Whether to include external dependencies
            strict_naming: Whether to use strict naming convention enforcement
        """
        self.project_root = Path(project_root).resolve()
        self.output_dir = output_dir or (self.project_root / '.repository_analysis')
        self.include_external_deps = include_external_deps
        self.strict_naming = strict_naming

        self.logger = logging.getLogger(__name__)

        # Initialize analysis modules
        self.traverser = create_traverser(str(self.project_root))
        self.calculator = create_calculator()
        self.extractor = create_extractor()
        self.dependency_analyzer = create_analyzer(
            str(self.project_root),
            include_external=include_external_deps
        )
        self.entry_detector = create_detector(str(self.project_root))
        self.naming_analyzer = create_naming_analyzer(
            str(self.project_root),
            strict_mode=strict_naming
        )

        # Statistics tracking
        self.start_time: Optional[datetime] = None
        self.error_count = 0
        self.warning_count = 0

    def generate_complete_inventory(
        self,
        save_intermediate: bool = True,
        max_files: Optional[int] = None
    ) -> RepositoryInventory:
        """
        Generate complete repository inventory.

        Args:
            save_intermediate: Whether to save intermediate analysis results
            max_files: Maximum number of files to analyze (for testing)

        Returns:
            RepositoryInventory: Complete inventory with all analysis results
        """
        self.start_time = datetime.now(timezone.utc)
        self.logger.info(f"Starting complete repository inventory for: {self.project_root}")

        try:
            # Step 1: File traversal and basic metadata
            self.logger.info("Step 1: File traversal and hash calculation")
            files = self._perform_file_traversal(max_files)

            # Step 2: Extended metadata extraction
            self.logger.info("Step 2: Extended metadata extraction")
            metadata_list = self._perform_metadata_extraction(files)

            if save_intermediate:
                self._save_intermediate_results("01_metadata", metadata_list)

            # Step 3: Dependency analysis
            self.logger.info("Step 3: Dependency graph analysis")
            dependency_graph = self._perform_dependency_analysis(metadata_list)

            if save_intermediate:
                self._save_intermediate_results("02_dependencies", dependency_graph)

            # Step 4: Entry point detection
            self.logger.info("Step 4: Entry point detection")
            entry_analysis = self._perform_entry_point_analysis(metadata_list, dependency_graph)

            if save_intermediate:
                self._save_intermediate_results("03_entry_points", entry_analysis)

            # Step 5: Naming convention analysis
            self.logger.info("Step 5: Naming convention analysis")
            naming_analysis = self._perform_naming_analysis(metadata_list)

            if save_intermediate:
                self._save_intermediate_results("04_naming", naming_analysis)

            # Step 6: Integration and risk assessment
            self.logger.info("Step 6: Integration and risk assessment")
            inventory = self._integrate_all_analyses(
                files, metadata_list, dependency_graph, entry_analysis, naming_analysis
            )

            # Step 7: Generate recommendations
            self.logger.info("Step 7: Generating recommendations")
            self._generate_recommendations(inventory)

            # Save final inventory
            final_path = self.output_dir / "complete_inventory.json"
            inventory.save_to_file(final_path)
            self.logger.info(f"Complete inventory saved to: {final_path}")

            duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()
            self.logger.info(f"Inventory generation completed in {duration:.2f} seconds")

            return inventory

        except Exception as e:
            self.logger.error(f"Error during inventory generation: {e}")
            raise

    def _perform_file_traversal(self, max_files: Optional[int] = None) -> List[FileInfo]:
        """Perform file traversal and hash calculation."""
        files = list(self.traverser.traverse())

        if max_files:
            files = files[:max_files]

        self.logger.info(f"Found {len(files)} files to analyze")

        # Calculate hashes for all files
        file_paths = [f.path for f in files]
        try:
            # Try the batch method if it exists
            if hasattr(self.calculator, 'calculate_hashes_batch'):
                hash_results = self.calculator.calculate_hashes_batch(file_paths)
            else:
                # Fall back to individual calculation
                hash_results = {}
                for file_path in file_paths:
                    try:
                        hash_results[file_path] = self.calculator.calculate_hash(file_path)
                    except Exception as e:
                        self.logger.warning(f"Error calculating hash for {file_path}: {e}")
                        hash_results[file_path] = ""
        except Exception as e:
            self.logger.warning(f"Error calculating hashes: {e}")
            hash_results = {}

        # Attach hashes to file info
        for file_info in files:
            setattr(file_info, 'hash', hash_results.get(file_info.path, ""))

        return files

    def _perform_metadata_extraction(self, files: List[FileInfo]) -> List[ExtendedMetadata]:
        """Perform extended metadata extraction."""
        metadata_list = self.extractor.extract_batch_metadata(files)
        self.logger.info(f"Extracted metadata for {len(metadata_list)} files")
        return metadata_list

    def _perform_dependency_analysis(self, metadata_list: List[ExtendedMetadata]) -> DependencyGraph:
        """Perform dependency graph analysis."""
        dependency_graph = self.dependency_analyzer.analyze_dependencies(metadata_list)

        stats = self.dependency_analyzer.get_statistics(dependency_graph)
        self.logger.info(f"Dependency analysis: {stats['total_edges']} dependencies found")

        return dependency_graph

    def _perform_entry_point_analysis(
        self,
        metadata_list: List[ExtendedMetadata],
        dependency_graph: DependencyGraph
    ) -> EntryPointAnalysis:
        """Perform entry point detection analysis."""
        entry_analysis = self.entry_detector.detect_entry_points(metadata_list, dependency_graph)

        stats = self.entry_detector.get_statistics(entry_analysis)
        self.logger.info(f"Entry point analysis: {stats['total_entry_points']} entry points found")

        return entry_analysis

    def _perform_naming_analysis(self, metadata_list: List[ExtendedMetadata]) -> NamingAnalysis:
        """Perform naming convention analysis."""
        naming_analysis = self.naming_analyzer.analyze_naming(metadata_list)

        stats = self.naming_analyzer.get_statistics(naming_analysis)
        self.logger.info(f"Naming analysis: {stats['total_violations']} violations found")

        return naming_analysis

    def _integrate_all_analyses(
        self,
        files: List[FileInfo],
        metadata_list: List[ExtendedMetadata],
        dependency_graph: DependencyGraph,
        entry_analysis: EntryPointAnalysis,
        naming_analysis: NamingAnalysis
    ) -> RepositoryInventory:
        """Integrate all analysis results into a complete inventory."""

        # Calculate analysis duration
        duration = (datetime.now(timezone.utc) - self.start_time).total_seconds()

        # Create metadata
        import sys
        inventory_metadata = InventoryMetadata(
            generation_timestamp=datetime.now(timezone.utc).isoformat(),
            project_root=str(self.project_root),
            total_files_analyzed=len(files),
            total_size_bytes=sum(f.size for f in files),
            analysis_duration_seconds=duration,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            error_count=self.error_count,
            warning_count=self.warning_count
        )

        # Create inventory
        inventory = RepositoryInventory(metadata=inventory_metadata)

        # Add file information
        inventory.files = [
            {
                "path": str(metadata.file_path),
                "size_bytes": metadata.size_bytes,
                "hash": getattr(metadata, 'hash', ''),
                "language": metadata.language,
                "file_type": metadata.file_type.value if metadata.file_type else 'unknown',
                "is_binary": metadata.is_binary,
                "is_test": metadata.is_test,
                "last_modified": metadata.last_modified.isoformat() if metadata.last_modified else None,
                "git_tracked": metadata.git_tracked,
                "line_count": getattr(metadata, 'line_count', 0),
                "dependencies": len([
                    dep for dep in dependency_graph.edges
                    if str(dep.source_file) == str(metadata.file_path)
                ])
            }
            for metadata in metadata_list
        ]

        # Add file hashes
        inventory.file_hashes = {
            str(metadata.file_path): getattr(metadata, 'hash', '')
            for metadata in metadata_list
        }

        # Add analysis results
        inventory.dependency_graph = dependency_graph.to_dict()
        inventory.entry_points = entry_analysis.to_dict()
        inventory.naming_analysis = naming_analysis.to_dict()

        # Generate summaries
        self._generate_summaries(inventory, metadata_list)

        # Perform risk assessment
        self._assess_reorganization_risk(inventory, entry_analysis, naming_analysis)

        return inventory

    def _generate_summaries(
        self,
        inventory: RepositoryInventory,
        metadata_list: List[ExtendedMetadata]
    ) -> None:
        """Generate summary statistics for the inventory."""

        # File type summary
        for metadata in metadata_list:
            file_type = metadata.file_type.value if metadata.file_type else 'unknown'
            inventory.file_type_summary[file_type] = inventory.file_type_summary.get(file_type, 0) + 1

        # Language summary
        for metadata in metadata_list:
            if metadata.language:
                inventory.language_summary[metadata.language] = inventory.language_summary.get(metadata.language, 0) + 1

        # Size distribution
        size_ranges = [
            ("0-1KB", 0, 1024),
            ("1KB-10KB", 1024, 10240),
            ("10KB-100KB", 10240, 102400),
            ("100KB-1MB", 102400, 1048576),
            ("1MB+", 1048576, float('inf'))
        ]

        for metadata in metadata_list:
            for range_name, min_size, max_size in size_ranges:
                if min_size <= metadata.size_bytes < max_size:
                    inventory.size_distribution[range_name] = inventory.size_distribution.get(range_name, 0) + 1
                    break

    def _assess_reorganization_risk(
        self,
        inventory: RepositoryInventory,
        entry_analysis: EntryPointAnalysis,
        naming_analysis: NamingAnalysis
    ) -> None:
        """Assess the risk level for repository reorganization."""

        risk_factors = []
        risk_score = 0

        # Entry point risk assessment
        critical_entry_points = entry_analysis.get_critical_entry_points()
        if len(critical_entry_points) > 10:
            risk_score += 3
            risk_factors.append(f"{len(critical_entry_points)} critical entry points")
        elif len(critical_entry_points) > 5:
            risk_score += 2
            risk_factors.append(f"{len(critical_entry_points)} critical entry points")
        elif len(critical_entry_points) > 0:
            risk_score += 1
            risk_factors.append(f"{len(critical_entry_points)} critical entry points")

        # Dependency complexity
        if inventory.dependency_graph:
            circular_deps = len(inventory.dependency_graph.get('circular_dependencies', []))
            total_deps = inventory.dependency_graph.get('total_edges', 0)

            if circular_deps > 0:
                risk_score += 2
                risk_factors.append(f"{circular_deps} circular dependencies")

            if total_deps > 1000:
                risk_score += 2
                risk_factors.append(f"{total_deps} total dependencies")
            elif total_deps > 500:
                risk_score += 1
                risk_factors.append(f"{total_deps} total dependencies")

        # Naming inconsistency impact
        high_naming_violations = len(naming_analysis.get_violations_by_severity("high"))
        if high_naming_violations > 50:
            risk_score += 2
            risk_factors.append(f"{high_naming_violations} high-priority naming violations")
        elif high_naming_violations > 10:
            risk_score += 1
            risk_factors.append(f"{high_naming_violations} high-priority naming violations")

        # File count impact
        total_files = len(inventory.files)
        if total_files > 1000:
            risk_score += 1
            risk_factors.append(f"{total_files} total files")

        # Determine overall risk level
        if risk_score >= 8:
            inventory.reorganization_risk = "CRITICAL"
        elif risk_score >= 5:
            inventory.reorganization_risk = "HIGH"
        elif risk_score >= 2:
            inventory.reorganization_risk = "MEDIUM"
        else:
            inventory.reorganization_risk = "LOW"

        # Identify critical and protected files
        for entry_point in critical_entry_points:
            file_path = str(entry_point.file_path)
            inventory.critical_files.append(file_path)
            inventory.protected_files.append(file_path)

        # Add files with many dependencies
        if inventory.dependency_graph:
            for edge in inventory.dependency_graph.get('edges', []):
                # Count incoming dependencies for each file
                target = edge.get('target')
                if target and target not in inventory.protected_files:
                    # Count how many files depend on this one
                    dependents = sum(
                        1 for e in inventory.dependency_graph.get('edges', [])
                        if e.get('target') == target
                    )
                    if dependents > 5:  # Arbitrary threshold
                        inventory.protected_files.append(target)

    def _generate_recommendations(self, inventory: RepositoryInventory) -> None:
        """Generate actionable recommendations for repository reorganization."""

        recommendations = []
        action_items = []

        # Risk-based recommendations
        if inventory.reorganization_risk == "CRITICAL":
            recommendations.append("⚠️  CRITICAL RISK: Extensive testing and staged reorganization required")
            recommendations.append("Create comprehensive backup and rollback plan")
            recommendations.append("Consider reorganizing in smaller, incremental steps")

            action_items.append({
                "priority": "critical",
                "action": "Create detailed reorganization plan",
                "description": "Break down reorganization into safe, testable stages",
                "estimated_effort": "high"
            })

        elif inventory.reorganization_risk == "HIGH":
            recommendations.append("⚠️  HIGH RISK: Careful planning and testing required")
            recommendations.append("Test all entry points before and after reorganization")

            action_items.append({
                "priority": "high",
                "action": "Validate all entry points",
                "description": "Ensure all critical entry points work after reorganization",
                "estimated_effort": "medium"
            })

        # Entry point recommendations
        if inventory.entry_points:
            critical_count = inventory.entry_points.get('critical_count', 0)
            if critical_count > 0:
                recommendations.append(f"Protect {critical_count} critical entry points during reorganization")

                action_items.append({
                    "priority": "high",
                    "action": "Document entry point dependencies",
                    "description": "Map all dependencies for critical entry points",
                    "estimated_effort": "medium"
                })

        # Dependency recommendations
        if inventory.dependency_graph:
            circular_deps = len(inventory.dependency_graph.get('circular_dependencies', []))
            if circular_deps > 0:
                recommendations.append(f"Resolve {circular_deps} circular dependencies before reorganization")

                action_items.append({
                    "priority": "high",
                    "action": "Fix circular dependencies",
                    "description": "Refactor code to eliminate circular import dependencies",
                    "estimated_effort": "high"
                })

        # Naming recommendations
        if inventory.naming_analysis:
            total_violations = inventory.naming_analysis.get('total_violations', 0)
            if total_violations > 100:
                recommendations.append(f"Address {total_violations} naming violations for consistency")

                action_items.append({
                    "priority": "medium",
                    "action": "Standardize naming conventions",
                    "description": "Implement consistent naming across the codebase",
                    "estimated_effort": "medium"
                })

        # General recommendations
        recommendations.extend([
            "Run all tests before and after reorganization",
            "Update documentation to reflect new structure",
            "Use version control to track all changes",
            "Validate build processes after reorganization"
        ])

        action_items.extend([
            {
                "priority": "medium",
                "action": "Update CI/CD pipelines",
                "description": "Ensure build and deployment scripts work with new structure",
                "estimated_effort": "low"
            },
            {
                "priority": "low",
                "action": "Update documentation",
                "description": "Reflect new file locations in all documentation",
                "estimated_effort": "low"
            }
        ])

        inventory.recommendations = recommendations
        inventory.action_items = action_items

    def _save_intermediate_results(self, stage: str, results: Any) -> None:
        """Save intermediate analysis results."""
        try:
            output_path = self.output_dir / f"{stage}_results.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Convert results to dictionary if needed
            if hasattr(results, 'to_dict'):
                data = results.to_dict()
            elif isinstance(results, list) and results and hasattr(results[0], 'to_dict'):
                data = [item.to_dict() for item in results]
            else:
                data = results

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            self.logger.debug(f"Saved {stage} results to: {output_path}")

        except Exception as e:
            self.logger.warning(f"Failed to save {stage} results: {e}")
            self.warning_count += 1


def create_generator(
    project_root: str,
    output_dir: Optional[str] = None,
    **kwargs: Any
) -> InventoryGenerator:
    """
    Factory function to create an inventory generator.

    Args:
        project_root: Root directory of the project
        output_dir: Directory to save analysis results
        **kwargs: Additional arguments for InventoryGenerator

    Returns:
        InventoryGenerator: Configured generator instance
    """
    return InventoryGenerator(
        project_root=Path(project_root),
        output_dir=Path(output_dir) if output_dir else None,
        **kwargs
    )


if __name__ == "__main__":
    # Example usage and testing
    import sys

    if len(sys.argv) != 2:
        print("Usage: python inventory_generator.py <project_root>")
        sys.exit(1)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    project_root = Path(sys.argv[1])

    print(f"Generating complete repository inventory for: {project_root}")

    # Create generator and run analysis
    generator = create_generator(str(project_root))
    inventory = generator.generate_complete_inventory(max_files=200)  # Limit for testing

    # Print summary
    print(f"\n📊 Repository Inventory Complete:")
    print(f"  📁 Total files: {inventory.metadata.total_files_analyzed}")
    print(f"  💾 Total size: {inventory.metadata.total_size_bytes:,} bytes")
    print(f"  ⏱️  Analysis time: {inventory.metadata.analysis_duration_seconds:.2f} seconds")
    print(f"  🎯 Reorganization risk: {inventory.reorganization_risk}")

    if inventory.critical_files:
        print(f"  🔴 Critical files: {len(inventory.critical_files)}")

    if inventory.recommendations:
        print(f"\n💡 Key Recommendations:")
        for rec in inventory.recommendations[:5]:
            print(f"  - {rec}")

    print(f"\n📄 Complete inventory saved to: {generator.output_dir / 'complete_inventory.json'}")
