import { createClient, SupabaseClient } from '@supabase/supabase-js';
import { randomUUID } from "crypto";
import { generateEmbedding } from './services/openaiService';
import { 
  type SupabaseDocument, 
  type SupabaseDocumentChunk, 
  type SupabaseSearchQuery,
  type InsertSupabaseDocument,
  type InsertSupabaseDocumentChunk,
  type InsertSupabaseSearchQuery,
  TABLES,
  VECTOR_SEARCH_CONFIG
} from "@shared/supabase-schema";

export interface IStorage {
  // Document operations
  createDocument(document: InsertSupabaseDocument): Promise<SupabaseDocument>;
  getDocument(id: string): Promise<SupabaseDocument | undefined>;
  getAllDocuments(): Promise<SupabaseDocument[]>;
  updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void>;
  updateDocumentContent(id: string, content: string): Promise<void>;
  deleteDocument(id: string): Promise<void>;
  
  // Document chunk operations
  createDocumentChunk(chunk: InsertSupabaseDocumentChunk): Promise<SupabaseDocumentChunk>;
  getDocumentChunks(documentId: string): Promise<SupabaseDocumentChunk[]>;
  getAllChunks(): Promise<SupabaseDocumentChunk[]>;
  deleteDocumentChunks(documentId: string): Promise<void>;
  
  // Search query operations
  createSearchQuery(query: InsertSupabaseSearchQuery): Promise<SupabaseSearchQuery>;
  getSearchQuery(id: string): Promise<SupabaseSearchQuery | undefined>;
  getAllSearchQueries(): Promise<SupabaseSearchQuery[]>;
  
  // Vector search operations
  searchSimilarChunks(queryEmbedding: number[], limit?: number): Promise<SupabaseDocumentChunk[]>;
  createVectorIndex(): Promise<void>;
}

export class SupabaseStorage implements IStorage {
  private supabase: SupabaseClient;

  constructor(supabaseUrl: string, supabaseKey: string) {
    this.supabase = createClient(supabaseUrl, supabaseKey);
  }

  async connect(): Promise<void> {
    // Test connection
    const { data, error } = await this.supabase.from(TABLES.DOCUMENTS).select('count').limit(1);
    if (error) {
      throw new Error(`Failed to connect to Supabase: ${error.message}`);
    }
    console.log('Supabase connected successfully');
  }

  async disconnect(): Promise<void> {
    // Supabase client doesn't need explicit disconnection
    console.log('Supabase connection closed');
  }

  async createVectorIndex(): Promise<void> {
    try {
      // Check if pgvector extension is available
      const { data, error } = await this.supabase.rpc('check_pgvector_extension');
      if (error) {
        console.warn('pgvector extension not available, using fallback similarity search');
      } else {
        console.log('pgvector extension is available for vector search');
      }
    } catch (error) {
      console.warn('Vector search setup check failed, using fallback similarity search');
    }
  }

