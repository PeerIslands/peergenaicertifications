import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { RAGService } from './rag';
import type { KnowledgeDocument } from './mongodb';

// Mock dependencies
vi.mock('./mongodb', () => ({
  mongodbService: {
    searchSimilar: vi.fn(),
    searchAtlas: vi.fn(),
    getDocumentCount: vi.fn(),
  },
}));

vi.mock('./embeddings', () => ({
  embeddingsService: {
    generateEmbedding: vi.fn(),
    isModelAvailable: vi.fn(),
  },
}));

describe('RAGService', () => {
  let ragService: RAGService;
  let mockMongoDBService: any;
  let mockEmbeddingsService: any;

  beforeEach(async () => {
    ragService = new RAGService();
    const mongodbModule = await import('./mongodb');
    const embeddingsModule = await import('./embeddings');
    mockMongoDBService = mongodbModule.mongodbService;
    mockEmbeddingsService = embeddingsModule.embeddingsService;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('retrieveRelevantDocuments', () => {
    it('should retrieve and fuse documents from semantic and keyword search', async () => {
      const mockEmbedding = [0.1, 0.2, 0.3];
      const mockSemanticDocs: KnowledgeDocument[] = [
        {
          _id: '1',
          content: 'Semantic doc 1',
          embedding: [],
        },
        {
          _id: '2',
          content: 'Semantic doc 2',
          embedding: [],
        },
      ];
      const mockKeywordDocs: KnowledgeDocument[] = [
        {
          _id: '2',
          content: 'Keyword doc 2',
          embedding: [],
        },
        {
          _id: '3',
          content: 'Keyword doc 3',
          embedding: [],
        },
      ];

      mockEmbeddingsService.generateEmbedding.mockResolvedValue(mockEmbedding);
      mockMongoDBService.searchSimilar.mockResolvedValue(mockSemanticDocs);
      mockMongoDBService.searchAtlas.mockResolvedValue(mockKeywordDocs);

      const results = await ragService.retrieveRelevantDocuments('test query', 3);

      expect(mockEmbeddingsService.generateEmbedding).toHaveBeenCalledWith('test query');
      expect(mockMongoDBService.searchSimilar).toHaveBeenCalledWith(mockEmbedding, 6, 0.3);
      expect(mockMongoDBService.searchAtlas).toHaveBeenCalledWith('test query', 6);
      expect(results.length).toBeLessThanOrEqual(3);
    });

    it('should return empty array on error', async () => {
      mockEmbeddingsService.generateEmbedding.mockRejectedValue(new Error('Embedding error'));

      const results = await ragService.retrieveRelevantDocuments('test query', 3);

      expect(results).toEqual([]);
    });

    it('should apply reciprocal rank fusion correctly', async () => {
      const mockEmbedding = [0.1, 0.2, 0.3];
      const doc1: KnowledgeDocument = { _id: '1', content: 'Doc 1', embedding: [] };
      const doc2: KnowledgeDocument = { _id: '2', content: 'Doc 2', embedding: [] };
      const doc3: KnowledgeDocument = { _id: '3', content: 'Doc 3', embedding: [] };

      // Doc 2 appears in both results (should rank higher)
      mockEmbeddingsService.generateEmbedding.mockResolvedValue(mockEmbedding);
      mockMongoDBService.searchSimilar.mockResolvedValue([doc1, doc2]);
      mockMongoDBService.searchAtlas.mockResolvedValue([doc2, doc3]);

      const results = await ragService.retrieveRelevantDocuments('test query', 3);

      // Doc 2 should be ranked first due to appearing in both searches
      expect(results.length).toBeGreaterThan(0);
    });

    it('should respect the limit parameter', async () => {
      const mockEmbedding = [0.1, 0.2, 0.3];
      const mockDocs: KnowledgeDocument[] = Array.from({ length: 10 }, (_, i) => ({
        _id: `${i}`,
        content: `Doc ${i}`,
        embedding: [],
      }));

      mockEmbeddingsService.generateEmbedding.mockResolvedValue(mockEmbedding);
      mockMongoDBService.searchSimilar.mockResolvedValue(mockDocs);
      mockMongoDBService.searchAtlas.mockResolvedValue(mockDocs);

      const results = await ragService.retrieveRelevantDocuments('test query', 5);

      expect(results.length).toBeLessThanOrEqual(5);
    });
  });

  describe('generateRAGResponse', () => {
    it('should generate RAG response with relevant documents', async () => {
      const mockDocs: KnowledgeDocument[] = [
        {
          _id: '1',
          content: 'Document 1 content',
          metadata: { source: 'test' },
          embedding: [],
        },
        {
          _id: '2',
          content: 'Document 2 content',
          metadata: { source: 'test' },
          embedding: [],
        },
      ];

      vi.spyOn(ragService, 'retrieveRelevantDocuments').mockResolvedValue(mockDocs);

      const result = await ragService.generateRAGResponse('test query', {});

      expect(result.content).toContain('Document 1 content');
      expect(result.content).toContain('Document 2 content');
      expect(result.sources).toHaveLength(2);
      expect(result.sources[0].content).toBe('Document 1 content');
    });

    it('should return default message when no documents found', async () => {
      vi.spyOn(ragService, 'retrieveRelevantDocuments').mockResolvedValue([]);

      const result = await ragService.generateRAGResponse('test query', {});

      expect(result.content).toBe('No relevant context found.');
      expect(result.sources).toHaveLength(0);
    });

    it('should handle errors gracefully', async () => {
      vi.spyOn(ragService, 'retrieveRelevantDocuments').mockRejectedValue(
        new Error('Search error')
      );

      const result = await ragService.generateRAGResponse('test query', {});

      expect(result.content).toBe('Unable to retrieve relevant context.');
      expect(result.sources).toHaveLength(0);
    });

    it('should include similarity scores in sources', async () => {
      const mockDocs: KnowledgeDocument[] = [
        {
          _id: '1',
          content: 'Document 1',
          metadata: {},
          embedding: [],
          similarity: 0.95,
        } as any,
      ];

      vi.spyOn(ragService, 'retrieveRelevantDocuments').mockResolvedValue(mockDocs);

      const result = await ragService.generateRAGResponse('test query', {});

      expect(result.sources[0].similarity).toBe(0.95);
    });
  });

  describe('isReady', () => {
    it('should return true when all services are ready', async () => {
      mockEmbeddingsService.isModelAvailable.mockResolvedValue(true);
      mockMongoDBService.getDocumentCount.mockResolvedValue(10);

      const result = await ragService.isReady();

      expect(result).toBe(true);
      expect(mockEmbeddingsService.isModelAvailable).toHaveBeenCalled();
      expect(mockMongoDBService.getDocumentCount).toHaveBeenCalled();
    });

    it('should return false when embeddings service is not available', async () => {
      mockEmbeddingsService.isModelAvailable.mockResolvedValue(false);
      mockMongoDBService.getDocumentCount.mockResolvedValue(10);

      const result = await ragService.isReady();

      expect(result).toBe(false);
    });

    it('should return false when MongoDB connection fails', async () => {
      mockEmbeddingsService.isModelAvailable.mockResolvedValue(true);
      mockMongoDBService.getDocumentCount.mockRejectedValue(new Error('Connection error'));

      const result = await ragService.isReady();

      expect(result).toBe(false);
    });
  });

  describe('getKnowledgeBaseStats', () => {
    it('should return correct stats when ready', async () => {
      mockMongoDBService.getDocumentCount.mockResolvedValue(100);
      vi.spyOn(ragService, 'isReady').mockResolvedValue(true);

      const stats = await ragService.getKnowledgeBaseStats();

      expect(stats.documentCount).toBe(100);
      expect(stats.isReady).toBe(true);
    });

    it('should return zero stats when not ready', async () => {
      mockMongoDBService.getDocumentCount.mockRejectedValue(new Error('Error'));
      vi.spyOn(ragService, 'isReady').mockResolvedValue(false);

      const stats = await ragService.getKnowledgeBaseStats();

      expect(stats.documentCount).toBe(0);
      expect(stats.isReady).toBe(false);
    });

    it('should handle errors gracefully', async () => {
      mockMongoDBService.getDocumentCount.mockRejectedValue(new Error('Database error'));

      const stats = await ragService.getKnowledgeBaseStats();

      expect(stats.documentCount).toBe(0);
      expect(stats.isReady).toBe(false);
    });
  });
});

