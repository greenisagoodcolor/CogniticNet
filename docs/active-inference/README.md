# Active Inference Framework for FreeAgentics

## Overview

The Active Inference framework in FreeAgentics provides a comprehensive implementation of the Free Energy Principle and Active Inference for creating adaptive, intelligent agents. This framework enables agents to:

- **Perceive** their environment through probabilistic inference
- **Learn** from experience by updating their generative models
- **Act** to minimize expected free energy and achieve their goals
- **Adapt** to changing environments through precision control and model updates

## Key Components

### 1. Generative Models

- **Discrete Models**: For categorical state spaces
- **Continuous Models**: For continuous state representations
- **Hybrid Models**: Combining discrete and continuous aspects

### 2. Inference Algorithms

- **Variational Inference**: Efficient approximate inference
- **Particle Filters**: For non-linear continuous models
- **Message Passing**: For hierarchical models

### 3. Policy Selection

- **Expected Free Energy**: Balancing exploration and exploitation
- **Sophisticated Inference**: Multi-step planning
- **Habit Learning**: Efficient cached policies

### 4. Learning Mechanisms

- **Parameter Learning**: Online Bayesian learning of model parameters
- **Structure Learning**: Discovering model structure from data
- **Active Learning**: Directed exploration for model improvement

### 5. Advanced Features

- **Hierarchical Inference**: Multi-level temporal abstractions
- **Precision Control**: Adaptive uncertainty weighting
- **Computational Optimization**: GPU acceleration and sparse operations

## Quick Start

### Installation

```bash
# Install required dependencies
pip install torch numpy scipy matplotlib networkx

# Install FreeAgentics (if not already installed)
pip install -e .
```

### Basic Usage

```python
import torch
from src.agents.active_inference.generative_model import (
    DiscreteGenerativeModel, ModelDimensions, ModelParameters
)
from src.agents.active_inference.inference import VariationalInference
from src.agents.active_inference.policy_selection import PolicySelector, PolicyConfig

# Define model dimensions
dims = ModelDimensions(
    num_states=4,
    num_observations=3,
    num_actions=2
)

# Create generative model
params = ModelParameters(use_gpu=torch.cuda.is_available())
gen_model = DiscreteGenerativeModel(dims, params)

# Create inference engine
inference = VariationalInference(dims, params)

# Create policy selector
policy_config = PolicyConfig(precision=1.0, planning_horizon=3)
policy_selector = PolicySelector(policy_config)

# Initialize belief state
belief = torch.ones(4) / 4  # Uniform prior

# Perception: Update belief given observation
observation = 1  # Observed state 1
belief = inference.update_beliefs(belief, observation, gen_model.A)

# Action: Select action based on expected free energy
G_values = policy_selector.compute_expected_free_energy(
    belief, gen_model.A, gen_model.B, gen_model.C,
    num_actions=2, horizon=3
)
action_probs = policy_selector.select_action(G_values)
action = torch.multinomial(action_probs, 1).item()

print(f"Updated belief: {belief}")
print(f"Selected action: {action} with probability {action_probs[action]:.3f}")
```

## Documentation

- [Mathematical Framework](mathematical-framework.md) - Detailed mathematical foundations
- [Implementation Guide](implementation-guide.md) - Step-by-step implementation details
- [API Reference](api-reference.md) - Complete API documentation

## License

This module is part of FreeAgentics and is released under the same license.
