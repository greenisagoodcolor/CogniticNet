# Naming Convention Workflow Guide

This guide provides detailed instructions for working with the automated naming convention system in FreeAgentics.

## Quick Start

1. **Install pre-commit hooks** (one-time setup):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Check current violations**:
   ```bash
   python3 scripts/audit-naming.py
   ```

3. **Fix violations automatically**:
   ```bash
   python3 scripts/fix-naming.py --apply --priority
   ```

## Understanding the Naming System

### Architecture Overview

The naming convention system consists of several integrated components:

```
┌─────────────────────────────────────────────────────────────┐
│                 Naming Convention System                    │
├─────────────────┬───────────────────┬──────────────────────┤
│   Detection     │   Automation      │   Integration        │
├─────────────────┼───────────────────┼──────────────────────┤
│ • audit-naming  │ • fix-naming      │ • pre-commit hooks   │
│ • check-naming  │ • batch-rename    │ • linter configs     │
│ • prohibited    │ • ast-refactor    │ • CI/CD pipeline     │
│   terms         │ • pipeline        │ • IDE integration    │
└─────────────────┴───────────────────┴──────────────────────┘
```

### Core Scripts

#### 1. **Detection Scripts**
- `scripts/audit-naming.py` - Comprehensive analysis of all violations
- `scripts/enhanced-check-naming.py` - Pre-commit hook for real-time checking
- `scripts/enhanced-prohibited-terms.py` - Gaming terminology detection
- `scripts/check-file-naming.py` - File name validation

#### 2. **Automation Scripts**
- `scripts/fix-naming.py` - Automated violation fixing with priority handling
- `scripts/batch-rename.py` - Large-scale file renaming operations
- `scripts/ast-refactor-enhanced.py` - AST-based reference updates
- `scripts/integrated-refactor-pipeline.py` - Complete workflow automation

#### 3. **Configuration Files**
- `.pre-commit-config.yaml` - Pre-commit hook configuration
- `config/.flake8` - Python linting rules with naming enforcement
- `config/.eslintrc-enhanced.js` - TypeScript/JavaScript naming rules
- `docs/standards/naming-conventions.json` - Machine-readable conventions

## Common Workflows

### Workflow 1: Daily Development

```bash
# 1. Start development (hooks are automatic)
git add .
git commit -m "feat: implement new feature"

# 2. If hooks fail, review violations
python3 scripts/enhanced-check-naming.py --verbose path/to/file

# 3. Fix automatically where possible
python3 scripts/fix-naming.py --apply

# 4. Commit fixes
git add .
git commit -m "fix: resolve naming convention violations"
```

### Workflow 2: Large Refactoring

```bash
# 1. Analyze current state
python3 scripts/audit-naming.py > violations-before.json

# 2. Plan changes (dry run)
python3 scripts/integrated-refactor-pipeline.py --language python

# 3. Execute refactoring
python3 scripts/integrated-refactor-pipeline.py --apply --language python

# 4. Verify results
python3 scripts/audit-naming.py > violations-after.json
```

### Workflow 3: New File Creation

```bash
# 1. Create file with proper naming
touch agents/core/my-new-module.py  # Python: kebab-case
touch web/components/MyComponent.tsx  # React: PascalCase

# 2. Validate naming before coding
python3 scripts/check-file-naming.py agents/core/my-new-module.py

# 3. Code with proper conventions
# (hooks will validate on commit)
```

## Violation Categories & Solutions

### High Priority Violations

#### Prohibited Terms
**Problem**: Using gaming terminology or old project names
```
❌ PlayerAgent, NPCAgent, spawn, CogniticNet
```

**Solution**: Use professional alternatives
```
✅ ExplorerAgent, AutonomousAgent, initialize, FreeAgentics
```

**Fix Command**:
```bash
python3 scripts/enhanced-prohibited-terms.py path/to/file
python3 scripts/fix-naming.py --apply
```

#### Syntax Errors
**Problem**: Files with Python syntax errors can't be parsed
```
❌ SyntaxError: invalid syntax (<file>, line 15)
```

**Solution**: Fix syntax manually or use IDE tools
```bash
# Use Python linter to identify issues
python3 -m py_compile path/to/file.py
flake8 --config=config/.flake8 path/to/file.py
```

### Medium Priority Violations

#### File Naming
**Problem**: Incorrect file name conventions
```
❌ movement_perception.py (snake_case)
❌ agentList.tsx (camelCase component)
```

**Solution**: Rename files with proper conventions
```
✅ movement-perception.py (kebab-case)
✅ AgentList.tsx (PascalCase component)
```

**Fix Command**:
```bash
python3 scripts/batch-rename.py --python-only  # For Python files
python3 scripts/batch-rename.py --typescript-only  # For TS files
```

