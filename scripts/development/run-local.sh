#!/bin/bash

# CogniticNet Development Environment - Local Development Server
# This script starts both backend and frontend servers with hot reload for development

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs/development"
BACKEND_LOG="$LOG_DIR/backend-dev.log"
FRONTEND_LOG="$LOG_DIR/frontend-dev.log"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Development configuration
BACKEND_PORT=8000
FRONTEND_PORT=3000
REDIS_PORT=6379
BACKEND_RELOAD=true
FRONTEND_RELOAD=true
PARALLEL_EXECUTION=true
OPEN_BROWSER=true
WATCH_MODE=true

# Process tracking
BACKEND_PID=""
FRONTEND_PID=""
REDIS_PID=""
CLEANUP_PERFORMED=false

# Initialize log directory
mkdir -p "$LOG_DIR"

# Logging function with prefixes
log() {
    local level="$1"
    local service="$2"
    shift 2
    local message="$*"
    local timestamp=$(date '+%H:%M:%S')

    # Service-specific color coding
    local service_color=""
    case "$service" in
        "BACKEND")
            service_color="$BLUE"
            ;;
        "FRONTEND")
            service_color="$CYAN"
            ;;
        "REDIS")
            service_color="$MAGENTA"
            ;;
        "SYSTEM")
            service_color="$GREEN"
            ;;
        *)
            service_color="$NC"
            ;;
    esac

    case "$level" in
        "INFO")
            echo -e "${service_color}[$timestamp]${NC} ${service_color}[$service]${NC} $message"
            ;;
        "WARN")
            echo -e "${service_color}[$timestamp]${NC} ${YELLOW}[$service WARN]${NC} $message"
            ;;
        "ERROR")
            echo -e "${service_color}[$timestamp]${NC} ${RED}[$service ERROR]${NC} $message"
            ;;
        "SUCCESS")
            echo -e "${service_color}[$timestamp]${NC} ${GREEN}[$service SUCCESS]${NC} $message"
            ;;
        "START")
            echo -e "${service_color}[$timestamp]${NC} ${BOLD}[$service STARTING]${NC} $message"
            ;;
        "STOP")
            echo -e "${service_color}[$timestamp]${NC} ${YELLOW}[$service STOPPING]${NC} $message"
            ;;
    esac
}

# Function to check if port is available
check_port() {
    local port="$1"
    local service="$2"

    if command -v lsof >/dev/null 2>&1 && lsof -i ":$port" >/dev/null 2>&1; then
        log "WARN" "SYSTEM" "Port $port is already in use (needed for $service)"
        return 1
    else
        log "SUCCESS" "SYSTEM" "Port $port is available for $service"
        return 0
    fi
}

# Function to start Redis for development
start_redis_dev() {
    log "START" "REDIS" "Starting Redis server for development..."

    # Check if Redis is already running
    if command -v redis-cli >/dev/null 2>&1 && redis-cli -p "$REDIS_PORT" ping >/dev/null 2>&1; then
        log "SUCCESS" "REDIS" "Redis server is already running on port $REDIS_PORT"
        return 0
    fi

    if ! command -v redis-server >/dev/null 2>&1; then
        log "WARN" "REDIS" "Redis server not found. Install Redis for full functionality."
        return 1
    fi

    # Start Redis server with development-friendly settings
    if redis-server --daemonize yes --port "$REDIS_PORT" --loglevel verbose >/dev/null 2>&1; then
        sleep 2
        if redis-cli -p "$REDIS_PORT" ping >/dev/null 2>&1; then
            log "SUCCESS" "REDIS" "Redis server started on port $REDIS_PORT"
            return 0
        else
            log "ERROR" "REDIS" "Redis server failed to start properly"
            return 1
        fi
    else
        log "ERROR" "REDIS" "Failed to start Redis server"
        return 1
    fi
}

