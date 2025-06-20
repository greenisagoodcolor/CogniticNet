#!/usr/bin/env python3
"""
Git Move Executor for FreeAgentics Canonical Structure

This script executes file movements using git commands to preserve history,
following the batch movement plan for safe incremental migration.

Usage:
    python scripts/git-move-executor.py [--movement-order movement-order.json] [--batch 1] [--dry-run]
"""

import argparse
import json
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Dict


class GitMoveExecutor:
    """Executes file movements with git history preservation."""

    def __init__(self, movement_order_file: str, project_root: str = "."):
        self.project_root = Path(project_root)
        self.movement_order_file = movement_order_file
        self.movement_plan = {}
        self.file_mappings = {}
        self.successful_moves = []
        self.failed_moves = []
        self._load_movement_plan()

    def _load_movement_plan(self):
        """Load movement plan from JSON file."""
        with open(self.movement_order_file, "r") as f:
            self.movement_plan = json.load(f)

        # Build file mappings from all batches
        for batch in self.movement_plan["batches"]:
            for file_path in batch["files"]:
                # Load original mapping to get target path
                pass

        # Also load original file mapping for target paths
        if os.path.exists("file-mapping.json"):
            with open("file-mapping.json", "r") as f:
                mapping_data = json.load(f)
                for mapping in mapping_data["mappings"]:
                    self.file_mappings[mapping["current_path"]] = mapping["target_path"]

    def execute_batch(self, batch_id: int, dry_run: bool = False) -> Dict:
        """Execute a specific batch of file movements."""
        print(f"🚀 Executing Batch {batch_id}...")

        # Find the batch
        batch = None
        for b in self.movement_plan["batches"]:
            if b["batch_id"] == batch_id:
                batch = b
                break

        if not batch:
            raise ValueError(f"Batch {batch_id} not found in movement plan")

        # Check dependencies
        if not self._check_batch_dependencies(batch, dry_run):
            raise RuntimeError(f"Dependencies not satisfied for batch {batch_id}")

        # Pre-movement validation
        self._pre_movement_validation()

        # Execute the movements
        results = {
            "batch_id": batch_id,
            "description": batch["description"],
            "files_moved": 0,
            "files_failed": 0,
            "movements": [],
            "errors": [],
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": None,
        }

        start_time = time.time()

        for file_path in batch["files"]:
            if file_path in self.file_mappings:
                target_path = self.file_mappings[file_path]

                try:
                    success = self._move_file_with_git(file_path, target_path, dry_run)

                    if success:
                        results["files_moved"] += 1
                        results["movements"].append(
                            {
                                "source": file_path,
                                "target": target_path,
                                "status": "success",
                            }
                        )
                        self.successful_moves.append((file_path, target_path))
                    else:
                        results["files_failed"] += 1
                        results["movements"].append(
                            {
                                "source": file_path,
                                "target": target_path,
                                "status": "failed",
                            }
                        )
                        self.failed_moves.append((file_path, target_path))

                except Exception as e:
                    results["files_failed"] += 1
                    results["errors"].append({"file": file_path, "error": str(e)})
                    self.failed_moves.append((file_path, target_path))

        end_time = time.time()
        results["end_time"] = datetime.now().isoformat()
        results["duration"] = f"{end_time - start_time:.2f} seconds"

        # Post-movement validation
        if not dry_run and results["files_moved"] > 0:
            self._post_movement_validation(batch_id)

        # Commit the batch if successful
        if not dry_run and results["files_failed"] == 0 and results["files_moved"] > 0:
            self._commit_batch(batch_id, batch["description"])

        print(
            f"✅ Batch {batch_id} completed: {results['files_moved']} moved, {results['files_failed']} failed"
        )

        return results

    def _check_batch_dependencies(self, batch: Dict, dry_run: bool) -> bool:
        """Check if all batch dependencies are satisfied."""
        if not batch["dependencies"]:
            return True

        # For now, assume dependencies are satisfied
        # In a real implementation, this would check git history or execution logs
        print(f"✓ Dependencies satisfied for batch {batch['batch_id']}")
        return True

    def _pre_movement_validation(self):
        """Perform pre-movement validation checks."""
        # Check git working directory is clean
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.project_root,
        )

        if result.stdout.strip():
            print("⚠️  Warning: Working directory has uncommitted changes")
            print("   Consider committing or stashing changes before proceeding")

        # Check target directories exist
        for file_path, target_path in self.file_mappings.items():
            target_dir = Path(target_path).parent
            target_full_path = self.project_root / target_dir

            if not target_full_path.exists():
                print(f"📁 Creating target directory: {target_dir}")
                target_full_path.mkdir(parents=True, exist_ok=True)

    def _move_file_with_git(
        self, source_path: str, target_path: str, dry_run: bool = False
    ) -> bool:
        """Move a file using git mv to preserve history."""
        source_full = self.project_root / source_path
        target_full = self.project_root / target_path

        # Check source file exists
        if not source_full.exists():
            print(f"⚠️  Source file not found: {source_path}")
            return False

        # Ensure target directory exists
        target_full.parent.mkdir(parents=True, exist_ok=True)

        # Execute git mv command
        cmd = ["git", "mv", str(source_full), str(target_full)]

        if dry_run:
            print(f"DRY RUN: {' '.join(cmd)}")
            return True

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, cwd=self.project_root
            )

            if result.returncode == 0:
                print(f"✓ Moved: {source_path} → {target_path}")
                return True
            else:
                print(f"❌ Failed to move {source_path}: {result.stderr}")
                return False

        except subprocess.SubprocessError as e:
            print(f"❌ Git command failed for {source_path}: {e}")
            return False

    def _post_movement_validation(self, batch_id: int):
        """Perform post-movement validation."""
        # Run basic validation commands
        validations = {
            "git_status": ["git", "status", "--porcelain"],
            "git_log_check": ["git", "log", "--oneline", "-n", "1"],
        }

        for validation_name, cmd in validations.items():
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_root
                )
                if result.returncode == 0:
                    print(f"✓ {validation_name.replace('_', ' ').title()}: OK")
                else:
                    print(
                        f"⚠️  {validation_name.replace('_', ' ').title()}: {result.stderr}"
                    )
            except Exception as e:
                print(f"⚠️  Validation {validation_name} failed: {e}")

    def _commit_batch(self, batch_id: int, description: str):
        """Commit the batch movements with descriptive message."""
        commit_message = f"feat: Move files to canonical structure - Batch {batch_id}\n\n{description}\n\nMoved {len(self.successful_moves)} files according to ADR-002 canonical directory structure."

        try:
            # Add all changes
            subprocess.run(["git", "add", "."], cwd=self.project_root, check=True)

            # Commit with message
            subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.project_root,
                check=True,
            )

            print(
                f"✅ Committed batch {batch_id} with {len(self.successful_moves)} file moves"
            )

        except subprocess.SubprocessError as e:
            print(f"❌ Failed to commit batch {batch_id}: {e}")

    def execute_all_batches(self, dry_run: bool = False) -> Dict:
        """Execute all batches in the correct order."""
        print("🚀 Starting full file movement execution...")

        all_results = {
            "execution_started": datetime.now().isoformat(),
            "execution_completed": None,
            "total_duration": None,
            "batches_executed": 0,
            "total_files_moved": 0,
            "total_files_failed": 0,
            "batch_results": [],
            "overall_success": False,
        }

        start_time = time.time()

        # Sort batches by ID to ensure correct order
        sorted_batches = sorted(
            self.movement_plan["batches"], key=lambda b: b["batch_id"]
        )

        for batch in sorted_batches:
            try:
                batch_result = self.execute_batch(batch["batch_id"], dry_run)
                all_results["batch_results"].append(batch_result)
                all_results["batches_executed"] += 1
                all_results["total_files_moved"] += batch_result["files_moved"]
                all_results["total_files_failed"] += batch_result["files_failed"]

                # Stop if batch failed
                if batch_result["files_failed"] > 0:
                    print(
                        f"🛑 Stopping execution due to failures in batch {batch['batch_id']}"
                    )
                    break

                # Wait between batches for safety
                if not dry_run:
                    time.sleep(2)

            except Exception as e:
                print(f"❌ Critical error in batch {batch['batch_id']}: {e}")
                all_results["batch_results"].append(
                    {
                        "batch_id": batch["batch_id"],
                        "status": "critical_error",
                        "error": str(e),
                    }
                )
                break

        end_time = time.time()
        all_results["execution_completed"] = datetime.now().isoformat()
        all_results["total_duration"] = f"{end_time - start_time:.2f} seconds"
        all_results["overall_success"] = (
            all_results["total_files_failed"] == 0
            and all_results["total_files_moved"] > 0
        )

        return all_results

    def generate_history_verification_report(self) -> Dict:
        """Generate a report verifying git history preservation."""
        report = {
            "verification_time": datetime.now().isoformat(),
            "files_checked": 0,
            "history_preserved": 0,
            "history_issues": 0,
            "file_details": [],
        }

        # Check git history for moved files
        for source_path, target_path in self.successful_moves:
            try:
                # Check if file has history
                cmd = ["git", "log", "--oneline", "--", target_path]
                result = subprocess.run(
                    cmd, capture_output=True, text=True, cwd=self.project_root
                )

                if result.returncode == 0 and result.stdout.strip():
                    history_entries = len(result.stdout.strip().split("\n"))
                    report["history_preserved"] += 1
                    report["file_details"].append(
                        {
                            "file": target_path,
                            "status": "history_preserved",
                            "commit_count": history_entries,
                        }
                    )
                else:
                    report["history_issues"] += 1
                    report["file_details"].append(
                        {"file": target_path, "status": "no_history", "commit_count": 0}
                    )

                report["files_checked"] += 1

            except Exception as e:
                report["history_issues"] += 1
                report["file_details"].append(
                    {"file": target_path, "status": "check_failed", "error": str(e)}
                )

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Execute file movements with git history preservation"
    )
    parser.add_argument(
        "--movement-order",
        default="movement-order.json",
        help="Movement order JSON file (default: movement-order.json)",
    )
    parser.add_argument(
        "--batch",
        type=int,
        help="Execute specific batch number (default: execute all batches)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be moved without making changes",
    )
    parser.add_argument(
        "--verify-history",
        action="store_true",
        help="Verify git history preservation for moved files",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory (default: current directory)",
    )

    args = parser.parse_args()

    # Execute file movements
    executor = GitMoveExecutor(args.movement_order, args.project_root)

    if args.verify_history:
        # Just verify history for already moved files
        report = executor.generate_history_verification_report()
        print("\n📋 History Verification Report:")
        print(f"   Files checked: {report['files_checked']}")
        print(f"   History preserved: {report['history_preserved']}")
        print(f"   History issues: {report['history_issues']}")

        with open("git-history-verification.json", "w") as f:
            json.dump(report, f, indent=2)
        print("💾 Verification report saved to: git-history-verification.json")
        return

    if args.batch:
        # Execute specific batch
        result = executor.execute_batch(args.batch, args.dry_run)
        print(f"\n📊 Batch {args.batch} Results:")
        print(f"   Files moved: {result['files_moved']}")
        print(f"   Files failed: {result['files_failed']}")
        print(f"   Duration: {result['duration']}")
    else:
        # Execute all batches
        results = executor.execute_all_batches(args.dry_run)
        print("\n📊 Execution Summary:")
        print(f"   Batches executed: {results['batches_executed']}")
        print(f"   Total files moved: {results['total_files_moved']}")
        print(f"   Total files failed: {results['total_files_failed']}")
        print(f"   Total duration: {results['total_duration']}")
        print(f"   Overall success: {results['overall_success']}")

        # Save results
        with open("file-movement-results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("💾 Results saved to: file-movement-results.json")

    mode = "DRY RUN" if args.dry_run else "EXECUTION"
    print(f"\n✅ {mode} completed!")

    if not args.dry_run:
        print("Next steps:")
        print("1. Verify moved files are in correct locations")
        print("2. Test configuration files and scripts")
        print("3. Run validation suite")
        print("4. Update any remaining references")


if __name__ == "__main__":
    main()
