import openai
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from mongodb_client import MongoDBClient
from config import OPENAI_API_KEY, EMBEDDING_MODEL

class RAGChatbot:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
        
        # Initialize OpenAI client
        self.openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Initialize MongoDB client
        self.mongodb_client = MongoDBClient()
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful AI assistant that answers questions based on the provided context from documents. 
        
Guidelines:
1. Use the provided context to answer questions accurately
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Don't make up information that's not in the context
4. Be concise but comprehensive in your answers
5. If asked about something not in the context, explain that you can only answer based on the uploaded documents

Context will be provided with each question."""
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for user query"""
        try:
            embedding = self.embedding_model.encode([query])
            return embedding[0].tolist()
        except Exception as e:
            raise Exception(f"Error generating query embedding: {str(e)}")
    
    def retrieve_relevant_context(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context from MongoDB based on query"""
        try:
            # Generate query embedding
            query_embedding = self.generate_query_embedding(query)
            
            # Perform similarity search
            relevant_chunks = self.mongodb_client.similarity_search(query_embedding, top_k)
            
            return relevant_chunks
        except Exception as e:
            raise Exception(f"Error retrieving relevant context: {str(e)}")
    
    def format_context(self, relevant_chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context string"""
        if not relevant_chunks:
            return "No relevant context found in the uploaded documents."
        
        context_parts = []
        for i, chunk in enumerate(relevant_chunks, 1):
            context_parts.append(f"Document: {chunk['filename']}")
            context_parts.append(f"Relevance Score: {chunk['similarity']:.3f}")
            context_parts.append(f"Content: {chunk['text']}")
            context_parts.append("-" * 50)
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using OpenAI GPT with context"""
        try:
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
    
    def chat(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Main chat function that combines retrieval and generation"""
        try:
            # Retrieve relevant context
            relevant_chunks = self.retrieve_relevant_context(query, top_k)
            
            # Format context
            context = self.format_context(relevant_chunks)
            
            # Generate response
            response = self.generate_response(query, context)
            
            return {
                'query': query,
                'response': response,
                'context_used': relevant_chunks,
                'num_sources': len(relevant_chunks)
            }
        except Exception as e:
            return {
                'query': query,
                'response': f"Error processing your question: {str(e)}",
                'context_used': [],
                'num_sources': 0
            }
    
    def get_conversation_starter(self) -> str:
        """Get a conversation starter message"""
        try:
            documents = self.mongodb_client.get_all_documents()
            if not documents:
                return "Hi! Please upload some documents first, then I'll be able to answer questions based on their content."
            
            doc_list = ", ".join([doc['filename'] for doc in documents[:3]])
            if len(documents) > 3:
                doc_list += f" and {len(documents) - 3} more"
            
            return f"Hi! I can help you find information from your uploaded documents: {doc_list}. What would you like to know?"
        except Exception as e:
            return "Hi! I'm ready to help you with questions about your uploaded documents. What would you like to know?"