# Function to start backend with hot reload
start_backend_dev() {
    log "START" "BACKEND" "Starting backend server with hot reload..."

    # Check port availability
    if ! check_port "$BACKEND_PORT" "backend"; then
        log "ERROR" "BACKEND" "Port $BACKEND_PORT is not available"
        return 1
    fi

    # Ensure we're in the project root and virtual environment is activated
    cd "$PROJECT_ROOT"

    # Check if virtual environment exists and activate it
    if [[ -f "$PROJECT_ROOT/venv/bin/activate" ]]; then
        source "$PROJECT_ROOT/venv/bin/activate"
        log "INFO" "BACKEND" "Activated Python virtual environment"
    elif [[ -f "$PROJECT_ROOT/venv/Scripts/activate" ]]; then
        source "$PROJECT_ROOT/venv/Scripts/activate"
        log "INFO" "BACKEND" "Activated Python virtual environment (Windows)"
    else
        log "WARN" "BACKEND" "Virtual environment not found, using system Python"
    fi

    # Determine backend startup command with hot reload
    local backend_cmd=""

    # Priority 1: uvicorn with reload (most common for FastAPI)
    if command -v uvicorn >/dev/null 2>&1; then
        # Look for main module
        if [[ -f "$PROJECT_ROOT/api/rest/main.py" ]]; then
            backend_cmd="uvicorn api.rest.main:app --host 0.0.0.0 --port $BACKEND_PORT --reload --reload-dir src --reload-dir api --reload-dir database --reload-dir inference --reload-dir agents"
        elif [[ -f "$PROJECT_ROOT/main.py" ]]; then
            backend_cmd="uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload --reload-dir src --reload-dir api"
        elif [[ -f "$PROJECT_ROOT/backend/main.py" ]]; then
            backend_cmd="cd backend && uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload"
        else
            backend_cmd="uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --reload"
        fi

    # Priority 2: Python with reload using watchdog
    elif [[ -f "$PROJECT_ROOT/main.py" ]]; then
        if command -v watchmedo >/dev/null 2>&1; then
            backend_cmd="watchmedo auto-restart --patterns='*.py' --recursive -- python main.py"
        else
            backend_cmd="python main.py"
            log "WARN" "BACKEND" "watchmedo not available, no auto-reload (install watchdog: pip install watchdog)"
        fi

    # Priority 3: Look for other entry points
    elif [[ -f "$PROJECT_ROOT/backend/app.py" ]]; then
        backend_cmd="cd backend && python app.py"
    elif [[ -f "$PROJECT_ROOT/app.py" ]]; then
        backend_cmd="python app.py"
    else
        log "ERROR" "BACKEND" "No backend entry point found"
        return 1
    fi

    log "INFO" "BACKEND" "Command: $backend_cmd"
    log "INFO" "BACKEND" "Hot reload: ${BACKEND_RELOAD}"
    log "INFO" "BACKEND" "Log file: $BACKEND_LOG"

    # Start backend in background
    eval "$backend_cmd" > "$BACKEND_LOG" 2>&1 &
    BACKEND_PID=$!

    # Wait for backend to start
    log "INFO" "BACKEND" "Waiting for backend to start..."
    local max_attempts=30
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s "http://localhost:$BACKEND_PORT/health" >/dev/null 2>&1 || \
           curl -s "http://localhost:$BACKEND_PORT/" >/dev/null 2>&1; then
            log "SUCCESS" "BACKEND" "Server started on http://localhost:$BACKEND_PORT (PID: $BACKEND_PID)"
            log "SUCCESS" "BACKEND" "API docs available at http://localhost:$BACKEND_PORT/docs"
            return 0
        fi

        sleep 2
        attempt=$((attempt + 1))

        # Check if process is still running
        if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            log "ERROR" "BACKEND" "Process died unexpectedly (check logs: tail -f $BACKEND_LOG)"
            return 1
        fi

        # Show progress
        if [[ $((attempt % 5)) -eq 0 ]]; then
            log "INFO" "BACKEND" "Still waiting... (attempt $attempt/$max_attempts)"
        fi
    done

    log "ERROR" "BACKEND" "Failed to start within timeout (check logs: tail -f $BACKEND_LOG)"
    return 1
}

