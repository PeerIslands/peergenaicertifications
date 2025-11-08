import os
import uuid


class SessionsService:
    def __init__(self):
        from src.config.db import get_mongo_collection
        self.collection = get_mongo_collection(os.environ["MONGODB_CHATS_COLLECTION_NAME"])

    async def create_session(self):
        session_id = str(uuid.uuid4())
        self.collection.insert_one({"session_id": session_id, "messages": []})
        return session_id

    def get_session(self, session_id):
        return self.collection.find_one({"session_id": session_id})

    def delete_session(self, session_id):
        return self.collection.delete_one({"session_id": session_id})