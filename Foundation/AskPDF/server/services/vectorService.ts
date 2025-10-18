import { MongoClient } from "mongodb";
import { OpenAIEmbeddings } from "@langchain/openai";
import { MongoDBAtlasVectorSearch } from "@langchain/mongodb";

export interface VectorConfig {
  mongoUri: string;
  databaseName: string;
  collectionName: string;
  openaiApiKey: string;
  embeddingModel?: string;
  embeddingApiVersion?: string;
  embeddingBaseUrl?: string;
}

export interface SearchResult {
  content: string;
  metadata?: any;
  score: number;
  id: string;
}

export interface VectorSearchResult {
  content: string;
  metadata?: any;
  finalScore: number;
  searchType: string;
  id: string;
}

// Simple BM25 implementation for keyword search
class SimpleBM25 {
  private documents: string[] = [];
  private documentFreqs: Map<string, number> = new Map();
  private totalDocs: number = 0;
  private avgDocLength: number = 0;
  private k1: number = 1.2;
  private b: number = 0.75;

  constructor(documents: string[]) {
    this.documents = documents;
    this.totalDocs = documents.length;
    this.avgDocLength = documents.reduce((sum, doc) => sum + doc.split(' ').length, 0) / this.totalDocs;
    this.buildDocumentFrequencies();
  }

  private buildDocumentFrequencies(): void {
    this.documentFreqs.clear();
    
    for (const doc of this.documents) {
      const terms = new Set(doc.toLowerCase().split(/\s+/));
      for (const term of Array.from(terms)) {
        this.documentFreqs.set(term, (this.documentFreqs.get(term) || 0) + 1);
      }
    }
  }

  search(query: string): number[] {
    const queryTerms = query.toLowerCase().split(/\s+/);
    const scores: number[] = [];

    for (let i = 0; i < this.documents.length; i++) {
      const doc = this.documents[i];
      const docTerms = doc.toLowerCase().split(/\s+/);
      const docLength = docTerms.length;
      
      let score = 0;
      
      for (const term of queryTerms) {
        const termFreq = docTerms.filter(t => t === term).length;
        const docFreq = this.documentFreqs.get(term) || 0;
        
        if (docFreq === 0) continue;
        
        // Calculate BM25 score for each query term
        const idf = Math.log((this.totalDocs - docFreq + 0.5) / (docFreq + 0.5));
        const tfScore = (termFreq * (this.k1 + 1)) / 
                       (termFreq + this.k1 * (1 - this.b + this.b * (docLength / this.avgDocLength)));
        
        score += idf * tfScore;
      }
      
      scores.push(score);
    }

    return scores;
  }
}

export class VectorService {
  private client: MongoClient;
  private embeddings!: OpenAIEmbeddings;
  private vectorStore!: MongoDBAtlasVectorSearch;
  private config: VectorConfig;
  private bm25Index: SimpleBM25 | null = null;
  private documents: Array<{ id: string; text: string; metadata?: any }> = [];

  constructor(config: VectorConfig) {
    this.config = config;
    this.client = new MongoClient(config.mongoUri);
    this.initializeEmbeddings();
  }

  private initializeEmbeddings(): void {
    this.embeddings = new OpenAIEmbeddings({
      openAIApiKey: this.config.openaiApiKey,
      modelName: this.config.embeddingModel,
      configuration: {
        baseURL: this.config.embeddingBaseUrl,
        defaultQuery: { "api-version": this.config.embeddingApiVersion || "2023-05-15" },
      },
    });
  }

  /**
   * Initialize the vector service
   */
  async initialize(): Promise<void> {
    try {
      console.log("Vector Service Configuration:");
      console.log("- Embedding Model:", this.config.embeddingModel);
      console.log("- MongoDB URI:", this.config.mongoUri);
      console.log("- Database:", this.config.databaseName);
      console.log("- Collection:", this.config.collectionName);
      
      await this.client.connect();
      console.log("Connected to MongoDB");

      // Initialize vector store
      this.vectorStore = new MongoDBAtlasVectorSearch(this.embeddings, {
        collection: this.client.db(this.config.databaseName).collection(this.config.collectionName),
        indexName: "vector_index",
        textKey: "text",
        embeddingKey: "embedding",
      });

      // Load documents for BM25 indexing
      await this.loadDocumentsForBM25();
      console.log("Vector service initialized successfully");
    } catch (error) {
      console.error("Failed to initialize vector service:", error);
      throw error;
    }
  }

  /**
   * Load documents for BM25 indexing
   */
  private async loadDocumentsForBM25(): Promise<void> {
    try {
      const db = this.client.db(this.config.databaseName);
      const collection = db.collection(this.config.collectionName);
      
      // Load documents with specific structure
      const docs = await collection.find({}, { 
        projection: { 
          _id: 1, 
          text: 1, 
          page_number: 1,
          chunk_index: 1,
          document_id: 1,
          document_name: 1,
          document_path: 1,
          global_chunk_index: 1,
          char_count: 1,
          word_count: 1,
          is_complete_page: 1
        } 
      }).toArray();
      
      this.documents = docs.map(doc => ({
        id: doc._id.toString(),
        text: doc.text,
        metadata: {
          page_number: doc.page_number,
          chunk_index: doc.chunk_index,
          document_id: doc.document_id,
          document_name: doc.document_name,
          document_path: doc.document_path,
          global_chunk_index: doc.global_chunk_index,
          char_count: doc.char_count,
          word_count: doc.word_count,
          is_complete_page: doc.is_complete_page,
        },
      }));

      // Create BM25 index
      const texts = this.documents.map(doc => doc.text);
      this.bm25Index = new SimpleBM25(texts);
      
      console.log(`Loaded ${this.documents.length} documents for BM25 indexing`);
    } catch (error) {
      console.error("Failed to load documents for BM25:", error instanceof Error ? error.message : String(error));
      // Continue without BM25 if it fails
    }
  }

