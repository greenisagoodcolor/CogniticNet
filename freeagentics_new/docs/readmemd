# FreeAgentics Agent Simulator

<div align="center">

![FreeAgentics Logo](public/placeholder-logo.svg)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.9-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-%3E%3D20.10-blue.svg)](https://www.docker.com/)

**A sophisticated multi-agent simulation platform implementing Active Inference principles for emergent intelligence and collaborative behavior.**

[Demo](https://freeagentics.demo) | [Documentation](doc/) | [Getting Started](doc/platform/getting_started.md) | [API Reference](doc/api/rest_api.md)

</div>

## 🌟 Overview

FreeAgentics is an advanced agent-based modeling platform that combines Active Inference theory with graph neural networks to create intelligent, autonomous agents capable of:

- **Emergent Behavior**: Agents develop complex behaviors through interaction and learning
- **Collaborative Intelligence**: Multi-agent systems that share knowledge and coordinate actions
- **Active Inference**: Agents minimize surprise and uncertainty through predictive processing
- **Real-time Adaptation**: Dynamic learning and behavior modification based on experience

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Python 3.9+ with pip
- Docker and Docker Compose (optional)
- 4GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/freeagentics.git
cd freeagentics

# Install dependencies
npm install
pip install -r requirements.txt

# Set up environment variables
cd environments && ./setup-env.sh
# Or manually:
# cp environments/env.example environments/.env.development
# Edit .env.development with your configuration

# Initialize the database
./scripts/setup-database.sh
# Or manually:
# cd src/database
# python manage.py init

# Start the development server
npm run dev
```

Visit `http://localhost:3000` to access the web interface.

For detailed setup instructions and development workflow, see [DEVELOPMENT.md](DEVELOPMENT.md).

### Docker Deployment

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
- [GNN Model Format](doc/gnn_models/model_format.md)
- [Contributing Guide](CONTRIBUTING.md)

### Examples
- [Basic Agent Creation](examples/basic_agent.py)
- [Custom GNN Models](examples/custom_gnn.py)
- [Multi-Agent Scenarios](examples/scenarios/)

## 🛠️ Development

For detailed development setup and workflows, see:
- [Development Guide](./DEVELOPMENT.md) - Complete development environment setup
- [Contributing Guide](./CONTRIBUTING.md) - How to contribute to the project
- [Code Quality Documentation](./docs/quality-index.md) - Code quality tools and processes

### Quick Start

```bash
# Install dependencies
npm install
pip install -r requirements-dev.txt

# Run quality checks
npm run quality

# Start development
npm run dev
```

## 🏗️ Architecture

FreeAgentics follows a modular, microservices-inspired architecture:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Frontend  │────▶│   API Gateway   │────▶│  Agent Engine   │
│   (Next.js)     │     │   (Express)     │     │   (Python)      │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │                         │
                               ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   PostgreSQL    │     │  Message Queue  │
                        │   Database      │     │  (Redis)        │
                        └─────────────────┘     └─────────────────┘
```

### Key Components

- **Frontend**: React-based UI with real-time visualization
- **API Gateway**: RESTful API with WebSocket support
- **Agent Engine**: Core simulation engine implementing Active Inference
- **World System**: Hexagonal grid-based environment using H3
- **Knowledge Graph**: Distributed knowledge representation and sharing
- **Message System**: Asynchronous agent communication

## 🤖 Agent Types

FreeAgentics includes four specialized agent classes:

### 🔍 Explorer
- Discovers new territories and resources
- Maps the environment
- Shares discoveries with other agents
- Optimizes exploration paths

### 💰 Merchant
- Facilitates resource trading
- Maintains market equilibrium
- Builds trade networks
- Optimizes profit strategies

### 📚 Scholar
- Analyzes patterns and data
- Generates new knowledge
- Teaches other agents
- Advances collective intelligence

### 🛡️ Guardian
- Protects territories
- Maintains security
- Coordinates defense
- Responds to threats

## 🧠 Core Features

### Active Inference Engine
- Free energy minimization
- Predictive processing
- Belief updating
- Action selection

### Graph Neural Networks
- Dynamic model architecture
- Personality-based initialization
- Real-time adaptation
- Knowledge integration

### Emergent Behaviors
- Social network formation
- Economic systems
- Knowledge communities
- Collective problem-solving

### Deployment Options
- Local development
- Docker containers
- Kubernetes orchestration
- Edge deployment (Raspberry Pi, Jetson Nano)

## 📚 Documentation

### For Users
- [Getting Started Guide](doc/platform/getting_started.md)
- [Agent Creator Guide](doc/platform/agent_creator_guide.md)
- [Active Inference Tutorial](doc/active_inference_guide.md)

### For Developers
- [API Reference](doc/api/rest_api.md)
-
