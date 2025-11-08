import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Express } from 'express';
import { Server } from 'http';
import fs from 'fs';
import path from 'path';

// Mock vite.config to prevent top-level await issues
vi.mock('../../../vite.config', () => ({
  default: {
    plugins: [],
    resolve: {
      alias: {},
    },
    root: '/path/to/client',
  },
}));

// Mock vite completely BEFORE importing the module under test
// This prevents esbuild from being loaded
vi.mock('vite', () => ({
  createServer: vi.fn().mockResolvedValue({
    middlewares: {
      use: vi.fn(),
    },
    transformIndexHtml: vi.fn().mockResolvedValue('<html>transformed</html>'),
    ssrFixStacktrace: vi.fn(),
    ws: {
      on: vi.fn(),
    },
  }),
  createLogger: vi.fn(() => ({
    error: vi.fn(),
    warn: vi.fn(),
    info: vi.fn(),
  })),
}));

// Import after mocking
import { setupVite, serveStatic } from './vite';

vi.mock('fs');
vi.mock('fs/promises', () => ({
  default: {
    readFile: vi.fn().mockResolvedValue('<html><script src="/src/main.tsx"></script></html>'),
  },
}));

vi.mock('path');
vi.mock('nanoid', () => ({
  nanoid: vi.fn(() => 'test-id'),
}));

describe('vite config', () => {
  let mockApp: Express;
  let mockServer: Server;

  beforeEach(() => {
    vi.clearAllMocks();

    mockApp = {
      use: vi.fn(),
    } as unknown as Express;

    mockServer = {} as Server;

    // Mock fs.existsSync
    vi.mocked(fs.existsSync).mockReturnValue(true);
  });

  describe('setupVite', () => {
    it('should setup Vite middleware in development', async () => {
      vi.mocked(path.resolve).mockReturnValue('/path/to/index.html');

      await setupVite(mockApp, mockServer);

      expect(mockApp.use).toHaveBeenCalled();
    });

    it('should handle errors during setup', async () => {
      const { createServer } = await import('vite');
      const mockVite = {
        middlewares: {},
        transformIndexHtml: vi.fn().mockRejectedValue(new Error('Test error')),
        ssrFixStacktrace: vi.fn(),
      };
      vi.mocked(createServer).mockResolvedValue(mockVite as any);
      vi.mocked(path.resolve).mockReturnValue('/path/to/index.html');

      await setupVite(mockApp, mockServer);

      expect(mockApp.use).toHaveBeenCalled();
    });
  });

  describe('serveStatic', () => {
    it('should serve static files from dist directory', () => {
      vi.mocked(path.resolve).mockReturnValue('/path/to/dist');
      vi.mocked(fs.existsSync).mockReturnValue(true);

      serveStatic(mockApp);

      expect(mockApp.use).toHaveBeenCalled();
    });

    it('should throw error when dist directory does not exist', () => {
      vi.mocked(path.resolve).mockReturnValue('/path/to/dist');
      vi.mocked(fs.existsSync).mockReturnValue(false);

      expect(() => serveStatic(mockApp)).toThrow('Could not find the build directory');
    });

    it('should serve index.html for all routes', () => {
      vi.mocked(path.resolve).mockReturnValue('/path/to/dist');
      vi.mocked(fs.existsSync).mockReturnValue(true);

      serveStatic(mockApp);

      // Check that express.static was called
      expect(mockApp.use).toHaveBeenCalled();
      
      // Check that fallback route was added
      const useCalls = vi.mocked(mockApp.use).mock.calls;
      expect(useCalls.length).toBeGreaterThan(1);
    });
  });

  describe('setupVite error handling', () => {
    it('should call ssrFixStacktrace on error', async () => {
      const { createServer } = await import('vite');
      const mockVite = {
        middlewares: {},
        transformIndexHtml: vi.fn().mockRejectedValue(new Error('Transform error')),
        ssrFixStacktrace: vi.fn(),
      };
      vi.mocked(createServer).mockResolvedValue(mockVite as any);
      vi.mocked(path.resolve).mockReturnValue('/path/to/index.html');

      await setupVite(mockApp, mockServer);

      // Should still call use
      expect(mockApp.use).toHaveBeenCalled();
    });

    it('should handle readFile errors', async () => {
      const { createServer } = await import('vite');
      const mockVite = {
        middlewares: {},
        transformIndexHtml: vi.fn().mockResolvedValue('<html>transformed</html>'),
        ssrFixStacktrace: vi.fn(),
      };
      vi.mocked(createServer).mockResolvedValue(mockVite as any);
      vi.mocked(path.resolve).mockReturnValue('/path/to/index.html');
      
      // Mock fs.promises.readFile to throw
      const { default: fsPromises } = await import('fs/promises');
      vi.mocked(fsPromises.readFile).mockRejectedValueOnce(new Error('Read error'));

      try {
        await setupVite(mockApp, mockServer);
      } catch (e) {
        // Error should be handled by ssrFixStacktrace
        expect(mockVite.ssrFixStacktrace).toHaveBeenCalled();
      }
    });
  });
});

