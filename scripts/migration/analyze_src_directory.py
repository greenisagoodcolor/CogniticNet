#!/usr/bin/env python3
"""
Analyze src/ Directory Components and Map to Canonical Structure

This script analyzes the existing src/ directory and creates a mapping
to the canonical structure defined in ADR-002.

Architectural Compliance:
- Maps components according to docs/architecture/decisions/002-canonical-directory-structure.md
- Respects dependency inversion principle from docs/architecture/decisions/003-dependency-rules.md
- Follows naming conventions from docs/architecture/decisions/004-naming-conventions.md
"""

import os
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ComponentAnalysis:
    """Analysis of a single component in src/"""

    src_path: str
    canonical_path: str
    layer: str  # Core, Interface, Infrastructure, Supporting
    component_type: str  # module, package, script, config, test
    dependencies: List[str]
    imports: List[str]
    exports: List[str]
    description: str
    migration_priority: int  # 1-4 (Infrastructure first, Interface last)
    git_history_preserve: bool
    conflicts: List[str]  # Potential conflicts with existing files


@dataclass
class MigrationPlan:
    """Complete migration plan for src/ directory"""

    timestamp: str
    components: List[ComponentAnalysis]
    layer_summary: Dict[str, int]
    conflicts_summary: List[str]
    migration_order: List[str]
    validation_checks: List[str]


