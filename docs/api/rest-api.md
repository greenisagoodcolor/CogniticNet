# FreeAgentics REST API Documentation

## Overview

The FreeAgentics REST API provides programmatic access to all platform features including agent management, world simulation, knowledge graphs, and conversations.

**Base URL**: `http://localhost:8000/api` (development)

**Authentication**: Bearer token in Authorization header

**Content Type**: `application/json`

## Authentication

### Get API Token

```http
POST /api/auth/token
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "secure_password"
}
```

Response:

```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

Use token in subsequent requests:

```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Agents

### List Agents

```http
GET /api/agents
```

Query parameters:

- `status`: Filter by status (active, inactive, all)
- `class`: Filter by agent class
- `limit`: Number of results (default: 20)
- `offset`: Pagination offset

Response:

```json
{
  "agents": [
    {
      "id": "agent_123",
      "name": "CuriousExplorer",
      "class": "Explorer",
      "status": "active",
      "personality": {
        "openness": 85,
        "conscientiousness": 60,
        "extraversion": 50,
        "agreeableness": 70,
        "neuroticism": 40
      },
      "position": {
        "hex": "8928308280fffff",
        "x": 10,
        "y": 15
      },
      "resources": {
        "energy": 75,
        "materials": 20,
        "knowledge": 35
      },
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T14:45:00Z"
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### Get Agent Details

```http
GET /api/agents/{agent_id}
```

Response includes full agent data with GNN model:

```json
{
  "id": "agent_123",
  "name": "CuriousExplorer",
  "class": "Explorer",
  "status": "active",
  "personality": {...},
  "position": {...},
  "resources": {...},
  "gnn_model": {
    "model_name": "CuriousExplorer",
    "version": "1.0",
    "beliefs": [...],
    "preferences": {...},
    "policies": [...]
  },
  "knowledge_graph": {
    "nodes": 45,
    "edges": 67,
    "patterns": 12
  },
  "stats": {
    "distance_traveled": 234,
    "resources_gathered": 89,
    "conversations_had": 15,
    "knowledge_shared": 23
  }
}
```

### Create Agent

```http
POST /api/agents
Content-Type: application/json

{
  "name": "WiseScholar",
  "class": "Scholar",
  "personality": {
    "openness": 70,
    "conscientiousness": 85,
    "extraversion": 30,
    "agreeableness": 75,
    "neuroticism": 35
  },
  "backstory": "A scholar dedicated to understanding...",
  "starting_position": "random"
}
```

Response:

```json
{
  "id": "agent_456",
  "name": "WiseScholar",
  "status": "created",
  "gnn_model_url": "/api/agents/agent_456/gnn"
}
```

### Update Agent

```http
PATCH /api/agents/{agent_id}
Content-Type: application/json

{
  "status": "inactive",
  "notes": "Pausing for maintenance"
}
```

### Delete Agent

```http
DELETE /api/agents/{agent_id}
```

### Get Agent GNN Model

```http
GET /api/agents/{agent_id}/gnn
```

Response:

```markdown
---
model_name: WiseScholar
version: 1.0
agent_class: Scholar
---

## Beliefs

...
```

### Update Agent GNN Model

```http
PUT /api/agents/{agent_id}/gnn
Content-Type: text/markdown

[GNN model content]
```

## World

### Get World State

```http
GET /api/world
```

Response:

```json
{
  "dimensions": {
    "radius": 20,
    "total_hexes": 1261
  },
  "biomes": {
    "forest": 315,
    "plains": 378,
    "mountains": 252,
    "desert": 189,
    "water": 127
  },
  "resources": {
    "total": 450,
    "by_type": {
      "energy": 150,
      "materials": 200,
      "knowledge": 100
    }
  },
  "agents": {
    "active": 15,
    "total": 23
  }
}
```

### Get Hex Details

```http
GET /api/world/hex/{hex_id}
```

Response:

```json
{
  "hex_id": "8928308280fffff",
  "coordinates": {
    "x": 10,
    "y": 15
  },
  "biome": "forest",
  "elevation": 45,
  "resources": [
    {
      "type": "materials",
      "amount": 50
    }
  ],
  "agents": ["agent_123"],
  "visibility": 0.8
}
```

### Get Visible Hexes

```http
GET /api/world/visible?agent_id={agent_id}
```

Returns hexes visible to the specified agent.

### Update World

```http
PATCH /api/world
Content-Type: application/json

{
  "add_resources": [
    {
      "hex_id": "8928308280fffff",
      "type": "knowledge",
      "amount": 25
    }
  ],
  "modify_terrain": [
    {
      "hex_id": "8928308281fffff",
      "biome": "plains"
    }
  ]
}
```

## Simulation

### Start Simulation

```http
POST /api/simulation/start
Content-Type: application/json

{
  "speed": 1.0,
  "max_steps": 1000,
  "auto_save": true,
  "save_interval": 100
}
```

Response:

```json
{
  "simulation_id": "sim_789",
  "status": "running",
  "start_time": "2024-01-15T15:00:00Z"
}
```

### Pause Simulation

```http
POST /api/simulation/pause
```

### Resume Simulation

```http
POST /api/simulation/resume
```

### Stop Simulation

```http
POST /api/simulation/stop
```

### Get Simulation Status

```http
GET /api/simulation/status
```

Response:

```json
{
  "simulation_id": "sim_789",
  "status": "running",
  "current_step": 245,
  "elapsed_time": 123.45,
  "agents_active": 15,
  "events_processed": 1234
}
```

### Step Simulation

```http
POST /api/simulation/step
Content-Type: application/json

