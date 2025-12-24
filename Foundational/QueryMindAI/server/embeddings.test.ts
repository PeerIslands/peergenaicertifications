import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { EmbeddingsService } from './embeddings';

// Mock OllamaEmbeddings
vi.mock('@langchain/ollama', () => ({
  OllamaEmbeddings: vi.fn().mockImplementation(() => ({
    embedQuery: vi.fn(),
    embedDocuments: vi.fn(),
  })),
}));

// Mock fetch globally
global.fetch = vi.fn();

describe('EmbeddingsService', () => {
  let embeddingsService: EmbeddingsService;
  let mockEmbeddings: any;

  beforeEach(async () => {
    const { OllamaEmbeddings } = await import('@langchain/ollama');
    embeddingsService = new EmbeddingsService();
    mockEmbeddings = (embeddingsService as any).embeddings;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('generateEmbedding', () => {
    it('should generate embedding for a single text', async () => {
      const mockEmbedding = [0.1, 0.2, 0.3, 0.4];
      mockEmbeddings.embedQuery.mockResolvedValue(mockEmbedding);

      const result = await embeddingsService.generateEmbedding('test text');

      expect(result).toEqual(mockEmbedding);
      expect(mockEmbeddings.embedQuery).toHaveBeenCalledWith('test text');
    });

    it('should throw error on failure', async () => {
      const error = new Error('Embedding generation failed');
      mockEmbeddings.embedQuery.mockRejectedValue(error);

      await expect(embeddingsService.generateEmbedding('test text')).rejects.toThrow(
        'Embedding generation failed'
      );
    });

    it('should handle empty string', async () => {
      const mockEmbedding = [];
      mockEmbeddings.embedQuery.mockResolvedValue(mockEmbedding);

      const result = await embeddingsService.generateEmbedding('');

      expect(result).toEqual(mockEmbedding);
    });
  });

  describe('generateEmbeddings', () => {
    it('should generate embeddings for multiple texts', async () => {
      const mockEmbeddingsArray = [
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9],
      ];
      mockEmbeddings.embedDocuments.mockResolvedValue(mockEmbeddingsArray);

      const texts = ['text1', 'text2', 'text3'];
      const result = await embeddingsService.generateEmbeddings(texts);

      expect(result).toEqual(mockEmbeddingsArray);
      expect(mockEmbeddings.embedDocuments).toHaveBeenCalledWith(texts);
    });

    it('should handle empty array', async () => {
      mockEmbeddings.embedDocuments.mockResolvedValue([]);

      const result = await embeddingsService.generateEmbeddings([]);

      expect(result).toEqual([]);
    });

    it('should throw error on failure', async () => {
      const error = new Error('Batch embedding generation failed');
      mockEmbeddings.embedDocuments.mockRejectedValue(error);

      await expect(embeddingsService.generateEmbeddings(['text1', 'text2'])).rejects.toThrow(
        'Batch embedding generation failed'
      );
    });
  });

  describe('isModelAvailable', () => {
    it('should return true when model is available', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          models: [
            { name: 'embeddinggemma:latest' },
            { name: 'other-model' },
          ],
        }),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await embeddingsService.isModelAvailable();

      expect(result).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/tags')
      );
    });

    it('should return false when model is not available', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          models: [
            { name: 'other-model' },
          ],
        }),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await embeddingsService.isModelAvailable();

      expect(result).toBe(false);
    });

    it('should return false when API request fails', async () => {
      const mockResponse = {
        ok: false,
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await embeddingsService.isModelAvailable();

      expect(result).toBe(false);
    });

    it('should return false on network error', async () => {
      global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

      const result = await embeddingsService.isModelAvailable();

      expect(result).toBe(false);
    });

    it('should use custom OLLAMA_BASE_URL when provided', async () => {
      const originalEnv = process.env.OLLAMA_BASE_URL;
      process.env.OLLAMA_BASE_URL = 'http://custom-ollama:11434';

      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          models: [{ name: 'embeddinggemma:latest' }],
        }),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const service = new EmbeddingsService();
      await service.isModelAvailable();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('http://custom-ollama:11434')
      );

      process.env.OLLAMA_BASE_URL = originalEnv;
    });

    it('should use default OLLAMA_BASE_URL when not provided', async () => {
      const originalEnv = process.env.OLLAMA_BASE_URL;
      delete process.env.OLLAMA_BASE_URL;

      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          models: [{ name: 'embeddinggemma:latest' }],
        }),
      };

      global.fetch = vi.fn().mockResolvedValue(mockResponse);

      const service = new EmbeddingsService();
      await service.isModelAvailable();

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:11434')
      );

      process.env.OLLAMA_BASE_URL = originalEnv;
    });
  });
});

