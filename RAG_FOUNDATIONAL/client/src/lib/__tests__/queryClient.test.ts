import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiRequest, getQueryFn } from '../queryClient';

describe('queryClient', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
  });

  describe('apiRequest', () => {
    it('should make GET request without body', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => '',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await apiRequest('GET', '/api/test');

      expect(global.fetch).toHaveBeenCalledWith('/api/test', {
        method: 'GET',
        headers: {},
        body: undefined,
        credentials: 'include',
      });
    });

    it('should make POST request with JSON body', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        text: async () => '',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const data = { key: 'value' };
      await apiRequest('POST', '/api/test', data);

      expect(global.fetch).toHaveBeenCalledWith('/api/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        credentials: 'include',
      });
    });

    it('should throw error on non-ok response', async () => {
      const mockResponse = {
        ok: false,
        status: 404,
        statusText: 'Not Found',
        text: async () => 'Resource not found',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await expect(apiRequest('GET', '/api/test')).rejects.toThrow('404: Resource not found');
    });

    it('should use statusText when response text is empty', async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => '',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      await expect(apiRequest('GET', '/api/test')).rejects.toThrow('500: Internal Server Error');
    });
  });

  describe('getQueryFn', () => {
    it('should fetch and return JSON when unauthorizedBehavior is throw', async () => {
      const mockData = { id: 1, name: 'test' };
      const mockResponse = {
        ok: true,
        status: 200,
        json: async () => mockData,
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const queryFn = getQueryFn({ on401: 'throw' });
      const result = await queryFn({ queryKey: ['/api', 'test'] } as any);

      expect(global.fetch).toHaveBeenCalledWith('/api/test', {
        credentials: 'include',
      });
      expect(result).toEqual(mockData);
    });

    it('should return null on 401 when unauthorizedBehavior is returnNull', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const queryFn = getQueryFn({ on401: 'returnNull' });
      const result = await queryFn({ queryKey: ['/api', 'test'] } as any);

      expect(result).toBeNull();
    });

    it('should throw on 401 when unauthorizedBehavior is throw', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        text: async () => 'Unauthorized',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const queryFn = getQueryFn({ on401: 'throw' });
      
      await expect(queryFn({ queryKey: ['/api', 'test'] } as any)).rejects.toThrow('401: Unauthorized');
    });

    it('should throw on non-401 error response', async () => {
      const mockResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        text: async () => 'Server error',
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const queryFn = getQueryFn({ on401: 'returnNull' });
      
      await expect(queryFn({ queryKey: ['/api', 'test'] } as any)).rejects.toThrow('500: Server error');
    });

    it('should handle query key with multiple segments', async () => {
      const mockData = { result: 'success' };
      const mockResponse = {
        ok: true,
        status: 200,
        json: async () => mockData,
      };
      (global.fetch as any).mockResolvedValueOnce(mockResponse);

      const queryFn = getQueryFn({ on401: 'throw' });
      const result = await queryFn({ queryKey: ['/api', 'users', '123'] } as any);

      expect(global.fetch).toHaveBeenCalledWith('/api/users/123', {
        credentials: 'include',
      });
      expect(result).toEqual(mockData);
    });
  });

  describe('queryClient configuration', () => {
    it('should export queryClient instance', async () => {
      const { queryClient } = await import('../queryClient');
      expect(queryClient).toBeDefined();
      expect(queryClient.getDefaultOptions).toBeDefined();
    });

    it('should have correct default query options', async () => {
      const { queryClient } = await import('../queryClient');
      const options = queryClient.getDefaultOptions();
      
      expect(options.queries?.refetchInterval).toBe(false);
      expect(options.queries?.refetchOnWindowFocus).toBe(false);
      expect(options.queries?.staleTime).toBe(Infinity);
      expect(options.queries?.retry).toBe(false);
      expect(options.mutations?.retry).toBe(false);
    });
  });
});

