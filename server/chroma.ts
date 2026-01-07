import type { RetrievedChunk } from "@shared/schema";

let isChromaAvailable = false;

// Cosine similarity calculation - fallback if Chroma is not available
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
  
  const magnitude = Math.sqrt(normA) * Math.sqrt(normB);
  return magnitude === 0 ? 0 : dotProduct / magnitude;
}

// In-memory fallback storage
const vectorStore: Map<string, {
  id: string;
  content: string;
  embedding: number[];
  documentId: string;
  page: number;
}> = new Map();

// Initialize Chroma client
export async function initializeChroma() {
  try {
    // Try to initialize Chroma, but don't fail if it's not available
    console.log("Chroma vector store initialized (in-memory fallback mode)");
    isChromaAvailable = true;
  } catch (error) {
    console.warn("Chroma not available, using in-memory vector store:", error);
    isChromaAvailable = false;
  }
}

// Add chunk to vector store
export async function addChunkToVectorStore(
  chunkId: string,
  content: string,
  embedding: number[],
  documentId: string,
  page: number
) {
  vectorStore.set(chunkId, {
    id: chunkId,
    content,
    embedding,
    documentId,
    page,
  });
  
  console.log(`📦 [VECTOR STORE] Added chunk:`, {
    id: chunkId,
    documentId,
    page,
    contentLength: content.length,
    embeddingDimensions: embedding.length,
    contentPreview: content.substring(0, 100) + (content.length > 100 ? '...' : ''),
  });
  console.log(`📊 [VECTOR STORE] Total chunks: ${vectorStore.size}`);
}

// Add multiple chunks in batch
export async function addChunksToVectorStore(chunks: Array<{
  id: string;
  content: string;
  embedding: number[];
  documentId: string;
  page: number;
}>) {
  console.log(`📦 [VECTOR STORE] Adding batch of ${chunks.length} chunks`);
  for (const chunk of chunks) {
    vectorStore.set(chunk.id, chunk);
  }
  console.log(`📊 [VECTOR STORE] Total chunks after batch: ${vectorStore.size}`);
  
  // Log summary by document
  const byDocument = new Map<string, number>();
  for (const chunk of Array.from(vectorStore.values())) {
    byDocument.set(chunk.documentId, (byDocument.get(chunk.documentId) || 0) + 1);
  }
  console.log(`📋 [VECTOR STORE] Chunks by document:`, Object.fromEntries(byDocument));
}

// Search similar chunks
export async function searchSimilarChunks(
  embedding: number[],
  documentId: string,
  topK: number = 5
): Promise<RetrievedChunk[]> {
  console.log(`🔍 [VECTOR STORE] Searching for similar chunks`);
  console.log(`   - Document ID: ${documentId}`);
  console.log(`   - Top K: ${topK}`);
  console.log(`   - Query embedding dimensions: ${embedding.length}`);
  console.log(`   - Total chunks in store: ${vectorStore.size}`);
  
  const documentChunks = Array.from(vectorStore.values())
    .filter(chunk => chunk.documentId === documentId);

  console.log(`   - Chunks for this document: ${documentChunks.length}`);

  if (documentChunks.length === 0) {
    console.log(`   - ⚠️  No chunks found for document ${documentId}`);
    return [];
  }

  // Calculate similarity scores
  const similarities = documentChunks.map(chunk => ({
    id: chunk.id,
    content: chunk.content,
    page: chunk.page,
    similarity: cosineSimilarity(embedding, chunk.embedding),
  }));

  // Sort by similarity (descending) and return top K
  const results = similarities
    .sort((a, b) => b.similarity - a.similarity)
    .slice(0, topK);
  
  console.log(`   - ✅ Found ${results.length} similar chunks:`);
  results.forEach((result, i) => {
    console.log(`     ${i + 1}. Similarity: ${result.similarity.toFixed(4)}, Page: ${result.page}, Content: ${result.content.substring(0, 80)}...`);
  });

  return results;
}

// Delete chunks for a document
export async function deleteDocumentChunks(documentId: string) {
  const entriesToDelete: string[] = [];
  for (const [id, chunk] of vectorStore.entries()) {
    if (chunk.documentId === documentId) {
      entriesToDelete.push(id);
    }
  }
  
  console.log(`🗑️  [VECTOR STORE] Deleting ${entriesToDelete.length} chunks for document ${documentId}`);
  
  for (const id of entriesToDelete) {
    vectorStore.delete(id);
  }
  
  console.log(`📊 [VECTOR STORE] Remaining chunks: ${vectorStore.size}`);
}

// Get collection stats
export async function getCollectionStats() {
  const stats = { vectorCount: vectorStore.size };
  
  // Log detailed stats
  console.log(`📊 [VECTOR STORE] Collection Statistics:`);
  console.log(`   - Total vectors: ${vectorStore.size}`);
  
  if (vectorStore.size > 0) {
    // Group by document
    const byDocument = new Map<string, number>();
    const byPage = new Map<number, number>();
    let totalEmbeddingDimensions = 0;
    
    for (const chunk of Array.from(vectorStore.values())) {
      byDocument.set(chunk.documentId, (byDocument.get(chunk.documentId) || 0) + 1);
      byPage.set(chunk.page, (byPage.get(chunk.page) || 0) + 1);
      totalEmbeddingDimensions = chunk.embedding.length;
    }
    
    console.log(`   - Documents: ${byDocument.size}`);
    console.log(`   - Chunks by document:`, Object.fromEntries(byDocument));
    console.log(`   - Embedding dimensions: ${totalEmbeddingDimensions}`);
    console.log(`   - Pages covered: ${byPage.size}`);
    
    // Show sample chunks
    const sampleChunks = Array.from(vectorStore.values()).slice(0, 3);
    console.log(`   - Sample chunks (first 3):`);
    sampleChunks.forEach((chunk, i) => {
      console.log(`     ${i + 1}. ID: ${chunk.id}, Doc: ${chunk.documentId}, Page: ${chunk.page}, Content: ${chunk.content.substring(0, 60)}...`);
    });
  }
  
  return stats;
}
