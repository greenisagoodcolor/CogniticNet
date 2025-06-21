#!/usr/bin/env python3
"""
Enhanced Pre-commit Naming Convention Checker
Comprehensive naming convention validation with detailed reporting
"""

import sys
import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Tuple, Optional


class EnhancedNamingChecker:
    def __init__(self, verbose: bool = False, fail_fast: bool = False):
        """Initialize with enhanced configuration"""
        self.verbose = verbose
        self.fail_fast = fail_fast
        self.conventions = self._load_conventions()
        self.violations = []
        self.stats = {
            "files_checked": 0,
            "files_skipped": 0,
            "violations_found": 0,
            "categories": set()
        }

        # File filtering configuration
        self.skip_patterns = {
            ".gitignore", ".env", "LICENSE", "README.md", "Makefile",
            "__init__.py", "package.json", "tsconfig.json", "jest.config.js",
            "jest.setup.js", "next-env.d.ts", "tailwind.config.ts"
        }
        self.skip_directories = {
            "node_modules", ".git", "__pycache__", "vendor", "build",
            "dist", ".venv", "venv", ".next", ".mypy_cache", ".pytest_cache",
            ".ruff_cache", ".repository_analysis", ".test_reports"
        }

    def _load_conventions(self) -> Dict:
        """Load naming conventions with fallback"""
        conventions_path = (
            Path(__file__).parent.parent / "docs/standards/naming-conventions.json"
        )
        try:
            with open(conventions_path, "r") as f:
                return json.load(f)
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not load naming conventions: {e}")
            # Return minimal fallback conventions
            return {
                "fileNaming": {
                    "python": {"pattern": "^[a-z][a-z0-9]*(-[a-z0-9]+)*\\.py$"},
                    "typescript": {
                        "components": {"pattern": "^[A-Z][a-zA-Z0-9]*\\.tsx$"}
                    }
                },
                "prohibitedTerms": [
                    {"term": "PlayerAgent", "replacement": "ExplorerAgent"},
                    {"term": "CogniticNet", "replacement": "FreeAgentics"}
                ]
            }

    def should_check_file(self, filepath: str) -> bool:
        """Enhanced file filtering logic"""
        path_obj = Path(filepath)

        # Skip non-existent files
        if not path_obj.exists():
            return False

        filename = path_obj.name

        # Skip specific files
        if filename in self.skip_patterns:
            return False

        # Skip directories
        if any(skip_dir in str(path_obj) for skip_dir in self.skip_directories):
            return False

        # Only check source files
        if not any(filepath.endswith(ext) for ext in [".py", ".ts", ".tsx", ".js", ".jsx"]):
            return False

        return True

    def check_file_naming(self, filepath: str) -> List[str]:
        """Enhanced file naming validation"""
        errors = []
        path_obj = Path(filepath)
        filename = path_obj.name
        ext = path_obj.suffix

        try:
            # Python files
            if ext == ".py":
                errors.extend(self._check_python_file_naming(filepath, filename))

            # TypeScript/JavaScript files
            elif ext in [".ts", ".tsx"]:
                errors.extend(self._check_typescript_file_naming(filepath, filename))

        except Exception as e:
            errors.append(f"Error checking file naming: {e}")

        return errors

    def _check_python_file_naming(self, filepath: str, filename: str) -> List[str]:
        """Check Python file naming conventions"""
        errors = []
        patterns = self.conventions.get("fileNaming", {}).get("python", {})

        if filename.startswith("test-") or filename.startswith("test_"):
            # Test files - allow both patterns but prefer kebab-case
            if not re.match(r"^test[-_][a-z][a-z0-9]*[-_][a-z0-9]*\.py$", filename):
                if "_" in filename:
                    suggested = filename.replace("_", "-")
                    errors.append(f"Test file '{filename}' should use kebab-case: '{suggested}'")
                else:
                    errors.append(f"Test file '{filename}' doesn't match test naming pattern")
        elif filename.startswith("_"):
            # Private files
            if not re.match(r"^_[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$", filename):
                errors.append(f"Private file '{filename}' should use kebab-case after underscore")
        else:
            # Regular files
            pattern = patterns.get("pattern", "^[a-z][a-z0-9]*(-[a-z0-9]+)*\\.py$")
            if not re.match(pattern, filename):
                if "_" in filename:
                    suggested = filename.replace("_", "-")
                    errors.append(f"Python file '{filename}' should use kebab-case: '{suggested}'")
                else:
                    errors.append(f"Python file '{filename}' doesn't match kebab-case pattern")

        return errors

    def _check_typescript_file_naming(self, filepath: str, filename: str) -> List[str]:
        """Check TypeScript file naming conventions"""
        errors = []

        # Component files
        if "components" in filepath and filename.endswith(".tsx"):
            if not re.match(r"^[A-Z][a-zA-Z0-9]*\.tsx$", filename):
                if "-" in filename:
                    # Convert kebab-case to PascalCase
                    name_part = filename.replace(".tsx", "")
                    suggested = "".join(word.capitalize() for word in name_part.split("-")) + ".tsx"
                    errors.append(f"Component '{filename}' should use PascalCase: '{suggested}'")
                else:
                    errors.append(f"Component '{filename}' should use PascalCase")

        # Hook files
        elif filename.startswith("use") and filename.endswith(".ts"):
            if not re.match(r"^use[A-Z][a-zA-Z0-9]*\.ts$", filename):
                if "-" in filename:
                    # Convert use-xxx-xxx to useXxxXxx
                    name_part = filename.replace("use-", "").replace(".ts", "")
                    camel_case = "".join(word.capitalize() for word in name_part.split("-"))
                    suggested = f"use{camel_case}.ts"
                    errors.append(f"Hook '{filename}' should use camelCase: '{suggested}'")
                else:
                    errors.append(f"Hook '{filename}' should match useXxx.ts pattern")

        return errors

    def check_code_content(self, filepath: str, content: str) -> List[str]:
        """Enhanced code content validation"""
        errors = []

        try:
            # Check for prohibited terms
            for term_info in self.conventions.get("prohibitedTerms", []):
                term = term_info["term"]
                if term in content:
                    replacement = term_info["replacement"]
                    count = content.count(term)
                    errors.append(
                        f"Found prohibited term '{term}' ({count}x) - use '{replacement}' instead"
                    )

            # Additional content checks based on file type
            if filepath.endswith(".py"):
                errors.extend(self._check_python_content(content))
            elif filepath.endswith((".ts", ".tsx")):
                errors.extend(self._check_typescript_content(content))

        except Exception as e:
            errors.append(f"Error checking content: {e}")

        return errors

    def _check_python_content(self, content: str) -> List[str]:
        """Check Python code naming conventions"""
        errors = []

        # Basic regex checks for common violations
        # Class names should be PascalCase
        class_matches = re.findall(r"class\s+([a-z][a-zA-Z0-9_]*)", content)
        for match in class_matches:
            if "_" in match or not match[0].isupper():
                errors.append(f"Class '{match}' should use PascalCase")

        # Function names should be snake_case
        func_matches = re.findall(r"def\s+([A-Z][a-zA-Z0-9_]*)", content)
        for match in func_matches:
            if match[0].isupper():
                suggested = re.sub(r'([A-Z])', r'_\1', match).lower().lstrip('_')
                errors.append(f"Function '{match}' should use snake_case: '{suggested}'")

        return errors

    def _check_typescript_content(self, content: str) -> List[str]:
        """Check TypeScript code naming conventions"""
        errors = []

        # Interface names should start with I (for domain interfaces)
        interface_matches = re.findall(r"interface\s+([A-Z][a-zA-Z0-9]*)", content)
        for match in interface_matches:
            if not match.startswith("I") and "Props" not in match:
                errors.append(f"Interface '{match}' should start with 'I' prefix")

        # Event handlers should start with 'handle'
        handler_matches = re.findall(r"(on[A-Z][a-zA-Z0-9]*)\s*=", content)
        for match in handler_matches:
            suggested = match.replace("on", "handle", 1)
            errors.append(f"Event handler '{match}' should use 'handle' prefix: '{suggested}'")

        return errors

    def check_files(self, filepaths: List[str]) -> bool:
        """Check multiple files and collect violations"""
        for filepath in filepaths:
            if not self.should_check_file(filepath):
                self.stats["files_skipped"] += 1
                continue

            self.stats["files_checked"] += 1
            file_violations = []

            # Check file naming
            naming_errors = self.check_file_naming(filepath)
            if naming_errors:
                for error in naming_errors:
                    self.violations.append((filepath, "file_naming", error))
                    file_violations.append(error)

            # Check file content
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                content_errors = self.check_code_content(filepath, content)
                if content_errors:
                    for error in content_errors:
                        self.violations.append((filepath, "content", error))
                        file_violations.append(error)

            except Exception as e:
                error_msg = f"Error reading file: {e}"
                self.violations.append((filepath, "read_error", error_msg))
                file_violations.append(error_msg)

            # Update statistics
            if file_violations:
                self.stats["violations_found"] += len(file_violations)

            # Fail fast if requested
            if self.fail_fast and file_violations:
                break

        return len(self.violations) == 0

    def report_violations(self) -> None:
        """Generate comprehensive violation report"""
        if not self.violations:
            print("✅ No naming convention violations found")
            if self.verbose:
                print(f"   Files checked: {self.stats['files_checked']}")
                print(f"   Files skipped: {self.stats['files_skipped']}")
            return

        print("❌ Naming convention violations found:\n")

        # Group violations by file
        violations_by_file = {}
        for filepath, category, error in self.violations:
            if filepath not in violations_by_file:
                violations_by_file[filepath] = []
            violations_by_file[filepath].append((category, error))

        # Report violations
        for filepath, file_violations in violations_by_file.items():
            print(f"📁 {filepath}:")
            for category, error in file_violations:
                icon = "📝" if category == "file_naming" else "🔍" if category == "content" else "❌"
                print(f"   {icon} {error}")
            print()

        # Summary
        print(f"📊 Summary:")
        print(f"   Total violations: {len(self.violations)}")
        print(f"   Files with issues: {len(violations_by_file)}")
        print(f"   Files checked: {self.stats['files_checked']}")

        print("\n💡 Run one of these to fix automatically:")
        print("   python scripts/enhanced-fix-naming.py --dry-run --priority")
        print("   python scripts/enhanced-fix-naming.py --apply --priority")


def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Check naming conventions")
    parser.add_argument("files", nargs="*", help="Files to check (default: from git)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first violation")
    parser.add_argument("--all", action="store_true", help="Check all source files")

    args = parser.parse_args()

    checker = EnhancedNamingChecker(verbose=args.verbose, fail_fast=args.fail_fast)

    # Determine files to check
    if args.all:
        # Check all source files
        files = []
        for ext in [".py", ".ts", ".tsx", ".js", ".jsx"]:
            files.extend(str(p) for p in Path(".").rglob(f"*{ext}"))
        files = [f for f in files if checker.should_check_file(f)]
    elif args.files:
        # Check specified files
        files = args.files
    else:
        # Check files from command line (pre-commit hook mode)
        files = sys.argv[1:] if len(sys.argv) > 1 else []

    if not files:
        print("No files to check")
        return 0

    # Run checks
    success = checker.check_files(files)
    checker.report_violations()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
