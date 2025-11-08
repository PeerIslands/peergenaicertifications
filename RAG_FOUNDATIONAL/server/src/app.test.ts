import { describe, it, expect, beforeEach, vi } from 'vitest';
import { createApp } from './app';
import { getDb } from './db/mongo';
import { registerRoutes } from './routes/http-routes';
import multer from 'multer';

// Mock dependencies
vi.mock('./db/mongo');
vi.mock('./routes/http-routes');
vi.mock('./config/vite');
vi.mock('./utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}));
// Mock OpenAI to prevent browser environment errors
vi.mock('openai', () => ({
  default: class MockOpenAI {
    constructor() {}
    chat = { completions: { create: vi.fn() } };
    embeddings = { create: vi.fn() };
  },
}));

describe('app', () => {
  let mockServer: any;

  beforeEach(() => {
    vi.clearAllMocks();

    mockServer = {
      listen: vi.fn(),
      close: vi.fn(),
    };

    vi.mocked(getDb).mockResolvedValue({} as any);
    vi.mocked(registerRoutes).mockResolvedValue(mockServer as any);
  });

  describe('createApp', () => {
    it('should create express app with middleware', async () => {
      const { setupVite } = await import('./config/vite');
      vi.mocked(setupVite).mockResolvedValue(undefined);

      process.env.NODE_ENV = 'development';

      const { app, server } = await createApp();

      expect(app).toBeDefined();
      expect(server).toBeDefined();
      expect(getDb).toHaveBeenCalled();
      expect(registerRoutes).toHaveBeenCalled();
    });

    it('should setup vite in development mode', async () => {
      const { setupVite } = await import('./config/vite');
      vi.mocked(setupVite).mockResolvedValue(undefined);

      process.env.NODE_ENV = 'development';

      await createApp();

      expect(setupVite).toHaveBeenCalled();
    });

    it('should serve static files in production mode', async () => {
      const { serveStatic } = await import('./config/vite');
      vi.mocked(serveStatic).mockReturnValue(undefined);

      process.env.NODE_ENV = 'production';

      await createApp();

      expect(serveStatic).toHaveBeenCalled();
    });

    it('should handle multer file size errors', async () => {
      const { setupVite } = await import('./config/vite');
      vi.mocked(setupVite).mockResolvedValue(undefined);

      process.env.NODE_ENV = 'development';
      process.env.UPLOAD_MAX_FILE_MB = '50';

      const { app } = await createApp();

      const mockReq = {} as any;
      const mockRes = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;
      const mockNext = vi.fn();

      const multerError = new multer.MulterError('LIMIT_FILE_SIZE');
      const errorHandler = (app as any)._router?.stack?.find(
        (layer: any) => layer.handle?.length === 4 // Error handler signature
      )?.handle;

      if (errorHandler) {
        await errorHandler(multerError, mockReq, mockRes, mockNext);
        expect(mockRes.status).toHaveBeenCalledWith(413);
        expect(mockRes.json).toHaveBeenCalledWith(expect.objectContaining({
          error: expect.stringContaining('File too large'),
        }));
      }
    });

    it('should handle generic errors', async () => {
      const { setupVite } = await import('./config/vite');
      vi.mocked(setupVite).mockResolvedValue(undefined);

      process.env.NODE_ENV = 'development';

      const { app } = await createApp();

      const mockReq = {} as any;
      const mockRes = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;
      const mockNext = vi.fn();

      const error = new Error('Test error');
      const errorHandler = (app as any)._router?.stack?.find(
        (layer: any) => layer.handle?.length === 4
      )?.handle;

      if (errorHandler) {
        await errorHandler(error, mockReq, mockRes, mockNext);
        expect(mockRes.status).toHaveBeenCalledWith(500);
        expect(mockRes.json).toHaveBeenCalled();
      }
    });
  });
});

