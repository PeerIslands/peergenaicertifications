from typing import List, Dict, Optional
from datetime import datetime
import json

class ConversationMemory:
    def __init__(self):
        # In-memory storage for conversation history
        # In production, this should be stored in a database
        self.conversations: Dict[str, List[Dict]] = {}
    
    def add_message(self, session_id: str, role: str, content: str, sources: List[str] = None):
        """Add a message to the conversation history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        message = {
            "role": role,  # "user" or "assistant"
            "content": content,
            "sources": sources or [],
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversations[session_id].append(message)
        
        # Keep only last 10 messages to prevent context from getting too long
        if len(self.conversations[session_id]) > 10:
            self.conversations[session_id] = self.conversations[session_id][-10:]
    
    def get_conversation_history(self, session_id: str, max_messages: int = 5) -> List[Dict]:
        """Get recent conversation history for context"""
        if session_id not in self.conversations:
            return []
        
        # Return last max_messages messages
        return self.conversations[session_id][-max_messages:]
    
    def get_conversation_context(self, session_id: str) -> str:
        """Get formatted conversation context for the LLM"""
        history = self.get_conversation_history(session_id, max_messages=4)
        
        if not history:
            return ""
        
        context_parts = []
        for message in history:
            role = message["role"]
            content = message["content"]
            context_parts.append(f"{role.capitalize()}: {content}")
        
        return "\n".join(context_parts)
    
    def clear_conversation(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]

# Global instance
conversation_memory = ConversationMemory()
