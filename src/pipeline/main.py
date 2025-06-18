#!/usr/bin/env python3
"""
CogniticNet Pipeline Orchestrator

This script discovers and executes numbered pipeline steps in order,
following the GNN pattern for modular processing.

Usage:
    python src/pipeline/main.py [options]
    
    # Run all steps
    python src/pipeline/main.py
    
    # Run specific steps
    python src/pipeline/main.py --only-steps 1,2
    
    # Skip certain steps
    python src/pipeline/main.py --skip-steps 4,5
"""

import sys
import os
import argparse
import logging
import importlib.util
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineOrchestrator:
    """Orchestrates the execution of numbered pipeline steps."""
    
    def __init__(self, args):
        self.args = args
        self.pipeline_dir = Path(__file__).parent
        self.output_dir = Path(args.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Pipeline state
        self.steps_executed = []
        self.results = {}
        self.start_time = None
        
    def discover_steps(self) -> List[Dict[str, Any]]:
        """Discover all numbered pipeline scripts."""
        steps = []
        
        # Find all scripts matching pattern [number]_*.py
        for file_path in sorted(self.pipeline_dir.glob("[0-9]*.py")):
            if file_path.name == "main.py":
                continue
                
            # Extract step number and name
            parts = file_path.stem.split("_", 1)
            if len(parts) == 2:
                try:
                    step_num = int(parts[0])
                    step_name = parts[1]
                    
                    steps.append({
                        'number': step_num,
                        'name': step_name,
                        'file': file_path,
                        'module_name': file_path.stem
                    })
                except ValueError:
                    logger.warning(f"Skipping invalid step file: {file_path}")
        
        return sorted(steps, key=lambda x: x['number'])
    
    def should_run_step(self, step: Dict[str, Any]) -> bool:
        """Determine if a step should be run based on filters."""
        step_num = step['number']
        step_name = step['name']
        
        # Check --only-steps
        if self.args.only_steps:
            only_list = [s.strip() for s in self.args.only_steps.split(',')]
            # Check both number and name
            if str(step_num) not in only_list and step_name not in only_list:
                return False
        
        # Check --skip-steps
        if self.args.skip_steps:
            skip_list = [s.strip() for s in self.args.skip_steps.split(',')]
            # Check both number and name
            if str(step_num) in skip_list or step_name in skip_list:
                return False
                
        return True
    
    def load_step_module(self, step: Dict[str, Any]):
        """Dynamically load a pipeline step module."""
        spec = importlib.util.spec_from_file_location(
            step['module_name'], 
            step['file']
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    
    def run_step(self, step: Dict[str, Any]) -> bool:
        """Execute a single pipeline step."""
        step_name = f"{step['number']}_{step['name']}"
        logger.info(f"\n{'='*60}")
        logger.info(f"Running step {step['number']}: {step['name']}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Load the module
            module = self.load_step_module(step)
            
            # Check for main function
            if not hasattr(module, 'main'):
                logger.error(f"Step {step_name} missing main() function")
                return False
            
            # Prepare step-specific args
            step_args = argparse.Namespace(**vars(self.args))
            
            # Execute the step
            success = module.main(step_args)
            
            elapsed = time.time() - start_time
            
            # Record results
            self.results[step_name] = {
                'success': success,
                'elapsed_seconds': elapsed,
                'timestamp': datetime.now().isoformat()
            }
            
            if success:
                logger.info(f"✅ Step {step_name} completed in {elapsed:.2f}s")
            else:
                logger.error(f"❌ Step {step_name} failed after {elapsed:.2f}s")
                
            return success
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Error in step {step_name}: {e}")
            
            self.results[step_name] = {
                'success': False,
                'elapsed_seconds': elapsed,
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            return False
    
    def run(self) -> bool:
        """Run the entire pipeline."""
        self.start_time = time.time()
        
        logger.info("CogniticNet Pipeline Starting...")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Discover available steps
        steps = self.discover_steps()
        
        if not steps:
            logger.error("No pipeline steps found!")
            return False
        
        logger.info(f"Discovered {len(steps)} pipeline steps")
        
        # Filter steps based on arguments
        steps_to_run = [s for s in steps if self.should_run_step(s)]
        
        if not steps_to_run:
            logger.warning("No steps to run after filtering")
            return True
        
        logger.info(f"Will run {len(steps_to_run)} steps: " + 
                   ", ".join(f"{s['number']}_{s['name']}" for s in steps_to_run))
        
        # Execute steps in order
        all_success = True
        
        for step in steps_to_run:
            success = self.run_step(step)
            self.steps_executed.append(step)
            
            if not success:
                all_success = False
                if not self.args.continue_on_error:
                    logger.error("Stopping pipeline due to step failure")
                    break
        
        # Save pipeline results
        self._save_results(all_success)
        
        total_elapsed = time.time() - self.start_time
        logger.info(f"\n{'='*60}")
        logger.info(f"Pipeline {'completed' if all_success else 'failed'} in {total_elapsed:.2f}s")
        logger.info(f"{'='*60}")
        
        return all_success
    
    def _save_results(self, overall_success: bool):
        """Save pipeline execution results."""
        report = {
            'pipeline': 'CogniticNet',
            'version': '1.0.0',
            'execution': {
                'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
                'end_time': datetime.now().isoformat(),
                'total_seconds': time.time() - self.start_time,
                'success': overall_success
            },
            'configuration': {
                'output_dir': str(self.output_dir),
                'models_dir': self.args.models_dir,
                'only_steps': self.args.only_steps,
                'skip_steps': self.args.skip_steps
            },
            'steps': self.results
        }
        
        # Save JSON report
        report_file = self.output_dir / 'pipeline_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save markdown summary
        self._save_markdown_summary(report)
        
        logger.info(f"Pipeline report saved to {report_file}")
    
    def _save_markdown_summary(self, report: Dict[str, Any]):
        """Create a human-readable summary."""
        summary_file = self.output_dir / 'pipeline_summary.md'
        
        with open(summary_file, 'w') as f:
            f.write("# CogniticNet Pipeline Execution Summary\n\n")
            f.write(f"**Date**: {report['execution']['start_time']}\n")
            f.write(f"**Duration**: {report['execution']['total_seconds']:.2f} seconds\n")
            f.write(f"**Status**: {'✅ Success' if report['execution']['success'] else '❌ Failed'}\n\n")
            
            f.write("## Steps Executed\n\n")
            f.write("| Step | Status | Duration |\n")
            f.write("|------|--------|----------|\n")
            
            for step_name, result in report['steps'].items():
                status = "✅" if result['success'] else "❌"
                duration = f"{result['elapsed_seconds']:.2f}s"
                f.write(f"| {step_name} | {status} | {duration} |\n")
            
            f.write("\n## Configuration\n\n")
            f.write(f"- **Output Directory**: `{report['configuration']['output_dir']}`\n")
            f.write(f"- **Models Directory**: `{report['configuration']['models_dir']}`\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CogniticNet Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Pipeline control
    parser.add_argument(
        '--only-steps', 
        help='Comma-separated list of steps to run (e.g., "1,2" or "initialize,parse_gnn")'
    )
    parser.add_argument(
        '--skip-steps', 
        help='Comma-separated list of steps to skip'
    )
    parser.add_argument(
        '--continue-on-error', 
        action='store_true',
        help='Continue running steps even if one fails'
    )
    
    # Directories
    parser.add_argument(
        '--output-dir', 
        default='output',
        help='Base directory for all output files (default: output)'
    )
    parser.add_argument(
        '--models-dir', 
        default='models',
        help='Directory containing GNN model files (default: models)'
    )
    
    # Common options passed to steps
    parser.add_argument(
        '--recursive', 
        action='store_true',
        help='Process directories recursively'
    )
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--dev', 
        action='store_true',
        help='Run in development mode'
    )
    parser.add_argument(
        '--skip-db', 
        action='store_true',
        help='Skip database checks'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run pipeline
    orchestrator = PipelineOrchestrator(args)
    success = orchestrator.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 