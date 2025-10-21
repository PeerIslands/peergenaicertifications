from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def embed_text(chunks):
    embeddings = []
    for chunk in chunks:
        resp = client.embeddings.create(
            input=chunk,
            model="text-embedding-3-small"
        )
        embeddings.append(resp.data[0].embedding)
    return embeddings
