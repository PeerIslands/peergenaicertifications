import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { MongoClient } from 'mongodb';
import { getDb, closeMongo } from './mongo';

// Mock MongoDB
vi.mock('mongodb');
vi.mock('../utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}));

describe('mongo', () => {
  const originalEnv = process.env.DATABASE_URL;
  const originalMongoDb = process.env.MONGODB_DB;

  let mockDb: any;
  let mockClient: any;
  let mockCollection: any;

  beforeEach(() => {
    vi.clearAllMocks();
    
    // Reset module state
    vi.resetModules();

    mockCollection = {
      createIndex: vi.fn().mockResolvedValue(true),
      findOne: vi.fn(),
      find: vi.fn(),
    };

    mockDb = {
      listCollections: vi.fn().mockReturnValue({
        toArray: vi.fn().mockResolvedValue([
          { name: 'users' },
          { name: 'pdfs' },
        ]),
      }),
      createCollection: vi.fn().mockResolvedValue(true),
      collection: vi.fn().mockReturnValue(mockCollection),
    };

    mockClient = {
      connect: vi.fn().mockResolvedValue(undefined),
      close: vi.fn().mockResolvedValue(undefined),
      db: vi.fn().mockReturnValue(mockDb),
    };

    (MongoClient as any).mockImplementation(() => mockClient);
  });

  afterEach(async () => {
    await closeMongo();
    process.env.DATABASE_URL = originalEnv;
    process.env.MONGODB_DB = originalMongoDb;
  });

  describe('getDb', () => {
    it('should connect to MongoDB and return db instance', async () => {
      process.env.DATABASE_URL = 'mongodb://localhost:27017/test';
      
      const db = await getDb();
      
      expect(MongoClient).toHaveBeenCalledWith('mongodb://localhost:27017/test', {});
      expect(mockClient.connect).toHaveBeenCalled();
      expect(mockClient.db).toHaveBeenCalled();
      expect(db).toBe(mockDb);
    });

    it('should throw error when DATABASE_URL is not set', async () => {
      delete process.env.DATABASE_URL;
      
      await expect(getDb()).rejects.toThrow('DATABASE_URL is not set');
    });

    it('should return cached db instance on subsequent calls', async () => {
      process.env.DATABASE_URL = 'mongodb://localhost:27017/test';
      
      const db1 = await getDb();
      const db2 = await getDb();
      
      expect(db1).toBe(db2);
      expect(MongoClient).toHaveBeenCalledTimes(1);
      expect(mockClient.connect).toHaveBeenCalledTimes(1);
    });

    it('should ensure collections are created', async () => {
      process.env.DATABASE_URL = 'mongodb://localhost:27017/test';
      mockDb.listCollections().toArray.mockResolvedValue([]);
      
      await getDb();
      
      expect(mockDb.createCollection).toHaveBeenCalledWith('users');
      expect(mockDb.createCollection).toHaveBeenCalledWith('pdfs');
      expect(mockDb.createCollection).toHaveBeenCalledWith('sessions');
      expect(mockDb.createCollection).toHaveBeenCalledWith('vectors');
      expect(mockDb.createCollection).toHaveBeenCalledWith('chat_queries');
      expect(mockDb.createCollection).toHaveBeenCalledWith('chat_responses');
    });
  });

  describe('closeMongo', () => {
    it('should close MongoDB connection', async () => {
      process.env.DATABASE_URL = 'mongodb://localhost:27017/test';
      await getDb();
      
      await closeMongo();
      
      expect(mockClient.close).toHaveBeenCalled();
    });

    it('should handle close when no client exists', async () => {
      await expect(closeMongo()).resolves.not.toThrow();
    });
  });
});

