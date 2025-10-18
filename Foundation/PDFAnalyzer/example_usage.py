#!/usr/bin/env python3
"""
Example usage of the PDF document ingestion system
"""
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import VectorMongoDB
from pdf_processor import PDFProcessor
from ingestion_pipeline import DocumentIngestionPipeline

def example_basic_usage():
    """Example of basic usage"""
    print("=== Basic Usage Example ===")
    
    # Initialize the pipeline
    pipeline = DocumentIngestionPipeline(
        pdf_folder_path="./PDF",
        mongodb_connection="mongodb://localhost:27017/",
        database_name="rag_documents"
    )
    
    # Run ingestion
    print("Starting document ingestion...")
    stats = pipeline.run_ingestion()
    
    print(f"Processed {stats['total_files_processed']} files")
    print(f"Created {stats['total_chunks_created']} chunks")
    print(f"Processed {stats['total_pages_processed']} pages")

def example_search_documents():
    """Example of searching documents"""
    print("\n=== Document Search Example ===")
    
    # Connect to database
    vector_db = VectorMongoDB("mongodb://localhost:27017/", "rag_documents")
    vector_db.connect()
    
    # Search for similar content
    query = "generative adversarial networks"
    results = vector_db.search_similar(query, limit=5)
    
    print(f"Search results for '{query}':")
    for i, result in enumerate(results, 1):
        print(f"{i}. Document: {result['document_name']}")
        print(f"   Page: {result['page_number']}")
        print(f"   Text: {result['text'][:100]}...")
        print()
    
    vector_db.close()

def example_get_document_info():
    """Example of getting document information"""
    print("\n=== Document Information Example ===")
    
    # Connect to database
    vector_db = VectorMongoDB("mongodb://localhost:27017/", "rag_documents")
    vector_db.connect()
    
    # Get database statistics
    stats = vector_db.get_document_stats()
    print("Database Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get chunks for a specific document
    pdf_files = list(Path("./PDF").glob("*.pdf"))
    if pdf_files:
        document_name = pdf_files[0].name
        chunks = vector_db.get_document_chunks(document_name)
        print(f"\nChunks for {document_name}:")
        for chunk in chunks[:3]:  # Show first 3 chunks
            print(f"  Page {chunk['page_number']}, Chunk {chunk['chunk_index']}: {chunk['text'][:50]}...")
    
    vector_db.close()

def example_custom_processing():
    """Example of custom PDF processing"""
    print("\n=== Custom Processing Example ===")
    
    # Initialize PDF processor with custom settings
    processor = PDFProcessor(chunk_size=500, chunk_overlap=100)
    
    # Process a single PDF file
    pdf_files = list(Path("./PDF").glob("*.pdf"))
    if pdf_files:
        pdf_file = pdf_files[0]
        print(f"Processing {pdf_file.name} with custom settings...")
        
        chunks = processor.process_pdf_file(str(pdf_file))
        stats = processor.get_processing_stats(chunks)
        
        print("Processing Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print(f"\nFirst chunk preview:")
        if chunks:
            print(f"  Text: {chunks[0]['text'][:100]}...")
            print(f"  Page: {chunks[0]['page_number']}")
            print(f"  Characters: {chunks[0]['char_count']}")

if __name__ == "__main__":
    print("PDF Document Ingestion System - Example Usage")
    print("=" * 50)
    
    # Check if PDF folder exists
    pdf_folder = Path("./PDF")
    if not pdf_folder.exists():
        print("Error: PDF folder not found. Please create a PDF folder and add PDF files.")
        sys.exit(1)
    
    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        print("Error: No PDF files found in PDF folder.")
        sys.exit(1)
    
    print(f"Found {len(pdf_files)} PDF files to process")
    
    try:
        # Run examples
        example_basic_usage()
        example_search_documents()
        example_get_document_info()
        example_custom_processing()
        
        print("\n" + "=" * 50)
        print("Examples completed successfully!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        sys.exit(1)
