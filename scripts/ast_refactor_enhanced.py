#!/usr/bin/env python3
"""
Enhanced AST-Based Code Refactoring Tool for FreeAgentics
Safely updates code references after file/symbol renaming with fallback for syntax errors
"""

import ast
import os
import re
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple, Union
import argparse


class PythonASTRefactor:
    """Python AST-based refactoring with regex fallback for syntax errors"""

    def __init__(self):
        self.changes = []
        self.errors = []
        self.import_map = {}  # old_module -> new_module

    def add_rename_mapping(self, old_path: str, new_path: str):
        """Add a file rename mapping for module path updates"""
        # Convert file paths to module paths
        old_module = self._path_to_module(old_path)
        new_module = self._path_to_module(new_path)

        if old_module and new_module:
            self.import_map[old_module] = new_module
            print(f"Mapping Python module: {old_module} → {new_module}")

    def _path_to_module(self, file_path: str) -> Optional[str]:
        """Convert file path to Python module path"""
        if not file_path.endswith('.py'):
            return None

        # Remove .py extension and convert path separators to dots
        module_path = file_path.replace('.py', '').replace('/', '.').replace('\\', '.')

        # Remove leading dots and common prefixes
        module_path = module_path.lstrip('.')

        # Handle __init__.py files
        if module_path.endswith('.__init__'):
            module_path = module_path[:-9]  # Remove .__init__

        return module_path if module_path else None

    def update_file_with_ast(self, file_path: str, content: str) -> Tuple[str, bool]:
        """Try to update using AST parsing"""
        try:
            tree = ast.parse(content)
            lines = content.split('\n')
            modified = False

            # Update import statements
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in self.import_map:
                            old_name = alias.name
                            new_name = self.import_map[old_name]

                            # Update the line
                            line_num = node.lineno - 1
                            if line_num < len(lines):
                                old_line = lines[line_num]
                                new_line = old_line.replace(old_name, new_name)

                                if new_line != old_line:
                                    lines[line_num] = new_line
                                    modified = True
                                    self.changes.append({
                                        'file': file_path,
                                        'line': node.lineno,
                                        'type': 'import',
                                        'method': 'ast',
                                        'old': old_line.strip(),
                                        'new': new_line.strip()
                                    })

                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module in self.import_map:
                        old_module = node.module
                        new_module = self.import_map[old_module]

                        # Update the line
                        line_num = node.lineno - 1
                        if line_num < len(lines):
                            old_line = lines[line_num]
                            new_line = old_line.replace(old_module, new_module)

                            if new_line != old_line:
                                lines[line_num] = new_line
                                modified = True
                                self.changes.append({
                                    'file': file_path,
                                    'line': node.lineno,
                                    'type': 'from_import',
                                    'method': 'ast',
                                    'old': old_line.strip(),
                                    'new': new_line.strip()
                                })

            return '\n'.join(lines), modified

        except SyntaxError as e:
            # Fall back to regex-based updates
            return self.update_file_with_regex(file_path, content)

    def update_file_with_regex(self, file_path: str, content: str) -> Tuple[str, bool]:
        """Fallback regex-based update for files with syntax errors"""
        original_content = content
        modified = False

        # Patterns for Python imports
        import_patterns = [
            # import module
            (r'(import\s+)(' + '|'.join(re.escape(old) for old in self.import_map.keys()) + r')(\s|$|,)', 'import'),
            # from module import ...
            (r'(from\s+)(' + '|'.join(re.escape(old) for old in self.import_map.keys()) + r')(\s+import)', 'from_import'),
        ]

        for pattern, import_type in import_patterns:
            def replace_import(match):
                nonlocal modified
                prefix = match.group(1)
                module_name = match.group(2)
                suffix = match.group(3)

                if module_name in self.import_map:
                    new_module = self.import_map[module_name]
                    modified = True
                    self.changes.append({
                        'file': file_path,
                        'type': import_type,
                        'method': 'regex',
                        'old': match.group(0),
                        'new': f"{prefix}{new_module}{suffix}"
                    })
                    return f"{prefix}{new_module}{suffix}"

                return match.group(0)

            content = re.sub(pattern, replace_import, content)

        return content, modified

    def update_file(self, file_path: str, dry_run: bool = True) -> bool:
        """Update imports in a Python file using AST with regex fallback"""
        if not file_path.endswith('.py'):
            return True

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Try AST first, fall back to regex if syntax error
            new_content, modified = self.update_file_with_ast(file_path, content)

            # Write changes if not dry run and modifications were made
            if modified and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✓ Updated imports in: {file_path}")
            elif modified:
                print(f"✓ Would update imports in: {file_path}")

            return True

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False


