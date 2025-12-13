import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { LangChainService } from './langchain';
import type { Message } from '@shared/schema';

// Mock the LangChain modules
vi.mock('@langchain/openai', () => ({
  ChatOpenAI: vi.fn().mockImplementation(() => ({
    invoke: vi.fn(),
  })),
}));

vi.mock('./rag', () => ({
  ragService: {
    generateRAGResponse: vi.fn(),
  },
}));

describe('LangChainService', () => {
  let langchainService: LangChainService;
  let mockLLM: any;

  beforeEach(() => {
    // Reset environment variables
    process.env.AZURE_OPENAI_API_KEY = 'test-key';
    process.env.AZURE_OPENAI_DEPLOYMENT_NAME = 'test-deployment';
    process.env.AZURE_OPENAI_ENDPOINT = 'https://test.openai.azure.com/';
    process.env.AZURE_OPENAI_MODEL_NAME = 'gpt-4o-mini';
    process.env.AZURE_OPENAI_API_VERSION = '2024-07-18';
    process.env.AZURE_OPENAI_TEMPERATURE = '0.5';
    process.env.AZURE_OPENAI_MAX_TOKENS = '500';

    langchainService = new LangChainService();
    mockLLM = (langchainService as any).llm;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('generateResponse', () => {
    const mockContext = {
      conversationId: 'conv-123',
      sessionId: 'session-123',
      messages: [] as Message[],
    };

    it('should generate a response successfully', async () => {
      const mockResponse = {
        content: 'This is a test response',
      };

      mockLLM.invoke = vi.fn().mockResolvedValue(mockResponse);

      const { ragService } = await import('./rag');
      vi.mocked(ragService.generateRAGResponse).mockResolvedValue({
        content: 'RAG context',
        sources: [],
      });

      const result = await langchainService.generateResponse('Hello', mockContext);

      expect(result.content).toBe('This is a test response');
      expect(result.responseTime).toBeGreaterThanOrEqual(0);
      expect(mockLLM.invoke).toHaveBeenCalled();
    });

    it('should handle RAG context in response', async () => {
      const mockResponse = {
        content: 'Response with RAG context',
      };

      mockLLM.invoke = vi.fn().mockResolvedValue(mockResponse);

      const { ragService } = await import('./rag');
      vi.mocked(ragService.generateRAGResponse).mockResolvedValue({
        content: 'Relevant context from knowledge base',
        sources: [{ content: 'Source 1', metadata: {} }],
      });

      const result = await langchainService.generateResponse('Hello', mockContext);

      expect(result.sources).toBeDefined();
      expect(result.sources).toHaveLength(1);
    });

    it('should handle RAG failure gracefully', async () => {
      const mockResponse = {
        content: 'Response without RAG',
      };

      mockLLM.invoke = vi.fn().mockResolvedValue(mockResponse);

      const { ragService } = await import('./rag');
      vi.mocked(ragService.generateRAGResponse).mockRejectedValue(
        new Error('RAG error')
      );

      const result = await langchainService.generateResponse('Hello', mockContext);

      expect(result.content).toBe('Response without RAG');
      expect(mockLLM.invoke).toHaveBeenCalled();
    });

    it('should handle missing API key', async () => {
      delete process.env.AZURE_OPENAI_API_KEY;
      const service = new LangChainService();

      const result = await service.generateResponse('Hello', mockContext);

      expect(result.content).toContain('API key');
      expect(result.content).toContain('not configured');
    });

    it('should handle timeout errors', async () => {
      mockLLM.invoke = vi.fn().mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 35000))
      );

      const result = await langchainService.generateResponse('Hello', mockContext);

      expect(result.content).toContain('longer than expected');
    });

    it('should handle invalid response from AI', async () => {
      mockLLM.invoke = vi.fn().mockResolvedValue({ content: null });

      const { ragService } = await import('./rag');
      vi.mocked(ragService.generateRAGResponse).mockResolvedValue({
        content: '',
        sources: [],
      });

      const result = await langchainService.generateResponse('Hello', mockContext);

      expect(result.content).toContain('technical difficulties');
    });

    it('should convert conversation history to LangChain messages', async () => {
      const mockResponse = {
        content: 'Response',
      };

      mockLLM.invoke = vi.fn().mockResolvedValue(mockResponse);

      const contextWithHistory = {
        ...mockContext,
        messages: [
          {
            id: '1',
            role: 'user' as const,
            content: 'First message',
            timestamp: new Date(),
            conversationId: 'conv-123',
            responseTime: null,
          },
          {
            id: '2',
            role: 'assistant' as const,
            content: 'First response',
            timestamp: new Date(),
            conversationId: 'conv-123',
            responseTime: 100,
          },
        ] as Message[],
      };

      const { ragService } = await import('./rag');
      vi.mocked(ragService.generateRAGResponse).mockResolvedValue({
        content: '',
        sources: [],
      });

      await langchainService.generateResponse('Second message', contextWithHistory);

      expect(mockLLM.invoke).toHaveBeenCalled();
      const callArgs = mockLLM.invoke.mock.calls[0][0];
      expect(callArgs.length).toBeGreaterThan(1); // System message + history + new message
    });
  });

  describe('getConversationSummary', () => {
    it('should return summary for messages', async () => {
      const messages: Message[] = [
        {
          id: '1',
          role: 'user',
          content: 'What is TypeScript?',
          timestamp: new Date(),
          conversationId: 'conv-123',
          responseTime: null,
        },
        {
          id: '2',
          role: 'assistant',
          content: 'TypeScript is...',
          timestamp: new Date(),
          conversationId: 'conv-123',
          responseTime: 100,
        },
      ];

      const summary = await langchainService.getConversationSummary(messages);

      expect(summary).toContain('What is TypeScript?');
    });

    it('should return default message for empty messages', async () => {
      const summary = await langchainService.getConversationSummary([]);
      expect(summary).toBe('No conversation yet');
    });

    it('should limit topics to first 3 user messages', async () => {
      const messages: Message[] = Array.from({ length: 5 }, (_, i) => ({
        id: `${i}`,
        role: 'user' as const,
        content: `Message ${i}`,
        timestamp: new Date(),
        conversationId: 'conv-123',
        responseTime: null,
      }));

      const summary = await langchainService.getConversationSummary(messages);

      expect(summary).toContain('Message 0');
      expect(summary).toContain('Message 1');
      expect(summary).toContain('Message 2');
      expect(summary).toContain('...');
    });
  });

  describe('validateConfiguration', () => {
    it('should return false when API key is missing', async () => {
      const originalKey = process.env.AZURE_OPENAI_API_KEY;
      delete process.env.AZURE_OPENAI_API_KEY;

      const result = await LangChainService.validateConfiguration();

      expect(result).toBe(false);
      process.env.AZURE_OPENAI_API_KEY = originalKey;
    });

    it('should return false when deployment name is missing', async () => {
      const originalDeployment = process.env.AZURE_OPENAI_DEPLOYMENT_NAME;
      delete process.env.AZURE_OPENAI_DEPLOYMENT_NAME;

      const result = await LangChainService.validateConfiguration();

      expect(result).toBe(false);
      process.env.AZURE_OPENAI_DEPLOYMENT_NAME = originalDeployment;
    });

    it('should handle validation errors gracefully', async () => {
      const originalKey = process.env.AZURE_OPENAI_API_KEY;
      process.env.AZURE_OPENAI_API_KEY = 'invalid-key';

      // Mock the ChatOpenAI to throw an error
      const { ChatOpenAI } = await import('@langchain/openai');
      vi.mocked(ChatOpenAI).mockImplementation(() => ({
        invoke: vi.fn().mockRejectedValue(new Error('401 Unauthorized')),
      } as any));

      const result = await LangChainService.validateConfiguration();

      expect(result).toBe(false);
      process.env.AZURE_OPENAI_API_KEY = originalKey;
    });
  });
});

