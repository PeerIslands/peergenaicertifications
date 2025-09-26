"""
Setup script for PDF Ingestion Tool.
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors."""
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
    """Check if Python version is compatible."""
    print("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ required, found {version.major}.{version.minor}")
        return False
    else:
        print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True


def install_dependencies():
    """Install Python dependencies."""
    print("\nInstalling Python dependencies...")
    return run_command("pip install -r requirements.txt", "Installing requirements")


def create_directories():
    """Create necessary directories."""
    print("\nCreating directories...")
    directories = ["pdfs", "logs"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(exist_ok=True)
            print(f"✓ Created directory: {directory}")
        else:
            print(f"✓ Directory already exists: {directory}")


def check_external_services():
    """Check if external services are available."""
    print("\nChecking external services...")
    
    # Check MongoDB
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb+srv://mongosh_aj:ajinkya123@cluster0.clx9fur.mongodb.net/", serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        print("✓ MongoDB Atlas connection successful")
        client.close()
    except Exception:
        print("✗ MongoDB Atlas connection failed")
        print("  Please check your MongoDB Atlas connection string and network access")
    
    # Check Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            
            # Check for embedding model
            models = response.json().get("models", [])
            embedding_models = [m for m in models if "embeddinggemma" in m.get("name", "")]
            if embedding_models:
                print(f"✓ Found embedding model: {embedding_models[0]['name']}")
            else:
                print("✗ embeddinggemma model not found")
                print("  Please install it: ollama pull embeddinggemma")
        else:
            print("✗ Ollama is not responding properly")
    except Exception:
        print("✗ Ollama is not running or not accessible")
        print("  Please start Ollama: ollama serve")
        print("  Then install model: ollama pull embeddinggemma")


def create_sample_config():
    """Create a sample configuration file."""
    print("\nCreating sample configuration...")
    
    config_content = """# PDF Ingestion Tool Configuration
# Update these values according to your setup

# PDF folder path (absolute or relative path)
PDF_FOLDER_PATH=./pdfs

# MongoDB configuration
MONGODB_URI=mongodb+srv://mongosh_aj:ajinkya123@cluster0.clx9fur.mongodb.net/
MONGODB_DATABASE=query-mind
MONGODB_COLLECTION=knowledge-base

# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=embeddinggemma

# Chunking configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
"""
    
    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(config_content)
        print("✓ Created .env configuration file")
    else:
        print("✓ .env file already exists")


def main():
    """Main setup function."""
    print("PDF Ingestion Tool - Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        print("Please upgrade Python to version 3.8 or higher")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("Failed to install dependencies")
        return 1
    
    # Create directories
    create_directories()
    
    # Create sample config
    create_sample_config()
    
    # Check external services
    check_external_services()
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Ensure MongoDB is running: mongod")
    print("2. Ensure Ollama is running: ollama serve")
    print("3. Install embedding model: ollama pull embeddinggemma")
    print("4. Place PDF files in the pdfs/ folder")
    print("5. Run: python test_installation.py")
    print("6. Run: python pdf_ingestion_tool.py")
    
    return 0


if __name__ == "__main__":
    exit(main())
