#!/usr/bin/env python3
"""
Setup script for the PDF Document Ingestion System
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"  Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    return run_command("pip install -r requirements.txt", "Installing dependencies")

def check_mongodb():
    """Check if MongoDB is available"""
    print("Checking MongoDB availability...")
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("✓ MongoDB is running and accessible")
        return True
    except Exception as e:
        print(f"✗ MongoDB is not accessible: {e}")
        print("  Please install and start MongoDB:")
        print("  - macOS: brew install mongodb-community && brew services start mongodb-community")
        print("  - Ubuntu: sudo apt install mongodb && sudo systemctl start mongod")
        print("  - Windows: Download from https://www.mongodb.com/try/download/community")
        return False

def create_directories():
    """Create necessary directories"""
    print("Creating directories...")
    directories = ['PDF', 'logs', 'output']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    try:
        import pymongo
        import sentence_transformers
        import PyPDF2
        import numpy
        import tqdm
        print("✓ All required modules imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print("PDF Document Ingestion System - Setup")
    print("=" * 40)
    
    success = True
    
    # Check Python version
    if not check_python_version():
        success = False
    
    # Install dependencies
    if not install_dependencies():
        success = False
    
    # Test imports
    if not test_imports():
        success = False
    
    # Create directories
    create_directories()
    
    # Check MongoDB (optional, will warn if not available)
    check_mongodb()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ Setup completed successfully!")
        print("\nNext steps:")
        print("1. Add PDF files to the 'PDF' folder")
        print("2. Start MongoDB if not already running")
        print("3. Run: python main.py")
        print("4. Or run: python example_usage.py for examples")
    else:
        print("✗ Setup completed with errors")
        print("Please fix the errors above and run setup again")
        sys.exit(1)

if __name__ == "__main__":
    main()
