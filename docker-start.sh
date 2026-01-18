#!/bin/bash

# Docker Start Script
# One-command startup for hackathon backend

set -e

echo "🐳 Starting Hackathon Backend with Docker..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Creating template .env file..."
    cat > .env << EOF
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=hackathon_db

# JWT Configuration (CHANGE THESE IN PRODUCTION)
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App Environment
APP_ENV=production
EOF
    echo "✅ Created .env file with random SECRET_KEY"
    echo "⚠️  Please review and update .env file as needed"
fi

# Build and start using docker-compose
echo "📦 Building Docker image..."
docker-compose build

echo "🚀 Starting container..."
docker-compose up -d

echo "⏳ Waiting for health check..."
sleep 5

# Check health
echo "🏥 Checking health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy!"
    echo ""
    echo "🌐 Backend is running at: http://localhost:8000"
    echo "📚 API docs: http://localhost:8000/docs"
    echo "💚 Health check: http://localhost:8000/health"
    echo ""
    echo "📋 Useful commands:"
    echo "  View logs:    docker-compose logs -f"
    echo "  Stop:         docker-compose down"
    echo "  Restart:      docker-compose restart"
else
    echo "⚠️  Health check failed. Checking logs..."
    docker-compose logs --tail=50
    echo ""
    echo "Please check the logs above for errors"
fi
