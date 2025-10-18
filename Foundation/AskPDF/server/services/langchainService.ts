import { ChatOpenAI } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { RunnableSequence } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";

export interface LLMConfig {
  openaiApiKey: string;
  openaiBaseUrl?: string;
  openaiApiVersion?: string;
  chatModel?: string;
  queryExpansionModel?: string;
  enableQueryExpansion?: boolean;
}

export interface LLMParameters {
  temperature: number;
  topP: number;
  maxTokens: number;
  frequencyPenalty: number;
  presencePenalty: number;
}

export class LangChainService {
  private chatModel!: ChatOpenAI;
  private queryExpansionModel!: ChatOpenAI;
  private config: LLMConfig;

  constructor(config: LLMConfig) {
    this.config = config;
    this.initializeModels();
  }

  private initializeModels(): void {
    // Set Azure OpenAI environment variables for chat model
    process.env.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = this.config.chatModel || "gpt-4o-mini";
    
    // Initialize main chat model
    this.chatModel = new ChatOpenAI({
      openAIApiKey: this.config.openaiApiKey,
      modelName: this.config.chatModel || "gpt-4o-mini",
      temperature: 0.7,
      configuration: {
        baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
        defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
      },
    });

    // Initialize query expansion model
    this.queryExpansionModel = new ChatOpenAI({
      openAIApiKey: this.config.openaiApiKey,
      modelName: this.config.queryExpansionModel || this.config.chatModel || "gpt-4o-mini",
      temperature: 0.3, // Lower temperature for more consistent expansion
      configuration: {
        baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
        defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
      },
    });
  }

  /**
   * Generate a response using the chat model with custom parameters
   */
  async generateResponse(
    prompt: string, 
    parameters?: Partial<LLMParameters>
  ): Promise<string> {
    try {
      // Create a chat model with the specified parameters
      const chatModel = parameters ? new ChatOpenAI({
        openAIApiKey: this.config.openaiApiKey,
        modelName: this.config.chatModel || "gpt-4o-mini",
        temperature: parameters.temperature || 0.7,
        topP: parameters.topP || 1.0,
        maxTokens: parameters.maxTokens || 2048,
        frequencyPenalty: parameters.frequencyPenalty || 0,
        presencePenalty: parameters.presencePenalty || 0,
        configuration: {
          baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
          defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
        },
      }) : this.chatModel;

      // Add word limit instruction to the prompt
      const limitedPrompt = `${prompt}\n\nIMPORTANT: Please keep your response concise and limit it to approximately 300 words maximum.`;
      
      const response = await chatModel.invoke(limitedPrompt);
      return response.content as string;
    } catch (error) {
      console.error("Error generating response:", error);
      throw new Error("Failed to generate response");
    }
  }

  /**
   * Expand a query using the query expansion model
   */
  async expandQuery(query: string): Promise<string> {
    if (!this.config.enableQueryExpansion) {
      return query;
    }

    try {
      const expansionPrompt = PromptTemplate.fromTemplate(`
        You are a helpful assistant that expands search queries to improve document retrieval.
        Given a user query, generate an expanded version that includes:
        1. Synonyms and related terms
        2. Technical terms that might be relevant
        3. Different ways to phrase the same question
        4. Context that might help find relevant documents

        Original query: {query}

        Expanded query (keep it concise but comprehensive):
      `);

      const expansionModel = new ChatOpenAI({
        openAIApiKey: this.config.openaiApiKey,
        modelName: this.config.queryExpansionModel || this.config.chatModel || "gpt-4o-mini",
        temperature: 0.3,
        configuration: {
          baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
          defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
        },
      });

      const chain = RunnableSequence.from([
        expansionPrompt,
        expansionModel,
        new StringOutputParser(),
      ]);

      const expandedQuery = await chain.invoke({ query });
      return expandedQuery.trim();
    } catch (error) {
      console.error("Error expanding query:", error);
      // Return original query if expansion fails
      return query;
    }
  }

  /**
   * Generate a RAG response using context and query
   */
  async generateRAGResponse(
    query: string,
    context: string,
    parameters?: Partial<LLMParameters>
  ): Promise<string> {
    try {
      const ragPrompt = PromptTemplate.fromTemplate(`
        You are a helpful assistant that answers questions based on the provided context.
        Use the context to answer the question accurately and comprehensively.
        If the context doesn't contain enough information to answer the question, say so.
        
        IMPORTANT: Keep your answer concise and limit it to approximately 300 words maximum.

        Context:
        {context}

        Question: {query}

        Answer (max 300 words):
      `);

      const chatModel = parameters ? new ChatOpenAI({
        openAIApiKey: this.config.openaiApiKey,
        modelName: this.config.chatModel || "gpt-4o-mini",
        temperature: parameters.temperature || 0.7,
        topP: parameters.topP || 1.0,
        maxTokens: parameters.maxTokens || 2048,
        frequencyPenalty: parameters.frequencyPenalty || 0,
        presencePenalty: parameters.presencePenalty || 0,
        configuration: {
          baseURL: this.config.openaiBaseUrl || "https://api.openai.com/v1",
          defaultQuery: { "api-version": this.config.openaiApiVersion || "2024-07-18" },
        },
      }) : this.chatModel;

      const chain = RunnableSequence.from([
        ragPrompt,
        chatModel,
        new StringOutputParser(),
      ]);

      const response = await chain.invoke({ query, context });
      return response.trim();
    } catch (error) {
      console.error("Error generating RAG response:", error);
      throw new Error("Failed to generate RAG response");
    }
  }

  /**
   * Get the current configuration
   */
  getConfig(): LLMConfig {
    return { ...this.config };
  }

  /**
   * Update configuration (useful for dynamic parameter changes)
   */
  updateConfig(newConfig: Partial<LLMConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.initializeModels();
  }
}
