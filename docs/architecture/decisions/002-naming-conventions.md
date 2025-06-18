# ADR-002: Naming Conventions and Code Standards

## Status
Accepted and Implemented

## Context
Following the successful migration from CogniticNet to FreeAgentics (ADR-001), the codebase exhibited significant naming inconsistencies that hindered readability, maintainability, and professional presentation. The expert committee identified this as a critical Day 2 priority for the 10-day transformation sprint.

### Issues Identified
1. **Inconsistent File Naming**: Mix of camelCase, snake_case, and kebab-case
2. **Gaming Terminology**: PlayerAgent, NPCAgent, spawn() - unprofessional for enterprise software
3. **TypeScript Conventions**: Components using kebab-case instead of PascalCase
4. **Missing Standards**: No interface prefixing, inconsistent method naming
5. **Legacy References**: Remaining "CogniticNet" references throughout codebase

## Decision
Implement comprehensive naming conventions across all languages and establish automated enforcement through tooling.

### Naming Standards Adopted

#### File Naming
- **Python**: kebab-case for all files (`belief-update.py`)
- **TypeScript Components**: PascalCase (`AgentDashboard.tsx`)
- **TypeScript Utilities**: camelCase (`apiClient.ts`)
- **TypeScript Hooks**: camelCase with 'use' prefix (`useAgentState.ts`)
- **Configuration**: kebab-case (`docker-compose.yml`)

#### Code Conventions

**Python**:
```python
class ExplorerAgent(BaseAgent):  # PascalCase classes
    def update_beliefs(self):     # snake_case methods
        MAX_ITERATIONS = 100      # UPPER_SNAKE_CASE constants
```

**TypeScript**:
```typescript
interface IAgent {                // 'I' prefix for domain interfaces
    beliefState: BeliefState;     // camelCase properties
}

const AgentCreator: React.FC = () => {  // PascalCase components
    const handleSubmit = () => {};      // 'handle' prefix for events
    const MAX_AGENTS = 1000;            // UPPER_SNAKE_CASE constants
}
```

#### Prohibited Terms
All gaming terminology replaced with professional multi-agent system terms:
- PlayerAgent → ExplorerAgent
- NPCAgent → AutonomousAgent
- spawn() → initialize()
- GameWorld → Environment

## Implementation

### Phase 1: Documentation (Completed)
- Created comprehensive CONTRIBUTING.md with human-readable standards
- Created machine-readable naming-conventions.json for tooling
- Established clear examples and anti-patterns

### Phase 2: Audit (Completed)
- Developed audit-naming.py script
- Scanned 523 files, found 301 violations
- Categorized by severity and type
- Generated detailed reports

### Phase 3: Automated Fixes (Completed)
- Developed fix-naming.py script
- Fixed 36 high-priority violations:
  - 5 prohibited term replacements
  - 6 Python file renames
  - 10 TypeScript component renames
  - 5 configuration file renames
  - 10 code convention fixes
- Used git mv to preserve history
- Updated all import references

### Phase 4: Documentation Updates (Current)
- Updated all documentation to reflect new conventions
- Created this ADR for permanent record
- Updated README and setup guides

## Consequences

### Positive
1. **Professional Appearance**: No gaming terminology, enterprise-ready naming
2. **Consistency**: Single standard across all languages
3. **Tooling Support**: Machine-readable format enables automation
4. **Developer Experience**: Clear patterns reduce cognitive load
5. **Investment Ready**: Shows attention to code quality

### Negative
1. **Learning Curve**: Developers must adapt to new conventions
2. **Ongoing Maintenance**: Need to monitor and fix violations
3. **Import Updates**: File renames require import updates

### Mitigations
- Comprehensive documentation in CONTRIBUTING.md
- Automated tooling for detection and fixes
- Pre-commit hooks (to be implemented)
- Regular audits in CI/CD pipeline

## Metrics

### Before
- 301 naming violations
- 6 prohibited gaming terms
- 111 incorrectly named Python files
- 71 incorrectly named TypeScript components

### After Phase 3
- 265 violations remaining (mostly lower priority)
- 0 prohibited gaming terms
- Consistent file naming in critical paths
- Professional terminology throughout

## Next Steps
1. Implement pre-commit hooks (Subtask 2.5)
2. Add CI/CD enforcement (Subtask 2.5)
3. Fix remaining lower-priority violations
4. Regular audits to prevent regression

## References
- [CONTRIBUTING.md](/CONTRIBUTING.md) - Human-readable conventions
- [naming-conventions.json](/docs/standards/naming-conventions.json) - Machine-readable rules
- [audit-naming.py](/scripts/audit-naming.py) - Audit tool
- [fix-naming.py](/scripts/fix-naming.py) - Automated fixes

---
*Decision made by: Robert Martin (Clean Code Lead)*
*Date: 2025-06-18*
*Version: 1.0*
