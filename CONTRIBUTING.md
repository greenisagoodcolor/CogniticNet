# Contributing to CogniticNet

Thank you for your interest in contributing to CogniticNet! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Process](#development-process)
4. [Coding Standards](#coding-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Documentation](#documentation)
7. [Pull Request Process](#pull-request-process)
8. [Issue Guidelines](#issue-guidelines)

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please read and follow our Code of Conduct:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive criticism
- Accept feedback gracefully
- Prioritize the project's best interests

## Getting Started

1. **Fork the Repository**
   - Navigate to the [CogniticNet repository](https://github.com/yourusername/cogniticnet)
   - Click the "Fork" button in the upper right corner
   - Clone your fork locally

2. **Set Up Development Environment**
   - Follow the instructions in [DEVELOPMENT.md](DEVELOPMENT.md)
   - Ensure all tests pass before making changes

3. **Find an Issue to Work On**
   - Check the [Issues](https://github.com/yourusername/cogniticnet/issues) page
   - Look for issues labeled `good first issue` or `help wanted`
   - Comment on the issue to let others know you're working on it

## Development Process

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Write clean, well-documented code
- Follow the coding standards
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Run all tests
npm test
pytest

# Run linters
npm run lint
python -m flake8 src/
```

### 4. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/) for our commit messages:

```bash
git commit -m "feat: add new agent behavior"
git commit -m "fix: resolve database connection issue"
git commit -m "docs: update API documentation"
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

## Coding Standards

### Python

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints for all functions
- Maximum line length: 88 characters (Black default)
- Use meaningful variable and function names

Example:
```python
from typing import List, Optional

def calculate_agent_score(
    agent_id: str,
    actions: List[str],
    multiplier: Optional[float] = 1.0
) -> float:
    """Calculate the score for an agent based on their actions.
    
    Args:
        agent_id: Unique identifier for the agent
        actions: List of action names performed
        multiplier: Optional score multiplier
        
    Returns:
        The calculated score as a float
    """
    base_score = len(actions) * 10
    return base_score * multiplier
```

### TypeScript/JavaScript

- Use TypeScript for all new code
- Follow the [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- Use functional components with hooks for React
- Prefer const over let, avoid var

Example:
```typescript
interface AgentProps {
  id: string;
  name: string;
  onUpdate?: (id: string) => void;
}

export const AgentCard: React.FC<AgentProps> = ({ id, name, onUpdate }) => {
  const handleClick = () => {
    onUpdate?.(id);
  };

  return (
    <div className="agent-card" onClick={handleClick}>
      <h3>{name}</h3>
      <p>ID: {id}</p>
    </div>
  );
};
```

## Testing Guidelines

### Unit Tests

- Write tests for all new functions and components
- Aim for at least 80% code coverage
- Use descriptive test names

### Integration Tests

- Test interactions between components
- Verify API endpoints work correctly
- Test database operations

### End-to-End Tests

- Test critical user workflows
- Ensure the application works as expected from a user's perspective

## Documentation

### Code Documentation

- Add docstrings to all Python functions and classes
- Use JSDoc comments for TypeScript/JavaScript
- Include examples in complex functions

### README Updates

- Update README.md if you add new features
- Keep installation instructions current
- Add new dependencies to requirements

### API Documentation

- Document all new API endpoints
- Include request/response examples
- Note any breaking changes

## Pull Request Process

### Before Submitting

1. **Ensure all tests pass**
2. **Run linters and fix any issues**
3. **Update documentation**
4. **Add entries to CHANGELOG.md**
5. **Rebase on latest main branch**

### Pull Request Template

When creating a pull request, include:

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process

1. At least one maintainer must review the PR
2. All CI checks must pass
3. Address all review comments
4. Maintainer will merge when ready

## Issue Guidelines

### Bug Reports

Include:
- Clear description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, versions)
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and benefits
- Possible implementation approach
- Any mockups or examples

### Questions

- Check documentation first
- Search existing issues
- Provide context and details

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation

Thank you for contributing to CogniticNet! 