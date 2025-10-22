import logging
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure, PyMongoError
from bson import ObjectId
from config import (
    MONGODB_URI,
    MONGODB_DB_NAME,
    MONGODB_COLLECTION_NAME,
    MONGODB_POOL_SIZE,
    MONGODB_MAX_POOL_SIZE,
)

logger = logging.getLogger(__name__)


class MongoDBClient:

    _connection_pool = None

    def __init__(self):
        try:
            if not MONGODB_URI:
                raise ValueError(
                    "MongoDB URI is not configured. Please set MONGODB_URI environment variable."
                )

            if MongoDBClient._connection_pool is None:
                logger.info("Initializing MongoDB connection pool")
                MongoDBClient._connection_pool = MongoClient(
                    MONGODB_URI,
                    tlsCAFile=certifi.where(),
                    minPoolSize=MONGODB_POOL_SIZE,
                    maxPoolSize=MONGODB_MAX_POOL_SIZE,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=5000,
                )
                MongoDBClient._connection_pool.admin.command("ping")
                logger.info("MongoDB connection pool initialized successfully")

            self.client = MongoDBClient._connection_pool
            self.db = self.client[MONGODB_DB_NAME]
            self.collection = self.db[MONGODB_COLLECTION_NAME]

            self._ensure_indexes()

        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise ConnectionError(f"MongoDB connection failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error initializing MongoDB client: {str(e)}")
            raise

    def _ensure_indexes(self):
        try:
            existing_indexes = self.collection.list_indexes()
            index_names = [idx["name"] for idx in existing_indexes]

            if "filename_1" not in index_names:
                self.collection.create_index("filename")
                logger.info("Created index on 'filename' field")

            if "timestamp_1" not in index_names:
                self.collection.create_index("timestamp")
                logger.info("Created index on 'timestamp' field")

        except OperationFailure as e:
            logger.warning(f"Could not create indexes: {str(e)}")
        except Exception as e:
            logger.warning(f"Unexpected error while creating indexes: {str(e)}")

    def _validate_document_data(self, document_data: Dict[str, Any]) -> bool:
        required_fields = ["filename", "text", "chunks", "embeddings", "num_chunks"]
        for field in required_fields:
            if field not in document_data:
                raise ValueError(f"Missing required field: {field}")

        if (
            not isinstance(document_data["filename"], str)
            or not document_data["filename"].strip()
        ):
            raise ValueError("Filename must be a non-empty string")

        if (
            not isinstance(document_data["chunks"], list)
            or len(document_data["chunks"]) == 0
        ):
            raise ValueError("Chunks must be a non-empty list")

        if (
            not isinstance(document_data["embeddings"], list)
            or len(document_data["embeddings"]) == 0
        ):
            raise ValueError("Embeddings must be a non-empty list")

        if len(document_data["chunks"]) != len(document_data["embeddings"]):
            raise ValueError("Number of chunks must match number of embeddings")

        return True

    def store_document(self, document_data: Dict[str, Any]) -> str:
        try:
            self._validate_document_data(document_data)

            doc = {
                "filename": document_data["filename"],
                "text": document_data["text"],
                "chunks": [],
                "timestamp": datetime.now(),
                "num_chunks": document_data["num_chunks"],
            }

            for i, (chunk, embedding) in enumerate(
                zip(document_data["chunks"], document_data["embeddings"])
            ):
                chunk_doc = {"chunk_id": i, "text": chunk, "embedding": embedding}
                doc["chunks"].append(chunk_doc)

            result = self.collection.insert_one(doc)
            logger.info(
                f"Successfully stored document: {document_data['filename']} with ID: {result.inserted_id}"
            )
            return str(result.inserted_id)

        except ValueError as e:
            logger.error(f"Validation error while storing document: {str(e)}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error while storing document: {str(e)}")
            raise ConnectionError(f"Failed to store document in MongoDB: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error storing document: {str(e)}")
            raise

    def get_all_documents(self) -> List[Dict[str, Any]]:
        try:
            documents = []
            cursor = self.collection.find(
                {}, {"filename": 1, "timestamp": 1, "num_chunks": 1}
            )
            for doc in cursor:
                documents.append(
                    {
                        "id": str(doc["_id"]),
                        "filename": doc["filename"],
                        "timestamp": doc["timestamp"],
                        "num_chunks": doc["num_chunks"],
                    }
                )
            logger.info(f"Retrieved {len(documents)} documents")
            return documents
        except PyMongoError as e:
            logger.error(f"MongoDB error while retrieving documents: {str(e)}")
            raise ConnectionError(f"Failed to retrieve documents: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error retrieving documents: {str(e)}")
            raise

    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        try:
            if not vec1 or not vec2:
                raise ValueError("Vectors cannot be empty")

            if len(vec1) != len(vec2):
                raise ValueError(
                    f"Vector dimensions must match. Got {len(vec1)} and {len(vec2)}"
                )

            vec1 = np.array(vec1)
            vec2 = np.array(vec2)

            dot_product = np.dot(vec1, vec2)
            norm_vec1 = np.linalg.norm(vec1)
            norm_vec2 = np.linalg.norm(vec2)

            if norm_vec1 == 0 or norm_vec2 == 0:
                logger.warning(
                    "Zero vector encountered in cosine similarity calculation"
                )
                return 0

            return float(dot_product / (norm_vec1 * norm_vec2))

        except ValueError as e:
            logger.error(f"Validation error in cosine similarity: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            raise

    def similarity_search(
        self, query_embedding: List[float], top_k: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            if not query_embedding:
                raise ValueError("Query embedding cannot be empty")

            if top_k <= 0:
                raise ValueError("top_k must be a positive integer")

            results = []

            cursor = self.collection.find({})
            document_count = 0

            for doc in cursor:
                document_count += 1
                for chunk in doc.get("chunks", []):
                    try:
                        similarity = self.cosine_similarity(
                            query_embedding, chunk["embedding"]
                        )

                        results.append(
                            {
                                "document_id": str(doc["_id"]),
                                "filename": doc["filename"],
                                "chunk_id": chunk["chunk_id"],
                                "text": chunk["text"],
                                "similarity": similarity,
                            }
                        )
                    except Exception as e:
                        chunk_id = chunk.get("chunk_id")
                        filename = doc.get("filename")
                        logger.warning(
                            "Error processing chunk %s in document %s: %s",
                            chunk_id,
                            filename,
                            str(e),
                        )
                        continue

            results.sort(key=lambda x: x["similarity"], reverse=True)
            top_results = results[:top_k]
            logger.info(
                "Similarity search completed. Processed %d documents, returning top %d results",
                document_count,
                len(top_results),
            )
            return top_results

        except ValueError as e:
            logger.error(f"Validation error in similarity search: {str(e)}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error during similarity search: {str(e)}")
            raise ConnectionError(f"Failed to perform similarity search: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during similarity search: {str(e)}")
            raise

    def delete_document(self, document_id: str) -> bool:
        try:
            if not document_id or not isinstance(document_id, str):
                raise ValueError("Document ID must be a non-empty string")

            try:
                object_id = ObjectId(document_id)
            except Exception:
                raise ValueError(f"Invalid document ID format: {document_id}")

            result = self.collection.delete_one({"_id": object_id})
            deleted = result.deleted_count > 0
            logger.info(
                f"Delete document {document_id}: {'Success' if deleted else 'Not found'}"
            )
            return deleted

        except ValueError as e:
            logger.error(f"Validation error while deleting document: {str(e)}")
            raise
        except PyMongoError as e:
            logger.error(f"MongoDB error while deleting document: {str(e)}")
            raise ConnectionError(f"Failed to delete document: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {str(e)}")
            raise

    def clear_all_documents(self) -> int:
        try:
            result = self.collection.delete_many({})
            deleted_count = result.deleted_count
            logger.info(f"Cleared all documents. Deleted {deleted_count} documents")
            return deleted_count
        except PyMongoError as e:
            logger.error(f"MongoDB error while clearing documents: {str(e)}")
            raise ConnectionError(f"Failed to clear documents: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error clearing documents: {str(e)}")
            raise

    def close_connection(self):
        logger.debug(
            "Connection pooling enabled - connection will remain open for reuse"
        )

    @classmethod
    def close_all_connections(cls):
        if cls._connection_pool is not None:
            try:
                cls._connection_pool.close()
                cls._connection_pool = None
                logger.info("MongoDB connection pool closed")
            except Exception as e:
                logger.error(f"Error closing MongoDB connection pool: {str(e)}")
