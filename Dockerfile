# CogniticNet Multi-Stage Dockerfile
# This Dockerfile builds both frontend and backend services

# Base stage for shared dependencies
FROM node:18-alpine AS base
RUN apk add --no-cache python3 make g++
WORKDIR /app

# Frontend dependencies
FROM base AS frontend-deps
COPY package*.json ./
RUN npm ci --only=production

# Frontend builder
FROM base AS frontend-builder
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Backend base
FROM python:3.11-slim AS backend-base
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Backend dependencies
FROM backend-base AS backend-deps
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Development stage - includes all tools
FROM backend-base AS development
COPY backend/requirements.txt backend/requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

COPY . .
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=development

# Run both frontend and backend in dev mode
CMD ["sh", "-c", "cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload & npm run dev"]

# Production frontend
FROM node:18-alpine AS frontend-production
WORKDIR /app

# Copy built application
COPY --from=frontend-builder /app/.next ./.next
COPY --from=frontend-builder /app/public ./public
COPY --from=frontend-builder /app/package*.json ./
COPY --from=frontend-deps /app/node_modules ./node_modules

EXPOSE 3000
ENV NODE_ENV=production
CMD ["npm", "start"]

# Production backend
FROM backend-base AS backend-production
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser

# Copy dependencies
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin

# Copy application
COPY backend ./backend
COPY src ./src
COPY models ./models

# Set ownership
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

CMD ["gunicorn", "backend.app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]

# Default to production backend 