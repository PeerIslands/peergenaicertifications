#!/bin/bash

# RAG Chat App - Frontend Startup Script

echo "🚀 Starting RAG Chat Frontend..."

# Change to frontend directory
cd frontend-rag-chat

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the frontend
echo "🌟 Starting React development server..."
npm start
