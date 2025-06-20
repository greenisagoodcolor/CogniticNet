#!/usr/bin/env python3
"""
Migrate src/ Directory to Canonical Structure

This script migrates components from src/ directory to the canonical structure
with git history preservation and intelligent conflict resolution.

Architectural Compliance:
- Follows migration plan from src_migration_analysis.json
- Preserves git history using git mv commands
- Respects dependency inversion principle
- Handles conflicts intelligently
"""

import os
import json
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass


@dataclass
class MigrationResult:
    """Result of a single component migration"""

    component: str
    src_path: str
    dest_path: str
    success: bool
    git_preserved: bool
    conflicts_resolved: List[str]
    errors: List[str]


class SrcMigrator:
    """Handles migration of src/ directory components"""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.migration_plan = self._load_migration_plan()
        self.results: List[MigrationResult] = []

    def _load_migration_plan(self) -> Dict[str, Any]:
        """Load migration plan from analysis"""
        plan_file = (
            self.project_root / "scripts" / "migration" / "src_migration_analysis.json"
        )
        if not plan_file.exists():
            raise FileNotFoundError(f"Migration plan not found: {plan_file}")

        with open(plan_file, "r") as f:
            return json.load(f)

    def _run_git_command(
        self, cmd: List[str], cwd: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """Run git command and return success status and output"""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would run: {' '.join(cmd)}")
                return True, "dry run"

            result = subprocess.run(
                cmd,
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()

    def _ensure_directory_exists(self, path: Path) -> bool:
        """Ensure directory exists, create if necessary"""
        try:
            if self.dry_run:
                print(f"[DRY RUN] Would create directory: {path}")
                return True

            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {path}: {e}")
            return False

    def _resolve_agents_conflict(
        self, src_path: Path, dest_path: Path
    ) -> Tuple[bool, List[str], List[str]]:
        """Resolve conflicts with existing agents/ directory"""
        conflicts_resolved = []
        errors = []

        # Strategy: Merge src/agents into existing agents/ structure
        # src/agents/active_inference.py -> agents/core/active_inference.py
        # src/agents/movement_perception.py -> agents/core/movement_perception.py
        # src/agents/testing/ -> agents/testing/

        try:
            # Create agents/core/ directory for src/agents modules
            core_dir = dest_path / "core"
            if not self._ensure_directory_exists(core_dir):
                errors.append(f"Failed to create {core_dir}")
                return False, conflicts_resolved, errors

            # Move Python files to agents/core/
            for item in src_path.iterdir():
                if (
                    item.is_file()
                    and item.suffix == ".py"
                    and item.name != "__init__.py"
                ):
                    dest_file = core_dir / item.name
                    success, output = self._run_git_command(
                        ["git", "mv", str(item), str(dest_file)]
                    )
                    if success:
                        conflicts_resolved.append(f"Moved {item.name} to agents/core/")
                    else:
                        errors.append(f"Failed to move {item.name}: {output}")

            # Handle testing directory
            testing_src = src_path / "testing"
            if testing_src.exists():
                testing_dest = dest_path / "testing"
                if testing_dest.exists():
                    # Merge testing directories
                    for item in testing_src.iterdir():
                        if item.is_file():
                            dest_file = testing_dest / f"src_{item.name}"
                            success, output = self._run_git_command(
                                ["git", "mv", str(item), str(dest_file)]
                            )
                            if success:
                                conflicts_resolved.append(
                                    f"Merged {item.name} into existing testing/"
                                )
                            else:
                                errors.append(f"Failed to merge {item.name}: {output}")
                else:
                    # Move entire testing directory
                    success, output = self._run_git_command(
                        ["git", "mv", str(testing_src), str(testing_dest)]
                    )
                    if success:
                        conflicts_resolved.append("Moved testing/ directory")
                    else:
                        errors.append(f"Failed to move testing/: {output}")

            # Handle __init__.py files
            init_src = src_path / "__init__.py"
            if init_src.exists():
                init_dest = core_dir / "__init__.py"
                success, output = self._run_git_command(
                    ["git", "mv", str(init_src), str(init_dest)]
                )
                if success:
                    conflicts_resolved.append("Moved __init__.py to agents/core/")
                else:
                    errors.append(f"Failed to move __init__.py: {output}")

            return True, conflicts_resolved, errors

        except Exception as e:
            errors.append(f"Exception during agents conflict resolution: {e}")
            return False, conflicts_resolved, errors

    def _migrate_component(self, component: Dict[str, Any]) -> MigrationResult:
        """Migrate a single component"""
        src_path = Path(component["src_path"])
        canonical_path = component["canonical_path"]

        # Convert canonical path to actual destination
        dest_path = self.project_root / canonical_path

        print(f"\n{'='*60}")
        print(f"Migrating: {src_path} -> {canonical_path}")
        print(
            f"Layer: {component['layer']}, Priority: {component['migration_priority']}"
        )

        conflicts_resolved = []
        errors = []
        git_preserved = False

        # Check if source exists
        full_src_path = self.project_root / src_path
        if not full_src_path.exists():
            errors.append(f"Source path does not exist: {full_src_path}")
            return MigrationResult(
                component=component["src_path"],
                src_path=str(src_path),
                dest_path=str(canonical_path),
                success=False,
                git_preserved=False,
                conflicts_resolved=conflicts_resolved,
                errors=errors,
            )

        # Handle special case: agents directory with conflicts
        if src_path.name == "agents" and len(component["conflicts"]) > 0:
            print("⚠️  Resolving agents directory conflicts...")
            success, resolved, errs = self._resolve_agents_conflict(
                full_src_path, dest_path
            )
            conflicts_resolved.extend(resolved)
            errors.extend(errs)

            if success:
                # Remove empty src/agents directory
                try:
                    if not self.dry_run and full_src_path.exists():
                        # Check if directory is empty
                        if not any(full_src_path.iterdir()):
                            full_src_path.rmdir()
                            conflicts_resolved.append(
                                "Removed empty src/agents directory"
                            )
                        else:
                            print(f"Warning: {full_src_path} not empty after migration")
                except Exception as e:
                    errors.append(f"Failed to remove empty src/agents: {e}")

            git_preserved = success

        else:
            # Standard migration for other components
            # Ensure destination directory exists
            dest_parent = dest_path.parent
            if not self._ensure_directory_exists(dest_parent):
                errors.append(f"Failed to create destination parent: {dest_parent}")
                return MigrationResult(
                    component=component["src_path"],
                    src_path=str(src_path),
                    dest_path=str(canonical_path),
                    success=False,
                    git_preserved=False,
                    conflicts_resolved=conflicts_resolved,
                    errors=errors,
                )

            # Use git mv to preserve history
            success, output = self._run_git_command(
                ["git", "mv", str(full_src_path), str(dest_path)]
            )

            if success:
                conflicts_resolved.append(
                    f"Successfully moved {src_path} to {canonical_path}"
                )
                git_preserved = True
            else:
                errors.append(f"Git mv failed: {output}")

                # Fallback: try regular move
                try:
                    if not self.dry_run:
                        if dest_path.exists():
                            shutil.rmtree(dest_path)
                        shutil.move(str(full_src_path), str(dest_path))
                        conflicts_resolved.append(
                            "Fallback move successful (no git history)"
                        )
                        git_preserved = False
                    else:
                        print(
                            f"[DRY RUN] Would fallback move {full_src_path} to {dest_path}"
                        )
                        git_preserved = False
                except Exception as e:
                    errors.append(f"Fallback move failed: {e}")

        success = len(errors) == 0

        # Print results
        if success:
            print("✅ Migration successful")
            for resolution in conflicts_resolved:
                print(f"   ✓ {resolution}")
        else:
            print("❌ Migration failed")
            for error in errors:
                print(f"   ✗ {error}")

        return MigrationResult(
            component=component["src_path"],
            src_path=str(src_path),
            dest_path=str(canonical_path),
            success=success,
            git_preserved=git_preserved,
            conflicts_resolved=conflicts_resolved,
            errors=errors,
        )

    def _update_imports_in_file(self, file_path: Path) -> List[str]:
        """Update import statements in a Python file"""
        updates = []

        if not file_path.suffix == ".py":
            return updates

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Update src.* imports to new locations
            import_mappings = {
                "infrastructure.database": "infrastructure.database",
                "infrastructure.hardware": "infrastructure.hardware",
                "infrastructure.deployment": "infrastructure.deployment",
                "infrastructure.export": "infrastructure.export",
                "agents.core": "agents.core",  # Special case
                "learning": "learning",
                "simulation": "simulation",
                "models": "models",
                "knowledge": "knowledge",
                "readiness": "readiness",
                "monitoring": "monitoring",
                "validation": "validation",
                "scripts.pipeline": "scripts.pipeline",
            }

            for old_import, new_import in import_mappings.items():
                if old_import in content:
                    content = content.replace(old_import, new_import)
                    updates.append(f"Updated import: {old_import} -> {new_import}")

            # Write back if changes were made
            if content != original_content and not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            updates.append(f"Error updating {file_path}: {e}")

        return updates

    def _update_all_imports(self) -> List[str]:
        """Update all import statements in the project"""
        print("\n" + "=" * 60)
        print("UPDATING IMPORT STATEMENTS")
        print("=" * 60)

        all_updates = []

        # Find all Python files in the project
        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories and node_modules
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]

            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    updates = self._update_imports_in_file(file_path)
                    if updates:
                        print(f"\nUpdated {file_path}:")
                        for update in updates:
                            print(f"  ✓ {update}")
                        all_updates.extend(updates)

        return all_updates

    def migrate_all(self) -> bool:
        """Migrate all components according to the plan"""
        print("\n" + "=" * 80)
        print("STARTING SRC DIRECTORY MIGRATION")
        print("=" * 80)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")

        print(f"Project root: {self.project_root}")
        print(f"Total components to migrate: {len(self.migration_plan['components'])}")

        # Migrate components in priority order
        for component in self.migration_plan["components"]:
            result = self._migrate_component(component)
            self.results.append(result)

            # Stop on critical failures
            if not result.success and component["layer"] == "Infrastructure":
                print(
                    f"\n❌ Critical infrastructure migration failed: {component['src_path']}"
                )
                print("Stopping migration to prevent dependency issues.")
                return False

        # Update imports after all migrations
        if not self.dry_run:
            import_updates = self._update_all_imports()
            print(f"\nImport updates completed: {len(import_updates)} changes")

        # Print final summary
        self._print_migration_summary()

        return all(result.success for result in self.results)

    def _print_migration_summary(self):
        """Print migration summary"""
        print("\n" + "=" * 80)
        print("MIGRATION SUMMARY")
        print("=" * 80)

        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        git_preserved = [r for r in self.results if r.git_preserved]

        print(f"Total components: {len(self.results)}")
        print(f"✅ Successful: {len(successful)}")
        print(f"❌ Failed: {len(failed)}")
        print(f"📚 Git history preserved: {len(git_preserved)}")

        if failed:
            print("\n❌ FAILED MIGRATIONS:")
            for result in failed:
                print(f"  - {result.component}")
                for error in result.errors:
                    print(f"    ✗ {error}")

        if successful:
            print("\n✅ SUCCESSFUL MIGRATIONS:")
            for result in successful:
                print(f"  - {result.component} -> {result.dest_path}")
                if result.conflicts_resolved:
                    print(f"    Conflicts resolved: {len(result.conflicts_resolved)}")

        print("\n" + "=" * 80)


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Migrate src/ directory to canonical structure"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root directory",
        default=Path(__file__).parent.parent.parent,
    )

    args = parser.parse_args()

    migrator = SrcMigrator(args.project_root, dry_run=args.dry_run)

    print(f"Starting migration from {args.project_root}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    success = migrator.migrate_all()

    if success:
        print("\n🎉 Migration completed successfully!")
        print("\nNext steps:")
        print("1. Test all moved components")
        print("2. Run tests to verify functionality")
        print("3. Update documentation references")
        print("4. Commit changes with appropriate message")
    else:
        print("\n💥 Migration completed with errors!")
        print("Review the errors above and fix before proceeding.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
