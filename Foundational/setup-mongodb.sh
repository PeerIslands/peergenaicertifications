#!/bin/bash

# MongoDB Vector Store Setup Script
echo "🚀 Setting up MongoDB Vector Store for PDF RAG..."

# Install dependencies
echo "📦 Installing MongoDB dependencies..."
npm install mongodb @types/mongodb @langchain/mongodb

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pdf_rag

# Server Configuration
PORT=8080
NODE_ENV=development

# Optional: OpenRouter API Key (fallback for OpenAI)
OPENROUTER_API_KEY=your_openrouter_api_key_here
EOF
    echo "✅ Created .env file. Please update with your actual API keys and MongoDB URI."
else
    echo "✅ .env file already exists."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with your MongoDB URI and OpenAI API key"
echo "2. Start MongoDB (if using local installation)"
echo "3. Run: npm run dev"
echo ""
echo "For detailed setup instructions, see MONGODB_SETUP.md"
