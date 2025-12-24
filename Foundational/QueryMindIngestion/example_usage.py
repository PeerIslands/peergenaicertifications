"""
Example usage of the PDF ingestion tool components.
"""
import os
from pathlib import Path

from pdf_ingestion_tool import PDFIngestionTool
from pdf_reader import PDFReader
from text_chunker import TextChunker
from mongodb_client import MongoDBClient
from embedding_generator import EmbeddingGenerator


def example_full_pipeline():
    """Example of using the complete PDF ingestion pipeline."""
    print("=== Full Pipeline Example ===")
    
    # Initialize the main tool
    tool = PDFIngestionTool()
    
    # Test connections
    if not tool.test_connections():
        print("Connection tests failed!")
        return
    
    # Process all PDFs
    try:
        results = tool.process_all_pdfs()
        print(f"Successfully processed {results['total_files_processed']} files")
        
        # Get statistics
        stats = tool.get_processing_stats()
        print(f"Database contains {stats['total_chunks']} chunks")
        
    except Exception as e:
        print(f"Error during processing: {e}")
    finally:
        tool.close_connections()


def example_individual_components():
    """Example of using individual components."""
    print("\n=== Individual Components Example ===")
    
    # Example PDF data (you would normally read this from a file)
    sample_pdf_data = {
        "file_path": "/path/to/sample.pdf",
        "file_name": "sample.pdf",
        "total_pages": 1,
        "text_content": "This is a sample PDF content. It contains some text that will be chunked and processed for embedding generation. The text is split into manageable pieces for better processing.",
        "metadata": {
            "title": "Sample Document",
            "author": "Example Author",
            "creator": "PDF Creator",
            "creation_date": "2024-01-01"
        }
    }
    
    # Step 1: Chunk the text using semantic chunking
    print("1. Chunking text with semantic chunking...")
    semantic_chunker = TextChunker(chunking_method="semantic")  # Uses semantic_threshold from config
    semantic_chunks = semantic_chunker.chunk_pdf_data(sample_pdf_data)
    print(f"   Created {len(semantic_chunks)} semantic chunks")
    
    # Step 1b: Chunk the text using recursive character splitting
    print("1b. Chunking text with recursive character splitting...")
    recursive_chunker = TextChunker(chunking_method="recursive", chunk_size=700, chunk_overlap=50)
    recursive_chunks = recursive_chunker.chunk_pdf_data(sample_pdf_data)
    print(f"   Created {len(recursive_chunks)} recursive chunks")
    
    # Use semantic chunks for the rest of the pipeline
    chunks = semantic_chunks
    
    # Step 2: Store in MongoDB
    print("2. Storing in MongoDB...")
    mongo = MongoDBClient()
    if mongo.test_connection():
        chunk_ids = mongo.insert_chunks(chunks)
        print(f"   Stored {len(chunk_ids)} chunks")
        
        # Step 3: Generate embeddings
        print("3. Generating embeddings...")
        embedder = EmbeddingGenerator()
        if embedder.test_connection():
            texts = [chunk["chunk_text"] for chunk in chunks]
            embeddings = embedder.generate_embeddings_batch(texts)
            
            # Update MongoDB with embeddings
            print("4. Updating MongoDB with embeddings...")
            for chunk_id, embedding in zip(chunk_ids, embeddings):
                mongo.update_chunk_embedding(chunk_id, embedding)
            
            print(f"   Generated {len(embeddings)} embeddings")
            
            # Show some stats
            stats = mongo.get_processing_stats()
            print(f"   Database now contains {stats['total_chunks']} total chunks")
        else:
            print("   Ollama connection failed!")
    else:
        print("   MongoDB connection failed!")
    
    mongo.close_connection()


def example_configuration():
    """Example of different configuration options."""
    print("\n=== Configuration Example ===")
    
    # Custom configuration for semantic chunking
    semantic_chunker = TextChunker(chunking_method="semantic")  # Uses semantic_threshold from config
    
    # Custom configuration for recursive character chunking
    recursive_chunker = TextChunker(
        chunking_method="recursive", 
        chunk_size=700, 
        chunk_overlap=50
    )
    
    custom_mongo = MongoDBClient(
        uri="mongodb://localhost:27017",
        database_name="custom_db",
        collection_name="custom_chunks"
    )
    custom_embedder = EmbeddingGenerator(
        base_url="http://localhost:11434",
        model_name="embeddinggemma"
    )
    
    print("Custom components initialized with:")
    print(f"  Semantic chunker: threshold from config (0.7)")
    print(f"  Recursive chunker: chunk_size=700, chunk_overlap=50")
    print(f"  MongoDB: custom_db.custom_chunks")
    print(f"  Ollama model: embeddinggemma")
    
    # Show chunking info for both methods
    print("\nSemantic chunking info:")
    semantic_info = semantic_chunker.get_chunking_info()
    for key, value in semantic_info.items():
        print(f"  {key}: {value}")
    
    print("\nRecursive chunking info:")
    recursive_info = recursive_chunker.get_chunking_info()
    for key, value in recursive_info.items():
        print(f"  {key}: {value}")


def example_error_handling():
    """Example of error handling."""
    print("\n=== Error Handling Example ===")
    
    try:
        # Try to read from non-existent folder
        reader = PDFReader("./non_existent_folder")
        pdf_files = reader.get_pdf_files()
    except FileNotFoundError as e:
        print(f"Expected error: {e}")
    
    try:
        # Try to connect to non-existent MongoDB
        mongo = MongoDBClient(uri="mongodb://localhost:99999")
        if not mongo.test_connection():
            print("Expected MongoDB connection failure")
    except Exception as e:
        print(f"Expected MongoDB error: {e}")


if __name__ == "__main__":
    print("PDF Ingestion Tool - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_configuration()
    example_error_handling()
    
    # Uncomment these to run the full examples (requires MongoDB and Ollama)
    # example_individual_components()
    # example_full_pipeline()
    
    print("\nTo run the full examples, ensure MongoDB and Ollama are running,")
    print("then uncomment the relevant lines in this script.")
