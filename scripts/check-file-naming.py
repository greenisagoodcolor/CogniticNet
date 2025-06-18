#!/usr/bin/env python3
"""
Check file naming conventions
"""

import sys
import os
import re

def check_python_file(filename):
    """Check Python file naming"""
    if filename.startswith('test-'):
        pattern = r'^test-[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$'
    elif filename.startswith('_'):
        pattern = r'^_[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$'
    else:
        pattern = r'^[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$'

    return re.match(pattern, filename) is not None

def check_typescript_component(filename):
    """Check TypeScript component naming"""
    pattern = r'^[A-Z][a-zA-Z0-9]*\.tsx$'
    return re.match(pattern, filename) is not None

def check_typescript_hook(filename):
    """Check TypeScript hook naming"""
    pattern = r'^use[A-Z][a-zA-Z0-9]*\.ts$'
    return re.match(pattern, filename) is not None

def main():
    files = sys.argv[1:]
    found_violations = False

    for filepath in files:
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1]

        # Skip certain files
        if filename in ['.gitignore', '.env', 'LICENSE', 'README.md', 'Makefile', '__init__.py']:
            continue

        error = None

        # Python files
        if ext == '.py':
            if not check_python_file(filename):
                error = f"Python file '{filename}' should use kebab-case"

        # TypeScript components
        elif ext == '.tsx' and 'components' in filepath:
            if not check_typescript_component(filename):
                error = f"Component file '{filename}' should use PascalCase"

        # TypeScript hooks
        elif ext == '.ts' and filename.startswith('use'):
            if not check_typescript_hook(filename):
                error = f"Hook file '{filename}' should match useXxx.ts pattern"

        if error:
            print(f"{filepath}: {error}")
            found_violations = True

    return 1 if found_violations else 0

if __name__ == "__main__":
    sys.exit(main())
