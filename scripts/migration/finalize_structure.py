import os
import shutil
from pathlib import Path

# This script finalizes the repository structure by moving the contents
# of the 'freeagentics_new' directory to the project root. It's designed
# to be run from the root of the CogniticNet project.

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SOURCE_DIR = PROJECT_ROOT / "freeagentics"
DEST_DIR = PROJECT_ROOT


def merge_directories(src: Path, dst: Path):
    """
    Recursively merges contents of src directory into dst directory.
    Overwrites files in dst with files from src if they exist.
    """
    print(f"Merging '{src}' into '{dst}'...")
    if not dst.exists():
        os.makedirs(dst)

    for item in os.listdir(src):
        src_path = src / item
        dst_path = dst / item

        if dst_path.is_dir() and src_path.is_dir():
            merge_directories(src_path, dst_path)
        elif dst_path.is_file() and src_path.is_file():
            print(f"  - Overwriting file: {dst_path}")
            shutil.copy2(src_path, dst_path)
            os.remove(src_path)
        elif dst_path.exists():
            print(
                f"  - Conflict: Cannot overwrite {dst_path} with {src_path}. Skipping."
            )
        else:
            print(f"  - Moving: {src_path} -> {dst_path}")
            shutil.move(str(src_path), str(dst_path))


def main():
    """
    Executes the final migration of files to the project root.
    """
    if not SOURCE_DIR.is_dir():
        print(f"Error: Source directory '{SOURCE_DIR}' not found.")
        print("Perhaps the structure has already been finalized.")
        return

    print("Starting structure finalization...")
    print(f"Moving contents from '{SOURCE_DIR}' to '{DEST_DIR}'")

    # We use a temporary name to avoid conflicts if a 'freeagentics' directory
    # already exists at the root for some reason.
    temp_source_name = f"{SOURCE_DIR.name}_temp_move"
    temp_source_dir = PROJECT_ROOT / temp_source_name

    try:
        os.rename(SOURCE_DIR, temp_source_dir)
        print(f"Renamed '{SOURCE_DIR}' to '{temp_source_dir}' for safe processing.")
    except FileNotFoundError:
        print(f"Error: Could not find '{SOURCE_DIR}' to rename.")
        print("Has the move already been partially completed?")
        # Check if the temp dir exists from a previous run
        if temp_source_dir.exists():
            print(
                f"Found existing temp directory '{temp_source_dir}'. Proceeding with merge."
            )
        else:
            return

    # Use the merge logic to move all files and directories
    merge_directories(temp_source_dir, DEST_DIR)

    # Clean up the now-empty temporary source directory
    try:
        if not os.listdir(temp_source_dir):
            os.rmdir(temp_source_dir)
            print(f"Successfully removed empty source directory: '{temp_source_dir}'")
        else:
            print(
                f"Warning: Source directory '{temp_source_dir}' is not empty after move. Manual cleanup may be required."
            )
            print("Remaining items:", os.listdir(temp_source_dir))

    except OSError as e:
        print(f"Error removing source directory '{temp_source_dir}': {e}")

    print("\nStructure finalization complete.")
    print("Next step: Run the cleanup script to remove old, unmigrated files.")


if __name__ == "__main__":
    main()
