#!/usr/bin/env python3
"""
Example usage of semantic chunking functionality.
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from text_chunker import TextChunker
from config import settings

def main():
    """Demonstrate semantic chunking usage."""
    
    print("=== Semantic Chunking Example ===\n")
    
    # Example 1: Use default configuration
    print("1. Using default configuration:")
    chunker_default = TextChunker()
    chunking_info = chunker_default.get_chunking_info()
    print(f"   Method: {chunking_info['chunking_method']}")
    print(f"   Model: {chunking_info['embedding_model']}")
    print(f"   Threshold: {chunking_info['semantic_threshold']}")
    print()
    
    # Example 2: Custom semantic chunking configuration
    print("2. Custom semantic chunking configuration:")
    chunker_custom = TextChunker(
        semantic_threshold=0.3  # Lower threshold for more sensitive splitting
    )
    chunking_info = chunker_custom.get_chunking_info()
    print(f"   Method: {chunking_info['chunking_method']}")
    print(f"   Model: {chunking_info['embedding_model']}")
    print(f"   Threshold: {chunking_info['semantic_threshold']}")
    print()
    
    # Example text for chunking
    sample_text = """
    Artificial Intelligence (AI) is transforming industries across the globe.
    Machine learning algorithms can now process vast amounts of data efficiently.
    Deep learning models have achieved remarkable success in image recognition.
    Natural language processing enables computers to understand human language.
    Computer vision systems can identify objects and patterns in images.
    Robotics combines AI with mechanical engineering to create intelligent machines.
    Autonomous vehicles use AI for navigation and decision-making.
    Healthcare applications of AI include medical diagnosis and drug discovery.
    Financial services use AI for fraud detection and algorithmic trading.
    The future of AI holds promise for solving complex global challenges.
    """
    
    print("4. Chunking sample text:")
    chunks = chunker_default.chunk_text(sample_text.strip())
    
    print(f"   Created {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i+1}: {chunk['chunk_size']} chars, method: {chunk['chunking_method']}")
        print(f"   Preview: {chunk['chunk_text'][:100]}...")
        print()
    
    print("=== Configuration Options ===")
    print("You can configure semantic chunking through:")
    print("1. Environment variables (create .env file):")
    print("   SEMANTIC_CHUNKING_THRESHOLD=0.5")
    print("   EMBEDDING_MODEL=embeddinggemma")
    print("   OLLAMA_BASE_URL=http://localhost:11434")
    print()
    print("2. Direct initialization:")
    print("   chunker = TextChunker(semantic_threshold=0.3)")
    print()
    print("3. Configuration file (config.py):")
    print("   Modify the default values in the Settings class")

if __name__ == "__main__":
    main()
