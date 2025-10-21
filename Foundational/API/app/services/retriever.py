import faiss
import numpy as np
from services.db import collection

class Retriever:
    def __init__(self):
        self.index = None
        self.texts = []

    def add(self, embeddings, chunks):
        if not embeddings:
            return
        vectors = np.array(embeddings).astype("float32")
        if self.index is None:
            self.index = faiss.IndexFlatL2(vectors.shape[1])
        self.index.add(vectors)
        self.texts.extend(chunks)

    def load_from_mongo(self):
        docs = list(collection.find({}))
        if docs:
            chunks = [d["chunk"] for d in docs]
            embeddings = [np.array(d["embedding"], dtype="float32") for d in docs]
            self.add(embeddings, chunks)

    def search(self, query_emb, k=3):
        if self.index is None or len(self.texts) == 0:
            return []
        D, I = self.index.search(np.array([query_emb]).astype("float32"), k)
        return [self.texts[i] for i in I[0] if i < len(self.texts)]

# global instance
retriever_engine = Retriever()
retriever_engine.load_from_mongo()
