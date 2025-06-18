# Docker Deployment Guide

This guide covers running CogniticNet using Docker across different environments: development, testing, staging, and production.

## Overview

CogniticNet provides Docker configurations for:
- **Development**: Hot reload, debugging tools, local databases
- **Testing**: Isolated, reproducible test environments
- **Staging**: Production-like with test data
- **Production**: Optimized, scaled, secure

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

## Quick Start

### Development Environment

```bash
# Clone repository
git clone https://github.com/ActiveInferenceInstitute/CogniticNet.git
cd CogniticNet

# Copy environment template
cp environments/README.md .env

# Edit .env with your API keys
# Then start development environment
docker-compose -f docker/development/docker-compose.yml up
```

Access:
- Web UI: http://localhost:3000
- API: http://localhost:8000
- Database Admin: http://localhost:8080

## Environment Configurations

### Development Environment

**File**: `docker/development/docker-compose.yml`

Features:
- Hot code reload
- Volume mounts for live editing
- Debug ports exposed
- Development databases
- Admin tools included

```yaml
services:
  frontend:
    build:
      context: ../..
      dockerfile: docker/development/Dockerfile.frontend
    volumes:
      - ../../app:/app/app
      - ../../components:/app/components
    environment:
      - NODE_ENV=development
    ports:
      - "3000:3000"

  backend:
    build:
      context: ../..
      dockerfile: docker/development/Dockerfile.backend
    volumes:
      - ../../src:/app/src
    environment:
      - API_RELOAD=true
    ports:
      - "8000:8000"
```

### Testing Environment

**File**: `docker/testing/docker-compose.yml`

Features:
- Isolated test databases
- No external dependencies
- Deterministic behavior
- Test data fixtures
- Coverage reporting

```bash
# Run tests
docker-compose -f docker/testing/docker-compose.yml up --abort-on-container-exit

# Run specific test suite
docker-compose -f docker/testing/docker-compose.yml run backend pytest tests/unit
```

### Staging Environment

**File**: `docker/staging/docker-compose.yml`

Features:
- Production builds
- Separate databases
- SSL/TLS enabled
- Monitoring enabled
- Performance testing

```bash
# Deploy to staging
docker-compose -f docker/staging/docker-compose.yml up -d

# View logs
docker-compose -f docker/staging/docker-compose.yml logs -f
```

### Production Environment

**File**: `docker/production/docker-compose.yml`

Features:
- Optimized builds
- Security hardening
- Auto-scaling ready
- Backup systems
- Monitoring & alerts

```bash
# Deploy to production
docker-compose -f docker/production/docker-compose.yml up -d

# Scale services
docker-compose -f docker/production/docker-compose.yml scale backend=3
```

## Dockerfiles

### Frontend Dockerfile

```dockerfile
# docker/development/Dockerfile.frontend
FROM node:18-alpine AS development

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Development server
CMD ["npm", "run", "dev"]

# Production build
FROM node:18-alpine AS production

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

### Backend Dockerfile

```dockerfile
# docker/development/Dockerfile.backend
FROM python:3.11-slim AS development

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Development server
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Production build
FROM python:3.11-slim AS production

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

## Service Architecture

### Core Services

1. **Frontend (Next.js)**
   - Port: 3000
   - Handles UI/UX
   - Server-side rendering
   - WebSocket client

2. **Backend (FastAPI)**
   - Port: 8000
   - REST API
   - WebSocket server
   - Business logic

3. **MCP Server**
   - Port: 8001
   - Model Context Protocol
   - AI assistant integration
   - Task automation

4. **PostgreSQL**
   - Port: 5432
   - Primary data store
   - Agent states
   - Simulation history

5. **Redis**
   - Port: 6379
   - Caching layer
   - Session storage
   - Message queue

### Support Services

6. **Nginx (Production)**
   - Port: 80/443
   - Reverse proxy
   - SSL termination
   - Load balancing

7. **Adminer (Development)**
   - Port: 8080
   - Database management
   - Query interface

## Environment Variables

### Required Variables

```bash
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...

# Database
DATABASE_URL=postgresql://user:pass@postgres:5432/cogniticnet

# Security
JWT_SECRET=generate-secure-secret
ENCRYPTION_KEY=generate-secure-key

# Redis
REDIS_URL=redis://redis:6379/0
```

### Environment-Specific

Development:
```bash
NODE_ENV=development
API_RELOAD=true
ENABLE_DEBUG_TOOLS=true
```

Production:
```bash
NODE_ENV=production
API_WORKERS=4
ENABLE_TELEMETRY=true
```

