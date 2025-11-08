import pytest
from unittest.mock import MagicMock, patch, mock_open
import PyPDF2
import docx
from document_processor import DocumentProcessor


class TestDocumentProcessor:

    def test_document_processor_initialization(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        assert processor is not None
        assert processor.embedding_model is not None

    def test_validate_file_success(
        self, mock_env_vars, mock_sentence_transformer, sample_uploaded_file
    ):
        processor = DocumentProcessor()
        assert processor._validate_file(sample_uploaded_file) is True

    def test_validate_file_none(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        with pytest.raises(ValueError, match="File object cannot be None"):
            processor._validate_file(None)

    def test_validate_file_no_name(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        del mock_file.name
        with pytest.raises(ValueError, match="missing 'name' attribute"):
            processor._validate_file(mock_file)

    def test_validate_file_unsupported_type(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        mock_file.name = "test.xyz"
        with pytest.raises(ValueError, match="Unsupported file type"):
            processor._validate_file(mock_file)

    def test_extract_text_from_txt_success(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        mock_file.name = "test.txt"
        mock_file.read.return_value = b"Test content"

        text = processor.extract_text_from_txt(mock_file)
        assert text == "Test content"

    def test_extract_text_from_txt_empty(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        mock_file.name = "test.txt"
        mock_file.read.return_value = b""

        with pytest.raises(RuntimeError, match="Error extracting text from TXT"):
            processor.extract_text_from_txt(mock_file)

    def test_extract_text_from_pdf_success(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()

        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test PDF content"

        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]

        mock_file = MagicMock()
        mock_file.name = "test.pdf"

        with patch("PyPDF2.PdfReader", return_value=mock_reader):
            text = processor.extract_text_from_pdf(mock_file)
            assert "Test PDF content" in text

    def test_extract_text_from_pdf_empty(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()

        mock_reader = MagicMock()
        mock_reader.pages = []

        mock_file = MagicMock()
        mock_file.name = "test.pdf"

        with patch("PyPDF2.PdfReader", return_value=mock_reader):
            with pytest.raises(RuntimeError, match="Error extracting text from PDF"):
                processor.extract_text_from_pdf(mock_file)

    def test_extract_text_from_docx_success(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()

        mock_paragraph = MagicMock()
        mock_paragraph.text = "Test DOCX content"

        mock_doc = MagicMock()
        mock_doc.paragraphs = [mock_paragraph]

        mock_file = MagicMock()
        mock_file.name = "test.docx"

        with patch("docx.Document", return_value=mock_doc):
            text = processor.extract_text_from_docx(mock_file)
            assert "Test DOCX content" in text

    def test_chunk_text_success(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        text = "This is a test. " * 100
        chunks = processor.chunk_text(text)
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)

    def test_chunk_text_empty(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        with pytest.raises(ValueError, match="Text must be a non-empty string"):
            processor.chunk_text("")

    def test_chunk_text_whitespace_only(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        with pytest.raises(ValueError, match="Text cannot be empty or whitespace only"):
            processor.chunk_text("   ")

    def test_generate_embeddings_success(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        chunks = ["This is a test chunk."]
        embeddings = processor.generate_embeddings(chunks)
        assert len(embeddings) == len(chunks)
        assert isinstance(embeddings[0], list)

    def test_generate_embeddings_empty_list(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        with pytest.raises(ValueError, match="Chunks must be a non-empty list"):
            processor.generate_embeddings([])

    def test_generate_embeddings_invalid_chunk(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        with pytest.raises(ValueError, match="Invalid chunk"):
            processor.generate_embeddings(["valid chunk", ""])

    def test_process_document_success(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        mock_file.name = "test.txt"
        mock_file.read.return_value = (
            b"This is a test document with enough content to create chunks."
        )

        result = processor.process_document(mock_file)
        assert "filename" in result
        assert "text" in result
        assert "chunks" in result
        assert "embeddings" in result
        assert "num_chunks" in result
        assert result["filename"] == "test.txt"

    def test_extract_text_unsupported_file_type(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        mock_file.name = "test.xyz"

        with pytest.raises(ValueError, match="Unsupported file type"):
            processor.extract_text(mock_file)

    def test_validate_chunk_params(self, mock_env_vars, mock_sentence_transformer):
        processor = DocumentProcessor()
        processor._validate_chunk_params()

    def test_extract_text_from_txt_unicode_decode_error(
        self, mock_env_vars, mock_sentence_transformer
    ):
        processor = DocumentProcessor()
        mock_file = MagicMock()
        mock_file.name = "test.txt"
        mock_file.read.return_value = b"Valid content"

        text = processor.extract_text_from_txt(mock_file)
        assert text == "Valid content"
