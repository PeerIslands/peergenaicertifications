import { type User, type InsertUser, type Conversation, type InsertConversation, type Message, type InsertMessage, type Analytics, type InsertAnalytics } from "@shared/schema";
import { randomUUID } from "crypto";

// modify the interface with any CRUD methods
// you might need

/**
 * Storage interface defining CRUD operations for users, conversations, messages, and analytics.
 * Provides an abstraction layer for data persistence operations.
 */
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

/**
 * In-memory storage implementation of the IStorage interface.
 * Uses Map data structures to store users, conversations, messages, and analytics in memory.
 * 
 * @remarks
 * This is a temporary storage solution. Data will be lost when the server restarts.
 * For production use, consider implementing a database-backed storage solution.
 */
export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private conversations: Map<string, Conversation>;
  private messages: Map<string, Message>;
  private analytics: Map<string, Analytics>;

  /**
   * Creates a new MemStorage instance with empty maps for all data types.
   */
  constructor() {
    this.users = new Map();
    this.conversations = new Map();
    this.messages = new Map();
    this.analytics = new Map();
  }

  /**
   * Retrieves a user by their unique identifier.
   * 
   * @param id - The unique identifier of the user
   * @returns A promise that resolves to the user if found, or undefined if not found
   */
  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  /**
   * Retrieves a user by their username.
   * 
   * @param username - The username to search for
   * @returns A promise that resolves to the user if found, or undefined if not found
   */
  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  /**
   * Creates a new user in the storage.
   * 
   * @param insertUser - The user data to insert (without id, which is auto-generated)
   * @returns A promise that resolves to the created user with generated id
   */
  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  /**
   * Creates a new conversation in the storage.
   * 
   * @param insertConversation - The conversation data to insert (without id and createdAt, which are auto-generated)
   * @returns A promise that resolves to the created conversation with generated id and timestamp
   */
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

  /**
   * Retrieves a conversation by its unique identifier.
   * 
   * @param id - The unique identifier of the conversation
   * @returns A promise that resolves to the conversation if found, or undefined if not found
   */
  async getConversation(id: string): Promise<Conversation | undefined> {
    return this.conversations.get(id);
  }

  /**
   * Retrieves all conversations associated with a session.
   * 
   * @param sessionId - The session identifier to filter conversations by
   * @returns A promise that resolves to an array of conversations for the session
   */
  async getConversationsBySession(sessionId: string): Promise<Conversation[]> {
    return Array.from(this.conversations.values()).filter(
      (conv) => conv.sessionId === sessionId
    );
  }

  /**
   * Creates a new message in the storage.
   * 
   * @param insertMessage - The message data to insert (without id and timestamp, which are auto-generated)
   * @returns A promise that resolves to the created message with generated id and timestamp
   */
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

  /**
   * Retrieves all messages for a specific conversation, sorted by timestamp.
   * 
   * @param conversationId - The conversation identifier to filter messages by
   * @returns A promise that resolves to an array of messages sorted chronologically
   */
  async getMessagesByConversation(conversationId: string): Promise<Message[]> {
    return Array.from(this.messages.values())
      .filter((msg) => msg.conversationId === conversationId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  /**
   * Retrieves all messages for all conversations in a session, sorted by timestamp.
   * 
   * @param sessionId - The session identifier to filter messages by
   * @returns A promise that resolves to an array of messages from all conversations in the session, sorted chronologically
   */
  async getMessagesBySession(sessionId: string): Promise<Message[]> {
    const conversations = await this.getConversationsBySession(sessionId);
    const conversationIds = conversations.map(c => c.id);
    
    return Array.from(this.messages.values())
      .filter((msg) => msg.conversationId && conversationIds.includes(msg.conversationId))
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  /**
   * Creates a new analytics event in the storage.
   * 
   * @param insertAnalytics - The analytics data to insert (without id and timestamp, which are auto-generated)
   * @returns A promise that resolves to the created analytics event with generated id and timestamp
   */
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

  /**
   * Retrieves all analytics events for a session, sorted by timestamp.
   * 
   * @param sessionId - The session identifier to filter analytics by
   * @returns A promise that resolves to an array of analytics events sorted chronologically
   */
  async getAnalyticsBySession(sessionId: string): Promise<Analytics[]> {
    return Array.from(this.analytics.values())
      .filter((analytics) => analytics.sessionId === sessionId)
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
  }

  /**
   * Calculates and returns analytics summary for a session.
   * 
   * @param sessionId - The session identifier to calculate analytics for
   * @returns A promise that resolves to an object containing:
   *   - totalMessages: Total number of messages in the session
   *   - averageResponseTime: Average response time in milliseconds
   *   - conversationCount: Number of conversations in the session
   *   - totalResponseTime: Sum of all response times in milliseconds
   */
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
