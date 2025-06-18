#!/usr/bin/env python3
"""
Check for prohibited terms in source files
"""

import sys

PROHIBITED_TERMS = {
    'PlayerAgent': 'ExplorerAgent',
    'NPCAgent': 'AutonomousAgent',
    'EnemyAgent': 'CompetitiveAgent',
    'GameWorld': 'Environment',
    'spawn': 'initialize',
    'respawn': 'reset',
}

def main():
    files = sys.argv[1:]
    found_violations = False

    for filepath in files:
        # Skip non-source files
        if not any(filepath.endswith(ext) for ext in ['.py', '.ts', '.tsx', '.js', '.jsx']):
            continue

        try:
            with open(filepath, 'r') as f:
                content = f.read()

            for term, replacement in PROHIBITED_TERMS.items():
                if term in content:
                    print(f"{filepath}: Found prohibited term '{term}' - use '{replacement}' instead")
                    found_violations = True
        except:
            pass

    return 1 if found_violations else 0

if __name__ == "__main__":
    sys.exit(main())
