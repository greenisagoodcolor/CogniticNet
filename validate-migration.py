#!/usr/bin/env python3
"""
Validate Migration Script
Ensures all files were moved correctly and no data was lost
Lead: Martin Fowler
"""

import os
import subprocess
import json
from collections import defaultdict


def count_files_by_extension(directory):
    """Count files by extension in a directory"""
    counts = defaultdict(int)
    total_size = 0

    for root, dirs, files in os.walk(directory):
        # Skip .git and node_modules
        if ".git" in root or "node_modules" in root:
            continue

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext:
                counts[ext] += 1
            else:
                counts["no_extension"] += 1

            # Get file size
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except:
                pass

    return dict(counts), total_size


def check_git_history():
    """Verify git history is preserved"""
    try:
        # Check if we can see history for moved files
        result = subprocess.run(
            ["git", "log", "--oneline", "-n", "5", "agents/base/data_model.py"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout:
            return (
                True,
                f"Git history preserved: {len(result.stdout.splitlines())} commits found",
            )
        else:
            return False, "Git history check failed"
    except Exception as e:
        return False, f"Git history check error: {e}"


def check_critical_files():
    """Check that critical files exist in new locations"""
    critical_files = [
        # Core agent files
        "agents/base/__init__.py",
        "agents/base/data_model.py",
        "agents/base/communication.py",
        # Active Inference
        "inference/engine/active-inference.py",
        "inference/engine/belief-update.py",
        "inference/gnn/__init__.py",
        # World
        "world/h3_world.py",
        "world/spatial/spatial_api.py",
        # API
        "api/rest/agents/route.ts",
        # Frontend
        "web/src/components/agent-dashboard.tsx",
        "web/src/lib/llm-client.ts",
        # Tests
        "tests/unit/test_agent_data_model.py",
        "tests/integration/test_active_inference_integration.py",
        # Documentation
        "docs/active-inference/README.md",
        # Config
        "package.json",
        "tsconfig.json",
        "pyproject.toml",
    ]

    missing_files = []
    found_files = []

    for file in critical_files:
        if os.path.exists(file):
            found_files.append(file)
        else:
            missing_files.append(file)

    return missing_files, found_files


def check_imports():
    """Verify no broken imports remain"""
    broken_imports = []

    # Python import patterns that should NOT exist
    bad_patterns = [
        "from agents.core.basic_agent",
        "import agents.core.basic_agent",
        "from agents.core.active_inference",
        "from src.gnn",
        "from src.world",
        "from src.tests",
    ]

    for root, dirs, files in os.walk("."):
        if ".git" in root or "node_modules" in root:
            continue

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for pattern in bad_patterns:
                        if pattern in content:
                            broken_imports.append((file_path, pattern))
                except:
                    pass

    return broken_imports


def check_old_references():
    """Check for any remaining FreeAgentics references"""
    old_references = []

    patterns = ["FreeAgentics", "freeagentics", "cogneticnet"]

    for root, dirs, files in os.walk("."):
        if ".git" in root or "node_modules" in root or ".taskmaster" in root:
            continue

        for file in files:
            if file.endswith(
                (".py", ".ts", ".tsx", ".js", ".jsx", ".md", ".yml", ".yaml")
            ):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    for line_num, line in enumerate(content.splitlines(), 1):
                        for pattern in patterns:
                            if pattern in line:
                                old_references.append((file_path, line_num, pattern))
                                break
                except:
                    pass

    return old_references


def main():
    """Run all validation checks"""
    print("🔍 Validating FreeAgentics Migration...\n")

    # 1. Count files
    print("1. File Count Analysis:")
    file_counts, total_size = count_files_by_extension(".")
    print(f"   Total files: {sum(file_counts.values())}")
    print(f"   Total size: {total_size / 1024 / 1024:.2f} MB")
    print(f"   Python files: {file_counts.get('.py', 0)}")
    print(
        f"   TypeScript files: {file_counts.get('.ts', 0) + file_counts.get('.tsx', 0)}"
    )
    print(
        f"   JavaScript files: {file_counts.get('.js', 0) + file_counts.get('.jsx', 0)}"
    )

    # 2. Check git history
    print("\n2. Git History Check:")
    history_ok, history_msg = check_git_history()
    print(f"   {'✅' if history_ok else '❌'} {history_msg}")

    # 3. Check critical files
    print("\n3. Critical Files Check:")
    missing, found = check_critical_files()
    print(f"   ✅ Found {len(found)} critical files")
    if missing:
        print(f"   ❌ Missing {len(missing)} files:")
        for file in missing[:5]:  # Show first 5
            print(f"      - {file}")
        if len(missing) > 5:
            print(f"      ... and {len(missing) - 5} more")

    # 4. Check imports
    print("\n4. Import Check:")
    broken = check_imports()
    if broken:
        print(f"   ❌ Found {len(broken)} files with old imports:")
        for file, pattern in broken[:5]:
            print(f"      - {file}: {pattern}")
    else:
        print("   ✅ No broken imports found")

    # 5. Check old references
    print("\n5. Old Reference Check:")
    old_refs = check_old_references()
    if old_refs:
        print(f"   ⚠️  Found {len(old_refs)} remaining FreeAgentics references:")
        for file, line, pattern in old_refs[:5]:
            print(f"      - {file}:{line} ({pattern})")
        if len(old_refs) > 5:
            print(f"      ... and {len(old_refs) - 5} more")
    else:
        print("   ✅ No old references found")

    # Summary
    print("\n" + "=" * 50)
    issues = len(missing) + len(broken) + (0 if history_ok else 1)

    if issues == 0 and len(old_refs) == 0:
        print("✅ MIGRATION VALIDATED SUCCESSFULLY!")
        print("   All files moved correctly with git history preserved.")
    else:
        print(f"⚠️  MIGRATION COMPLETED WITH {issues} ISSUES")
        if not history_ok:
            print("   - Git history issue detected")
        if missing:
            print(f"   - {len(missing)} missing critical files")
        if broken:
            print(f"   - {len(broken)} broken imports")
        if old_refs:
            print(f"   - {len(old_refs)} old references (non-critical)")

    # Save report
    report = {
        "file_counts": file_counts,
        "total_size_mb": total_size / 1024 / 1024,
        "git_history_ok": history_ok,
        "missing_files": missing,
        "broken_imports": [{"file": f, "pattern": p} for f, p in broken],
        "old_references_count": len(old_refs),
    }

    with open("VALIDATION_REPORT.json", "w") as f:
        json.dump(report, f, indent=2)

    print("\n📄 Detailed report saved to: VALIDATION_REPORT.json")


if __name__ == "__main__":
    main()
