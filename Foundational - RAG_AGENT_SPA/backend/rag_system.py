import os
import logging
from typing import List, Dict, Any
import openai
from langchain_core.documents import Document
import json

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self):
        """Initialize the RAG system with OpenAI"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.openai_api_key)

        # Simple document storage
        self.documents = []

        logger.info("RAG system initialized successfully")

    def add_documents(self, documents: List[Document]):
        """Add documents to the system"""
        try:
            self.documents.extend(documents)
            logger.info(f"Added {len(documents)} documents to system")
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise

    def query(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """Query the RAG system with a question"""
        try:
            if not self.documents:
                raise ValueError("No documents available. Please upload documents first.")

            # Create context from documents
            context = ""
            sources = []

            for doc in self.documents[:max_results]:
                context += doc.page_content + "\n\n"
                if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                    sources.append(doc.metadata['source'])

            # Create prompt
            prompt = f"""
            Based on the following documents, answer the question: {question}

            Documents:
            {context}

            Answer:
            """

            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "sources": list(set(sources)),
                "confidence": 0.8
            }

        except Exception as e:
            logger.error(f"Error querying RAG system: {e}")
            raise

    def has_documents(self) -> bool:
        """Check if there are documents in the system"""
        return len(self.documents) > 0

    def get_document_count(self) -> int:
        """Get the number of documents in the system"""
        return len(self.documents)

    def clear_documents(self):
        """Clear all documents from the system"""
        self.documents = []
        logger.info("All documents cleared from system")