import pdf from 'pdf-parse';
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { getPostgresStorage } from '../postgres-storage';
import { generateEmbedding, generateRAGResponse, type SearchContext } from './openaiService';
import type { SupabaseDocumentChunk } from '@shared/supabase-schema';

// Cosine similarity function
function cosineSimilarity(a: number[], b: number[]): number {
  if (a.length !== b.length) return 0;
  
  let dotProduct = 0;
  let normA = 0;
  let normB = 0;
  
  for (let i = 0; i < a.length; i++) {
    dotProduct += a[i] * b[i];
    normA += a[i] * a[i];
    normB += b[i] * b[i];
  }
  
  return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
}

// Use LangChain's RecursiveCharacterTextSplitter for better text chunking
async function chunkTextWithLangChain(text: string, maxChunkSize: number = 500, overlap: number = 200): Promise<string[]> {
  const splitter = new RecursiveCharacterTextSplitter({
    chunkSize: maxChunkSize,
    chunkOverlap: overlap,
    separators: ["\n\n", "\n", ". ", "! ", "? ", " ", ""],
    keepSeparator: true,
  });
  
  const chunks = await splitter.splitText(text);
  return chunks;
}

export async function processPDFDocument(documentId: string, pdfBuffer: Buffer): Promise<void> {
  try {
    const storage = await getPostgresStorage();
    await storage.updateDocumentStatus(documentId, "processing");
    
    // Extract text from PDF
    const pdfData = await pdf(pdfBuffer);
    const text = pdfData.text;
    
    // Store full document content
    await storage.updateDocumentContent(documentId, text);
    
    // Use LangChain's text splitter for better chunking
    const chunks = await chunkTextWithLangChain(text);
    
    // Get document info for metadata
    const document = await storage.getDocument(documentId);
    
    // Process each chunk
    for (let i = 0; i < chunks.length; i++) {
      const chunk = chunks[i];
      
      // Generate embedding for chunk
      const embedding = await generateEmbedding(chunk);
      
      // Store chunk with embedding and metadata
      await storage.createDocumentChunk({
        document_id: documentId,
        content: chunk,
        embedding,
        page_number: null, // PDF parsing doesn't reliably give page numbers
        chunk_index: i,
        metadata: {
          documentName: document?.name || "Unknown Document",
          chunkType: "text"
        }
      });
    }
    
    // Update document status
    await storage.updateDocumentStatus(documentId, "ready", chunks.length);
    
  } catch (error) {
    const storage = await getPostgresStorage();
    await storage.updateDocumentStatus(documentId, "error");
    throw new Error(`Failed to process PDF: ${(error as Error).message}`);
  }
}

export async function performRAGSearch(query: string): Promise<{
  response: string;
  sources: Array<{
    document: string;
    page?: number;
    excerpt: string;
    relevance: number;
  }>;
}> {
  try {
    const storage = await getPostgresStorage();
    
    // Generate embedding for the query
    const queryEmbedding = await generateEmbedding(query);
    
    // Hybrid search: Combine vector search and text search
    const [vectorResults, textResults] = await Promise.all([
      // Vector search for semantic similarity
      storage.searchSimilarChunks(queryEmbedding, 5),
      // Text search for keyword matching
      performTextSearch(storage, query, 5)
    ]);
    
    // Combine and deduplicate results
    const combinedChunks = combineSearchResults(vectorResults, textResults, query);
    
    if (combinedChunks.length === 0) {
      throw new Error("No relevant content found. Please check your query or upload more documents.");
    }
    
    // Get document information for each chunk
    const relevantChunks = await Promise.all(
      combinedChunks.map(async (chunk) => {
        const document = await storage.getDocument(chunk.document_id);
        return {
          content: chunk.content,
          documentName: document?.name || chunk.metadata?.documentName || "Unknown Document",
          pageNumber: chunk.page_number || undefined,
          similarity: (chunk as any).hybridScore || 0.8,
        };
      })
    );
    
    // Create search context
    const searchContext: SearchContext = {
      query,
      relevantChunks,
    };
    
    // Generate AI response
    const result = await generateRAGResponse(searchContext);
    
    // Store search query with sources
    await storage.createSearchQuery({
      query,
      response: result.response,
      sources: result.sources.map((source, index) => ({
        document_id: combinedChunks[index]?.document_id || "",
        document_name: source.document,
        chunk_id: combinedChunks[index]?.id || "",
        content: source.excerpt,
        score: source.relevance
      })),
    });
    
    return result;
  } catch (error) {
    throw new Error(`RAG search failed: ${(error as Error).message}`);
  }
}

// Text search function for keyword matching
async function performTextSearch(storage: any, query: string, limit: number): Promise<SupabaseDocumentChunk[]> {
  try {
    // Get all chunks and perform text search
    const allChunks = await storage.getAllChunks();
    
    // Simple keyword matching with scoring
    const queryWords = query.toLowerCase().split(/\s+/).filter(word => word.length > 2);
    
    const scoredChunks = allChunks.map((chunk: SupabaseDocumentChunk) => {
      const content = chunk.content.toLowerCase();
      let score = 0;
      
      // Count keyword matches
      queryWords.forEach(word => {
        const matches = (content.match(new RegExp(word, 'g')) || []).length;
        score += matches;
      });
      
      // Boost score for exact phrase matches
      if (content.includes(query.toLowerCase())) {
        score += 5;
      }
      
      // Normalize score
      const normalizedScore = Math.min(score / queryWords.length, 1);
      
      return { ...chunk, textScore: normalizedScore };
    });
    
    // Sort by text score and return top results
    return scoredChunks
      .filter((chunk: any) => chunk.textScore > 0)
      .sort((a: any, b: any) => b.textScore - a.textScore)
      .slice(0, limit);
  } catch (error) {
    console.error('Text search failed:', error);
    return [];
  }
}

// Combine vector and text search results with hybrid scoring
function combineSearchResults(
  vectorResults: SupabaseDocumentChunk[], 
  textResults: any[], 
  query: string
): SupabaseDocumentChunk[] {
  const chunkMap = new Map<string, any>();
  
  // Add vector search results with vector score
  vectorResults.forEach(chunk => {
    chunkMap.set(chunk.id, {
      ...chunk,
      vectorScore: 0.8, // Default vector score
      hybridScore: 0.8
    });
  });
  
  // Add text search results and combine scores
  textResults.forEach(chunk => {
    const existing = chunkMap.get(chunk.id);
    if (existing) {
      // Combine scores for existing chunks
      existing.textScore = chunk.textScore;
      existing.hybridScore = (existing.vectorScore + chunk.textScore) / 2;
    } else {
      // Add new chunks from text search
      chunkMap.set(chunk.id, {
        ...chunk,
        vectorScore: 0,
        textScore: chunk.textScore,
        hybridScore: chunk.textScore * 0.7 // Slightly lower weight for text-only results
      });
    }
  });
  
  // Sort by hybrid score and return top results
  return Array.from(chunkMap.values())
    .sort((a, b) => b.hybridScore - a.hybridScore)
    .slice(0, 5);
}
