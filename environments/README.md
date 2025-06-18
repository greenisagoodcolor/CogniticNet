# CogniticNet Environment Configuration

This directory contains environment-specific configurations for different deployment scenarios.

## Environment Files

Create the following files based on your deployment needs:

- `.env.development` - Local development settings
- `.env.testing` - Testing environment settings  
- `.env.staging` - Staging server settings
- `.env.production` - Production deployment settings

## Configuration Template

```bash
# Application
NODE_ENV=development
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Backend API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_RELOAD=true
API_LOG_LEVEL=debug

# Database
DATABASE_URL=postgresql://cogniticnet:password@localhost:5432/cogniticnet

# Redis
REDIS_URL=redis://localhost:6379/0

# LLM Configuration
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
PERPLEXITY_API_KEY=your_key_here

# Model Settings
DEFAULT_MODEL=claude-3-opus-20240229
FALLBACK_MODEL=gpt-4-turbo-preview
RESEARCH_MODEL=sonar-medium-online

# Security
ENCRYPTION_KEY=generate_secure_key
JWT_SECRET=generate_secure_secret
API_KEY_SALT=generate_secure_salt

# Features
ENABLE_HOT_RELOAD=true
ENABLE_DEBUG_TOOLS=true
ENABLE_API_DOCS=true

# Resource Limits
MAX_AGENTS_PER_SIMULATION=10
MAX_SIMULATION_STEPS=1000
MAX_KNOWLEDGE_GRAPH_NODES=10000
```

## Security Notes

- Never commit actual environment files to version control
- Use strong, unique values for all secrets
- Rotate keys regularly in production
- Use environment-specific databases 