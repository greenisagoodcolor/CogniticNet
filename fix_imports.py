#!/usr/bin/env python3
"""
Fix Import Statements

This script fixes import statements that reference modules with hyphens,
replacing them with underscore equivalents.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix import statements in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix import statements with hyphens
        # Pattern: from .module_name import or from ...module-name import
        pattern = r'(from\s+\.+)([a-zA-Z0-9_-]+?)(-[a-zA-Z0-9_-]*?)(\s+import)'

        def replace_import(match):
            prefix = match.group(1)
            module_start = match.group(2)
            hyphen_part = match.group(3)
            suffix = match.group(4)

            # Replace hyphens with underscores in the module name
            fixed_module = module_start + hyphen_part.replace('-', '_')
            return prefix + fixed_module + suffix

        original_content = content
        content = re.sub(pattern, replace_import, content)

        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed imports in: {file_path}")
            return True

        return False

    except Exception as e:
        print(f"⚠️ Error processing {file_path}: {e}")
        return False

def main():
    """Fix all import statements in Python files"""
    fixed_count = 0
    total_count = 0

    # Find all Python files
    for root, dirs, files in os.walk('.'):
        # Skip certain directories
        if any(skip in root for skip in ['.git', 'venv', '__pycache__', '.pytest_cache']):
            continue

        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_count += 1

                if fix_imports_in_file(file_path):
                    fixed_count += 1

    print(f"\n📊 Summary:")
    print(f"   Files processed: {total_count}")
    print(f"   Files fixed: {fixed_count}")

if __name__ == "__main__":
    main()
