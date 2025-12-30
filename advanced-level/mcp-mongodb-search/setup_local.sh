#!/bin/bash

# Local Setup Script for MCP MongoDB Search Solution

echo "=========================================="
echo "MCP MongoDB Search - Local Setup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Check if MongoDB is running (optional check)
if command -v mongod &> /dev/null; then
    echo "✓ MongoDB found"
    # Try to check if MongoDB is running
    if pgrep -x "mongod" > /dev/null; then
        echo "✓ MongoDB is running"
    else
        echo "⚠ MongoDB is installed but not running"
        echo "  Start MongoDB with: brew services start mongodb-community (macOS)"
        echo "  Or: sudo systemctl start mongod (Linux)"
        echo "  Or: mongod (direct start)"
    fi
else
    echo "⚠ MongoDB not found in PATH"
    echo "  Install MongoDB: https://www.mongodb.com/try/download/community"
fi
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# MongoDB Configuration for Local Development
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=PeerGenAI_practice_db

# Logging Configuration
LOG_LEVEL=INFO

# Query Configuration
DEFAULT_QUERY_LIMIT=10
EOF
    echo "✓ .env file created with default local settings"
else
    echo "✓ .env file already exists"
fi
echo ""

echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Make sure MongoDB is running locally"
echo "2. Activate virtual environment: source venv/bin/activate"
echo "3. Run the application: python app.py"
echo "4. Or run examples: python example_usage.py"
echo ""
echo "To test MongoDB connection, run: python test_connection.py"
echo ""

