#!/bin/bash

# RAG Chat App - Backend Startup Script

echo "🚀 Starting RAG Chat Backend..."

# Change to backend directory
cd backend-rag-chat

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Start the backend
echo "🌟 Starting FastAPI server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8000
