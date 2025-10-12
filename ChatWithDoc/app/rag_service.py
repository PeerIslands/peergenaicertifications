from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain_core.prompts import PromptTemplate
from chromadb.config import Settings as ChromaSettings

from .config import settings

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RagError(Exception):
    pass


@dataclass
class IngestResult:
    file_path: str
    num_pages: int
    num_chunks: int
    success: bool = True
    error_message: Optional[str] = None


def get_embeddings():
    """Get embeddings with validation"""
    if settings.openai_api_key:
        logger.info(f"Using OpenAI embeddings: {settings.openai_embedding_model}")
        return OpenAIEmbeddings(model=settings.openai_embedding_model)
    raise RagError("No embedding provider configured. Set OPENAI_API_KEY.")


def _collection_name_for_current_provider() -> str:
    """Get collection name - must be consistent across operations"""
    collection = f"docs_openai_{settings.openai_embedding_model}"
    logger.info(f"Using collection: {collection}")
    return collection


def get_vector_store(persist_directory: Optional[str] = None) -> Chroma:
    """Get vector store with validation"""
    persist_directory = persist_directory or settings.chroma_dir
    embeddings = get_embeddings()
    collection_name = _collection_name_for_current_provider()
    
    # Ensure directory exists
    Path(persist_directory).mkdir(parents=True, exist_ok=True)
    
    client_settings = ChromaSettings(
        anonymized_telemetry=False,
        persist_directory=persist_directory,
    )
    
    vectordb = Chroma(
        embedding_function=embeddings,
        collection_name=collection_name,
        client_settings=client_settings,
        persist_directory=persist_directory,
    )
    
    # Log collection stats
    try:
        if hasattr(vectordb, "_collection") and vectordb._collection:
            count = vectordb._collection.count()
            logger.info(f"Vector store connected. Documents in collection: {count}")
        else:
            logger.warning("Could not determine collection count")
    except Exception as e:
        logger.warning(f"Could not get collection count: {str(e)}")
    
    return vectordb


def load_pdf_documents(pdf_path: str) -> List[Document]:
    """Load PDF with comprehensive error handling"""
    try:
        # Validate file exists
        if not Path(pdf_path).exists():
            raise RagError(f"PDF file not found: {pdf_path}")
        
        # Validate file is not empty
        if Path(pdf_path).stat().st_size == 0:
            raise RagError(f"PDF file is empty: {pdf_path}")
        
        logger.info(f"Loading PDF: {pdf_path}")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load()
        
        if not pages:
            raise RagError(f"No pages extracted from PDF: {pdf_path}")
        
        logger.info(f"Loaded {len(pages)} pages from {pdf_path}")
        
        # Normalize metadata
        for i, p in enumerate(pages):
            # Handle different metadata formats
            page_num = p.metadata.get("page", p.metadata.get("page_number", i))
            p.metadata = {
                "source": Path(pdf_path).name,
                "page": int(page_num) if page_num is not None else i,
                "file_path": str(pdf_path),
            }
            
            # Validate page content
            if not p.page_content or not p.page_content.strip():
                logger.warning(f"Empty content on page {page_num} of {pdf_path}")
            else:
                logger.debug(f"Page {page_num}: {len(p.page_content)} characters")
        
        return pages
    
    except Exception as e:
        logger.error(f"Error loading PDF {pdf_path}: {str(e)}")
        raise RagError(f"Failed to load PDF {pdf_path}: {str(e)}")


def split_documents(documents: List[Document]) -> List[Document]:
    """Split documents with validation"""
    if not documents:
        return []
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Slightly larger chunks for better context
        chunk_overlap=200,  # More overlap to maintain continuity
        separators=["\n\n", "\n", ". ", ".", " "],
        length_function=len,
    )
    
    chunks = splitter.split_documents(documents)
    
    # Add chunk metadata and validate
    valid_chunks = []
    for idx, c in enumerate(chunks):
        if c.page_content and c.page_content.strip():
            c.metadata = {**c.metadata, "chunk_id": idx}
            valid_chunks.append(c)
        else:
            logger.warning(f"Skipping empty chunk {idx}")
    
    logger.info(f"Split {len(documents)} documents into {len(valid_chunks)} valid chunks")
    return valid_chunks


