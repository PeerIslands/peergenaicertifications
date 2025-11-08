#!/bin/bash

echo "🚀 Starting RAG Document Chat Application"
echo "========================================"

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY is not set"
    echo "Please set your OpenAI API key:"
    echo "export OPENAI_API_KEY='your-api-key-here'"
    echo ""
    echo "You can still upload documents, but chat functionality will be limited."
    echo ""
fi

# Check if MongoDB is running (basic check)
if ! nc -z localhost 27017 2>/dev/null; then
    echo "⚠️  Warning: MongoDB doesn't seem to be running on localhost:27017"
    echo "Please start MongoDB or set MONGODB_URI to your MongoDB connection string"
    echo ""
    echo "To start MongoDB locally:"
    echo "mongod --dbpath /path/to/your/db"
    echo ""
fi

echo "🌐 Starting Streamlit application..."
echo "The app will open in your browser automatically."
echo "If it doesn't, navigate to: http://localhost:8501"
echo ""

# Start the Streamlit app
streamlit run main.py
