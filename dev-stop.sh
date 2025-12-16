#!/bin/bash

# Skyvern Development Stop Script
# This script stops all Skyvern services

set -e

cd "$(dirname "$0")"

echo "🛑 Stopping Skyvern services..."

# Stop any running Skyvern processes
pkill -f "skyvern run server" || true
pkill -f "npm run dev" || true

# Stop Docker containers
if docker ps | grep -q skyvern; then
    echo "📦 Stopping Docker containers..."
    docker-compose down
fi

echo "✅ All Skyvern services stopped!"