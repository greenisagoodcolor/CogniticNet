#!/usr/bin/env python3
"""
Enhanced Naming Convention Fix Script
Automatically fixes naming convention violations found in the audit with improved error handling
Lead: Robert Martin (Clean Code)
"""

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional


class EnhancedNamingFixer:
    def __init__(self, dry_run: bool = False, priority_mode: bool = False):
        self.dry_run = dry_run
        self.priority_mode = priority_mode
        self.fixed_count = 0
        self.error_count = 0
        self.skipped_count = 0
        self.changes_log = []

        # Load audit report
        audit_path = Path(__file__).parent.parent / "NAMING_AUDIT_REPORT.json"
        if audit_path.exists():
            with open(audit_path, "r") as f:
                self.audit_report = json.load(f)
        else:
            print("Warning: No audit report found. Run audit-naming.py first.")
            self.audit_report = {}

        # Define priority order (1 = highest priority)
        self.priority_order = {
            "prohibited_terms": 1,
            "syntax_errors": 2,  # Skip these for now
            "typescript_components": 3,
            "python_files": 4,
            "typescript_interfaces": 5,
            "typescript_hooks": 6,
            "python_methods": 7,
            "config_files": 8,
            "typescript_handlers": 9,
        }

    def fix_all(self):
        """Fix all naming violations with optional priority mode"""
        print(f"🔧 Enhanced naming fixes{' (DRY RUN)' if self.dry_run else ''}...\n")

        if self.priority_mode:
            self.fix_by_priority()
        else:
            # Fix in traditional order
            self.fix_prohibited_terms()
            self.fix_python_file_names()
            self.fix_typescript_file_names()
            self.fix_config_file_names()
            self.fix_python_code_naming()
            self.fix_typescript_code_naming()

        self.save_changes_log()
        self.print_summary()

    def fix_by_priority(self):
        """Fix violations in priority order"""
        print("📊 Processing violations by priority...\n")

        violation_categories = self.audit_report.get("violations_by_category", {})
        sorted_categories = sorted(
            violation_categories.items(),
            key=lambda x: self.priority_order.get(x[0], 99)
        )

        for category, data in sorted_categories:
            priority = self.priority_order.get(category, 99)
            print(f"Priority {priority}: {category.replace('_', ' ').title()} ({data['count']} violations)")

            if category == "prohibited_terms":
                self.fix_prohibited_terms()
            elif category == "syntax_errors":
                print("   ⚠️  Skipping syntax errors (requires manual fix)")
                self.skipped_count += data['count']
            elif category == "typescript_components":
                self.fix_typescript_file_names()
            elif category == "python_files":
                self.fix_python_file_names()
            elif category == "typescript_interfaces":
                self.fix_typescript_interfaces()
            elif category == "typescript_hooks":
                self.fix_typescript_hooks()
            elif category == "python_methods":
                self.fix_python_code_naming()
            elif category == "config_files":
                self.fix_config_file_names()
            elif category == "typescript_handlers":
                self.fix_typescript_handlers()

            print()  # Empty line between categories

    def fix_prohibited_terms(self):
        """Replace prohibited terms in all files"""
        print("1. Fixing prohibited terms...")

        # Enhanced replacements including new terms
        replacements = {
            "cogniticnet": "freeagentics",
            "CogniticNet": "FreeAgentics",
            "COGNITICNET": "FREEAGENTICS",
            "PlayerAgent": "ExplorerAgent",
            "NPCAgent": "AutonomousAgent",
            "EnemyAgent": "CompetitiveAgent",
            "GameWorld": "Environment",
            "spawn": "initialize",
            "respawn": "reset",
        }

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("prohibited_terms", {})
            .get("violations", [])
        )

        fixed_files = set()
        for violation in violations:
            filepath = violation["file"]
            if filepath in fixed_files:
                continue

            # Skip files that are likely to have intentional references (like this script)
            if "fix-naming.py" in filepath or "audit-naming.py" in filepath:
                print(f"   ⚠️  Skipping {filepath} (contains intentional references)")
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                for old_term, new_term in replacements.items():
                    if old_term in content:
                        content = content.replace(old_term, new_term)
                        self.changes_log.append(
                            {
                                "type": "prohibited_term",
                                "file": filepath,
                                "old": old_term,
                                "new": new_term,
                            }
                        )

                if content != original_content:
                    if not self.dry_run:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)

                    fixed_files.add(filepath)
                    self.fixed_count += 1
                    print(f"   ✓ Fixed prohibited terms in: {filepath}")

            except Exception as e:
                self.error_count += 1
                print(f"   ✗ Error fixing {filepath}: {e}")

    def fix_typescript_interfaces(self):
        """Fix TypeScript interface naming (add I prefix)"""
        print("🔧 Fixing TypeScript interface names...")

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("typescript_interfaces", {})
            .get("violations", [])
        )

        # Group violations by file to process more efficiently
        violations_by_file = {}
        for violation in violations:
            filepath = violation["file"]
            if filepath not in violations_by_file:
                violations_by_file[filepath] = []

            # Extract interface name from issue
            issue = violation["issue"]
            if "Interface '" in issue and "' should start with 'I'" in issue:
                interface_name = issue.split("Interface '")[1].split("'")[0]
                violations_by_file[filepath].append(interface_name)

        fixed_files = 0
        for filepath, interface_names in violations_by_file.items():
            if not os.path.exists(filepath):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                for interface_name in interface_names:
                    # Skip Props interfaces and very common names that might cause issues
                    if ("Props" in interface_name or
                        interface_name in ["State", "Node", "Link", "Data", "Config"]):
                        continue

                    new_name = f"I{interface_name}"

                    # Update interface declaration
                    pattern = f"interface\\s+{re.escape(interface_name)}\\b"
                    replacement = f"interface {new_name}"
                    content = re.sub(pattern, replacement, content)

                    # Update references (be conservative to avoid false positives)
                    content = re.sub(f":\\s*{re.escape(interface_name)}\\b", f": {new_name}", content)
                    content = re.sub(f"<{re.escape(interface_name)}\\b", f"<{new_name}", content)

                if content != original_content:
                    if not self.dry_run:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)

                    fixed_files += 1
                    self.fixed_count += len(interface_names)
                    print(f"   ✓ Fixed interfaces in: {filepath}")

            except Exception as e:
                self.error_count += 1
                print(f"   ✗ Error fixing {filepath}: {e}")

    def fix_typescript_hooks(self):
        """Fix TypeScript hook file naming"""
        print("🔧 Fixing TypeScript hook file names...")

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("typescript_hooks", {})
            .get("violations", [])
        )

        for violation in violations:
            filepath = violation["file"]
            if not os.path.exists(filepath):
                continue

            directory = os.path.dirname(filepath)
            old_name = os.path.basename(filepath)

            # Convert use-xxx-xxx.ts to useXxxXxx.ts
            if old_name.startswith("use-") and old_name.endswith(".ts"):
                # Remove use- prefix and .ts suffix
                middle_part = old_name[4:-3]  # Remove "use-" and ".ts"

                # Convert kebab-case to camelCase
                parts = middle_part.split("-")
                camel_case = parts[0] + "".join(word.capitalize() for word in parts[1:])
                new_name = f"use{camel_case.capitalize()}.ts"

                if old_name != new_name:
                    new_path = os.path.join(directory, new_name)

                    if not self.dry_run:
                        try:
                            subprocess.run(
                                ["git", "mv", filepath, new_path],
                                check=True,
                                capture_output=True,
                            )
                            self.fixed_count += 1
                            print(f"   ✓ Renamed: {old_name} → {new_name}")
                        except subprocess.CalledProcessError:
                            os.rename(filepath, new_path)
                            self.fixed_count += 1
                            print(f"   ✓ Renamed (no git): {old_name} → {new_name}")
                    else:
                        self.fixed_count += 1
                        print(f"   ✓ Would rename: {old_name} → {new_name}")

                    self.changes_log.append(
                        {"type": "hook_rename", "old_path": filepath, "new_path": new_path}
                    )

    def fix_typescript_handlers(self):
        """Fix TypeScript event handler naming"""
        print("🔧 Fixing TypeScript event handler names...")

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("typescript_handlers", {})
            .get("violations", [])
        )

        fixed_files = set()
        for violation in violations:
            filepath = violation["file"]
            if filepath in fixed_files or not os.path.exists(filepath):
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Replace onChange with handleChange, onSelect with handleSelect, etc.
                content = re.sub(r"\bon([A-Z][a-zA-Z0-9]*)\b", r"handle\1", content)

                if content != original_content:
                    if not self.dry_run:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)

                    fixed_files.add(filepath)
                    self.fixed_count += 1
                    print(f"   ✓ Fixed event handlers in: {filepath}")

            except Exception as e:
                self.error_count += 1
                print(f"   ✗ Error fixing {filepath}: {e}")

    def fix_python_file_names(self):
        """Fix Python file naming to kebab-case"""
        print("\n2. Fixing Python file names...")

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("python_files", {})
            .get("violations", [])
        )

        for violation in violations:
            filepath = violation["file"]
            if not os.path.exists(filepath):
                continue

            directory = os.path.dirname(filepath)
            old_name = os.path.basename(filepath)

            # Convert to kebab-case
            new_name = self._to_kebab_case(old_name.replace(".py", "")) + ".py"

            if old_name != new_name:
                new_path = os.path.join(directory, new_name)

                if not self.dry_run:
                    # Use git mv to preserve history
                    try:
                        subprocess.run(
                            ["git", "mv", filepath, new_path],
                            check=True,
                            capture_output=True,
                        )
                        self.fixed_count += 1
                        print(f"   ✓ Renamed: {old_name} → {new_name}")
                    except subprocess.CalledProcessError:
                        # Fallback to regular rename
                        os.rename(filepath, new_path)
                        self.fixed_count += 1
                        print(f"   ✓ Renamed (no git): {old_name} → {new_name}")
                else:
                    self.fixed_count += 1
                    print(f"   ✓ Would rename: {old_name} → {new_name}")

                self.changes_log.append(
                    {"type": "file_rename", "old_path": filepath, "new_path": new_path}
                )

    def fix_typescript_file_names(self):
        """Fix TypeScript component file naming"""
        print("\n3. Fixing TypeScript file names...")

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("typescript_components", {})
            .get("violations", [])
        )

        for violation in violations:
            filepath = violation["file"]
            if not os.path.exists(filepath) or "components" not in filepath:
                continue

            directory = os.path.dirname(filepath)
            old_name = os.path.basename(filepath)

            # Convert kebab-case to PascalCase for components
            if old_name.endswith(".tsx") and "-" in old_name:
                parts = old_name.replace(".tsx", "").split("-")
                new_name = "".join(part.capitalize() for part in parts) + ".tsx"

                if old_name != new_name:
                    new_path = os.path.join(directory, new_name)

                    if not self.dry_run:
                        try:
                            subprocess.run(
                                ["git", "mv", filepath, new_path],
                                check=True,
                                capture_output=True,
                            )
                            self.fixed_count += 1
                            print(f"   ✓ Renamed: {old_name} → {new_name}")
                        except (subprocess.CalledProcessError, OSError):
                            os.rename(filepath, new_path)
                            self.fixed_count += 1
                            print(f"   ✓ Renamed (no git): {old_name} → {new_name}")
                    else:
                        self.fixed_count += 1
                        print(f"   ✓ Would rename: {old_name} → {new_name}")

                    self.changes_log.append(
                        {
                            "type": "file_rename",
                            "old_path": filepath,
                            "new_path": new_path,
                        }
                    )

                    # Update imports in other files
                    self._update_imports(old_name, new_name, directory)

    def fix_config_file_names(self):
        """Fix configuration file naming"""
        print("\n4. Fixing config file names...")

        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("config_files", {})
            .get("violations", [])
        )

        for violation in violations:
            filepath = violation["file"]
            if not os.path.exists(filepath):
                continue

            directory = os.path.dirname(filepath)
            old_name = os.path.basename(filepath)

            # Special cases
            if old_name in ["jest.config.js", "jest.setup.js", "commitlint.config.js"]:
                # These are standard names, skip
                continue

            # Convert to kebab-case
            name_parts = old_name.split(".")
            base_name = name_parts[0]
            extension = ".".join(name_parts[1:])

            new_base = self._to_kebab_case(base_name)
            new_name = f"{new_base}.{extension}"

            if old_name != new_name:
                new_path = os.path.join(directory, new_name)

                if not self.dry_run:
                    try:
                        subprocess.run(
                            ["git", "mv", filepath, new_path],
                            check=True,
                            capture_output=True,
                        )
                        self.fixed_count += 1
                        print(f"   ✓ Renamed: {old_name} → {new_name}")
                    except (IOError, UnicodeDecodeError):
                        pass
                else:
                    self.fixed_count += 1
                    print(f"   ✓ Would rename: {old_name} → {new_name}")

    def fix_python_code_naming(self):
        """Fix Python code naming conventions"""
        print("\n5. Fixing Python code naming...")

        # Fix setUp/tearDown methods in tests
        test_files = []
        for root, dirs, files in os.walk("."):
            if any(skip in root for skip in [".git", "node_modules", "__pycache__"]):
                continue
            for file in files:
                if file.startswith("test") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))

        for filepath in test_files:
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Fix setUp → set_up
                content = re.sub(r"\bdef setUp\(", "def set_up(", content)
                # Fix tearDown → tear_down
                content = re.sub(r"\bdef tearDown\(", "def tear_down(", content)

                if content != original_content:
                    if not self.dry_run:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)

                    self.fixed_count += 1
                    print(f"   ✓ Fixed method names in: {filepath}")

            except Exception as e:
                self.error_count += 1
                print(f"   ✗ Error fixing {filepath}: {e}")

    def fix_typescript_code_naming(self):
        """Fix TypeScript code naming conventions"""
        print("\n6. Fixing TypeScript code naming...")

        # Fix interface names (add I prefix)
        violations = (
            self.audit_report.get("violations_by_category", {})
            .get("typescript_interfaces", {})
            .get("violations", [])
        )

        fixed_files = set()
        for violation in violations[:20]:  # Limit to prevent too many changes
            filepath = violation["file"]
            if filepath in fixed_files or not os.path.exists(filepath):
                continue

            interface_name = violation["issue"].split("'")[1]

            # Skip Props interfaces
            if "Props" in interface_name:
                continue

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content

                # Add I prefix to interface
                new_name = f"I{interface_name}"
                pattern = f"interface\\s+{interface_name}\\b"
                replacement = f"interface {new_name}"

                content = re.sub(pattern, replacement, content)

                # Update all references
                content = re.sub(f":\\s*{interface_name}\\b", f": {new_name}", content)
                content = re.sub(f"<{interface_name}\\b", f"<{new_name}", content)
                content = re.sub(
                    f"extends\\s+{interface_name}\\b", f"extends {new_name}", content
                )

                if content != original_content:
                    if not self.dry_run:
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(content)

                    fixed_files.add(filepath)
                    self.fixed_count += 1
                    print(
                        f"   ✓ Fixed interface {interface_name} → {new_name} in: {filepath}"
                    )

            except Exception as e:
                self.error_count += 1
                print(f"   ✗ Error fixing {filepath}: {e}")

    def _to_kebab_case(self, name: str) -> str:
        """Convert string to kebab-case"""
        # Handle camelCase and PascalCase
        name = re.sub("(.)([A-Z][a-z]+)", r"\1-\2", name)
        name = re.sub("([a-z0-9])([A-Z])", r"\1-\2", name)
        # Handle snake_case
        name = name.replace("_", "-")
        # Clean up and lowercase
        name = re.sub("-+", "-", name)
        return name.lower().strip("-")

    def _update_imports(self, old_name: str, new_name: str, directory: str):
        """Update imports when files are renamed"""
        # This is a simplified version - in production would need more sophisticated import updating
        old_import = old_name.replace(".tsx", "").replace(".ts", "")
        new_import = new_name.replace(".tsx", "").replace(".ts", "")

        for root, dirs, files in os.walk("."):
            if any(skip in root for skip in [".git", "node_modules"]):
                continue

            for file in files:
                if file.endswith((".ts", ".tsx", ".js", ".jsx")):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            content = f.read()

                        if old_import in content:
                            content = content.replace(
                                f"'{old_import}'", f"'{new_import}'"
                            )
                            content = content.replace(
                                f'"{old_import}"', f'"{new_import}"'
                            )
                            content = content.replace(
                                f"/{old_import}", f"/{new_import}"
                            )

                            if not self.dry_run:
                                with open(filepath, "w", encoding="utf-8") as f:
                                    f.write(content)

                            print(f"      Updated imports in: {filepath}")

                    except (IOError, UnicodeDecodeError):
                        pass

    def save_changes_log(self):
        """Save log of all changes made"""
        log_path = "NAMING_FIXES_LOG.json"

        log_data = {
            "dry_run": self.dry_run,
            "fixed_count": self.fixed_count,
            "error_count": self.error_count,
            "changes": self.changes_log,
        }

        with open(log_path, "w") as f:
            json.dump(log_data, f, indent=2)

        print(f"\n📄 Changes log saved to: {log_path}")

    def print_summary(self):
        """Print summary of fixes"""
        print("\n" + "=" * 50)
        print(f"✅ Enhanced Naming Fix Summary{' (DRY RUN)' if self.dry_run else ''}")
        print(f"   Fixed: {self.fixed_count} issues")
        print(f"   Errors: {self.error_count}")
        print(f"   Skipped: {self.skipped_count}")

        total_processed = self.fixed_count + self.error_count + self.skipped_count
        if total_processed > 0:
            success_rate = (self.fixed_count / total_processed) * 100
            print(f"   Success Rate: {success_rate:.1f}%")

        if self.dry_run:
            print("\n⚠️  This was a DRY RUN - no files were actually changed")
            print("   Run with --apply to make the changes")
        elif self.fixed_count > 0:
            print(f"\n📄 Changes log saved to: NAMING_FIXES_LOG.json")
            print("   Consider running tests to verify changes")

        if self.priority_mode:
            print("\n💡 Tip: Review skipped syntax errors manually")
            print("   Run 'python3 scripts/audit-naming.py' to see updated violations")


def main():
    """Run the naming fixes"""
    import argparse

    parser = argparse.ArgumentParser(description="Fix naming convention violations")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making changes",
    )
    parser.add_argument(
        "--apply", action="store_true", help="Actually make the changes"
    )
    parser.add_argument(
        "--priority", action="store_true", help="Fix violations in priority order"
    )

    args = parser.parse_args()

    if not args.apply and not args.dry_run:
        args.dry_run = True

    fixer = EnhancedNamingFixer(dry_run=args.dry_run, priority_mode=args.priority)
    fixer.fix_all()

    if args.dry_run:
        print(
            "\n💡 Tip: Run 'python3 scripts/fix-naming.py --apply' to apply these fixes"
        )


if __name__ == "__main__":
    main()
