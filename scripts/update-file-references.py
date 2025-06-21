#!/usr/bin/env python3
"""
File Reference Updater for FreeAgentics Canonical Structure

This script updates import statements, configuration references, and file paths
after files have been moved to the new canonical directory structure.

Usage:
    python scripts/update-file-references.py [--mapping file-mapping.json] [--dry-run]
"""

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple


class ReferenceUpdater:
    """Updates file references after canonical structure migration."""

    def __init__(self, mapping_file: str, project_root: str = "."):
        self.project_root = Path(project_root)
        self.mapping_file = mapping_file
        self.file_mappings = {}
        self.files_processed = 0
        self.references_updated = 0
        self._load_mappings()

        # Define patterns for different file types that might reference moved files
        self.config_reference_patterns = {
            # Package.json may reference configuration files
            "package.json": [
                (
                    r'"(?:eslintConfig|prettier)"\s*:\s*"([^"]*)"',
                    "config file reference",
                ),
                (
                    r'"(?:lint-staged)"\s*:\s*{[^}]*"([^"]*eslintrc[^"]*)"',
                    "lint-staged config",
                ),
            ],
            # VS Code settings may reference config files
            ".vscode/settings.json": [
                (
                    r'"[^"]*\.(?:eslintrc|prettierrc|editorconfig)"',
                    "tool config reference",
                ),
            ],
            # GitHub workflows may reference scripts
            ".github/workflows/*.yml": [
                (
                    r'(?:run|script):\s*(?:\.\/)?scripts\/([^"\s\n]+)',
                    "script reference",
                ),
            ],
            # Docker files may reference scripts or configs
            "Dockerfile*": [
                (r"COPY\s+(?:\.\/)?scripts\/([^\s]+)", "script copy"),
                (r"RUN\s+(?:\.\/)?scripts\/([^\s]+)", "script execution"),
            ],
            # Make files may reference scripts
            "Makefile*": [
                (r"(?:^|\s)(?:\.\/)?scripts\/([^\s]+)", "makefile script"),
            ],
            # Shell scripts may reference other scripts or configs
            "*.sh": [
                (r"source\s+(?:\.\/)?scripts\/([^\s]+)", "script sourcing"),
                (r"(?:\.\/)?scripts\/([^\s\n]+)", "script reference"),
            ],
            # Python files may import or reference other files
            "*.py": [
                (r"from\s+scripts\.([^\s]+)\s+import", "python import"),
                (r"import\s+scripts\.([^\s]+)", "python import"),
                (r'(?:open|Path)\(["\'](?:\.\/)?scripts\/([^"\']+)["\']', "file path"),
            ],
            # TypeScript/JavaScript files
            "*.{ts,js,tsx,jsx}": [
                (r'import.*["\'](?:\.\/)?scripts\/([^"\']+)["\']', "js/ts import"),
                (
                    r'require\(["\'](?:\.\/)?scripts\/([^"\']+)["\']\)',
                    "require statement",
                ),
            ],
        }

    def _load_mappings(self):
        """Load file mappings from JSON file."""
        with open(self.mapping_file, "r") as f:
            data = json.load(f)

        # Convert to easier lookup format
        for mapping in data["mappings"]:
            self.file_mappings[mapping["current_path"]] = mapping["target_path"]

    def update_all_references(self, dry_run: bool = False) -> Dict:
        """Update all file references based on the mapping."""
        print("🔍 Scanning for file references to update...")

        results = {
            "files_processed": 0,
            "references_updated": 0,
            "files_with_updates": [],
            "errors": [],
        }

        # Scan all relevant files for references
        for pattern, reference_patterns in self.config_reference_patterns.items():
            files_to_check = self._find_files_by_pattern(pattern)

            for file_path in files_to_check:
                try:
                    updates = self._update_file_references(
                        file_path, reference_patterns, dry_run
                    )
                    if updates:
                        results["files_with_updates"].append(
                            {"file": str(file_path), "updates": updates}
                        )
                        results["references_updated"] += len(updates)

                    results["files_processed"] += 1

                except Exception as e:
                    results["errors"].append({"file": str(file_path), "error": str(e)})

        self.files_processed = results["files_processed"]
        self.references_updated = results["references_updated"]

        return results

    def _find_files_by_pattern(self, pattern: str) -> List[Path]:
        """Find files matching a glob pattern."""
        files = []

        # Handle different pattern types
        if "*" in pattern:
            # Glob pattern
            for match in self.project_root.glob(pattern):
                if match.is_file():
                    files.append(match)
        else:
            # Exact file name
            file_path = self.project_root / pattern
            if file_path.exists() and file_path.is_file():
                files.append(file_path)

        return files

    def _update_file_references(
        self,
        file_path: Path,
        reference_patterns: List[Tuple[str, str]],
        dry_run: bool = False,
    ) -> List[Dict]:
        """Update references in a specific file."""
        updates = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Apply each reference pattern
            for pattern, description in reference_patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)

                for match in matches:
                    # Extract the referenced file path
                    if match.groups():
                        referenced_file = match.group(1)
                    else:
                        referenced_file = match.group(0)

                    # Check if this file has been moved
                    old_path = self._normalize_path(referenced_file)
                    if old_path in self.file_mappings:
                        new_path = self.file_mappings[old_path]

                        # Update the content
                        old_match = match.group(0)
                        new_match = old_match.replace(old_path, new_path)
                        content = content.replace(old_match, new_match)

                        updates.append(
                            {
                                "pattern": description,
                                "old_reference": old_path,
                                "new_reference": new_path,
                                "line_content": old_match.strip(),
                            }
                        )

            # Write updated content if changes were made
            if content != original_content and not dry_run:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")

        return updates

    def _normalize_path(self, path: str) -> str:
        """Normalize a file path for consistent comparison."""
        # Remove leading ./ if present
        if path.startswith("./"):
            path = path[2:]

        # Convert to Path and back to string for normalization
        return str(Path(path))

    def update_package_json_references(self, dry_run: bool = False) -> List[Dict]:
        """Update package.json script references to moved files."""
        updates = []
        package_json = self.project_root / "package.json"

        if not package_json.exists():
            return updates

        try:
            with open(package_json, "r") as f:
                content = f.read()

            original_content = content

            # Look for script references in package.json
            for old_path, new_path in self.file_mappings.items():
                if old_path in content:
                    # Update script references
                    content = content.replace(f'"{old_path}"', f'"{new_path}"')
                    content = content.replace(f"'{old_path}'", f"'{new_path}'")
                    content = content.replace(f"{old_path}", f"{new_path}")

                    updates.append(
                        {
                            "file": "package.json",
                            "old_reference": old_path,
                            "new_reference": new_path,
                            "type": "script_reference",
                        }
                    )

            if content != original_content and not dry_run:
                with open(package_json, "w") as f:
                    f.write(content)

        except Exception as e:
            print(f"⚠️  Error updating package.json: {e}")

        return updates

    def update_readme_references(self, dry_run: bool = False) -> List[Dict]:
        """Update README file references to moved files."""
        updates = []
        readme_files = ["README.md", "README.rst", "README.txt"]

        for readme_name in readme_files:
            readme_path = self.project_root / readme_name
            if not readme_path.exists():
                continue

            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Update file references in markdown links and code blocks
                for old_path, new_path in self.file_mappings.items():
                    # Markdown links: [text](path)
                    content = re.sub(
                        rf"\[([^\]]*)\]\({re.escape(old_path)}\)",
                        rf"[\1]({new_path})",
                        content,
                    )

                    # Code blocks and inline code
                    content = content.replace(f"`{old_path}`", f"`{new_path}`")
                    content = content.replace(f"```{old_path}```", f"```{new_path}```")

                    if old_path in content:
                        updates.append(
                            {
                                "file": readme_name,
                                "old_reference": old_path,
                                "new_reference": new_path,
                                "type": "documentation_reference",
                            }
                        )

                if content != original_content and not dry_run:
                    with open(readme_path, "w", encoding="utf-8") as f:
                        f.write(content)

            except Exception as e:
                print(f"⚠️  Error updating {readme_name}: {e}")

        return updates

    def generate_update_report(self, results: Dict) -> Dict:
        """Generate comprehensive update report."""
        return {
            "summary": {
                "files_processed": results["files_processed"],
                "references_updated": results["references_updated"],
                "files_with_updates": len(results["files_with_updates"]),
                "errors": len(results["errors"]),
            },
            "detailed_updates": results["files_with_updates"],
            "errors": results["errors"],
            "most_common_patterns": self._analyze_update_patterns(results),
            "validation_needed": self._identify_validation_files(results),
        }

    def _analyze_update_patterns(self, results: Dict) -> List[Dict]:
        """Analyze most common update patterns."""
        pattern_counts = {}

        for file_update in results["files_with_updates"]:
            for update in file_update["updates"]:
                pattern = update["pattern"]
                if pattern not in pattern_counts:
                    pattern_counts[pattern] = 0
                pattern_counts[pattern] += 1

        # Sort by frequency
        sorted_patterns = sorted(
            pattern_counts.items(), key=lambda x: x[1], reverse=True
        )

        return [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted_patterns[:5]
        ]

    def _identify_validation_files(self, results: Dict) -> List[str]:
        """Identify files that need manual validation after updates."""
        validation_files = set()

        # Files with configuration updates need validation
        for file_update in results["files_with_updates"]:
            file_path = file_update["file"]

            # Configuration files need tool validation
            if any(
                config in file_path
                for config in [".eslintrc", ".prettierrc", "package.json"]
            ):
                validation_files.add(file_path)

            # Script files need execution validation
            if file_path.endswith(".sh") or "script" in file_path:
                validation_files.add(file_path)

        return sorted(list(validation_files))


