# Agent Creation Guide

This comprehensive guide provides step-by-step instructions for creating agents in CogniticNet, from basic concepts to advanced configurations and deployment strategies.

## Table of Contents
- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Agent Types and Personalities](#agent-types-and-personalities)
- [Step-by-Step Agent Creation](#step-by-step-agent-creation)
- [Configuration Reference](#configuration-reference)
- [Deployment Strategies](#deployment-strategies)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Advanced Topics](#advanced-topics)

## Overview

CogniticNet agents are autonomous entities that operate within the simulation environment using Active Inference principles. Each agent:

- **Perceives** its environment through observations
- **Thinks** using Active Inference and optional LLM integration
- **Acts** based on decisions and behaviors
- **Updates** its internal state based on results

### Key Concepts

- **Agent Types**: Predefined behavioral profiles (explorer, merchant, guardian, etc.)
- **Personality**: Numerical traits that influence behavior
- **Goals**: Objectives the agent tries to achieve
- **Capabilities**: Actions the agent can perform
- **Coalition Formation**: Agents can work together in groups

## Prerequisites

Before creating agents, ensure you have:

### System Requirements
- Python 3.11+ installed
- CogniticNet project set up and running
- Database (PostgreSQL) configured
- Redis (optional, for distributed operations)

### API Access
- CogniticNet server running on `http://localhost:8000` (default)
- Valid API authentication (if configured)
- Network connectivity to the server

### Dependencies
```bash
# Core dependencies
pip install httpx asyncio pydantic

# Optional for enhanced features
pip install numpy scipy torch  # For AI features
```

## Quick Start

The fastest way to create demo agents is using the provided creation script:

```bash
# Create 20 diverse demo agents
python scripts/demo/create-demo-agents.py --count 20

# Create agents with specific distribution
python scripts/demo/create-demo-agents.py \
    --count 30 \
    --explorers 0.3 \
    --merchants 0.2 \
    --guardians 0.2 \
    --scholars 0.15 \
    --monitors 0.1 \
    --specialists 0.05

# Enable coalition formation
python scripts/demo/create-demo-agents.py \
    --count 25 \
    --enable-coalitions \
    --coalition-threshold 0.6
```

### Quick API Creation

For programmatic creation:

```python
import asyncio
import httpx
from scripts.demo.create_demo_agents import AgentTypeGenerator, Position

async def create_simple_agent():
    # Generate agent configuration
    position = Position(x=100.0, y=50.0, z=0.0)
    agent = AgentTypeGenerator.generate_agent('explorer', position)

    # Create via API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/agents",
            json=agent.to_dict()
        )
        return response.json()

# Run it
agent_data = asyncio.run(create_simple_agent())
print(f"Created agent: {agent_data['agent_id']}")
```

## Agent Types and Personalities

CogniticNet supports six primary agent types, each with distinct behavioral profiles:

### 1. Explorer 🗺️
**Purpose**: Discovery and territorial mapping

**Personality Profile**:
- High exploration tendency (0.9)
- Moderate cooperation (0.6)
- High risk tolerance (0.8)
- High adaptability (0.8)

**Capabilities**: `move`, `observe`, `map`, `scout`, `navigate`

**Typical Goals**:
- Explore new areas
- Map territory
- Discover resources
- Chart unknown regions

**Use Cases**:
- Initial world exploration
- Resource discovery missions
- Pathfinding for other agents

---

### 2. Merchant 💼
**Purpose**: Trade and resource management

**Personality Profile**:
- Low exploration tendency (0.4)
- High cooperation (0.8)
- Low risk tolerance (0.3)
- High communication frequency (0.9)

**Capabilities**: `trade`, `negotiate`, `assess_value`, `transport`, `communicate`

**Typical Goals**:
- Maximize profit
- Establish trade routes
- Build relationships
- Optimize resource distribution

**Use Cases**:
- Economic simulations
- Resource trading networks
- Market dynamics modeling

---

### 3. Guardian 🛡️
**Purpose**: Protection and security

**Personality Profile**:
- Low exploration tendency (0.2)
- Very high cooperation (0.9)
- Very low risk tolerance (0.1)
- High leadership tendency (0.8)

**Capabilities**: `defend`, `protect`, `monitor`, `alert`, `coordinate`

**Typical Goals**:
- Protect allies
- Maintain security
- Prevent threats
- Coordinate defenses

**Use Cases**:
- Security simulations
- Defense coordination
- Risk management scenarios

---

### 4. Scholar 📚
**Purpose**: Research and knowledge acquisition

**Personality Profile**:
- Moderate exploration (0.3)
- High cooperation (0.7)
- Low risk tolerance (0.2)
- Very high learning rate (0.9)

**Capabilities**: `research`, `analyze`, `synthesize`, `document`, `teach`

**Typical Goals**:
- Acquire knowledge
- Share discoveries
- Solve problems
- Document findings

**Use Cases**:
- Research simulations
- Knowledge networks
- Problem-solving scenarios

---

### 5. Monitor 👁️
**Purpose**: Observation and intelligence gathering

**Personality Profile**:
- Moderate exploration (0.5)
- Moderate cooperation (0.5)
- Moderate risk tolerance (0.4)
- Very high adaptability (0.9)

**Capabilities**: `observe`, `record`, `analyze_patterns`, `report`, `track`

**Typical Goals**:
- Gather intelligence
- Monitor changes
- Report findings
- Track patterns

**Use Cases**:
- Surveillance systems
- Data collection
- Pattern recognition

---

### 6. Specialist 🎯
**Purpose**: Domain expertise and optimization

**Personality Profile**:
- High exploration (0.6)
- Lower cooperation (0.4)
- Moderate risk tolerance (0.5)
- High leadership tendency (0.7)

**Capabilities**: `specialize`, `optimize`, `innovate`, `execute`, `perfect`

**Typical Goals**:
- Master domain
- Optimize performance
- Achieve excellence
- Innovate solutions

**Use Cases**:
- Optimization problems
- Specialized tasks
- Performance tuning

## Step-by-Step Agent Creation

### Step 1: Define Agent Requirements

Before creating an agent, determine:

1. **Purpose**: What should the agent accomplish?
2. **Environment**: Where will the agent operate?
3. **Interactions**: Will it work alone or with others?
4. **Constraints**: Any limitations or special requirements?

### Step 2: Choose Agent Type

Select the most appropriate base type:

```python
from scripts.demo.create_demo_agents import AgentTypeGenerator

# Available types
agent_types = ['explorer', 'merchant', 'guardian', 'scholar', 'monitor', 'specialist']

# For discovery tasks
agent_type = 'explorer'

# For economic simulations
agent_type = 'merchant'

# For security scenarios
agent_type = 'guardian'
```

### Step 3: Configure Position

Set the agent's starting location:

```python
from scripts.demo.create_demo_agents import Position

# Basic positioning
position = Position(x=100.0, y=200.0, z=0.0)

# Random positioning within bounds
import random
world_bounds = {'min_x': -1000, 'max_x': 1000, 'min_y': -1000, 'max_y': 1000}
position = Position(
    x=random.uniform(world_bounds['min_x'], world_bounds['max_x']),
    y=random.uniform(world_bounds['min_y'], world_bounds['max_y']),
    z=0.0
)
```

### Step 4: Customize Personality (Optional)

Adjust personality traits for specific behaviors:

```python
# Generate base agent
agent = AgentTypeGenerator.generate_agent('explorer', position)

# Customize personality
agent.personality.exploration_tendency = 0.95  # Very exploratory
agent.personality.cooperation_level = 0.8      # More cooperative
agent.personality.risk_tolerance = 0.6         # Moderate risk
```

### Step 5: Set Goals and Capabilities

Customize the agent's objectives:

```python
# Add custom goals
custom_goals = [
    "explore_quadrant_alpha",
    "establish_base_camp",
    "report_discoveries_hourly"
]
agent.goals.extend(custom_goals)

# Add custom capabilities
custom_capabilities = ["build_shelter", "signal_rescue"]
agent.capabilities.extend(custom_capabilities)
```

### Step 6: Configure Advanced Features

Set up additional parameters:

```python
# Energy management
agent.energy = 85.0
agent.max_energy = 120.0

# Knowledge and metadata
agent.knowledge.update({
    "mission_priority": "high",
    "reporting_frequency": 30,  # minutes
    "authorized_areas": ["alpha", "beta"]
})

agent.metadata.update({
    "creator": "mission_control",
    "deployment_phase": "initial_survey",
    "expected_duration": 240  # minutes
})
```

### Step 7: Create via API

Deploy the agent to the simulation:

```python
import asyncio
import httpx

async def create_agent_api(agent_config):
    api_config = {
        'base_url': 'http://localhost:8000',
        'timeout': 30.0
    }

    async with httpx.AsyncClient(timeout=api_config['timeout']) as client:
        try:
            # Convert agent config to dictionary
            agent_data = {
                'name': agent_config.name,
                'agent_type': agent_config.agent_type,
                'position': {
                    'x': agent_config.position.x,
                    'y': agent_config.position.y,
                    'z': agent_config.position.z
                },
                'personality': {
                    'exploration_tendency': agent_config.personality.exploration_tendency,
                    'cooperation_level': agent_config.personality.cooperation_level,
                    'risk_tolerance': agent_config.personality.risk_tolerance,
                    'learning_rate': agent_config.personality.learning_rate,
                    'communication_frequency': agent_config.personality.communication_frequency,
                    'resource_sharing': agent_config.personality.resource_sharing,
                    'leadership_tendency': agent_config.personality.leadership_tendency,
                    'adaptability': agent_config.personality.adaptability
                },
                'energy': agent_config.energy,
                'max_energy': agent_config.max_energy,
                'capabilities': agent_config.capabilities,
                'goals': agent_config.goals,
                'knowledge': agent_config.knowledge,
                'metadata': agent_config.metadata
            }

            # Create agent
            response = await client.post(
                f"{api_config['base_url']}/api/v1/agents",
                json=agent_data,
                headers={'Content-Type': 'application/json'}
            )

            response.raise_for_status()
            result = response.json()

            print(f"✅ Agent created successfully!")
            print(f"   Agent ID: {result.get('agent_id')}")
            print(f"   Name: {result.get('name')}")
            print(f"   Type: {result.get('agent_type')}")

            return result

        except httpx.HTTPError as e:
            print(f"❌ HTTP Error: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"   Status: {e.response.status_code}")
                print(f"   Details: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            return None

# Create the agent
result = asyncio.run(create_agent_api(agent))
```

### Step 8: Verify Deployment

Confirm the agent is operational:

```python
async def verify_agent(agent_id):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://localhost:8000/api/v1/agents/{agent_id}")
        if response.status_code == 200:
            agent_data = response.json()
            print(f"✅ Agent {agent_id} is active")
            print(f"   Status: {agent_data.get('status')}")
            print(f"   Energy: {agent_data.get('energy')}")
            return True
        else:
            print(f"❌ Agent {agent_id} verification failed")
            return False

# Verify if result contains agent_id
if result and 'agent_id' in result:
    asyncio.run(verify_agent(result['agent_id']))
```

## Configuration Reference

### AgentConfig Fields

```python
@dataclass
class AgentConfig:
    name: str                    # Unique agent name
    agent_type: str             # Type: explorer, merchant, etc.
    personality: AgentPersonality # Personality traits (0.0-1.0)
    position: Position          # 3D coordinates
    energy: float = 100.0       # Current energy level
    max_energy: float = 100.0   # Maximum energy capacity
    capabilities: List[str]     # Available actions
    goals: List[str]           # Agent objectives
    knowledge: Dict[str, Any]   # Agent knowledge base
    metadata: Dict[str, Any]    # Additional configuration
```

### Personality Traits

| Trait | Range | Description | Impact |
|-------|-------|-------------|---------|
| `exploration_tendency` | 0.0-1.0 | Likelihood to explore new areas | Movement patterns, curiosity |
| `cooperation_level` | 0.0-1.0 | Willingness to work with others | Coalition formation, sharing |
| `risk_tolerance` | 0.0-1.0 | Acceptance of uncertain outcomes | Decision making, action selection |
| `learning_rate` | 0.0-1.0 | Speed of adaptation and learning | Belief updates, skill acquisition |
| `communication_frequency` | 0.0-1.0 | How often agent communicates | Message sending, information sharing |
| `resource_sharing` | 0.0-1.0 | Willingness to share resources | Economic behavior, cooperation |
| `leadership_tendency` | 0.0-1.0 | Likelihood to take leadership roles | Group dynamics, initiative taking |
| `adaptability` | 0.0-1.0 | Flexibility in changing situations | Response to environment changes |

### Energy Management

```python
# Energy configuration
agent.energy = 80.0           # Starting energy (0-max_energy)
agent.max_energy = 120.0      # Maximum capacity

# Energy costs (configured per action type)
action_costs = {
    'move': 2.0,
    'observe': 1.0,
    'communicate': 1.5,
    'trade': 3.0,
    'defend': 4.0
}
```

## Deployment Strategies

### Single Agent Deployment

```python
# Create and deploy individual agent
agent = AgentTypeGenerator.generate_agent('explorer', position)
result = await create_agent_api(agent)
```

### Batch Deployment

```python
# Create multiple agents efficiently
async def deploy_agent_batch(agent_configs, batch_size=10):
    results = []

    for i in range(0, len(agent_configs), batch_size):
        batch = agent_configs[i:i+batch_size]

        # Create batch concurrently
        tasks = [create_agent_api(config) for config in batch]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"❌ Batch creation error: {result}")
            else:
                results.append(result)

        # Brief pause between batches
        await asyncio.sleep(1.0)

    return results

# Deploy 50 agents in batches of 10
agent_configs = AgentTypeGenerator.generate_diverse_batch(50, world_bounds)
results = await deploy_agent_batch(agent_configs, batch_size=10)
```

### Coalition Deployment

```python
# Create agents designed to work together
from scripts.demo.create_demo_agents import CoalitionManager

# Generate compatible agents
agents = AgentTypeGenerator.generate_diverse_batch(20, world_bounds)

# Form coalitions
coalitions = CoalitionManager.form_coalitions(
    agents,
    min_coalition_size=3,
    max_coalition_size=6,
    compatibility_threshold=0.6
)

# Deploy coalitions
for i, coalition in enumerate(coalitions):
    print(f"Coalition {i+1}: {len(coalition)} agents")

    # Deploy coalition members
    coalition_results = []
    for agent in coalition:
        result = await create_agent_api(agent)
        if result:
            coalition_results.append(result)

    # Set up coalition coordination
    if len(coalition_results) > 1:
        await setup_coalition_coordination(coalition_results)
```

## Best Practices

### 1. Agent Naming

```python
# Use descriptive, unique names
good_names = [
    "Explorer-Alpha-001",
    "Merchant-Trading-Post-1",
    "Guardian-Perimeter-West",
    "Scholar-Research-Team-A"
]

# Avoid generic names
avoid_names = ["Agent1", "test", "temp"]
```

### 2. Position Planning

```python
# Strategic positioning
positions = {
    'explorers': [
        Position(x=-500, y=-500),  # Southwest corner
        Position(x=500, y=500),    # Northeast corner
    ],
    'guardians': [
        Position(x=0, y=0),        # Central protection
        Position(x=-250, y=250),   # Strategic points
    ],
    'merchants': [
        Position(x=100, y=-100),   # Near trade routes
    ]
}
```

### 3. Personality Tuning

```python
# Balanced personalities for stability
def create_balanced_explorer():
    agent = AgentTypeGenerator.generate_agent('explorer', position)

    # Fine-tune for specific mission
    agent.personality.exploration_tendency = 0.85  # High but not reckless
    agent.personality.cooperation_level = 0.75     # Team player
    agent.personality.risk_tolerance = 0.65        # Calculated risks

    return agent
```

### 4. Error Handling

```python
async def robust_agent_creation(agent_config, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await create_agent_api(agent_config)
            if result:
                return result
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    print(f"❌ Failed to create agent after {max_retries} attempts")
    return None
```

### 5. Performance Monitoring

```python
# Monitor agent creation performance
import time

async def monitored_creation(agent_configs):
    start_time = time.time()
    results = []

    for i, config in enumerate(agent_configs):
        agent_start = time.time()
        result = await create_agent_api(config)
        agent_time = time.time() - agent_start

        if result:
            results.append(result)
            print(f"Agent {i+1}/{len(agent_configs)} created in {agent_time:.2f}s")
        else:
            print(f"❌ Agent {i+1} creation failed")

    total_time = time.time() - start_time
    success_rate = len(results) / len(agent_configs) * 100

    print(f"📊 Summary:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Average time per agent: {total_time/len(agent_configs):.2f}s")

    return results
```

## Troubleshooting

### Common Issues and Solutions

#### 1. API Connection Errors

**Problem**: Cannot connect to CogniticNet API

**Solutions**:
```python
# Check server status
async def check_server_status():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print("✅ Server is running")
                return True
            else:
                print(f"⚠️ Server responded with status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")
        return False

# Verify before creating agents
if await check_server_status():
    # Proceed with agent creation
    pass
```

#### 2. Agent Creation Fails

**Problem**: HTTP 400/422 errors during creation

**Common causes and fixes**:

```python
# Validate agent configuration before sending
def validate_agent_config(agent_config):
    errors = []

    # Check required fields
    if not agent_config.name:
        errors.append("Agent name is required")

    if agent_config.agent_type not in ['explorer', 'merchant', 'guardian', 'scholar', 'monitor', 'specialist']:
        errors.append(f"Invalid agent type: {agent_config.agent_type}")

    # Check personality values
    personality_attrs = [
        'exploration_tendency', 'cooperation_level', 'risk_tolerance',
        'learning_rate', 'communication_frequency', 'resource_sharing',
        'leadership_tendency', 'adaptability'
    ]

    for attr in personality_attrs:
        value = getattr(agent_config.personality, attr)
        if not (0.0 <= value <= 1.0):
            errors.append(f"Personality {attr} must be between 0.0 and 1.0, got {value}")

    # Check energy values
    if agent_config.energy < 0 or agent_config.energy > agent_config.max_energy:
        errors.append(f"Energy {agent_config.energy} must be between 0 and {agent_config.max_energy}")

    return errors

# Use validation before creation
errors = validate_agent_config(agent)
if errors:
    print("❌ Agent configuration errors:")
    for error in errors:
        print(f"   - {error}")
else:
    result = await create_agent_api(agent)
```

#### 3. Position Conflicts

**Problem**: Agents created in invalid positions

**Solution**:
```python
# Get valid world bounds before positioning
async def get_world_bounds():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/api/v1/world")
            if response.status_code == 200:
                world_data = response.json()
                return world_data.get('bounds', {
                    'min_x': -1000, 'max_x': 1000,
                    'min_y': -1000, 'max_y': 1000
                })
    except Exception as e:
        print(f"Warning: Could not get world bounds, using defaults: {e}")

    return {'min_x': -1000, 'max_x': 1000, 'min_y': -1000, 'max_y': 1000}

# Use valid bounds for positioning
world_bounds = await get_world_bounds()
position = Position(
    x=random.uniform(world_bounds['min_x'], world_bounds['max_x']),
    y=random.uniform(world_bounds['min_y'], world_bounds['max_y']),
    z=0.0
)
```

#### 4. Memory/Performance Issues

**Problem**: Slow agent creation or high memory usage

**Solutions**:

```python
# Implement rate limiting
import asyncio
from asyncio import Semaphore

async def rate_limited_creation(agent_configs, max_concurrent=5):
    semaphore = Semaphore(max_concurrent)

    async def create_with_limit(config):
        async with semaphore:
            return await create_agent_api(config)

    tasks = [create_with_limit(config) for config in agent_configs]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Monitor memory usage
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.1f} MB")
    return memory_mb

# Check memory before large batch operations
initial_memory = monitor_memory()
results = await rate_limited_creation(agent_configs)
final_memory = monitor_memory()
print(f"Memory increased by: {final_memory - initial_memory:.1f} MB")
```

### Debugging Tools

#### Agent Status Checker

```python
async def debug_agent_status(agent_id):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://localhost:8000/api/v1/agents/{agent_id}")
            if response.status_code == 200:
                agent_data = response.json()
                print(f"🔍 Agent {agent_id} Debug Info:")
                print(f"   Name: {agent_data.get('name')}")
                print(f"   Type: {agent_data.get('agent_type')}")
                print(f"   Status: {agent_data.get('status')}")
                print(f"   Energy: {agent_data.get('energy')}/{agent_data.get('max_energy')}")
                print(f"   Position: ({agent_data.get('position', {}).get('x')}, {agent_data.get('position', {}).get('y')})")
                print(f"   Goals: {len(agent_data.get('goals', []))}")
                print(f"   Capabilities: {len(agent_data.get('capabilities', []))}")
                return agent_data
            else:
                print(f"❌ Agent {agent_id} not found (status {response.status_code})")
                return None
        except Exception as e:
            print(f"❌ Error checking agent {agent_id}: {e}")
            return None
```

#### Configuration Validator

```python
def deep_validate_config(agent_config):
    """Comprehensive configuration validation"""
    issues = []
    warnings = []

    # Name validation
    if len(agent_config.name) < 3:
        issues.append("Agent name should be at least 3 characters")
    if len(agent_config.name) > 100:
        issues.append("Agent name should be less than 100 characters")

    # Personality balance check
    p = agent_config.personality
    high_traits = sum([
        p.exploration_tendency > 0.8,
        p.cooperation_level > 0.8,
        p.risk_tolerance > 0.8,
        p.leadership_tendency > 0.8
    ])

    if high_traits > 2:
        warnings.append("Agent has many high personality traits, may be unbalanced")

    # Energy efficiency
    if agent_config.energy < agent_config.max_energy * 0.5:
        warnings.append("Agent starting with low energy, may need immediate attention")

    # Goals validation
    if len(agent_config.goals) == 0:
        warnings.append("Agent has no goals defined")
    elif len(agent_config.goals) > 10:
        warnings.append("Agent has many goals, may be inefficient")

    # Capabilities validation
    if len(agent_config.capabilities) == 0:
        issues.append("Agent has no capabilities defined")

    return {
        'issues': issues,
        'warnings': warnings,
        'valid': len(issues) == 0
    }
```

## Advanced Topics

### Custom Agent Types

Create specialized agent types for unique use cases:

```python
class CustomAgentTypeGenerator(AgentTypeGenerator):
    """Extended agent type generator with custom types"""

    CUSTOM_TYPES = {
        'negotiator': {
            'base_personality': {
                'exploration_tendency': 0.3,
                'cooperation_level': 0.9,
                'risk_tolerance': 0.4,
                'learning_rate': 0.8,
                'communication_frequency': 0.95,
                'resource_sharing': 0.6,
                'leadership_tendency': 0.7,
                'adaptability': 0.8
            },
            'capabilities': ['negotiate', 'mediate', 'assess_proposals', 'communicate', 'analyze_relationships'],
            'base_goals': ['resolve_conflicts', 'facilitate_agreements', 'optimize_outcomes'],
            'energy_range': (70, 90),
            'names': ['Mediator Prime', 'Negotiator Alpha', 'Diplomat One']
        }
    }

    @classmethod
    def generate_custom_agent(cls, agent_type: str, position: Position, **kwargs):
        # Check custom types first
        if agent_type in cls.CUSTOM_TYPES:
            type_def = cls.CUSTOM_TYPES[agent_type]
            # Use similar logic as base class
            return cls._create_from_definition(type_def, agent_type, position, **kwargs)
        else:
            # Fall back to base types
            return super().generate_agent(agent_type, position, **kwargs)
```

### Dynamic Personality Adjustment

Adjust agent personalities based on performance:

```python
async def adjust_personality_based_on_performance(agent_id, performance_data):
    """Dynamically adjust agent personality based on performance metrics"""

    # Get current agent state
    current_agent = await debug_agent_status(agent_id)
    if not current_agent:
        return False

    # Calculate adjustments
    adjustments = {}

    # If agent is underperforming in exploration
    if performance_data.get('exploration_efficiency', 0) < 0.5:
        adjustments['exploration_tendency'] = min(1.0,
            current_agent['personality']['exploration_tendency'] + 0.1)

    # If agent is having cooperation issues
    if performance_data.get('cooperation_success', 0) < 0.6:
        adjustments['cooperation_level'] = min(1.0,
            current_agent['personality']['cooperation_level'] + 0.15)

    # Apply adjustments via API
    if adjustments:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"http://localhost:8000/api/v1/agents/{agent_id}/personality",
                json=adjustments
            )
            return response.status_code == 200

    return True
```

### Integration with External Systems

Connect agents to external data sources:

```python
async def create_data_driven_agent(data_source_config):
    """Create agent with configuration driven by external data"""

    # Fetch configuration from external source
    external_data = await fetch_external_config(data_source_config)

    # Generate agent based on external parameters
    agent_type = external_data.get('recommended_type', 'explorer')
    position = Position(
        x=external_data.get('optimal_x', 0),
        y=external_data.get('optimal_y', 0)
    )

    agent = AgentTypeGenerator.generate_agent(agent_type, position)

    # Override with external data
    if 'personality_overrides' in external_data:
        for trait, value in external_data['personality_overrides'].items():
            if hasattr(agent.personality, trait):
                setattr(agent.personality, trait, value)

    # Add external metadata
    agent.metadata.update({
        'data_source': data_source_config['source'],
        'external_id': external_data.get('id'),
        'last_sync': datetime.now().isoformat()
    })

    return agent

async def fetch_external_config(config):
    """Placeholder for external data fetching"""
    # This would connect to your external system
    return {
        'recommended_type': 'explorer',
        'optimal_x': 150,
        'optimal_y': -200,
        'personality_overrides': {
            'exploration_tendency': 0.95,
            'cooperation_level': 0.8
        },
        'id': 'ext_001'
    }
```

---

## Summary

This guide covers the complete agent creation process in CogniticNet, from basic concepts to advanced deployment strategies. Key takeaways:

1. **Start Simple**: Use the demo script for quick experimentation
2. **Plan Carefully**: Consider agent types, positions, and goals
3. **Validate Thoroughly**: Check configurations before deployment
4. **Monitor Performance**: Track creation success and agent behavior
5. **Handle Errors Gracefully**: Implement robust error handling
6. **Scale Thoughtfully**: Use batch operations and rate limiting

For additional support:
- Check the [API Documentation](../api/README.md)
- Review [Coalition Formation Guide](./coalition-formation.md)
- See [Troubleshooting Guide](../troubleshooting.md)
- Join the developer community discussions

Happy agent creation! 🤖✨