# Function to start frontend with hot reload
start_frontend_dev() {
    log "START" "FRONTEND" "Starting frontend server with hot reload..."

    # Check port availability
    if ! check_port "$FRONTEND_PORT" "frontend"; then
        log "ERROR" "FRONTEND" "Port $FRONTEND_PORT is not available"
        return 1
    fi

    # Look for frontend directory and entry points
    local frontend_cmd=""
    local frontend_dir="$PROJECT_ROOT"

    # Check for frontend in subdirectories
    if [[ -d "$PROJECT_ROOT/web" && -f "$PROJECT_ROOT/web/package.json" ]]; then
        frontend_dir="$PROJECT_ROOT/web"
    elif [[ -d "$PROJECT_ROOT/frontend" && -f "$PROJECT_ROOT/frontend/package.json" ]]; then
        frontend_dir="$PROJECT_ROOT/frontend"
    elif [[ -f "$PROJECT_ROOT/package.json" ]]; then
        frontend_dir="$PROJECT_ROOT"
    else
        log "WARN" "FRONTEND" "No frontend configuration found - skipping frontend startup"
        return 0
    fi

    log "INFO" "FRONTEND" "Frontend directory: $frontend_dir"
    cd "$frontend_dir"

    # Check if node_modules exists
    if [[ ! -d "$frontend_dir/node_modules" ]]; then
        log "WARN" "FRONTEND" "Dependencies not installed, installing now..."
        if command -v yarn >/dev/null 2>&1; then
            log "INFO" "FRONTEND" "Installing with yarn..."
            yarn install
        elif command -v npm >/dev/null 2>&1; then
            log "INFO" "FRONTEND" "Installing with npm..."
            npm install
        else
            log "ERROR" "FRONTEND" "Neither npm nor yarn found"
            return 1
        fi
    fi

    # Determine frontend startup command
    if [[ -f "$frontend_dir/next.config.js" ]] || [[ -f "$frontend_dir/next.config.ts" ]]; then
        # Next.js
        frontend_cmd="npm run dev -- --port $FRONTEND_PORT"
        log "INFO" "FRONTEND" "Detected Next.js application"

    elif [[ -f "$frontend_dir/vite.config.js" ]] || [[ -f "$frontend_dir/vite.config.ts" ]]; then
        # Vite
        frontend_cmd="npm run dev -- --port $FRONTEND_PORT --host"
        log "INFO" "FRONTEND" "Detected Vite application"

    elif [[ -f "$frontend_dir/src/App.js" ]] || [[ -f "$frontend_dir/src/App.tsx" ]]; then
        # Create React App
        frontend_cmd="BROWSER=none PORT=$FRONTEND_PORT npm start"
        log "INFO" "FRONTEND" "Detected Create React App"

    elif [[ -f "$frontend_dir/package.json" ]]; then
        # Check package.json scripts
        if grep -q '"dev"' "$frontend_dir/package.json"; then
            frontend_cmd="npm run dev"
        elif grep -q '"start"' "$frontend_dir/package.json"; then
            frontend_cmd="npm start"
        else
            log "ERROR" "FRONTEND" "No recognized start script found in package.json"
            return 1
        fi
        log "INFO" "FRONTEND" "Using package.json script"
    else
        log "ERROR" "FRONTEND" "No frontend configuration found"
        return 1
    fi

    log "INFO" "FRONTEND" "Command: $frontend_cmd"
    log "INFO" "FRONTEND" "Hot reload: ${FRONTEND_RELOAD}"
    log "INFO" "FRONTEND" "Log file: $FRONTEND_LOG"

    # Start frontend in background
    eval "$frontend_cmd" > "$FRONTEND_LOG" 2>&1 &
    FRONTEND_PID=$!

    # Wait for frontend to start
    log "INFO" "FRONTEND" "Waiting for frontend to start..."
    local max_attempts=30
    local attempt=0

    while [[ $attempt -lt $max_attempts ]]; do
        if curl -s "http://localhost:$FRONTEND_PORT" >/dev/null 2>&1; then
            log "SUCCESS" "FRONTEND" "Server started on http://localhost:$FRONTEND_PORT (PID: $FRONTEND_PID)"
            return 0
        fi

        sleep 2
        attempt=$((attempt + 1))

        # Check if process is still running
        if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
            log "ERROR" "FRONTEND" "Process died unexpectedly (check logs: tail -f $FRONTEND_LOG)"
            return 1
        fi

        # Show progress
        if [[ $((attempt % 5)) -eq 0 ]]; then
            log "INFO" "FRONTEND" "Still waiting... (attempt $attempt/$max_attempts)"
        fi
    done

    log "ERROR" "FRONTEND" "Failed to start within timeout (check logs: tail -f $FRONTEND_LOG)"
    return 1
}

# Function to open browser
open_browser_dev() {
    if [[ "$OPEN_BROWSER" != "true" ]]; then
        return 0
    fi

    log "INFO" "SYSTEM" "Opening browser..."

    local url="http://localhost:$FRONTEND_PORT"

    # Wait a bit for frontend to be fully ready
    sleep 3

    if command -v open >/dev/null 2>&1; then
        # macOS
        open "$url" >/dev/null 2>&1 &
    elif command -v xdg-open >/dev/null 2>&1; then
        # Linux
        xdg-open "$url" >/dev/null 2>&1 &
    elif command -v start >/dev/null 2>&1; then
        # Windows
        start "$url" >/dev/null 2>&1 &
    else
        log "INFO" "SYSTEM" "Could not auto-open browser. Please visit: $url"
        return 0
    fi

    log "SUCCESS" "SYSTEM" "Browser opened to $url"
}

