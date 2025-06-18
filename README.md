# CogniticNet Agent Simulator

<div align="center">

![CogniticNet Logo](public/placeholder-logo.svg)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE.md)
[![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.9-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/docker-%3E%3D20.10-blue.svg)](https://www.docker.com/)

**A sophisticated multi-agent simulation platform implementing Active Inference principles for emergent intelligence and collaborative behavior.**

[Demo](https://cogniticnet.demo) | [Documentation](doc/) | [Getting Started](doc/platform/getting_started.md) | [API Reference](doc/api/rest_api.md)

</div>

## 🌟 Overview

CogniticNet is an advanced agent-based modeling platform that combines Active Inference theory with graph neural networks to create intelligent, autonomous agents capable of:

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
git clone https://github.com/yourusername/cogniticnet.git
cd cogniticnet

# Install dependencies
npm install
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize the database
npm run db:init

# Start the development server
npm run dev
```

Visit `http://localhost:3000` to access the web interface.

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

CogniticNet follows a modular, microservices-inspired architecture:

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

CogniticNet includes four specialized agent classes:

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

### Project Structure
```
cogniticnet/
├── app/              # Next.js frontend
├── src/              # Python backend
│   ├── agents/       # Agent implementations
│   ├── world/        # Environment system
│   ├── knowledge/    # Knowledge management
│   └── simulation/   # Core engine
├── components/       # React components
├── tests/           # Test suites
└── docker/          # Docker configurations
```

### Running Tests
```bash
# Frontend tests
npm test

# Backend tests
pytest

# Integration tests
npm run test:integration

# Performance tests
npm run test:performance
```

### Code Quality
```bash
# Linting
npm run lint
python -m flake8 src/

# Type checking
npm run type-check
python -m mypy src/

# Format code
npm run format
python -m black src/
```

## 🚀 Deployment

### Production Deployment

1. **Configure environment**:
   ```bash
   cp .env.production.example .env.production
   # Edit with production settings
   ```

2. **Build assets**:
   ```bash
   npm run build
   python -m pip install -r requirements.prod.txt
   ```

3. **Deploy with Docker**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Edge Deployment

For deployment on edge devices:

```bash
# Optimize for Raspberry Pi
python scripts/optimize_edge.py --platform raspberry-pi

# Deploy to device
./scripts/deploy_edge.sh pi@raspberrypi.local
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Standards
- Follow TypeScript/Python style guides
- Write comprehensive tests
- Document new features
- Update relevant documentation

## 📊 Performance

CogniticNet is optimized for:
- **Scalability**: Handle 1000+ agents
- **Real-time**: Sub-100ms message latency
- **Efficiency**: Low memory footprint
- **Flexibility**: Runs on edge devices

## 🔒 Security

- API authentication via JWT tokens
- Encrypted agent communications
- Input validation and sanitization
- Regular security audits

## 📄 License

This project is licensed under the MIT License - see [LICENSE.md](LICENSE.md) for details.

## 🙏 Acknowledgments

- Active Inference community
- H3 geospatial indexing system
- Open source contributors

## 📞 Support

- **Documentation**: [docs.cogniticnet.io](https://docs.cogniticnet.io)
- **Issues**: [GitHub Issues](https://github.com/yourusername/cogniticnet/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cogniticnet/discussions)
- **Email**: support@cogniticnet.io

---

<div align="center">
Made with ❤️ by the CogniticNet Team
</div>
