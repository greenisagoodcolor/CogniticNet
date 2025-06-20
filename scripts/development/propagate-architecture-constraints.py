import json
from pathlib import Path
from typing import Dict, Any, List

# This script enforces architectural consistency by injecting a critical
# directive into all pending tasks and subtasks.

TASKS_FILE = (
    Path(__file__).resolve().parent.parent.parent
    / ".taskmaster"
    / "tasks"
    / "tasks.json"
)
ADR_PATH = "docs/architecture/decisions/002-canonical-directory-structure.md"
DIRECTIVE = (
    f"**CRITICAL ARCHITECTURAL REQUIREMENT:** All file creation, code placement, "
    f"and modifications must strictly adhere to the project's canonical structure "
    f"defined in `{ADR_PATH}`. Before proceeding, review this document.\n\n---\n\n"
)


def update_task_details(task: Dict[str, Any]):
    """Recursively updates a task and its subtasks."""
    if task.get("status") == "pending":
        original_details = task.get("details", "")
        if not original_details.strip().startswith("**CRITICAL"):
            task["details"] = DIRECTIVE + original_details
            print(f"Updated task: {task['id']} - {task['title']}")

    if "subtasks" in task and task["subtasks"]:
        for subtask in task["subtasks"]:
            update_task_details(subtask)


def main():
    """Main function to update the tasks file."""
    if not TASKS_FILE.exists():
        print(f"Error: Tasks file not found at {TASKS_FILE}")
        return

    print(f"Loading tasks from {TASKS_FILE}...")
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    tasks: List[Dict[str, Any]] = []
    # The tasks are a list at the top level of the JSON file.
    if isinstance(data, list):
        tasks = data
    # Handle the case where it might be under a 'tasks' key
    elif isinstance(data, dict) and "tasks" in data:
        tasks = data["tasks"]
    else:
        print("Error: Could not find a list of tasks in the JSON file.")
        return

    for task in tasks:
        update_task_details(task)

    print(f"Saving updated tasks to {TASKS_FILE}...")
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("Architectural constraints have been propagated to all pending tasks.")


if __name__ == "__main__":
    main()