def ingest_pdfs(paths: Iterable[str]) -> List[IngestResult]:
    """Ingest PDFs with per-file error handling"""
    if not paths:
        return []
    
    vectordb = get_vector_store()
    results: List[IngestResult] = []
    total_chunks = 0
    
    for path in paths:
        try:
            logger.info(f"Processing: {path}")
            pages = load_pdf_documents(path)
            chunks = split_documents(pages)
            
            if not chunks:
                results.append(IngestResult(
                    file_path=str(path), 
                    num_pages=len(pages), 
                    num_chunks=0,
                    success=False,
                    error_message="No chunks created from document"
                ))
                continue
            
            # Add documents in batches
            batch_size = 100
            added_count = 0
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                try:
                    vectordb.add_documents(batch)
                    added_count += len(batch)
                    logger.info(f"Added batch {i//batch_size + 1}: {len(batch)} chunks")
                except Exception as e:
                    logger.error(f"Failed to add batch: {str(e)}")
                    raise
            
            # Persist (for older Chroma versions)
            try:
                vectordb.persist()
                logger.info("Vector store persisted")
            except AttributeError:
                logger.info("Persist not needed (newer Chroma version)")
            
            total_chunks += added_count
            
            results.append(IngestResult(
                file_path=str(path), 
                num_pages=len(pages), 
                num_chunks=added_count,
                success=True
            ))
            logger.info(f"✓ Successfully ingested: {path} ({added_count} chunks)")
            
        except Exception as e:
            logger.error(f"✗ Failed to ingest {path}: {str(e)}")
            results.append(IngestResult(
                file_path=str(path), 
                num_pages=0, 
                num_chunks=0,
                success=False,
                error_message=str(e)
            ))
    
    logger.info(f"Ingestion complete. Total chunks added: {total_chunks}")
    
    # Verify documents were added
    try:
        vectordb = get_vector_store()
        if hasattr(vectordb, "_collection") and vectordb._collection:
            final_count = vectordb._collection.count()
            logger.info(f"Final collection size: {final_count} documents")
    except Exception as e:
        logger.warning(f"Could not verify final count: {str(e)}")
    
    return results


def list_sources() -> List[str]:
    """List all unique sources in the vector store"""
    try:
        vectordb = get_vector_store()
        
        # Direct access to collection for more reliable results
        if hasattr(vectordb, "_collection") and vectordb._collection:
            collection = vectordb._collection
            # Get all documents (or a large sample)
            result = collection.get(limit=1000)
            metadatas = result.get("metadatas", [])
            sources = sorted({m.get("source", "unknown") for m in metadatas if m})
            logger.info(f"Found {len(sources)} unique sources from {len(metadatas)} documents")
            return sources
        else:
            # Fallback: use similarity search with a common word
            docs = vectordb.similarity_search("document", k=100)
            sources = sorted({d.metadata.get("source", "unknown") for d in docs})
            logger.info(f"Found {len(sources)} sources (fallback method)")
            return sources
            
    except Exception as e:
        logger.error(f"Error listing sources: {str(e)}")
        return []


def delete_source(source_file_name: str) -> int:
    """Delete all documents from a specific source"""
    try:
        vectordb = get_vector_store()
        where = {"source": source_file_name}
        
        if hasattr(vectordb, "_collection") and vectordb._collection is not None:
            collection = vectordb._collection
            items = collection.get(where=where)
            ids = items.get("ids", [])
            
            if ids:
                collection.delete(ids=ids)
                try:
                    vectordb.persist()
                except AttributeError:
                    pass
                logger.info(f"Deleted {len(ids)} chunks from {source_file_name}")
            else:
                logger.warning(f"No documents found for source: {source_file_name}")
            
            return len(ids)
        return 0
    except Exception as e:
        logger.error(f"Error deleting source {source_file_name}: {str(e)}")
        return 0


