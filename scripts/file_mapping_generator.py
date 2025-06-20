#!/usr/bin/env python3
"""
File Mapping Generator for FreeAgentics Canonical Structure

This script analyzes the current directory structure and generates a mapping
of files to their correct locations according to ADR-002 (Canonical Directory Structure).

Usage:
    python scripts/file-mapping-generator.py [--output mapping.json] [--dry-run]
"""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class FileMapping:
    """Represents a file movement mapping."""

    current_path: str
    target_path: str
    reason: str
    layer: str
    priority: int  # 1=critical, 2=important, 3=optional
    dependencies: List[str]


class FileMapperAnalyzer:
    """Analyzes current file structure and generates canonical mappings."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.mappings: List[FileMapping] = []

        # Define canonical layers per ADR-002
        self.domain_dirs = {"agents", "inference", "coalitions", "world"}
        self.interface_dirs = {"api", "web"}
        self.infrastructure_dirs = {"infrastructure", "config", "data"}
        self.documentation_dirs = {"docs"}
        self.testing_dirs = {"tests"}

        # Files that should be in root
        self.root_files = {
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "CONTRIBUTING.md",
            "GOVERNANCE.md",
            "SECURITY.md",
            ".gitignore",
            ".gitattributes",
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "Makefile",
            "package.json",
            "pyproject.toml",
            "requirements.txt",
            "requirements-dev.txt",
            "setup.py",
            "setup.cfg",
        }

        # Configuration files that should be in config/
        self.config_files = {
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintignore",
            ".prettierrc.js",
            ".prettierrc.json",
            ".prettierignore",
            ".editorconfig",
            ".coveragerc",
            ".lintstagedrc.js",
            ".markdownlint.json",
            ".size-limit.json",
            "tailwind.config.ts",
            "tailwind.config.js",
            "next.config.js",
            "next.config.ts",
            "next-env.d.ts",
            "tsconfig.json",
            "tsconfig.build.json",
            "vite.config.ts",
            "jest.config.js",
            "jest.config.ts",
            "vitest.config.ts",
        }

        # Hidden/system directories to ignore
        self.ignore_dirs = {
            ".git",
            ".github",
            ".vscode",
            ".cursor",
            ".roo",
            ".claude",
            "node_modules",
            ".next",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".ci_output",
            ".test_reports",
            ".test_configs",
            ".repository_analysis",
            ".taskmaster",
            ".husky",
        }

    def analyze_project(self) -> List[FileMapping]:
        """Analyze project structure and generate file mappings."""
        print("🔍 Analyzing project structure for file mappings...")

        # Analyze each directory/file in project root
        for item in self.project_root.iterdir():
            if item.name.startswith(".") and item.name in self.ignore_dirs:
                continue

            if item.is_file():
                self._analyze_root_file(item)
            elif item.is_dir():
                self._analyze_directory(item)

        # Sort mappings by priority (critical first)
        self.mappings.sort(key=lambda m: (m.priority, m.current_path))

        print(f"✅ Analysis complete. Found {len(self.mappings)} files to move.")
        return self.mappings

    def _analyze_root_file(self, file_path: Path):
        """Analyze a root-level file for potential movement."""
        filename = file_path.name

        # Config files should move to config/
        if filename in self.config_files:
            self.mappings.append(
                FileMapping(
                    current_path=str(file_path.relative_to(self.project_root)),
                    target_path=f"config/{filename}",
                    reason="Configuration file should be in config/ directory per ADR-002",
                    layer="infrastructure",
                    priority=2,
                    dependencies=[],
                )
            )

        # Check for misplaced scripts or utilities
        elif filename.endswith(".py") and filename not in self.root_files:
            self.mappings.append(
                FileMapping(
                    current_path=str(file_path.relative_to(self.project_root)),
                    target_path=f"scripts/{filename}",
                    reason="Python utility script should be in scripts/ directory",
                    layer="infrastructure",
                    priority=3,
                    dependencies=[],
                )
            )

    def _analyze_directory(self, dir_path: Path):
        """Analyze a directory for canonical compliance."""
        dirname = dir_path.name

        # Check if directory is already in correct layer
        if dirname in (
            self.domain_dirs
            | self.interface_dirs
            | self.infrastructure_dirs
            | self.documentation_dirs
            | self.testing_dirs
        ):
            # Directory is correctly placed, check internal structure
            self._analyze_directory_contents(dir_path)
            return

        # Handle special cases
        if dirname == "data":
            self._move_data_directory(dir_path)
        elif dirname == "scripts":
            self._analyze_scripts_directory(dir_path)
        elif dirname == "__mocks__":
            self._move_directory(
                dir_path,
                "tests/__mocks__",
                "Mock files should be in tests/ directory",
                2,
            )
        else:
            # Unknown directory - needs manual review
            print(f"⚠️  Unknown directory: {dirname} - requires manual review")

    def _analyze_directory_contents(self, dir_path: Path):
        """Analyze contents of correctly placed directories."""
        # For now, assume internal structure is correct
        # Could add more sophisticated analysis here
        pass

    def _move_data_directory(self, dir_path: Path):
        """Move data directory to infrastructure layer."""
        for item in dir_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(self.project_root)
                new_path = Path("infrastructure") / relative_path

                self.mappings.append(
                    FileMapping(
                        current_path=str(relative_path),
                        target_path=str(new_path),
                        reason="Data files belong in infrastructure layer per ADR-002",
                        layer="infrastructure",
                        priority=2,
                        dependencies=[],
                    )
                )

    def _analyze_scripts_directory(self, dir_path: Path):
        """Analyze scripts directory for proper organization."""
        for item in dir_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(self.project_root)

                # Deployment scripts should be in infrastructure
                if "deployment" in str(item) or "setup" in str(item):
                    new_path = Path("infrastructure/scripts") / item.relative_to(
                        dir_path
                    )

                    self.mappings.append(
                        FileMapping(
                            current_path=str(relative_path),
                            target_path=str(new_path),
                            reason="Deployment/setup scripts belong in infrastructure layer",
                            layer="infrastructure",
                            priority=2,
                            dependencies=[],
                        )
                    )

    def _move_directory(
        self, dir_path: Path, target_base: str, reason: str, priority: int
    ):
        """Move entire directory to new location."""
        for item in dir_path.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(self.project_root)
                relative_to_dir = item.relative_to(dir_path)
                new_path = Path(target_base) / relative_to_dir

                self.mappings.append(
                    FileMapping(
                        current_path=str(relative_path),
                        target_path=str(new_path),
                        reason=reason,
                        layer=self._determine_layer(target_base),
                        priority=priority,
                        dependencies=[],
                    )
                )

    def _determine_layer(self, path: str) -> str:
        """Determine which architectural layer a path belongs to."""
        first_part = path.split("/")[0]

        if first_part in self.domain_dirs:
            return "domain"
        elif first_part in self.interface_dirs:
            return "interface"
        elif first_part in self.infrastructure_dirs:
            return "infrastructure"
        elif first_part in self.documentation_dirs:
            return "documentation"
        elif first_part in self.testing_dirs:
            return "testing"
        else:
            return "unknown"

    def generate_report(self) -> Dict:
        """Generate a comprehensive report of the mapping analysis."""
        layer_stats = {}
        priority_stats = {}

        for mapping in self.mappings:
            # Layer statistics
            layer = mapping.layer
            if layer not in layer_stats:
                layer_stats[layer] = 0
            layer_stats[layer] += 1

            # Priority statistics
            priority = mapping.priority
            if priority not in priority_stats:
                priority_stats[priority] = 0
            priority_stats[priority] += 1

        return {
            "summary": {
                "total_files_to_move": len(self.mappings),
                "layer_distribution": layer_stats,
                "priority_distribution": priority_stats,
            },
            "mappings": [asdict(mapping) for mapping in self.mappings],
            "layers": {
                "domain": list(self.domain_dirs),
                "interface": list(self.interface_dirs),
                "infrastructure": list(self.infrastructure_dirs),
                "documentation": list(self.documentation_dirs),
                "testing": list(self.testing_dirs),
            },
        }


def main():
    parser = argparse.ArgumentParser(
        description="Generate file mapping for canonical directory structure"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="file-mapping.json",
        help="Output file for mapping data (default: file-mapping.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate mapping without creating output file",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Analyze project structure
    analyzer = FileMapperAnalyzer(args.project_root)
    mappings = analyzer.analyze_project()

    # Generate report
    report = analyzer.generate_report()

    # Print summary
    print("\n📊 File Mapping Summary:")
    print(f"   Total files to move: {report['summary']['total_files_to_move']}")
    print(f"   Layer distribution: {report['summary']['layer_distribution']}")
    print(f"   Priority distribution: {report['summary']['priority_distribution']}")

    # Print sample mappings
    if mappings:
        print("\n📝 Sample mappings:")
        for mapping in mappings[:5]:
            print(f"   {mapping.current_path} → {mapping.target_path}")
            print(f"      Reason: {mapping.reason}")

        if len(mappings) > 5:
            print(f"   ... and {len(mappings) - 5} more")

    # Save results
    if not args.dry_run:
        output_path = Path(args.output)
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\n💾 Mapping saved to: {output_path}")
        print("Next steps:")
        print("1. Review the mapping file")
        print("2. Run file movement script")
        print("3. Update import statements")
        print("4. Test and commit changes")


if __name__ == "__main__":
    main()
