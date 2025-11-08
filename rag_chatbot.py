import logging
from typing import List, Dict, Any
import openai
from sentence_transformers import SentenceTransformer
from mongodb_client import MongoDBClient
from config import OPENAI_API_KEY, EMBEDDING_MODEL

logger = logging.getLogger(__name__)


class RAGChatbot:

    def __init__(self):
        try:
            if not OPENAI_API_KEY:
                raise ValueError(
                    "OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables."
                )

            logger.info("Initializing RAG Chatbot")
            self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)

            self.mongodb_client = MongoDBClient()

            self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents.

Guidelines:
1. Use the provided context to answer questions accurately
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Don't make up information that's not in the context
4. Be concise but comprehensive in your answers
5. If asked about something not in the context, explain that you can only answer based on the uploaded documents

Context will be provided with each question."""

            logger.info("RAG Chatbot initialized successfully")

        except ValueError as e:
            logger.error(f"Configuration error initializing RAG Chatbot: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error initializing RAG Chatbot: {str(e)}")
            raise RuntimeError(f"Failed to initialize RAG Chatbot: {str(e)}")

    def _validate_query(self, query: str) -> bool:
        if not query or not isinstance(query, str):
            raise ValueError("Query must be a non-empty string")

        if not query.strip():
            raise ValueError("Query cannot be empty or whitespace only")

        if len(query.strip()) < 3:
            raise ValueError("Query is too short. Please provide at least 3 characters")

        if len(query) > 5000:
            raise ValueError("Query is too long. Please limit to 5000 characters")

        return True

    def generate_query_embedding(self, query: str) -> List[float]:
        try:
            self._validate_query(query)

            logger.info(f"Generating embedding for query: {query[:100]}...")
            embedding = self.embedding_model.encode([query])

            if embedding is None or len(embedding) == 0:
                raise RuntimeError("Failed to generate query embedding")

            result = embedding[0].tolist()
            logger.info("Query embedding generated successfully")
            return result

        except ValueError as e:
            logger.error(f"Validation error generating query embedding: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise RuntimeError(f"Failed to generate query embedding: {str(e)}")

    def retrieve_relevant_context(
        self, query: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        try:
            self._validate_query(query)

            if top_k <= 0:
                raise ValueError("top_k must be a positive integer")

            if top_k > 100:
                logger.warning(f"top_k value {top_k} is very large. Using 100 instead.")
                top_k = 100

            logger.info(f"Retrieving relevant context for query (top_k={top_k})")

            query_embedding = self.generate_query_embedding(query)

            relevant_chunks = self.mongodb_client.similarity_search(
                query_embedding, top_k
            )

            logger.info(f"Retrieved {len(relevant_chunks)} relevant chunks")
            return relevant_chunks

        except ValueError as e:
            logger.error(f"Validation error retrieving context: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving relevant context: {str(e)}")
            raise RuntimeError(f"Failed to retrieve context: {str(e)}")

    def format_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        try:
            if not isinstance(relevant_chunks, list):
                raise ValueError("relevant_chunks must be a list")

            if not relevant_chunks:
                logger.warning("No relevant context found")
                return "No relevant context found in the uploaded documents."

            context_parts = []
            for i, chunk in enumerate(relevant_chunks, 1):
                if not isinstance(chunk, dict):
                    logger.warning(f"Invalid chunk at index {i-1}: not a dictionary")
                    continue

                filename = chunk.get("filename", "Unknown")
                similarity = chunk.get("similarity", 0.0)
                text = chunk.get("text", "")

                context_parts.append(f"Document: {filename}")
                context_parts.append(f"Relevance Score: {similarity:.3f}")
                context_parts.append(f"Content: {text}")
                context_parts.append("-" * 50)

            result = "\n".join(context_parts)
            logger.info(f"Formatted context with {len(relevant_chunks)} chunks")
            return result

        except Exception as e:
            logger.error(f"Error formatting context: {str(e)}")
            raise RuntimeError(f"Failed to format context: {str(e)}")

    def generate_response(self, query: str, context: str) -> str:
        try:
            self._validate_query(query)

            if not context or not isinstance(context, str):
                raise ValueError("Context must be a non-empty string")

            logger.info("Generating response using OpenAI")

            messages = [
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"Context:\n{context}\n\nQuestion: {query}",
                },
            ]

            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
            )

            if not response or not response.choices:
                raise RuntimeError("OpenAI returned empty response")

            answer = response.choices[0].message.content.strip()

            if not answer:
                raise RuntimeError("OpenAI returned empty answer")

            logger.info("Response generated successfully")
            return answer

        except ValueError as e:
            logger.error(f"Validation error generating response: {str(e)}")
            raise
        except openai.RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            raise RuntimeError("Rate limit exceeded. Please try again later.")
        except openai.APIConnectionError as e:
            logger.error(f"OpenAI connection error: {str(e)}")
            raise RuntimeError(
                "Failed to connect to OpenAI. Please check your internet connection."
            )
        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise RuntimeError(f"Failed to generate response: {str(e)}")

    def chat(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        try:
            self._validate_query(query)

            logger.info(f"Processing chat query: {query[:100]}...")

            relevant_chunks = self.retrieve_relevant_context(query, top_k)

            context = self.format_context(relevant_chunks)

            response = self.generate_response(query, context)

            result = {
                "query": query,
                "response": response,
                "context_used": relevant_chunks,
                "num_sources": len(relevant_chunks),
            }

            logger.info(
                f"Chat query processed successfully with {len(relevant_chunks)} sources"
            )
            return result

        except ValueError as e:
            logger.error(f"Validation error in chat: {str(e)}")
            return {
                "query": query,
                "response": f"Invalid input: {str(e)}",
                "context_used": [],
                "num_sources": 0,
            }
        except RuntimeError as e:
            logger.error(f"Runtime error in chat: {str(e)}")
            return {
                "query": query,
                "response": f"Error processing your question: {str(e)}",
                "context_used": [],
                "num_sources": 0,
            }
        except Exception as e:
            logger.error(f"Unexpected error in chat: {str(e)}")
            return {
                "query": query,
                "response": f"An unexpected error occurred: {str(e)}",
                "context_used": [],
                "num_sources": 0,
            }

    def get_conversation_starter(self) -> str:
        try:
            documents = self.mongodb_client.get_all_documents()
            if not documents:
                logger.info("No documents found for conversation starter")
                return "Hi! Please upload some documents first, then I'll be able to answer questions based on their content."

            doc_list = ", ".join([doc["filename"] for doc in documents[:3]])
            if len(documents) > 3:
                doc_list += f" and {len(documents) - 3} more"

            logger.info(
                "Generated conversation starter for %d documents", len(documents)
            )
            return f"Hi! I can help you find information from your uploaded documents: {doc_list}. What would you like to know?"

        except Exception as e:
            logger.error(f"Error generating conversation starter: {str(e)}")
            return "Hi! I'm ready to help you with questions about your uploaded documents. What would you like to know?"