  /**
   * Perform semantic search using vector embeddings
   */
  async performSemanticSearch(query: string, k: number): Promise<SearchResult[]> {
    try {
      const searchResults = await this.vectorStore.similaritySearchWithScore(query, k);
      return searchResults.map(([doc, score]) => ({
        content: doc.pageContent,
        metadata: doc.metadata,
        score: score,
        id: doc.metadata?._id || Math.random().toString(),
      }));
    } catch (error) {
      console.error("Error in semantic search:", error);
      return [];
    }
  }

  /**
   * Perform BM25 keyword search
   */
  performBM25Search(query: string, k: number): SearchResult[] {
    if (!this.bm25Index) {
      console.warn("BM25 index not available");
      return [];
    }

    try {
      const scores = this.bm25Index.search(query);
      const results = scores
        .map((score, index) => ({
          content: this.documents[index].text,
          metadata: this.documents[index].metadata,
          score: score,
          id: this.documents[index].id,
        }))
        .filter(result => result.score > 0)
        .sort((a, b) => b.score - a.score)
        .slice(0, k);

      return results;
    } catch (error) {
      console.error("Error in BM25 search:", error);
      return [];
    }
  }

  /**
   * Perform hybrid search combining semantic and BM25 results
   */
  async performHybridSearch(query: string, k: number): Promise<VectorSearchResult[]> {
    try {
      // Perform both searches in parallel
      const [semanticResults, bm25Results] = await Promise.all([
        this.performSemanticSearch(query, k),
        Promise.resolve(this.performBM25Search(query, k))
      ]);

      // Combine results using Reciprocal Rank Fusion
      return this.combineSearchResults(semanticResults, bm25Results, k);
    } catch (error) {
      console.error("Error in hybrid search:", error);
      return [];
    }
  }

  /**
   * Combine search results using Reciprocal Rank Fusion (RRF)
   */
  private combineSearchResults(
    semanticResults: SearchResult[],
    bm25Results: SearchResult[],
    k: number
  ): VectorSearchResult[] {
    return this.reciprocalRankFusion(semanticResults, bm25Results, k);
  }

  /**
   * Reciprocal Rank Fusion algorithm
   */
  private reciprocalRankFusion(
    semanticResults: SearchResult[],
    bm25Results: SearchResult[],
    k: number,
    kParam: number = 60 // RRF parameter, typically 60
  ): VectorSearchResult[] {
    
    const documentScores = new Map<string, {
      content: string;
      metadata?: any;
      rrfScore: number;
      semanticRank: number;
      bm25Rank: number;
      semanticScore: number;
      bm25Score: number;
      id: string;
    }>();

    // Process semantic results
    semanticResults.forEach((result, index) => {
      const rank = index + 1;
      const rrfScore = 1 / (kParam + rank);
      
      documentScores.set(result.id, {
        content: result.content,
        metadata: result.metadata,
        rrfScore,
        semanticRank: rank,
        bm25Rank: Infinity, // Will be updated if found in BM25 results
        semanticScore: result.score,
        bm25Score: 0,
        id: result.id,
      });
    });

    // Process BM25 results and combine scores
    bm25Results.forEach((result, index) => {
      const rank = index + 1;
      const rrfScore = 1 / (kParam + rank);
      
      const existing = documentScores.get(result.id);
      if (existing) {
        // Document exists in both results - combine RRF scores
        existing.rrfScore += rrfScore;
        existing.bm25Rank = rank;
        existing.bm25Score = result.score;
      } else {
        // Document only in BM25 results
        documentScores.set(result.id, {
          content: result.content,
          metadata: result.metadata,
          rrfScore,
          semanticRank: Infinity,
          bm25Rank: rank,
          semanticScore: 0,
          bm25Score: result.score,
          id: result.id,
        });
      }
    });

    // Convert to array and sort by RRF score
    const finalResults = Array.from(documentScores.values())
      .sort((a, b) => b.rrfScore - a.rrfScore)
      .slice(0, k)
      .map(result => {
        // Determine search type based on which rank is better
        const searchType = result.semanticRank < result.bm25Rank ? 'semantic' : 'keyword';
        
        // Normalize RRF score to 0-1 range for display
        const maxPossibleScore = 2 / kParam; // Maximum possible RRF score (when rank=1 in both)
        const normalizedScore = Math.min(result.rrfScore / maxPossibleScore, 1);
        
        return {
          content: result.content,
          metadata: result.metadata,
          finalScore: normalizedScore,
          searchType,
          id: result.id,
        };
      });

    return finalResults;
  }

  /**
   * Get document statistics
   */
  getDocumentStats(): { totalDocuments: number; avgChunkSize: number } {
    const totalDocuments = this.documents.length;
    const avgChunkSize = totalDocuments > 0 
      ? this.documents.reduce((sum, doc) => sum + doc.text.length, 0) / totalDocuments 
      : 0;

    return { totalDocuments, avgChunkSize };
  }

  /**
   * Close the MongoDB connection
   */
  async close(): Promise<void> {
    await this.client.close();
  }
}
