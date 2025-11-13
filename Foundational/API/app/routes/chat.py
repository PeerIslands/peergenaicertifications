from fastapi import APIRouter
from pydantic import BaseModel
from services import embedder, retriever
from openai import OpenAI
import os

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ChatRequest(BaseModel):
    query: str

@router.post("/")
async def chat(req: ChatRequest):
    # Embed the query
    query_emb = embedder.embed_text([req.query])[0]

    # Retrieve top chunks
    top_chunks = retriever.retriever_engine.search(query_emb, k=3)
    context = "\n".join(top_chunks) if top_chunks else "No context found."

    # Generate answer
    prompt = f"Answer the question based on the context below:\n\nContext: {context}\n\nQuestion: {req.query}\n\nAnswer:"
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    answer = completion.choices[0].message.content.strip()
    return {"answer": answer, "retrieved_chunks": len(top_chunks)}
