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

class ChatService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = "/api";
  }

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

  async getConversation(conversationId: string): Promise<ConversationResponse> {
    const response = await fetch(`${this.baseUrl}/conversation/${conversationId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async getAnalytics(sessionId: string): Promise<AnalyticsResponse> {
    const response = await fetch(`${this.baseUrl}/analytics/${sessionId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  async checkHealth(): Promise<{ status: string; llmConfigured: boolean }> {
    const response = await fetch(`${this.baseUrl}/health`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return response.json();
  }
}

export const chatService = new ChatService();
