// API client for ChatPDFEngine
const API_BASE = '/api';

export interface Document {
  _id: string;
  filename: string;
  originalName: string;
  size: number;
  status: 'uploading' | 'processing' | 'completed' | 'error';
  uploadDate?: string | Date;
  processedDate?: string | Date;
}

export interface Conversation {
  _id: string;
  title: string;
  createdAt?: string | Date;
  updatedAt?: string | Date;
  pdfDocumentId?: string;
  isActive: boolean;
}

export interface Message {
  _id: string;
  conversationId: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string | Date;
  metadata?: {
    pdfChunks?: string[];
    sources?: Array<{
      page: number;
      text: string;
    }>;
  };
}

export class ChatAPI {
  // Upload PDF
  static async uploadPDF(file: File): Promise<{ success: boolean; document: Document }> {
    const formData = new FormData();
    formData.append('pdf', file);

    const response = await fetch(`${API_BASE}/upload-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error('Failed to upload PDF');
    }

    return response.json();
  }

  // Get all documents
  static async getDocuments(): Promise<Document[]> {
    const response = await fetch(`${API_BASE}/documents`);
    if (!response.ok) {
      throw new Error('Failed to fetch documents');
    }
    return response.json();
  }

  // Get all conversations
  static async getConversations(): Promise<Conversation[]> {
    const response = await fetch(`${API_BASE}/conversations`);
    if (!response.ok) {
      throw new Error('Failed to fetch conversations');
    }
    return response.json();
  }

  // Create new conversation
  static async createConversation(title: string, pdfDocumentId?: string): Promise<Conversation> {
    const response = await fetch(`${API_BASE}/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, pdfDocumentId }),
    });

    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }

    return response.json();
  }

  // Get messages for a conversation
  static async getMessages(conversationId: string): Promise<Message[]> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`);
    if (!response.ok) {
      throw new Error('Failed to fetch messages');
    }
    return response.json();
  }

  // Send message and get AI response
  static async sendMessage(conversationId: string, content: string): Promise<{ userMessage: Message; aiMessage: Message }> {
    const response = await fetch(`${API_BASE}/conversations/${conversationId}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ content }),
    });

    if (!response.ok) {
      throw new Error('Failed to send message');
    }

    return response.json();
  }
}
