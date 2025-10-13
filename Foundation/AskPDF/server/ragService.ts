import { MongoClient } from "mongodb";
import { OpenAIEmbeddings } from "@langchain/openai";
import { MongoDBAtlasVectorSearch } from "@langchain/mongodb";
import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";

export interface RAGConfig {
  mongoUri: string;
  databaseName: string;
  collectionName: string;
  openaiApiKey: string;
  openaiBaseUrl?: string;
  openaiApiVersion?: string;
  azureInstanceName?: string;
  embeddingModel?: string;
  embeddingApiVersion?: string;
  embeddingBaseUrl?: string;
  chatModel?: string;
  enableQueryExpansion?: boolean;
  queryExpansionModel?: string;
}

export interface RAGResponse {
  answer: string;
  sources: Array<{
    content: string;
    metadata?: any;
    score?: number;
  }>;
}

export interface LLMParameters {
  temperature: number;
  topP: number;
  maxTokens: number;
  frequencyPenalty: number;
  presencePenalty: number;
}

// Simple BM25 implementation
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
    this.avgDocLength = documents.reduce((sum, doc) => sum + this.tokenize(doc).length, 0) / this.totalDocs;
    this.buildIndex();
  }

  private tokenize(text: string): string[] {
    return text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(token => token.length > 0);
  }

  private buildIndex(): void {
    this.documentFreqs.clear();
    
    for (const doc of this.documents) {
      const tokens = this.tokenize(doc);
      const uniqueTokens = new Set(tokens);
      
      for (const token of Array.from(uniqueTokens)) {
        this.documentFreqs.set(token, (this.documentFreqs.get(token) || 0) + 1);
      }
    }
  }

  search(query: string): number[] {
    const queryTokens = this.tokenize(query);
    const scores: number[] = [];

    for (let i = 0; i < this.documents.length; i++) {
      const doc = this.documents[i];
      const docTokens = this.tokenize(doc);
      const docLength = docTokens.length;
      
      let score = 0;
      const termFreqs = new Map<string, number>();
      
      // Count term frequencies in document
      for (const token of docTokens) {
        termFreqs.set(token, (termFreqs.get(token) || 0) + 1);
      }

      // Calculate BM25 score for each query term
      for (const term of queryTokens) {
        const tf = termFreqs.get(term) || 0;
        const df = this.documentFreqs.get(term) || 0;
        
        if (df > 0) {
          const idf = Math.log((this.totalDocs - df + 0.5) / (df + 0.5));
          const tfScore = (tf * (this.k1 + 1)) / (tf + this.k1 * (1 - this.b + this.b * (docLength / this.avgDocLength)));
          score += idf * tfScore;
        }
      }
      
      scores.push(score);
    }

    return scores;
  }
}

export class RAGService {
  private client: MongoClient;
  private embeddings: OpenAIEmbeddings;
  private vectorStore!: MongoDBAtlasVectorSearch;
  private chatModel: ChatOpenAI;
  private queryExpansionModel: ChatOpenAI;
  private config: RAGConfig;
  private bm25Index: SimpleBM25 | null = null;
  private documents: Array<{ id: string; text: string; metadata?: any }> = [];

  constructor(config: RAGConfig) {
    this.config = config;
    this.client = new MongoClient(config.mongoUri);
    this.embeddings = new OpenAIEmbeddings({
      openAIApiKey: config.openaiApiKey,
      modelName: config.embeddingModel,
      configuration: {
        baseURL: config.embeddingBaseUrl,
        defaultQuery: { "api-version": config.embeddingApiVersion || "2023-05-15" },
      },
    });
    // Set Azure OpenAI environment variables for chat model
    process.env.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = config.chatModel || "gpt-4o-mini";
    
    this.chatModel = new ChatOpenAI({
      openAIApiKey: config.openaiApiKey,
      modelName: config.chatModel || "gpt-4o-mini",
      temperature: 0.7,
      configuration: {
        baseURL: config.openaiBaseUrl || "https://api.openai.com/v1",
        defaultQuery: { "api-version": config.openaiApiVersion || "2024-07-18" },
      },
    });

    // Initialize query expansion model (can be same as chat model or different)
    this.queryExpansionModel = new ChatOpenAI({
      openAIApiKey: config.openaiApiKey,
      modelName: config.queryExpansionModel || config.chatModel || "gpt-4o-mini",
      temperature: 0.3, // Lower temperature for more consistent expansion
      configuration: {
        baseURL: config.openaiBaseUrl || "https://api.openai.com/v1",
        defaultQuery: { "api-version": config.openaiApiVersion || "2024-07-18" },
      },
    });
  }

