#!/bin/bash

# FC Strategy Coach - Frontend Start Script

echo "🚀 Starting FC Strategy Coach Frontend..."

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Copying from .env.example..."
    cp .env.example .env
fi

# Start dev server
echo "✅ Starting Vite development server..."
npm run dev
