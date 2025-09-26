"""
PDF reading functionality using PyPDF2.
"""
import os
from typing import List, Dict, Any
from pathlib import Path
import PyPDF2
from config import settings


class PDFReader:
    """Handles reading PDF files from a directory."""
    
    def __init__(self, folder_path: str = None):
        """Initialize PDF reader with folder path."""
        self.folder_path = Path(folder_path or settings.pdf_folder_path)
        
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files from the configured folder."""
        if not self.folder_path.exists():
            raise FileNotFoundError(f"PDF folder not found: {self.folder_path}")
            
        pdf_files = list(self.folder_path.glob("*.pdf"))
        if not pdf_files:
            raise FileNotFoundError(f"No PDF files found in: {self.folder_path}")
            
        return pdf_files
    
    def read_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """Read a single PDF file and extract text."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}"
                
                return {
                    "file_path": str(pdf_path),
                    "file_name": pdf_path.name,
                    "total_pages": len(pdf_reader.pages),
                    "text_content": text_content.strip(),
                    "metadata": {
                        "title": pdf_reader.metadata.get("/Title", "") if pdf_reader.metadata else "",
                        "author": pdf_reader.metadata.get("/Author", "") if pdf_reader.metadata else "",
                        "creator": pdf_reader.metadata.get("/Creator", "") if pdf_reader.metadata else "",
                        "creation_date": str(pdf_reader.metadata.get("/CreationDate", "")) if pdf_reader.metadata else "",
                    }
                }
                
        except Exception as e:
            raise Exception(f"Error reading PDF {pdf_path}: {str(e)}")
    
    def read_all_pdfs(self) -> List[Dict[str, Any]]:
        """Read all PDF files from the configured folder."""
        pdf_files = self.get_pdf_files()
        pdf_data = []
        
        for pdf_file in pdf_files:
            try:
                pdf_content = self.read_pdf(pdf_file)
                pdf_data.append(pdf_content)
                print(f"Successfully read: {pdf_file.name}")
            except Exception as e:
                print(f"Error reading {pdf_file.name}: {str(e)}")
                continue
                
        return pdf_data
