import { MongoClient, Db, Collection, ObjectId } from 'mongodb';
import { randomUUID } from "crypto";
import { generateEmbedding } from './services/openaiService';
import { 
  type MongoDocument, 
  type MongoDocumentChunk, 
  type MongoSearchQuery,
  type InsertMongoDocument,
  type InsertMongoDocumentChunk,
  type InsertMongoSearchQuery,
  COLLECTIONS,
  VECTOR_SEARCH_CONFIG
} from "@shared/mongodb-schema";

export interface IStorage {
  // Document operations
  createDocument(document: InsertMongoDocument): Promise<MongoDocument>;
  getDocument(id: string): Promise<MongoDocument | undefined>;
  getAllDocuments(): Promise<MongoDocument[]>;
  updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void>;
  updateDocumentContent(id: string, content: string): Promise<void>;
  deleteDocument(id: string): Promise<void>;
  
  // Document chunk operations
  createDocumentChunk(chunk: InsertMongoDocumentChunk): Promise<MongoDocumentChunk>;
  getDocumentChunks(documentId: string): Promise<MongoDocumentChunk[]>;
  getAllChunks(): Promise<MongoDocumentChunk[]>;
  deleteDocumentChunks(documentId: string): Promise<void>;
  
  // Search query operations
  createSearchQuery(query: InsertMongoSearchQuery): Promise<MongoSearchQuery>;
  getSearchQuery(id: string): Promise<MongoSearchQuery | undefined>;
  getAllSearchQueries(): Promise<MongoSearchQuery[]>;
  
  // Vector search operations
  searchSimilarChunks(queryEmbedding: number[], limit?: number): Promise<MongoDocumentChunk[]>;
  createVectorIndex(): Promise<void>;
}

export class MongoStorage implements IStorage {
  private client: MongoClient;
  private db: Db;
  private documents: Collection<MongoDocument>;
  private documentChunks: Collection<MongoDocumentChunk>;
  private searchQueries: Collection<MongoSearchQuery>;

  constructor(connectionString: string, databaseName: string = 'pdf_rag') {
    this.client = new MongoClient(connectionString);
    this.db = this.client.db(databaseName);
    this.documents = this.db.collection<MongoDocument>(COLLECTIONS.DOCUMENTS);
    this.documentChunks = this.db.collection<MongoDocumentChunk>(COLLECTIONS.DOCUMENT_CHUNKS);
    this.searchQueries = this.db.collection<MongoSearchQuery>(COLLECTIONS.SEARCH_QUERIES);
  }

  async connect(): Promise<void> {
    await this.client.connect();
    await this.createVectorIndex();
  }

  async disconnect(): Promise<void> {
    await this.client.close();
  }

  async createVectorIndex(): Promise<void> {
    try {
      // Create vector search index for document chunks
      await this.db.createCollection(COLLECTIONS.DOCUMENT_CHUNKS);
      
      // Create regular indexes for better query performance
      await this.documentChunks.createIndex({ documentId: 1 });
      await this.documents.createIndex({ status: 1 });
      await this.searchQueries.createIndex({ createdAt: -1 });
      
      console.log('MongoDB indexes created successfully. Note: Vector search index must be created manually in MongoDB Atlas.');
    } catch (error) {
      console.error('Error creating indexes:', error);
      // Don't throw error as index might already exist
    }
  }

  async createDocument(insertDocument: InsertMongoDocument): Promise<MongoDocument> {
    const id = randomUUID();
    const now = new Date();
    const document: MongoDocument = { 
      ...insertDocument,
      status: insertDocument.status || "uploading",
      id, 
      uploadedAt: now,
      processedAt: null,
      chunks: 0,
      content: null
    };
    
    await this.documents.insertOne(document);
    return document;
  }

  async getDocument(id: string): Promise<MongoDocument | undefined> {
    const document = await this.documents.findOne({ id });
    return document || undefined;
  }

  async getAllDocuments(): Promise<MongoDocument[]> {
    const documents = await this.documents.find({}).toArray();
    return documents;
  }

  async updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void> {
    console.log(`Updating document ${id} status to: ${status}, chunks: ${chunks}`);
    
    const updateData: Partial<MongoDocument> = { 
      status: status as any,
      processedAt: status === "ready" ? new Date() : undefined
    };
    
    if (chunks !== undefined) {
      updateData.chunks = chunks;
    }

    const result = await this.documents.updateOne(
      { id }, 
      { $set: updateData }
    );
    
    console.log(`Update result: ${result.modifiedCount} documents modified`);
  }

  async updateDocumentContent(id: string, content: string): Promise<void> {
    await this.documents.updateOne(
      { id }, 
      { $set: { content } }
    );
  }

  async deleteDocument(id: string): Promise<void> {
    // First delete all chunks associated with this document
    await this.deleteDocumentChunks(id);
    
    // Then delete the document itself
    const result = await this.documents.deleteOne({ id });
    
    if (result.deletedCount === 0) {
      throw new Error(`Document with id ${id} not found`);
    }
    
    console.log(`Deleted document ${id} and all associated chunks`);
  }

