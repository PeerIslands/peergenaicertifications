import requests
import json
from typing import List, Dict
from config import settings
from services.conversation_memory import conversation_memory

class RAGPipeline:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    async def generate_response(self, query: str, session_id: str = None) -> Dict:
        """Generate RAG response using retrieved chunks and LLaMA 3"""
        # Retrieve relevant chunks for context
        relevant_chunks = await self.vector_store.search_similar_chunks(query, top_k=3)
        
        if not relevant_chunks:
            return {
                "response": "I don't have any relevant information to answer your question. Please ensure documents are loaded from the files directory first.",
                "sources": []
            }
        
        # Build context from retrieved chunks
        context = self._build_context(relevant_chunks)
        
        # Get conversation context if session_id is provided
        conversation_context = ""
        if session_id:
            conversation_context = conversation_memory.get_conversation_context(session_id)
        
        # Create RAG prompt
        rag_prompt = self._create_rag_prompt(query, context, conversation_context)
        
        # Generate response using LLaMA 3
        response = await self._query_llama(rag_prompt)
        
        # Extract sources
        sources = list({chunk["file_name"] for chunk in relevant_chunks})
        
        return {
            "response": response,
            "sources": sources
        }
    
    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(f"Source {i} (from {chunk['file_name']}):\n{chunk['content']}\n")
        return "\n".join(context_parts)
    
    def _create_rag_prompt(self, query: str, context: str, conversation_context: str = "") -> str:
        """Create RAG prompt for LLaMA 3"""        
        # Build the prompt with conversation context if available
        if conversation_context:
            prompt = f"""Answer this question concisely based on the provided context and conversation history. Provide a direct answer to the question in 1-2 sentences. Do not start with phrases like "According to the context" or "Based on the provided context".

Conversation History:
{conversation_context}

Context: {context}

Question: {query}

Answer:"""
        else:
            prompt = f"""Answer this question concisely based on the provided context. Provide a direct answer to the question in 1-2 sentences. Do not start with phrases like "According to the context" or "Based on the provided context".

Context: {context}

Question: {query}

Answer:"""
        
        return prompt
    
    async def _query_llama(self, prompt: str) -> str:
        """Query LLaMA 3 model via Ollama API"""
        try:
            payload = {
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.8,        
                    "num_predict": 200,  
                    "stop": ["Question:", "Answer:", "Context:"]
                }
            }
            
            response = requests.post(
                settings.LLAMA_MODEL_ENDPOINT,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Sorry, I couldn't generate a response.")
            else:
                return f"Error: Unable to connect to LLaMA model (Status: {response.status_code})"
                
        except requests.exceptions.RequestException as e:
            return f"Error: Unable to connect to LLaMA model ({str(e)})"
        except Exception as e:
            return f"Error: {str(e)}"