# Function to display development status
display_dev_status() {
    echo ""
    echo "========================================"
    echo "    CogniticNet Development Server"
    echo "========================================"
    echo ""

    log "SUCCESS" "SYSTEM" "Development environment is running!"
    echo ""

    log "INFO" "SYSTEM" "Service URLs:"
    if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        log "INFO" "SYSTEM" "  Frontend:  http://localhost:$FRONTEND_PORT"
    fi
    if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        log "INFO" "SYSTEM" "  Backend:   http://localhost:$BACKEND_PORT"
        log "INFO" "SYSTEM" "  API Docs:  http://localhost:$BACKEND_PORT/docs"
    fi
    echo ""

    log "INFO" "SYSTEM" "Service Status:"
    if redis-cli -p "$REDIS_PORT" ping >/dev/null 2>&1; then
        log "SUCCESS" "SYSTEM" "  ✓ Redis server running"
    else
        log "WARN" "SYSTEM" "  ✗ Redis server not running"
    fi

    if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        log "SUCCESS" "SYSTEM" "  ✓ Backend server running (PID: $BACKEND_PID) with hot reload"
    else
        log "ERROR" "SYSTEM" "  ✗ Backend server not running"
    fi

    if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        log "SUCCESS" "SYSTEM" "  ✓ Frontend server running (PID: $FRONTEND_PID) with hot reload"
    else
        log "WARN" "SYSTEM" "  ✗ Frontend server not running"
    fi

    echo ""
    log "INFO" "SYSTEM" "Development Features:"
    log "INFO" "SYSTEM" "  Hot Reload: Backend ✓  Frontend ✓"
    log "INFO" "SYSTEM" "  File Watching: Active"
    log "INFO" "SYSTEM" "  Auto Restart: Enabled"
    echo ""

    log "INFO" "SYSTEM" "Development Actions:"
    log "INFO" "SYSTEM" "  View backend logs:  tail -f $BACKEND_LOG"
    log "INFO" "SYSTEM" "  View frontend logs: tail -f $FRONTEND_LOG"
    log "INFO" "SYSTEM" "  Stop development:   Press Ctrl+C"
    echo ""

    log "INFO" "SYSTEM" "Development Tips:"
    log "INFO" "SYSTEM" "  - Backend changes will auto-restart the server"
    log "INFO" "SYSTEM" "  - Frontend changes will auto-refresh the browser"
    log "INFO" "SYSTEM" "  - Check logs if hot reload stops working"
    echo ""
}

