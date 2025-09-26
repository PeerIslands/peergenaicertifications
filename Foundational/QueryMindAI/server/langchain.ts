import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage, AIMessage, SystemMessage } from "@langchain/core/messages";
import { type Message } from "@shared/schema";
import { ragService } from "./rag";

export interface ChatContext {
  conversationId: string;
  sessionId: string;
  messages: Message[];
}

export class LangChainService {
  private llm: ChatOpenAI;

  constructor() {
    // Initialize Azure OpenAI
    this.llm = new ChatOpenAI({
      model: process.env.AZURE_OPENAI_MODEL_NAME || "gpt-4o-mini",
      openAIApiKey: process.env.AZURE_OPENAI_API_KEY,
      configuration: {
        baseURL: `${process.env.AZURE_OPENAI_ENDPOINT}openai/deployments/${process.env.AZURE_OPENAI_DEPLOYMENT_NAME}`,
        defaultQuery: {
          'api-version': process.env.AZURE_OPENAI_API_VERSION || "2024-07-18",
        },
      },
      temperature: parseFloat(process.env.AZURE_OPENAI_TEMPERATURE || "0.5"),
      maxTokens: parseInt(process.env.AZURE_OPENAI_MAX_TOKENS || "500"),
    });
  }

  /**
   * Generate AI response using LangChain with RAG
   */
  async generateResponse(
    userMessage: string,
    context: ChatContext
  ): Promise<{ content: string; responseTime: number; sources?: any[] }> {
    const startTime = Date.now();

    try {
      // Validate Azure OpenAI configuration
      if (!process.env.AZURE_OPENAI_API_KEY) {
        throw new Error("Azure OpenAI API key is not configured");
      }

      // Get RAG context
      let ragContext = '';
      let sources: any[] = [];
      
      try {
        const ragResult = await ragService.generateRAGResponse(userMessage, context);
        ragContext = ragResult.content;
        sources = ragResult.sources;
      } catch (error) {
        console.warn('RAG retrieval failed, continuing without context:', error);
      }

      // Convert database messages to LangChain format
      const langchainMessages = this.convertToLangChainMessages(context.messages, ragContext);
      
      // Add the new user message
      langchainMessages.push(new HumanMessage(userMessage));

      // Generate response with timeout
      const response = await Promise.race([
        this.llm.invoke(langchainMessages),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error("Request timeout")), 30000)
        )
      ]) as any;
      
      const responseTime = Date.now() - startTime;
      
      if (!response || !response.content) {
        throw new Error("Invalid response from AI model");
      }
      
      return {
        content: response.content as string,
        responseTime,
        sources: sources.length > 0 ? sources : undefined,
      };
    } catch (error) {
      console.error("Error generating AI response:", error);
      
      const responseTime = Date.now() - startTime;
      
      // Provide more specific error messages
      let errorMessage = "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.";
      
      if (error instanceof Error) {
        if (error.message.includes("API key")) {
          errorMessage = "Azure OpenAI API key is not configured properly.";
        } else if (error.message.includes("timeout")) {
          errorMessage = "The AI is taking longer than expected to respond. Please try again.";
        } else if (error.message.includes("connection") || error.message.includes("network")) {
          errorMessage = "Unable to connect to Azure OpenAI service. Please check your internet connection.";
        } else if (error.message.includes("quota") || error.message.includes("rate limit")) {
          errorMessage = "Azure OpenAI service is temporarily unavailable due to rate limits. Please try again later.";
        }
      }
      
      return {
        content: errorMessage,
        responseTime,
      };
    }
  }

  /**
   * Convert database messages to LangChain message format with RAG context
   */
  private convertToLangChainMessages(messages: Message[], ragContext: string = '') {
    const langchainMessages = [];

    // Add system message with RAG context
    let systemMessage = "You are a helpful AI assistant. You provide intelligent, helpful, and accurate responses to user questions. " +
      "Always be polite, informative, and engaging in your responses. Think step by step and provide clear answers. Answer in less than 10 lines.";

    if (ragContext && ragContext !== 'No relevant context found.') {
      systemMessage += `\n\nRelevant context from knowledge base:\n${ragContext}\n\nUse this context to provide more accurate and helpful responses. If the context doesn't seem relevant to the user's question, you can still provide a helpful response based on your general knowledge.`;
    }

    langchainMessages.push(new SystemMessage(systemMessage));

    // Convert conversation history
    for (const message of messages) {
      if (message.role === "user") {
        langchainMessages.push(new HumanMessage(message.content));
      } else if (message.role === "assistant") {
        langchainMessages.push(new AIMessage(message.content));
      }
    }

    return langchainMessages;
  }

  /**
   * Get conversation summary for analytics
   */
  async getConversationSummary(messages: Message[]): Promise<string> {
    if (messages.length === 0) return "No conversation yet";

    const userMessages = messages.filter(m => m.role === "user");
    const topics = userMessages.slice(0, 3).map(m => m.content.substring(0, 50));
    
    return `Topics discussed: ${topics.join(", ")}${topics.length < userMessages.length ? "..." : ""}`;
  }

  /**
   * Check if Azure OpenAI service is accessible
   */
  private async isAzureOpenAIAccessible(): Promise<boolean> {
    try {
      // Test with a simple completion request
      const testResponse = await this.llm.invoke([
        new HumanMessage("Hello")
      ]);
      
      return !!(testResponse && testResponse.content && testResponse.content.length > 0);
    } catch (error) {
      console.error("Azure OpenAI service check failed:", error);
      return false;
    }
  }

  /**
   * Validate Azure OpenAI configuration
   */
  static async validateConfiguration(): Promise<boolean> {
    try {
      // Check required environment variables
      if (!process.env.AZURE_OPENAI_API_KEY) {
        console.error("AZURE_OPENAI_API_KEY is not set in environment variables");
        return false;
      }

      if (!process.env.AZURE_OPENAI_DEPLOYMENT_NAME) {
        console.error("AZURE_OPENAI_DEPLOYMENT_NAME is not set in environment variables");
        return false;
      }

      // Test the configuration by creating a temporary instance
      const testLLM = new ChatOpenAI({
        model: process.env.AZURE_OPENAI_MODEL_NAME || "gpt-4o-mini",
        openAIApiKey: process.env.AZURE_OPENAI_API_KEY,
        configuration: {
          baseURL: `${process.env.AZURE_OPENAI_ENDPOINT}openai/deployments/${process.env.AZURE_OPENAI_DEPLOYMENT_NAME}`,
          defaultQuery: {
            'api-version': process.env.AZURE_OPENAI_API_VERSION || "2024-07-18",
          },
        },
        temperature: 0.1,
        maxTokens: 10,
      });

      // Test with a simple request
      const testResponse = await testLLM.invoke([
        new HumanMessage("Test")
      ]);

      if (!testResponse || !testResponse.content) {
        console.error("Azure OpenAI service returned invalid response");
        return false;
      }

      console.log("Azure OpenAI configuration validated successfully");
      return true;
    } catch (error) {
      console.error("Azure OpenAI service validation failed:", error);
      
      if (error instanceof Error) {
        if (error.message.includes("401") || error.message.includes("Unauthorized")) {
          console.error("Invalid API key or unauthorized access");
        } else if (error.message.includes("404")) {
          console.error("Deployment not found. Please check your deployment name");
        } else if (error.message.includes("quota") || error.message.includes("rate limit")) {
          console.error("Rate limit exceeded or quota exceeded");
        } else {
          console.error("Connection error:", error.message);
        }
      }
      
      return false;
    }
  }
}
