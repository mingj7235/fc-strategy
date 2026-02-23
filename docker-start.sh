#!/bin/bash

# FC Strategy Coach - Docker Compose Start Script

echo "🚀 Starting FC Strategy Coach with Docker Compose..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Build and start all services
echo "📦 Building Docker images..."
docker-compose build

echo "🎯 Starting all services..."
docker-compose up

# To run in background, use: docker-compose up -d
