# ADR-005: Active Inference Architecture

- **Status**: Accepted
- **Date**: 2025-06-20
- **Deciders**: Expert Committee (Fowler, Beck, Martin, Harris, et al.)
- **Category**: Core Domain Architecture
- **Impact**: High
- **Technical Story**: Task 6: Implement Active Inference Core

## Context and Problem Statement

FreeAgentics requires a cognitive engine that enables agents to make intelligent decisions under uncertainty, update beliefs based on observations, and select actions that minimize prediction error. Traditional rule-based AI systems lack the principled mathematical foundation needed for adaptive, goal-directed behavior in complex, dynamic environments.

The system must support:
- Autonomous agent decision-making based on beliefs and observations
- Real-time belief updating as new information becomes available
- Policy selection that balances exploration and exploitation
- Mathematical rigor in uncertainty quantification
- Scalable performance for thousands of concurrent agents

## Decision Drivers

- **Mathematical Foundation**: Need a principled approach to uncertainty and decision-making
- **Scalability**: Must support 1000+ agents in real-time simulation
- **Adaptability**: Agents must learn and adapt to changing environments
- **Interpretability**: Decision processes must be transparent and debuggable
- **Performance**: Calculations must be fast enough for real-time operation
- **Modularity**: Core cognitive engine must be independent of specific agent types

## Considered Options

### Option 1: Rule-Based Expert Systems
- **Pros**:
  - Simple to implement and understand
  - Deterministic behavior
  - Easy to debug
- **Cons**:
  - No principled handling of uncertainty
  - Brittleness in unexpected situations
  - Exponential rule explosion
  - No learning capability
- **Implementation Effort**: Low

### Option 2: Deep Reinforcement Learning
- **Pros**:
  - Proven success in complex domains
  - Can learn from experience
  - Handles high-dimensional state spaces
- **Cons**:
  - Black box decision making
  - Requires massive training data
  - Unstable training process
  - No built-in uncertainty quantification
- **Implementation Effort**: High

### Option 3: Active Inference Framework
- **Pros**:
  - Principled mathematical foundation
  - Built-in uncertainty quantification
  - Unified framework for perception and action
  - Biologically plausible
  - Interpretable decision processes
  - Scales well with vectorized operations
- **Cons**:
  - Complex mathematical concepts
  - Requires specialized knowledge
  - Computational overhead for belief updates
- **Implementation Effort**: Medium

### Option 4: Hybrid Symbolic-Neural Approach
- **Pros**:
  - Combines symbolic reasoning with neural adaptation
  - More interpretable than pure neural methods
- **Cons**:
  - Complex integration between subsystems
  - No unified mathematical framework
  - Difficult to balance symbolic and neural components
- **Implementation Effort**: High

## Decision Outcome

**Chosen option**: "Active Inference Framework" because it provides the most principled mathematical foundation for autonomous agent cognition while maintaining interpretability and scalability.

### Implementation Strategy

1. **Core Mathematical Components**:
   - BeliefState: Probabilistic representation of agent knowledge
   - FreeEnergyCalculator: Policy evaluation using variational free energy
   - BeliefUpdater: Bayesian belief updates from observations
   - PolicySelector: Action selection minimizing expected free energy

2. **Mathematical Foundation**:
   ```
   Free Energy: F = -log P(o|s) + KL[Q(s)||P(s)]
   Where:
   - P(o|s): Likelihood of observations given states
   - Q(s): Approximate posterior beliefs
   - P(s): Prior beliefs
   - KL: Kullback-Leibler divergence
   ```

3. **Performance Optimizations**:
   - Vectorized operations with NumPy
   - JIT compilation with Numba for hot paths
   - Caching for repeated calculations
   - Batch processing for multiple agents

4. **Architecture Integration**:
   - Core inference engine in `inference/` directory
   - Agent-specific behaviors in `agents/` directory
   - Interface adapters for external integrations
   - Strict dependency inversion (core doesn't depend on interfaces)

### Validation Criteria

- Mathematical accuracy verified against published Active Inference literature
- Performance benchmarks: 1000+ agents with <10ms per decision cycle
- Memory efficiency: <2KB per agent belief state
- Property-based tests verify mathematical invariants
- Integration tests validate agent behavior emergence

### Positive Consequences

- **Principled Decision Making**: All agent decisions have mathematical justification
- **Uncertainty Handling**: Built-in quantification and propagation of uncertainty
- **Adaptability**: Agents naturally adapt to new environments through belief updates
- **Interpretability**: Decision processes are transparent and debuggable
- **Scalability**: Vectorized operations enable thousands of concurrent agents
- **Extensibility**: Framework supports different agent types and behaviors

### Negative Consequences

- **Complexity**: Requires understanding of variational inference and information theory
- **Computational Overhead**: Belief updates require matrix operations
- **Learning Curve**: Developers need training in Active Inference concepts
- **Mathematical Dependencies**: Relies on advanced mathematical libraries

## Compliance and Enforcement

- **Validation**: Mathematical unit tests verify invariants (beliefs sum to 1, free energy minimization)
- **Monitoring**: Performance profiling tracks computation time and memory usage
- **Violations**: Any deviation from mathematical principles must be justified and documented

## Implementation Details

### Core Components Structure
```
inference/
├── active_inference_engine.py     # Main engine orchestrating components
├── belief_state.py               # Probabilistic belief representation
├── free_energy_calculator.py     # Policy evaluation mathematics
├── belief_updater.py            # Bayesian update implementation
├── policy_selector.py           # Action selection algorithms
├── interfaces/                  # Abstract interfaces for integrations
│   ├── observation_provider.py  # Interface for perception systems
│   ├── action_executor.py       # Interface for action systems
│   └── world_model.py           # Interface for environment models
└── optimizations/               # Performance-critical implementations
    ├── vectorized_operations.py # NumPy-based batch processing
    └── jit_functions.py         # Numba-compiled hot paths
```

### Integration with Agent System
- Agents compose with ActiveInferenceEngine for cognitive processing
- Belief states represent agent knowledge about world and goals
- Policy selection drives agent actions in each simulation step
- External world interactions flow through dependency-inverted interfaces

## Links and References

- [Friston, K. (2019). Active Inference: A Process Theory](https://www.frontiersin.org/articles/10.3389/fncom.2016.00089/full)
- [Parr, T. & Friston, K. (2019). Generalised free energy and active inference](https://www.sciencedirect.com/science/article/pii/S0022249617303170)
- [PyMDP: Python library for Active Inference](https://github.com/infer-actively/pymdp)
- [Task 6: Implement Active Inference Core](../../../.taskmaster/tasks/task_006.txt)
- [ADR-002: Canonical Directory Structure](002-canonical-directory-structure.md)
- [ADR-003: Dependency Rules](003-dependency-rules.md)

---

**Mathematical Note**: The Active Inference framework is grounded in the free energy principle, which states that all adaptive systems minimize their variational free energy. This provides a unified account of perception, action, and learning that is both mathematically rigorous and biologically plausible.