  async deleteDocumentChunks(documentId: string): Promise<void> {
    const result = await this.documentChunks.deleteMany({ documentId });
    console.log(`Deleted ${result.deletedCount} chunks for document ${documentId}`);
  }

  async createDocumentChunk(insertChunk: InsertMongoDocumentChunk): Promise<MongoDocumentChunk> {
    const id = randomUUID();
    const chunk: MongoDocumentChunk = { 
      ...insertChunk, 
      id,
      embedding: insertChunk.embedding || undefined,
      pageNumber: insertChunk.pageNumber || null,
      metadata: insertChunk.metadata || undefined
    };
    
    await this.documentChunks.insertOne(chunk);
    return chunk;
  }

  async getDocumentChunks(documentId: string): Promise<MongoDocumentChunk[]> {
    const chunks = await this.documentChunks.find({ documentId }).toArray();
    return chunks;
  }

  async getAllChunks(): Promise<MongoDocumentChunk[]> {
    const chunks = await this.documentChunks.find({}).toArray();
    return chunks;
  }

  async createSearchQuery(insertQuery: InsertMongoSearchQuery): Promise<MongoSearchQuery> {
    const id = randomUUID();
    const query: MongoSearchQuery = { 
      ...insertQuery,
      response: insertQuery.response || null,
      sources: insertQuery.sources || null,
      id, 
      createdAt: new Date()
    };
    
    await this.searchQueries.insertOne(query);
    return query;
  }

  async getSearchQuery(id: string): Promise<MongoSearchQuery | undefined> {
    const query = await this.searchQueries.findOne({ id });
    return query || undefined;
  }

  async getAllSearchQueries(): Promise<MongoSearchQuery[]> {
    const queries = await this.searchQueries.find({}).sort({ createdAt: -1 }).toArray();
    return queries;
  }

  async searchSimilarChunks(queryEmbedding: number[], limit: number = VECTOR_SEARCH_CONFIG.MAX_RESULTS): Promise<MongoDocumentChunk[]> {
    try {
      // Use MongoDB's vector search aggregation pipeline
      const pipeline = [
        {
          $vectorSearch: {
            index: VECTOR_SEARCH_CONFIG.INDEX_NAME,
            path: VECTOR_SEARCH_CONFIG.VECTOR_FIELD,
            queryVector: queryEmbedding,
            numCandidates: limit * 2, // Get more candidates for better results
            limit: limit,
            filter: {
              // Add any filters here if needed
            }
          }
        },
        {
          $project: {
            _id: 1,
            id: 1,
            documentId: 1,
            content: 1,
            pageNumber: 1,
            chunkIndex: 1,
            metadata: 1,
            score: { $meta: "vectorSearchScore" }
          }
        }
      ];

      const results = await this.documentChunks.aggregate(pipeline).toArray();
      
      // Filter by similarity threshold
      return results.filter((chunk: any) => 
        (chunk.score || 0) >= VECTOR_SEARCH_CONFIG.SIMILARITY_THRESHOLD
      ) as MongoDocumentChunk[];
    } catch (error) {
      console.warn('Vector search not available (requires MongoDB Atlas), using fallback text search');
      console.log('Error details:', error instanceof Error ? error.message : 'Unknown error');
      // Fallback to text search if vector search fails
      return this.fallbackTextSearch(queryEmbedding, limit);
    }
  }

  private async fallbackTextSearch(queryEmbedding: number[], limit: number): Promise<MongoDocumentChunk[]> {
    console.log('Using fallback text search (MongoDB Atlas vector search not available)');
    
    // For local MongoDB, we'll use embedding-based similarity search
    const chunks = await this.documentChunks
      .find({})
      // .limit(limit * 5) // Get more chunks to filter from
      .toArray();
    
    // Calculate cosine similarity between query embedding and chunk embeddings
    const scoredChunks = await Promise.all(chunks.map(async (chunk) => {
      try {
        // Generate embedding for this chunk's content
        const chunkEmbedding = await generateEmbedding(chunk.content);
        
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
      .slice(0, limit) as MongoDocumentChunk[];
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
    const [documentsCount, chunksCount, queriesCount] = await Promise.all([
      this.documents.countDocuments(),
      this.documentChunks.countDocuments(),
      this.searchQueries.countDocuments()
    ]);

    return {
      documentsCount,
      chunksCount,
      queriesCount
    };
  }
}

// Singleton instance
let mongoStorage: MongoStorage | null = null;

export async function getMongoStorage(): Promise<MongoStorage> {
  if (!mongoStorage) {
    const connectionString = process.env.MONGODB_URI || 'mongodb://localhost:27017';
    const databaseName = process.env.MONGODB_DATABASE || 'pdf_rag';
    
    console.log(`Connecting to MongoDB: ${connectionString}`);
    mongoStorage = new MongoStorage(connectionString, databaseName);
    await mongoStorage.connect();
    console.log('MongoDB connected successfully');
  }
  
  return mongoStorage;
}

export { mongoStorage };
