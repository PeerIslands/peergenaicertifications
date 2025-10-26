#!/bin/bash

# RAG Chat App - Complete Setup Script

echo "🚀 Setting up RAG Chat App..."

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Check MongoDB
if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB not found. Please install MongoDB or use MongoDB Atlas"
fi

# Check Ollama
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found. Please install Ollama and pull LLaMA 3 model"
    echo "   Install: curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   Model: ollama pull llama3"
fi

echo "✅ Prerequisites check complete"

# Setup backend
echo "📦 Setting up backend..."
cd backend-rag-chat
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    echo "📝 Created .env file. Please edit it with your configuration."
fi

# Setup frontend
echo "📦 Setting up frontend..."
cd ../frontend-rag-chat
npm install

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your MongoDB URI and other settings"
echo "2. Start MongoDB: mongod"
echo "3. Start Ollama: ollama serve"
echo "4. Pull LLaMA 3: ollama pull llama3"
echo "5. Start backend: ./run_backend.sh"
echo "6. Start frontend: ./run_frontend.sh"
echo ""
echo "Access the app at: http://localhost:3000"
