import ast
import json
import os
import sys
from pathlib import Path
from typing import Dict, Optional

class ImportUpdater(ast.NodeTransformer):
    """
    An AST visitor to update import statements based on a file migration map.
    """
    def __init__(self, current_file: Path, migration_map: Dict[str, str], project_root: Path):
        self.current_file = current_file
        self.migration_map = migration_map
        self.project_root = project_root
        self.changed = False

    def _get_new_relative_import(self, target_module_path: Path) -> Optional[str]:
        """
        Calculates the new relative import path from the current file to the target module.
        """
        # Get the new path for the current file
        current_file_str = str(self.current_file)
        new_current_file_str = self.migration_map.get(current_file_str, current_file_str)
        new_current_file = Path(new_current_file_str)

        # Get the new path for the target module
        target_module_str = str(target_module_path)
        new_target_module_str = self.migration_map.get(target_module_str, target_module_str)
        new_target_module = Path(new_target_module_str)

        try:
            # Calculate the relative path from the directory of the new current file
            # to the new target file
            relative_path = new_target_module.relative_to(new_current_file.parent)
        except ValueError:
            # This can happen if they are on different drives, or if one is not a subpath of the other's root
            # In our case, it means we need to find the common ancestor and go up from there.
            common_ancestor = Path(os.path.commonpath([new_current_file.parent, new_target_module]))
            up_levels = len(new_current_file.parent.parts) - len(common_ancestor.parts)

            path_from_common = new_target_module.relative_to(common_ancestor)

            relative_path = Path('../' * up_levels) / path_from_common


        # Convert the relative path to a Python module path
        module_path = str(relative_path).replace('/', '.')

        # Remove the .py extension
        if module_path.endswith('.py'):
            module_path = module_path[:-3]

        # Handle __init__.py files
        if module_path.endswith('.__init__'):
            module_path = module_path[:-9]

        return module_path

    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.AST:
        if node.module:
            # Attempt to resolve the module to a file path
            # This is a simplified resolver and might need to be more robust

            # Simple relative import
            if node.level > 0:
                # Resolve relative path
                current_dir = self.current_file.parent

                # Go up `level` directories
                for _ in range(node.level - 1):
                    current_dir = current_dir.parent

                module_parts = node.module.split('.')

                possible_paths = [
                    current_dir.joinpath(*module_parts).with_suffix('.py'),
                    current_dir.joinpath(*module_parts, '__init__.py')
                ]

                target_path = None
                for path in possible_paths:
                    if path.exists():
                        target_path = path
                        break

            # Absolute import
            else:
                module_parts = node.module.split('.')
                # This is a simplification, assumes absolute imports are from project root
                # A proper implementation would check sys.path
                possible_paths = [
                    self.project_root.joinpath(*module_parts).with_suffix('.py'),
                    self.project_root.joinpath(*module_parts, '__init__.py')
                ]
                target_path = None
                for path in possible_paths:
                    if path.exists():
                        target_path = path
                        break

            if target_path and str(target_path) in self.migration_map:
                new_module_path = self._get_new_relative_import(target_path)
                if new_module_path:
                    print(f"  Rewriting import in {self.current_file}: from {node.module} -> from {new_module_path}")
                    node.module = new_module_path
                    node.level = 1 # All new imports will be relative from the new location
                    self.changed = True

        return node


def update_imports_in_file(file_path_str: str, migration_map: Dict[str, str], project_root: Path) -> Optional[str]:
    """
    Updates the import statements in a single Python file.

    Returns the new content if changed, otherwise None.
    """
    file_path = Path(file_path_str)

    # Only process python files
    if file_path.suffix != '.py':
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        tree = ast.parse(source_code)
        updater = ImportUpdater(file_path, migration_map, project_root)
        new_tree = updater.visit(tree)

        if updater.changed:
            return ast.unparse(new_tree)

    except Exception as e:
        print(f"Could not process {file_path}: {e}")

    return None


def main(apply_changes: bool = False):
    """
    Updates import statements in the codebase based on the migration map.
    By default, it performs a dry run. Pass --apply to actually write changes.
    """
    # Allow overriding via command line argument
    if len(sys.argv) > 1 and sys.argv[1] == '--apply':
        apply_changes = True

    project_root = Path(__file__).resolve().parent.parent.parent
    map_path = project_root / "migration-map.json"

    if not map_path.exists():
        print(f"Error: migration-map.json not found at {map_path}")
        return

    with open(map_path, 'r') as f:
        migration_map = json.load(f)

    print(f"--- Running Import Updater (Apply changes: {apply_changes}) ---")

    # We need to check all python files, not just the ones being moved.
    # A file might not be moved but its imports need to change.
    all_python_files = list(project_root.rglob("*.py"))

    for file_path in all_python_files:
        # Skip files in the new directory for now
        if 'freeagentics_new' in str(file_path):
            continue

        new_content = update_imports_in_file(str(file_path), migration_map, project_root)

        if new_content:
            if apply_changes:
                print(f"Updating file: {file_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            else:
                print(f"File to update (dry run): {file_path}")

    print("--- Import Updater Complete ---")


if __name__ == "__main__":
    # The main function will check sys.argv itself
    main()
