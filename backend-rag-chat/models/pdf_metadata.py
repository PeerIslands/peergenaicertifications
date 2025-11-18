from pydantic import BaseModel
from typing import List
from datetime import datetime

class PDFMetadata(BaseModel):
    file_name: str
    file_size: int
    processed_time: datetime
    chunk_count: int

class DocumentResponse(BaseModel):
    message: str
    processed_files: List[PDFMetadata]
    total_chunks: int
