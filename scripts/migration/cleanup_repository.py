#!/usr/bin/env python3
"""
Repository cleanup script for post-migration cleanup.
Removes old files, empty directories, and build artifacts safely.
"""

import os
import shutil
from pathlib import Path
from typing import List, Set

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Files and directories that should NEVER be deleted
PROTECTED_PATHS = {
    ".git",
    ".github",
    ".gitignore",
    ".env",
    ".env.example",
    "freeagentics_new",  # Our new structure
    "scripts",  # Keep our migration scripts
    "docs/architecture",  # Keep our ADRs
    ".taskmaster",  # Keep Task Master files
    ".pre-commit-config.yaml",
    "migration-map.json",
    "migration-plan.json",
    "migration-plan-updated.json",
}

# File extensions for build artifacts
BUILD_ARTIFACTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".so",
    ".dll",
    ".dylib",
    ".egg-info",
    ".dist-info",
    ".coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "__pycache__",
    ".next",
    ".nuxt",
    "dist",
    "build",
}

# Directories that are likely empty after migration
LIKELY_EMPTY_DIRS = {
    "agents",
    "api",
    "coalitions",
    "inference",
    "world",
    "tests",
    "web",
    "environments",
    "models",
    "docs/doc",
}


class RepositoryCleanup:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.files_to_delete: List[Path] = []
        self.dirs_to_delete: List[Path] = []
        self.protected_files: Set[Path] = set()

    def is_protected(self, path: Path) -> bool:
        """Check if a path is protected from deletion."""
        path_str = str(path.relative_to(PROJECT_ROOT))

        # Check exact matches
        if path_str in PROTECTED_PATHS:
            return True

        # Check if path is within protected directories
        for protected in PROTECTED_PATHS:
            if path_str.startswith(protected + "/") or path_str.startswith(
                protected + "\\"
            ):
                return True

        return False

    def is_build_artifact(self, path: Path) -> bool:
        """Check if a path is a build artifact."""
        if path.suffix in BUILD_ARTIFACTS:
            return True
        if path.name in BUILD_ARTIFACTS:
            return True
        return False

    def scan_for_cleanup(self):
        """Scan the repository for files and directories to clean up."""
        print("🔍 Scanning repository for cleanup candidates...")

        for root, dirs, files in os.walk(PROJECT_ROOT):
            root_path = Path(root)

            # Skip protected directories
            if self.is_protected(root_path):
                continue

            # Check files in this directory
            for file in files:
                file_path = root_path / file

                if self.is_protected(file_path):
                    self.protected_files.add(file_path)
                    continue

                # Mark build artifacts for deletion
                if self.is_build_artifact(file_path):
                    self.files_to_delete.append(file_path)
                    continue

                # Check if file was supposed to be migrated but wasn't
                if self.should_be_cleaned_up(file_path):
                    self.files_to_delete.append(file_path)

        # Find empty directories
        self.find_empty_directories()

    def should_be_cleaned_up(self, file_path: Path) -> bool:
        """Determine if a file should be cleaned up based on migration status."""
        # If the file is in a directory that should be mostly empty after migration
        relative_path = file_path.relative_to(PROJECT_ROOT)
        first_part = (
            str(relative_path).split("/")[0]
            if "/" in str(relative_path)
            else str(relative_path).split("\\")[0]
        )

        if first_part in LIKELY_EMPTY_DIRS:
            # Check if there's a corresponding file in freeagentics_new
            new_structure_path = PROJECT_ROOT / "freeagentics_new" / relative_path
            if new_structure_path.exists():
                return True  # File was migrated, old one can be deleted

        return False

    def find_empty_directories(self):
        """Find directories that are empty or contain only empty subdirectories."""
        for root, dirs, files in os.walk(PROJECT_ROOT, topdown=False):
            root_path = Path(root)

            if self.is_protected(root_path):
                continue

            # Check if directory is empty or contains only files marked for deletion
            remaining_files = []
            for file in files:
                file_path = root_path / file
                if file_path not in self.files_to_delete and not self.is_protected(
                    file_path
                ):
                    remaining_files.append(file)

            # Check if directory has any non-empty subdirectories
            remaining_dirs = []
            for dir_name in dirs:
                dir_path = root_path / dir_name
                if dir_path not in self.dirs_to_delete and not self.is_protected(
                    dir_path
                ):
                    remaining_dirs.append(dir_name)

            # If no remaining files or directories, mark for deletion
            if not remaining_files and not remaining_dirs:
                relative_path = root_path.relative_to(PROJECT_ROOT)
                first_part = (
                    str(relative_path).split("/")[0]
                    if "/" in str(relative_path)
                    else str(relative_path).split("\\")[0]
                )

                if (
                    first_part in LIKELY_EMPTY_DIRS
                    or len(str(relative_path).split("/")) > 1
                ):
                    self.dirs_to_delete.append(root_path)

    def display_cleanup_plan(self):
        """Display what will be cleaned up."""
        print(f"\\n📋 Cleanup Plan ({'DRY RUN' if self.dry_run else 'EXECUTION'}):")
        print(f"{'='*60}")

        if self.files_to_delete:
            print(f"\\n🗑️  Files to delete ({len(self.files_to_delete)}):")
            for file_path in sorted(self.files_to_delete):
                relative_path = file_path.relative_to(PROJECT_ROOT)
                file_size = file_path.stat().st_size if file_path.exists() else 0
                print(f"  - {relative_path} ({file_size} bytes)")

        if self.dirs_to_delete:
            print(f"\\n📁 Empty directories to remove ({len(self.dirs_to_delete)}):")
            for dir_path in sorted(self.dirs_to_delete):
                relative_path = dir_path.relative_to(PROJECT_ROOT)
                print(f"  - {relative_path}/")

        if self.protected_files:
            print(
                f"\\n🛡️  Protected files (will NOT be deleted) ({len(self.protected_files)}):"
            )
            for file_path in sorted(list(self.protected_files)[:10]):  # Show first 10
                relative_path = file_path.relative_to(PROJECT_ROOT)
                print(f"  - {relative_path}")
            if len(self.protected_files) > 10:
                print(f"  ... and {len(self.protected_files) - 10} more")

        total_size = sum(f.stat().st_size for f in self.files_to_delete if f.exists())
        print(
            f"\\n💾 Total space to be freed: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)"
        )

    def execute_cleanup(self):
        """Execute the cleanup plan."""
        if self.dry_run:
            print("\\n⚠️  This is a DRY RUN. No files will actually be deleted.")
            return

        print("\\n🧹 Executing cleanup...")

        # Delete files
        deleted_files = 0
        for file_path in self.files_to_delete:
            try:
                if file_path.exists():
                    file_path.unlink()
                    deleted_files += 1
                    print(f"  ✅ Deleted: {file_path.relative_to(PROJECT_ROOT)}")
            except Exception as e:
                print(
                    f"  ❌ Failed to delete {file_path.relative_to(PROJECT_ROOT)}: {e}"
                )

        # Remove empty directories
        deleted_dirs = 0
        for dir_path in self.dirs_to_delete:
            try:
                if dir_path.exists() and dir_path.is_dir():
                    shutil.rmtree(dir_path)
                    deleted_dirs += 1
                    print(
                        f"  ✅ Removed directory: {dir_path.relative_to(PROJECT_ROOT)}/"
                    )
            except Exception as e:
                print(
                    f"  ❌ Failed to remove directory {dir_path.relative_to(PROJECT_ROOT)}: {e}"
                )

        print(
            f"\\n✨ Cleanup complete! Deleted {deleted_files} files and {deleted_dirs} directories."
        )


def main():
    """Main cleanup function."""
    import sys

    # Check if --execute flag is provided
    dry_run = "--execute" not in sys.argv

    if dry_run:
        print("🧹 Repository Cleanup Tool (DRY RUN MODE)")
        print("Use --execute flag to actually perform the cleanup")
    else:
        print("🧹 Repository Cleanup Tool (EXECUTION MODE)")
        print("⚠️  WARNING: This will permanently delete files!")

    print(f"📁 Working directory: {PROJECT_ROOT}")

    cleanup = RepositoryCleanup(dry_run=dry_run)
    cleanup.scan_for_cleanup()
    cleanup.display_cleanup_plan()

    cleanup.execute_cleanup()


if __name__ == "__main__":
    main()
