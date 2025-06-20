#!/usr/bin/env python3
"""
Comprehensive Batch Renaming Script for FreeAgentics
Handles large-scale file and directory renaming with advanced options
"""

import os
import re
import json
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse
from datetime import datetime


class BatchRenamer:
    def __init__(self, dry_run: bool = True, use_git: bool = True, backup: bool = True):
        """Initialize batch renamer with safety options"""
        self.dry_run = dry_run
        self.use_git = use_git
        self.backup = backup
        self.operations = []
        self.errors = []
        self.stats = {
            "files_processed": 0,
            "files_renamed": 0,
            "directories_renamed": 0,
            "errors": 0,
            "skipped": 0
        }

        # Safety patterns - never rename these
        self.protected_patterns = {
            ".git", "__pycache__", "node_modules", ".env", ".venv",
            "venv", ".next", "build", "dist", "coverage"
        }

    def _is_protected(self, path: str) -> bool:
        """Check if path should be protected from renaming"""
        path_parts = Path(path).parts
        return any(pattern in path_parts for pattern in self.protected_patterns)

    def _to_kebab_case(self, name: str) -> str:
        """Convert string to kebab-case"""
        # Handle camelCase and PascalCase
        name = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
        name = re.sub("([a-z0-9])([A-Z])", r"\1-\2", name)
        # Handle snake_case
        name = name.replace("_", "-")
        # Clean up and lowercase
        name = re.sub("-+", "-", name)
        return name.lower().strip("-")

    def _to_pascal_case(self, name: str) -> str:
        """Convert string to PascalCase"""
        # Split on various delimiters
        parts = re.split(r"[-_\s]+", name)
        return "".join(word.capitalize() for word in parts if word)

    def _to_camel_case(self, name: str) -> str:
        """Convert string to camelCase"""
        pascal = self._to_pascal_case(name)
        return pascal[0].lower() + pascal[1:] if pascal else ""

    def plan_python_file_renames(self, root_dir: str = ".") -> List[Dict]:
        """Plan Python file renames to kebab-case"""
        renames = []

        for root, dirs, files in os.walk(root_dir):
            # Skip protected directories
            if self._is_protected(root):
                continue

            for file in files:
                if not file.endswith(".py"):
                    continue

                filepath = os.path.join(root, file)
                filename_base = file.replace(".py", "")

                # Skip special files
                if filename_base in ["__init__", "__main__"]:
                    continue

                # Check if it needs renaming to kebab-case
                if "_" in filename_base or not re.match(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$", filename_base):
                    new_name = self._to_kebab_case(filename_base) + ".py"

                    if new_name != file:
                        renames.append({
                            "type": "file",
                            "old_path": filepath,
                            "new_path": os.path.join(root, new_name),
                            "reason": "Python file should use kebab-case",
                            "language": "python"
                        })

        return renames

    def plan_typescript_file_renames(self, root_dir: str = ".") -> List[Dict]:
        """Plan TypeScript file renames based on type"""
        renames = []

        for root, dirs, files in os.walk(root_dir):
            # Skip protected directories
            if self._is_protected(root):
                continue

            for file in files:
                if not file.endswith((".ts", ".tsx")):
                    continue

                filepath = os.path.join(root, file)
                filename_base = file.replace(".tsx", "").replace(".ts", "")
                extension = ".tsx" if file.endswith(".tsx") else ".ts"

                # Component files should be PascalCase
                if "components" in root and extension == ".tsx":
                    if not re.match(r"^[A-Z][a-zA-Z0-9]*$", filename_base):
                        new_name = self._to_pascal_case(filename_base) + extension
                        if new_name != file:
                            renames.append({
                                "type": "file",
                                "old_path": filepath,
                                "new_path": os.path.join(root, new_name),
                                "reason": "React component should use PascalCase",
                                "language": "typescript"
                            })

                # Hook files should be camelCase
                elif filename_base.startswith("use") and extension == ".ts":
                    if "-" in filename_base:
                        # Convert use-hook-name to useHookName
                        hook_part = filename_base[3:]  # Remove "use"
                        camel_hook = self._to_camel_case(hook_part)
                        new_name = f"use{camel_hook.capitalize()}{extension}"
                        if new_name != file:
                            renames.append({
                                "type": "file",
                                "old_path": filepath,
                                "new_path": os.path.join(root, new_name),
                                "reason": "React hook should use camelCase",
                                "language": "typescript"
                            })

        return renames

    def plan_all_renames(self, root_dir: str = ".") -> List[Dict]:
        """Plan all renames for the project"""
        all_renames = []

        print("🔍 Planning Python file renames...")
        all_renames.extend(self.plan_python_file_renames(root_dir))

        print("🔍 Planning TypeScript file renames...")
        all_renames.extend(self.plan_typescript_file_renames(root_dir))

        # Sort by depth (deeper paths first to avoid parent/child conflicts)
        all_renames.sort(key=lambda x: x["old_path"].count(os.sep), reverse=True)

        return all_renames

    def execute_batch_rename(self, operations: List[Dict]) -> None:
        """Execute all rename operations"""
        if not operations:
            print("No rename operations to perform.")
            return

        print(f"\n{'🔧 Executing' if not self.dry_run else '📋 Planned'} {len(operations)} rename operations...\n")

        for i, operation in enumerate(operations, 1):
            print(f"{i:3d}. {operation['reason']}")

            if self.dry_run:
                print(f"     Would rename: {operation['old_path']} → {operation['new_path']}")
                self.stats["files_processed"] += 1
            else:
                if self._execute_rename(operation):
                    if operation["type"] == "file":
                        self.stats["files_renamed"] += 1
                    self.stats["files_processed"] += 1
                else:
                    self.stats["errors"] += 1

        self._print_summary(operations)

    def _execute_rename(self, operation: Dict) -> bool:
        """Execute a single rename operation"""
        old_path = operation["old_path"]
        new_path = operation["new_path"]

        try:
            # Use git mv if available and requested
            if self.use_git and self._is_git_tracked(old_path):
                result = subprocess.run(
                    ["git", "mv", old_path, new_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"   ✓ Git moved: {old_path} → {new_path}")
                    return True
                else:
                    print(f"   ⚠️ Git mv failed, using regular rename")

            # Fallback to regular rename
            os.rename(old_path, new_path)
            print(f"   ✓ Renamed: {old_path} → {new_path}")
            return True

        except Exception as e:
            error_msg = f"Failed to rename {old_path} → {new_path}: {e}"
            self.errors.append(error_msg)
            print(f"   ✗ {error_msg}")
            return False

    def _is_git_tracked(self, path: str) -> bool:
        """Check if file is tracked by git"""
        try:
            result = subprocess.run(
                ["git", "ls-files", path],
                capture_output=True,
                text=True
            )
            return bool(result.stdout.strip())
        except:
            return False

    def _print_summary(self, operations: List[Dict]) -> None:
        """Print operation summary"""
        print("\n" + "=" * 60)
        print(f"{'📋 Batch Rename Summary' if self.dry_run else '✅ Batch Rename Complete'}")
        print(f"   Total operations: {len(operations)}")
        print(f"   Files processed: {self.stats['files_processed']}")
        print(f"   Files renamed: {self.stats['files_renamed']}")
        print(f"   Errors: {self.stats['errors']}")

        if self.errors:
            print(f"\n❌ Errors encountered:")
            for error in self.errors:
                print(f"   • {error}")

        if self.dry_run:
            print(f"\n⚠️  This was a DRY RUN - no files were actually renamed")
            print(f"   Run with --apply to execute the renames")


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(
        description="Comprehensive batch renaming for FreeAgentics naming conventions"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually perform the renames (default is dry-run)"
    )
    parser.add_argument(
        "--no-git", action="store_true",
        help="Don't use git mv (use regular rename)"
    )
    parser.add_argument(
        "--root", default=".",
        help="Root directory to start renaming from"
    )
    parser.add_argument(
        "--python-only", action="store_true",
        help="Only rename Python files"
    )
    parser.add_argument(
        "--typescript-only", action="store_true",
        help="Only rename TypeScript files"
    )

    args = parser.parse_args()

    # Initialize renamer
    renamer = BatchRenamer(
        dry_run=not args.apply,
        use_git=not args.no_git,
        backup=True
    )

    # Plan renames based on flags
    operations = []
    if args.python_only:
        operations = renamer.plan_python_file_renames(args.root)
    elif args.typescript_only:
        operations = renamer.plan_typescript_file_renames(args.root)
    else:
        operations = renamer.plan_all_renames(args.root)

    # Execute renames
    renamer.execute_batch_rename(operations)


if __name__ == "__main__":
    main()
