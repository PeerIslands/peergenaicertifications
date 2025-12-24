#!/usr/bin/env python3
"""
Examples demonstrating different semantic_threshold values for TextChunker.
This script shows how different threshold values affect chunking behavior.
"""
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from text_chunker import TextChunker
from config import settings

def demonstrate_thresholds():
    """Demonstrate different semantic threshold values."""
    
    # Sample academic text (similar to your PDF content)
    sample_text = """
    Generative Adversarial Networks (GANs) represent a revolutionary approach to machine learning.
    The generator network learns to create realistic data samples from random noise.
    The discriminator network learns to distinguish between real and generated samples.
    This adversarial training process leads to increasingly realistic data generation.
    
    Deep learning architectures have evolved significantly over the past decade.
    Convolutional Neural Networks (CNNs) excel at image recognition tasks.
    Recurrent Neural Networks (RNNs) are effective for sequential data processing.
    Transformer architectures have revolutionized natural language processing.
    
    Attention mechanisms allow models to focus on relevant parts of input sequences.
    Self-attention enables parallel processing of sequence elements.
    Multi-head attention provides multiple representation subspaces.
    These innovations have led to breakthroughs in machine translation and text generation.
    """
    
    # Different threshold values to test
    thresholds = [
        (0.2, "Very sensitive - many small chunks"),
        (0.35, "Balanced - good for academic papers"),
        (0.5, "Default - moderate chunking"),
        (0.7, "Less sensitive - larger chunks")
    ]
    
    print("=== Semantic Threshold Comparison ===\n")
    
    for threshold, description in thresholds:
        print(f"Threshold: {threshold} - {description}")
        print("-" * 50)
        
        try:
            # Note: TextChunker now only uses config threshold
            # To test different thresholds, modify config.py or use environment variables
            print(f"Note: TextChunker uses config threshold ({settings.semantic_chunking_threshold})")
            print("To test different thresholds, modify config.py or set environment variable")
            chunker = TextChunker()
            
            # Get chunking info
            info = chunker.get_chunking_info()
            print(f"Embedding model: {info['embedding_model']}")
            print(f"Actual threshold: {info['semantic_threshold']}")
            
            # Chunk the text
            chunks = chunker.chunk_text(sample_text.strip())
            
            print(f"Number of chunks: {len(chunks)}")
            print("Chunk sizes:", [chunk['chunk_size'] for chunk in chunks])
            
            # Show first chunk preview
            if chunks:
                first_chunk = chunks[0]['chunk_text']
                preview = first_chunk[:100] + "..." if len(first_chunk) > 100 else first_chunk
                print(f"First chunk preview: {preview}")
            
            print()
            
        except Exception as e:
            print(f"Error with threshold {threshold}: {e}")
            print()

def recommend_thresholds():
    """Provide recommendations for different use cases."""
    
    print("=== Semantic Threshold Recommendations ===\n")
    
    recommendations = [
        {
            "use_case": "Academic/Research Papers",
            "threshold": "0.3-0.4",
            "reason": "Provides good balance between granularity and context preservation",
            "example": "Set SEMANTIC_CHUNKING_THRESHOLD=0.35 in .env file"
        },
        {
            "use_case": "Technical Documentation",
            "threshold": "0.4-0.5",
            "reason": "Maintains logical sections while allowing detailed chunking",
            "example": "Set SEMANTIC_CHUNKING_THRESHOLD=0.45 in .env file"
        },
        {
            "use_case": "General Text Processing",
            "threshold": "0.5",
            "reason": "Default balanced approach for most applications",
            "example": "Set SEMANTIC_CHUNKING_THRESHOLD=0.5 in .env file"
        },
        {
            "use_case": "Large Document Summarization",
            "threshold": "0.6-0.7",
            "reason": "Creates larger chunks with more comprehensive context",
            "example": "Set SEMANTIC_CHUNKING_THRESHOLD=0.65 in .env file"
        },
        {
            "use_case": "Fine-grained Analysis",
            "threshold": "0.2-0.3",
            "reason": "Creates many small chunks for detailed analysis",
            "example": "Set SEMANTIC_CHUNKING_THRESHOLD=0.25 in .env file"
        }
    ]
    
    for rec in recommendations:
        print(f"Use Case: {rec['use_case']}")
        print(f"Recommended Threshold: {rec['threshold']}")
        print(f"Reason: {rec['reason']}")
        print(f"Example: {rec['example']}")
        print()

def threshold_guidelines():
    """Provide general guidelines for choosing thresholds."""
    
    print("=== Threshold Selection Guidelines ===\n")
    
    print("Threshold Range Effects:")
    print("• 0.1-0.3: Very sensitive splitting, creates many small chunks")
    print("• 0.3-0.5: Balanced approach, good for most use cases")
    print("• 0.5-0.7: Less sensitive, creates larger chunks with more context")
    print("• 0.7-0.9: Very coarse splitting, creates large chunks")
    print()
    
    print("Factors to Consider:")
    print("• Document type (academic, technical, general)")
    print("• Desired chunk granularity")
    print("• Context preservation needs")
    print("• Downstream processing requirements")
    print()
    
    print("Testing Recommendations:")
    print("• Start with 0.35 for academic content")
    print("• Test with sample documents")
    print("• Adjust based on chunk quality and quantity")
    print("• Consider your embedding model's characteristics")

if __name__ == "__main__":
    print("Semantic Threshold Examples for TextChunker")
    print("=" * 60)
    
    # Show recommendations first
    recommend_thresholds()
    
    # Show guidelines
    threshold_guidelines()
    
    # Demonstrate different thresholds (requires Ollama to be running)
    print("\n" + "=" * 60)
    print("Note: The demonstration below requires Ollama to be running")
    print("with the 'embeddinggemma' model available.")
    print("=" * 60)
    
    try:
        demonstrate_thresholds()
    except Exception as e:
        print(f"Demonstration failed (likely Ollama not running): {e}")
        print("\nTo run the demonstration:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull the model: ollama pull embeddinggemma")
        print("3. Run this script again")
