from fastapi import APIRouter
from services import news_scraper, chunker, embedder, retriever
from services.db import collection

router = APIRouter()

@router.get("/fetch")
def fetch_news():
    articles = news_scraper.fetch_today_news()
    total_chunks = 0
    for article in articles:
        text = article["summary"]
        chunks = chunker.chunk_text(text)
        embeddings = embedder.embed_text(chunks)

        docs = [
            {
                "title": article["title"],
                "link": article["link"],
                "chunk": c,
                "embedding": e
            }
            for c, e in zip(chunks, embeddings)
        ]
        if docs:
            collection.insert_many(docs)
            retriever.retriever_engine.add(embeddings, chunks)
            total_chunks += len(chunks)
    return {"status": "success", "articles_fetched": len(articles), "chunks_stored": total_chunks}
