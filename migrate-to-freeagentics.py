#!/usr/bin/env python3
"""
FreeAgentics Migration Script
Preserves git history while transforming FreeAgentics to FreeAgentics structure
Lead: Martin Fowler
"""

import os
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import sys

class MigrationManager:
    def __init__(self, source_dir: str = ".", target_dir: str = "freeagentics_new", dry_run: bool = False):
        self.source_dir = Path(source_dir).absolute()
        self.target_dir = Path(target_dir).absolute()
        self.dry_run = dry_run
        self.migration_log = []
        self.error_log = []

    def log(self, message: str):
        """Log migration activity"""
        print(f"[MIGRATE] {message}")
        self.migration_log.append(message)

    def error(self, message: str):
        """Log errors"""
        print(f"[ERROR] {message}", file=sys.stderr)
        self.error_log.append(message)

    def git_mv(self, source: str, dest: str) -> bool:
        """Execute git mv command with error handling"""
        try:
            if self.dry_run:
                self.log(f"DRY RUN: git mv {source} {dest}")
                return True

            # Ensure destination directory exists
            dest_dir = os.path.dirname(dest)
            if dest_dir:
                os.makedirs(dest_dir, exist_ok=True)

            result = subprocess.run(
                ["git", "mv", source, dest],
                capture_output=True,
                text=True,
                check=True
            )
            self.log(f"Moved: {source} → {dest}")
            return True
        except subprocess.CalledProcessError as e:
            self.error(f"Failed to move {source}: {e.stderr}")
            return False

    def get_migration_mappings(self) -> Dict[str, str]:
        """Define file migration mappings from old to new structure"""
        mappings = {
            # Agent files
            "src/agents/basic_agent": "agents/base",
            "src/agents/active_inference": "inference/engine",
            "src/agents/agents.base.communication.py": "agents/base/communication.py",

            # Active Inference
            "src/agents/active_inference/inference.py": "inference/engine/active-inference.py",
            "src/agents/active_inference/belief_update.py": "inference/engine/belief-update.py",
            "src/agents/active_inference/policy_learning.py": "inference/engine/policy-selection.py",

            # GNN
            "src/gnn": "inference/gnn",

            # Coalition
            "src/agents/coalition": "coalitions/formation",
            "src/agents/coalition/coalition_criteria.py": "coalitions/formation/preference-matching.py",
            "src/agents/coalition/business_opportunities.py": "coalitions/contracts/resource-sharing.py",

            # World
            "src/world/h3_world.py": "world/grid/hex-world.py",
            "src/spatial/spatial_api.py": "world/grid/spatial-index.py",

            # API Routes
            "app/api": "api/rest",

            # Frontend components
            "app/components": "web/src/components",
            "src/hooks": "web/src/hooks",
            "src/lib": "web/src/lib",
            "src/contexts": "web/src/contexts",

            # Infrastructure
            "environments/demo/docker-compose.yml": "infrastructure/docker/docker-compose.yml",
            "environments/demo/Dockerfile.web": "infrastructure/docker/Dockerfile.web",

            # Configuration
            "environments": "config/environments",

            # Tests
            "src/tests": "tests",

            # Documentation
            "doc": "docs",

            # Scripts
            "scripts/freeagentics-cli.js": "scripts/freeagentics-cli.js",
        }

        return mappings

    def rename_references(self, file_path: str):
        """Update references from FreeAgentics to FreeAgentics in file content"""
        if not os.path.exists(file_path):
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace various forms of the old name
            replacements = [
                ("FreeAgentics", "FreeAgentics"),
                ("freeagentics", "freeagentics"),
                ("freeagentics", "freeagentics"),  # Fix typo variant
                ("FREEAGENTICS", "FREEAGENTICS"),
            ]

            modified = False
            for old, new in replacements:
                if old in content:
                    content = content.replace(old, new)
                    modified = True

            if modified and not self.dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"Updated references in: {file_path}")

        except Exception as e:
            self.error(f"Failed to update references in {file_path}: {e}")

    def create_migration_stages(self) -> List[Dict[str, List[Tuple[str, str]]]]:
        """Define migration stages for controlled execution"""
        stages = [
            {
                "name": "Stage 1: Core Agent Structure",
                "migrations": [
                    ("src/agents/basic_agent", "agents/base"),
                    ("src/agents/explorer", "agents/explorer"),
                    ("src/agents/merchant", "agents/merchant"),
                    ("src/agents/scholar", "agents/scholar"),
                    ("src/agents/guardian", "agents/guardian"),
                ]
            },
            {
                "name": "Stage 2: Active Inference Engine",
                "migrations": [
                    ("src/agents/active_inference", "inference/engine"),
                    ("src/gnn", "inference/gnn"),
                    ("src/llm", "inference/llm"),
                ]
            },
            {
                "name": "Stage 3: Coalition & World",
                "migrations": [
                    ("src/agents/coalition", "coalitions"),
                    ("src/world", "world"),
                    ("src/spatial", "world/spatial"),
                ]
            },
            {
                "name": "Stage 4: API & Frontend",
                "migrations": [
                    ("app/api", "api/rest"),
                    ("app/components", "web/src/components"),
                    ("src/hooks", "web/src/hooks"),
                    ("src/lib", "web/src/lib"),
                ]
            },
            {
                "name": "Stage 5: Infrastructure & Config",
                "migrations": [
                    ("environments", "config/environments"),
                    ("src/database", "data/database"),
                    ("src/tests", "tests"),
                    ("doc", "docs"),
                ]
            }
        ]

        return stages

    def execute_migration(self):
        """Execute the migration in stages"""
        self.log("Starting FreeAgentics migration...")

        # Create git tag for rollback
        if not self.dry_run:
            try:
                subprocess.run(["git", "tag", "pre-freeagentics-migration"], check=True)
                self.log("Created rollback tag: pre-freeagentics-migration")
            except:
                self.log("Tag already exists or git not initialized")

        stages = self.create_migration_stages()

        for stage_num, stage in enumerate(stages, 1):
            self.log(f"\n{stage['name']}")
            self.log("-" * 50)

            for source, dest in stage['migrations']:
                if os.path.exists(source):
                    self.git_mv(source, dest)
                else:
                    self.log(f"Skipping (not found): {source}")

            # Create stage checkpoint
            if not self.dry_run:
                try:
                    subprocess.run([
                        "git", "commit", "-m",
                        f"Migration {stage['name']}"
                    ], check=True)
                    self.log(f"Committed {stage['name']}")
                except:
                    self.log("Nothing to commit for this stage")

        # Update all file references
        self.log("\nUpdating file references...")
        if not self.dry_run:
            for root, dirs, files in os.walk("."):
                # Skip .git and node_modules
                if '.git' in root or 'node_modules' in root:
                    continue

                for file in files:
                    if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx', '.md', '.yml', '.yaml', '.json')):
                        file_path = os.path.join(root, file)
                        self.rename_references(file_path)

        self.log("\nMigration complete!")
        self.save_migration_report()

    def save_migration_report(self):
        """Save migration report"""
        report = {
            "migration_log": self.migration_log,
            "error_log": self.error_log,
            "timestamp": str(Path.ctime(Path.cwd())),
            "dry_run": self.dry_run
        }

        report_path = "MIGRATION_REPORT.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.log(f"Migration report saved to: {report_path}")

def main():
    parser = argparse.ArgumentParser(description="Migrate FreeAgentics to FreeAgentics structure")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without making changes")
    parser.add_argument("--source", default=".", help="Source directory")
    parser.add_argument("--target", default="freeagentics_new", help="Target directory")

    args = parser.parse_args()

    migrator = MigrationManager(
        source_dir=args.source,
        target_dir=args.target,
        dry_run=args.dry_run
    )

    migrator.execute_migration()

if __name__ == "__main__":
    main()
