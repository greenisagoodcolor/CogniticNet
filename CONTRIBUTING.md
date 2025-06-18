# Contributing to FreeAgentics

Welcome to FreeAgentics! This document outlines our coding standards, naming conventions, and contribution guidelines. Following these standards ensures consistency and maintainability across our codebase.

## Table of Contents
- [Naming Conventions](#naming-conventions)
- [Code Style](#code-style)
- [Git Workflow](#git-workflow)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)

## Naming Conventions

### Overview
FreeAgentics uses consistent naming conventions across all languages and file types. These conventions are enforced through automated linting and CI/CD checks.

### File Naming

#### Python Files
- Use **kebab-case** for all Python files: `agent-manager.py`, `belief-update.py`
- Test files: `test-{module-name}.py` (e.g., `test-belief-update.py`)
- Private modules: prefix with underscore `_internal-utils.py`

#### TypeScript/JavaScript Files
- Components: **PascalCase** for React components: `AgentDashboard.tsx`
- Utilities: **camelCase** for utility files: `apiClient.ts`
- Hooks: **camelCase** with 'use' prefix: `useAgentState.ts`
- Tests: `{filename}.test.{ext}` (e.g., `AgentDashboard.test.tsx`)

#### Configuration Files
- Use **kebab-case**: `docker-compose.yml`, `jest-config.js`
- Environment specific: `{env}.yml` (e.g., `production.yml`)

### Code Naming Standards

#### Python
```python
# Classes: PascalCase
class ExplorerAgent(BaseAgent):
    """Professional multi-agent system component."""

    # Instance variables: snake_case with underscore for private
    def __init__(self):
        self.belief_state = {}
        self._internal_cache = {}

    # Methods: snake_case, verb phrases
    def update_beliefs(self, observation: Dict[str, Any]) -> BeliefState:
        """Update agent's belief state based on observation."""
        pass

    # Constants: UPPER_SNAKE_CASE
    MAX_BELIEF_PRECISION = 0.99
    DEFAULT_LEARNING_RATE = 0.01

    # Private methods: prefix with underscore
    def _calculate_free_energy(self) -> float:
        """Internal calculation method."""
        pass
```

#### TypeScript/React
```typescript
// Interfaces: PascalCase with 'I' prefix for domain interfaces
interface IAgent {
  id: string;
  beliefState: BeliefState;
}

// Types: PascalCase
type AgentConfig = {
  learningRate: number;
  maxIterations: number;
};

// Components: PascalCase
export const AgentCreator: React.FC<AgentCreatorProps> = ({ onAgentCreate }) => {
  // Hooks: camelCase with 'use' prefix
  const [isCreating, setIsCreating] = useState(false);
  const { agents, createAgent } = useAgentStore();

  // Event handlers: camelCase with 'handle' prefix
  const handleCreateAgent = async (config: AgentConfig) => {
    // Implementation
  };

  // Constants: UPPER_SNAKE_CASE
  const MAX_AGENTS = 1000;
  const DEFAULT_TIMEOUT = 5000;
};

// Utility functions: camelCase, verb phrases
export const calculateBeliefEntropy = (beliefs: BeliefState): number => {
  // Implementation
};

// Enums: PascalCase with PascalCase values
enum AgentStatus {
  Active = 'ACTIVE',
  Learning = 'LEARNING',
  Idle = 'IDLE'
}
```

### Database Naming
- Tables: **snake_case** plural: `agents`, `belief_states`
- Columns: **snake_case**: `agent_id`, `created_at`
- Indexes: `idx_{table}_{columns}`: `idx_agents_status_created_at`
- Foreign keys: `fk_{table}_{referenced_table}`: `fk_beliefs_agents`

### API Endpoints
```
GET    /api/v1/agents              # List resources (plural)
POST   /api/v1/agents              # Create resource
GET    /api/v1/agents/:id          # Get specific resource
PUT    /api/v1/agents/:id          # Update resource
DELETE /api/v1/agents/:id          # Delete resource
POST   /api/v1/agents/:id/beliefs  # Nested resource action
```

### Prohibited Terms
Never use gaming terminology. Use professional multi-agent system terms:
- ❌ PlayerAgent → ✅ ExplorerAgent
- ❌ NPCAgent → ✅ AutonomousAgent
- ❌ EnemyAgent → ✅ CompetitiveAgent
- ❌ GameWorld → ✅ Environment
- ❌ spawn() → ✅ initialize()
- ❌ respawn() → ✅ reset()

## Code Style

### Python
- Follow [PEP 8](https://pep8.org/) with 100-character line limit
- Use type hints for all function signatures
- Docstrings for all public classes and methods
- Run `black` formatter and `ruff` linter

### TypeScript
- Follow [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use strict TypeScript configuration
- Prefer functional components and hooks in React
- Run `prettier` formatter and `eslint` linter

### General Principles
1. **Explicit over implicit**: Clear naming over brevity
2. **Consistency**: Same patterns throughout codebase
3. **Domain language**: Use Active Inference and multi-agent terminology
4. **No magic numbers**: Always use named constants
5. **Early returns**: Reduce nesting with guard clauses

## Git Workflow

### Branch Naming
- Feature: `feature/description-in-kebab-case`
- Bugfix: `fix/description-in-kebab-case`
- Refactor: `refactor/description-in-kebab-case`
- Docs: `docs/description-in-kebab-case`

### Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat(agents): add belief update mechanism
fix(inference): correct free energy calculation
docs(api): update agent endpoint documentation
refactor(coalitions): improve formation algorithm
test(beliefs): add edge case coverage
```

### Pull Request Process
1. Create branch from `main`
2. Make changes following conventions
3. Add tests for new functionality
4. Update documentation
5. Run linters and tests locally
6. Create PR with descriptive title
7. Address review feedback

## Testing Requirements

### Coverage Requirements
- Minimum 80% coverage for new code
- Critical paths require 90%+ coverage
- All public APIs must have tests

### Test Structure
```python
# Python example
def test_agent_belief_update_increases_precision():
    """Test that belief updates increase precision over time."""
    # Arrange
    agent = ExplorerAgent()
    initial_precision = agent.precision

    # Act
    agent.update_beliefs(observation)

    # Assert
    assert agent.precision > initial_precision
```

### Test Naming
- Descriptive test names explaining the scenario
- Format: `test_{unit}_{scenario}_{expected_outcome}`
- Example: `test_belief_update_with_noisy_observation_maintains_stability`

## Documentation Standards

### Code Documentation
- All public APIs must have docstrings/JSDoc
- Include parameters, return types, and examples
- Document exceptions and edge cases

### Architecture Decisions
- Use ADR format in `docs/architecture/decisions/`
- Number sequentially: `001-structure.md`, `002-inference.md`
- Include context, decision, and consequences

### README Files
- Each major module has its own README
- Include purpose, usage examples, and API reference
- Keep synchronized with code changes

## Pre-commit Hooks

Install pre-commit hooks:
```bash
pip install pre-commit
pre-commit install
```

Hooks will run:
- Code formatters (black, prettier)
- Linters (ruff, eslint)
- Type checkers (mypy, tsc)
- Naming convention validators

## Questions?

For questions about these conventions:
1. Check existing code for examples
2. Ask in development discussions
3. Propose changes via PR to this document

Remember: Consistency is key. When in doubt, follow existing patterns in the codebase.

---
*Last updated: 2025-06-18*
*Version: 1.0*
