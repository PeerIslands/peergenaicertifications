#!/usr/bin/env python3
"""
Main script for PDF document ingestion into Vector MongoDB
"""
import argparse
import sys
import os
from pathlib import Path
import logging

from ingestion_pipeline import DocumentIngestionPipeline

def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ingestion.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Ingest PDF documents into Vector MongoDB database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage - process all PDFs in current PDF folder
  python main.py

  # Specify custom PDF folder
  python main.py --pdf-folder /path/to/pdfs

  # Custom MongoDB connection
  python main.py --mongodb-uri "mongodb://localhost:27017/"

  # Custom chunk size and overlap
  python main.py --chunk-size 1500 --chunk-overlap 300

  # Force reprocess all files
  python main.py --force-reprocess

  # Verbose output
  python main.py --verbose
        """
    )
    
    # Required arguments
    parser.add_argument(
        '--pdf-folder',
        type=str,
        default='./PDF',
        help='Path to folder containing PDF files (default: ./PDF)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--mongodb-uri',
        type=str,
        default=os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'),
        help='MongoDB connection URI (default: mongodb://localhost:27017/)'
    )
    
    parser.add_argument(
        '--database-name',
        type=str,
        default=os.getenv('DATABASE_NAME', 'rag_documents'),
        help='MongoDB database name (default: rag_documents)'
    )
    
    parser.add_argument(
        '--chunk-size',
        type=int,
        default=1000,
        help='Maximum characters per chunk (default: 1000)'
    )
    
    parser.add_argument(
        '--chunk-overlap',
        type=int,
        default=200,
        help='Character overlap between chunks (default: 200)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=50,
        help='Number of chunks to process in each batch (default: 50)'
    )
    
    parser.add_argument(
        '--force-reprocess',
        action='store_true',
        help='Force reprocessing of all files, even if already processed'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--stats-file',
        type=str,
        default='ingestion_stats.json',
        help='Output file for processing statistics (default: ingestion_stats.json)'
    )
    
    parser.add_argument(
        '--use-azure-openai',
        action='store_true',
        default=os.getenv('USE_AZURE_OPENAI', 'false').lower() == 'true',
        help='Use Azure OpenAI for embeddings instead of sentence-transformers'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Validate PDF folder
    pdf_folder = Path(args.pdf_folder)
    if not pdf_folder.exists():
        logger.error(f"PDF folder does not exist: {pdf_folder}")
        sys.exit(1)
    
    if not pdf_folder.is_dir():
        logger.error(f"PDF folder is not a directory: {pdf_folder}")
        sys.exit(1)
    
    # Check for PDF files
    pdf_files = list(pdf_folder.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {pdf_folder}")
        logger.info("Please add PDF files to the folder and try again")
        sys.exit(0)
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    try:
        # Initialize pipeline
        pipeline = DocumentIngestionPipeline(
            pdf_folder_path=str(pdf_folder),
            mongodb_connection=args.mongodb_uri,
            database_name=args.database_name,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
            batch_size=args.batch_size,
            use_azure_openai=args.use_azure_openai
        )
        
        # Run ingestion
        logger.info("Starting document ingestion...")
        stats = pipeline.run_ingestion(force_reprocess=args.force_reprocess)
        
        # Save statistics
        pipeline.save_stats(args.stats_file)
        
        # Print summary
        print("\n" + "="*60)
        print("INGESTION SUMMARY")
        print("="*60)
        print(f"Files processed: {stats['total_files_processed']}")
        print(f"Chunks created: {stats['total_chunks_created']}")
        print(f"Pages processed: {stats['total_pages_processed']}")
        print(f"Failed files: {len(stats['failed_files'])}")
        
        if 'processing_duration_seconds' in stats:
            print(f"Processing time: {stats['processing_duration_seconds']:.2f} seconds")
            print(f"Chunks per second: {stats['chunks_per_second']:.2f}")
        
        if stats['failed_files']:
            print("\nFailed files:")
            for failed in stats['failed_files']:
                print(f"  - {failed['file']}: {failed['error']}")
        
        print(f"\nStatistics saved to: {args.stats_file}")
        print("="*60)
        
        # Exit with appropriate code
        if stats['failed_files']:
            logger.warning("Some files failed to process")
            sys.exit(1)
        else:
            logger.info("All files processed successfully")
            sys.exit(0)
            
    except KeyboardInterrupt:
        logger.info("Ingestion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
