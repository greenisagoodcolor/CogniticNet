#!/usr/bin/env python3
"""
2_parse_gnn.py - Parse and Validate GNN Models

This script handles parsing and validation of GNN model files,
ensuring all agent models are properly formatted and ready for use.
"""

import sys
import logging
from pathlib import Path
import json
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from gnn.parser import GNNParser
from gnn.validator import GNNValidator

logger = logging.getLogger(__name__)


class ParseGNNStep:
    """Handles GNN model parsing and validation."""
    
    def __init__(self, args):
        self.args = args
        self.models_dir = Path(args.models_dir)
        self.output_dir = Path(args.output_dir) / "2_parse_gnn"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.parser = GNNParser()
        self.validator = GNNValidator()
        
    def run(self):
        """Execute the GNN parsing process."""
        logger.info(f"Parsing GNN models from {self.models_dir}")
        
        results = {
            'step': 'parse_gnn',
            'status': 'started',
            'models': {},
            'summary': {
                'total': 0,
                'valid': 0,
                'invalid': 0
            }
        }
        
        try:
            # Find all GNN model files
            model_files = self._find_model_files()
            results['summary']['total'] = len(model_files)
            
            if not model_files:
                logger.warning("No GNN model files found")
                results['status'] = 'completed'
                self._save_results(results)
                return True
            
            # Parse and validate each model
            for model_file in model_files:
                model_result = self._process_model(model_file)
                results['models'][str(model_file)] = model_result
                
                if model_result['valid']:
                    results['summary']['valid'] += 1
                else:
                    results['summary']['invalid'] += 1
            
            # Determine overall status
            if results['summary']['invalid'] == 0:
                results['status'] = 'completed'
                logger.info(f"All {results['summary']['valid']} models parsed successfully")
            else:
                results['status'] = 'completed_with_errors'
                logger.warning(
                    f"Parsed {results['summary']['valid']} valid models, "
                    f"{results['summary']['invalid']} invalid"
                )
            
            # Save results
            self._save_results(results)
            
            # Save valid models separately
            self._save_valid_models(results)
            
            return results['summary']['invalid'] == 0
            
        except Exception as e:
            logger.error(f"GNN parsing error: {e}")
            results['status'] = 'error'
            results['error'] = str(e)
            self._save_results(results)
            return False
    
    def _find_model_files(self) -> List[Path]:
        """Find all GNN model files in the models directory."""
        model_files = []
        
        if self.args.recursive:
            pattern = "**/*.gnn.md"
        else:
            pattern = "*.gnn.md"
            
        for file_path in self.models_dir.glob(pattern):
            model_files.append(file_path)
            
        logger.info(f"Found {len(model_files)} GNN model files")
        return sorted(model_files)
    
    def _process_model(self, model_file: Path) -> Dict[str, Any]:
        """Process a single GNN model file."""
        logger.debug(f"Processing {model_file}")
        
        result = {
            'file': str(model_file.relative_to(self.models_dir)),
            'valid': False,
            'parsed': False,
            'errors': [],
            'warnings': [],
            'model_data': None
        }
        
        try:
            # Parse the model
            model = self.parser.parse_file(str(model_file))
            result['parsed'] = True
            
            # Validate the model
            validation_result = self.validator.validate(model)
            
            result['valid'] = validation_result.is_valid
            result['errors'] = validation_result.errors
            result['warnings'] = validation_result.warnings
            
            if result['valid']:
                # Store model data
                result['model_data'] = {
                    'name': model.name,
                    'version': model.version,
                    'agent_class': model.agent_class,
                    'metadata': model.metadata,
                    'beliefs': len(model.beliefs) if model.beliefs else 0,
                    'preferences': len(model.preferences) if model.preferences else 0,
                    'policies': len(model.policies) if model.policies else 0
                }
                
        except Exception as e:
            result['errors'].append(f"Parse error: {str(e)}")
            logger.error(f"Error processing {model_file}: {e}")
            
        return result
    
    def _save_results(self, results: Dict[str, Any]):
        """Save parsing results."""
        output_file = self.output_dir / 'gnn_parsing_report.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {output_file}")
        
        # Also create a markdown report
        self._create_markdown_report(results)
    
    def _save_valid_models(self, results: Dict[str, Any]):
        """Save valid models for use by other pipeline steps."""
        valid_models = {}
        
        for file_path, model_result in results['models'].items():
            if model_result['valid'] and model_result['model_data']:
                valid_models[file_path] = model_result['model_data']
        
        output_file = self.output_dir / 'valid_models.json'
        with open(output_file, 'w') as f:
            json.dump(valid_models, f, indent=2)
        logger.info(f"Valid models saved to {output_file}")
    
    def _create_markdown_report(self, results: Dict[str, Any]):
        """Create a human-readable markdown report."""
        output_file = self.output_dir / 'gnn_parsing_report.md'
        
        with open(output_file, 'w') as f:
            f.write("# GNN Model Parsing Report\n\n")
            f.write(f"**Status**: {results['status']}\n")
            f.write(f"**Total Models**: {results['summary']['total']}\n")
            f.write(f"**Valid**: {results['summary']['valid']}\n")
            f.write(f"**Invalid**: {results['summary']['invalid']}\n\n")
            
            if results['summary']['valid'] > 0:
                f.write("## Valid Models\n\n")
                for file_path, model in results['models'].items():
                    if model['valid']:
                        f.write(f"### {model['file']}\n")
                        if model['model_data']:
                            data = model['model_data']
                            f.write(f"- **Name**: {data['name']}\n")
                            f.write(f"- **Version**: {data['version']}\n")
                            f.write(f"- **Class**: {data['agent_class']}\n")
                            f.write(f"- **Beliefs**: {data['beliefs']}\n")
                            f.write(f"- **Preferences**: {data['preferences']}\n")
                            f.write(f"- **Policies**: {data['policies']}\n\n")
            
            if results['summary']['invalid'] > 0:
                f.write("## Invalid Models\n\n")
                for file_path, model in results['models'].items():
                    if not model['valid']:
                        f.write(f"### {model['file']}\n")
                        for error in model['errors']:
                            f.write(f"- ❌ {error}\n")
                        f.write("\n")


def main(args):
    """Main entry point for GNN parsing step."""
    step = ParseGNNStep(args)
    return step.run()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--models-dir', default='models')
    parser.add_argument('--output-dir', default='output')
    parser.add_argument('--recursive', action='store_true')
    args = parser.parse_args()
    
    logging.basicConfig(level=logging.INFO)
    success = main(args)
    sys.exit(0 if success else 1) 