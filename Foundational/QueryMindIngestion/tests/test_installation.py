"""
Test script to verify installation and dependencies.
"""
import sys
import importlib


def test_imports():
    """Test if all required packages can be imported."""
    required_packages = [
        'langchain',
        'langchain_community',
        'pymongo',
        'PyPDF2',
        'pydantic',
        'pydantic_settings',
        'ollama'
    ]
    
    print("Testing package imports...")
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError as e:
            print(f"✗ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\nFailed to import: {', '.join(failed_imports)}")
        print("Please install missing packages with: pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All packages imported successfully!")
        return True


def test_local_modules():
    """Test if local modules can be imported."""
    local_modules = [
        'config',
        'pdf_reader',
        'text_chunker',
        'mongodb_client',
        'embedding_generator',
        'pdf_ingestion_tool'
    ]
    
    print("\nTesting local module imports...")
    failed_imports = []
    
    for module in local_modules:
        try:
            importlib.import_module(module)
            print(f"✓ {module}")
        except ImportError as e:
            print(f"✗ {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFailed to import local modules: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✓ All local modules imported successfully!")
        return True


def test_configuration():
    """Test configuration loading."""
    print("\nTesting configuration...")
    try:
        from config import settings
        print(f"✓ PDF folder path: {settings.pdf_folder_path}")
        print(f"✓ MongoDB URI: {settings.mongodb_uri}")
        print(f"✓ MongoDB database: {settings.mongodb_database}")
        print(f"✓ MongoDB collection: {settings.mongodb_collection}")
        print(f"✓ Ollama base URL: {settings.ollama_base_url}")
        print(f"✓ Embedding model: {settings.embedding_model}")
        return True
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return False


def main():
    """Run all tests."""
    print("PDF Ingestion Tool - Installation Test")
    print("=" * 50)
    
    all_tests_passed = True
    
    # Test package imports
    if not test_imports():
        all_tests_passed = False
    
    # Test local modules
    if not test_local_modules():
        all_tests_passed = False
    
    # Test configuration
    if not test_configuration():
        all_tests_passed = False
    
    print("\n" + "=" * 50)
    if all_tests_passed:
        print("✓ All tests passed! Installation is successful.")
        print("\nNext steps:")
        print("1. Ensure MongoDB is running")
        print("2. Ensure Ollama is running with embeddinggemma model")
        print("3. Place PDF files in the pdfs/ folder")
        print("4. Run: python pdf_ingestion_tool.py")
    else:
        print("✗ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
