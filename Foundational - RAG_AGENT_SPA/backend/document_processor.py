import os
import logging
from typing import List
import PyPDF2
from langchain.schema import Document

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        """Initialize the document processor"""
        pass

    def process_pdf(self, file_path: str) -> List[Document]:
        """Process a PDF file and extract text content"""
        try:
            documents = []

            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        text = page.extract_text()

                        if text.strip():  # Only add non-empty pages
                            doc = Document(
                                page_content=text,
                                metadata={
                                    "source": file_path,
                                    "page": page_num + 1,
                                    "total_pages": len(pdf_reader.pages)
                                }
                            )
                            documents.append(doc)

                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                        continue

            logger.info(f"Processed {len(documents)} pages from {file_path}")
            return documents

        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            raise

    def process_text_file(self, file_path: str) -> List[Document]:
        """Process a text file and extract content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            doc = Document(
                page_content=content,
                metadata={
                    "source": file_path,
                    "type": "text_file"
                }
            )

            logger.info(f"Processed text file {file_path}")
            return [doc]

        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            raise