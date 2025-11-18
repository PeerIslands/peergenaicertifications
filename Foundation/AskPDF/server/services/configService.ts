import { RAGConfig } from "./ragOrchestrator";

export class ConfigService {
  private static instance: ConfigService;
  private config: RAGConfig;

  private constructor() {
    this.config = this.loadConfigFromEnvironment();
  }

  public static getInstance(): ConfigService {
    if (!ConfigService.instance) {
      ConfigService.instance = new ConfigService();
    }
    return ConfigService.instance;
  }

  private loadConfigFromEnvironment(): RAGConfig {
    // Validate required environment variables
    const requiredVars = ['OPENAI_API_KEY', 'MONGODB_URI'];
    const missingVars = requiredVars.filter(varName => !process.env[varName]);
    
    if (missingVars.length > 0) {
      throw new Error(`Missing required environment variables: ${missingVars.join(', ')}`);
    }

    return {
      // LangChain Configuration
      openaiApiKey: process.env.OPENAI_API_KEY!,
      openaiBaseUrl: process.env.OPENAI_BASE_URL || "https://test-poc1-rag-openai.openai.azure.com/",
      openaiApiVersion: process.env.OPENAI_API_VERSION || "2025-01-01-preview",
      azureInstanceName: process.env.AZURE_INSTANCE_NAME || "test-poc1-rag-openai",
      chatModel: process.env.CHAT_MODEL || "gpt-4o-mini",
      enableQueryExpansion: process.env.ENABLE_QUERY_EXPANSION === "true" || false,
      queryExpansionModel: process.env.QUERY_EXPANSION_MODEL || process.env.CHAT_MODEL || "gpt-4o-mini",

      // Vector Service Configuration
      mongoUri: process.env.MONGODB_URI!,
      databaseName: process.env.MONGODB_DATABASE || "doc-analysis",
      collectionName: process.env.MONGODB_COLLECTION || "document_chunks",
      embeddingModel: process.env.EMBEDDING_MODEL || "text-embedding-ada-002",
      embeddingApiVersion: process.env.OPENAI_EMBDEDDING_MODEL_API_VERSION || "2023-05-15",
      embeddingBaseUrl: process.env.OPENAI_EMBEDDING_BASE_URL || "https://test-poc1-rag-openai.openai.azure.com/openai/deployments/text-embedding-ada-002/embeddings?api-version=2023-05-15",
    };
  }

  public getConfig(): RAGConfig {
    return { ...this.config };
  }

  public updateConfig(updates: Partial<RAGConfig>): void {
    this.config = { ...this.config, ...updates };
  }

  public validateConfig(): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate OpenAI API Key
    if (!this.config.openaiApiKey || this.config.openaiApiKey.length < 10) {
      errors.push("Invalid OpenAI API key");
    }

    // Validate MongoDB URI
    if (!this.config.mongoUri || !this.config.mongoUri.startsWith('mongodb')) {
      errors.push("Invalid MongoDB URI");
    }

    // Validate database and collection names
    if (!this.config.databaseName || this.config.databaseName.trim().length === 0) {
      errors.push("Database name is required");
    }

    if (!this.config.collectionName || this.config.collectionName.trim().length === 0) {
      errors.push("Collection name is required");
    }

    // Validate model names
    if (!this.config.chatModel || this.config.chatModel.trim().length === 0) {
      errors.push("Chat model is required");
    }

    if (!this.config.embeddingModel || this.config.embeddingModel.trim().length === 0) {
      errors.push("Embedding model is required");
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  public getConfigSummary(): Record<string, any> {
    return {
      // Safe to expose
      openaiBaseUrl: this.config.openaiBaseUrl,
      openaiApiVersion: this.config.openaiApiVersion,
      azureInstanceName: this.config.azureInstanceName,
      chatModel: this.config.chatModel,
      enableQueryExpansion: this.config.enableQueryExpansion,
      queryExpansionModel: this.config.queryExpansionModel,
      databaseName: this.config.databaseName,
      collectionName: this.config.collectionName,
      embeddingModel: this.config.embeddingModel,
      embeddingApiVersion: this.config.embeddingApiVersion,
      embeddingBaseUrl: this.config.embeddingBaseUrl,
      // Masked sensitive data
      openaiApiKey: this.maskApiKey(this.config.openaiApiKey),
      mongoUri: this.maskMongoUri(this.config.mongoUri),
    };
  }

  private maskApiKey(apiKey: string): string {
    if (apiKey.length <= 8) return "***";
    return apiKey.substring(0, 4) + "***" + apiKey.substring(apiKey.length - 4);
  }

  private maskMongoUri(uri: string): string {
    try {
      const url = new URL(uri);
      return `${url.protocol}//${url.hostname}:${url.port || '27017'}/***`;
    } catch {
      return "***";
    }
  }
}