#### Code Naming
**Problem**: Incorrect variable, class, or function names
```python
❌ class agentManager:  # Should be PascalCase
❌ def CreateAgent():   # Should be snake_case
```

**Solution**: Follow language conventions
```python
✅ class AgentManager:
✅ def create_agent():
```

### Low Priority Violations

#### Config Files
**Problem**: Configuration files using snake_case
```
❌ test_config.json
```

**Solution**: Use kebab-case for config files
```
✅ test-config.json
```

## Troubleshooting

### Common Issues

#### 1. **Pre-commit Hook Failures**

**Error**: `Executable 'python' not found`
```bash
# Solution: Ensure python3 is available
which python3
# Update hook configuration if needed
```

**Error**: `Permission denied`
```bash
# Solution: Make scripts executable
chmod +x scripts/*.py
```

#### 2. **AST Parsing Failures**

**Error**: `SyntaxError: invalid syntax`
```bash
# Solution: Fix syntax errors manually
python3 -c "import ast; ast.parse(open('file.py').read())"
```

**Error**: `TypeError: expected str, bytes or os.PathLike object`
```bash
# Solution: Check file encoding
file -bi path/to/file.py
```

#### 3. **Import Update Failures**

**Error**: AST refactor doesn't update imports
```bash
# Solution: Use manual mapping
python3 scripts/ast-refactor-enhanced.py \
  --add-mapping old/path.py new/path.py \
  --apply
```

#### 4. **Batch Rename Issues**

**Error**: `git mv` fails during batch rename
```bash
# Solution: Ensure clean git state
git status
git add .  # Stage any unstaged files first
```

### Emergency Procedures

#### Skip Pre-commit Hooks (Use Sparingly)
```bash
# Skip all hooks
git commit --no-verify -m "Emergency commit"

# Skip specific hook
SKIP=enhanced-naming-check git commit -m "Skip naming check only"
```

#### Rollback Renaming Changes
```bash
# If batch rename goes wrong
git checkout HEAD -- .  # Reset all changes
# OR
git reset --hard HEAD~1  # Reset to previous commit
```

#### Disable Hooks Temporarily
```bash
# Uninstall hooks
pre-commit uninstall

# Reinstall when ready
pre-commit install
```

## Advanced Usage

### Custom Naming Rules

To add custom naming rules, modify:
1. `docs/standards/naming-conventions.json` - Add new patterns
2. `scripts/enhanced-check-naming.py` - Add validation logic
3. `scripts/fix-naming.py` - Add fix logic

### Integration with CI/CD

```yaml
# .github/workflows/naming-check.yml
name: Naming Convention Check
on: [push, pull_request]
jobs:
  naming:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install pre-commit
      - run: pre-commit run --all-files
```

### IDE Integration

#### VS Code Settings
```json
{
  "python.linting.flake8Enabled": true,
  "python.linting.flake8Args": ["--config=config/.flake8"],
  "eslint.options": {
    "configFile": "config/.eslintrc-enhanced.js"
  }
}
```

#### PyCharm Configuration
1. File → Settings → Tools → External Tools
2. Add tool: `scripts/check-file-naming.py`
3. Configure keyboard shortcut for quick validation

## Performance Tips

### Large Codebases

For projects with 1000+ files:
```bash
# Use parallel processing
python3 scripts/audit-naming.py --parallel

# Process by directory
python3 scripts/fix-naming.py --root=agents/ --apply
python3 scripts/fix-naming.py --root=web/ --apply
```

### Incremental Updates

For gradual adoption:
```bash
# Fix only new/modified files
git diff --name-only | xargs python3 scripts/enhanced-check-naming.py

# Priority-based fixing
python3 scripts/fix-naming.py --priority --dry-run  # Review first
python3 scripts/fix-naming.py --priority --apply    # Apply high priority only
```

## Contributing to the Naming System

### Adding New Patterns

1. **Update Convention Rules**:
   - Modify `docs/standards/naming-conventions.json`
   - Add test cases in violation detection

2. **Enhance Detection**:
   - Update `scripts/enhanced-check-naming.py`
   - Add new violation categories

3. **Implement Fixes**:
   - Update `scripts/fix-naming.py`
   - Add automated fix logic

4. **Test Changes**:
   ```bash
   python3 scripts/audit-naming.py  # Test detection
   python3 scripts/fix-naming.py --dry-run  # Test fixes
   ```

### Reporting Issues

When reporting naming system issues, include:
1. Full error message
2. File causing the issue
3. Expected vs. actual behavior
4. Environment details (Python version, OS)

For more help, see:
- [ADR-004: Naming Conventions](docs/architecture/decisions/ADR-004-naming-conventions.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- Project Issues on GitHub
