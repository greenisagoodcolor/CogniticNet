# Explorer Agent Model

## Model Metadata
- **Name**: Explorer
- **Version**: 1.0
- **Type**: Active Inference Agent
- **Description**: Exploration-focused agent that minimizes uncertainty about the environment

## State Space
```gnn
States: S
  position: H3Cell[resolution=7]
  energy: Real[0, 100]
  knowledge_coverage: Real[0, 1]
  explored_cells: Set[H3Cell]
  
Hidden States: H
  world_map: Graph[H3Cell, TerrainInfo]
  resource_locations: Set[H3Cell]
  uncertainty_map: Map[H3Cell, Real[0, 1]]
```

## Observation Space
```gnn
Observations: O
  visible_cells: List[H3Cell]
  terrain_type: Categorical[forest, plains, mountain, water]
  resources: List[Resource]
  other_agents: List[AgentInfo]
  energy_cost: Real[0, 10]
```

## Action Space
```gnn
Actions: A
  move: Direction[N, NE, SE, S, SW, NW]
  gather: Resource
  communicate: Message
  rest: Duration
```

## Generative Model
```gnn
# Observation model - how hidden states generate observations
P(o|s): observation_model
  visible_cells = h3.k_ring(position, 1)
  terrain_type = world_map[position].terrain
  resources = filter_visible(resource_locations, visible_cells)
  
# Transition model - how states evolve given actions  
P(s'|s,a): transition_model
  IF a.type == move:
    position' = h3.get_neighbor(position, a.direction)
    energy' = energy - movement_cost(position, position')
    explored_cells' = explored_cells ∪ {position'}
    
  IF a.type == gather:
    energy' = min(100, energy + a.resource.value)
    resource_locations' = resource_locations \ {position}
```

## Preferences (C)
```gnn
C_exploration: observation -> Real
  # Strongly prefer observations that reduce uncertainty
  preference = -uncertainty_map[visible_cells].mean()
  weight = 0.8  # High weight on exploration
  
C_energy: observation -> Real  
  # Moderate preference for maintaining energy
  preference = sigmoid(energy - 30)  # Worry when below 30
  weight = 0.2
  
C_discovery: observation -> Real
  # Reward for finding new resources
  preference = count(new_resources) * 2.0
  weight = 0.5
```

## Active Inference
```gnn
# Free Energy calculation
F(o, μ) = complexity(μ) - accuracy(o, μ) + pragmatic(μ)

# Belief update (perception)
μ(s) <- argmin F(o, μ)
       μ
       
# Policy selection (action)
π(a|s) <- argmin E[F(o', μ') | a, μ]
          a
```

## Initial Beliefs
```gnn
μ_0(world_map) = uniform  # No prior knowledge
μ_0(resources) = sparse   # Expect resources to be rare
μ_0(uncertainty) = 1.0    # Maximum uncertainty initially
```

## Learning Rules
```gnn
# Update uncertainty map after observations
uncertainty_map[observed_cells] *= 0.1  # Drastically reduce

# Learn terrain patterns
IF repeated_observation(terrain_pattern):
  world_map.add_pattern(terrain_pattern)
  
# Update resource distribution beliefs
resource_prior = update_dirichlet(resource_prior, observed_resources)
```

## Behavioral Policies
```gnn
# Exploration policy - maximize information gain
exploration_policy:
  target = argmax(uncertainty_map)
  path = a_star(position, target, world_map)
  RETURN path[0]
  
# Energy management policy  
energy_policy:
  IF energy < 20:
    target = nearest(resource_locations)
    RETURN move_toward(target)
  ELSE:
    RETURN exploration_policy()
    
# Main policy
main_policy:
  IF energy < 20:
    RETURN energy_policy()
  ELSE:
    RETURN exploration_policy()
```

## Model Parameters
```gnn
learning_rate: 0.1
discount_factor: 0.95
exploration_bonus: 2.0
energy_threshold: 20
communication_range: 3  # H3 cells
```

## Personality Mapping
```gnn
# From personality sliders to model parameters
exploration_weight = personality.exploration / 100
energy_weight = 1 - exploration_weight
learning_rate = 0.05 + (personality.curiosity / 100) * 0.15
risk_tolerance = personality.risk_tolerance / 100
``` 