  async initialize(): Promise<void> {
    try {
      console.log("RAG Service Configuration:");
      console.log("- Base URL:", this.config.openaiBaseUrl);
      console.log("- API Version:", this.config.openaiApiVersion);
      console.log("- Azure Instance Name:", this.config.azureInstanceName);
      console.log("- Embedding Model:", this.config.embeddingModel);
      console.log("- Chat Model:", this.config.chatModel);
      console.log("- Query Expansion Enabled:", this.config.enableQueryExpansion);
      console.log("- Query Expansion Model:", this.config.queryExpansionModel);
      console.log("- MongoDB URI:", this.config.mongoUri);
      console.log("- Database:", this.config.databaseName);
      console.log("- Collection:", this.config.collectionName);
      
      await this.client.connect();
      console.log("Connected to MongoDB");

      // Initialize vector store
      this.vectorStore = new MongoDBAtlasVectorSearch(this.embeddings, {
        collection: this.client.db(this.config.databaseName).collection(this.config.collectionName),
        indexName: "vector_index", // Adjust based on your Atlas Vector Search index
        textKey: "text", // Your document structure uses "text" field
        embeddingKey: "embedding", // Your document structure uses "embedding" field
      });

      // Load documents for BM25 indexing
      await this.loadDocumentsForBM25();
console.log(this.vectorStore);
      console.log("RAG service initialized successfully");
    } catch (error) {
      console.error("Failed to initialize RAG service:", error);
      throw error;
    }
  }

