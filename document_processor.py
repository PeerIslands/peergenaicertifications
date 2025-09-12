import os
import PyPDF2
import docx
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import numpy as np
from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

class DocumentProcessor:
    def __init__(self):
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
    
    def extract_text_from_pdf(self, pdf_file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def extract_text_from_docx(self, docx_file) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(docx_file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            raise Exception(f"Error extracting text from DOCX: {str(e)}")
    
    def extract_text_from_txt(self, txt_file) -> str:
        """Extract text from TXT file"""
        try:
            content = txt_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content
        except Exception as e:
            raise Exception(f"Error extracting text from TXT: {str(e)}")
    
    def extract_text(self, uploaded_file) -> str:
        """Extract text from uploaded file based on file type"""
        file_extension = uploaded_file.name.split('.')[-1].lower()
        
        if file_extension == 'pdf':
            return self.extract_text_from_pdf(uploaded_file)
        elif file_extension == 'docx':
            return self.extract_text_from_docx(uploaded_file)
        elif file_extension == 'txt':
            return self.extract_text_from_txt(uploaded_file)
        else:
            raise Exception(f"Unsupported file type: {file_extension}")
    
    def chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        text_length = len(text)
        
        while start < text_length:
            end = min(start + CHUNK_SIZE, text_length)
            
            # Try to end at a sentence boundary
            if end < text_length:
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + CHUNK_SIZE - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - CHUNK_OVERLAP if end < text_length else end
        
        return chunks
    
    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate embeddings for text chunks"""
        try:
            embeddings = self.embedding_model.encode(chunks)
            return embeddings.tolist()
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    def process_document(self, uploaded_file) -> Dict[str, Any]:
        """Process uploaded document and return chunks with embeddings"""
        try:
            # Extract text
            text = self.extract_text(uploaded_file)
            
            # Split into chunks
            chunks = self.chunk_text(text)
            
            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)
            
            return {
                'filename': uploaded_file.name,
                'text': text,
                'chunks': chunks,
                'embeddings': embeddings,
                'num_chunks': len(chunks)
            }
        except Exception as e:
            raise Exception(f"Error processing document: {str(e)}")
