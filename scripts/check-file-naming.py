#!/usr/bin/env python3
"""
Check file naming conventions based on ADR-004 v1.1.
"""

import sys
import os
import re

# Core module directories that are allowed to use snake_case for Python modules
CORE_MODULE_DIRS = ["agents/", "coalitions/", "inference/", "world/"]


def check_python_file(filepath):
    """Check Python file naming based on location and pattern."""
    filename = os.path.basename(filepath)

    # Rule 1: Allow test_*.py pattern for pytest discovery
    if filename.startswith("test_") and filename.endswith(".py"):
        return True

    # Rule 2: Allow snake_case for modules within core directories
    # Normalize path for consistent matching
    normalized_path = filepath.replace(os.sep, "/")
    if any(core_dir in normalized_path for core_dir in CORE_MODULE_DIRS):
        # Assuming that if it's in a core dir, it's a module that can be snake_case
        return True

    # Rule 3: Enforce kebab-case for all other Python scripts
    # This pattern allows for single-word names as well
    pattern = r"^[a-z0-9]+(-[a-z0-9]+)*\.py$"
    if filename.startswith("test-"):
        pattern = r"^test-[a-z0-9]+(-[a-z0-9]+)*\.py$"
    elif filename.startswith("_"):
        pattern = r"^_[a-z0-9]+(-[a-z0-9]+)*\.py$"

    return re.match(pattern, filename) is not None


def check_typescript_component(filename):
    """Check TypeScript component naming"""
    pattern = r"^[A-Z][a-zA-Z0-9]*\.tsx$"
    return re.match(pattern, filename) is not None


def check_typescript_hook(filename):
    """Check TypeScript hook naming"""
    pattern = r"^use[A-Z][a-zA-Z0-9]*\.ts$"
    return re.match(pattern, filename) is not None


def main():
    files = sys.argv[1:]
    found_violations = False

    for filepath in files:
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1]

        # Skip certain files
        if filename in [
            ".gitignore",
            ".env",
            "LICENSE",
            "README.md",
            "Makefile",
            "__init__.py",
        ]:
            continue

        error = None

        # Python files
        if ext == ".py":
            if not check_python_file(filepath):
                error = f"Python file '{filename}' violates naming conventions (see ADR-004 v1.1). Should be kebab-case unless it is a core module or standard test."

        # TypeScript components
        elif ext == ".tsx" and "components" in filepath:
            if not check_typescript_component(filename):
                error = f"Component file '{filename}' should use PascalCase"

        # TypeScript hooks
        elif ext == ".ts" and filename.startswith("use"):
            if not check_typescript_hook(filename):
                error = f"Hook file '{filename}' should match useXxx.ts pattern"

        if error:
            print(f"{filepath}: {error}")
            found_violations = True

    return 1 if found_violations else 0


if __name__ == "__main__":
    sys.exit(main())
