import { LangChainService, LLMParameters } from "./langchainService";
import { VectorService, VectorSearchResult } from "./vectorService";

export interface RAGConfig {
  // LangChain Configuration
  openaiApiKey: string;
  openaiBaseUrl?: string;
  openaiApiVersion?: string;
  azureInstanceName?: string;
  chatModel?: string;
  enableQueryExpansion?: boolean;
  queryExpansionModel?: string;

  // Vector Service Configuration
  mongoUri: string;
  databaseName: string;
  collectionName: string;
  embeddingModel?: string;
  embeddingApiVersion?: string;
  embeddingBaseUrl?: string;
}

export interface RAGResponse {
  answer: string;
  sources: Array<{
    content: string;
    metadata?: any;
    score?: number;
    searchType?: string;
  }>;
}

export class RAGOrchestrator {
  private langchainService!: LangChainService;
  private vectorService!: VectorService;
  private config: RAGConfig;

  constructor(config: RAGConfig) {
    this.config = config;
    this.initializeServices();
  }

  private initializeServices(): void {
    // Initialize LangChain service
    this.langchainService = new LangChainService({
      openaiApiKey: this.config.openaiApiKey,
      openaiBaseUrl: this.config.openaiBaseUrl,
      openaiApiVersion: this.config.openaiApiVersion,
      chatModel: this.config.chatModel,
      queryExpansionModel: this.config.queryExpansionModel,
      enableQueryExpansion: this.config.enableQueryExpansion,
    });

    // Initialize Vector service
    this.vectorService = new VectorService({
      mongoUri: this.config.mongoUri,
      databaseName: this.config.databaseName,
      collectionName: this.config.collectionName,
      openaiApiKey: this.config.openaiApiKey,
      embeddingModel: this.config.embeddingModel,
      embeddingApiVersion: this.config.embeddingApiVersion,
      embeddingBaseUrl: this.config.embeddingBaseUrl,
    });
  }

  /**
   * Initialize the RAG orchestrator and all its services
   */
  async initialize(): Promise<void> {
    try {
      console.log("Initializing RAG Orchestrator...");
      await this.vectorService.initialize();
      console.log("RAG Orchestrator initialized successfully");
    } catch (error) {
      console.error("Failed to initialize RAG Orchestrator:", error);
      throw error;
    }
  }

  /**
   * Perform RAG search with query expansion and hybrid retrieval
   */
  async search(
    query: string, 
    k: number = 5, 
    llmParams?: LLMParameters
  ): Promise<RAGResponse> {
    try {
      console.log(`Processing query: "${query}" with k=${k}`);

      // Step 1: Query Expansion (if enabled)
      const expandedQuery = await this.langchainService.expandQuery(query);
      console.log(`Expanded query: "${expandedQuery}"`);

      // Step 2: Hybrid Search (Semantic + BM25)
      const searchResults = await this.vectorService.performHybridSearch(expandedQuery, k);
      console.log(`Found ${searchResults.length} relevant documents`);

      if (searchResults.length === 0) {
        return {
          answer: "I couldn't find any relevant information in the documents to answer your question.",
          sources: [],
        };
      }

      // Step 3: Context Assembly
      const context = this.assembleContext(searchResults);
      console.log(`Assembled context length: ${context.length} characters`);

      // Step 4: Generate Response
      const answer = await this.langchainService.generateRAGResponse(
        query, 
        context, 
        llmParams
      );

      // Step 5: Format Sources
      const sources = this.formatSources(searchResults);

      return {
        answer,
        sources,
      };
    } catch (error) {
      console.error("Error in RAG search:", error);
      throw new Error("Failed to process RAG search");
    }
  }

  /**
   * Perform semantic search only
   */
  async semanticSearch(query: string, k: number = 5): Promise<VectorSearchResult[]> {
    try {
      const results = await this.vectorService.performSemanticSearch(query, k);
      return results.map(result => ({
        content: result.content,
        metadata: result.metadata,
        finalScore: result.score,
        searchType: 'semantic',
        id: result.id,
      }));
    } catch (error) {
      console.error("Error in semantic search:", error);
      return [];
    }
  }

  /**
   * Perform keyword search only
   */
  async keywordSearch(query: string, k: number = 5): Promise<VectorSearchResult[]> {
    try {
      const results = this.vectorService.performBM25Search(query, k);
      return results.map(result => ({
        content: result.content,
        metadata: result.metadata,
        finalScore: result.score,
        searchType: 'keyword',
        id: result.id,
      }));
    } catch (error) {
      console.error("Error in keyword search:", error);
      return [];
    }
  }

  /**
   * Generate a response without document retrieval (direct LLM call)
   */
  async generateDirectResponse(
    query: string, 
    llmParams?: LLMParameters
  ): Promise<string> {
    try {
      return await this.langchainService.generateResponse(query, llmParams);
    } catch (error) {
      console.error("Error generating direct response:", error);
      throw new Error("Failed to generate direct response");
    }
  }

  /**
   * Expand a query using the query expansion model
   */
  async expandQuery(query: string): Promise<string> {
    try {
      return await this.langchainService.expandQuery(query);
    } catch (error) {
      console.error("Error expanding query:", error);
      return query; // Return original query if expansion fails
    }
  }

  /**
   * Assemble context from search results
   */
  private assembleContext(searchResults: VectorSearchResult[]): string {
    const contextParts = searchResults.map((result, index) => {
      const sourceInfo = result.metadata?.document_name 
        ? `[Source ${index + 1}: ${result.metadata.document_name}`
        : `[Source ${index + 1}`;
      
      const pageInfo = result.metadata?.page_number 
        ? `, Page ${result.metadata.page_number}`
        : '';
      
      const chunkInfo = result.metadata?.chunk_index !== undefined 
        ? `, Chunk ${result.metadata.chunk_index}`
        : '';
      
      return `${sourceInfo}${pageInfo}${chunkInfo}]\n${result.content}`;
    });

    return contextParts.join('\n\n');
  }

  /**
   * Format sources for response
   */
  private formatSources(searchResults: VectorSearchResult[]): Array<{
    content: string;
    metadata?: any;
    score?: number;
    searchType?: string;
  }> {
    return searchResults.map(result => ({
      content: result.content,
      metadata: result.metadata,
      score: result.finalScore,
      searchType: result.searchType,
    }));
  }

  /**
   * Get system statistics
   */
  getSystemStats(): {
    documentStats: { totalDocuments: number; avgChunkSize: number };
    config: RAGConfig;
  } {
    return {
      documentStats: this.vectorService.getDocumentStats(),
      config: this.config,
    };
  }

  /**
   * Update configuration
   */
  updateConfig(newConfig: Partial<RAGConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.initializeServices();
  }

  /**
   * Close all services
   */
  async close(): Promise<void> {
    await this.vectorService.close();
  }
}
