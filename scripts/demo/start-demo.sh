#!/bin/bash
# Start CogniticNet Demo Environment

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/../.." && pwd )"

echo "🚀 Starting CogniticNet Demo Environment"
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Navigate to project root
cd "$PROJECT_ROOT"

# Create necessary directories
echo "📁 Creating demo directories..."
mkdir -p docker/demo/demo-assets
mkdir -p scripts/demo/scenarios
mkdir -p scripts/demo/monitor

# Build and start demo environment
echo "🏗️  Building demo containers..."
docker-compose -f docker/demo/docker-compose.yml build

echo "🚀 Starting demo services..."
docker-compose -f docker/demo/docker-compose.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to initialize..."
sleep 10

# Check service health
echo "🔍 Checking service status..."
docker-compose -f docker/demo/docker-compose.yml ps

# Display access information
echo ""
echo "✅ Demo Environment Started Successfully!"
echo "========================================"
echo ""
echo "🌐 Access Points:"
echo "  - Main Demo App:     http://localhost:8080"
echo "  - Direct App Access: http://localhost:3030"
echo "  - Monitor Dashboard: http://localhost:3031"
echo "  - Demo Database:     localhost:5433"
echo "  - Demo Redis:        localhost:6380"
echo ""
echo "📊 Demo Features:"
echo "  - Pre-populated with 4 demo agents"
echo "  - 5 automated scenarios running"
echo "  - 10x accelerated simulation speed"
echo "  - Real-time updates via WebSocket"
echo ""
echo "🛑 To stop the demo:"
echo "  ./scripts/demo/stop-demo.sh"
echo ""
echo "📋 To view logs:"
echo "  docker-compose -f docker/demo/docker-compose.yml logs -f [service-name]"
echo ""
echo "Enjoy the demo! 🎉" 