#!/usr/bin/env python3
"""Script to generate comprehensive development documentation."""

import os

DEVELOPMENT_MD = """# CogniticNet Development Guide

This guide provides comprehensive instructions for setting up and working with the CogniticNet development environment.

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Working with Docker](#working-with-docker)
5. [Database Development](#database-development)
6. [Frontend Development](#frontend-development)
7. [Backend Development](#backend-development)
8. [Testing](#testing)
9. [Code Quality](#code-quality)
10. [Debugging](#debugging)
11. [Performance Profiling](#performance-profiling)
12. [Deployment](#deployment)
13. [Troubleshooting](#troubleshooting)

## Development Environment Setup

### Prerequisites

Before starting development, ensure you have the following installed:

- **Node.js** (v18.0.0 or higher)
- **Python** (v3.9 or higher)
- **Docker** and **Docker Compose** (v20.10 or higher)
- **PostgreSQL** (v13 or higher) - Optional if using Docker
- **Redis** (v6 or higher) - Optional if using Docker
- **Git** (v2.30 or higher)

### Initial Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/cogniticnet.git
   cd cogniticnet
   ```

2. **Set Up Environment Variables**
   ```bash
   # Use the setup script for interactive configuration
   cd environments
   ./setup-env.sh
   
   # Or manually copy and edit
   cp env.development .env.development
   # Edit .env.development with your configuration
   ```

3. **Install Dependencies**
   ```bash
   # Frontend dependencies
   npm install
   
   # Backend dependencies
   pip install -r requirements.txt
   
   # Development dependencies
   pip install -r requirements-dev.txt
   ```

4. **Initialize the Database**
   ```bash
   # Using the setup script
   ./scripts/setup-database.sh
   
   # Or manually
   cd src/database
   python manage.py init
   ```

5. **Verify Installation**
   ```bash
   # Check all services
   npm run check:all
   
   # Run basic tests
   npm test
   pytest tests/unit
   ```

## Project Structure

```
cogniticnet/
├── app/                    # Next.js frontend application
│   ├── (dashboard)/       # Dashboard routes
│   ├── api/              # API routes
│   ├── components/       # React components
│   └── styles/          # CSS/styling files
├── src/                   # Python backend source
│   ├── agents/          # Agent implementations
│   ├── database/        # Database models and migrations
│   ├── knowledge/       # Knowledge graph system
│   ├── simulation/      # Simulation engine
│   └── world/          # World/environment system
├── environments/          # Environment configurations
│   ├── development/     # Docker compose for dev
│   ├── demo/           # Demo environment setup
│   └── *.env files     # Environment templates
├── scripts/              # Utility scripts
├── tests/               # Test suites
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── e2e/           # End-to-end tests
├── doc/                 # Documentation
└── models/              # GNN model definitions
```

## Development Workflow

### Git Workflow

We follow a modified GitFlow workflow:

1. **Main Branches**
   - `main` - Production-ready code
   - `develop` - Integration branch for features
   - `feature/*` - Feature development
   - `hotfix/*` - Emergency fixes
   - `release/*` - Release preparation

2. **Feature Development**
   ```bash
   # Create feature branch
   git checkout -b feature/your-feature-name develop
   
   # Make changes and commit
   git add .
   git commit -m "feat: implement new feature"
   
   # Push to remote
   git push origin feature/your-feature-name
   
   # Create pull request
   ```

3. **Commit Message Convention**
   We use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes
   - `refactor:` - Code refactoring
   - `test:` - Test additions/changes
   - `chore:` - Build process/auxiliary tool changes

### Daily Development Cycle

1. **Start Your Day**
   ```bash
   # Pull latest changes
   git pull origin develop
   
   # Start development environment
   docker-compose up -d
   # Or for local development
   npm run dev
   ```

2. **Check System Status**
   ```bash
   # Verify all services are running
   docker-compose ps
   
   # Check database connection
   cd src/database && python manage.py check
   
   # View logs if needed
   docker-compose logs -f
   ```

3. **Make Changes**
   - Write code following our style guides
   - Add/update tests as needed
   - Update documentation
   - Run linters before committing

4. **Before Committing**
   ```bash
   # Run tests
   npm test
   pytest
   
   # Run linters
   npm run lint
   python -m flake8 src/
   
   # Format code
   npm run format
   python -m black src/
   ```

## Working with Docker

### Docker Compose Commands

```bash
# Start all services
docker-compose -f environments/development/docker-compose.yml up -d

# Stop all services
docker-compose -f environments/development/docker-compose.yml down

# View logs
docker-compose -f environments/development/docker-compose.yml logs -f [service]

# Execute commands in containers
docker-compose -f environments/development/docker-compose.yml exec backend bash
docker-compose -f environments/development/docker-compose.yml exec frontend sh

# Rebuild containers
docker-compose -f environments/development/docker-compose.yml build --no-cache
```

### Docker Development Tips

1. **Volume Management**
   - Code is mounted as volumes for hot reload
   - Database data persists in Docker volumes
   - Use `docker volume ls` to list volumes
   - Use `docker volume prune` to clean unused volumes

2. **Network Debugging**
   ```bash
   # List networks
   docker network ls
   
   # Inspect network
   docker network inspect cogniticnet_default
   ```

3. **Container Resources**
   ```bash
   # Monitor resource usage
   docker stats
   
   # Limit resources in docker-compose.yml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
   ```

## Database Development

### Working with Migrations

1. **Create a New Migration**
   ```bash
   cd src/database
   alembic revision -m "Add new field to agents"
   ```

2. **Auto-generate Migration**
   ```bash
   # After modifying models.py
   alembic revision --autogenerate -m "Auto migration for model changes"
   ```

3. **Apply Migrations**
   ```bash
   # Upgrade to latest
   alembic upgrade head
   
   # Upgrade to specific revision
   alembic upgrade +1
   
   # Downgrade
   alembic downgrade -1
   ```

### Database Operations

```bash
# Access database shell
docker-compose exec postgres psql -U cogniticnet -d cogniticnet_dev

# Backup database
docker-compose exec postgres pg_dump -U cogniticnet cogniticnet_dev > backup.sql

# Restore database
docker-compose exec -T postgres psql -U cogniticnet cogniticnet_dev < backup.sql

# Reset database
cd src/database && python manage.py drop-db && python manage.py init
```

## Frontend Development

### Development Server

```bash
# Start Next.js development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Analyze bundle size
npm run analyze
```

### Component Development

1. **Creating Components**
   ```typescript
   // app/components/MyComponent.tsx
   'use client';
   
   import { useState } from 'react';
   
   interface MyComponentProps {
     title: string;
     onAction?: () => void;
   }
   
   export default function MyComponent({ title, onAction }: MyComponentProps) {
     const [state, setState] = useState(false);
     
     return (
       <div className="component-wrapper">
         <h2>{title}</h2>
         <button onClick={onAction}>Action</button>
       </div>
     );
   }
   ```

2. **Using Shadcn/UI Components**
   ```bash
   # Add a new component
   npx shadcn-ui@latest add button
   npx shadcn-ui@latest add dialog
   ```

## Backend Development

### Running the Backend

```bash
# Start FastAPI development server
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or use the Python script
python src/main.py
```

### API Development

1. **Creating New Endpoints**
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.orm import Session
   from src.database.connection import get_db
   
   router = APIRouter(prefix="/api/v1/agents", tags=["agents"])
   
   @router.get("/")
   async def get_agents(db: Session = Depends(get_db)):
       agents = db.query(Agent).all()
       return {"agents": agents}
   ```

## Testing

### Running Tests

```bash
# Run all tests
npm test && pytest

# Run specific test suites
npm test -- --testPathPattern=components
pytest tests/unit/test_agents.py

# Run with coverage
npm test -- --coverage
pytest --cov=src tests/

# Run in watch mode
npm test -- --watch
pytest-watch
```

## Code Quality

### Linting and Formatting

1. **Python (Black, Flake8, MyPy)**
   ```bash
   # Format code
   black src/ tests/
   
   # Check linting
   flake8 src/ tests/
   
   # Type checking
   mypy src/
   ```

2. **TypeScript/JavaScript (ESLint, Prettier)**
   ```bash
   # Lint code
   npm run lint
   
   # Fix linting issues
   npm run lint:fix
   
   # Format code
   npm run format
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   ```bash
   # Check PostgreSQL is running
   docker-compose ps postgres
   
   # Check connection
   cd src/database && python manage.py check
   
   # Common fixes:
   # - Verify DATABASE_URL in .env
   # - Check PostgreSQL logs: docker-compose logs postgres
   # - Ensure database exists: createdb cogniticnet_dev
   ```

2. **Module Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH="${PYTHONPATH}:${PWD}"
   
   # Or add to .env
   PYTHONPATH=/app
   ```

3. **Docker Issues**
   ```bash
   # Clean rebuild
   docker-compose down -v
   docker-compose build --no-cache
   docker-compose up -d
   
   # Check disk space
   docker system df
   docker system prune -a
   ```

---

Remember to keep this documentation updated as the project evolves!
"""

CONTRIBUTING_MD = """# Contributing to CogniticNet

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
    \"\"\"Calculate the score for an agent based on their actions.
    
    Args:
        agent_id: Unique identifier for the agent
        actions: List of action names performed
        multiplier: Optional score multiplier
        
    Returns:
        The calculated score as a float
    \"\"\"
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
"""

def main():
    """Create development documentation files."""
    # Create DEVELOPMENT.md
    with open('DEVELOPMENT.md', 'w') as f:
        f.write(DEVELOPMENT_MD)
    print("✅ Created DEVELOPMENT.md")
    
    # Create CONTRIBUTING.md
    with open('CONTRIBUTING.md', 'w') as f:
        f.write(CONTRIBUTING_MD)
    print("✅ Created CONTRIBUTING.md")
    
    print("\n📚 Development documentation created successfully!")
    print("   - DEVELOPMENT.md: Comprehensive development guide")
    print("   - CONTRIBUTING.md: Contribution guidelines")

if __name__ == "__main__":
    main() 