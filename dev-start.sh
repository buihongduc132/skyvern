#!/bin/bash

# Skyvern Development Start Script
# This script starts Skyvern services for development

set -e

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Create necessary directories
mkdir -p artifacts videos har log

case "${1:-all}" in
    "server")
        echo "🚀 Starting Skyvern API Server..."
        .venv/bin/skyvern run server
        ;;
    "ui")
        echo "🎨 Starting Skyvern UI..."
        cd skyvern-frontend
        npm run dev
        ;;
    "all")
        echo "🚀 Starting Skyvern API Server and UI..."
        # Start server in background
        .venv/bin/skyvern run server &
        SERVER_PID=$!
        
        # Wait a moment for server to start
        sleep 5
        
        # Start UI in background
        cd skyvern-frontend
        npm run dev &
        UI_PID=$!
        
        echo "✅ Services started!"
        echo "🌐 API Server: http://localhost:28743"
        echo "🎨 UI: http://localhost:28742"
        echo "📚 API Docs: http://localhost:28743/docs"
        echo ""
        echo "Press Ctrl+C to stop all services"
        
        # Wait for interrupt
        trap "echo 'Stopping services...'; kill $SERVER_PID $UI_PID; exit" INT
        wait
        ;;
    *)
        echo "Usage: $0 [server|ui|all]"
        echo "  server - Start API server only"
        echo "  ui     - Start UI only"
        echo "  all    - Start both API server and UI (default)"
        exit 1
        ;;
esac
