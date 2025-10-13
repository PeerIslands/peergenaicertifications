export interface ChatResponse {
  id: string;
  answer: string;
  sources: Array<{
    content: string;
    metadata?: any;
    score?: number;
  }>;
  timestamp: string;
}

export interface ChatHistoryItem {
  _id: string;
  userId: string;
  query: string;
  response: string;
  sources?: Array<{
    content: string;
    metadata?: any;
    score?: number;
    searchType?: string;
  }>;
  createdAt: string;
}

export class ChatService {
  private baseUrl: string;

  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }

  async sendMessage(query: string, userId: string, parameters: {
    topK: number;
    temperature: number;
    topP: number;
    maxTokens: number;
    frequencyPenalty: number;
    presencePenalty: number;
  }): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, userId, ...parameters }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getChatHistory(userId: string): Promise<ChatHistoryItem[]> {
    const response = await fetch(`${this.baseUrl}/api/chat/history/${userId}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch chat history: ${response.statusText}`);
    }

    return response.json();
  }

  async getChatHistoryEntry(id: string): Promise<ChatHistoryItem> {
    const response = await fetch(`${this.baseUrl}/api/chat/history/entry/${id}`);

    if (!response.ok) {
      throw new Error(`Failed to fetch chat history entry: ${response.statusText}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    const response = await fetch(`${this.baseUrl}/api/health`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }
}

export const chatService = new ChatService();
