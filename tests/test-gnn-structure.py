"""
Test GNN Repository Structure

This test validates that the repository follows the GNN-based structure
and that all components are properly organized.
"""
import os
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestGNNStructure(unittest.TestCase):
    """Test that the repository follows GNN-based structure."""

    def set_up(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent

    def test_directory_structure_exists(self):
        """Test that all required directories exist."""
        required_dirs = ['doc', 'doc/gnn_models', 'src', 'src/gnn', 'src/agents', 'src/world', 'src/knowledge', 'src/learning', 'src/validation', 'src/monitoring', 'src/simulation', 'src/models', 'models', 'models/base', 'tests']
        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            self.assertTrue(full_path.exists(), f"Required directory '{dir_path}' does not exist")

    def test_documentation_files_exist(self):
        """Test that key documentation files exist."""
        required_docs = ['doc/about_platform.md', 'doc/active_inference_guide.md', 'doc/gnn_models/model_format.md']
        for doc_path in required_docs:
            full_path = self.root_dir / doc_path
            self.assertTrue(full_path.exists(), f"Required documentation '{doc_path}' does not exist")

    def test_main_pipeline_exists(self):
        """Test that main.py pipeline orchestrator exists."""
        main_path = self.root_dir / 'src' / 'main.py'
        self.assertTrue(main_path.exists(), "Pipeline orchestrator 'src/main.py' does not exist")
        with open(main_path) as f:
            content = f.read()
            self.assertIn('FreeAgenticsPipeline', content)
            self.assertIn('_stage_parse_gnn', content)
            self.assertIn('_stage_create_agents', content)

    def test_gnn_models_exist(self):
        """Test that GNN model files exist."""
        model_files = ['models/base/explorer.gnn.md', 'models/base/merchant.gnn.md']
        for model_path in model_files:
            full_path = self.root_dir / model_path
            self.assertTrue(full_path.exists(), f"GNN model '{model_path}' does not exist")

    def test_gnn_modules_can_be_imported(self):
        """Test that GNN modules can be imported."""
        try:
            from ....freeagentics_new.inference.gnn.parser import GNNParser
            from ....freeagentics_new.inference.gnn.validator import GNNValidator
            from ....freeagentics_new.inference.gnn.executor import GNNExecutor
            from ....freeagentics_new.inference.gnn.generator import GNNGenerator
        except ImportError as e:
            self.fail(f'Failed to import GNN modules: {e}')

    def test_agent_modules_can_be_imported(self):
        """Test that agent modules can be imported."""
        try:
            from ....freeagentics_new.inference.engine.--init-- import ActiveInferenceAgent
            from ....freeagentics_new.agents.movement-perception import MovementPerceptionSystem
            from agents.core.agents.base.communication import AgentConversation
        except ImportError as e:
            self.fail(f'Failed to import agent modules: {e}')

    def test_world_module_can_be_imported(self):
        """Test that world module can be imported."""
        try:
            from ....freeagentics_new.world.h3-world import H3World
        except ImportError as e:
            self.fail(f'Failed to import world module: {e}')

    def test_knowledge_modules_can_be_imported(self):
        """Test that knowledge modules can be imported."""
        try:
            from knowledge.knowledge_graph import AgentKnowledgeGraph
            from knowledge.knowledge_sharing import KnowledgeSharingProtocol
        except ImportError as e:
            self.fail(f'Failed to import knowledge modules: {e}')

    def test_no_scattered_files(self):
        """Test that there are no scattered Python files in root."""
        root_files = list(self.root_dir.glob('*.py'))
        allowed_root_files = ['setup.py', 'conftest.py']
        unexpected_files = [f for f in root_files if f.name not in allowed_root_files]
        self.assertEqual(len(unexpected_files), 0, f'Found unexpected Python files in root: {[f.name for f in unexpected_files]}')

    def test_clean_separation_of_concerns(self):
        """Test that models directory contains only data (GNN models), not code."""
        models_dir = self.root_dir / 'models'
        py_files = list(models_dir.rglob('*.py'))
        self.assertEqual(len(py_files), 0, f'Models directory should contain only GNN models (data), not Python code. Found: {py_files}')
        gnn_files = list(models_dir.rglob('*.gnn.md'))
        self.assertGreater(len(gnn_files), 0, 'Models directory should contain GNN model files (*.gnn.md)')

    def test_architecture_screams_active_inference(self):
        """Test that the architecture clearly shows this is an Active Inference platform."""
        ai_indicators = [self.root_dir / 'src' / 'agents' / 'active_inference.py', self.root_dir / 'doc' / 'active_inference_guide.md']
        for indicator in ai_indicators:
            self.assertTrue(indicator.exists(), f"Active Inference indicator '{indicator}' not found")
        main_path = self.root_dir / 'src' / 'main.py'
        with open(main_path) as f:
            content = f.read()
            self.assertIn('Active Inference', content)
            self.assertIn('free energy', content.lower())

class TestGNNModelParsing(unittest.TestCase):
    """Test GNN model parsing and validation."""

    def set_up(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(self.root_dir))

    def test_can_parse_base_models(self):
        """Test that base GNN models can be parsed."""
        from ....freeagentics_new.inference.gnn.parser import GNNParser
        parser = GNNParser()
        model_files = [self.root_dir / 'models' / 'base' / 'explorer.gnn.md', self.root_dir / 'models' / 'base' / 'merchant.gnn.md']
        for model_file in model_files:
            if model_file.exists():
                try:
                    model = parser.parse(str(model_file))
                    self.assertIsNotNone(model)
                    self.assertIsNotNone(model.name)
                    self.assertIsNotNone(model.version)
                except Exception as e:
                    self.fail(f'Failed to parse {model_file}: {e}')

    def test_can_validate_models(self):
        """Test that GNN models can be validated."""
        from ....freeagentics_new.inference.gnn.parser import GNNParser
        from ....freeagentics_new.inference.gnn.validator import GNNValidator
        parser = GNNParser()
        validator = GNNValidator()
        model_file = self.root_dir / 'models' / 'base' / 'explorer.gnn.md'
        if model_file.exists():
            try:
                model = parser.parse(str(model_file))
                result = validator.validate(model)
                self.assertTrue(result.is_valid, f'Model validation failed: {result.errors}')
            except Exception as e:
                self.fail(f'Failed to validate model: {e}')

class TestPipelineIntegration(unittest.TestCase):
    """Test pipeline integration."""

    def set_up(self):
        """Set up test environment."""
        self.root_dir = Path(__file__).parent.parent
        sys.path.insert(0, str(self.root_dir))

    def test_pipeline_can_be_imported(self):
        """Test that the pipeline can be imported."""
        try:
            from src.main import FreeAgenticsPipeline
        except ImportError as e:
            self.fail(f'Failed to import pipeline: {e}')

    def test_pipeline_has_all_stages(self):
        """Test that pipeline has all required stages."""
        from src.main import FreeAgenticsPipeline
        pipeline = FreeAgenticsPipeline()
        required_stages = ['initialize', 'parse_gnn', 'create_agents', 'initialize_world', 'run_simulation', 'extract_knowledge', 'share_knowledge', 'evaluate_readiness', 'export']
        for stage in required_stages:
            self.assertIn(stage, pipeline.stages, f"Required stage '{stage}' not found in pipeline")
if __name__ == '__main__':
    unittest.main()
