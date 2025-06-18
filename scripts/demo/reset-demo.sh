#!/bin/bash
# Reset CogniticNet Demo Environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "🔄 Resetting CogniticNet Demo Environment"
echo "========================================"
echo ""
echo "⚠️  WARNING: This will delete all demo data!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

# Navigate to project root
cd "$PROJECT_ROOT"

# Stop and remove everything
echo "🛑 Stopping demo services..."
docker-compose -f docker/demo/docker-compose.yml down -v

# Remove demo images to force rebuild
echo "🗑️  Removing demo images..."
docker rmi $(docker images -q "*cogniticnet-demo*") 2>/dev/null || true

# Clean up directories
echo "🧹 Cleaning up demo directories..."
rm -rf docker/demo/demo-assets/*
rm -rf scripts/demo/monitor/node_modules

echo ""
echo "✅ Demo Environment Reset Complete"
echo ""
echo "To start fresh:"
echo "  ./scripts/demo/start-demo.sh"
echo "" 