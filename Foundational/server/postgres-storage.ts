import pg from 'pg';
const { Pool, Client } = pg;
import type { Pool as PoolType } from 'pg';
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
import { IStorage } from './supabase-storage';

export class PostgresStorage implements IStorage {
  private pool: PoolType;

  constructor(connectionString: string) {
    this.pool = new Pool({
      connectionString: connectionString,
      ssl: false, // Set to true if your database requires SSL
    });
  }

  async connect(): Promise<void> {
    try {
      const client = await this.pool.connect();
      await client.query('SELECT NOW()');
      client.release();
      console.log('PostgreSQL connected successfully');
    } catch (error) {
      throw new Error(`Failed to connect to PostgreSQL: ${(error as Error).message}`);
    }
  }

  async disconnect(): Promise<void> {
    await this.pool.end();
    console.log('PostgreSQL connection closed');
  }

  async createVectorIndex(): Promise<void> {
    try {
      const client = await this.pool.connect();
      try {
        // Check if pgvector extension is available
        const result = await client.query(
          "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
        );
        if (result.rows[0].exists) {
          console.log('pgvector extension is available for vector search');
        } else {
          console.warn('pgvector extension not available, using fallback similarity search');
        }
      } finally {
        client.release();
      }
    } catch (error) {
      console.warn('Vector search setup check failed, using fallback similarity search');
    }
  }

