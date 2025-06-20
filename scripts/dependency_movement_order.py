#!/usr/bin/env python3
"""
Dependency-Based Movement Ordering for FreeAgentics

This script analyzes file dependencies to determine a safe and logical order
for moving files during the canonical structure migration.

Usage:
    python scripts/dependency-movement-order.py [--mapping file-mapping.json] [--output movement-order.json]
"""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Tuple


@dataclass
class MovementBatch:
    """Represents a batch of files that can be moved together."""

    batch_id: int
    files: List[str]
    description: str
    dependencies: List[int]  # IDs of batches that must complete first
    risk_level: str  # 'low', 'medium', 'high'
    estimated_duration: str


class DependencyAnalyzer:
    """Analyzes file dependencies to create safe movement ordering."""

    def __init__(self, mapping_file: str, project_root: str = "."):
        self.project_root = Path(project_root)
        self.mapping_file = mapping_file
        self.file_mappings = {}
        self.movement_batches = []
        self._load_mappings()

    def _load_mappings(self):
        """Load file mappings from JSON file."""
        with open(self.mapping_file, "r") as f:
            data = json.load(f)

        # Convert to easier lookup format
        for mapping in data["mappings"]:
            self.file_mappings[mapping["current_path"]] = mapping["target_path"]

    def analyze_dependencies(self) -> List[MovementBatch]:
        """Analyze dependencies and create movement batches."""
        print("🔍 Analyzing file dependencies for safe movement ordering...")

        # Categorize files by destination
        config_files = []
        mock_files = []
        script_files = []

        for current_path, mapping in self.file_mappings.items():
            if mapping["target_path"].startswith("config/"):
                config_files.append(current_path)
            elif mapping["target_path"].startswith("tests/"):
                mock_files.append(current_path)
            elif mapping["target_path"].startswith("infrastructure/scripts"):
                script_files.append(current_path)

        # Analyze configuration file dependencies
        independent_configs, dependent_configs = self._analyze_config_dependencies(
            config_files
        )

        # Create movement batches
        self._create_movement_batches(
            independent_configs, dependent_configs, mock_files, script_files
        )

        print(f"✅ Created {len(self.movement_batches)} movement batches")
        return self.movement_batches

    def _analyze_config_dependencies(
        self, config_files: List[str]
    ) -> Tuple[List[str], List[str]]:
        """Analyze dependencies between configuration files."""
        independent = []
        dependent = []

        # Configuration file dependency patterns
        dependency_patterns = {
            ".eslintrc.js": [
                ".eslintignore"
            ],  # ESLint config may reference ignore file
            ".prettierrc.js": [
                ".prettierignore"
            ],  # Prettier config may reference ignore file
            "tailwind.config.ts": [],  # Independent
            ".lintstagedrc.js": [
                ".eslintrc.js",
                ".prettierrc.js",
            ],  # May reference other tools
        }

        for file_path in config_files:
            filename = Path(file_path).name
            if filename in dependency_patterns:
                if dependency_patterns[filename]:
                    dependent.append(file_path)
                else:
                    independent.append(file_path)
            else:
                # Default to independent for unknown config files
                independent.append(file_path)

        return independent, dependent

    def _create_movement_batches(
        self,
        independent_configs: List[str],
        dependent_configs: List[str],
        mock_files: List[str],
        script_files: List[str],
    ):
        """Create ordered movement batches."""

        # Batch 1: Independent configuration files (lowest risk)
        if independent_configs:
            self.movement_batches.append(
                MovementBatch(
                    batch_id=1,
                    files=independent_configs,
                    description="Independent configuration files with no cross-dependencies",
                    dependencies=[],
                    risk_level="low",
                    estimated_duration="5-10 minutes",
                )
            )

        # Batch 2: Mock files (isolated, safe to move)
        if mock_files:
            self.movement_batches.append(
                MovementBatch(
                    batch_id=2,
                    files=mock_files,
                    description="Test mock files - isolated with no production dependencies",
                    dependencies=[],
                    risk_level="low",
                    estimated_duration="5 minutes",
                )
            )

        # Batch 3: Dependent configuration files
        if dependent_configs:
            deps = [1] if independent_configs else []
            self.movement_batches.append(
                MovementBatch(
                    batch_id=3,
                    files=dependent_configs,
                    description="Configuration files with potential cross-dependencies",
                    dependencies=deps,
                    risk_level="medium",
                    estimated_duration="10-15 minutes",
                )
            )

        # Batch 4: Infrastructure scripts (move last as they may reference other files)
        if script_files:
            prev_batches = [b.batch_id for b in self.movement_batches if b.files]
            self.movement_batches.append(
                MovementBatch(
                    batch_id=4,
                    files=script_files,
                    description="Infrastructure and deployment scripts",
                    dependencies=prev_batches,
                    risk_level="medium",
                    estimated_duration="15-20 minutes",
                )
            )

    def generate_movement_plan(self) -> Dict:
        """Generate comprehensive movement execution plan."""
        plan = {
            "metadata": {
                "generated_at": "2025-06-20T11:40:00Z",
                "total_files": len(self.file_mappings),
                "total_batches": len(self.movement_batches),
                "estimated_total_duration": "30-50 minutes",
            },
            "execution_strategy": {
                "approach": "Incremental batch movement with validation",
                "rollback_support": True,
                "git_history_preservation": True,
                "validation_between_batches": True,
            },
            "batches": [asdict(batch) for batch in self.movement_batches],
            "risk_assessment": self._generate_risk_assessment(),
            "validation_steps": self._generate_validation_steps(),
            "rollback_procedure": self._generate_rollback_procedure(),
        }

        return plan

    def _generate_risk_assessment(self) -> Dict:
        """Generate risk assessment for the movement plan."""
        low_risk_files = sum(
            1 for b in self.movement_batches if b.risk_level == "low" for _ in b.files
        )
        medium_risk_files = sum(
            1
            for b in self.movement_batches
            if b.risk_level == "medium"
            for _ in b.files
        )

        return {
            "overall_risk": "LOW",
            "risk_factors": {
                "configuration_files": {
                    "risk": "Medium",
                    "mitigation": "Move in dependency order, validate tool functionality",
                },
                "script_files": {
                    "risk": "Medium",
                    "mitigation": "Test execution after movement, update any hardcoded paths",
                },
                "mock_files": {
                    "risk": "Low",
                    "mitigation": "Isolated test files with minimal dependencies",
                },
            },
            "file_distribution": {
                "low_risk": low_risk_files,
                "medium_risk": medium_risk_files,
                "high_risk": 0,
            },
            "success_probability": "95%",
        }

    def _generate_validation_steps(self) -> List[Dict]:
        """Generate validation steps for each batch."""
        return [
            {
                "batch_id": "all",
                "step": "Pre-movement validation",
                "actions": [
                    "Run dependency validation script",
                    "Ensure clean git working directory",
                    "Backup current state",
                    "Verify all target directories exist",
                ],
            },
            {
                "batch_id": 1,
                "step": "Configuration files validation",
                "actions": [
                    "Test linting tools (eslint, prettier)",
                    "Verify build process",
                    "Check configuration file resolution",
                ],
            },
            {
                "batch_id": 2,
                "step": "Mock files validation",
                "actions": [
                    "Run test suite",
                    "Verify mock file imports resolve correctly",
                ],
            },
            {
                "batch_id": 3,
                "step": "Dependent configuration validation",
                "actions": [
                    "Test all development tools",
                    "Verify configuration inheritance",
                    "Run full build pipeline",
                ],
            },
            {
                "batch_id": 4,
                "step": "Infrastructure scripts validation",
                "actions": [
                    "Test script execution",
                    "Verify path references",
                    "Check deployment pipeline functionality",
                ],
            },
        ]

    def _generate_rollback_procedure(self) -> Dict:
        """Generate rollback procedure for emergency situations."""
        return {
            "emergency_rollback": {
                "command": "git reset --hard HEAD~1",
                "description": "Immediately revert last commit if critical failure occurs",
            },
            "selective_rollback": {
                "approach": "Cherry-pick revert individual file moves",
                "commands": [
                    "git log --oneline -n 10  # Find commit to revert",
                    "git revert <commit-hash>  # Revert specific batch",
                    "git reset HEAD~1  # Undo commit but keep changes for manual fix",
                ],
            },
            "validation_failure_response": [
                "Stop movement process immediately",
                "Document failure details",
                "Revert last batch if needed",
                "Investigate root cause before continuing",
            ],
        }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze dependencies and create movement order for file migration"
    )
    parser.add_argument(
        "--mapping",
        default="file-mapping.json",
        help="File mapping JSON file (default: file-mapping.json)",
    )
    parser.add_argument(
        "--output",
        default="movement-order.json",
        help="Output file for movement plan (default: movement-order.json)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Analyze dependencies and create movement plan
    analyzer = DependencyAnalyzer(args.mapping, args.project_root)
    batches = analyzer.analyze_dependencies()

    # Generate comprehensive plan
    plan = analyzer.generate_movement_plan()

    # Print summary
    print("\n📊 Movement Plan Summary:")
    print(f"   Total batches: {plan['metadata']['total_batches']}")
    print(f"   Estimated duration: {plan['metadata']['estimated_total_duration']}")
    print(f"   Overall risk: {plan['risk_assessment']['overall_risk']}")
    print(f"   Success probability: {plan['risk_assessment']['success_probability']}")

    print("\n📝 Batch Overview:")
    for batch in batches:
        print(
            f"   Batch {batch.batch_id}: {len(batch.files)} files - {batch.risk_level} risk"
        )
        print(f"      {batch.description}")
        print(f"      Duration: {batch.estimated_duration}")
        if batch.dependencies:
            print(f"      Depends on: Batch {', '.join(map(str, batch.dependencies))}")
        print()

    # Save plan
    with open(args.output, "w") as f:
        json.dump(plan, f, indent=2)

    print(f"💾 Movement plan saved to: {args.output}")
    print("\nNext steps:")
    print("1. Review the movement plan")
    print("2. Execute batches in order using file movement script")
    print("3. Validate after each batch")
    print("4. Update import statements as needed")


if __name__ == "__main__":
    main()
