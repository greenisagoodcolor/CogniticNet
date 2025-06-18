.PHONY: help dev test lint format quality clean install setup docker-up docker-down

# Default target
help:
	@echo "🧠 CogniticNet Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install    - Install all dependencies"
	@echo "  make setup      - Complete project setup"
	@echo ""
	@echo "Development:"
	@echo "  make dev        - Start development server"
	@echo "  make test       - Run tests"
	@echo "  make lint       - Check code style"
	@echo "  make format     - Auto-format code"
	@echo "  make quality    - Run all quality checks"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-up  - Start all services"
	@echo "  make docker-down - Stop all services"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean      - Clean build artifacts"
	@echo "  make cli        - Open interactive CLI"

# Installation
install:
	npm install
	cd src && pip install -r ../requirements.txt -r ../requirements-dev.txt

setup: install
	npx husky install
	cd src/database && python manage.py init

# Development
dev:
	npm run dev

test:
	npm test
	python -m pytest src/tests/

test-frontend:
	npm test

test-backend:
	python -m pytest src/tests/

test-watch:
	npm run test:watch

coverage:
	@echo "Generating code coverage reports..."
	npm run test:coverage
	coverage run -m pytest src/tests/
	coverage report
	coverage html
	coverage xml

coverage-view:
	@echo "Opening coverage reports..."
	@if [ -f coverage/lcov-report/index.html ]; then \
		open coverage/lcov-report/index.html; \
	fi
	@if [ -f coverage/html/index.html ]; then \
		open coverage/html/index.html; \
	fi

coverage-upload:
	@echo "Uploading coverage to Codecov..."
	npx codecov

coverage-interactive:
	@node scripts/coverage-report.js

coverage-full:
	@node scripts/coverage-report.js full

lint:
	npm run lint:strict

format:
	npm run all:format

quality:
	npm run quality:full

quality-all:
	npm run all:quality

# Docker
docker-up:
	cd environments/development && docker-compose up -d

docker-down:
	cd environments/development && docker-compose down

docker-logs:
	cd environments/development && docker-compose logs -f

# Python specific
python-lint:
	npm run python:lint

python-format:
	npm run python:format

python-test:
	npm run python:test

# Utilities
clean:
	npm run clean
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

deps-check:
	npm run check-deps

deps-update:
	npm run update-deps

size:
	npm run size

deadcode:
	npm run find-deadcode

# Interactive CLI
cli:
	npm run cogniticnet

# Build
build:
	npm run build

build-analyze:
	npm run analyze

# Git hooks
hooks-install:
	npx husky install

hooks-uninstall:
	rm -rf .husky
