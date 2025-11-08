import { describe, it, expect, beforeEach, vi } from 'vitest';
import { storage, MongoStorage } from './storage';
import { getDb } from '../db/mongo';

// Mock dependencies
vi.mock('../db/mongo');

describe('MongoStorage', () => {
  let mockDb: any;
  let mockCollection: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockCollection = {
      findOne: vi.fn(),
      find: vi.fn().mockReturnValue({
        sort: vi.fn().mockReturnValue({
          toArray: vi.fn().mockResolvedValue([]),
        }),
      }),
      insertOne: vi.fn().mockResolvedValue({ insertedId: 'test-id' }),
      updateOne: vi.fn().mockResolvedValue({ modifiedCount: 1 }),
      findOneAndUpdate: vi.fn().mockResolvedValue({
        value: { id: 'test-id', userId: 'user-1', fileName: 'test.pdf' },
      }),
      deleteOne: vi.fn().mockResolvedValue({ deletedCount: 1 }),
    };

    mockDb = {
      collection: vi.fn().mockReturnValue(mockCollection),
    };

    vi.mocked(getDb).mockResolvedValue(mockDb as any);
  });

  describe('getUser', () => {
    it('should retrieve a user by id', async () => {
      const mockUser = {
        id: 'user-1',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
      };
      mockCollection.findOne.mockResolvedValue(mockUser);

      const user = await storage.getUser('user-1');

      expect(mockDb.collection).toHaveBeenCalledWith('users');
      expect(mockCollection.findOne).toHaveBeenCalledWith({ id: 'user-1' });
      expect(user).toEqual(mockUser);
    });

    it('should return undefined when user not found', async () => {
      mockCollection.findOne.mockResolvedValue(null);

      const user = await storage.getUser('non-existent');

      expect(user).toBeNull();
    });
  });

  describe('upsertUser', () => {
    it('should create a new user when user does not exist', async () => {
      mockCollection.findOne.mockResolvedValue(null);

      const userData = {
        id: 'user-1',
        email: 'test@example.com',
        firstName: 'Test',
        lastName: 'User',
      };

      const user = await storage.upsertUser(userData);

      expect(mockDb.collection).toHaveBeenCalledWith('users');
      expect(mockCollection.findOne).toHaveBeenCalledWith({ id: 'user-1' });
      expect(mockCollection.updateOne).toHaveBeenCalledWith(
        { id: 'user-1' },
        { $set: expect.objectContaining({ id: 'user-1', email: 'test@example.com' }) },
        { upsert: true }
      );
      expect(user.id).toBe('user-1');
      expect(user.email).toBe('test@example.com');
    });

    it('should update existing user when user exists', async () => {
      const existingUser = {
        id: 'user-1',
        email: 'old@example.com',
        firstName: 'Old',
        createdAt: new Date('2020-01-01'),
      };
      mockCollection.findOne.mockResolvedValue(existingUser);

      const userData = {
        id: 'user-1',
        email: 'new@example.com',
        firstName: 'New',
      };

      const user = await storage.upsertUser(userData);

      expect(mockCollection.updateOne).toHaveBeenCalled();
      expect(user.id).toBe('user-1');
    });
  });

  describe('getPdfs', () => {
    it('should retrieve all PDFs for a user', async () => {
      const mockPdfs = [
        { id: 'pdf-1', userId: 'user-1', fileName: 'test1.pdf' },
        { id: 'pdf-2', userId: 'user-1', fileName: 'test2.pdf' },
      ];

      const mockFind = {
        sort: vi.fn().mockReturnValue({
          toArray: vi.fn().mockResolvedValue(mockPdfs),
        }),
      };
      mockCollection.find.mockReturnValue(mockFind);

      const pdfs = await storage.getPdfs('user-1');

      expect(mockDb.collection).toHaveBeenCalledWith('pdfs');
      expect(mockCollection.find).toHaveBeenCalledWith({ userId: 'user-1' });
      expect(pdfs).toEqual(mockPdfs);
    });

    it('should return empty array when no PDFs found', async () => {
      const pdfs = await storage.getPdfs('user-1');
      expect(pdfs).toEqual([]);
    });
  });

  describe('getPdf', () => {
    it('should retrieve a PDF by id', async () => {
      const mockPdf = {
        id: 'pdf-1',
        userId: 'user-1',
        fileName: 'test.pdf',
        originalName: 'Test.pdf',
      };
      mockCollection.findOne.mockResolvedValue(mockPdf);

      const pdf = await storage.getPdf('pdf-1');

      expect(mockDb.collection).toHaveBeenCalledWith('pdfs');
      expect(mockCollection.findOne).toHaveBeenCalledWith({ id: 'pdf-1' });
      expect(pdf).toEqual(mockPdf);
    });

    it('should return undefined when PDF not found', async () => {
      mockCollection.findOne.mockResolvedValue(null);

      const pdf = await storage.getPdf('non-existent');

      expect(pdf).toBeNull();
    });
  });

  describe('createPdf', () => {
    it('should create a new PDF document', async () => {
      const insertPdf = {
        userId: 'user-1',
        fileName: 'test.pdf',
        originalName: 'Test.pdf',
        filePath: '/path/to/file',
        fileSize: 1024,
        pageCount: 1,
        extractedText: 'test content',
      };

      const pdf = await storage.createPdf(insertPdf);

      expect(mockDb.collection).toHaveBeenCalledWith('pdfs');
      expect(mockCollection.insertOne).toHaveBeenCalled();
      expect(pdf.id).toBeDefined();
      expect(pdf.userId).toBe('user-1');
      expect(pdf.fileName).toBe('test.pdf');
      expect(pdf.uploadedAt).toBeInstanceOf(Date);
    });
  });

  describe('updatePdf', () => {
    it('should update an existing PDF', async () => {
      const updates = { extractedText: 'updated content' };
      mockCollection.findOneAndUpdate.mockResolvedValue({
        value: { id: 'pdf-1', extractedText: 'updated content' },
      });

      const pdf = await storage.updatePdf('pdf-1', updates);

      expect(mockDb.collection).toHaveBeenCalledWith('pdfs');
      expect(mockCollection.findOneAndUpdate).toHaveBeenCalledWith(
        { id: 'pdf-1' },
        { $set: updates },
        { returnDocument: 'after' }
      );
      expect(pdf).toBeDefined();
      expect(pdf?.extractedText).toBe('updated content');
    });

    it('should return undefined when PDF not found', async () => {
      mockCollection.findOneAndUpdate.mockResolvedValue({ value: null });

      const pdf = await storage.updatePdf('non-existent', {});

      expect(pdf).toBeUndefined();
    });
  });

  describe('deletePdf', () => {
    it('should delete a PDF by id', async () => {
      const deleted = await storage.deletePdf('pdf-1');

      expect(mockDb.collection).toHaveBeenCalledWith('pdfs');
      expect(mockCollection.deleteOne).toHaveBeenCalledWith({ id: 'pdf-1' });
      expect(deleted).toBe(true);
    });

    it('should return false when PDF not found', async () => {
      mockCollection.deleteOne.mockResolvedValue({ deletedCount: 0 });

      const deleted = await storage.deletePdf('non-existent');

      expect(deleted).toBe(false);
    });
  });

  describe('searchPdfs', () => {
    it('should search PDFs by query', async () => {
      const mockPdfs = [
        { id: 'pdf-1', userId: 'user-1', originalName: 'test.pdf', extractedText: 'search term' },
      ];

      const mockFind = {
        sort: vi.fn().mockReturnValue({
          toArray: vi.fn().mockResolvedValue(mockPdfs),
        }),
      };
      mockCollection.find.mockReturnValue(mockFind);

      const pdfs = await storage.searchPdfs('user-1', 'search');

      expect(mockDb.collection).toHaveBeenCalledWith('pdfs');
      expect(mockCollection.find).toHaveBeenCalled();
      expect(pdfs).toEqual(mockPdfs);
    });

    it('should return empty array when no matches found', async () => {
      const pdfs = await storage.searchPdfs('user-1', 'non-existent');
      expect(pdfs).toEqual([]);
    });
  });
});

