import { describe, it, expect, beforeEach } from 'vitest';
import { MemStorage } from './storage';
import type { InsertUser, InsertConversation, InsertMessage, InsertAnalytics } from '@shared/schema';

describe('MemStorage', () => {
  let storage: MemStorage;

  beforeEach(() => {
    storage = new MemStorage();
  });

  describe('User operations', () => {
    it('should create a user', async () => {
      const insertUser: InsertUser = {
        username: 'testuser',
        password: 'password123',
      };

      const user = await storage.createUser(insertUser);

      expect(user.id).toBeDefined();
      expect(user.username).toBe('testuser');
      expect(user.password).toBe('password123');
    });

    it('should get a user by id', async () => {
      const insertUser: InsertUser = {
        username: 'testuser',
        password: 'password123',
      };

      const createdUser = await storage.createUser(insertUser);
      const retrievedUser = await storage.getUser(createdUser.id);

      expect(retrievedUser).toBeDefined();
      expect(retrievedUser?.id).toBe(createdUser.id);
      expect(retrievedUser?.username).toBe('testuser');
    });

    it('should return undefined for non-existent user', async () => {
      const user = await storage.getUser('non-existent-id');
      expect(user).toBeUndefined();
    });

    it('should get a user by username', async () => {
      const insertUser: InsertUser = {
        username: 'testuser',
        password: 'password123',
      };

      await storage.createUser(insertUser);
      const retrievedUser = await storage.getUserByUsername('testuser');

      expect(retrievedUser).toBeDefined();
      expect(retrievedUser?.username).toBe('testuser');
    });

    it('should return undefined for non-existent username', async () => {
      const user = await storage.getUserByUsername('non-existent');
      expect(user).toBeUndefined();
    });
  });

  describe('Conversation operations', () => {
    it('should create a conversation', async () => {
      const insertConversation: InsertConversation = {
        sessionId: 'session-123',
      };

      const conversation = await storage.createConversation(insertConversation);

      expect(conversation.id).toBeDefined();
      expect(conversation.sessionId).toBe('session-123');
      expect(conversation.createdAt).toBeInstanceOf(Date);
    });

    it('should get a conversation by id', async () => {
      const insertConversation: InsertConversation = {
        sessionId: 'session-123',
      };

      const createdConversation = await storage.createConversation(insertConversation);
      const retrievedConversation = await storage.getConversation(createdConversation.id);

      expect(retrievedConversation).toBeDefined();
      expect(retrievedConversation?.id).toBe(createdConversation.id);
      expect(retrievedConversation?.sessionId).toBe('session-123');
    });

    it('should get conversations by session id', async () => {
      const sessionId = 'session-123';

      await storage.createConversation({ sessionId });
      await storage.createConversation({ sessionId });
      await storage.createConversation({ sessionId: 'other-session' });

      const conversations = await storage.getConversationsBySession(sessionId);

      expect(conversations).toHaveLength(2);
      expect(conversations.every(c => c.sessionId === sessionId)).toBe(true);
    });
  });

  describe('Message operations', () => {
    it('should create a message', async () => {
      const conversation = await storage.createConversation({ sessionId: 'session-123' });
      const insertMessage: InsertMessage = {
        conversationId: conversation.id,
        role: 'user',
        content: 'Hello, world!',
      };

      const message = await storage.createMessage(insertMessage);

      expect(message.id).toBeDefined();
      expect(message.conversationId).toBe(conversation.id);
      expect(message.role).toBe('user');
      expect(message.content).toBe('Hello, world!');
      expect(message.timestamp).toBeInstanceOf(Date);
    });

    it('should create a message with response time', async () => {
      const conversation = await storage.createConversation({ sessionId: 'session-123' });
      const insertMessage: InsertMessage = {
        conversationId: conversation.id,
        role: 'assistant',
        content: 'Response',
        responseTime: 150,
      };

      const message = await storage.createMessage(insertMessage);

      expect(message.responseTime).toBe(150);
    });

    it('should get messages by conversation id', async () => {
      const conversation = await storage.createConversation({ sessionId: 'session-123' });
      
      const message1 = await storage.createMessage({
        conversationId: conversation.id,
        role: 'user',
        content: 'First message',
      });

      // Add a small delay to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 10));

      const message2 = await storage.createMessage({
        conversationId: conversation.id,
        role: 'assistant',
        content: 'Second message',
      });

      const messages = await storage.getMessagesByConversation(conversation.id);

      expect(messages).toHaveLength(2);
      expect(messages[0].id).toBe(message1.id);
      expect(messages[1].id).toBe(message2.id);
      expect(messages[0].timestamp.getTime()).toBeLessThanOrEqual(messages[1].timestamp.getTime());
    });

    it('should get messages by session id', async () => {
      const sessionId = 'session-123';
      const conversation1 = await storage.createConversation({ sessionId });
      const conversation2 = await storage.createConversation({ sessionId });

      await storage.createMessage({
        conversationId: conversation1.id,
        role: 'user',
        content: 'Message 1',
      });

      await storage.createMessage({
        conversationId: conversation2.id,
        role: 'user',
        content: 'Message 2',
      });

      const messages = await storage.getMessagesBySession(sessionId);

      expect(messages).toHaveLength(2);
    });

    it('should return empty array for non-existent conversation', async () => {
      const messages = await storage.getMessagesByConversation('non-existent-id');
      expect(messages).toHaveLength(0);
    });
  });

  describe('Analytics operations', () => {
    it('should create an analytics event', async () => {
      const insertAnalytics: InsertAnalytics = {
        sessionId: 'session-123',
        eventType: 'message_sent',
        data: JSON.stringify({ messageLength: 10 }),
      };

      const analytics = await storage.createAnalyticsEvent(insertAnalytics);

      expect(analytics.id).toBeDefined();
      expect(analytics.sessionId).toBe('session-123');
      expect(analytics.eventType).toBe('message_sent');
      expect(analytics.data).toBe(JSON.stringify({ messageLength: 10 }));
      expect(analytics.timestamp).toBeInstanceOf(Date);
    });

    it('should get analytics by session id', async () => {
      const sessionId = 'session-123';

      await storage.createAnalyticsEvent({
        sessionId, eventType: 'message_sent', data: null,
      });
      await storage.createAnalyticsEvent({
        sessionId, eventType: 'response_received', data: null,
      });

      const analytics = await storage.getAnalyticsBySession(sessionId);

      expect(analytics).toHaveLength(2);
      expect(analytics.every(a => a.sessionId === sessionId)).toBe(true);
    });

    it('should get analytics summary', async () => {
      const sessionId = 'session-123';
      const conversation = await storage.createConversation({ sessionId });

      // Create messages with response times
      await storage.createMessage({
        conversationId: conversation.id,
        role: 'user',
        content: 'Message 1',
      });

      await storage.createMessage({
        conversationId: conversation.id,
        role: 'assistant',
        content: 'Response 1',
        responseTime: 100,
      });

      await storage.createMessage({
        conversationId: conversation.id,
        role: 'user',
        content: 'Message 2',
      });

      await storage.createMessage({
        conversationId: conversation.id,
        role: 'assistant',
        content: 'Response 2',
        responseTime: 200,
      });

      const summary = await storage.getAnalyticsSummary(sessionId);

      expect(summary.totalMessages).toBe(4);
      expect(summary.conversationCount).toBe(1);
      expect(summary.averageResponseTime).toBe(150); // (100 + 200) / 2
      expect(summary.totalResponseTime).toBe(300);
    });

    it('should handle analytics summary with no assistant messages', async () => {
      const sessionId = 'session-123';
      const conversation = await storage.createConversation({ sessionId });

      await storage.createMessage({
        conversationId: conversation.id,
        role: 'user',
        content: 'Message 1',
      });

      const summary = await storage.getAnalyticsSummary(sessionId);

      expect(summary.totalMessages).toBe(1);
      expect(summary.averageResponseTime).toBe(0);
      expect(summary.totalResponseTime).toBe(0);
    });
  });
});

