import { mongodbService, type KnowledgeDocument } from './mongodb';
import { embeddingsService } from './embeddings';

export interface RAGResult {
  content: string;
  sources: Array<{
    content: string;
    metadata?: any;
    similarity?: number;
  }>;
}

/**
 * Implements Reciprocal Rank Fusion (RRF) algorithm to combine semantic and keyword search results.
 * RRF combines rankings from multiple retrieval methods by summing reciprocal ranks.
 * 
 * @param semanticResults - Array of documents from semantic search with their ranks
 * @param keywordResults - Array of documents from keyword search with their ranks
 * @param k - The RRF constant parameter (default: 30). Higher values reduce the impact of rank position
 * @returns An array of unique documents sorted by combined RRF score in descending order
 * 
 * @remarks
 * The RRF score for a document is calculated as: sum(1 / (k + rank)) across all result sets.
 * Documents appearing in multiple result sets will have higher combined scores.
 */
function reciprocalRankFusion(
  semanticResults: Array<{ doc: KnowledgeDocument; rank: number }>,
  keywordResults: Array<{ doc: KnowledgeDocument; rank: number }>,
  k: number = 30
): KnowledgeDocument[] {
  const docScores = new Map<string, number>();

  // Add semantic search scores
  semanticResults.forEach(({ doc, rank }) => {
    const docId = doc._id || doc.content;
    const score = 1 / (k + rank);
    docScores.set(docId, (docScores.get(docId) || 0) + score);
  });

  // Add keyword search scores
  keywordResults.forEach(({ doc, rank }) => {
    const docId = doc._id || doc.content;
    const score = 1 / (k + rank);
    docScores.set(docId, (docScores.get(docId) || 0) + score);
  });

  // Sort by combined score and return documents
  const sortedDocs = Array.from(docScores.entries())
    .sort(([, scoreA], [, scoreB]) => scoreB - scoreA)
    .map(([docId]) => {
      // Find the document by ID
      const semanticDoc = semanticResults.find(({ doc }) => (doc._id || doc.content) === docId)?.doc;
      const keywordDoc = keywordResults.find(({ doc }) => (doc._id || doc.content) === docId)?.doc;
      return semanticDoc || keywordDoc!;
    });

  return sortedDocs;
}

/**
 * Service for Retrieval-Augmented Generation (RAG) operations.
 * Combines semantic search (embeddings) and keyword search (BM25) to retrieve relevant documents.
 */
export class RAGService {
  /**
   * Retrieves relevant documents from the knowledge base using hybrid search (semantic + keyword).
   * 
   * @param query - The search query string
   * @param limit - Maximum number of documents to return (default: 3)
   * @returns A promise that resolves to an array of relevant knowledge documents
   * 
   * @remarks
   * Uses Reciprocal Rank Fusion to combine results from:
   * - Semantic search (vector similarity using embeddings)
   * - Keyword search (MongoDB Atlas Search with BM25 algorithm)
   */
  async retrieveRelevantDocuments(query: string, limit: number = 3): Promise<KnowledgeDocument[]> {
    try {
      // Semantic search using embeddings
      const queryEmbedding = await embeddingsService.generateEmbedding(query);
      const semanticResults = await mongodbService.searchSimilar(queryEmbedding, limit * 2, 0.3);
      
      // Keyword search using MongoDB Atlas Search (BM25)
      const keywordResults = await mongodbService.searchAtlas(query, limit * 2);

      // Convert semantic results to include rank
      const semanticResultsWithRank = semanticResults.map((doc, index) => ({
        doc,
        rank: index
      }));

      // Convert keyword results to include rank
      const keywordResultsWithRank = keywordResults.map((doc, index) => ({
        doc,
        rank: index
      }));

      // Apply Reciprocal Rank Fusion with k=30
      const fusedResults = reciprocalRankFusion(
        semanticResultsWithRank,
        keywordResultsWithRank,
        30
      );

      // Return top results up to the limit
      return fusedResults.slice(0, limit);
    } catch (error) {
      console.error('Failed to retrieve relevant documents:', error);
      return [];
    }
  }

  /**
   * Generates a RAG response by retrieving relevant documents and formatting them as context.
   * 
   * @param query - The user's query to search for relevant context
   * @param context - Additional context (currently unused but kept for API compatibility)
   * @returns A promise that resolves to a RAGResult containing:
   *   - content: Formatted context text from retrieved documents
   *   - sources: Array of source documents with metadata and similarity scores
   */
  async generateRAGResponse(query: string, context: any): Promise<RAGResult> {
    try {
      // Retrieve relevant documents
      const relevantDocs = await this.retrieveRelevantDocuments(query);
      
      // Format the context for the LLM
      const contextText = relevantDocs.length > 0 
        ? relevantDocs.map(doc => doc.content).join('\n\n')
        : 'No relevant context found.';

      const sources = relevantDocs.map(doc => ({
        content: doc.content,
        metadata: doc.metadata,
        similarity: (doc as any).similarity,
      }));

      return {
        content: contextText,
        sources,
      };
    } catch (error) {
      console.error('Failed to generate RAG response:', error);
      return {
        content: 'Unable to retrieve relevant context.',
        sources: [],
      };
    }
  }

  /**
   * Checks if the RAG service is ready by verifying embeddings model and MongoDB connection.
   * 
   * @returns A promise that resolves to true if both embeddings service and MongoDB are ready, false otherwise
   */
  async isReady(): Promise<boolean> {
    try {
      const isEmbeddingsReady = await embeddingsService.isModelAvailable();
      // Test MongoDB connection
      await mongodbService.getDocumentCount();
      return isEmbeddingsReady;
    } catch (error) {
      console.error('RAG service not ready:', error);
      return false;
    }
  }

  /**
   * Retrieves statistics about the knowledge base.
   * 
   * @returns A promise that resolves to an object containing:
   *   - documentCount: Total number of documents in the knowledge base
   *   - isReady: Whether the RAG service is fully operational
   */
  async getKnowledgeBaseStats(): Promise<{ documentCount: number; isReady: boolean }> {
    try {
      const documentCount = await mongodbService.getDocumentCount();
      const isReady = await this.isReady();
      
      return {
        documentCount,
        isReady,
      };
    } catch (error) {
      console.error('Failed to get knowledge base stats:', error);
      return {
        documentCount: 0,
        isReady: false,
      };
    }
  }
}

export const ragService = new RAGService();
