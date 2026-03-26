#!/bin/bash
# clean.sh - Clean up containers, volumes, and database

echo "🧹 Cleaning up..."

# Stop and remove containers
docker compose down -v 2>/dev/null || docker compose down -v

# Remove database files
rm -f backend/data/*.db
rm -f backend/*.db

# Remove Python cache files
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove logs
rm -f backend/*.log

echo "✅ Cleanup complete"
echo ""
echo "💡 To rebuild, run: ./start.sh"