# Merchant Agent Model

## Model Metadata
- **Name**: Merchant
- **Version**: 1.0
- **Type**: Active Inference Agent
- **Description**: Trade-focused agent that minimizes surprise about resource availability and maximizes value through exchange

## State Space
```gnn
States: S
  position: H3Cell[resolution=7]
  energy: Real[0, 100]
  inventory: Map[ResourceType, Integer]
  wealth: Real[0, ∞)
  trade_history: List[TradeRecord]
  
Hidden States: H
  market_prices: Map[ResourceType, Real]
  agent_locations: Map[AgentId, H3Cell]
  trade_networks: Graph[AgentId, TrustScore]
  resource_distribution: Map[H3Cell, ResourceProbability]
```

## Observation Space
```gnn
Observations: O
  visible_cells: List[H3Cell]
  nearby_agents: List[AgentInfo]
  local_resources: List[Resource]
  trade_offers: List[TradeOffer]
  market_signals: List[PriceSignal]
```

## Action Space
```gnn
Actions: A
  move: Direction[N, NE, SE, S, SW, NW]
  gather: Resource
  propose_trade: TradeOffer
  accept_trade: TradeId
  broadcast_prices: PriceList
  negotiate: CounterOffer
```

## Generative Model
```gnn
# Observation model
P(o|s): observation_model
  visible_cells = h3.k_ring(position, 1)
  nearby_agents = filter_by_distance(agent_locations, position, 3)
  trade_opportunities = generate_from_network(trade_networks, nearby_agents)
  
# Transition model  
P(s'|s,a): transition_model
  IF a.type == trade:
    inventory' = update_inventory(inventory, a.trade_details)
    wealth' = wealth + calculate_profit(a.trade_details, market_prices)
    trade_history' = trade_history + [a.trade_details]
    
  IF a.type == move:
    position' = h3.get_neighbor(position, a.direction)
    energy' = energy - movement_cost(position, position')
```

## Preferences (C)
```gnn
C_profit: observation -> Real
  # Strongly prefer profitable trades
  expected_profit = sum(trade_offers.map(evaluate_profit))
  preference = log(1 + expected_profit)
  weight = 0.7
  
C_inventory: observation -> Real  
  # Prefer balanced inventory
  diversity = entropy(inventory.values())
  preference = diversity - inventory_cost(inventory)
  weight = 0.3
  
C_reputation: observation -> Real
  # Value good trade relationships
  trust_score = mean(trade_networks[nearby_agents].trust)
  preference = trust_score
  weight = 0.4
```

## Active Inference
```gnn
# Market-aware free energy
F_market(o, μ) = market_surprise(o, μ) + inventory_complexity(μ) + trade_risk(μ)

# Belief update with market priors
μ(market) <- bayesian_update(μ_prior, market_signals)

# Trade policy selection
π_trade(a|s) <- softmax(-expected_free_energy(a) / temperature)
  where temperature = market_volatility()
```

## Initial Beliefs
```gnn
μ_0(market_prices) = historical_average
μ_0(resource_distribution) = uniform_with_bias(biome_types)
μ_0(agent_trustworthiness) = 0.5  # Neutral initial trust
```

## Learning Rules
```gnn
# Update market price beliefs
market_prices = exponential_moving_average(
  market_prices, 
  observed_trades, 
  alpha=0.2
)

# Learn agent trading patterns
FOR agent IN trade_partners:
  pattern = extract_trading_pattern(trade_history, agent)
  trade_networks[agent].pattern = pattern
  
# Update resource distribution model
resource_distribution = update_beta_binomial(
  resource_distribution,
  observed_resources
)
```

## Behavioral Policies
```gnn
# Market making policy
market_maker_policy:
  spread = calculate_bid_ask_spread(market_volatility)
  buy_price = market_price - spread/2
  sell_price = market_price + spread/2
  RETURN broadcast_prices(buy_price, sell_price)
  
# Arbitrage policy
arbitrage_policy:
  opportunities = find_price_differences(nearby_agents)
  IF profitable_route(opportunities):
    RETURN execute_arbitrage(opportunities)
    
# Inventory management
inventory_policy:
  IF inventory_imbalanced():
    needed = most_needed_resource()
    RETURN seek_trade(needed)
  ELSE:
    RETURN market_maker_policy()
    
# Main policy
main_policy:
  IF good_trade_available():
    RETURN accept_best_trade()
  ELIF arbitrage_opportunity():
    RETURN arbitrage_policy()
  ELSE:
    RETURN inventory_policy()
```

## Model Parameters
```gnn
learning_rate: 0.15
discount_factor: 0.9
risk_aversion: 0.3
min_profit_margin: 0.1
max_inventory_size: 50
trust_decay_rate: 0.05
market_memory: 20  # trades
```

## Personality Mapping
```gnn
# From personality sliders to model parameters
risk_aversion = 1 - (personality.risk_tolerance / 100)
negotiation_skill = personality.cooperation / 100
market_memory = 10 + (personality.efficiency / 100) * 40
trust_initial = 0.3 + (personality.cooperation / 100) * 0.4
```

## Social Protocols
```gnn
# Trade negotiation protocol
negotiate_trade:
  initial_offer = calculate_fair_offer(inventory, their_needs)
  
  WHILE not agreed AND rounds < 5:
    IF their_counter_offer > my_minimum:
      RETURN accept()
    ELSE:
      my_counter = interpolate(initial_offer, their_offer, round/5)
      RETURN counter_offer(my_counter)
      
# Trust update after trade
update_trust(agent, trade_outcome):
  IF trade_successful:
    trust[agent] = min(1.0, trust[agent] + 0.1)
  ELSE:
    trust[agent] = max(0.0, trust[agent] - 0.2)
``` 