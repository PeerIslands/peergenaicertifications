import os
from datetime import datetime

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.config.db import get_mongo_collection, get_vector_store,get_retriever
from src.config.llm import get_llm_model
from src.prompts.template import prompt

import langchain
langchain.debug = True

def format_docs(docs):
    print(len(docs))
    for d in docs:
        print("---")
        print(d)
        print("---")
    return "\n\n".join([d.page_content if hasattr(d, "page_content") else d["text"] for d in docs])


class ChatService:
    def __init__(self):
        self.collection = get_mongo_collection(os.environ["MONGODB_CHATS_COLLECTION_NAME"])
        self.vector_store = get_vector_store()
        self.retriever = get_retriever()
        self.model = get_llm_model()

    async def chat(self, session_id, message, role="user"):
        if not session_id:
            raise ValueError("Session ID is required")
        if not message.strip():
            raise ValueError("Message cannot be empty")

        # Save user message
        self.save_message(session_id, message, role)

        # Load history
        raw_history = await self.get_messages(session_id)
        history_str = "\n".join([f"{m['role']}: {m['content']}" for m in raw_history])

        # Construct chain
        chain = (
                {
                    "context": lambda x: format_docs(self.retriever.get_relevant_documents(x["question"])),
                    "question": RunnablePassthrough(),
                    "history": lambda x: history_str
                }
                | prompt
                | self.model
                | StrOutputParser()
        )

        input_data = {
            "question": message,
        }

        # Async invoke
        answer = await chain.ainvoke(input_data)

        # Save assistant response
        self.save_message(session_id, answer, "ai")

        return answer

    def save_message(self, session_id, message,role="user"):
        user_message = {
            "role": role,
            "content": message,
            "timestamp" : datetime.now()
        }
        self.collection.update_one(
            {"session_id": session_id},
            {"$push": {"messages": user_message}}
        )
        return user_message

    async def get_messages(self, session_id):
        session = self.collection.find_one({"session_id": session_id})
        if session:
            return session.get("messages", [])
        return []