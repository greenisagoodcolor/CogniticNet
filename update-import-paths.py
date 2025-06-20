#!/usr/bin/env python3
"""
Update Import Paths Script
Updates all import statements to reflect the new FreeAgentics directory structure
Lead: Martin Fowler
"""

import os
import re

# Define import mappings from old to new structure
IMPORT_MAPPINGS = {
    # Python imports
    "from agents.base": "from agents.base",
    "import agents.base": "import agents.base",
    "from inference.engine": "from inference.engine",
    "import inference.engine": "import inference.engine",
    "from coalitions": "from coalitions",
    "import coalitions": "import coalitions",
    "from inference.gnn": "from inference.gnn",
    "import inference.gnn": "import inference.gnn",
    "from inference.llm": "from inference.llm",
    "import inference.llm": "import inference.llm",
    "from world": "from world",
    "import world": "import world",
    "from world.spatial": "from world.spatial",
    "import world.spatial": "import world.spatial",
    "from tests": "from tests",
    "import tests": "import tests",
    # TypeScript/JavaScript imports
    "@/api/rest": "@/api/rest",
    "@/web/src/components": "@/web/src/components",
    "from '@/api/rest": "from '@/api/rest",
    "from '@/web/src/components": "from '@/web/src/components",
    "from 'api/rest": "from 'api/rest",
    "from 'web/src/components": "from 'web/src/components",
    "@/web/src/hooks": "@/web/src/hooks",
    "@/web/src/lib": "@/web/src/lib",
    "@/web/src/contexts": "@/web/src/contexts",
    "from '@/web/src/hooks": "from '@/web/src/hooks",
    "from '@/web/src/lib": "from '@/web/src/lib",
    "from '@/web/src/contexts": "from '@/web/src/contexts",
    # Relative imports that need updating
    "../agents/base": "../agents/base",
    "../inference/engine": "../inference/engine",
    "../inference/gnn": "../inference/gnn",
    "../inference/llm": "../inference/llm",
    # Update references to agents.base.communication.py
    "agents.base.communication": "agents.base.communication",
    # Doc references
    "/docs/": "/docs/",
    # Package name updates
    "FreeAgentics": "FreeAgentics",
    "freeagentics": "freeagentics",
    "freeagentics": "freeagentics",
}


def update_imports_in_file(file_path: str) -> int:
    """Update imports in a single file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content
        changes_made = 0

        # Apply all mappings
        for old_import, new_import in IMPORT_MAPPINGS.items():
            if old_import in content:
                content = content.replace(old_import, new_import)
                changes_made += content.count(new_import) - original_content.count(
                    new_import
                )

        # Special case: Update Python relative imports
        if file_path.endswith(".py"):
            # Update from . imports based on new file location
            file_dir = os.path.dirname(file_path)

            # If file is in agents/base, update relative imports
            if "agents/base" in file_dir:
                content = re.sub(r"from \. import", "from agents.base import", content)
                content = re.sub(
                    r"from \.\.active_inference", "from inference.engine", content
                )

            # If file is in inference/engine, update relative imports
            if "inference/engine" in file_dir:
                content = re.sub(
                    r"from \. import", "from inference.engine import", content
                )
                content = re.sub(r"from \.\.gnn", "from inference.gnn", content)

        # Write back if changes were made
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✓ Updated {changes_made} imports in: {file_path}")
            return changes_made

        return 0

    except Exception as e:
        print(f"✗ Error updating {file_path}: {e}")
        return 0


def main():
    """Main function to update all imports"""
    print("Updating import paths for FreeAgentics migration...")

    total_files = 0
    total_changes = 0

    # File extensions to process
    extensions = {".py", ".ts", ".tsx", ".js", ".jsx"}

    # Directories to skip
    skip_dirs = {
        ".git",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        "venv",
        ".venv",
    }

    # Walk through all files
    for root, dirs, files in os.walk("."):
        # Remove skip directories from dirs to prevent walking into them
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                changes = update_imports_in_file(file_path)
                if changes > 0:
                    total_files += 1
                    total_changes += changes

    print("\nImport update complete!")
    print(f"- Files updated: {total_files}")
    print(f"- Total import changes: {total_changes}")

    # Also update any JSON config files
    print("\nUpdating configuration files...")

    config_files = [
        "tsconfig.json",
        "package.json",
        "pyproject.toml",
        ".eslintrc.json",
        "jest.config.js",
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    content = f.read()

                original = content

                # Update path mappings
                content = content.replace("src/agents", "agents")
                content = content.replace("src/gnn", "inference/gnn")
                content = content.replace("src/llm", "inference/llm")
                content = content.replace("src/world", "world")
                content = content.replace("src/tests", "tests")
                content = content.replace("app/api", "api/rest")
                content = content.replace("app/components", "web/src/components")
                content = content.replace("FreeAgentics", "FreeAgentics")
                content = content.replace("freeagentics", "freeagentics")

                if content != original:
                    with open(config_file, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"✓ Updated config: {config_file}")

            except Exception as e:
                print(f"✗ Error updating {config_file}: {e}")


if __name__ == "__main__":
    main()
