import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { api, ApiError } from '../api';

// Mock fetch
global.fetch = vi.fn();

describe('api', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('ApiError', () => {
    it('should create an ApiError with status and message', () => {
      const error = new ApiError(404, 'Not Found');
      expect(error.status).toBe(404);
      expect(error.message).toBe('Not Found');
      expect(error.name).toBe('ApiError');
    });
  });

  describe('pdfs.list', () => {
    it('should fetch and return list of PDFs', async () => {
      const mockPdfs = [{ id: '1', originalName: 'test.pdf' }];
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPdfs,
      });

      const result = await api.pdfs.list();
      expect(result).toEqual(mockPdfs);
      expect(global.fetch).toHaveBeenCalledWith('/api/pdfs', expect.any(Object));
    });

    it('should throw ApiError on failed request', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
      });

      await expect(api.pdfs.list()).rejects.toThrow(ApiError);
      
      // Reset mock and test error message
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Server error' }),
      });
      
      try {
        await api.pdfs.list();
      } catch (error: any) {
        expect(error.message).toContain('Server error');
      }
    });
  });

  describe('pdfs.get', () => {
    it('should fetch and return a single PDF', async () => {
      const mockPdf = { id: '1', originalName: 'test.pdf' };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPdf,
      });

      const result = await api.pdfs.get('1');
      expect(result).toEqual(mockPdf);
      expect(global.fetch).toHaveBeenCalledWith('/api/pdfs/1', expect.any(Object));
    });
  });

  describe('pdfs.upload', () => {
    it('should upload a file and return PDF object', async () => {
      const mockPdf = { id: '1', originalName: 'test.pdf' };
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPdf,
      });

      const result = await api.pdfs.upload(file);
      expect(result).toEqual(mockPdf);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/pdfs/upload',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData),
        })
      );
    });

    it('should throw ApiError on failed upload', async () => {
      const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
      
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 400,
        statusText: 'Bad Request',
        json: async () => ({ error: 'Invalid file' }),
      });

      await expect(api.pdfs.upload(file)).rejects.toThrow(ApiError);
    });
  });

  describe('pdfs.delete', () => {
    it('should delete a PDF', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const result = await api.pdfs.delete('1');
      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/pdfs/1',
        expect.objectContaining({ method: 'DELETE' })
      );
    });
  });

  describe('pdfs.download', () => {
    it('should return download URL', () => {
      const url = api.pdfs.download('1');
      expect(url).toBe('/api/pdfs/1/download');
    });
  });

  describe('pdfs.search', () => {
    it('should search PDFs and return results', async () => {
      const mockPdfs = [{ id: '1', originalName: 'test.pdf' }];
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockPdfs,
      });

      const result = await api.pdfs.search('test query');
      expect(result).toEqual(mockPdfs);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/pdfs/search?q=test%20query',
        expect.any(Object)
      );
    });

    it('should encode search query properly', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await api.pdfs.search('test & query');
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/pdfs/search?q=test%20%26%20query',
        expect.any(Object)
      );
    });
  });

  describe('rag.chat', () => {
    it('should send chat messages and return reply', async () => {
      const mockResponse = {
        reply: 'Test reply',
        sources: [{ pdfId: '1', preview: 'Test preview' }],
      };
      (global.fetch as any).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const messages = [{ role: 'user', content: 'Hello' }];
      const result = await api.rag.chat(messages);
      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        '/api/rag/chat',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ messages }),
        })
      );
    });

    it('should throw ApiError on failed chat request', async () => {
      (global.fetch as any).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => ({ error: 'Chat failed' }),
      });

      await expect(
        api.rag.chat([{ role: 'user', content: 'Hello' }])
      ).rejects.toThrow(ApiError);
    });
  });
});