def query_documents(query: str, strategy: str = "similarity", k: int = 6) -> Tuple[str, List[Document]]:
    """
    Optimized query function that works for ALL scenarios.
    Simplified to use hybrid retrieval: MMR + similarity with higher k for multi-document queries.
    """
    if not query or not query.strip():
        raise RagError("Query must not be empty.")

    logger.info(f"=" * 80)
    logger.info(f"QUERY: {query}")
    logger.info(f"Parameters: k={k}")
    logger.info(f"=" * 80)
    
    # Verify collection has documents
    try:
        vectordb = get_vector_store()
        if hasattr(vectordb, "_collection") and vectordb._collection:
            doc_count = vectordb._collection.count()
            logger.info(f"Collection contains {doc_count} documents")
            if doc_count == 0:
                logger.error("Collection is empty!")
                return ("No documents have been uploaded yet. Please upload PDFs first.", [])
    except Exception as e:
        logger.error(f"Error checking collection: {str(e)}")
    
    # STEP 1: Get diverse candidates using MMR (better for multi-document queries)
    try:
        logger.info("Retrieving documents using MMR for diversity...")
        # Use higher fetch_k to ensure we get documents from multiple sources
        fetch_k = max(k * 4, 20)  # Fetch more candidates
        mmr_docs = vectordb.max_marginal_relevance_search(
            query, 
            k=k * 2,  # Get 2x documents initially
            fetch_k=fetch_k
        )
        logger.info(f"MMR retrieved {len(mmr_docs)} diverse documents from {fetch_k} candidates")
        
        # Log source diversity
        sources = {d.metadata.get('source', 'unknown') for d in mmr_docs}
        logger.info(f"Documents span {len(sources)} different sources: {sources}")
        
    except Exception as e:
        logger.error(f"MMR search failed: {str(e)}, falling back to similarity")
        mmr_docs = []
    
    # STEP 2: Also get top similarity matches (for relevance)
    try:
        logger.info("Retrieving documents using similarity search...")
        sim_docs_with_scores = vectordb.similarity_search_with_score(query, k=k * 2)
        sim_docs = [doc for doc, score in sim_docs_with_scores]
        logger.info(f"Similarity search retrieved {len(sim_docs)} documents")
        
        # Log top scores
        for i, (doc, score) in enumerate(sim_docs_with_scores[:3]):
            logger.info(f"  Top {i+1}: score={score:.4f}, source={doc.metadata.get('source')}, page={doc.metadata.get('page')}")
            
    except Exception as e:
        logger.error(f"Similarity search failed: {str(e)}")
        sim_docs = []
    
    # STEP 3: Combine and deduplicate results (prioritize similarity, add diversity from MMR)
    seen_content = set()
    combined_docs = []
    
    # First add similarity results (most relevant)
    for doc in sim_docs:
        content_hash = hash(doc.page_content[:200])  # Use first 200 chars as fingerprint
        if content_hash not in seen_content:
            seen_content.add(content_hash)
            combined_docs.append(doc)
    
    # Then add MMR results for diversity (if not already included)
    for doc in mmr_docs:
        content_hash = hash(doc.page_content[:200])
        if content_hash not in seen_content and len(combined_docs) < k * 2:
            seen_content.add(content_hash)
            combined_docs.append(doc)
    
    # Limit to reasonable number
    final_docs = combined_docs[:min(k * 2, 12)]
    
    logger.info(f"Combined retrieval: {len(final_docs)} unique documents")
    
    if not final_docs:
        logger.warning("No documents retrieved!")
        return ("I couldn't find relevant information in the uploaded PDFs.", [])
    
    # Log final document set
    for i, doc in enumerate(final_docs[:5]):
        logger.info(f"Final Doc {i+1}: {doc.metadata.get('source')} - Page {doc.metadata.get('page')} - {len(doc.page_content)} chars")
    
    # STEP 4: Build context from retrieved documents
    context_parts = []
    for i, doc in enumerate(final_docs):
        source = doc.metadata.get('source', 'Unknown')
        page = doc.metadata.get('page', '?')
        # Include source attribution in context for multi-document queries
        context_parts.append(f"[From {source}, Page {page}]\n{doc.page_content}")
    
    context = "\n\n---\n\n".join(context_parts)
    logger.info(f"Built context: {len(context)} characters from {len(final_docs)} documents")
    
    # STEP 5: Generate answer using LLM with two-stage process
    if settings.openai_api_key:
        try:
            llm = ChatOpenAI(model="gpt-4o", temperature=0)
            
            # Stage 1: Extract relevant information from each document chunk
            logger.info("Stage 1: Extracting relevant information from chunks...")
            extraction_prompt = PromptTemplate.from_template(
                """Extract information relevant to answering the question. Be concise but preserve key details.

Question: {question}

Document excerpt:
{chunk}

Relevant information (or "Not relevant" if this chunk doesn't help answer the question):"""
            )
            
            extracted_info = []
            for i, doc in enumerate(final_docs):
                try:
                    response = llm.invoke(extraction_prompt.format(
                        question=query,
                        chunk=f"[{doc.metadata.get('source')}, Page {doc.metadata.get('page')}]\n{doc.page_content}"
                    ))
                    info = response.content if hasattr(response, "content") else str(response)
                    
                    # Only include if chunk is relevant
                    if info.strip().lower() not in ["not relevant", "not relevant.", "n/a", ""]:
                        extracted_info.append({
                            'info': info.strip(),
                            'source': doc.metadata.get('source', 'Unknown'),
                            'page': doc.metadata.get('page', '?')
                        })
                        logger.info(f"  Chunk {i+1}: Extracted {len(info)} chars from {doc.metadata.get('source')}")
                    else:
                        logger.info(f"  Chunk {i+1}: Not relevant")
                except Exception as e:
                    logger.error(f"Failed to extract from chunk {i+1}: {str(e)}")
                    continue
            
            logger.info(f"Extracted information from {len(extracted_info)}/{len(final_docs)} chunks")
            
            if not extracted_info:
                return ("I couldn't find relevant information in the uploaded PDFs to answer your question.", final_docs[:k])
            
            # Stage 2: Synthesize and summarize the extracted information
            logger.info("Stage 2: Synthesizing final answer...")
            
            # Build consolidated context with source attribution
            consolidated_context = "\n\n".join([
                f"From {item['source']} (Page {item['page']}):\n{item['info']}"
                for item in extracted_info
            ])
            
            synthesis_prompt = PromptTemplate.from_template(
                """You are synthesizing information from multiple document sources to answer a question.

Instructions:
1. Provide a clear, comprehensive answer based on the information below
2. Synthesize information from multiple sources into a coherent response
3. When information comes from specific documents, mention them naturally (e.g., "According to [document name]...")
4. Structure your answer with clear sections if the question is complex
5. Be concise but complete - aim for a well-organized summary
6. If sources contradict, acknowledge both perspectives
7. End with a brief 1-2 sentence summary of the key takeaway

Question: {question}

Extracted information from documents:
{context}

Comprehensive Answer:"""
            )
            
            response = llm.invoke(synthesis_prompt.format(
                question=query,
                context=consolidated_context
            ))
            answer = response.content if hasattr(response, "content") else str(response)
            logger.info(f"Final answer generated: {len(answer)} characters")
            
            # Optional: Add source summary at the end
            sources_used = set(item['source'] for item in extracted_info)
            
            return (answer.strip() , final_docs[:k])
            
        except Exception as e:
            logger.error(f"LLM generation failed: {str(e)}")
            # Fallback to returning context
            answer = f"Found relevant information from {len(final_docs)} document sections:\n\n{context[:2000]}"
            return (answer, final_docs[:k])
    
    # No LLM available - return context
    answer = f"Found relevant information from {len(final_docs)} document sections:\n\n{context[:2000]}"
    return (answer, final_docs[:k])