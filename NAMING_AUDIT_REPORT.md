# FreeAgentics Naming Convention Audit Report

**Date**: 2025-06-18
**Auditor**: Robert Martin (Clean Code Lead)

## Summary

- Total files scanned: 748
- Total violations found: 428
- Violation categories: 9

## Violations by Category

### Prohibited Terms
**Count**: 14

- `./docs/examples/agent-creation-examples.py`: Found prohibited term 'CogniticNet' (2 occurrences)
- `./scripts/check-prohibited-terms.py`: Found prohibited term 'PlayerAgent' (1 occurrences)
- `./scripts/check-prohibited-terms.py`: Found prohibited term 'NPCAgent' (1 occurrences)
- `./scripts/check-prohibited-terms.py`: Found prohibited term 'EnemyAgent' (1 occurrences)
- `./scripts/check-prohibited-terms.py`: Found prohibited term 'GameWorld' (1 occurrences)
- ... and 9 more

### Syntax Errors
**Count**: 59

- `./tests/test-gnn-structure.py`: Python syntax error - cannot parse
- `./tests/unit/test-batch-processor.py`: Python syntax error - cannot parse
- `./tests/unit/test-model-mapper.py`: Python syntax error - cannot parse
- `./tests/unit/test-decision-making.py`: Python syntax error - cannot parse
- `./tests/unit/test-perception.py`: Python syntax error - cannot parse
- ... and 54 more

### Typescript Components
**Count**: 71

- `./web/components/gridworld.tsx`: Component 'gridworld.tsx' doesn't match PascalCase pattern
- `./web/components/memoryviewer.tsx`: Component 'memoryviewer.tsx' doesn't match PascalCase pattern
- `./web/components/navbar.tsx`: Component 'navbar.tsx' doesn't match PascalCase pattern
- `./web/components/agentcard.tsx`: Component 'agentcard.tsx' doesn't match PascalCase pattern
- `./web/components/agent-list.tsx`: Component 'agent-list.tsx' doesn't match PascalCase pattern
- ... and 66 more

### Python Files
**Count**: 53

- `./tests/test_readiness_evaluator.py`: File 'test_readiness_evaluator.py' doesn't match kebab-case pattern: ^[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$
- `./world/--init--.py`: File '--init--.py' doesn't match kebab-case pattern: ^[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$
- `./world/spatial/--init--.py`: File '--init--.py' doesn't match kebab-case pattern: ^[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$
- `./agents/core/movement_perception.py`: File 'movement_perception.py' doesn't match kebab-case pattern: ^[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$
- `./agents/core/active_inference.py`: File 'active_inference.py' doesn't match kebab-case pattern: ^[a-z][a-z0-9]*(-[a-z0-9]+)*\.py$
- ... and 48 more

### Python Methods
**Count**: 4

- `./inference/engine/generative_model.py`: Function '_initialize_A' doesn't match snake_case pattern
- `./inference/engine/generative_model.py`: Function '_initialize_B' doesn't match snake_case pattern
- `./inference/engine/generative_model.py`: Function '_initialize_C' doesn't match snake_case pattern
- `./inference/engine/generative_model.py`: Function '_initialize_D' doesn't match snake_case pattern

### Config Files
**Count**: 149

- `./.repository_analysis/complete_inventory.json`: Config file 'complete_inventory.json' doesn't match kebab-case pattern
- `./.repository_analysis/inventory_summary.json`: Config file 'inventory_summary.json' doesn't match kebab-case pattern
- `./.test_reports/baseline_report_20250620_103624.json`: Config file 'baseline_report_20250620_103624.json' doesn't match kebab-case pattern
- `./tests/jest.setup.js`: Config file 'jest.setup.js' doesn't match kebab-case pattern
- `./tests/jest.config.js`: Config file 'jest.config.js' doesn't match kebab-case pattern
- ... and 144 more

### Typescript Hooks
**Count**: 4

- `./web/components/ui/use-toast.ts`: Hook 'use-toast.ts' doesn't match useXxx pattern
- `./web/hooks/use-conversation-orchestrator.ts`: Hook 'use-conversation-orchestrator.ts' doesn't match useXxx pattern
- `./web/hooks/use-toast.ts`: Hook 'use-toast.ts' doesn't match useXxx pattern
- `./web/hooks/use-autonomous-conversations.ts`: Hook 'use-autonomous-conversations.ts' doesn't match useXxx pattern

### Typescript Interfaces
**Count**: 71

- `./web/components/memoryviewer.tsx`: Interface 'to' should start with 'I' prefix
- `./web/components/knowledge-graph.tsx`: Interface 'Link' should start with 'I' prefix
- `./web/components/agent-relationship-network.tsx`: Interface 'NetworkLink' should start with 'I' prefix
- `./web/components/readiness-panel.tsx`: Interface 'HardwareTarget' should start with 'I' prefix
- `./web/components/global-knowledge-graph.tsx`: Interface 'Node' should start with 'I' prefix
- ... and 66 more

### Typescript Handlers
**Count**: 3

- `./web/components/ui/carousel.tsx`: Event handler 'onSelect' should start with 'handle' not 'on'
- `./web/hooks/use-mobile.tsx`: Event handler 'onChange' should start with 'handle' not 'on'
- `./web/hooks/use-conversation-orchestrator.ts`: Event handler 'onSendMessageRef' should start with 'handle' not 'on'
