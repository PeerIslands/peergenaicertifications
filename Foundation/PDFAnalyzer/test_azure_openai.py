#!/usr/bin/env python3
"""
Test script for Azure OpenAI integration
"""
import os
import sys
from azure_embeddings import AzureOpenAIEmbeddings, HybridEmbeddingService

def test_azure_openai_connection():
    """Test Azure OpenAI connection"""
    print("Testing Azure OpenAI connection...")
    
    try:
        # Check if environment variables are set
        endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        api_key = os.getenv('AZURE_OPENAI_API_KEY')
        
        if not endpoint or not api_key:
            print("❌ Azure OpenAI environment variables not set")
            print("Please set:")
            print("  export AZURE_OPENAI_ENDPOINT='https://your-resource.openai.azure.com/'")
            print("  export AZURE_OPENAI_API_KEY='your-api-key-here'")
            return False
        
        # Initialize Azure OpenAI service
        azure_service = AzureOpenAIEmbeddings(
            endpoint=endpoint,
            api_key=api_key
        )
        
        # Test connection
        if azure_service.test_connection():
            print("✅ Azure OpenAI connection successful")
            
            # Test embedding generation
            test_text = "This is a test document for embedding generation."
            embedding = azure_service.generate_embedding(test_text)
            print(f"✅ Generated embedding with {len(embedding)} dimensions")
            
            return True
        else:
            print("❌ Azure OpenAI connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Azure OpenAI: {e}")
        return False

def test_hybrid_service():
    """Test hybrid embedding service"""
    print("\nTesting Hybrid Embedding Service...")
    
    try:
        # Test with sentence transformers (default)
        print("Testing sentence transformers...")
        hybrid_service = HybridEmbeddingService(use_azure=False)
        test_text = "This is a test for sentence transformers."
        embedding = hybrid_service.generate_embedding(test_text)
        print(f"✅ Sentence transformers embedding: {len(embedding)} dimensions")
        
        # Test with Azure OpenAI (if configured)
        if os.getenv('AZURE_OPENAI_ENDPOINT') and os.getenv('AZURE_OPENAI_API_KEY'):
            print("Testing Azure OpenAI...")
            hybrid_service_azure = HybridEmbeddingService(
                use_azure=True,
                endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY')
            )
            embedding_azure = hybrid_service_azure.generate_embedding(test_text)
            print(f"✅ Azure OpenAI embedding: {len(embedding_azure)} dimensions")
        else:
            print("⚠️  Azure OpenAI not configured, skipping test")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing hybrid service: {e}")
        return False

def test_batch_embeddings():
    """Test batch embedding generation"""
    print("\nTesting batch embedding generation...")
    
    try:
        if not (os.getenv('AZURE_OPENAI_ENDPOINT') and os.getenv('AZURE_OPENAI_API_KEY')):
            print("⚠️  Azure OpenAI not configured, skipping batch test")
            return True
        
        azure_service = AzureOpenAIEmbeddings(
            endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY')
        )
        
        test_texts = [
            "First document about machine learning.",
            "Second document about artificial intelligence.",
            "Third document about natural language processing."
        ]
        
        embeddings = azure_service.generate_embeddings_batch(test_texts)
        print(f"✅ Generated {len(embeddings)} embeddings in batch")
        
        for i, embedding in enumerate(embeddings):
            print(f"  Embedding {i+1}: {len(embedding)} dimensions")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing batch embeddings: {e}")
        return False

def main():
    """Main test function"""
    print("Azure OpenAI Integration Test")
    print("=" * 40)
    
    success = True
    
    # Test Azure OpenAI connection
    if not test_azure_openai_connection():
        success = False
    
    # Test hybrid service
    if not test_hybrid_service():
        success = False
    
    # Test batch embeddings
    if not test_batch_embeddings():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed!")
        print("\nYou can now use Azure OpenAI with:")
        print("  python main.py --use-azure-openai")
    else:
        print("❌ Some tests failed!")
        print("Please check your Azure OpenAI configuration.")
        sys.exit(1)

if __name__ == "__main__":
    main()