class TypeScriptASTRefactor:
    """TypeScript/JavaScript import refactoring using regex patterns"""

    def __init__(self):
        self.changes = []
        self.errors = []
        self.import_map = {}  # old_path -> new_path

    def add_rename_mapping(self, old_path: str, new_path: str):
        """Add a file rename mapping for import path updates"""
        # Convert to relative import paths
        old_import = self._path_to_import(old_path)
        new_import = self._path_to_import(new_path)

        if old_import and new_import:
            self.import_map[old_import] = new_import

            # Also add variations for relative imports
            old_basename = os.path.basename(old_import)
            new_basename = os.path.basename(new_import)
            if old_basename != new_basename:
                self.import_map[old_basename] = new_basename

            print(f"Mapping TypeScript import: {old_import} → {new_import}")

    def _path_to_import(self, file_path: str) -> Optional[str]:
        """Convert file path to import path"""
        if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
            return None

        # Remove extension for import paths
        import_path = file_path
        for ext in ['.tsx', '.ts', '.jsx', '.js']:
            if import_path.endswith(ext):
                import_path = import_path[:-len(ext)]
                break

        return import_path

    def update_file(self, file_path: str, dry_run: bool = True) -> bool:
        """Update imports in a TypeScript/JavaScript file using regex"""
        if not file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
            return True

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            modified = False

            # Enhanced patterns to match import statements
            import_patterns = [
                # import ... from '...'
                r"(import\s+[^'\"]*\s+from\s+['\"])([^'\"]+)(['\"])",
                # import('...')
                r"(import\s*\(\s*['\"])([^'\"]+)(['\"])",
                # require('...')
                r"(require\s*\(\s*['\"])([^'\"]+)(['\"])",
                # export ... from '...'
                r"(export\s+[^'\"]*\s+from\s+['\"])([^'\"]+)(['\"])",
            ]

            for pattern in import_patterns:
                def replace_import(match):
                    nonlocal modified
                    prefix = match.group(1)
                    import_path = match.group(2)
                    suffix = match.group(3)

                    # Check if this import path needs updating
                    for old_path, new_path in self.import_map.items():
                        # Direct match
                        if import_path == old_path:
                            modified = True
                            self.changes.append({
                                'file': file_path,
                                'type': 'import_direct',
                                'old': f"{prefix}{import_path}{suffix}",
                                'new': f"{prefix}{new_path}{suffix}"
                            })
                            return f"{prefix}{new_path}{suffix}"

                        # Relative path match
                        elif import_path.endswith('/' + old_path):
                            new_import_path = import_path.replace('/' + old_path, '/' + new_path)
                            modified = True
                            self.changes.append({
                                'file': file_path,
                                'type': 'import_relative',
                                'old': f"{prefix}{import_path}{suffix}",
                                'new': f"{prefix}{new_import_path}{suffix}"
                            })
                            return f"{prefix}{new_import_path}{suffix}"

                        # Component name in path
                        elif '/' + old_path in import_path:
                            new_import_path = import_path.replace('/' + old_path, '/' + new_path)
                            modified = True
                            self.changes.append({
                                'file': file_path,
                                'type': 'import_component',
                                'old': f"{prefix}{import_path}{suffix}",
                                'new': f"{prefix}{new_import_path}{suffix}"
                            })
                            return f"{prefix}{new_import_path}{suffix}"

                    return match.group(0)

                content = re.sub(pattern, replace_import, content)

            # Write changes if not dry run and modifications were made
            if modified and not dry_run:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ Updated imports in: {file_path}")
            elif modified:
                print(f"✓ Would update imports in: {file_path}")

            return True

        except Exception as e:
            error_msg = f"Error processing {file_path}: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False