{
  "steps": 1
}
```

## Knowledge

### Get Agent Knowledge Graph

```http
GET /api/agents/{agent_id}/knowledge
```

Response:

```json
{
  "nodes": [
    {
      "id": "node_1",
      "type": "location",
      "data": {
        "hex_id": "8928308280fffff",
        "biome": "forest",
        "resources": ["materials"]
      }
    },
    {
      "id": "node_2",
      "type": "agent",
      "data": {
        "agent_id": "agent_456",
        "name": "WiseScholar",
        "trust_level": 0.8
      }
    }
  ],
  "edges": [
    {
      "source": "node_1",
      "target": "node_2",
      "type": "met_at",
      "weight": 1.0
    }
  ],
  "patterns": [
    {
      "id": "pattern_1",
      "type": "resource_location",
      "confidence": 0.85,
      "description": "Materials often found in forest biomes"
    }
  ]
}
```

### Query Knowledge

```http
POST /api/agents/{agent_id}/knowledge/query
Content-Type: application/json

{
  "query_type": "shortest_path",
  "from": "current_position",
  "to": "nearest_knowledge_resource"
}
```

### Share Knowledge

```http
POST /api/knowledge/share
Content-Type: application/json

{
  "from_agent": "agent_123",
  "to_agent": "agent_456",
  "knowledge_type": "locations",
  "filter": {
    "biome": "forest",
    "has_resources": true
  }
}
```

## Conversations

### Get Conversations

```http
GET /api/conversations
```

Query parameters:

- `agent_id`: Filter by participant
- `since`: Timestamp for recent conversations
- `limit`: Number of results

Response:

```json
{
  "conversations": [
    {
      "id": "conv_123",
      "participants": ["agent_123", "agent_456"],
      "start_time": "2024-01-15T14:30:00Z",
      "messages": [
        {
          "from": "agent_123",
          "to": "agent_456",
          "content": "Hello! I've discovered materials in the eastern forest.",
          "intent": "share_discovery",
          "timestamp": "2024-01-15T14:30:15Z"
        }
      ],
      "outcomes": {
        "knowledge_shared": true,
        "alliance_formed": false,
        "trade_completed": false
      }
    }
  ]
}
```

### Get Conversation Details

```http
GET /api/conversations/{conversation_id}
```

### Send Message

```http
POST /api/conversations/message
Content-Type: application/json

{
  "from_agent": "agent_123",
  "to_agent": "agent_456",
  "content": "Would you like to explore together?",
  "intent": "propose_alliance"
}
```

## Models

### List Available Models

```http
GET /api/models
```

Response:

```json
{
  "models": [
    {
      "name": "Explorer",
      "version": "1.0",
      "class": "Explorer",
      "description": "Base explorer template",
      "path": "models/base/explorer.gnn.md"
    }
  ]
}
```

### Get Model Content

```http
GET /api/models/{model_name}
```

### Validate Model

```http
POST /api/models/validate
Content-Type: text/markdown

[GNN model content]
```

Response:

```json
{
  "valid": true,
  "errors": [],
  "warnings": ["High neuroticism may cause frequent belief updates"]
}
```

## Backstory Generation

### Generate Backstory

```http
POST /api/generate/backstory
Content-Type: application/json

{
  "personality": {
    "openness": 80,
    "conscientiousness": 60,
    "extraversion": 50,
    "agreeableness": 70,
    "neuroticism": 40
  },
  "template": "origin_story",
  "keywords": ["ancient", "knowledge", "quest"]
}
```

Response:

```json
{
  "backstory": "Born in the shadow of ancient ruins...",
  "themes": ["exploration", "discovery", "wisdom"],
  "suggested_name": "Sage Pathfinder"
}
```

## System

### Health Check

```http
GET /api/health
```

Response:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "redis": "connected",
    "llm": "available"
  }
}
```

### Get Statistics

```http
GET /api/stats
```

Response:

```json
{
  "agents": {
    "total": 42,
    "active": 15,
    "by_class": {
      "Explorer": 12,
      "Merchant": 8,
      "Scholar": 15,
      "Guardian": 7
    }
  },
  "simulations": {
    "total_run": 156,
    "total_steps": 45678,
    "average_duration": 234.5
  },
  "knowledge": {
    "total_nodes": 12345,
    "total_patterns": 456,
    "shared_instances": 789
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "error": {
    "code": "AGENT_NOT_FOUND",
    "message": "Agent with ID agent_999 not found",
    "details": {
      "agent_id": "agent_999"
    }
  }
}
```

Common error codes:

- `UNAUTHORIZED`: Missing or invalid token
- `FORBIDDEN`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `VALIDATION_ERROR`: Invalid input data
- `CONFLICT`: Resource conflict
- `INTERNAL_ERROR`: Server error

## Rate Limiting

API requests are rate limited:

- Authenticated: 1000 requests/hour
- Unauthenticated: 100 requests/hour

Rate limit headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642252800
```

## Webhooks

Configure webhooks for real-time events:

```http
POST /api/webhooks
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "events": ["agent.created", "conversation.started", "pattern.discovered"],
  "secret": "webhook_secret"
}
```

Events are sent as POST requests with signature verification.

---

_For WebSocket API documentation, see [WebSocket API](websocket_api.md)_
