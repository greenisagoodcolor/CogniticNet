# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CogniticNet is a multi-agent UI design grid world for creating, managing, and observing autonomous AI agent interactions. It consists of a Next.js frontend and FastAPI Python backend, designed to explore emergent behaviors in multi-agent systems.
. CogniticNet as a comprehensive Active Inference agent platform following the GNN (Generalized Notation Notation) pattern. The platform now includes both the core Active Inference engine AND a full web interface for agent creation, world simulation, knowledge visualization, and conversation monitoring.

## Ar

### 1. Project Structure (GNN Pattern)

Created a follows a directory structure following GNN conventions with KISS and "triple play" docs, src, app separately f with a high level docker setup and quick guide. 

```
CogniticNet/
├── doc/                    # Documentation (GNN pattern)
│   ├── platform/          # Platform-specific guides
│   ├── api/              # API documentation
│   └── gnn_models/       # Model format specs
├── src/                   # Core engine (GNN pattern)
│   ├── pipeline/         # Numbered processing scripts
│   │   ├── main.py      # Pipeline orchestrator
│   │   ├── 1_initialize.py
│   │   └── 2_parse_gnn.py
│   └── gnn/             # GNN processing
├── app/                  # Next.js web interface
│   ├── (dashboard)/     # Main app routes
│   │   ├── agents/      # Agent creator
│   │   ├── world/       # World simulation
│   │   ├── knowledge/   # Knowledge graphs
│   │   └── conversations/ # Chat monitor
│   └── page.tsx         # Landing dashboard
├── environments/        # Environment configs
├── docker/             # Docker configurations
│   ├── development/
│   ├── testing/
│   ├── staging/
│   └── production/
└── models/            # GNN model library
```

### 2. Documentation

Created comprehensive documentation following GNN patterns:

- **README.md**: Complete platform overview with Triple Play architecture
- **doc/about_platform.md**: Vision, concepts, and use cases
- **doc/platform/getting_started.md**: Setup and quick start guide
- **doc/platform/agent_creator_guide.md**: Detailed agent creation instructions
- **doc/gnn_models/model_format.md**: GNN model specification
- **doc/api/rest_api.md**: Complete REST API documentation
- **DOCKER.md**: Comprehensive Docker deployment guide
- **environments/README.md**: Environment configuration guide

### 3. Processing Pipeline

Implemented GNN-style numbered pipeline scripts:

- **src/pipeline/main.py**: Orchestrator that discovers and runs numbered scripts
- **src/pipeline/1_initialize.py**: Environment setup and validation
- **src/pipeline/2_parse_gnn.py**: GNN model parsing and validation

Features:
- Dynamic step discovery
- Selective execution (--only-steps, --skip-steps)
- Comprehensive reporting
- Error handling and recovery

### 4. Web Interface Routes

Created full dashboard interface:

- **app/page.tsx**: Landing dashboard with stats and quick actions
- **app/(dashboard)/agents/page.tsx**: Agent management and creation
- **app/(dashboard)/world/page.tsx**: H3 world simulation view
- **app/(dashboard)/knowledge/page.tsx**: Knowledge graph visualization
- **app/(dashboard)/conversations/page.tsx**: Real-time conversation monitoring
- **app/(dashboard)/layout.tsx**: Shared dashboard layout

### 5. Docker Infrastructure

Created multi-environment Docker setup:

- **docker-compose.yml**: Root compose for quick start
- **Dockerfile**: Multi-stage build for all services
- **docker/development/docker-compose.yml**: Hot reload development
- **docker/[env]/**: Configurations for testing, staging, production, demo

Services configured:
- Frontend (Next.js)
- Backend (FastAPI)
- MCP Server
- PostgreSQL
- Redis
- Nginx (production)
- Adminer (development)

### 6. Environment Configuration

Created flexible environment system:

- Template in environments/README.md
- Support for .env.development, .env.testing, .env.staging, .env.production, .env.demo
- Comprehensive configuration options
- Security best practices

## Key Features Implemented

### Visual Design Tools
- Agent Creator with personality sliders
- AI-powered backstory generation
- Real-time GNN model preview
- Visual agent customization

### World Simulation
- H3 hexagonal grid visualization
- Multiple view modes (terrain, resources, agents)
- Simulation controls
- Hex detail panels

### Knowledge Systems
- Force-directed graph visualization
- Individual and collective views
- Pattern detection display
- Graph statistics

### Communication Monitor
- Real-time conversation streams
- Intent analysis
- Multi-agent dialogue support
- Emergent pattern detection

### Developer Experience
- GNN pipeline orchestration
- Comprehensive API documentation
- Docker development environment
- Hot reload support

## Technical Implementation

### Frontend Stack
- React 19 with Server Components
- Next.js 15 App Router
- TypeScript throughout
- Tailwind CSS + Shadcn UI
- Real-time WebSocket support

### Backend Stack
- Python 3.11+ with FastAPI
- GNN parser and validator
- Active Inference engine
- NetworkX for graphs
- Pydantic validation

### Infrastructure
- Docker containerization
- PostgreSQL + Redis
- Environment-based config
- Horizontal scaling ready

## Usage

### Quick Start
```bash
# Clone and setup
git clone https://github.com/ActiveInferenceInstitute/CogniticNet.git
cd CogniticNet
cp environments/README.md .env

# Run with Docker
docker-compose up

# Or run manually
python src/pipeline/main.py --only-steps 1,2
npm run dev
```

### Access Points
- Web Interface: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MCP Server: http://localhost:8001

## What Makes This Special

1. **GNN Integration**: First platform to fully implement GNN patterns for Active Inference
2. **Visual Tools**: No coding required to create complex agents
3. **Real-time Visualization**: See agents think and interact
4. **Hardware Ready**: Export agents for deployment
5. **Research Platform**: Reproducible experiments with Active Inference

## Next Steps

The platform is now ready for:
1. Creating agents through the visual interface
2. Running simulations in the H3 world
3. Analyzing emergent behaviors
4. Deploying to production environments
5. Contributing new agent models

---

*"Making Active Inference accessible, visual, and deployable"*