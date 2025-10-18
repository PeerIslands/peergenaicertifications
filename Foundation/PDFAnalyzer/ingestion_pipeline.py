"""
Main Document Ingestion Pipeline
"""
import os
import logging
from typing import List, Dict, Any
from pathlib import Path
from tqdm import tqdm
import json
from datetime import datetime

from database import VectorMongoDB
from pdf_processor import PDFProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ingestion.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentIngestionPipeline:
    """Main pipeline for ingesting documents into vector database"""
    
    def __init__(self, 
                 pdf_folder_path: str,
                 mongodb_connection: str = None,
                 database_name: str = "rag_documents",
                 chunk_size: int = 1000,
                 chunk_overlap: int = 200,
                 batch_size: int = 50,
                 use_azure_openai: bool = False):
        """
        Initialize the ingestion pipeline
        
        Args:
            pdf_folder_path: Path to folder containing PDF files
            mongodb_connection: MongoDB connection string
            database_name: Name of the MongoDB database
            chunk_size: Maximum characters per chunk
            chunk_overlap: Character overlap between chunks
            batch_size: Number of chunks to process in each batch
        """
        self.pdf_folder_path = Path(pdf_folder_path)
        self.batch_size = batch_size
        
        # Initialize components
        self.pdf_processor = PDFProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.vector_db = VectorMongoDB(connection_string=mongodb_connection, database_name=database_name, use_azure_openai=use_azure_openai)
        
        # Statistics tracking
        self.stats = {
            'total_files_processed': 0,
            'total_chunks_created': 0,
            'total_pages_processed': 0,
            'failed_files': [],
            'processing_start_time': None,
            'processing_end_time': None
        }
    
    def connect_database(self):
        """Establish database connection and create indexes"""
        try:
            self.vector_db.connect()
            self.vector_db.create_indexes()
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def process_single_file(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a single PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict: Processing results and statistics
        """
        try:
            logger.info(f"Processing file: {os.path.basename(pdf_path)}")
            
            # Process PDF and get chunks
            chunks = self.pdf_processor.process_pdf_file(pdf_path)
            
            if not chunks:
                logger.warning(f"No chunks generated for file: {pdf_path}")
                return {
                    'success': False,
                    'chunks_created': 0,
                    'pages_processed': 0,
                    'error': 'No chunks generated'
                }
            
            # Insert chunks into database in batches
            chunks_inserted = 0
            for i in range(0, len(chunks), self.batch_size):
                batch = chunks[i:i + self.batch_size]
                try:
                    self.vector_db.insert_chunks_batch(batch)
                    chunks_inserted += len(batch)
                except Exception as e:
                    logger.error(f"Failed to insert batch {i//self.batch_size + 1}: {e}")
                    # Try inserting chunks individually
                    for chunk in batch:
                        try:
                            self.vector_db.insert_chunk(chunk)
                            chunks_inserted += 1
                        except Exception as chunk_error:
                            logger.error(f"Failed to insert individual chunk: {chunk_error}")
            
            # Calculate statistics
            pages_processed = len(set(chunk['page_number'] for chunk in chunks))
            
            result = {
                'success': True,
                'chunks_created': chunks_inserted,
                'pages_processed': pages_processed,
                'file_name': os.path.basename(pdf_path),
                'processing_stats': self.pdf_processor.get_processing_stats(chunks)
            }
            
            logger.info(f"Successfully processed {os.path.basename(pdf_path)}: "
                       f"{chunks_inserted} chunks, {pages_processed} pages")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to process file {pdf_path}: {e}")
            return {
                'success': False,
                'chunks_created': 0,
                'pages_processed': 0,
                'error': str(e)
            }
    
    def run_ingestion(self, force_reprocess: bool = False) -> Dict[str, Any]:
        """
        Run the complete ingestion pipeline
        
        Args:
            force_reprocess: If True, reprocess files even if they already exist in database
            
        Returns:
            Dict: Complete ingestion results and statistics
        """
        self.stats['processing_start_time'] = datetime.now()
        logger.info("Starting document ingestion pipeline")
        
        try:
            # Connect to database
            self.connect_database()
            
            # Get list of PDF files
            pdf_files = list(self.pdf_folder_path.glob("*.pdf"))
            
            if not pdf_files:
                logger.warning(f"No PDF files found in {self.pdf_folder_path}")
                return self.stats
            
            logger.info(f"Found {len(pdf_files)} PDF files to process")
            
            # Process each file
            for pdf_file in tqdm(pdf_files, desc="Processing PDFs"):
                try:
                    # Check if file already processed (if not forcing reprocess)
                    if not force_reprocess:
                        existing_chunks = self.vector_db.get_document_chunks(os.path.basename(pdf_file))
                        if existing_chunks:
                            logger.info(f"Skipping {pdf_file.name} - already processed")
                            continue
                    
                    # Process the file
                    result = self.process_single_file(str(pdf_file))
                    
                    if result['success']:
                        self.stats['total_files_processed'] += 1
                        self.stats['total_chunks_created'] += result['chunks_created']
                        self.stats['total_pages_processed'] += result['pages_processed']
                    else:
                        self.stats['failed_files'].append({
                            'file': str(pdf_file),
                            'error': result.get('error', 'Unknown error')
                        })
                        
                except Exception as e:
                    logger.error(f"Unexpected error processing {pdf_file}: {e}")
                    self.stats['failed_files'].append({
                        'file': str(pdf_file),
                        'error': str(e)
                    })
            
            # Final statistics
            self.stats['processing_end_time'] = datetime.now()
            processing_duration = (self.stats['processing_end_time'] - 
                                 self.stats['processing_start_time']).total_seconds()
            
            self.stats['processing_duration_seconds'] = processing_duration
            self.stats['chunks_per_second'] = (self.stats['total_chunks_created'] / 
                                             processing_duration if processing_duration > 0 else 0)
            
            # Get database statistics
            try:
                db_stats = self.vector_db.get_document_stats()
                self.stats.update(db_stats)
            except Exception as e:
                logger.warning(f"Could not retrieve database statistics: {e}")
            
            # Log final results
            logger.info("=" * 50)
            logger.info("INGESTION COMPLETE")
            logger.info("=" * 50)
            logger.info(f"Files processed: {self.stats['total_files_processed']}")
            logger.info(f"Chunks created: {self.stats['total_chunks_created']}")
            logger.info(f"Pages processed: {self.stats['total_pages_processed']}")
            logger.info(f"Failed files: {len(self.stats['failed_files'])}")
            logger.info(f"Processing time: {processing_duration:.2f} seconds")
            logger.info(f"Chunks per second: {self.stats['chunks_per_second']:.2f}")
            
            if self.stats['failed_files']:
                logger.warning("Failed files:")
                for failed in self.stats['failed_files']:
                    logger.warning(f"  - {failed['file']}: {failed['error']}")
            
            return self.stats
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            self.stats['processing_end_time'] = datetime.now()
            self.stats['pipeline_error'] = str(e)
            raise
        finally:
            # Close database connection
            self.vector_db.close()
    
    def save_stats(self, output_file: str = "ingestion_stats.json"):
        """Save processing statistics to file"""
        try:
            with open(output_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
            logger.info(f"Statistics saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save statistics: {e}")
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database state"""
        try:
            self.vector_db.connect()
            stats = self.vector_db.get_document_stats()
            self.vector_db.close()
            return stats
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {}
