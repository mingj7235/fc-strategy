#!/bin/bash

# FC Strategy Coach - Backend Start Script

echo "🚀 Starting FC Strategy Coach Backend..."

cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your NEXON_API_KEY"
fi

# Run migrations
echo "📦 Running migrations..."
python manage.py migrate

# Start server
echo "✅ Starting Django development server..."
python manage.py runserver