# Function to cleanup processes
cleanup() {
    if [[ "$CLEANUP_PERFORMED" == "true" ]]; then
        return
    fi

    CLEANUP_PERFORMED=true

    log "STOP" "SYSTEM" "Stopping development environment..."

    # Stop frontend
    if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        log "STOP" "FRONTEND" "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill "$FRONTEND_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$FRONTEND_PID" 2>/dev/null || true
    fi

    # Stop backend
    if [[ -n "$BACKEND_PID" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        log "STOP" "BACKEND" "Stopping backend server (PID: $BACKEND_PID)..."
        kill "$BACKEND_PID" 2>/dev/null || true
        sleep 2
        kill -9 "$BACKEND_PID" 2>/dev/null || true
    fi

    # Note: We don't stop Redis as it might be used by other processes

    log "SUCCESS" "SYSTEM" "Development environment stopped"
    echo ""
}

# Function to wait for user interruption with process monitoring
wait_for_interruption() {
    log "INFO" "SYSTEM" "Development server is running. Press Ctrl+C to stop."
    echo ""

    # Wait for SIGINT (Ctrl+C) or SIGTERM
    trap 'cleanup; exit 0' SIGINT SIGTERM

    # Monitor processes and provide status updates
    while true; do
        # Check if critical processes are still running
        if [[ -n "$BACKEND_PID" ]] && ! kill -0 "$BACKEND_PID" 2>/dev/null; then
            log "ERROR" "BACKEND" "Process died unexpectedly - check logs: tail -f $BACKEND_LOG"
            break
        fi

        if [[ -n "$FRONTEND_PID" ]] && ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
            log "WARN" "FRONTEND" "Process died unexpectedly - check logs: tail -f $FRONTEND_LOG"
        fi

        sleep 10
    done
}

# Function to start development environment based on configuration
start_development_environment() {
    # Start Redis (optional for development)
    if ! start_redis_dev; then
        log "WARN" "SYSTEM" "Redis failed to start - some features may not work"
    fi

    # Start backend
    if ! start_backend_dev; then
        log "ERROR" "SYSTEM" "Failed to start backend server"
        cleanup
        exit 1
    fi

    # Start frontend
    if ! start_frontend_dev; then
        log "WARN" "SYSTEM" "Failed to start frontend server - backend will still be available"
    fi

    # Open browser (if frontend is running)
    if [[ -n "$FRONTEND_PID" ]] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        open_browser_dev
    fi
}

# Function to display help
show_help() {
    echo "CogniticNet Development Environment Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  --help, -h              Show this help message"
    echo "  --version, -v           Show version information"
    echo "  --backend-only          Start only the backend server"
    echo "  --frontend-only         Start only the frontend server"
    echo "  --no-browser            Don't open browser automatically"
    echo "  --no-reload             Disable hot reload (not recommended for development)"
    echo "  --backend-port <port>   Backend port (default: $BACKEND_PORT)"
    echo "  --frontend-port <port>  Frontend port (default: $FRONTEND_PORT)"
    echo "  --verbose               Enable verbose logging"
    echo ""
    echo "This script starts the CogniticNet development environment with:"
    echo "  - Backend server with hot reload (uvicorn --reload)"
    echo "  - Frontend dev server with hot module replacement"
    echo "  - Redis server (optional)"
    echo "  - Automatic browser opening"
    echo "  - File watching and auto-restart"
    echo ""
    echo "Hot reload features:"
    echo "  - Backend: Watches Python files and auto-restarts server"
    echo "  - Frontend: Watches source files and auto-refreshes browser"
    echo ""
    echo "The development server will run until you press Ctrl+C."
    echo ""
}

# Handle script arguments
BACKEND_ONLY=false
FRONTEND_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        "--help"|"-h")
            show_help
            exit 0
            ;;
        "--version"|"-v")
            echo "CogniticNet Development Environment v1.0.0"
            exit 0
            ;;
        "--backend-only")
            BACKEND_ONLY=true
            FRONTEND_RELOAD=false
            log "INFO" "SYSTEM" "Backend-only mode enabled"
            shift
            ;;
        "--frontend-only")
            FRONTEND_ONLY=true
            BACKEND_RELOAD=false
            log "INFO" "SYSTEM" "Frontend-only mode enabled"
            shift
            ;;
        "--no-browser")
            OPEN_BROWSER=false
            log "INFO" "SYSTEM" "Automatic browser opening disabled"
            shift
            ;;
        "--no-reload")
            BACKEND_RELOAD=false
            FRONTEND_RELOAD=false
            log "INFO" "SYSTEM" "Hot reload disabled"
            shift
            ;;
        "--backend-port")
            BACKEND_PORT="$2"
            log "INFO" "SYSTEM" "Backend port set to: $BACKEND_PORT"
            shift 2
            ;;
        "--frontend-port")
            FRONTEND_PORT="$2"
            log "INFO" "SYSTEM" "Frontend port set to: $FRONTEND_PORT"
            shift 2
            ;;
        "--verbose")
            set -x
            log "INFO" "SYSTEM" "Verbose logging enabled"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo ""
    echo "========================================"
    echo "  CogniticNet Development Environment"
    echo "========================================"
    echo ""

    log "INFO" "SYSTEM" "Starting development environment..."
    log "INFO" "SYSTEM" "Project root: $PROJECT_ROOT"
    log "INFO" "SYSTEM" "Log directory: $LOG_DIR"
    echo ""

    # Start services based on configuration
    if [[ "$BACKEND_ONLY" == "true" ]]; then
        start_redis_dev || log "WARN" "SYSTEM" "Redis failed to start"
        start_backend_dev || { log "ERROR" "SYSTEM" "Failed to start backend"; cleanup; exit 1; }
    elif [[ "$FRONTEND_ONLY" == "true" ]]; then
        start_frontend_dev || { log "ERROR" "SYSTEM" "Failed to start frontend"; cleanup; exit 1; }
        open_browser_dev
    else
        start_development_environment
    fi

    # Display status
    display_dev_status

    # Wait for user to stop
    wait_for_interruption

    # Cleanup
    cleanup
}

# Run main function
main
