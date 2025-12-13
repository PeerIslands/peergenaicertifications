export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  responseTime?: number;
}

export interface AnalyticsData {
  totalMessages: number;
  averageResponseTime: number;
  conversationCount: number;
  totalResponseTime: number;
}

export interface ChatResponse {
  success: boolean;
  conversationId: string;
  userMessage: ChatMessage;
  aiMessage: ChatMessage;
}

export interface ConversationResponse {
  success: boolean;
  messages: ChatMessage[];
}

export interface AnalyticsResponse {
  success: boolean;
  analytics: AnalyticsData;
}

/**
 * Service for interacting with the chat API endpoints.
 * Provides methods to send messages, retrieve conversations, and fetch analytics.
 */
class ChatService {
  private baseUrl: string;

  /**
   * Creates a new ChatService instance.
   * Initializes the base URL for API requests (defaults to "/api").
   */
  constructor() {
    this.baseUrl = "/api";
  }

  /**
   * Sends a chat message to the server and receives an AI response.
   * 
   * @param message - The user's message text
   * @param sessionId - The session identifier for tracking the conversation
   * @param conversationId - Optional conversation identifier to continue an existing conversation
   * @returns A promise that resolves to a ChatResponse containing user and AI messages
   * @throws Will throw an error if the HTTP request fails
   */
  async sendMessage(
    message: string,
    sessionId: string,
    conversationId?: string
  ): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        message,
        sessionId,
        conversationId,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Retrieves all messages from a specific conversation.
   * 
   * @param conversationId - The unique identifier of the conversation
   * @returns A promise that resolves to a ConversationResponse containing all messages
   * @throws Will throw an error if the HTTP request fails
   */
  async getConversation(conversationId: string): Promise<ConversationResponse> {
    const response = await fetch(`${this.baseUrl}/conversation/${conversationId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Retrieves analytics data for a session.
   * 
   * @param sessionId - The session identifier to get analytics for
   * @returns A promise that resolves to an AnalyticsResponse containing analytics summary
   * @throws Will throw an error if the HTTP request fails
   */
  async getAnalytics(sessionId: string): Promise<AnalyticsResponse> {
    const response = await fetch(`${this.baseUrl}/analytics/${sessionId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  /**
   * Checks the health status of the API server and LLM configuration.
   * 
   * @returns A promise that resolves to an object containing server status and LLM configuration state
   * @throws Will throw an error if the HTTP request fails
   */
  async checkHealth(): Promise<{ status: string; llmConfigured: boolean }> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const chatService = new ChatService();
