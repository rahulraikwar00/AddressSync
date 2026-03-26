#!/bin/bash
# start.sh - Start the entire application

echo "🚀 Starting Address Sync Application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Detect which compose command to use
if command -v docker compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
elif docker compose version &> /dev/null 2>&1; then
    COMPOSE_CMD="docker compose"
else
    echo "❌ Docker Compose is not installed."
    echo "Install with: sudo apt-get install docker-compose-plugin"
    exit 1
fi

echo "📦 Using: $COMPOSE_CMD"

# Build and start containers
echo "📦 Building and starting containers..."
$COMPOSE_CMD up -d --build

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is running at http://localhost:8000"
        echo "📖 API Docs at http://localhost:8000/docs"
        break
    fi
    sleep 2
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "   Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  Backend might still be starting. Check logs with: $COMPOSE_CMD logs"
fi

echo ""
echo "📋 Useful commands:"
echo "  View logs: $COMPOSE_CMD logs -f"
echo "  Stop: $COMPOSE_CMD down"
echo "  Restart: $COMPOSE_CMD restart"
echo "  Clean everything: ./clean.sh"