"""
Main PDF ingestion tool that orchestrates the entire process.
"""
import os
from typing import List, Dict, Any
from pathlib import Path

from pdf_reader import PDFReader
from text_chunker import TextChunker
from mongodb_client import MongoDBClient
from embedding_generator import EmbeddingGenerator
from config import settings


class PDFIngestionTool:
    """Main tool for PDF ingestion, chunking, and embedding generation."""
    
    def __init__(self):
        """Initialize all components."""
        self.pdf_reader = PDFReader()
        self.text_chunker = TextChunker("recursive", 1000, 0)
        self.mongodb_client = MongoDBClient()
        self.embedding_generator = EmbeddingGenerator()
        
    def test_connections(self) -> bool:
        """Test all external connections."""
        print("Testing connections...")
        
        # Test MongoDB connection
        if not self.mongodb_client.test_connection():
            return False
            
        # Test Ollama connection
        if not self.embedding_generator.test_connection():
            return False
            
        print("All connections successful!")
        return True
    
    def process_single_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Process a single PDF file through the entire pipeline."""
        print(f"\nProcessing PDF: {pdf_path.name}")
        
        # Step 1: Read PDF
        print("  Reading PDF...")
        pdf_data = self.pdf_reader.read_pdf(pdf_path)
        
        # Step 2: Chunk text
        print("  Chunking text...")
        chunking_info = self.text_chunker.get_chunking_info()
        print(f"  Using {chunking_info['chunking_method']} chunking method")
        
        # Print all properties of chunking_info object
        print("  Chunking Info Properties:")
        for key, value in chunking_info.items():
            print(f"    {key}: {value}")
        chunks = self.text_chunker.chunk_pdf_data(pdf_data)
        print(f"  Created {len(chunks)} chunks")
        
        # Step 3: Store chunks in MongoDB
        print("  Storing chunks in MongoDB...")
        chunk_ids = self.mongodb_client.insert_chunks(chunks)
        print(f"  Stored {len(chunk_ids)} chunks")
        
        # Step 4: Generate embeddings and update MongoDB
        print("  Generating embeddings...")
        texts_to_embed = [chunk["chunk_text"] for chunk in chunks]
        embeddings = self.embedding_generator.generate_embeddings_batch(texts_to_embed)
        
        # Update MongoDB documents with embeddings
        print("  Updating MongoDB with embeddings...")
        for i, (chunk_id, embedding) in enumerate(zip(chunk_ids, embeddings)):
            self.mongodb_client.update_chunk_embedding(chunk_id, embedding)
        
        print(f"  Successfully processed {pdf_path.name}")
        
        return {
            "file_name": pdf_path.name,
            "chunks_created": len(chunks),
            "chunks_stored": len(chunk_ids),
            "embeddings_generated": len(embeddings)
        }
    
    def process_all_pdfs(self) -> Dict[str, Any]:
        """Process all PDF files in the configured folder."""
        print("Starting PDF ingestion process...")
        
        # Test connections first
        if not self.test_connections():
            raise Exception("Connection tests failed. Please check your configuration.")
        
        # Clear all existing documents from MongoDB before processing
        print("Clearing existing documents from MongoDB...")
        deleted_count = self.mongodb_client.clear_all_documents()
        
        # Create MongoDB indexes
        self.mongodb_client.create_indexes()
        
        # Get all PDF files
        try:
            pdf_files = self.pdf_reader.get_pdf_files()
        except FileNotFoundError as e:
            raise Exception(f"PDF folder error: {str(e)}")
        
        print(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each PDF
        results = []
        total_chunks = 0
        total_embeddings = 0
        
        for pdf_file in pdf_files:
            try:
                result = self.process_single_pdf(pdf_file)
                results.append(result)
                total_chunks += result["chunks_created"]
                total_embeddings += result["embeddings_generated"]
            except Exception as e:
                print(f"Error processing {pdf_file.name}: {str(e)}")
                continue
        
        # Summary
        summary = {
            "total_files_processed": len(results),
            "total_chunks_created": total_chunks,
            "total_embeddings_generated": total_embeddings,
            "files": results
        }
        
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Files processed: {summary['total_files_processed']}")
        print(f"Total chunks created: {summary['total_chunks_created']}")
        print(f"Total embeddings generated: {summary['total_embeddings_generated']}")
        
        return summary
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about processed data."""
        try:
            all_chunks = self.mongodb_client.get_all_chunks()
            
            stats = {
                "total_chunks": len(all_chunks),
                "chunks_with_embeddings": len([c for c in all_chunks if "embedding" in c]),
                "unique_files": len(set(c["metadata"]["source_file"] for c in all_chunks)),
                "files": {}
            }
            
            # Group by file
            for chunk in all_chunks:
                file_name = chunk["metadata"]["source_file"]
                if file_name not in stats["files"]:
                    stats["files"][file_name] = {
                        "chunks": 0,
                        "has_embeddings": 0
                    }
                stats["files"][file_name]["chunks"] += 1
                if "embedding" in chunk:
                    stats["files"][file_name]["has_embeddings"] += 1
            
            return stats
        except Exception as e:
            raise Exception(f"Error getting stats: {str(e)}")
    
    def cleanup_file(self, file_name: str) -> int:
        """Remove all chunks for a specific file."""
        deleted_count = self.mongodb_client.delete_chunks_by_file(file_name)
        print(f"Deleted {deleted_count} chunks for file: {file_name}")
        return deleted_count
    
    def close_connections(self):
        """Close all external connections."""
        self.mongodb_client.close_connection()


def main():
    """Main function to run the PDF ingestion tool."""
    try:
        # Initialize the tool
        tool = PDFIngestionTool()
        
        # Process all PDFs
        results = tool.process_all_pdfs()
        
        # Show final stats
        print("\n=== FINAL STATISTICS ===")
        stats = tool.get_processing_stats()
        print(f"Total chunks in database: {stats['total_chunks']}")
        print(f"Chunks with embeddings: {stats['chunks_with_embeddings']}")
        print(f"Unique files processed: {stats['unique_files']}")
        
        # Close connections
        tool.close_connections()
        
    except Exception as e:
        print(f"Error in main process: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
