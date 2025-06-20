#!/usr/bin/env python3
"""
Update Import Statements After src/ Migration

This script updates all import statements in the codebase to reflect
the new canonical structure after src/ directory migration.

Architectural Compliance:
- Updates imports to match canonical structure from ADR-002
- Handles special cases like agents/core/ namespace
- Preserves functionality while enforcing clean architecture
"""

import os
import re
import ast
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ImportUpdate:
    """Record of an import update"""

    file_path: str
    line_number: int
    old_import: str
    new_import: str
    import_type: str  # 'import', 'from_import'


class ImportUpdater:
    """Updates import statements throughout the codebase"""

    def __init__(self, project_root: Path, dry_run: bool = False):
        self.project_root = project_root
        self.dry_run = dry_run
        self.import_mappings = self._create_import_mappings()
        self.updates: List[ImportUpdate] = []

    def _create_import_mappings(self) -> Dict[str, str]:
        """Create mapping of old imports to new imports"""
        return {
            # Infrastructure Layer
            "infrastructure.database": "infrastructure.database",
            "infrastructure.hardware": "infrastructure.hardware",
            "infrastructure.deployment": "infrastructure.deployment",
            "infrastructure.export": "infrastructure.export",
            # Core Layer - Special handling for agents
            "agents.core.active_inference": "agents.core.active_inference",
            "agents.core.movement_perception": "agents.core.movement_perception",
            "agents.core.testing": "agents.testing",
            "agents.core": "agents.core",  # Default for unspecified agents.core imports
            # Supporting Layer
            "learning": "learning",
            "simulation": "simulation",
            "models": "models",
            "knowledge": "knowledge",
            "readiness": "readiness",
            "monitoring": "monitoring",
            "validation": "validation",
            # Interface Layer
            "scripts.pipeline": "scripts.pipeline",
        }

    def _find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []

        for root, dirs, files in os.walk(self.project_root):
            # Skip hidden directories, node_modules, and __pycache__
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".") and d not in ["node_modules", "__pycache__"]
            ]

            for file in files:
                if file.endswith(".py"):
                    python_files.append(Path(root) / file)

        return python_files

    def _analyze_imports_with_ast(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """Analyze imports using AST to get accurate line numbers and types"""
        imports_found = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports_found.append((node.lineno, alias.name, "import"))
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports_found.append((node.lineno, node.module, "from_import"))

        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

        return imports_found

    def _update_file_imports(self, file_path: Path) -> List[ImportUpdate]:
        """Update imports in a single file"""
        file_updates = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            original_lines = lines.copy()

            # Get AST-based import analysis
            ast_imports = self._analyze_imports_with_ast(file_path)

            # Update each line
            for line_num, original_import, import_type in ast_imports:
                line_idx = line_num - 1  # Convert to 0-based index
                if line_idx >= len(lines):
                    continue

                line = lines[line_idx]
                updated_line = line

                # Check each mapping
                for old_import, new_import in self.import_mappings.items():
                    if old_import in line:
                        # Use regex for more precise replacement
                        patterns = [
                            # Match "import src.module"
                            (
                                rf"\bimport\s+{re.escape(old_import)}\b",
                                f"import {new_import}",
                            ),
                            # Match "from src.module import"
                            (
                                rf"\bfrom\s+{re.escape(old_import)}\b",
                                f"from {new_import}",
                            ),
                            # Match "import src.module as alias"
                            (
                                rf"\bimport\s+{re.escape(old_import)}\s+as\s+",
                                f"import {new_import} as ",
                            ),
                            # Match "from src.module.submodule import"
                            (
                                rf"\bfrom\s+{re.escape(old_import)}\.",
                                f"from {new_import}.",
                            ),
                        ]

                        for pattern, replacement in patterns:
                            if re.search(pattern, line):
                                new_line = re.sub(pattern, replacement, line)
                                if new_line != line:
                                    lines[line_idx] = new_line
                                    file_updates.append(
                                        ImportUpdate(
                                            file_path=str(
                                                file_path.relative_to(self.project_root)
                                            ),
                                            line_number=line_num,
                                            old_import=line.strip(),
                                            new_import=new_line.strip(),
                                            import_type=import_type,
                                        )
                                    )
                                    updated_line = new_line
                                    break

                        if updated_line != line:
                            break

            # Write back if changes were made
            if lines != original_lines and not self.dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.writelines(lines)

        except Exception as e:
            print(f"Error updating {file_path}: {e}")

        return file_updates

    def update_all_imports(self) -> bool:
        """Update imports in all Python files"""
        print("\n" + "=" * 80)
        print("UPDATING IMPORT STATEMENTS")
        print("=" * 80)

        if self.dry_run:
            print("🔍 DRY RUN MODE - No actual changes will be made")

        python_files = self._find_python_files()
        print(f"Found {len(python_files)} Python files to check")

        files_updated = 0
        total_updates = 0

        for file_path in python_files:
            file_updates = self._update_file_imports(file_path)
            if file_updates:
                files_updated += 1
                total_updates += len(file_updates)
                self.updates.extend(file_updates)

                print(f"\n📝 Updated {file_path.relative_to(self.project_root)}:")
                for update in file_updates:
                    print(f"  Line {update.line_number}: {update.old_import}")
                    print(f"  →         {update.new_import}")

        print("\n" + "=" * 80)
        print("IMPORT UPDATE SUMMARY")
        print("=" * 80)
        print(f"Files checked: {len(python_files)}")
        print(f"Files updated: {files_updated}")
        print(f"Total import updates: {total_updates}")

        if self.dry_run:
            print("\n🔍 DRY RUN - No files were actually modified")
        else:
            print("\n✅ Import updates completed successfully")

        return True

    def validate_imports(self) -> List[str]:
        """Validate that updated imports are syntactically correct"""
        print("\n" + "=" * 60)
        print("VALIDATING UPDATED IMPORTS")
        print("=" * 60)

        errors = []
        python_files = self._find_python_files()

        for file_path in python_files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Try to parse with AST
                ast.parse(content)

            except SyntaxError as e:
                error_msg = (
                    f"Syntax error in {file_path.relative_to(self.project_root)}: {e}"
                )
                errors.append(error_msg)
                print(f"❌ {error_msg}")
            except Exception as e:
                error_msg = (
                    f"Error validating {file_path.relative_to(self.project_root)}: {e}"
                )
                errors.append(error_msg)
                print(f"⚠️  {error_msg}")

        if not errors:
            print("✅ All files have valid Python syntax")
        else:
            print(f"\n❌ Found {len(errors)} validation errors")

        return errors

    def save_update_log(self, log_file: Path):
        """Save detailed update log"""
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("Import Update Log\n")
            f.write("=" * 50 + "\n\n")

            for update in self.updates:
                f.write(f"File: {update.file_path}\n")
                f.write(f"Line: {update.line_number}\n")
                f.write(f"Type: {update.import_type}\n")
                f.write(f"Old:  {update.old_import}\n")
                f.write(f"New:  {update.new_import}\n")
                f.write("-" * 40 + "\n")

        print(f"📋 Detailed update log saved to: {log_file}")


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update import statements after src/ migration"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate syntax after updates"
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Project root directory",
        default=Path(__file__).parent.parent.parent,
    )

    args = parser.parse_args()

    updater = ImportUpdater(args.project_root, dry_run=args.dry_run)

    print(f"Starting import updates in {args.project_root}")
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")

    # Update imports
    success = updater.update_all_imports()

    # Save log
    if updater.updates:
        log_file = args.project_root / "scripts" / "migration" / "import_update_log.txt"
        updater.save_update_log(log_file)

    # Validate if requested
    if args.validate and not args.dry_run:
        errors = updater.validate_imports()
        if errors:
            print(f"\n❌ Validation failed with {len(errors)} errors")
            return 1

    if success:
        print("\n🎉 Import updates completed successfully!")
        return 0
    else:
        print("\n💥 Import updates completed with errors!")
        return 1


if __name__ == "__main__":
    exit(main())
