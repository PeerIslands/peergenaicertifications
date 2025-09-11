import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor

from src.config.db import vector_store, get_mongo_collection
from src.config.llm import get_embedding_model , get_llm_model
from src.utils.document_loader import load_pdf
from src.utils.splitter import text_split
import tempfile


def _process_document_sync(file_path: str):
    """Synchronous document processing"""
    # Load PDF document
    documents = load_pdf(file_path)

    # Split documents into chunks
    docs_split = text_split(documents, chunk_size=1000, chunk_overlap=200)

    # load into vector store
    vector_store.add_documents(documents=docs_split)

    return vector_store


class ProcessFileService:
    def __init__(self):
        self.llm = get_llm_model()

        self.embeddings = get_embedding_model()

        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)

        self.file_collection = get_mongo_collection(os.environ["MONGODB_FILES_COLLECTION_NAME"])

    async def get_files(self):
        """Get all files from the collection"""
        return list(self.file_collection.find({}, {"_id": 0}))

    async def delete_file(self, file_id: str):
        """Delete a file entry from the collection"""
        result = self.file_collection.delete_one({"file_id": file_id})
        if result.deleted_count == 0:
            raise ValueError("File not found")
        return {"status": "deleted"}

    def create_file_entry(self, filename: str, size: int, uploaded_at: str):
        """Create a file entry in the collection"""
        file_entry = {
              "file_id": str(uuid.uuid4()),
              "filename": filename,
              "size": size,
              "uploaded_at": uploaded_at
            }
        self.file_collection.insert_one(file_entry)
        return file_entry

    async def process_document(self, filename: str, content: bytes) -> str:
        """Process a PDF document and create a vector store"""
        try:
            # Save content to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(content)
                tmp_file_path = tmp_file.name

            # Process document in thread pool
            loop = asyncio.get_event_loop()
            vector_store = await loop.run_in_executor(
                self.executor,
                _process_document_sync,
                tmp_file_path
            )

            # Create a entry in file collection for tracking
            self.create_file_entry(
                filename=filename,
                size=len(content),
                uploaded_at=str(asyncio.get_event_loop().time())
            )
            # Clean up temporary file
            os.unlink(tmp_file_path)

            return 'success'

        except Exception as e:
            raise e
