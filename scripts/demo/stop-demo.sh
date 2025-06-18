#!/bin/bash
# Stop CogniticNet Demo Environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "🛑 Stopping CogniticNet Demo Environment"
echo "========================================"

# Navigate to project root
cd "$PROJECT_ROOT"

# Stop demo services
echo "📦 Stopping demo containers..."
docker-compose -f docker/demo/docker-compose.yml down

# Optional: Remove volumes (uncomment if needed)
# echo "🗑️  Removing demo volumes..."
# docker-compose -f docker/demo/docker-compose.yml down -v

echo ""
echo "✅ Demo Environment Stopped"
echo ""
echo "To restart the demo:"
echo "  ./scripts/demo/start-demo.sh"
echo "" 