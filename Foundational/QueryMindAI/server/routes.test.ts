import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import type { Express, Request, Response } from 'express';
import { createServer, Server } from 'http';
import { registerRoutes } from './routes';

// Mock dependencies
vi.mock('./storage', () => ({
  storage: {
    createConversation: vi.fn(),
    getMessagesByConversation: vi.fn(),
    createMessage: vi.fn(),
    createAnalyticsEvent: vi.fn(),
    getAnalyticsSummary: vi.fn(),
  },
}));

vi.mock('./langchain', () => ({
  LangChainService: vi.fn().mockImplementation(() => ({
    generateResponse: vi.fn(),
  })),
}));

vi.mock('./rag', () => ({
  ragService: {
    retrieveRelevantDocuments: vi.fn(),
    getKnowledgeBaseStats: vi.fn(),
  },
}));

vi.mock('./mongodb', () => ({
  mongodbService: {
    connect: vi.fn(),
  },
}));

describe('registerRoutes', () => {
  let mockApp: Partial<Express>;
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let registeredRoutes: Map<string, any>;

  beforeEach(() => {
    registeredRoutes = new Map();
    mockApp = {
      post: vi.fn((path: any, ...handlers: any[]) => {
        registeredRoutes.set(`POST ${path}`, handlers);
        return mockApp as Express;
      }) as any,
      get: vi.fn((path: any, ...handlers: any[]) => {
        registeredRoutes.set(`GET ${path}`, handlers);
        return mockApp as Express;
      }) as any,
    };

    mockRequest = {
      body: {},
      params: {},
      query: {},
    };

    mockResponse = {
      json: vi.fn().mockReturnThis(),
      status: vi.fn().mockReturnThis(),
    };
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should register all routes and return HTTP server', async () => {
    const { mongodbService } = await import('./mongodb');
    vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

    const server = await registerRoutes(mockApp as Express);

    expect(server).toBeInstanceOf(Server);
    expect(mockApp.post).toHaveBeenCalledWith(
      '/api/chat',
      expect.any(Function),
      expect.any(Function)
    );
    expect(mockApp.get).toHaveBeenCalled();
  });

  describe('POST /api/chat', () => {
    let chatHandler: any;
    let validateMiddleware: any;

    beforeEach(async () => {
      const { mongodbService } = await import('./mongodb');
      vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

      await registerRoutes(mockApp as Express);

      const handlers = registeredRoutes.get('POST /api/chat');
      validateMiddleware = handlers[0];
      chatHandler = handlers[1];
    });

    it('should create conversation and return response', async () => {
      const { storage } = await import('./storage');
      const { LangChainService } = await import('./langchain');

      const mockConversation = {
        id: 'conv-123',
        sessionId: 'session-123',
        createdAt: new Date(),
      };

      const mockUserMessage = {
        id: 'msg-1',
        role: 'user' as const,
        content: 'Hello',
        timestamp: new Date(),
        conversationId: 'conv-123',
        responseTime: null,
      };

      const mockAiMessage = {
        id: 'msg-2',
        role: 'assistant' as const,
        content: 'Hi there!',
        timestamp: new Date(),
        conversationId: 'conv-123',
        responseTime: 150,
      };

      const mockAiResponse = {
        content: 'Hi there!',
        responseTime: 150,
        sources: [],
      };

      vi.mocked(storage.createConversation).mockResolvedValue(mockConversation as any);
      vi.mocked(storage.getMessagesByConversation).mockResolvedValue([]);
      vi.mocked(storage.createMessage).mockResolvedValueOnce(mockUserMessage as any);
      vi.mocked(storage.createMessage).mockResolvedValueOnce(mockAiMessage as any);
      vi.mocked(storage.createAnalyticsEvent).mockResolvedValue({} as any);

      const mockLangChainService = new LangChainService();
      vi.mocked(mockLangChainService.generateResponse).mockResolvedValue(mockAiResponse);

      mockRequest.body = {
        message: 'Hello',
        sessionId: 'session-123',
      };

      // Call validate middleware first
      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());

      // Then call the chat handler
      await chatHandler(mockRequest as Request, mockResponse as Response);

      expect(storage.createConversation).toHaveBeenCalled();
      expect(storage.createMessage).toHaveBeenCalledTimes(2);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: true,
          conversationId: 'conv-123',
        })
      );
    });

    it('should use existing conversationId if provided', async () => {
      const { storage } = await import('./storage');
      const { LangChainService } = await import('./langchain');

      const mockUserMessage = {
        id: 'msg-1',
        role: 'user' as const,
        content: 'Hello',
        timestamp: new Date(),
        conversationId: 'existing-conv',
        responseTime: null,
      };

      const mockAiMessage = {
        id: 'msg-2',
        role: 'assistant' as const,
        content: 'Hi!',
        timestamp: new Date(),
        conversationId: 'existing-conv',
        responseTime: 100,
      };

      vi.mocked(storage.getMessagesByConversation).mockResolvedValue([]);
      vi.mocked(storage.createMessage).mockResolvedValueOnce(mockUserMessage as any);
      vi.mocked(storage.createMessage).mockResolvedValueOnce(mockAiMessage as any);
      vi.mocked(storage.createAnalyticsEvent).mockResolvedValue({} as any);

      const mockLangChainService = new LangChainService();
      vi.mocked(mockLangChainService.generateResponse).mockResolvedValue({
        content: 'Hi!',
        responseTime: 100,
      });

      mockRequest.body = {
        message: 'Hello',
        sessionId: 'session-123',
        conversationId: 'existing-conv',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await chatHandler(mockRequest as Request, mockResponse as Response);

      expect(storage.createConversation).not.toHaveBeenCalled();
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          conversationId: 'existing-conv',
        })
      );
    });

    it('should handle errors gracefully', async () => {
      const { storage } = await import('./storage');

      vi.mocked(storage.createConversation).mockRejectedValue(new Error('Database error'));

      mockRequest.body = {
        message: 'Hello',
        sessionId: 'session-123',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await chatHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          error: 'Internal server error',
        })
      );
    });
  });

  describe('GET /api/conversation/:conversationId', () => {
    let conversationHandler: any;
    let validateMiddleware: any;

    beforeEach(async () => {
      const { mongodbService } = await import('./mongodb');
      vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

      await registerRoutes(mockApp as Express);

      const handlers = registeredRoutes.get('GET /api/conversation/:conversationId');
      validateMiddleware = handlers[0];
      conversationHandler = handlers[1];
    });

    it('should return conversation messages', async () => {
      const { storage } = await import('./storage');

      const mockMessages = [
        {
          id: 'msg-1',
          role: 'user' as const,
          content: 'Hello',
          timestamp: new Date(),
          conversationId: 'conv-123',
          responseTime: null,
        },
        {
          id: 'msg-2',
          role: 'assistant' as const,
          content: 'Hi!',
          timestamp: new Date(),
          conversationId: 'conv-123',
          responseTime: 100,
        },
      ];

      vi.mocked(storage.getMessagesByConversation).mockResolvedValue(mockMessages as any);

      mockRequest.params = {
        conversationId: '123e4567-e89b-12d3-a456-426614174000',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await conversationHandler(mockRequest as Request, mockResponse as Response);

      expect(storage.getMessagesByConversation).toHaveBeenCalledWith(
        '123e4567-e89b-12d3-a456-426614174000'
      );
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: true,
          messages: expect.arrayContaining([
            expect.objectContaining({
              id: 'msg-1',
              role: 'user',
              content: 'Hello',
            }),
          ]),
        })
      );
    });

    it('should handle errors', async () => {
      const { storage } = await import('./storage');

      vi.mocked(storage.getMessagesByConversation).mockRejectedValue(
        new Error('Database error')
      );

      mockRequest.params = {
        conversationId: '123e4567-e89b-12d3-a456-426614174000',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await conversationHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
    });
  });

  describe('GET /api/analytics/:sessionId', () => {
    let analyticsHandler: any;
    let validateMiddleware: any;

    beforeEach(async () => {
      const { mongodbService } = await import('./mongodb');
      vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

      await registerRoutes(mockApp as Express);

      const handlers = registeredRoutes.get('GET /api/analytics/:sessionId');
      validateMiddleware = handlers[0];
      analyticsHandler = handlers[1];
    });

    it('should return analytics summary', async () => {
      const { storage } = await import('./storage');

      const mockAnalytics = {
        totalMessages: 10,
        averageResponseTime: 150,
        conversationCount: 2,
        totalResponseTime: 1500,
      };

      vi.mocked(storage.getAnalyticsSummary).mockResolvedValue(mockAnalytics);

      mockRequest.params = {
        sessionId: 'session-123',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await analyticsHandler(mockRequest as Request, mockResponse as Response);

      expect(storage.getAnalyticsSummary).toHaveBeenCalledWith('session-123');
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: true,
          analytics: mockAnalytics,
        })
      );
    });

    it('should handle errors', async () => {
      const { storage } = await import('./storage');

      vi.mocked(storage.getAnalyticsSummary).mockRejectedValue(new Error('Database error'));

      mockRequest.params = {
        sessionId: 'session-123',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await analyticsHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
    });
  });

  describe('GET /api/rag/search', () => {
    let ragSearchHandler: any;
    let validateMiddleware: any;

    beforeEach(async () => {
      const { mongodbService } = await import('./mongodb');
      vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

      await registerRoutes(mockApp as Express);

      const handlers = registeredRoutes.get('GET /api/rag/search');
      validateMiddleware = handlers[0];
      ragSearchHandler = handlers[1];
    });

    it('should return RAG search results', async () => {
      const { ragService } = await import('./rag');

      const mockResults = [
        {
          content: 'Document 1',
          metadata: { source: 'test' },
          similarity: 0.95,
        },
      ];

      vi.mocked(ragService.retrieveRelevantDocuments).mockResolvedValue(mockResults as any);

      mockRequest.query = {
        query: 'test query',
        limit: '5',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await ragSearchHandler(mockRequest as Request, mockResponse as Response);

      expect(ragService.retrieveRelevantDocuments).toHaveBeenCalledWith('test query', 5);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: true,
          query: 'test query',
          results: expect.arrayContaining([
            expect.objectContaining({
              content: 'Document 1',
            }),
          ]),
        })
      );
    });

    it('should use default limit when not provided', async () => {
      const { ragService } = await import('./rag');

      vi.mocked(ragService.retrieveRelevantDocuments).mockResolvedValue([]);

      mockRequest.query = {
        query: 'test query',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await ragSearchHandler(mockRequest as Request, mockResponse as Response);

      expect(ragService.retrieveRelevantDocuments).toHaveBeenCalledWith('test query', 5);
    });

    it('should handle errors', async () => {
      const { ragService } = await import('./rag');

      vi.mocked(ragService.retrieveRelevantDocuments).mockRejectedValue(
        new Error('Search error')
      );

      mockRequest.query = {
        query: 'test query',
      };

      await validateMiddleware(mockRequest as Request, mockResponse as Response, vi.fn());
      await ragSearchHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
    });
  });

  describe('GET /api/rag/status', () => {
    let ragStatusHandler: any;

    beforeEach(async () => {
      const { mongodbService } = await import('./mongodb');
      vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

      await registerRoutes(mockApp as Express);

      const handlers = registeredRoutes.get('GET /api/rag/status');
      ragStatusHandler = handlers[0];
    });

    it('should return RAG status', async () => {
      const { ragService } = await import('./rag');

      vi.mocked(ragService.getKnowledgeBaseStats).mockResolvedValue({
        isReady: true,
        documentCount: 100,
      });

      await ragStatusHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          success: true,
          ragReady: true,
          documentCount: 100,
          mongodbConnected: true,
        })
      );
    });

    it('should handle errors', async () => {
      const { ragService } = await import('./rag');

      vi.mocked(ragService.getKnowledgeBaseStats).mockRejectedValue(new Error('Error'));

      await ragStatusHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.status).toHaveBeenCalledWith(500);
    });
  });

  describe('GET /api/health', () => {
    let healthHandler: any;

    beforeEach(async () => {
      const { mongodbService } = await import('./mongodb');
      vi.mocked(mongodbService.connect).mockResolvedValue(undefined);

      await registerRoutes(mockApp as Express);

      const handlers = registeredRoutes.get('GET /api/health');
      healthHandler = handlers[0];
    });

    it('should return health status', async () => {
      const { LangChainService } = await import('./langchain');
      const { ragService } = await import('./rag');

      vi.mocked(LangChainService.validateConfiguration).mockResolvedValue(true);
      vi.mocked(ragService.getKnowledgeBaseStats).mockResolvedValue({
        isReady: true,
        documentCount: 50,
      });

      await healthHandler(mockRequest as Request, mockResponse as Response);

      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'ok',
          llmConfigured: true,
          ragReady: true,
          documentCount: 50,
        })
      );
    });
  });
});

