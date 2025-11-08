import logging
from typing import List, Dict, Any
import PyPDF2
import docx
from sentence_transformers import SentenceTransformer
from config import EMBEDDING_MODEL, CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


class DocumentProcessor:

    def __init__(self):
        try:
            logger.info(f"Initializing DocumentProcessor with model: {EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
            logger.info("DocumentProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize DocumentProcessor: {str(e)}")
            raise RuntimeError(f"Failed to initialize embedding model: {str(e)}")

    def _validate_file(self, file_obj) -> bool:
        if file_obj is None:
            raise ValueError("File object cannot be None")

        if not hasattr(file_obj, "name"):
            raise ValueError("Invalid file object: missing 'name' attribute")

        file_name = file_obj.name
        if not file_name or not isinstance(file_name, str):
            raise ValueError("File name must be a non-empty string")

        file_extension = file_name.split(".")[-1].lower()
        supported_extensions = ["pdf", "docx", "txt"]
        if file_extension not in supported_extensions:
            raise ValueError(
                f"Unsupported file type: {file_extension}. Supported types: {', '.join(supported_extensions)}"
            )

        return True

    def extract_text_from_pdf(self, pdf_file) -> str:
        try:
            logger.info(f"Extracting text from PDF: {pdf_file.name}")
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            if len(pdf_reader.pages) == 0:
                raise ValueError("PDF file is empty or has no pages")

            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(
                        f"Error extracting text from page {page_num}: {str(e)}"
                    )
                    continue

            if not text.strip():
                raise ValueError("No text could be extracted from the PDF")

            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text

        except PyPDF2.errors.PdfReadError as e:
            logger.error(f"Invalid or corrupted PDF file: {str(e)}")
            raise ValueError(f"Invalid or corrupted PDF file: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise RuntimeError(f"Error extracting text from PDF: {str(e)}")

    def extract_text_from_docx(self, docx_file) -> str:
        try:
            logger.info(f"Extracting text from DOCX: {docx_file.name}")
            doc = docx.Document(docx_file)

            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text:
                    text += paragraph.text + "\n"

            if not text.strip():
                raise ValueError("No text could be extracted from the DOCX file")

            logger.info(f"Successfully extracted {len(text)} characters from DOCX")
            return text

        except docx.opc.exceptions.PackageNotFoundError as e:
            logger.error(f"Invalid DOCX file format: {str(e)}")
            raise ValueError(f"Invalid DOCX file format: {str(e)}")
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            raise RuntimeError(f"Error extracting text from DOCX: {str(e)}")

    def extract_text_from_txt(self, txt_file) -> str:
        try:
            logger.info(f"Extracting text from TXT: {txt_file.name}")
            content = txt_file.read()
            if isinstance(content, bytes):
                try:
                    content = content.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        content = content.decode("latin-1")
                    except Exception:
                        raise ValueError(
                            "Unable to decode text file. Unsupported encoding."
                        )

            if not content.strip():
                raise ValueError("Text file is empty")

            logger.info(f"Successfully extracted {len(content)} characters from TXT")
            return content

        except Exception as e:
            logger.error(f"Error extracting text from TXT: {str(e)}")
            raise RuntimeError(f"Error extracting text from TXT: {str(e)}")

    def extract_text(self, uploaded_file) -> str:
        try:
            self._validate_file(uploaded_file)
            file_extension = uploaded_file.name.split(".")[-1].lower()

            if file_extension == "pdf":
                return self.extract_text_from_pdf(uploaded_file)
            elif file_extension == "docx":
                return self.extract_text_from_docx(uploaded_file)
            elif file_extension == "txt":
                return self.extract_text_from_txt(uploaded_file)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")

        except ValueError as e:
            logger.error(f"Validation error during text extraction: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during text extraction: {str(e)}")
            raise

    def _validate_chunk_params(self):
        if CHUNK_SIZE <= 0:
            raise ValueError("CHUNK_SIZE must be a positive integer")
        if CHUNK_OVERLAP < 0:
            raise ValueError("CHUNK_OVERLAP cannot be negative")
        if CHUNK_OVERLAP >= CHUNK_SIZE:
            raise ValueError("CHUNK_OVERLAP must be less than CHUNK_SIZE")

    def chunk_text(self, text: str) -> List[str]:
        try:
            if not text or not isinstance(text, str):
                raise ValueError("Text must be a non-empty string")

            if not text.strip():
                raise ValueError("Text cannot be empty or whitespace only")

            self._validate_chunk_params()

            logger.info(
                f"Chunking text of length {len(text)} with chunk_size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}"
            )

            chunks = []
            start = 0
            text_length = len(text)

            while start < text_length:
                end = min(start + CHUNK_SIZE, text_length)

                if end < text_length:
                    for i in range(end, max(start + CHUNK_SIZE - 100, start), -1):
                        if i < len(text) and text[i] in ".!?":
                            end = i + 1
                            break

                chunk = text[start:end].strip()
                if chunk:
                    chunks.append(chunk)

                start = end - CHUNK_OVERLAP if end < text_length else end

            if not chunks:
                raise ValueError("Failed to create any chunks from the text")

            logger.info(f"Created {len(chunks)} chunks")
            return chunks

        except ValueError as e:
            logger.error(f"Validation error during text chunking: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during text chunking: {str(e)}")
            raise

    def generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        try:
            if not chunks or not isinstance(chunks, list):
                raise ValueError("Chunks must be a non-empty list")

            if len(chunks) == 0:
                raise ValueError("Cannot generate embeddings for empty chunk list")

            for i, chunk in enumerate(chunks):
                if not chunk or not isinstance(chunk, str) or not chunk.strip():
                    raise ValueError(
                        f"Invalid chunk at index {i}: must be a non-empty string"
                    )

            logger.info(f"Generating embeddings for {len(chunks)} chunks")
            embeddings = self.embedding_model.encode(chunks)

            if embeddings is None or len(embeddings) == 0:
                raise RuntimeError(
                    "Embedding generation failed: no embeddings returned"
                )

            embeddings_list = embeddings.tolist()
            logger.info(f"Successfully generated {len(embeddings_list)} embeddings")
            return embeddings_list

        except ValueError as e:
            logger.error(f"Validation error during embedding generation: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

    def process_document(self, uploaded_file) -> Dict[str, Any]:
        try:
            logger.info(f"Processing document: {uploaded_file.name}")

            text = self.extract_text(uploaded_file)

            chunks = self.chunk_text(text)

            embeddings = self.generate_embeddings(chunks)

            result = {
                "filename": uploaded_file.name,
                "text": text,
                "chunks": chunks,
                "embeddings": embeddings,
                "num_chunks": len(chunks),
            }

            logger.info(
                f"Successfully processed document: {uploaded_file.name} ({len(chunks)} chunks)"
            )
            return result

        except ValueError as e:
            logger.error(
                f"Validation error processing document {uploaded_file.name}: {str(e)}"
            )
            raise
        except RuntimeError as e:
            logger.error(
                f"Runtime error processing document {uploaded_file.name}: {str(e)}"
            )
            raise
        except Exception as e:
            logger.error(
                f"Unexpected error processing document {uploaded_file.name}: {str(e)}"
            )
            raise RuntimeError(f"Failed to process document: {str(e)}")