  async createDocument(insertDocument: InsertSupabaseDocument): Promise<SupabaseDocument> {
    const { data, error } = await this.supabase
      .from(TABLES.DOCUMENTS)
      .insert({
        ...insertDocument,
        status: insertDocument.status || "uploading",
        uploaded_at: new Date().toISOString(),
        processed_at: null,
        chunks: 0,
        content: null
      })
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to create document: ${error.message}`);
    }

    return data;
  }

  async getDocument(id: string): Promise<SupabaseDocument | undefined> {
    const { data, error } = await this.supabase
      .from(TABLES.DOCUMENTS)
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return undefined; // Document not found
      }
      throw new Error(`Failed to get document: ${error.message}`);
    }

    return data;
  }

  async getAllDocuments(): Promise<SupabaseDocument[]> {
    const { data, error } = await this.supabase
      .from(TABLES.DOCUMENTS)
      .select('*')
      .order('uploaded_at', { ascending: false });

    if (error) {
      throw new Error(`Failed to get documents: ${error.message}`);
    }

    return data || [];
  }

  async updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void> {
    console.log(`Updating document ${id} status to: ${status}, chunks: ${chunks}`);
    
    const updateData: any = { 
      status: status,
      updated_at: new Date().toISOString()
    };
    
    if (status === "ready") {
      updateData.processed_at = new Date().toISOString();
    }
    
    if (chunks !== undefined) {
      updateData.chunks = chunks;
    }

    const { error } = await this.supabase
      .from(TABLES.DOCUMENTS)
      .update(updateData)
      .eq('id', id);
    
    if (error) {
      throw new Error(`Failed to update document status: ${error.message}`);
    }
    
    console.log(`Document ${id} status updated successfully`);
  }

  async updateDocumentContent(id: string, content: string): Promise<void> {
    const { error } = await this.supabase
      .from(TABLES.DOCUMENTS)
      .update({ 
        content,
        updated_at: new Date().toISOString()
      })
      .eq('id', id);
    
    if (error) {
      throw new Error(`Failed to update document content: ${error.message}`);
    }
  }

  async deleteDocument(id: string): Promise<void> {
    // First delete all chunks associated with this document
    await this.deleteDocumentChunks(id);
    
    // Then delete the document itself
    const { error } = await this.supabase
      .from(TABLES.DOCUMENTS)
      .delete()
      .eq('id', id);
    
    if (error) {
      throw new Error(`Failed to delete document: ${error.message}`);
    }
    
    console.log(`Deleted document ${id} and all associated chunks`);
  }

  async deleteDocumentChunks(documentId: string): Promise<void> {
    const { error } = await this.supabase
      .from(TABLES.DOCUMENT_CHUNKS)
      .delete()
      .eq('document_id', documentId);
    
    if (error) {
      throw new Error(`Failed to delete document chunks: ${error.message}`);
    }
    
    console.log(`Deleted chunks for document ${documentId}`);
  }

  async createDocumentChunk(insertChunk: InsertSupabaseDocumentChunk): Promise<SupabaseDocumentChunk> {
    const { data, error } = await this.supabase
      .from(TABLES.DOCUMENT_CHUNKS)
      .insert({
        ...insertChunk,
        embedding: insertChunk.embedding || null,
        page_number: insertChunk.page_number || null,
        metadata: insertChunk.metadata || null
      })
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to create document chunk: ${error.message}`);
    }

    return data;
  }

  async getDocumentChunks(documentId: string): Promise<SupabaseDocumentChunk[]> {
    const { data, error } = await this.supabase
      .from(TABLES.DOCUMENT_CHUNKS)
      .select('*')
      .eq('document_id', documentId)
      .order('chunk_index');

    if (error) {
      throw new Error(`Failed to get document chunks: ${error.message}`);
    }

    return data || [];
  }

  async getAllChunks(): Promise<SupabaseDocumentChunk[]> {
    const { data, error } = await this.supabase
      .from(TABLES.DOCUMENT_CHUNKS)
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error(`Failed to get all chunks: ${error.message}`);
    }

    return data || [];
  }

  async createSearchQuery(insertQuery: InsertSupabaseSearchQuery): Promise<SupabaseSearchQuery> {
    const { data, error } = await this.supabase
      .from(TABLES.SEARCH_QUERIES)
      .insert({
        ...insertQuery,
        response: insertQuery.response || null,
        sources: insertQuery.sources || null
      })
      .select()
      .single();

    if (error) {
      throw new Error(`Failed to create search query: ${error.message}`);
    }

    return data;
  }

  async getSearchQuery(id: string): Promise<SupabaseSearchQuery | undefined> {
    const { data, error } = await this.supabase
      .from(TABLES.SEARCH_QUERIES)
      .select('*')
      .eq('id', id)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        return undefined; // Query not found
      }
      throw new Error(`Failed to get search query: ${error.message}`);
    }

    return data;
  }

  async getAllSearchQueries(): Promise<SupabaseSearchQuery[]> {
    const { data, error } = await this.supabase
      .from(TABLES.SEARCH_QUERIES)
      .select('*')
      .order('created_at', { ascending: false });

    if (error) {
      throw new Error(`Failed to get search queries: ${error.message}`);
    }

    return data || [];
  }

  async searchSimilarChunks(queryEmbedding: number[], limit: number = VECTOR_SEARCH_CONFIG.MAX_RESULTS): Promise<SupabaseDocumentChunk[]> {
    try {
      // Try to use Supabase's vector search if pgvector is available
      const { data, error } = await this.supabase.rpc('match_document_chunks', {
        query_embedding: queryEmbedding,
        match_threshold: VECTOR_SEARCH_CONFIG.SIMILARITY_THRESHOLD,
        match_count: limit
      });

      if (error) {
        console.warn('Vector search not available, using fallback text search');
        return this.fallbackTextSearch(queryEmbedding, limit);
      }

      return data || [];
    } catch (error) {
      console.warn('Vector search failed, using fallback text search');
      return this.fallbackTextSearch(queryEmbedding, limit);
    }
  }

  private async fallbackTextSearch(queryEmbedding: number[], limit: number): Promise<SupabaseDocumentChunk[]> {
    console.log('Using fallback text search (pgvector not available)');
    
    // Get all chunks and perform similarity search
    const chunks = await this.getAllChunks();
    
    // Calculate cosine similarity between query embedding and chunk embeddings
    const scoredChunks = await Promise.all(chunks.map(async (chunk) => {
      try {
        // Generate embedding for this chunk's content if it doesn't have one
        let chunkEmbedding = chunk.embedding;
        if (!chunkEmbedding) {
          chunkEmbedding = await generateEmbedding(chunk.content);
        }
        
        // Calculate cosine similarity
        const similarity = this.calculateCosineSimilarity(queryEmbedding, chunkEmbedding);
        
        return {
          ...chunk,
          score: similarity
        };
      } catch (error) {
        console.warn('Error generating embedding for chunk:', error);
        // Fallback to a low score if embedding generation fails
        return {
          ...chunk,
          score: 0.1
        };
      }
    }));
    
    // Sort by similarity score and return top results
    return scoredChunks
      .sort((a, b) => (b.score || 0) - (a.score || 0))
      .slice(0, limit)
      .filter(chunk => (chunk.score || 0) >= VECTOR_SEARCH_CONFIG.SIMILARITY_THRESHOLD);
  }

  private calculateCosineSimilarity(vecA: number[], vecB: number[]): number {
    if (vecA.length !== vecB.length) {
      return 0;
    }
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < vecA.length; i++) {
      dotProduct += vecA[i] * vecB[i];
      normA += vecA[i] * vecA[i];
      normB += vecB[i] * vecB[i];
    }
    
    if (normA === 0 || normB === 0) {
      return 0;
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }

  // Helper method to get database stats
  async getStats(): Promise<{
    documentsCount: number;
    chunksCount: number;
    queriesCount: number;
  }> {
    const [documentsResult, chunksResult, queriesResult] = await Promise.all([
      this.supabase.from(TABLES.DOCUMENTS).select('*', { count: 'exact', head: true }),
      this.supabase.from(TABLES.DOCUMENT_CHUNKS).select('*', { count: 'exact', head: true }),
      this.supabase.from(TABLES.SEARCH_QUERIES).select('*', { count: 'exact', head: true })
    ]);

    if (documentsResult.error) throw new Error(`Failed to get documents count: ${documentsResult.error.message}`);
    if (chunksResult.error) throw new Error(`Failed to get chunks count: ${chunksResult.error.message}`);
    if (queriesResult.error) throw new Error(`Failed to get queries count: ${queriesResult.error.message}`);

    return {
      documentsCount: documentsResult.count || 0,
      chunksCount: chunksResult.count || 0,
      queriesCount: queriesResult.count || 0
    };
  }
}

// Singleton instance
let supabaseStorage: SupabaseStorage | null = null;

export async function getSupabaseStorage(): Promise<SupabaseStorage> {
  if (!supabaseStorage) {
    const supabaseUrl = process.env.SUPABASE_URL || 'https://ieskrbcedzfcclbkzxct.supabase.co';
    const supabaseKey = process.env.SUPABASE_KEY || '';
    
    if (!supabaseKey) {
      throw new Error('SUPABASE_KEY environment variable is required');
    }
    
    console.log(`Connecting to Supabase: ${supabaseUrl}`);
    supabaseStorage = new SupabaseStorage(supabaseUrl, supabaseKey);
    await supabaseStorage.connect();
    console.log('Supabase connected successfully');
  }
  
  return supabaseStorage;
}

export { supabaseStorage };
