import os
import uuid
from typing import List, Dict
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from config import settings

class FileProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
        )
        self.files_directory = Path(__file__).parent.parent.parent / "files"
    
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files from the files directory"""
        if not self.files_directory.exists():
            return []
        
        pdf_files = self.files_directory.glob("*.pdf")
        return sorted(pdf_files)  # Sort for consistent ordering
    
    def process_pdf_file(self, file_path: Path) -> Dict:
        """Process a single PDF file and return chunks with metadata"""
        try:
            # Load PDF using PyPDF
            loader = PyPDFLoader(str(file_path))
            documents = loader.load()
            
            # Split documents into chunks
            chunks = self.text_splitter.split_documents(documents)
            
            # Generate document ID
            doc_id = str(uuid.uuid4())
            
            # Prepare chunks with metadata
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "doc_id": doc_id,
                    "file_name": file_path.name,
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "content": chunk.page_content,
                    "metadata": chunk.metadata,
                    "chunk_index": i
                }
                processed_chunks.append(chunk_data)
            
            return {
                "doc_id": doc_id,
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
                "chunks": processed_chunks,
                "chunk_count": len(processed_chunks)
            }
            
        except Exception as e:
            print(f"Error processing file {file_path.name}: {str(e)}")
            return {
                "doc_id": "",
                "file_name": file_path.name,
                "file_size": 0,
                "chunks": [],
                "chunk_count": 0
            }
    
    def process_all_files(self) -> List[Dict]:
        """Process all PDF files in the files directory"""
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print("No PDF files found in the files directory")
            return []
        
        results = []
        for file_path in pdf_files:
            print(f"Processing file: {file_path.name}")
            result = self.process_pdf_file(file_path)
            if result:
                results.append(result)
                print(f"Successfully processed {file_path.name} - {result['chunk_count']} chunks")
            else:
                print(f"Failed to process {file_path.name}")
        
        return results
