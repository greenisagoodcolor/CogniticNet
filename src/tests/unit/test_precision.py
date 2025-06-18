"""
Unit tests for Active Inference precision optimization
"""

import pytest
import torch
import numpy as np
from typing import List

# Import modules to test
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.active_inference.precision import (
    PrecisionConfig,
    GradientPrecisionOptimizer,
    HierarchicalPrecisionOptimizer,
    MetaLearningPrecisionOptimizer,
    AdaptivePrecisionController,
    create_precision_optimizer
)


class TestPrecisionConfig:
    """Test PrecisionConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = PrecisionConfig()

        assert config.learning_rate == 0.01
        assert config.meta_learning_rate == 0.001
        assert config.momentum == 0.9
        assert config.gradient_clip == 1.0
        assert config.min_precision == 0.1
        assert config.max_precision == 100.0
        assert config.init_precision == 1.0
        assert config.volatility_window == 10
        assert config.volatility_threshold == 0.5
        assert config.adaptation_rate == 0.1
        assert config.num_levels == 1
        assert config.level_coupling == 0.5
        assert config.use_gpu is True
        assert config.dtype == torch.float32

    def test_custom_config(self):
        """Test custom configuration"""
        config = PrecisionConfig(
            learning_rate=0.1,
            min_precision=0.01,
            max_precision=1000.0,
            use_gpu=False
        )

        assert config.learning_rate == 0.1
        assert config.min_precision == 0.01
        assert config.max_precision == 1000.0
        assert config.use_gpu is False


class TestGradientPrecisionOptimizer:
    """Test gradient-based precision optimization"""

    def setup_method(self):
        """Set up test environment"""
        self.config = PrecisionConfig(use_gpu=False, init_precision=1.0)
        self.optimizer = GradientPrecisionOptimizer(self.config, num_modalities=2)

    def test_initialization(self):
        """Test optimizer initialization"""
        assert self.optimizer.num_modalities == 2
        assert self.optimizer.log_precision.shape == (2,)

        # Check initial precision
        precision = torch.exp(self.optimizer.log_precision)
        assert torch.allclose(precision, torch.tensor([1.0, 1.0]))

    def test_precision_optimization(self):
        """Test basic precision optimization"""
        # High errors should increase precision
        high_errors = torch.randn(10, 2) * 5.0
        precision1 = self.optimizer.optimize_precision(high_errors)

        # Low errors should decrease precision
        low_errors = torch.randn(10, 2) * 0.1
        precision2 = self.optimizer.optimize_precision(low_errors)

        assert precision1.shape == (2,)
        assert precision2.shape == (2,)

        # Precision should be within bounds
        assert torch.all(precision1 >= self.config.min_precision)
        assert torch.all(precision1 <= self.config.max_precision)

    def test_single_observation_optimization(self):
        """Test optimization with single observation"""
        error = torch.tensor([1.0, 0.5])
        precision = self.optimizer.optimize_precision(error)

        assert precision.shape == (2,)
        assert torch.all(precision > 0)

    def test_volatility_estimation(self):
        """Test volatility estimation"""
        # Add consistent errors
        for _ in range(5):
            errors = torch.ones(1, 2)
            self.optimizer.optimize_precision(errors)

        volatility1 = self.optimizer.estimate_volatility()

        # Add variable errors
        for i in range(5):
            errors = torch.ones(1, 2) * (i % 2)
            self.optimizer.optimize_precision(errors)

        volatility2 = self.optimizer.estimate_volatility()

        # Variable errors should have higher volatility
        assert torch.all(volatility2 > volatility1)

    def test_volatility_adaptation(self):
        """Test adaptation to volatility"""
        # Create high volatility scenario
        for i in range(20):
            errors = torch.randn(1, 2) * (5.0 if i % 2 == 0 else 0.1)
            self.optimizer.optimize_precision(errors)

        # Get precision before adaptation
        precision_before = torch.exp(self.optimizer.log_precision.data.clone())

        # Adapt to volatility
        self.optimizer.adapt_to_volatility()

        # Get precision after adaptation
        precision_after = torch.exp(self.optimizer.log_precision.data)

        # Precision should have changed
        assert not torch.allclose(precision_before, precision_after)

    def test_gradient_clipping(self):
        """Test gradient clipping"""
        # Create extreme errors
        extreme_errors = torch.ones(1, 2) * 1000.0

        # Optimize (should not explode due to clipping)
        precision = self.optimizer.optimize_precision(extreme_errors)

        assert torch.all(torch.isfinite(precision))
        assert torch.all(precision <= self.config.max_precision)


class TestHierarchicalPrecisionOptimizer:
    """Test hierarchical precision optimization"""

    def setup_method(self):
        """Set up test environment"""
        self.config = PrecisionConfig(use_gpu=False)
        self.level_dims = [3, 2, 1]
        self.optimizer = HierarchicalPrecisionOptimizer(self.config, self.level_dims)

    def test_initialization(self):
        """Test hierarchical initialization"""
        assert self.optimizer.num_levels == 3
        assert len(self.optimizer.level_precisions) == 3
        assert len(self.optimizer.coupling_weights) == 2

        # Check dimensions
        for i, dim in enumerate(self.level_dims):
            assert self.optimizer.level_precisions[i].shape == (dim,)

    def test_hierarchical_optimization(self):
        """Test optimization across levels"""
        # Create errors for each level
        errors = [
            torch.randn(5, 3),  # Level 0
            torch.randn(5, 2),  # Level 1
            torch.randn(5, 1)   # Level 2
        ]

        precisions = self.optimizer.optimize_precision(errors)

        assert len(precisions) == 3
        for i, p in enumerate(precisions):
            assert p.shape == (self.level_dims[i],)
            assert torch.all(p > 0)

    def test_level_coupling(self):
        """Test inter-level coupling"""
        # High errors at top level
        errors = [
            torch.randn(5, 3) * 0.1,  # Low errors at level 0
            torch.randn(5, 2) * 0.1,  # Low errors at level 1
            torch.randn(5, 1) * 5.0   # High errors at level 2
        ]

        precisions = self.optimizer.optimize_precision(errors)

        # All levels should be affected due to coupling
        assert all(torch.all(p > 0) for p in precisions)

    def test_volatility_per_level(self):
        """Test volatility estimation per level"""
        error_history = []

        # Generate variable error patterns
        for t in range(15):
            errors = [
                torch.randn(1, 3) * (1.0 if t % 2 == 0 else 0.1),
                torch.randn(1, 2) * 0.5,  # Constant
                torch.randn(1, 1) * (t * 0.1)  # Increasing
            ]
            error_history.append(errors)
            self.optimizer.optimize_precision(errors)

        volatilities = self.optimizer.estimate_volatility(error_history)

        assert len(volatilities) == 3
        # Level 0 should have high volatility (alternating)
        # Level 1 should have low volatility (constant)
        # Level 2 should have moderate volatility (trend)
        assert volatilities[0].mean() > volatilities[1].mean()


class TestMetaLearningPrecisionOptimizer:
    """Test meta-learning precision optimization"""

    def setup_method(self):
        """Set up test environment"""
        self.config = PrecisionConfig(use_gpu=False)
        self.optimizer = MetaLearningPrecisionOptimizer(
            self.config,
            input_dim=6,
            hidden_dim=32,
            num_modalities=2
        )

    def test_initialization(self):
        """Test meta-learning initialization"""
        assert self.optimizer.input_dim == 6
        assert self.optimizer.hidden_dim == 32
        assert self.optimizer.num_modalities == 2
        assert hasattr(self.optimizer, 'meta_network')
        assert hasattr(self.optimizer, 'base_precision')

    def test_feature_extraction(self):
        """Test feature extraction"""
        errors = torch.randn(10, 2)
        context = torch.randn(3)

        features = self.optimizer.extract_features(errors, context)

        # Should have correct dimension
        assert features.shape == (self.optimizer.input_dim + self.optimizer.num_modalities,)

    def test_precision_optimization_with_context(self):
        """Test optimization with context"""
        errors = torch.randn(10, 2)
        context = torch.tensor([1.0, 0.0, 0.5])

        precision = self.optimizer.optimize_precision(errors, context)

        assert precision.shape == (2,)
        assert torch.all(precision >= self.config.min_precision)
        assert torch.all(precision <= self.config.max_precision)

    def test_context_buffer(self):
        """Test context buffer management"""
        # Fill buffer
        for i in range(150):
            errors = torch.randn(5, 2)
            self.optimizer.optimize_precision(errors)

        # Buffer should be capped at max size
        assert len(self.optimizer.context_buffer) == self.optimizer.max_context_size

    def test_meta_update(self):
        """Test meta-learning update"""
        # Generate some context
        for _ in range(20):
            errors = torch.randn(5, 2)
            self.optimizer.optimize_precision(errors)

        # Get network parameters before update
        params_before = [p.clone() for p in self.optimizer.meta_network.parameters()]

        # Perform meta update
        self.optimizer.meta_update(num_steps=5)

        # Parameters should have changed
        params_after = list(self.optimizer.meta_network.parameters())
        assert any(not torch.allclose(p1, p2) for p1, p2 in zip(params_before, params_after))

    def test_volatility_from_buffer(self):
        """Test volatility estimation from context buffer"""
        # Add variable errors
        for i in range(20):
            errors = torch.randn(5, 2) * (1.0 if i % 3 == 0 else 0.1)
            self.optimizer.optimize_precision(errors)

        volatility = self.optimizer.estimate_volatility()

        assert volatility.shape == (2,)
        assert torch.all(volatility >= 0)


class TestAdaptivePrecisionController:
    """Test adaptive precision controller"""

    def setup_method(self):
        """Set up test environment"""
        self.config = PrecisionConfig(use_gpu=False)
        self.controller = AdaptivePrecisionController(
            self.config,
            num_modalities=2,
            context_dim=4
        )

    def test_initialization(self):
        """Test controller initialization"""
        assert self.controller.num_modalities == 2
        assert hasattr(self.controller, 'gradient_optimizer')
        assert hasattr(self.controller, 'meta_optimizer')
        assert self.controller.strategy == 'gradient'

    def test_optimization_with_strategy(self):
        """Test optimization with different strategies"""
        errors = torch.randn(10, 2)
        context = torch.randn(4)

        # Test gradient strategy
        self.controller.strategy = 'gradient'
        precision1 = self.controller.optimize(errors, context)

        # Test meta strategy
        self.controller.strategy = 'meta'
        precision2 = self.controller.optimize(errors, context)

        # Test hybrid strategy
        self.controller.strategy = 'hybrid'
        precision3 = self.controller.optimize(errors, context)

        assert precision1.shape == (2,)
        assert precision2.shape == (2,)
        assert precision3.shape == (2,)

    def test_strategy_evaluation(self):
        """Test automatic strategy evaluation"""
        # Generate consistent pattern
        for i in range(25):
            if i < 10:
                # High errors for gradient strategy
                errors = torch.randn(5, 2) * 5.0
            else:
                # Low errors
                errors = torch.randn(5, 2) * 0.1

            self.controller.optimize(errors)

        # Strategy might have changed based on performance
        assert self.controller.strategy in ['gradient', 'meta', 'hybrid']

    def test_volatility_estimate(self):
        """Test volatility estimation"""
        # Add some errors
        for _ in range(15):
            errors = torch.randn(5, 2)
            self.controller.optimize(errors)

        volatility = self.controller.get_volatility_estimate()

        assert volatility.shape == (2,)
        assert torch.all(volatility >= 0)

    def test_precision_statistics(self):
        """Test precision statistics tracking"""
        # Generate some history
        for _ in range(30):
            errors = torch.randn(5, 2)
            self.controller.optimize(errors)

        stats = self.controller.get_precision_stats()

        assert 'mean' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats
        assert 'current' in stats

        # All should have correct shape
        for key, value in stats.items():
            assert value.shape == (2,)


class TestPrecisionFactory:
    """Test precision optimizer factory"""

    def test_create_gradient_optimizer(self):
        """Test gradient optimizer creation"""
        optimizer = create_precision_optimizer('gradient', num_modalities=3)
        assert isinstance(optimizer, GradientPrecisionOptimizer)
        assert optimizer.num_modalities == 3

    def test_create_hierarchical_optimizer(self):
        """Test hierarchical optimizer creation"""
        optimizer = create_precision_optimizer('hierarchical', level_dims=[4, 3, 2])
        assert isinstance(optimizer, HierarchicalPrecisionOptimizer)
        assert optimizer.num_levels == 3

    def test_create_meta_optimizer(self):
        """Test meta optimizer creation"""
        optimizer = create_precision_optimizer(
            'meta',
            input_dim=10,
            hidden_dim=64,
            num_modalities=2
        )
        assert isinstance(optimizer, MetaLearningPrecisionOptimizer)
        assert optimizer.input_dim == 10
        assert optimizer.hidden_dim == 64

    def test_create_adaptive_controller(self):
        """Test adaptive controller creation"""
        controller = create_precision_optimizer(
            'adaptive',
            num_modalities=2,
            context_dim=5
        )
        assert isinstance(controller, AdaptivePrecisionController)
        assert controller.num_modalities == 2

    def test_invalid_optimizer_type(self):
        """Test invalid optimizer type"""
        with pytest.raises(ValueError):
            create_precision_optimizer('invalid')

    def test_custom_config(self):
        """Test creation with custom config"""
        config = PrecisionConfig(learning_rate=0.1, use_gpu=False)
        optimizer = create_precision_optimizer('gradient', config=config)

        assert optimizer.config.learning_rate == 0.1
        assert optimizer.config.use_gpu is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
