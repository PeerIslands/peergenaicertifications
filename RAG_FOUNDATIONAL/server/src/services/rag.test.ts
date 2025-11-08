import { describe, it, expect, beforeEach, vi } from 'vitest';
import { indexPdfInVectorStore, answerWithRag, retrieveContextForQuery, ensureUserVectors } from './rag';
import { storage } from './storage';
import { getDb } from '../db/mongo';

// Use vi.hoisted to create mocks that can be used in vi.mock
const { mockEmbeddingsCreate, mockChatCompletionsCreate } = vi.hoisted(() => {
  const mockEmbeddingsCreate = vi.fn().mockResolvedValue({
    data: [{ embedding: Array(1536).fill(0.1) }],
  });
  const mockChatCompletionsCreate = vi.fn().mockResolvedValue({
    choices: [{ message: { content: 'Test response' } }],
  });
  return { mockEmbeddingsCreate, mockChatCompletionsCreate };
});

vi.mock('openai', () => {
  return {
    default: vi.fn().mockImplementation(() => ({
      embeddings: {
        create: mockEmbeddingsCreate,
      },
      chat: {
        completions: {
          create: mockChatCompletionsCreate,
        },
      },
    })),
  };
});
vi.mock('./storage');
vi.mock('../db/mongo');
vi.mock('../utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}));
vi.mock('@langchain/textsplitters', () => ({
  RecursiveCharacterTextSplitter: class {
    splitText(text: string) {
      // Simple mock: split by spaces into chunks
      const chunks = [];
      for (let i = 0; i < text.length; i += 500) {
        chunks.push(text.slice(i, i + 500));
      }
      return chunks.length > 0 ? chunks : [text];
    }
  },
}));

describe('rag service', () => {
  let mockDb: any;
  let mockCollection: any;

  beforeEach(() => {
    vi.clearAllMocks();
    mockEmbeddingsCreate.mockResolvedValue({
      data: [{ embedding: Array(1536).fill(0.1) }],
    });
    mockChatCompletionsCreate.mockResolvedValue({
      choices: [{ message: { content: 'Test response' } }],
    });

    mockCollection = {
      deleteMany: vi.fn().mockResolvedValue({ deletedCount: 0 }),
      find: vi.fn().mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      }),
      bulkWrite: vi.fn().mockResolvedValue({}),
      findOne: vi.fn().mockResolvedValue(null),
      aggregate: vi.fn().mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      }),
    };

    mockDb = {
      collection: vi.fn().mockReturnValue(mockCollection),
    };

    vi.mocked(getDb).mockResolvedValue(mockDb as any);
  });

  describe('indexPdfInVectorStore', () => {
    it('should index PDF text into vector store', async () => {
      const userId = 'user-1';
      const pdfId = 'pdf-1';
      const text = 'This is a test document with some content. '.repeat(100);

      mockEmbeddingsCreate.mockResolvedValue({
        data: Array(10).fill(null).map(() => ({
          embedding: Array(1536).fill(0.1),
        })),
      });

      const count = await indexPdfInVectorStore(userId, {
        pdfId,
        originalName: 'test.pdf',
        text,
      });

      expect(mockDb.collection).toHaveBeenCalledWith('vectors');
      expect(mockCollection.deleteMany).toHaveBeenCalled();
      expect(count).toBeGreaterThan(0);
    });

    it('should return 0 for empty text', async () => {
      const count = await indexPdfInVectorStore('user-1', {
        pdfId: 'pdf-1',
        text: '',
      });

      expect(count).toBe(0);
    });

    it('should handle embedding errors gracefully', async () => {
      // Use a non-rate-limit error so it throws immediately without retries
      mockEmbeddingsCreate.mockRejectedValue(new Error('API error'));

      await expect(
        indexPdfInVectorStore('user-1', {
          pdfId: 'pdf-1',
          text: 'test',
        })
      ).rejects.toThrow('API error');
    }, 10000); // Increase timeout to 10s in case of retries
  });

  describe('ensureUserVectors', () => {
    it('should ensure vectors exist for user PDFs', async () => {
      const mockPdfs = [
        { id: 'pdf-1', extractedText: 'test content' },
        { id: 'pdf-2', extractedText: 'more content' },
      ];

      vi.mocked(storage.getPdfs).mockResolvedValue(mockPdfs as any);
      mockCollection.findOne.mockResolvedValue(null);

      await ensureUserVectors('user-1');

      expect(storage.getPdfs).toHaveBeenCalledWith('user-1');
    });

    it('should skip PDFs without text', async () => {
      const mockPdfs = [
        { id: 'pdf-1', extractedText: '' },
      ];

      vi.mocked(storage.getPdfs).mockResolvedValue(mockPdfs as any);

      await ensureUserVectors('user-1');

      expect(mockCollection.deleteMany).not.toHaveBeenCalled();
    });
  });

  describe('retrieveContextForQuery', () => {
    it('should retrieve context using local similarity', async () => {
      const userId = 'user-1';
      const query = 'test query';

      mockCollection.find.mockReturnValue({
        toArray: vi.fn().mockResolvedValue([
          {
            pdfId: 'pdf-1',
            index: 0,
            text: 'test content',
            embedding: Array(1536).fill(0.1),
            originalName: 'test.pdf',
          },
        ]),
      });

      const context = await retrieveContextForQuery(userId, query, 1);

      expect(mockDb.collection).toHaveBeenCalledWith('vectors');
      expect(context).toBeDefined();
      expect(Array.isArray(context)).toBe(true);
    });

    it('should return empty array when no context found', async () => {
      mockCollection.find.mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      });

      const context = await retrieveContextForQuery('user-1', 'query', 1);

      expect(context).toEqual([]);
    });

    it('should filter by pdfId when provided', async () => {
      mockCollection.find.mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      });

      await retrieveContextForQuery('user-1', 'query', 1, 'pdf-1');

      expect(mockCollection.find).toHaveBeenCalledWith({ userId: 'user-1', pdfId: 'pdf-1' });
    });
  });

  describe('answerWithRag', () => {
    it('should generate answer with RAG', async () => {
      const userId = 'user-1';
      const messages = [
        { role: 'user', content: 'What is this about?' },
      ];

      mockCollection.find.mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      });

      mockChatCompletionsCreate.mockResolvedValue({
        choices: [{ message: { content: 'This is about test content' } }],
      });

      vi.mocked(storage.getPdfs).mockResolvedValue([]);

      const result = await answerWithRag({ userId, messages });

      expect(result).toBeDefined();
      expect(result.reply).toBe('This is about test content');
      expect(result.sources).toBeDefined();
    });

    it('should handle chat completion errors', async () => {
      mockCollection.find.mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      });

      mockChatCompletionsCreate.mockRejectedValue(new Error('API error'));

      vi.mocked(storage.getPdfs).mockResolvedValue([]);

      await expect(
        answerWithRag({
          userId: 'user-1',
          messages: [{ role: 'user', content: 'test' }],
        })
      ).rejects.toThrow();
    });

    it('should handle empty messages', async () => {
      mockCollection.find.mockReturnValue({
        toArray: vi.fn().mockResolvedValue([]),
      });

      mockChatCompletionsCreate.mockResolvedValue({
        choices: [{ message: { content: 'Response' } }],
      });

      vi.mocked(storage.getPdfs).mockResolvedValue([]);

      const result = await answerWithRag({
        userId: 'user-1',
        messages: [],
      });

      // Should still process but with empty question
      expect(result).toBeDefined();
    });
  });
});

