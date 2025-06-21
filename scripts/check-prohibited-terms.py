#!/usr/bin/env python3
"""
Enhanced Prohibited Terms Checker
Checks for prohibited terms in source files based on naming conventions JSON
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Set


class ProhibitedTermsChecker:
    def __init__(self):
        """Initialize checker with naming conventions"""
        self.conventions_path = (
            Path(__file__).parent.parent / "docs/standards/naming-conventions.json"
        )
        self.prohibited_terms = self._load_prohibited_terms()
        self.source_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".yml", ".yaml"}
        self.skip_paths = {
            "node_modules", ".git", "__pycache__", "vendor", "build", "dist",
            ".venv", "venv", ".next", ".mypy_cache", ".pytest_cache", ".ruff_cache"
        }
        self.source_directories = {
            "agents", "inference", "coalitions", "world", "api", "web",
            "scripts", "docs", "tests", "infrastructure"
        }

    def _load_prohibited_terms(self) -> Dict[str, str]:
        """Load prohibited terms from conventions JSON"""
        try:
            with open(self.conventions_path, "r") as f:
                conventions = json.load(f)

            terms = {}
            for term_info in conventions.get("prohibitedTerms", []):
                terms[term_info["term"]] = term_info["replacement"]
            return terms
        except Exception as e:
            print(f"Warning: Could not load naming conventions: {e}")
            # Fallback to hardcoded terms
            return {
                "ExplorerAgent": "ExplorerAgent",
                "AutonomousAgent": "AutonomousAgent",
                "CompetitiveAgent": "CompetitiveAgent",
                "Environment": "Environment",
                "initialize": "initialize",
                "reinitialize": "reset",
                "freeagentics": "freeagentics",
                "FreeAgentics": "FreeAgentics",
                "FREEAGENTICS": "FREEAGENTICS"
            }

    def should_check_file(self, filepath: str) -> bool:
        """Determine if file should be checked"""
        filepath_obj = Path(filepath)

        # Skip non-existent files
        if not filepath_obj.exists():
            return False

        # Skip directories we don't care about
        if any(part in str(filepath_obj) for part in self.skip_paths):
            return False

        # Only check files with relevant extensions
        if filepath_obj.suffix not in self.source_extensions:
            return False

        # Only check files in our source directories (or root level files)
        parts = filepath_obj.parts
        if len(parts) > 1 and not any(part in parts for part in self.source_directories):
            return False

        return True

    def check_file(self, filepath: str) -> List[str]:
        """Check a single file for prohibited terms"""
        violations = []

        if not self.should_check_file(filepath):
            return violations

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            for term, replacement in self.prohibited_terms.items():
                if term in content:
                    count = content.count(term)
                    violations.append(
                        f"Found prohibited term '{term}' ({count} occurrences) - use '{replacement}' instead"
                    )

        except (IOError, UnicodeDecodeError) as e:
            violations.append(f"Error reading file: {e}")

        return violations

    def check_files(self, filepaths: List[str]) -> bool:
        """Check multiple files and report violations"""
        found_violations = False
        total_violations = 0

        for filepath in filepaths:
            violations = self.check_file(filepath)
            if violations:
                found_violations = True
                print(f"{filepath}:")
                for violation in violations:
                    print(f"  {violation}")
                    total_violations += 1
                print()  # Empty line for readability

        if found_violations:
            print(f"❌ Total violations: {total_violations}")
            print("💡 Run 'python scripts/fix-naming.py --apply' to fix these automatically")
        else:
            print("✅ No prohibited terms found")

        return found_violations

    def get_all_source_files(self) -> List[str]:
        """Get all source files in the project"""
        files = []
        for directory in self.source_directories:
            dir_path = Path(directory)
            if dir_path.exists():
                for ext in self.source_extensions:
                    files.extend(str(p) for p in dir_path.rglob(f"*{ext}"))

        # Add root level files
        for ext in self.source_extensions:
            files.extend(str(p) for p in Path(".").glob(f"*{ext}"))

        return [f for f in files if self.should_check_file(f)]


def main():
    """Main function for command line usage"""
    checker = ProhibitedTermsChecker()

    # If files provided as arguments, check those
    if len(sys.argv) > 1:
        files = sys.argv[1:]
        found_violations = checker.check_files(files)
    else:
        # Check all source files
        print("🔍 Checking all source files for prohibited terms...")
        files = checker.get_all_source_files()
        found_violations = checker.check_files(files)

    return 1 if found_violations else 0


if __name__ == "__main__":
    sys.exit(main())
