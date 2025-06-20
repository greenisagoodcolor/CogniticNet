#!/usr/bin/env python3
"""
Update the migration plan to only include files that still exist in their original locations.
"""

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
MIGRATION_PLAN_PATH = PROJECT_ROOT / "migration-plan.json"
UPDATED_PLAN_PATH = PROJECT_ROOT / "migration-plan-updated.json"


def main():
    """Update migration plan with only existing files."""

    if not MIGRATION_PLAN_PATH.exists():
        print(f"Original migration plan not found at {MIGRATION_PLAN_PATH}")
        return

    with open(MIGRATION_PLAN_PATH, "r") as f:
        original_plan = json.load(f)

    updated_plan = []

    for item in original_plan:
        source_path = Path(item["source"])

        # Only include if source file still exists
        if source_path.exists():
            updated_plan.append(item)
        else:
            print(f"Skipping {source_path} (already moved or doesn't exist)")

    print(f"Original plan: {len(original_plan)} files")
    print(f"Updated plan: {len(updated_plan)} files")

    with open(UPDATED_PLAN_PATH, "w") as f:
        json.dump(updated_plan, f, indent=2)

    print(f"Updated migration plan saved to {UPDATED_PLAN_PATH}")


if __name__ == "__main__":
    main()
