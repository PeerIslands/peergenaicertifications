#!/usr/bin/env python3
"""
Test script for semantic chunking functionality.
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from text_chunker import TextChunker
from config import settings

def test_semantic_chunking():
    """Test semantic chunking with sample text."""
    
    # Sample text for testing
    sample_text = """
    Machine learning is a subset of artificial intelligence that focuses on algorithms and statistical models.
    These algorithms enable computer systems to improve their performance on a specific task through experience.
    Deep learning is a subset of machine learning that uses neural networks with multiple layers.
    Neural networks are inspired by the structure and function of the human brain.
    Natural language processing is another important area of AI that deals with human language.
    Computer vision enables machines to interpret and understand visual information from the world.
    Reinforcement learning is a type of machine learning where agents learn through interaction with an environment.
    Supervised learning uses labeled training data to learn a mapping from inputs to outputs.
    Unsupervised learning finds hidden patterns in data without labeled examples.
    Transfer learning allows models to apply knowledge learned in one domain to another domain.
    """
    
    print("=== Testing Semantic Chunking ===")
    print(f"Configuration:")
    print(f"  Semantic threshold: {settings.semantic_chunking_threshold}")
    print(f"  Embedding model: {settings.embedding_model}")
    print(f"  Ollama base URL: {settings.ollama_base_url}")
    print()
    
    # Initialize chunker
    chunker = TextChunker()
    
    # Get chunking info
    chunking_info = chunker.get_chunking_info()
    print(f"Chunking method: {chunking_info['chunking_method']}")
    print(f"Embeddings available: {chunking_info['embeddings_available']}")
    print()
    
    # Test chunking
    print("Testing chunking...")
    chunks = chunker.chunk_text(sample_text.strip())
    
    print(f"Number of chunks created: {len(chunks)}")
    print()
    
    # Display chunks
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(f"Method: {chunk['chunking_method']}")
        print(f"Size: {chunk['chunk_size']} characters")
        print(f"Content: {chunk['chunk_text'][:200]}...")
        print()
    
    return chunks

def test_custom_threshold():
    """Test semantic chunking with custom threshold."""
    
    print("=== Testing Semantic Chunking with Custom Threshold ===")
    
    # Initialize chunker with custom threshold
    chunker = TextChunker(semantic_threshold=0.3)
    
    # Get chunking info
    chunking_info = chunker.get_chunking_info()
    print(f"Chunking method: {chunking_info['chunking_method']}")
    print(f"Semantic threshold: {chunking_info['semantic_threshold']}")
    print()
    
    # Sample text
    sample_text = """
    This is a test document with multiple paragraphs.
    
    Each paragraph contains different information.
    The semantic chunker will group related content together.
    
    It will respect semantic boundaries and meaning structure.
    """
    
    # Test chunking
    chunks = chunker.chunk_text(sample_text.strip())
    
    print(f"Number of chunks created: {len(chunks)}")
    print()
    
    # Display chunks
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(f"Method: {chunk['chunking_method']}")
        print(f"Size: {chunk['chunk_size']} characters")
        print(f"Content: {chunk['chunk_text']}")
        print()
    
    return chunks

if __name__ == "__main__":
    try:
        # Test semantic chunking
        semantic_chunks = test_semantic_chunking()
        
        print("\n" + "="*50 + "\n")
        
        # Test custom threshold
        custom_chunks = test_custom_threshold()
        
        print("\n=== Test Summary ===")
        print(f"Default semantic chunks: {len(semantic_chunks)}")
        print(f"Custom threshold chunks: {len(custom_chunks)}")
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
