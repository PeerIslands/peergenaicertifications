import { type User, type InsertUser, type Conversation, type InsertConversation, type Message, type InsertMessage, type Analytics, type InsertAnalytics } from "@shared/schema";
import { randomUUID } from "crypto";

// modify the interface with any CRUD methods
// you might need

export interface IStorage {
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // Conversation methods
  createConversation(conversation: InsertConversation): Promise<Conversation>;
  getConversation(id: string): Promise<Conversation | undefined>;
  getConversationsBySession(sessionId: string): Promise<Conversation[]>;
  
  // Message methods
  createMessage(message: InsertMessage): Promise<Message>;
  getMessagesByConversation(conversationId: string): Promise<Message[]>;
  getMessagesBySession(sessionId: string): Promise<Message[]>;
  
  // Analytics methods
  createAnalyticsEvent(analytics: InsertAnalytics): Promise<Analytics>;
  getAnalyticsBySession(sessionId: string): Promise<Analytics[]>;
  getAnalyticsSummary(sessionId: string): Promise<{
    totalMessages: number;
    averageResponseTime: number;
    conversationCount: number;
    totalResponseTime: number;
  }>;
}

export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private conversations: Map<string, Conversation>;
  private messages: Map<string, Message>;
  private analytics: Map<string, Analytics>;

  constructor() {
    this.users = new Map();
    this.conversations = new Map();
    this.messages = new Map();
    this.analytics = new Map();
  }

  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createConversation(insertConversation: InsertConversation): Promise<Conversation> {
    const id = randomUUID();
    const conversation: Conversation = {
      ...insertConversation,
      id,
      createdAt: new Date(),
    };
    this.conversations.set(id, conversation);
    return conversation;
  }

  async getConversation(id: string): Promise<Conversation | undefined> {
    return this.conversations.get(id);
  }

  async getConversationsBySession(sessionId: string): Promise<Conversation[]> {
    return Array.from(this.conversations.values()).filter(
      (conv) => conv.sessionId === sessionId
    );
  }

  async createMessage(insertMessage: InsertMessage): Promise<Message> {
    const id = randomUUID();
    const message: Message = {
      ...insertMessage,
      id,
      timestamp: new Date(),
      conversationId: insertMessage.conversationId || null,
      responseTime: insertMessage.responseTime || null,
    };
    this.messages.set(id, message);
    return message;
  }

  async getMessagesByConversation(conversationId: string): Promise<Message[]> {
    return Array.from(this.messages.values())
      .filter((msg) => msg.conversationId === conversationId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  async getMessagesBySession(sessionId: string): Promise<Message[]> {
    const conversations = await this.getConversationsBySession(sessionId);
    const conversationIds = conversations.map(c => c.id);
    
    return Array.from(this.messages.values())
      .filter((msg) => msg.conversationId && conversationIds.includes(msg.conversationId))
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  async createAnalyticsEvent(insertAnalytics: InsertAnalytics): Promise<Analytics> {
    const id = randomUUID();
    const analytics: Analytics = {
      ...insertAnalytics,
      id,
      timestamp: new Date(),
      data: insertAnalytics.data || null,
    };
    this.analytics.set(id, analytics);
    return analytics;
  }

  async getAnalyticsBySession(sessionId: string): Promise<Analytics[]> {
    return Array.from(this.analytics.values())
      .filter((analytics) => analytics.sessionId === sessionId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  async getAnalyticsSummary(sessionId: string): Promise<{
    totalMessages: number;
    averageResponseTime: number;
    conversationCount: number;
    totalResponseTime: number;
  }> {
    const messages = await this.getMessagesBySession(sessionId);
    const conversations = await this.getConversationsBySession(sessionId);
    
    const assistantMessages = messages.filter(m => m.role === 'assistant' && m.responseTime);
    const totalResponseTime = assistantMessages.reduce((sum, msg) => sum + (msg.responseTime || 0), 0);
    const averageResponseTime = assistantMessages.length > 0 ? totalResponseTime / assistantMessages.length : 0;
    
    return {
      totalMessages: messages.length,
      averageResponseTime,
      conversationCount: conversations.length,
      totalResponseTime,
    };
  }
}

export const storage = new MemStorage();
