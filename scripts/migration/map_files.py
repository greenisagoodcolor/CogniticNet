import json
import os
from pathlib import Path

# The new directory structure as defined in ADR-001
# This is a simplified representation for mapping purposes
TARGET_STRUCTURE = {
    # Core Domain
    "agents": "freeagentics_new/agents",
    "inference": "freeagentics_new/inference",
    "coalitions": "freeagentics_new/coalitions",
    "world": "freeagentics_new/world",
    # Interface Layer
    "api": "freeagentics_new/api",
    "web": "freeagentics_new/web",
    # Infrastructure Layer
    "infrastructure": "freeagentics_new/infrastructure",
    "config": "freeagentics_new/config",
    # Data Assets
    "data": "freeagentics_new/data",
    # Automation
    "scripts": "freeagentics_new/scripts",
    # Test Suites
    "tests": "freeagentics_new/tests",
    # Documentation
    "docs": "freeagentics_new/docs",
}

# Mapping of old top-level directories to new ones
# This is highly specific to the current messy structure
OLD_TO_NEW_ROOT = {
    "agents": "agents",
    "src/agents": "agents",
    "inference": "inference",
    "src/inference": "inference",
    "coalitions": "coalitions",
    "src/coalitions": "coalitions",
    "world": "world",
    "src/world": "world",
    "api": "api",
    "src/api": "api",
    "web/src": "web",
    "environments": "config/environments",
    "src/database": "data",
    "scripts/repository_analysis": "scripts/development",
    "tests/unit": "tests/unit",
    "tests/integration": "tests/integration",
    "docs/doc": "docs",
    "models": "data/schemas", # GNN models
}

def kebab_case(name: str) -> str:
    """Converts a string to kebab-case."""
    name = name.replace('_', '-').replace(' ', '-')
    return ''.join(c for c in name if c.isalnum() or c == '-').lower()

def get_target_path(current_path: Path, project_root: Path) -> Path:
    """
    Determines the new path for a file based on mapping rules.
    """
    # Normalize to relative path
    try:
        relative_path = current_path.relative_to(project_root)
    except ValueError:
        return current_path # Not in project root, don't move

    parts = relative_path.parts

    # Ignore certain files and directories
    if any(p.startswith('.') for p in parts) or '__pycache__' in parts:
        return current_path
    if relative_path.name in ["migrate-to-freeagentics.py", "map_files.py", "migration-map.json"]:
         return current_path
    if "freeagentics_new" in parts:
        return current_path # Already in the new structure

    # Apply root mapping
    for old_root, new_root in OLD_TO_NEW_ROOT.items():
        if str(relative_path).startswith(old_root):
            new_parts = new_root.split('/') + list(parts[len(old_root.split('/')):])

            # Convert filename and directories to kebab-case as per ADR-002
            # but keep extension
            filename = new_parts[-1]
            stem, ext = os.path.splitext(filename)
            kebab_stem = kebab_case(stem)

            # Special exceptions for filenames that should not be converted
            if filename in ["Dockerfile", "Makefile", "README.md", "LICENSE"]:
                 kebab_stem = stem

            kebab_filename = f"{kebab_stem}{ext}"

            kebab_dirs = [kebab_case(p) for p in new_parts[:-1]]

            new_path_str = "/".join(kebab_dirs + [kebab_filename])

            # Prepend the target base directory
            return project_root / "freeagentics_new" / new_path_str


    # Fallback for files not in the explicit mapping (e.g., root files)
    # Move most root files to docs or config
    if len(parts) == 1:
        if relative_path.suffix in ['.md', '.txt']:
            return project_root / TARGET_STRUCTURE["docs"] / kebab_case(relative_path.name)
        if relative_path.suffix in ['.json', '.yml', '.yaml', '.toml', '.js']:
             return project_root / TARGET_STRUCTURE["config"] / kebab_case(relative_path.name)
        if relative_path.suffix in ['.sh']:
            return project_root / TARGET_STRUCTURE["scripts"] / "setup" / kebab_case(relative_path.name)


    return current_path # If no rule matches, keep it where it is

def main():
    """
    Generates a mapping of current file paths to their new target paths.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    file_mapping: dict[str, str] = {}

    for root, _, files in os.walk(project_root):
        # Skip the target directory to avoid re-mapping
        if 'freeagentics_new' in root:
            continue

        for file in files:
            current_path = Path(root) / file
            target_path = get_target_path(current_path, project_root)

            if current_path != target_path:
                file_mapping[str(current_path)] = str(target_path)

    output_path = project_root / "migration-map.json"
    with open(output_path, 'w') as f:
        json.dump(file_mapping, f, indent=2)

    print(f"Generated file mapping for {len(file_mapping)} files at: {output_path}")

if __name__ == "__main__":
    main()