  async createDocument(insertDocument: InsertSupabaseDocument): Promise<SupabaseDocument> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `INSERT INTO ${TABLES.DOCUMENTS} (name, size, status, uploaded_at, processed_at, chunks, content)
         VALUES ($1, $2, $3, $4, $5, $6, $7)
         RETURNING *`,
        [
          insertDocument.name,
          insertDocument.size,
          insertDocument.status || 'uploading',
          new Date().toISOString(),
          null,
          0,
          null
        ]
      );
      return this.mapRowToDocument(result.rows[0]);
    } catch (error) {
      throw new Error(`Failed to create document: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async getDocument(id: string): Promise<SupabaseDocument | undefined> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `SELECT * FROM ${TABLES.DOCUMENTS} WHERE id = $1`,
        [id]
      );
      if (result.rows.length === 0) {
        return undefined;
      }
      return this.mapRowToDocument(result.rows[0]);
    } catch (error) {
      throw new Error(`Failed to get document: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async getAllDocuments(): Promise<SupabaseDocument[]> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `SELECT * FROM ${TABLES.DOCUMENTS} ORDER BY uploaded_at DESC`
      );
      return result.rows.map((row: any) => this.mapRowToDocument(row));
    } catch (error) {
      throw new Error(`Failed to get documents: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void> {
    console.log(`Updating document ${id} status to: ${status}, chunks: ${chunks}`);
    const client = await this.pool.connect();
    try {
      const updateFields: string[] = ['status = $1', 'updated_at = $2'];
      const values: any[] = [status, new Date().toISOString()];
      let paramIndex = 3;

      if (status === 'ready') {
        updateFields.push(`processed_at = $${paramIndex}`);
        values.push(new Date().toISOString());
        paramIndex++;
      }

      if (chunks !== undefined) {
        updateFields.push(`chunks = $${paramIndex}`);
        values.push(chunks);
        paramIndex++;
      }

      values.push(id);

      await client.query(
        `UPDATE ${TABLES.DOCUMENTS} SET ${updateFields.join(', ')} WHERE id = $${paramIndex}`,
        values
      );
      console.log(`Document ${id} status updated successfully`);
    } catch (error) {
      throw new Error(`Failed to update document status: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async updateDocumentContent(id: string, content: string): Promise<void> {
    const client = await this.pool.connect();
    try {
      await client.query(
        `UPDATE ${TABLES.DOCUMENTS} SET content = $1, updated_at = $2 WHERE id = $3`,
        [content, new Date().toISOString(), id]
      );
    } catch (error) {
      throw new Error(`Failed to update document content: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async deleteDocument(id: string): Promise<void> {
    const client = await this.pool.connect();
    try {
      // Delete chunks first (CASCADE should handle this, but being explicit)
      await this.deleteDocumentChunks(id);
      
      await client.query(
        `DELETE FROM ${TABLES.DOCUMENTS} WHERE id = $1`,
        [id]
      );
      console.log(`Deleted document ${id} and all associated chunks`);
    } catch (error) {
      throw new Error(`Failed to delete document: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async deleteDocumentChunks(documentId: string): Promise<void> {
    const client = await this.pool.connect();
    try {
      await client.query(
        `DELETE FROM ${TABLES.DOCUMENT_CHUNKS} WHERE document_id = $1`,
        [documentId]
      );
      console.log(`Deleted chunks for document ${documentId}`);
    } catch (error) {
      throw new Error(`Failed to delete document chunks: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async createDocumentChunk(insertChunk: InsertSupabaseDocumentChunk): Promise<SupabaseDocumentChunk> {
    const client = await this.pool.connect();
    try {
      // Check if pgvector is available by checking the column type
      const columnCheck = await client.query(`
        SELECT data_type 
        FROM information_schema.columns 
        WHERE table_name = $1 AND column_name = 'embedding'
      `, [TABLES.DOCUMENT_CHUNKS]);
      
      const isVectorType = columnCheck.rows.length > 0 && columnCheck.rows[0].data_type === 'USER-DEFINED';
      
      // Format embedding based on column type
      let embeddingValue: string | null = null;
      if (insertChunk.embedding) {
        if (isVectorType) {
          // For VECTOR type: PostgreSQL array format
          embeddingValue = '[' + insertChunk.embedding.join(',') + ']';
        } else {
          // For TEXT type: JSON string format
          embeddingValue = JSON.stringify(insertChunk.embedding);
        }
      }
      
      const query = isVectorType
        ? `INSERT INTO ${TABLES.DOCUMENT_CHUNKS} 
           (document_id, content, embedding, page_number, chunk_index, metadata)
           VALUES ($1, $2, $3::vector, $4, $5, $6)
           RETURNING *`
        : `INSERT INTO ${TABLES.DOCUMENT_CHUNKS} 
           (document_id, content, embedding, page_number, chunk_index, metadata)
           VALUES ($1, $2, $3, $4, $5, $6)
           RETURNING *`;
      
      const result = await client.query(query, [
        insertChunk.document_id,
        insertChunk.content,
        embeddingValue,
        insertChunk.page_number || null,
        insertChunk.chunk_index,
        insertChunk.metadata ? JSON.stringify(insertChunk.metadata) : null
      ]);
      return this.mapRowToChunk(result.rows[0]);
    } catch (error) {
      throw new Error(`Failed to create document chunk: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async getDocumentChunks(documentId: string): Promise<SupabaseDocumentChunk[]> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `SELECT * FROM ${TABLES.DOCUMENT_CHUNKS} WHERE document_id = $1 ORDER BY chunk_index`,
        [documentId]
      );
      return result.rows.map((row: any) => this.mapRowToChunk(row));
    } catch (error) {
      throw new Error(`Failed to get document chunks: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async getAllChunks(): Promise<SupabaseDocumentChunk[]> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `SELECT * FROM ${TABLES.DOCUMENT_CHUNKS} ORDER BY created_at DESC`
      );
      return result.rows.map((row: any) => this.mapRowToChunk(row));
    } catch (error) {
      throw new Error(`Failed to get all chunks: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async createSearchQuery(insertQuery: InsertSupabaseSearchQuery): Promise<SupabaseSearchQuery> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `INSERT INTO ${TABLES.SEARCH_QUERIES} (query, response, sources)
         VALUES ($1, $2, $3)
         RETURNING *`,
        [
          insertQuery.query,
          insertQuery.response || null,
          insertQuery.sources ? JSON.stringify(insertQuery.sources) : null
        ]
      );
      return this.mapRowToSearchQuery(result.rows[0]);
    } catch (error) {
      throw new Error(`Failed to create search query: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async getSearchQuery(id: string): Promise<SupabaseSearchQuery | undefined> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `SELECT * FROM ${TABLES.SEARCH_QUERIES} WHERE id = $1`,
        [id]
      );
      if (result.rows.length === 0) {
        return undefined;
      }
      return this.mapRowToSearchQuery(result.rows[0]);
    } catch (error) {
      throw new Error(`Failed to get search query: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async getAllSearchQueries(): Promise<SupabaseSearchQuery[]> {
    const client = await this.pool.connect();
    try {
      const result = await client.query(
        `SELECT * FROM ${TABLES.SEARCH_QUERIES} ORDER BY created_at DESC`
      );
      return result.rows.map((row: any) => this.mapRowToSearchQuery(row));
    } catch (error) {
      throw new Error(`Failed to get search queries: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  async searchSimilarChunks(queryEmbedding: number[], limit: number = VECTOR_SEARCH_CONFIG.MAX_RESULTS): Promise<SupabaseDocumentChunk[]> {
    const client = await this.pool.connect();
    try {
      // Check if pgvector is available
      const extensionCheck = await client.query(
        "SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = 'vector')"
      );
      const hasPgVector = extensionCheck.rows[0].exists;
      
      if (hasPgVector) {
        // Check if embedding column is VECTOR type
        const columnCheck = await client.query(`
          SELECT data_type 
          FROM information_schema.columns 
          WHERE table_name = $1 AND column_name = 'embedding'
        `, [TABLES.DOCUMENT_CHUNKS]);
        
        const isVectorType = columnCheck.rows.length > 0 && columnCheck.rows[0].data_type === 'USER-DEFINED';
        
        if (isVectorType) {
          // Use pgvector similarity search
          const embeddingArrayStr = '[' + queryEmbedding.join(',') + ']';
          
          const result = await client.query(
            `SELECT 
              id, document_id, content, embedding, page_number, chunk_index, metadata, created_at, updated_at,
              1 - (embedding <=> $1::vector) AS similarity
             FROM ${TABLES.DOCUMENT_CHUNKS}
             WHERE embedding IS NOT NULL
               AND 1 - (embedding <=> $1::vector) > $2
             ORDER BY embedding <=> $1::vector
             LIMIT $3`,
            [embeddingArrayStr, VECTOR_SEARCH_CONFIG.SIMILARITY_THRESHOLD, limit]
          );

          if (result.rows.length > 0) {
            return result.rows.map((row: any) => this.mapRowToChunk(row));
          }
        }
      }

      // Fallback to text search if vector search doesn't work
      console.warn('Vector search not available, using fallback text search');
      return this.fallbackTextSearch(queryEmbedding, limit);
    } catch (error) {
      console.warn('Vector search failed, using fallback text search:', (error as Error).message);
      return this.fallbackTextSearch(queryEmbedding, limit);
    } finally {
      client.release();
    }
  }

  private async fallbackTextSearch(queryEmbedding: number[], limit: number): Promise<SupabaseDocumentChunk[]> {
    console.log('Using fallback text search (pgvector not available)');
    
    const chunks = await this.getAllChunks();
    
    const scoredChunks = await Promise.all(chunks.map(async (chunk) => {
      try {
        let chunkEmbedding = chunk.embedding;
        if (!chunkEmbedding) {
          chunkEmbedding = await generateEmbedding(chunk.content);
        }
        
        const similarity = this.calculateCosineSimilarity(queryEmbedding, chunkEmbedding);
        
        return {
          ...chunk,
          score: similarity
        };
      } catch (error) {
        console.warn('Error generating embedding for chunk:', error);
        return {
          ...chunk,
          score: 0.1
        };
      }
    }));
    
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

  async getStats(): Promise<{
    documentsCount: number;
    chunksCount: number;
    queriesCount: number;
  }> {
    const client = await this.pool.connect();
    try {
      const [documentsResult, chunksResult, queriesResult] = await Promise.all([
        client.query(`SELECT COUNT(*) as count FROM ${TABLES.DOCUMENTS}`),
        client.query(`SELECT COUNT(*) as count FROM ${TABLES.DOCUMENT_CHUNKS}`),
        client.query(`SELECT COUNT(*) as count FROM ${TABLES.SEARCH_QUERIES}`)
      ]);

      return {
        documentsCount: parseInt(documentsResult.rows[0].count, 10),
        chunksCount: parseInt(chunksResult.rows[0].count, 10),
        queriesCount: parseInt(queriesResult.rows[0].count, 10)
      };
    } catch (error) {
      throw new Error(`Failed to get stats: ${(error as Error).message}`);
    } finally {
      client.release();
    }
  }

  // Helper methods to map database rows to schema types
  private mapRowToDocument(row: any): SupabaseDocument {
    return {
      id: row.id,
      name: row.name,
      size: row.size,
      status: row.status,
      uploaded_at: row.uploaded_at?.toISOString() || new Date().toISOString(),
      processed_at: row.processed_at?.toISOString() || null,
      chunks: row.chunks || 0,
      content: row.content || null,
      created_at: row.created_at?.toISOString() || new Date().toISOString(),
      updated_at: row.updated_at?.toISOString() || new Date().toISOString(),
    };
  }

  private mapRowToChunk(row: any): SupabaseDocumentChunk {
    let embedding: number[] | undefined;
    if (row.embedding) {
      // Handle different embedding formats
      if (typeof row.embedding === 'string') {
        try {
          // Try parsing as JSON (for TEXT column type)
          embedding = JSON.parse(row.embedding);
        } catch {
          // If JSON parsing fails, try parsing as PostgreSQL array string format
          try {
            // Remove brackets and split by comma
            const cleaned = row.embedding.replace(/[\[\]]/g, '');
            const parsed = cleaned.split(',').map((v: string) => parseFloat(v.trim())).filter((v: number) => !isNaN(v));
            embedding = parsed.length > 0 ? parsed : undefined;
          } catch {
            embedding = undefined;
          }
        }
      } else if (Array.isArray(row.embedding)) {
        // Already an array (from pgvector VECTOR type)
        embedding = row.embedding;
      } else if (row.embedding && typeof row.embedding === 'object' && 'toArray' in row.embedding) {
        // Handle pgvector vector type that might have a toArray method
        embedding = Array.from(row.embedding as any);
      }
    }

    return {
      id: row.id,
      document_id: row.document_id,
      content: row.content,
      embedding,
      page_number: row.page_number || null,
      chunk_index: row.chunk_index,
      metadata: row.metadata ? (typeof row.metadata === 'string' ? JSON.parse(row.metadata) : row.metadata) : undefined,
      created_at: row.created_at?.toISOString() || new Date().toISOString(),
      updated_at: row.updated_at?.toISOString() || new Date().toISOString(),
    };
  }

  private mapRowToSearchQuery(row: any): SupabaseSearchQuery {
    return {
      id: row.id,
      query: row.query,
      response: row.response || null,
      sources: row.sources ? (typeof row.sources === 'string' ? JSON.parse(row.sources) : row.sources) : null,
      created_at: row.created_at?.toISOString() || new Date().toISOString(),
      updated_at: row.updated_at?.toISOString() || new Date().toISOString(),
    };
  }
}

// Singleton instance
let postgresStorage: PostgresStorage | null = null;

export async function getPostgresStorage(): Promise<PostgresStorage> {
  if (!postgresStorage) {
    try {
      // Parse JDBC connection string or use environment variables
      const connectionString = process.env.DATABASE_URL || 
        (() => {
          // Parse JDBC format: jdbc:postgresql://host:port/db?user=user&password=pass
          const jdbcUrl = process.env.JDBC_URL || 'jdbc:postgresql://35.193.24.101:5432/myappdb?user=myappuser&password=ChangeThisPassword123!';
          const match = jdbcUrl.match(/jdbc:postgresql:\/\/([^:]+):(\d+)\/([^?]+)\?user=([^&]+)&password=(.+)/);
          if (match) {
            const [, host, port, database, user, password] = match;
            return `postgresql://${user}:${encodeURIComponent(password)}@${host}:${port}/${database}`;
          }
          throw new Error('Invalid JDBC connection string format');
        })();
      
      console.log(`Connecting to PostgreSQL...`);
      postgresStorage = new PostgresStorage(connectionString);
      await postgresStorage.connect();
      console.log('PostgreSQL connected successfully');
    } catch (error) {
      console.error('Failed to initialize PostgreSQL storage:', error);
      throw error;
    }
  }
  
  return postgresStorage;
}

export { postgresStorage };