## Networking

### Development Network
- All services on `cogniticnet_dev` network
- Ports exposed to host
- No SSL required

### Production Network
- Frontend/Backend on `public` network
- Database/Redis on `private` network
- SSL/TLS required
- Firewall rules applied

## Volumes

### Persistent Data
```yaml
volumes:
  postgres_data:    # Database files
  redis_data:       # Cache persistence
  model_storage:    # GNN models
  simulation_data:  # Results/logs
```

### Development Mounts
```yaml
volumes:
  - ./src:/app/src  # Hot reload
  - ./models:/app/models
```

## Commands

### Building Images

```bash
# Build all services
docker-compose -f docker/[env]/docker-compose.yml build

# Build specific service
docker-compose -f docker/[env]/docker-compose.yml build frontend

# Build with no cache
docker-compose -f docker/[env]/docker-compose.yml build --no-cache
```

### Managing Containers

```bash
# Start services
docker-compose -f docker/[env]/docker-compose.yml up -d

# Stop services
docker-compose -f docker/[env]/docker-compose.yml down

# Restart service
docker-compose -f docker/[env]/docker-compose.yml restart backend

# View logs
docker-compose -f docker/[env]/docker-compose.yml logs -f [service]
```

### Database Operations

```bash
# Run migrations
docker-compose -f docker/[env]/docker-compose.yml exec backend alembic upgrade head

# Create backup
docker-compose -f docker/[env]/docker-compose.yml exec postgres pg_dump -U cogniticnet > backup.sql

# Restore backup
docker-compose -f docker/[env]/docker-compose.yml exec -T postgres psql -U cogniticnet < backup.sql
```

### Debugging

```bash
# Enter container shell
docker-compose -f docker/[env]/docker-compose.yml exec backend bash

# View running processes
docker-compose -f docker/[env]/docker-compose.yml ps

# Check resource usage
docker stats

# Inspect network
docker network inspect cogniticnet_default
```

## Performance Tuning

### Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Scaling

```bash
# Scale backend instances
docker-compose -f docker/production/docker-compose.yml scale backend=3

# Scale with limits
docker-compose -f docker/production/docker-compose.yml up -d --scale backend=3
```

## Security

### Production Hardening

1. **Use specific image versions**
   ```dockerfile
   FROM python:3.11.7-slim
   ```

2. **Run as non-root user**
   ```dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

3. **Minimize attack surface**
   ```dockerfile
   RUN apt-get purge -y --auto-remove gcc g++
   ```

4. **Use secrets management**
   ```yaml
   secrets:
     db_password:
       external: true
   ```

### Network Security

```yaml
networks:
  public:
    driver: bridge
  private:
    driver: bridge
    internal: true
```

## Monitoring

### Health Checks

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Logging

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Find process using port
   lsof -i :3000
   
   # Change port in docker-compose.yml
   ports:
     - "3001:3000"
   ```

2. **Permission errors**
   ```bash
   # Fix volume permissions
   docker-compose exec backend chown -R appuser:appuser /app
   ```

3. **Out of memory**
   ```bash
   # Increase Docker memory
   # Docker Desktop: Preferences > Resources
   # Linux: Update /etc/docker/daemon.json
   ```

4. **Slow builds**
   ```bash
   # Use BuildKit
   export DOCKER_BUILDKIT=1
   docker-compose build
   ```

### Debug Mode

Enable debug logging:
```yaml
environment:
  - LOG_LEVEL=debug
  - DEBUG=true
```

## Best Practices

1. **Use .dockerignore**
   ```
   node_modules
   .next
   .pytest_cache
   __pycache__
   .env
   ```

2. **Layer caching**
   - Copy dependency files first
   - Install dependencies
   - Then copy source code

3. **Multi-stage builds**
   - Development stage with tools
   - Production stage optimized

4. **Environment parity**
   - Keep environments similar
   - Use same base images
   - Test in staging first

5. **Regular updates**
   ```bash
   # Update base images
   docker-compose pull
   
   # Rebuild with updates
   docker-compose build --pull
   ```

## CI/CD Integration

### GitHub Actions

```yaml
- name: Build and test
  run: |
    docker-compose -f docker/testing/docker-compose.yml build
    docker-compose -f docker/testing/docker-compose.yml run tests
```

### Deployment

```bash
# Tag for release
docker tag cogniticnet_backend:latest registry.example.com/cogniticnet/backend:v1.0.0

# Push to registry
docker push registry.example.com/cogniticnet/backend:v1.0.0
```

---

*For more details, see the [deployment guide](doc/platform/deployment_guide.md)* 