def main():
    parser = argparse.ArgumentParser(
        description="Update file references after canonical structure migration"
    )
    parser.add_argument(
        "--mapping",
        default="file-mapping.json",
        help="File mapping JSON file (default: file-mapping.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without making changes",
    )
    parser.add_argument(
        "--output",
        default="reference-updates.json",
        help="Output file for update report (default: reference-updates.json)",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Update file references
    updater = ReferenceUpdater(args.mapping, args.project_root)

    print("🔄 Starting file reference updates...")

    # Update general references
    results = updater.update_all_references(args.dry_run)

    # Update specific file types
    package_updates = updater.update_package_json_references(args.dry_run)
    readme_updates = updater.update_readme_references(args.dry_run)

    # Combine all updates
    all_updates = results.copy()
    if package_updates:
        all_updates["files_with_updates"].extend(
            [{"file": "package.json", "updates": package_updates}]
        )
    if readme_updates:
        all_updates["files_with_updates"].extend(
            [{"file": "README.md", "updates": readme_updates}]
        )

    # Generate report
    report = updater.generate_update_report(all_updates)

    # Print summary
    mode = "DRY RUN" if args.dry_run else "UPDATE"
    print(f"\n📊 {mode} Summary:")
    print(f"   Files processed: {report['summary']['files_processed']}")
    print(f"   References updated: {report['summary']['references_updated']}")
    print(f"   Files with updates: {report['summary']['files_with_updates']}")
    print(f"   Errors: {report['summary']['errors']}")

    if report["validation_needed"]:
        print("\n🔍 Files needing validation:")
        for file_path in report["validation_needed"]:
            print(f"   - {file_path}")

    # Save report
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n💾 Update report saved to: {args.output}")

    if not args.dry_run and report["summary"]["references_updated"] > 0:
        print("\n✅ Reference updates completed!")
        print("Next steps:")
        print("1. Test configuration files (eslint, prettier, etc.)")
        print("2. Verify script execution")
        print("3. Run build pipeline")
        print("4. Commit changes")
    elif args.dry_run:
        print("\n🔍 Dry run completed. Use --no-dry-run to apply changes.")


if __name__ == "__main__":
    main()
