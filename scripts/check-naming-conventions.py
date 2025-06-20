#!/usr/bin/env python3
"""
Pre-commit hook to check naming conventions
"""

import sys
import os
import re
import json
from pathlib import Path


def load_conventions():
    """Load naming conventions from JSON file"""
    conventions_path = (
        Path(__file__).parent.parent / "docs/standards/naming-conventions.json"
    )
    with open(conventions_path, "r") as f:
        return json.load(f)


def check_file_naming(filepath, conventions):
    """Check if file name follows conventions"""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1]

    # Skip certain files
    if filename in [".gitignore", ".env", "LICENSE", "README.md", "Makefile"]:
        return True

    errors = []

    # Python files
    if ext == ".py":
        patterns = conventions["fileNaming"]["python"]

        if filename.startswith("test-"):
            pattern = patterns["testPattern"]
            if not re.match(pattern, filename):
                errors.append(
                    f"Test file '{filename}' doesn't match pattern: {pattern}"
                )
        elif filename.startswith("_"):
            pattern = patterns["privatePattern"]
            if not re.match(pattern, filename):
                errors.append(
                    f"Private file '{filename}' doesn't match pattern: {pattern}"
                )
        else:
            pattern = patterns["pattern"]
            if not re.match(pattern, filename):
                errors.append(
                    f"Python file '{filename}' doesn't match kebab-case pattern"
                )

    # TypeScript/JavaScript files
    elif ext in [".ts", ".tsx"]:
        # Component files
        if "components" in filepath and ext == ".tsx":
            pattern = conventions["fileNaming"]["typescript"]["components"]["pattern"]
            if not re.match(pattern, filename):
                errors.append(f"Component '{filename}' should be PascalCase")

        # Hook files
        elif filename.startswith("use"):
            pattern = conventions["fileNaming"]["typescript"]["hooks"]["pattern"]
            if not re.match(pattern, filename):
                errors.append(f"Hook '{filename}' doesn't match useXxx.ts pattern")

    return errors


def check_code_content(filepath, content, conventions):
    """Check code content for naming violations"""
    errors = []

    # Check for prohibited terms
    for term_info in conventions["prohibitedTerms"]:
        term = term_info["term"]
        if term in content:
            errors.append(
                f"Found prohibited term '{term}' - use '{term_info['replacement']}' instead"
            )

    return errors


def main():
    """Main pre-commit hook function"""
    conventions = load_conventions()
    files = sys.argv[1:]

    all_errors = []

    for filepath in files:
        # Skip non-source files
        if not any(
            filepath.endswith(ext) for ext in [".py", ".ts", ".tsx", ".js", ".jsx"]
        ):
            continue

        # Check file naming
        file_errors = check_file_naming(filepath, conventions)
        if file_errors:
            all_errors.extend([(filepath, err) for err in file_errors])

        # Check file content
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            content_errors = check_code_content(filepath, content, conventions)
            if content_errors:
                all_errors.extend([(filepath, err) for err in content_errors])
        except Exception as e:
            all_errors.append((filepath, f"Error reading file: {e}"))

    # Report errors
    if all_errors:
        print("❌ Naming convention violations found:\n")
        for filepath, error in all_errors:
            print(f"  {filepath}: {error}")
        print(f"\n❌ Total violations: {len(all_errors)}")
        print(
            "\n💡 Run 'python scripts/fix-naming.py --apply' to fix some issues automatically"
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
