#!/usr/bin/env python3
"""
1_initialize.py - Environment Setup and Validation

This script handles the initialization phase of the FreeAgentics pipeline,
ensuring all dependencies are installed and the environment is properly configured.
"""

import os
import sys
import logging
from pathlib import Path
import subprocess
import json

logger = logging.getLogger(__name__)


class InitializationStep:
    """Handles environment setup and validation for FreeAgentics."""

    def __init__(self, args):
        self.args = args
        self.root_dir = Path(__file__).parent.parent.parent
        self.output_dir = Path(args.output_dir) / "1_initialize"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """Execute the initialization process."""
        logger.info("Starting FreeAgentics initialization...")

        results = {"step": "initialize", "status": "started", "checks": {}}

        try:
            # Check Python version
            results["checks"]["python_version"] = self._check_python_version()

            # Check required directories
            results["checks"]["directories"] = self._check_directories()

            # Check Python dependencies
            results["checks"]["python_deps"] = self._check_python_dependencies()

            # Check Node.js and npm
            results["checks"]["nodejs"] = self._check_nodejs()

            # Check environment configuration
            results["checks"]["environment"] = self._check_environment()

            # Check database connectivity
            if not self.args.skip_db:
                results["checks"]["database"] = self._check_database()

            # Validate all checks passed
            all_passed = all(
                check.get("status") == "passed" for check in results["checks"].values()
            )

            results["status"] = "completed" if all_passed else "failed"

            # Save results
            self._save_results(results)

            if not all_passed:
                logger.error("Initialization failed. Please fix the issues above.")
                return False

            logger.info("Initialization completed successfully!")
            return True

        except Exception as e:
            logger.error(f"Initialization error: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            self._save_results(results)
            return False

    def _check_python_version(self):
        """Ensure Python version is 3.11+."""
        version = sys.version_info
        required = (3, 11)

        passed = version >= required

        return {
            "status": "passed" if passed else "failed",
            "current": f"{version.major}.{version.minor}.{version.micro}",
            "required": f"{required[0]}.{required[1]}+",
            "message": "Python version check",
        }

    def _check_directories(self):
        """Ensure required directories exist."""
        required_dirs = ["src", "models", "doc", "tests", "app", "components", "lib"]

        missing = []
        for dir_name in required_dirs:
            dir_path = self.root_dir / dir_name
            if not dir_path.exists():
                missing.append(dir_name)

        return {
            "status": "passed" if not missing else "failed",
            "required": required_dirs,
            "missing": missing,
            "message": "Directory structure check",
        }

    def _check_python_dependencies(self):
        """Check if Python dependencies are installed."""
        try:
            import numpy
            import networkx
            import sklearn
            import fastapi
            import pydantic

            return {"status": "passed", "message": "Core Python dependencies installed"}
        except ImportError as e:
            return {
                "status": "failed",
                "message": f"Missing Python dependency: {e.name}",
                "hint": "Run: pip install -r requirements.txt",
            }

    def _check_nodejs(self):
        """Check Node.js and npm installation."""
        try:
            node_version = subprocess.check_output(
                ["node", "--version"], text=True
            ).strip()

            npm_version = subprocess.check_output(
                ["npm", "--version"], text=True
            ).strip()

            return {
                "status": "passed",
                "node_version": node_version,
                "npm_version": npm_version,
                "message": "Node.js environment ready",
            }
        except (subprocess.CalledProcessError, FileNotFoundError):
            return {
                "status": "failed",
                "message": "Node.js not found",
                "hint": "Install Node.js 18+ from https://nodejs.org",
            }

    def _check_environment(self):
        """Check environment configuration."""
        env_file = self.root_dir / ".env"

        if not env_file.exists():
            return {
                "status": "warning",
                "message": "No .env file found",
                "hint": "Copy environments/.env.example to .env and configure",
            }

        # Check for required env vars
        required_vars = ["ANTHROPIC_API_KEY", "DATABASE_URL", "JWT_SECRET"]

        missing = []
        for var in required_vars:
            if not os.getenv(var):
                missing.append(var)

        return {
            "status": "passed" if not missing else "warning",
            "missing_vars": missing,
            "message": "Environment configuration check",
        }

    def _check_database(self):
        """Check database connectivity."""
        try:
            # This would normally test the actual connection
            # For now, just check if DATABASE_URL is set
            db_url = os.getenv("DATABASE_URL")

            if not db_url:
                return {"status": "failed", "message": "DATABASE_URL not configured"}

            return {"status": "passed", "message": "Database configuration found"}
        except Exception as e:
            return {"status": "failed", "message": f"Database check failed: {e}"}

    def _save_results(self, results):
        """Save initialization results."""
        output_file = self.output_dir / "initialization_report.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")


def main(args):
    """Main entry point for initialization step."""
    step = InitializationStep(args)
    return step.run()


if __name__ == "__main__":
    # This allows running the script directly
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--skip-db", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    success = main(args)
    sys.exit(0 if success else 1)