  private async loadDocumentsForBM25(): Promise<void> {
    try {
      const db = this.client.db(this.config.databaseName);
      const collection = db.collection(this.config.collectionName);
      
      // Load documents with your specific structure
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

  async search(query: string, k: number = 5, llmParams?: LLMParameters): Promise<RAGResponse> {
    try {
      // Expand query if enabled
      const expandedQuery = this.config.enableQueryExpansion 
        ? await this.expandQuery(query, llmParams) 
        : query;

      // Perform hybrid search: 75% semantic + 25% BM25
      const [semanticResults, bm25Results] = await Promise.all([
        this.performSemanticSearch(expandedQuery, k * 2), // Get more results for better hybrid scoring
        this.performBM25Search(expandedQuery, k * 2),
      ]);

      // Combine and score results
      const hybridResults = this.combineSearchResults(semanticResults, bm25Results, k);

      // Extract sources
      const sources = hybridResults.map(result => ({
        content: result.content,
        metadata: result.metadata,
        score: result.finalScore,
        searchType: result.searchType,
      }));

      // Create context from retrieved documents
      const context = sources.map(source => source.content).join("\n\n");

      // Create prompt template
      const promptTemplate = PromptTemplate.fromTemplate(`
You are a helpful AI assistant. Use the following context to answer the user's question. 
If the context doesn't contain enough information to answer the question, say so.

Context:
{context}

Question: {question}

Answer:`);

      // Create a chat model with the specified parameters
      const chatModel = llmParams ? new ChatOpenAI({
        openAIApiKey: this.config.openaiApiKey,
        modelName: this.config.chatModel || "gpt-4o-mini",
        temperature: llmParams.temperature,
        maxTokens: llmParams.maxTokens,
        topP: llmParams.topP,
        frequencyPenalty: llmParams.frequencyPenalty,
        presencePenalty: llmParams.presencePenalty,
        configuration: {
          baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
          defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
        },
      }) : this.chatModel;

      // Create the chain
      const chain = RunnableSequence.from([
        promptTemplate,
        chatModel,
        new StringOutputParser(),
      ]);

      // Generate response
      const answer = await chain.invoke({
        context,
        question: query,
      });

      return {
        answer,
        sources,
      };
    } catch (error) {
      console.error("Error in RAG search:", error);
      throw new Error(`RAG search failed: ${error instanceof Error ? error.message : String(error)}`);
    }
  }

  private async expandQuery(originalQuery: string, llmParams?: LLMParameters): Promise<string> {
    try {
      const expansionPrompt = PromptTemplate.fromTemplate(`
You are a helpful assistant that expands search queries to improve document retrieval. 
Your task is to enhance the user's query by adding relevant synonyms, related terms, and alternative phrasings 
that would help find more comprehensive information.

Original query: {query}

Please provide an expanded version that includes:
1. Synonyms and alternative terms
2. Related concepts and terminology
3. Different ways to phrase the same question
4. Technical terms that might be relevant

Keep the expanded query concise but comprehensive. Return only the expanded query, no explanations.

Expanded query:`);

      // Use the same parameters for query expansion, but with lower temperature for consistency
      const expansionModel = llmParams ? new ChatOpenAI({
        openAIApiKey: this.config.openaiApiKey,
        modelName: this.config.queryExpansionModel || this.config.chatModel || "gpt-4o-mini",
        temperature: Math.min(llmParams.temperature, 0.3), // Cap at 0.3 for more consistent expansion
        maxTokens: Math.min(llmParams.maxTokens, 512), // Limit tokens for expansion
        topP: llmParams.topP,
        frequencyPenalty: llmParams.frequencyPenalty,
        presencePenalty: llmParams.presencePenalty,
        configuration: {
          baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
          defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
        },
      }) : this.queryExpansionModel;

      const expansionChain = RunnableSequence.from([
        expansionPrompt,
        expansionModel,
        new StringOutputParser(),
      ]);

      const expandedQuery = await expansionChain.invoke({ query: originalQuery });
      
      // Log for debugging (remove in production)
      console.log(`Query expansion: "${originalQuery}" -> "${expandedQuery}"`);
      
      return expandedQuery.trim();
    } catch (error) {
      console.error("Query expansion failed:", error);
      // Fallback to original query if expansion fails
      return originalQuery;
    }
  }

  private async performSemanticSearch(query: string, k: number): Promise<Array<{ content: string; metadata?: any; score: number; id: string }>> {
    try {
      const searchResults = await this.vectorStore.similaritySearchWithScore(query, k);
      return searchResults.map(([doc, score]) => ({
        content: doc.pageContent,
        metadata: doc.metadata,
        score: score,
        id: doc.metadata?._id || Math.random().toString(),
      }));
    } catch (error) {
      console.error("Semantic search failed:", error);
      return [];
    }
  }

  private performBM25Search(query: string, k: number): Array<{ content: string; metadata?: any; score: number; id: string }> {
    if (!this.bm25Index) {
      console.warn("BM25 index not available, skipping keyword search");
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
      console.error("BM25 search failed:", error);
      return [];
    }
  }

  private combineSearchResults(
    semanticResults: Array<{ content: string; metadata?: any; score: number; id: string }>,
    bm25Results: Array<{ content: string; metadata?: any; score: number; id: string }>,
    k: number
  ): Array<{ content: string; metadata?: any; finalScore: number; searchType: string; id: string }> {
    
    // Use Reciprocal Rank Fusion (RRF) for better ranking combination
    return this.reciprocalRankFusion(semanticResults, bm25Results, k);
  }

  private reciprocalRankFusion(
    semanticResults: Array<{ content: string; metadata?: any; score: number; id: string }>,
    bm25Results: Array<{ content: string; metadata?: any; score: number; id: string }>,
    k: number,
    kParam: number = 60 // RRF parameter, typically 60
  ): Array<{ content: string; metadata?: any; finalScore: number; searchType: string; id: string }> {
    
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

  async close(): Promise<void> {
    await this.client.close();
  }
}

// Singleton instance
let ragService: RAGService | null = null;

export function getRAGService(): RAGService {
  if (!ragService) {
    const config: RAGConfig = {
      mongoUri: process.env.MONGODB_URI || "",
      databaseName: process.env.MONGODB_DATABASE || "doc-analysis",
      collectionName: process.env.MONGODB_COLLECTION || "document_chunks",
      openaiApiKey: process.env.OPENAI_API_KEY || "",
      openaiBaseUrl: process.env.OPENAI_BASE_URL || "https://test-poc1-rag-openai.openai.azure.com/",
      openaiApiVersion: process.env.OPENAI_API_VERSION || "2025-01-01-preview",
      azureInstanceName: process.env.AZURE_INSTANCE_NAME || "test-poc1-rag-openai",
      embeddingModel: process.env.EMBEDDING_MODEL || "text-embedding-ada-002",
      embeddingApiVersion: process.env.OPENAI_EMBDEDDING_MODEL_API_VERSION || "2023-05-15",
      embeddingBaseUrl: process.env.OPENAI_EMBEDDING_BASE_URL || "https://test-poc1-rag-openai.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15",
      chatModel: process.env.CHAT_MODEL || "gpt-4o-mini",
      enableQueryExpansion: process.env.ENABLE_QUERY_EXPANSION === "true" || false,
      queryExpansionModel: process.env.QUERY_EXPANSION_MODEL || process.env.CHAT_MODEL || "gpt-4o-mini",
    };

    if (!config.openaiApiKey) {
      throw new Error("OPENAI_API_KEY environment variable is required");
    }

    ragService = new RAGService(config);
  }
  return ragService;
}