class ASTCodeRefactor:
    """Enhanced AST-based code refactoring coordinator with error handling"""

    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.python_refactor = PythonASTRefactor()
        self.typescript_refactor = TypeScriptASTRefactor()
        self.rename_mappings = []

    def load_rename_plan(self, plan_file: str) -> bool:
        """Load rename plan from JSON file"""
        try:
            with open(plan_file, 'r') as f:
                plan_data = json.load(f)

            self.rename_mappings = plan_data.get('operations', [])

            # Add mappings to language-specific refactors
            for mapping in self.rename_mappings:
                old_path = mapping['old_path']
                new_path = mapping['new_path']

                if old_path.endswith('.py'):
                    self.python_refactor.add_rename_mapping(old_path, new_path)
                elif old_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                    self.typescript_refactor.add_rename_mapping(old_path, new_path)

            print(f"Loaded {len(self.rename_mappings)} rename mappings from {plan_file}")
            return True

        except Exception as e:
            print(f"Error loading rename plan: {e}")
            return False

    def add_manual_mapping(self, old_path: str, new_path: str):
        """Manually add a rename mapping"""
        mapping = {
            'old_path': old_path,
            'new_path': new_path,
            'type': 'file'
        }
        self.rename_mappings.append(mapping)

        if old_path.endswith('.py'):
            self.python_refactor.add_rename_mapping(old_path, new_path)
        elif old_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
            self.typescript_refactor.add_rename_mapping(old_path, new_path)

    def find_source_files(self, root_dir: str = ".") -> List[str]:
        """Find all source files that might need updating"""
        source_files = []

        for root, dirs, files in os.walk(root_dir):
            # Skip protected directories
            if any(skip in root for skip in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']):
                continue

            for file in files:
                if file.endswith(('.py', '.ts', '.tsx', '.js', '.jsx')):
                    source_files.append(os.path.join(root, file))

        return source_files

    def update_all_references(self, root_dir: str = ".") -> Dict[str, int]:
        """Update all code references based on rename mappings"""
        if not self.rename_mappings:
            print("No rename mappings loaded. Load a plan or add manual mappings first.")
            return {}

        source_files = self.find_source_files(root_dir)
        stats = {
            'files_processed': 0,
            'files_updated': 0,
            'python_changes': 0,
            'typescript_changes': 0,
            'python_errors': 0,
            'typescript_errors': 0
        }

        print(f"\n🔧 {'Updating' if not self.dry_run else 'Analyzing'} references in {len(source_files)} files...\n")

        for file_path in source_files:
            stats['files_processed'] += 1

            if file_path.endswith('.py'):
                if self.python_refactor.update_file(file_path, self.dry_run):
                    changes_for_file = [c for c in self.python_refactor.changes if c['file'] == file_path]
                    if changes_for_file:
                        stats['files_updated'] += 1
                        stats['python_changes'] += len(changes_for_file)
                else:
                    stats['python_errors'] += 1

            elif file_path.endswith(('.ts', '.tsx', '.js', '.jsx')):
                if self.typescript_refactor.update_file(file_path, self.dry_run):
                    changes_for_file = [c for c in self.typescript_refactor.changes if c['file'] == file_path]
                    if changes_for_file:
                        stats['files_updated'] += 1
                        stats['typescript_changes'] += len(changes_for_file)
                else:
                    stats['typescript_errors'] += 1

        self._print_summary(stats)
        return stats

    def _print_summary(self, stats: Dict[str, int]):
        """Print refactoring summary"""
        print("\n" + "=" * 60)
        print(f"{'📋 Enhanced AST Refactor Analysis' if self.dry_run else '✅ Enhanced AST Refactor Complete'}")
        print(f"   Files processed: {stats['files_processed']}")
        print(f"   Files updated: {stats['files_updated']}")
        print(f"   Python changes: {stats['python_changes']}")
        print(f"   TypeScript changes: {stats['typescript_changes']}")
        print(f"   Python errors: {stats['python_errors']}")
        print(f"   TypeScript errors: {stats['typescript_errors']}")

        # Show detailed changes
        all_changes = self.python_refactor.changes + self.typescript_refactor.changes
        if all_changes:
            print(f"\n📝 Sample changes:")
            for change in all_changes[:5]:  # Show first 5 changes
                method = change.get('method', 'regex')
                print(f"   {change['file']} ({change['type']}, {method}):")
                print(f"     - {change['old']}")
                print(f"     + {change['new']}")

            if len(all_changes) > 5:
                print(f"   ... and {len(all_changes) - 5} more changes")

        if self.dry_run:
            print(f"\n⚠️  This was a DRY RUN - no files were actually changed")
            print(f"   Run with --apply to make the changes")


def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(
        description="Enhanced AST-based code refactoring for renamed files"
    )
    parser.add_argument(
        "--apply", action="store_true",
        help="Actually make the changes (default is dry-run)"
    )
    parser.add_argument(
        "--plan",
        help="JSON file containing rename plan (from batch-rename.py)"
    )
    parser.add_argument(
        "--root", default=".",
        help="Root directory to search for source files"
    )
    parser.add_argument(
        "--add-mapping", nargs=2, metavar=('OLD_PATH', 'NEW_PATH'),
        action='append', default=[],
        help="Manually add old_path new_path mapping (can be used multiple times)"
    )

    args = parser.parse_args()

    # Initialize refactor
    refactor = ASTCodeRefactor(dry_run=not args.apply)

    # Load rename plan if provided
    if args.plan:
        if not refactor.load_rename_plan(args.plan):
            return 1

    # Add manual mappings
    for old_path, new_path in args.add_mapping:
        refactor.add_manual_mapping(old_path, new_path)

    # Update references
    stats = refactor.update_all_references(args.root)

    return 0


if __name__ == "__main__":
    exit(main())
