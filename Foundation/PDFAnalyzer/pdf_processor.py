"""
PDF Processing Module for Text Extraction and Page-wise Chunking
"""
import os
import uuid
from typing import List, Dict, Any, Generator
import PyPDF2
import logging
import re
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF text extraction and chunking processor"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize PDF processor
        
        Args:
            chunk_size: Maximum number of characters per chunk
            chunk_overlap: Number of characters to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Extract text from PDF file page by page
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List[Dict]: List of pages with extracted text and metadata
        """
        try:
            pages = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                logger.info(f"Processing PDF: {os.path.basename(pdf_path)} ({total_pages} pages)")
                
                for page_num in range(total_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        
                        # Clean and preprocess text
                        cleaned_text = self._clean_text(text)
                        
                        if cleaned_text.strip():  # Only add non-empty pages
                            pages.append({
                                'page_number': page_num + 1,
                                'text': cleaned_text,
                                'char_count': len(cleaned_text),
                                'word_count': len(cleaned_text.split())
                            })
                            
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
                
                logger.info(f"Successfully extracted text from {len(pages)} pages")
                return pages
                
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {pdf_path}: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and preprocess extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers (simple heuristic)
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip lines that are likely page numbers or headers
            if (len(line) < 3 or 
                line.isdigit() or 
                re.match(r'^\d+$', line) or
                re.match(r'^Page \d+$', line, re.IGNORECASE)):
                continue
            cleaned_lines.append(line)
        
        return ' '.join(cleaned_lines).strip()
    
    def chunk_text(self, text: str, page_number: int) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            page_number: Page number for metadata
            
        Returns:
            List[Dict]: List of text chunks with metadata
        """
        if len(text) <= self.chunk_size:
            return [{
                'text': text,
                'page_number': page_number,
                'chunk_index': 0,
                'char_count': len(text),
                'word_count': len(text.split()),
                'is_complete_page': True
            }]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 200 characters
                search_start = max(start, end - 200)
                sentence_end = text.rfind('.', search_start, end)
                
                if sentence_end > search_start:
                    end = sentence_end + 1
                else:
                    # Look for word boundary
                    word_end = text.rfind(' ', search_start, end)
                    if word_end > search_start:
                        end = word_end
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'page_number': page_number,
                    'chunk_index': chunk_index,
                    'char_count': len(chunk_text),
                    'word_count': len(chunk_text.split()),
                    'is_complete_page': False
                })
                chunk_index += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_pdf_file(self, pdf_path: str, document_id: str = None) -> List[Dict[str, Any]]:
        """
        Process a single PDF file and return all chunks
        
        Args:
            pdf_path: Path to the PDF file
            document_id: Optional document ID (will generate if not provided)
            
        Returns:
            List[Dict]: List of all chunks from the PDF
        """
        if document_id is None:
            document_id = str(uuid.uuid4())
        
        # Extract text from all pages
        pages = self.extract_text_from_pdf(pdf_path)
        
        all_chunks = []
        global_chunk_index = 0
        
        for page in pages:
            # Chunk the page text
            page_chunks = self.chunk_text(page['text'], page['page_number'])
            
            # Add document metadata to each chunk
            for chunk in page_chunks:
                chunk.update({
                    'document_id': document_id,
                    'document_name': os.path.basename(pdf_path),
                    'document_path': pdf_path,
                    'global_chunk_index': global_chunk_index
                })
                all_chunks.append(chunk)
                global_chunk_index += 1
        
        logger.info(f"Processed {len(pages)} pages into {len(all_chunks)} chunks for document {document_id}")
        return all_chunks
    
    def process_pdf_folder(self, folder_path: str) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Process all PDF files in a folder
        
        Args:
            folder_path: Path to the folder containing PDF files
            
        Yields:
            List[Dict]: Chunks from each processed PDF file
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            raise FileNotFoundError(f"Folder not found: {folder_path}")
        
        pdf_files = list(folder.glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in folder: {folder_path}")
            return
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing: {pdf_file.name}")
                chunks = self.process_pdf_file(str(pdf_file))
                yield chunks
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_file.name}: {e}")
                continue
    
    def get_processing_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about processed chunks
        
        Args:
            chunks: List of processed chunks
            
        Returns:
            Dict: Processing statistics
        """
        if not chunks:
            return {}
        
        total_chunks = len(chunks)
        total_pages = len(set(chunk['page_number'] for chunk in chunks))
        total_documents = len(set(chunk['document_id'] for chunk in chunks))
        
        char_counts = [chunk['char_count'] for chunk in chunks]
        word_counts = [chunk['word_count'] for chunk in chunks]
        
        stats = {
            'total_chunks': total_chunks,
            'total_pages': total_pages,
            'total_documents': total_documents,
            'avg_chars_per_chunk': sum(char_counts) / len(char_counts),
            'avg_words_per_chunk': sum(word_counts) / len(word_counts),
            'min_chars_per_chunk': min(char_counts),
            'max_chars_per_chunk': max(char_counts),
            'complete_pages': sum(1 for chunk in chunks if chunk.get('is_complete_page', False))
        }
        
        return stats
