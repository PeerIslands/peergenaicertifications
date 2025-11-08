#!/usr/bin/env python3
"""
Test script to verify the RAG application setup
"""

import os
import sys
from datetime import datetime


def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")

    try:
        import streamlit

        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False

    try:
        import pymongo

        print("✅ PyMongo imported successfully")
    except ImportError as e:
        print(f"❌ PyMongo import failed: {e}")
        return False

    try:
        import sentence_transformers

        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers import failed: {e}")
        return False

    try:
        import openai

        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
        return False

    try:
        import PyPDF2

        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False

    try:
        import docx

        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ python-docx import failed: {e}")
        return False

    return True


def test_local_imports():
    """Test if local modules can be imported"""
    print("\n🔍 Testing local module imports...")

    try:
        from config import OPENAI_API_KEY, MONGODB_URI, EMBEDDING_MODEL

        print("✅ Config module imported successfully")
    except ImportError as e:
        print(f"❌ Config import failed: {e}")
        return False

    try:
        from document_processor import DocumentProcessor

        print("✅ DocumentProcessor imported successfully")
    except ImportError as e:
        print(f"❌ DocumentProcessor import failed: {e}")
        return False

    try:
        from mongodb_client import MongoDBClient

        print("✅ MongoDBClient imported successfully")
    except ImportError as e:
        print(f"❌ MongoDBClient import failed: {e}")
        return False

    try:
        from rag_chatbot import RAGChatbot

        print("✅ RAGChatbot imported successfully")
    except ImportError as e:
        print(f"❌ RAGChatbot import failed: {e}")
        return False

    return True


def test_configuration():
    """Test configuration settings"""
    print("\n🔍 Testing configuration...")

    from config import OPENAI_API_KEY, MONGODB_URI, EMBEDDING_MODEL

    if OPENAI_API_KEY:
        print("✅ OpenAI API key is configured")
    else:
        print("⚠️  OpenAI API key is not set (required for chat functionality)")

    if MONGODB_URI:
        print(f"✅ MongoDB URI is configured: {MONGODB_URI}")
    else:
        print("❌ MongoDB URI is not configured")

    if EMBEDDING_MODEL:
        print(f"✅ Embedding model is configured: {EMBEDDING_MODEL}")
    else:
        print("❌ Embedding model is not configured")

    return True


def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")

    try:
        from mongodb_client import MongoDBClient

        client = MongoDBClient()
        client.close_connection()
        print("✅ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("💡 Make sure MongoDB is running or check your connection string")
        return False


def test_embedding_model():
    """Test embedding model loading"""
    print("\n🔍 Testing embedding model...")

    try:
        from sentence_transformers import SentenceTransformer
        from config import EMBEDDING_MODEL

        print(f"Loading model: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)

        # Test encoding
        test_text = "This is a test sentence."
        embedding = model.encode([test_text])
        print(
            f"✅ Embedding model loaded successfully (dimension: {len(embedding[0])})"
        )
        return True
    except Exception as e:
        print(f"❌ Embedding model test failed: {e}")
        return False


def test_document_processor():
    """Test document processor functionality"""
    print("\n🔍 Testing document processor...")

    try:
        from document_processor import DocumentProcessor

        processor = DocumentProcessor()

        # Test text chunking
        test_text = "This is a test document. " * 100  # Create a longer text
        chunks = processor.chunk_text(test_text)
        print(f"✅ Text chunking works (created {len(chunks)} chunks)")

        # Test embedding generation
        embeddings = processor.generate_embeddings(
            chunks[:2]
        )  # Test with first 2 chunks
        print(f"✅ Embedding generation works (dimension: {len(embeddings[0])})")

        return True
    except Exception as e:
        print(f"❌ Document processor test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 RAG Application Setup Test")
    print("=" * 50)

    tests = [
        test_imports,
        test_local_imports,
        test_configuration,
        test_mongodb_connection,
        test_embedding_model,
        test_document_processor,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your RAG application is ready to use.")
        print("\n🚀 To start the application, run:")
        print("   streamlit run main.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
        print("\n💡 Common solutions:")
        print("   - Install missing dependencies: pip install -r requirements.txt")
        print("   - Set OpenAI API key: export OPENAI_API_KEY='your-key'")
        print("   - Start MongoDB: mongod --dbpath /path/to/your/db")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