class SrcDirectoryAnalyzer:
    """Analyzer for src/ directory components"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.canonical_mapping = self._load_canonical_mapping()
        self.existing_files = self._scan_existing_files()

    def _load_canonical_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Load canonical structure mapping from ADR-002"""
        return {
            # Core Domain Layer (Business Logic)
            "agents": {
                "canonical_path": "agents/",
                "layer": "Core",
                "priority": 2,
                "description": "Agent implementations and behaviors",
            },
            "coalitions": {
                "canonical_path": "coalitions/",
                "layer": "Core",
                "priority": 2,
                "description": "Coalition formation and management",
            },
            "world": {
                "canonical_path": "world/",
                "layer": "Core",
                "priority": 2,
                "description": "World state and spatial management",
            },
            "inference": {
                "canonical_path": "inference/",
                "layer": "Core",
                "priority": 2,
                "description": "Active inference and GNN processing",
            },
            # Infrastructure Layer (External Dependencies)
            "database": {
                "canonical_path": "infrastructure/database/",
                "layer": "Infrastructure",
                "priority": 1,
                "description": "Database connections and models",
            },
            "hardware": {
                "canonical_path": "infrastructure/hardware/",
                "layer": "Infrastructure",
                "priority": 1,
                "description": "Hardware abstraction layer",
            },
            "deployment": {
                "canonical_path": "infrastructure/deployment/",
                "layer": "Infrastructure",
                "priority": 1,
                "description": "Deployment and packaging",
            },
            "export": {
                "canonical_path": "infrastructure/export/",
                "layer": "Infrastructure",
                "priority": 1,
                "description": "Export and serialization",
            },
            # Supporting Layer (Utilities and Shared)
            "models": {
                "canonical_path": "models/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Data models and schemas",
            },
            "learning": {
                "canonical_path": "learning/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Learning algorithms and pattern extraction",
            },
            "knowledge": {
                "canonical_path": "knowledge/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Knowledge management and graphs",
            },
            "monitoring": {
                "canonical_path": "monitoring/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Runtime monitoring and debugging",
            },
            "validation": {
                "canonical_path": "validation/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Validation and verification utilities",
            },
            "readiness": {
                "canonical_path": "readiness/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Readiness evaluation and health checks",
            },
            "simulation": {
                "canonical_path": "simulation/",
                "layer": "Supporting",
                "priority": 3,
                "description": "Simulation engine and management",
            },
            # Interface Layer (External Communication)
            "pipeline": {
                "canonical_path": "scripts/pipeline/",
                "layer": "Interface",
                "priority": 4,
                "description": "Processing pipelines and workflows",
            },
        }

    def _scan_existing_files(self) -> Set[str]:
        """Scan existing files in canonical locations"""
        existing = set()
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
            for file in files:
                if not file.startswith("."):
                    rel_path = os.path.relpath(
                        os.path.join(root, file), self.project_root
                    )
                    existing.add(rel_path)
        return existing

    def _analyze_python_file(self, file_path: Path) -> Tuple[List[str], List[str]]:
        """Analyze Python file for imports and exports"""
        imports = []
        exports = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    exports.append(node.name)
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            exports.append(target.id)

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

        return imports, exports

    def _detect_conflicts(self, canonical_path: str) -> List[str]:
        """Detect potential conflicts with existing files"""
        conflicts = []
        target_path = self.project_root / canonical_path

        if target_path.exists():
            conflicts.append(f"Target directory {canonical_path} already exists")

        # Check for specific file conflicts
        for existing_file in self.existing_files:
            if existing_file.startswith(canonical_path):
                conflicts.append(f"File conflict: {existing_file}")

        return conflicts

    def analyze_component(self, src_component: str) -> ComponentAnalysis:
        """Analyze a single component in src/"""
        src_component_path = self.src_path / src_component

        # Get mapping info
        mapping_info = self.canonical_mapping.get(
            src_component,
            {
                "canonical_path": f"unmapped/{src_component}/",
                "layer": "Unknown",
                "priority": 5,
                "description": f"Unmapped component: {src_component}",
            },
        )

        # Analyze files in component
        imports = []
        exports = []
        dependencies = []

        if src_component_path.exists():
            for root, dirs, files in os.walk(src_component_path):
                # Skip node_modules and hidden directories
                dirs[:] = [
                    d for d in dirs if not d.startswith(".") and d != "node_modules"
                ]

                for file in files:
                    if file.endswith(".py"):
                        file_path = Path(root) / file
                        file_imports, file_exports = self._analyze_python_file(
                            file_path
                        )
                        imports.extend(file_imports)
                        exports.extend(file_exports)

                        # Detect internal dependencies
                        for imp in file_imports:
                            if imp.startswith("src."):
                                dep_component = imp.split(".")[1]
                                if (
                                    dep_component != src_component
                                    and dep_component not in dependencies
                                ):
                                    dependencies.append(dep_component)

        # Determine component type
        component_type = "package"
        if src_component_path.is_file():
            component_type = "module"
        elif any(
            f.endswith(".py")
            for f in os.listdir(src_component_path)
            if os.path.isfile(src_component_path / f)
        ):
            component_type = "package"
        else:
            component_type = "directory"

        # Detect conflicts
        conflicts = self._detect_conflicts(mapping_info["canonical_path"])

        return ComponentAnalysis(
            src_path=f"src/{src_component}",
            canonical_path=mapping_info["canonical_path"],
            layer=mapping_info["layer"],
            component_type=component_type,
            dependencies=dependencies,
            imports=list(set(imports)),
            exports=list(set(exports)),
            description=mapping_info["description"],
            migration_priority=mapping_info["priority"],
            git_history_preserve=True,
            conflicts=conflicts,
        )

    def generate_migration_plan(self) -> MigrationPlan:
        """Generate complete migration plan"""
        components = []

        # Analyze each component in src/
        for item in os.listdir(self.src_path):
            item_path = self.src_path / item
            if (
                item_path.is_dir()
                and not item.startswith(".")
                and item != "node_modules"
            ):
                component = self.analyze_component(item)
                components.append(component)

        # Sort by migration priority (Infrastructure first)
        components.sort(key=lambda x: x.migration_priority)

        # Generate layer summary
        layer_summary = {}
        for component in components:
            layer_summary[component.layer] = layer_summary.get(component.layer, 0) + 1

        # Collect all conflicts
        conflicts_summary = []
        for component in components:
            conflicts_summary.extend(component.conflicts)

        # Generate migration order
        migration_order = [comp.src_path for comp in components]

        # Generate validation checks
        validation_checks = [
            "Verify all imports are updated",
            "Check dependency inversion compliance",
            "Validate architectural layer separation",
            "Confirm git history preservation",
            "Test all moved components",
            "Update documentation references",
        ]

        return MigrationPlan(
            timestamp=datetime.now().isoformat(),
            components=components,
            layer_summary=layer_summary,
            conflicts_summary=list(set(conflicts_summary)),
            migration_order=migration_order,
            validation_checks=validation_checks,
        )

    def save_analysis(self, plan: MigrationPlan, output_file: Path):
        """Save analysis to JSON file"""
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(plan), f, indent=2, default=str)

        print(f"Analysis saved to {output_file}")

    def print_summary(self, plan: MigrationPlan):
        """Print analysis summary"""
        print("\n" + "=" * 80)
        print("SRC DIRECTORY MIGRATION ANALYSIS")
        print("=" * 80)

        print(f"\nTimestamp: {plan.timestamp}")
        print(f"Total Components: {len(plan.components)}")

        print("\nLayer Distribution:")
        for layer, count in plan.layer_summary.items():
            print(f"  {layer}: {count} components")

        print("\nMigration Order (by priority):")
        for i, component in enumerate(plan.components, 1):
            print(f"  {i}. {component.src_path} -> {component.canonical_path}")
            print(
                f"     Layer: {component.layer}, Priority: {component.migration_priority}"
            )
            if component.conflicts:
                print(f"     ⚠️  Conflicts: {len(component.conflicts)}")

        if plan.conflicts_summary:
            print(f"\n⚠️  CONFLICTS DETECTED ({len(plan.conflicts_summary)}):")
            for conflict in plan.conflicts_summary[:10]:  # Show first 10
                print(f"  - {conflict}")
            if len(plan.conflicts_summary) > 10:
                print(f"  ... and {len(plan.conflicts_summary) - 10} more")

        print("\nValidation Checklist:")
        for check in plan.validation_checks:
            print(f"  □ {check}")

        print("\n" + "=" * 80)


def main():
    """Main execution function"""
    project_root = Path(__file__).parent.parent.parent
    analyzer = SrcDirectoryAnalyzer(project_root)

    print("Analyzing src/ directory components...")
    plan = analyzer.generate_migration_plan()

    # Save analysis
    output_file = project_root / "scripts" / "migration" / "src_migration_analysis.json"
    analyzer.save_analysis(plan, output_file)

    # Print summary
    analyzer.print_summary(plan)

    print(f"\nDetailed analysis saved to: {output_file}")
    print("Next steps:")
    print("1. Review conflicts and resolve them")
    print("2. Run migration script with git history preservation")
    print("3. Update all import statements")
    print("4. Validate architectural compliance")


if __name__ == "__main__":
    main()
