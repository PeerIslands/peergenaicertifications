import { MongoClient, Db, Collection } from 'mongodb';

export interface KnowledgeDocument {
  _id?: string;
  content: string;
  metadata?: {
    source?: string;
    title?: string;
    createdAt?: Date;
    [key: string]: any;
  };
  embedding: number[];
}

/**
 * Service for interacting with MongoDB to store and retrieve knowledge base documents.
 * Provides methods for semantic search (vector similarity) and keyword search (Atlas Search).
 */
export class MongoDBService {
  private client: MongoClient;
  private db: Db;
  private collection: Collection<KnowledgeDocument>;

  /**
   * Creates a new MongoDBService instance.
   * Initializes MongoDB client and collection using environment variables or defaults.
   */
  constructor() {
    const mongoUri = process.env.MONGODB_URI || 'mongodb+srv://mongosh_aj:ajinkya123@cluster0.clx9fur.mongodb.net/';
    const databaseName = process.env.MONGODB_DATABASE || 'query-mind';
    const collectionName = process.env.MONGODB_COLLECTION || 'knowledge-base';

    this.client = new MongoClient(mongoUri);
    this.db = this.client.db(databaseName);
    this.collection = this.db.collection<KnowledgeDocument>(collectionName);
  }

  /**
   * Establishes a connection to the MongoDB database.
   * 
   * @returns A promise that resolves when the connection is established
   * @throws Will throw an error if the connection fails
   */
  async connect(): Promise<void> {
    try {
      await this.client.connect();
      console.log('Connected to MongoDB');
    } catch (error) {
      console.error('Failed to connect to MongoDB:', error);
      throw error;
    }
  }

  /**
   * Closes the MongoDB connection.
   * 
   * @returns A promise that resolves when the connection is closed
   */
  async disconnect(): Promise<void> {
    await this.client.close();
  }

  /**
   * Performs semantic search using cosine similarity on document embeddings.
   * 
   * @param queryEmbedding - The embedding vector of the query
   * @param limit - Maximum number of results to return (default: 5)
   * @param threshold - Minimum similarity score threshold (default: 0.7)
   * @returns A promise that resolves to an array of knowledge documents sorted by similarity score
   * @throws Will throw an error if the search operation fails
   * 
   * @remarks
   * Uses MongoDB aggregation pipeline to calculate cosine similarity between query embedding
   * and stored document embeddings. Only returns documents above the similarity threshold.
   */
  async searchSimilar(queryEmbedding: number[], limit: number = 5, threshold: number = 0.7): Promise<KnowledgeDocument[]> {
    try {
      // Use MongoDB aggregation pipeline for cosine similarity search
      const pipeline = [
        {
          $addFields: {
            similarity: {
              $let: {
                vars: {
                  dotProduct: {
                    $reduce: {
                      input: { $range: [0, { $size: "$embedding" }] },
                      initialValue: 0,
                      in: {
                        $add: [
                          "$$value",
                          {
                            $multiply: [
                              { $arrayElemAt: ["$embedding", "$$this"] },
                              { $arrayElemAt: [queryEmbedding, "$$this"] }
                            ]
                          }
                        ]
                      }
                    }
                  },
                  magnitudeA: {
                    $sqrt: {
                      $reduce: {
                        input: "$embedding",
                        initialValue: 0,
                        in: { $add: ["$$value", { $multiply: ["$$this", "$$this"] }] }
                      }
                    }
                  },
                  magnitudeB: {
                    $sqrt: {
                      $reduce: {
                        input: queryEmbedding,
                        initialValue: 0,
                        in: { $add: ["$$value", { $multiply: ["$$this", "$$this"] }] }
                      }
                    }
                  }
                },
                in: {
                  $divide: [
                    "$$dotProduct",
                    { $multiply: ["$$magnitudeA", "$$magnitudeB"] }
                  ]
                }
              }
            }
          }
        },
        {
          $match: {
            similarity: { $gte: threshold }
          }
        },
        {
          $sort: { similarity: -1 }
        },
        {
          $limit: limit
        }
      ];

      const results = await this.collection.aggregate(pipeline).toArray();
      // Ensure all required properties are present in the returned objects
      return results.map(doc => ({
        _id: doc._id?.toString(),
        content: doc.chunk_text ?? "",
        metadata: doc.metadata ?? {},
        embedding: Array.isArray(doc.embedding) ? doc.embedding : [],
      })) as KnowledgeDocument[];
    } catch (error) {
      console.error('Failed to search similar documents:', error);
      throw error;
    }
  }

  /**
   * Retrieves all documents from the knowledge base collection.
   * 
   * @returns A promise that resolves to an array of all knowledge documents
   * @throws Will throw an error if the operation fails
   */
  async getAllDocuments(): Promise<KnowledgeDocument[]> {
    try {
      return await this.collection.find({}).toArray();
    } catch (error) {
      console.error('Failed to get all documents:', error);
      throw error;
    }
  }

  /**
   * Performs keyword search using MongoDB Atlas Search with BM25 algorithm.
   * 
   * @param query - The search query string
   * @param limit - Maximum number of results to return (default: 5)
   * @returns A promise that resolves to an array of knowledge documents sorted by relevance score
   * @throws Will throw an error if the search operation fails
   * 
   * @remarks
   * Requires MongoDB Atlas Search index named "chunk_text_atlas_search" to be configured.
   * Searches in the "chunk_text" field of documents.
   */
  async searchAtlas(query: string, limit: number = 5): Promise<KnowledgeDocument[]> {
    try {
      // Use MongoDB Atlas Search with BM25 algorithm
      const pipeline = [
        {
          $search: {
            index: "chunk_text_atlas_search",
            text: {
              query: query,
              path: "chunk_text", // Search in the chunk_text field
              score: { boost: { value: 1 } }
            }
          }
        },
        {
          $limit: limit
        },
        {
          $project: {
            _id: 1,
            chunk_text: 1,
            metadata: 1,
            embedding: 1,
            score: { $meta: "searchScore" }
          }
        }
      ];

      const results = await this.collection.aggregate(pipeline).toArray();
      
      // Convert to KnowledgeDocument format
      return results.map(doc => ({
        _id: doc._id?.toString(),
        content: doc.chunk_text ?? "",
        metadata: doc.metadata ?? {},
        embedding: Array.isArray(doc.embedding) ? doc.embedding : [],
        score: doc.score // Include the search score
      })) as KnowledgeDocument[];
    } catch (error) {
      console.error('Failed to search with Atlas Search:', error);
      throw error;
    }
  }

  /**
   * Gets the total count of documents in the knowledge base collection.
   * 
   * @returns A promise that resolves to the number of documents in the collection
   * @throws Will throw an error if the operation fails
   */
  async getDocumentCount(): Promise<number> {
    try {
      return await this.collection.countDocuments();
    } catch (error) {
      console.error('Failed to get document count:', error);
      throw error;
    }
  }
}

export const mongodbService = new MongoDBService();
