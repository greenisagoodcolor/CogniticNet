#!/usr/bin/env python3
"""
Check for prohibited terms in source files
"""

import sys
from pathlib import Path

PROHIBITED_TERMS = {
    "PlayerAgent": "ExplorerAgent",
    "NPCAgent": "AutonomousAgent",
    "EnemyAgent": "CompetitiveAgent",
    "GameWorld": "Environment",
}


def main():
    files = sys.argv[1:]
    found_violations = False

    for filepath in files:
        filepath_obj = Path(filepath)

        # Skip node_modules, vendor directories, and other generated content
        if any(
            part in str(filepath_obj)
            for part in [
                "node_modules",
                ".git",
                "__pycache__",
                "vendor",
                "build",
                "dist",
            ]
        ):
            continue

        # Only check our source files
        if not any(
            filepath.endswith(ext) for ext in [".py", ".ts", ".tsx", ".js", ".jsx"]
        ):
            continue

        # Skip files outside our main source directories
        if not any(
            part in str(filepath_obj)
            for part in [
                "agents",
                "inference",
                "coalitions",
                "world",
                "api",
                "web",
                "scripts",
            ]
        ):
            continue

        try:
            with open(filepath, "r") as f:
                content = f.read()

            for term, replacement in PROHIBITED_TERMS.items():
                if term in content:
                    print(
                        f"{filepath}: Found prohibited term '{term}' - use '{replacement}' instead"
                    )
                    found_violations = True
        except (IOError, UnicodeDecodeError):
            pass

    return 1 if found_violations else 0


if __name__ == "__main__":
    sys.exit(main())
