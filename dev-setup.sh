#!/bin/bash

# Skyvern Development Setup Script
# This script sets up and starts Skyvern for development

set -e

echo "🚀 Starting Skyvern Development Setup..."

# Navigate to skyvern directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start PostgreSQL if not running
if ! docker ps | grep -q skyvern-postgres-1; then
    echo "📦 Starting PostgreSQL database..."
    docker-compose up -d postgres
    
    # Wait for database to be healthy
    echo "⏳ Waiting for database to be ready..."
    while ! docker ps | grep -q "skyvern-postgres-1.*healthy"; do
        sleep 2
    done
    echo "✅ Database is ready!"
else
    echo "✅ PostgreSQL is already running"
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies if needed
if ! pip show skyvern > /dev/null 2>&1; then
    echo "📦 Installing Skyvern dependencies..."
    pip install -e .
fi

# Create necessary directories
mkdir -p artifacts videos har log

echo "🎯 Skyvern development environment is ready!"
echo ""
echo "📋 Available commands:"
echo "  ./dev-start server    - Start API server only"
echo "  ./dev-start ui        - Start UI only" 
echo "  ./dev-start all       - Start both API server and UI"
echo "  ./dev-stop           - Stop all services"
echo ""
echo "🌐 Access URLs:"
echo "  API Server: http://localhost:28743"
echo "  UI: http://localhost:28742"
echo "  API Docs: http://localhost:28743/docs"
