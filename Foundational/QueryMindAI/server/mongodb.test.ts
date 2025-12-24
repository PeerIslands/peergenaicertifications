import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { MongoDBService } from './mongodb';
import type { KnowledgeDocument } from './mongodb';

// Mock MongoDB client
vi.mock('mongodb', () => ({
  MongoClient: vi.fn().mockImplementation(() => ({
    connect: vi.fn(),
    close: vi.fn(),
    db: vi.fn().mockReturnValue({
      collection: vi.fn().mockReturnValue({
        aggregate: vi.fn().mockReturnValue({
          toArray: vi.fn(),
        }),
        find: vi.fn().mockReturnValue({
          toArray: vi.fn(),
        }),
        countDocuments: vi.fn(),
      }),
    }),
  })),
}));

describe('MongoDBService', () => {
  let mongodbService: MongoDBService;
  let mockCollection: any;
  let mockClient: any;

  beforeEach(async () => {
    const { MongoClient } = await import('mongodb');
    mongodbService = new MongoDBService();
    mockClient = (mongodbService as any).client;
    mockCollection = (mongodbService as any).collection;
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('connect', () => {
    it('should connect to MongoDB successfully', async () => {
      mockClient.connect.mockResolvedValue(undefined);

      await mongodbService.connect();

      expect(mockClient.connect).toHaveBeenCalled();
    });

    it('should throw error on connection failure', async () => {
      const error = new Error('Connection failed');
      mockClient.connect.mockRejectedValue(error);

      await expect(mongodbService.connect()).rejects.toThrow('Connection failed');
    });
  });

  describe('disconnect', () => {
    it('should close MongoDB connection', async () => {
      mockClient.close.mockResolvedValue(undefined);

      await mongodbService.disconnect();

      expect(mockClient.close).toHaveBeenCalled();
    });
  });

  describe('searchSimilar', () => {
    it('should perform cosine similarity search', async () => {
      const queryEmbedding = [0.1, 0.2, 0.3];
      const mockResults = [
        {
          _id: '1',
          chunk_text: 'Document 1',
          metadata: { source: 'test' },
          embedding: [0.1, 0.2, 0.3],
          similarity: 0.95,
        },
        {
          _id: '2',
          chunk_text: 'Document 2',
          metadata: { source: 'test' },
          embedding: [0.2, 0.3, 0.4],
          similarity: 0.85,
        },
      ];

      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockResolvedValue(mockResults);

      const results = await mongodbService.searchSimilar(queryEmbedding, 5, 0.7);

      expect(mockCollection.aggregate).toHaveBeenCalled();
      expect(results).toHaveLength(2);
      expect(results[0].content).toBe('Document 1');
      expect(results[0].metadata).toEqual({ source: 'test' });
    });

    it('should filter by similarity threshold', async () => {
      const queryEmbedding = [0.1, 0.2, 0.3];
      const mockResults = [
        {
          _id: '1',
          chunk_text: 'High similarity',
          embedding: [],
          similarity: 0.95,
        },
        {
          _id: '2',
          chunk_text: 'Low similarity',
          embedding: [],
          similarity: 0.5, // Below threshold
        },
      ];

      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockResolvedValue(mockResults);

      const results = await mongodbService.searchSimilar(queryEmbedding, 5, 0.7);

      // The aggregation pipeline should filter by threshold
      expect(mockCollection.aggregate).toHaveBeenCalled();
    });

    it('should handle empty results', async () => {
      const queryEmbedding = [0.1, 0.2, 0.3];
      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockResolvedValue([]);

      const results = await mongodbService.searchSimilar(queryEmbedding, 5, 0.7);

      expect(results).toHaveLength(0);
    });

    it('should handle documents without chunk_text', async () => {
      const queryEmbedding = [0.1, 0.2, 0.3];
      const mockResults = [
        {
          _id: '1',
          metadata: {},
          embedding: [],
        },
      ];

      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockResolvedValue(mockResults);

      const results = await mongodbService.searchSimilar(queryEmbedding, 5, 0.7);

      expect(results[0].content).toBe('');
    });

    it('should throw error on search failure', async () => {
      const queryEmbedding = [0.1, 0.2, 0.3];
      const error = new Error('Search failed');
      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockRejectedValue(error);

      await expect(mongodbService.searchSimilar(queryEmbedding, 5, 0.7)).rejects.toThrow(
        'Search failed'
      );
    });
  });

  describe('getAllDocuments', () => {
    it('should retrieve all documents', async () => {
      const mockDocuments: KnowledgeDocument[] = [
        {
          _id: '1',
          content: 'Document 1',
          embedding: [],
        },
        {
          _id: '2',
          content: 'Document 2',
          embedding: [],
        },
      ];

      const mockFind = mockCollection.find();
      mockFind.toArray.mockResolvedValue(mockDocuments);

      const results = await mongodbService.getAllDocuments();

      expect(mockCollection.find).toHaveBeenCalledWith({});
      expect(results).toEqual(mockDocuments);
    });

    it('should handle empty collection', async () => {
      const mockFind = mockCollection.find();
      mockFind.toArray.mockResolvedValue([]);

      const results = await mongodbService.getAllDocuments();

      expect(results).toHaveLength(0);
    });

    it('should throw error on failure', async () => {
      const error = new Error('Query failed');
      const mockFind = mockCollection.find();
      mockFind.toArray.mockRejectedValue(error);

      await expect(mongodbService.getAllDocuments()).rejects.toThrow('Query failed');
    });
  });

  describe('searchAtlas', () => {
    it('should perform Atlas Search with BM25', async () => {
      const query = 'test query';
      const mockResults = [
        {
          _id: '1',
          chunk_text: 'Relevant document',
          metadata: { source: 'test' },
          embedding: [],
          score: 0.95,
        },
      ];

      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockResolvedValue(mockResults);

      const results = await mongodbService.searchAtlas(query, 5);

      expect(mockCollection.aggregate).toHaveBeenCalled();
      expect(results).toHaveLength(1);
      expect(results[0].content).toBe('Relevant document');
    });

    it('should respect limit parameter', async () => {
      const query = 'test';
      const mockResults = Array.from({ length: 10 }, (_, i) => ({
        _id: `${i}`,
        chunk_text: `Doc ${i}`,
        metadata: {},
        embedding: [],
        score: 0.9,
      }));

      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockResolvedValue(mockResults);

      const results = await mongodbService.searchAtlas(query, 5);

      // The aggregation pipeline should limit results
      expect(mockCollection.aggregate).toHaveBeenCalled();
    });

    it('should handle search errors', async () => {
      const query = 'test';
      const error = new Error('Atlas Search failed');
      const mockAggregate = mockCollection.aggregate();
      mockAggregate.toArray.mockRejectedValue(error);

      await expect(mongodbService.searchAtlas(query, 5)).rejects.toThrow(
        'Atlas Search failed'
      );
    });
  });

  describe('getDocumentCount', () => {
    it('should return document count', async () => {
      mockCollection.countDocuments.mockResolvedValue(100);

      const count = await mongodbService.getDocumentCount();

      expect(count).toBe(100);
      expect(mockCollection.countDocuments).toHaveBeenCalledWith();
    });

    it('should return zero for empty collection', async () => {
      mockCollection.countDocuments.mockResolvedValue(0);

      const count = await mongodbService.getDocumentCount();

      expect(count).toBe(0);
    });

    it('should throw error on failure', async () => {
      const error = new Error('Count failed');
      mockCollection.countDocuments.mockRejectedValue(error);

      await expect(mongodbService.getDocumentCount()).rejects.toThrow('Count failed');
    });
  });

  describe('constructor', () => {
    it('should use environment variables for configuration', () => {
      const originalUri = process.env.MONGODB_URI;
      const originalDb = process.env.MONGODB_DATABASE;
      const originalCollection = process.env.MONGODB_COLLECTION;

      process.env.MONGODB_URI = 'mongodb://test-uri';
      process.env.MONGODB_DATABASE = 'test-db';
      process.env.MONGODB_COLLECTION = 'test-collection';

      const service = new MongoDBService();

      expect(service).toBeDefined();

      process.env.MONGODB_URI = originalUri;
      process.env.MONGODB_DATABASE = originalDb;
      process.env.MONGODB_COLLECTION = originalCollection;
    });

    it('should use default values when environment variables are not set', () => {
      const originalUri = process.env.MONGODB_URI;
      const originalDb = process.env.MONGODB_DATABASE;
      const originalCollection = process.env.MONGODB_COLLECTION;

      delete process.env.MONGODB_URI;
      delete process.env.MONGODB_DATABASE;
      delete process.env.MONGODB_COLLECTION;

      const service = new MongoDBService();

      expect(service).toBeDefined();

      process.env.MONGODB_URI = originalUri;
      process.env.MONGODB_DATABASE = originalDb;
      process.env.MONGODB_COLLECTION = originalCollection;
    });
  });
});

