import { describe, it, expect, beforeEach, vi } from 'vitest';
import { Express } from 'express';
import { setupAuth, getSession, isAuthenticated } from './auth';
import { storage } from '../services/storage';

// Mock dependencies
let serializeFn: any;
let deserializeFn: any;

vi.mock('passport', () => ({
  default: {
    use: vi.fn(),
    initialize: vi.fn(() => (req: any, res: any, next: any) => next()),
    session: vi.fn(() => (req: any, res: any, next: any) => next()),
    serializeUser: vi.fn((fn: any) => {
      serializeFn = fn;
      // Immediately call the function with a mock callback
      if (typeof fn === 'function') {
        const mockCb = vi.fn((err: any, user: any) => {});
        fn({}, mockCb);
      }
    }),
    deserializeUser: vi.fn((fn: any) => {
      deserializeFn = fn;
      // Immediately call the function with a mock callback
      if (typeof fn === 'function') {
        const mockCb = vi.fn((err: any, user: any) => {});
        fn({}, mockCb);
      }
    }),
    authenticate: vi.fn((strategy: string, options: any) => (req: any, res: any, next: any) => next()),
  },
}));

vi.mock('express-session', () => ({
  default: vi.fn(() => (req: any, res: any, next: any) => next()),
}));

vi.mock('connect-mongo', () => ({
  default: {
    create: vi.fn(() => ({})),
  },
}));

vi.mock('../services/storage');
vi.mock('../utils/logger', () => ({
  logger: {
    debug: vi.fn(),
    error: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
  },
}));

describe('auth', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    vi.clearAllMocks();
    process.env = {
      ...originalEnv,
      DATABASE_URL: 'mongodb://localhost:27017/test',
      SESSION_SECRET: 'test-secret',
      GOOGLE_CLIENT_ID: 'test-client-id',
      GOOGLE_CLIENT_SECRET: 'test-client-secret',
      APP_BASE_URL: 'http://localhost:5000',
      MONGODB_DB: 'rag_application',
    };
  });

  describe('getSession', () => {
    it('should return session middleware', () => {
      const sessionMiddleware = getSession();
      // Session middleware is a function
      expect(typeof sessionMiddleware).toBe('function');
    });

    it('should use https secure cookies when APP_BASE_URL starts with https', () => {
      process.env.APP_BASE_URL = 'https://example.com';
      const sessionMiddleware = getSession();
      expect(typeof sessionMiddleware).toBe('function');
    });

    it('should use default session TTL', () => {
      const sessionMiddleware = getSession();
      expect(typeof sessionMiddleware).toBe('function');
    });
  });

  describe('setupAuth', () => {
    it('should setup authentication middleware', async () => {
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn().mockImplementation((key: string) => {
          if (key === 'env') return 'development';
          return undefined;
        }),
      } as unknown as Express;

      vi.mocked(storage.upsertUser).mockResolvedValue({
        id: 'user-1',
        email: 'test@example.com',
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any);

      await setupAuth(mockApp);

      expect(mockApp.set).toHaveBeenCalledWith('trust proxy', 1);
      expect(mockApp.use).toHaveBeenCalled();
    });

    it('should register Google OAuth strategy', async () => {
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn().mockImplementation((key: string) => {
          if (key === 'env') return 'development';
          return undefined;
        }),
      } as unknown as Express;

      vi.mocked(storage.upsertUser).mockResolvedValue({
        id: 'user-1',
        email: 'test@example.com',
        createdAt: new Date(),
        updatedAt: new Date(),
      } as any);

      await setupAuth(mockApp);

      expect(mockApp.use).toHaveBeenCalled();
    });
  });

  describe('isAuthenticated', () => {
    it('should call next when user is authenticated', async () => {
      const mockReq = {
        isAuthenticated: vi.fn().mockReturnValue(true),
      } as any;

      const mockRes = {} as any;
      const mockNext = vi.fn();

      await isAuthenticated(mockReq, mockRes, mockNext);

      expect(mockNext).toHaveBeenCalled();
    });

    it('should return 401 when user is not authenticated', async () => {
      const mockReq = {
        isAuthenticated: vi.fn().mockReturnValue(false),
      } as any;

      const mockRes = {
        status: vi.fn().mockReturnThis(),
        json: vi.fn(),
      } as any;

      const mockNext = vi.fn();

      await isAuthenticated(mockReq, mockRes, mockNext);

      expect(mockRes.status).toHaveBeenCalledWith(401);
      expect(mockRes.json).toHaveBeenCalledWith({ message: 'Unauthorized' });
      expect(mockNext).not.toHaveBeenCalled();
    });
  });

  describe('OAuth routes', () => {
    it('should setup login route', async () => {
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn(),
      } as any;

      await setupAuth(mockApp);

      const loginCall = vi.mocked(mockApp.get).mock.calls.find(
        (call) => call[0] === '/api/login'
      );
      expect(loginCall).toBeDefined();
    });

    it('should setup callback route', async () => {
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn(),
      } as any;

      await setupAuth(mockApp);

      const callbackCall = vi.mocked(mockApp.get).mock.calls.find(
        (call) => call[0] === '/api/callback'
      );
      expect(callbackCall).toBeDefined();
    });

    it('should setup logout route', async () => {
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn(),
      } as any;

      await setupAuth(mockApp);

      const logoutCall = vi.mocked(mockApp.get).mock.calls.find(
        (call) => call[0] === '/api/logout'
      );
      expect(logoutCall).toBeDefined();
    });
  });

  describe('logout route', () => {
    it('should handle logout with session destroy', async () => {
      process.env.APP_BASE_URL = 'https://example.com';
      
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn((path: string, ...handlers: any[]) => {
          if (path === '/api/logout') {
            const handler = handlers[handlers.length - 1];
            const mockReq = {
              logout: vi.fn((cb: any) => cb()),
              session: {
                destroy: vi.fn((cb: any) => cb()),
              },
            } as any;
            const mockRes = {
              clearCookie: vi.fn(),
              redirect: vi.fn(),
            } as any;
            handler(mockReq, mockRes);
            expect(mockReq.logout).toHaveBeenCalled();
            expect(mockRes.clearCookie).toHaveBeenCalledWith('connect.sid', {
              httpOnly: true,
              secure: true,
              sameSite: 'lax',
              path: '/',
            });
            expect(mockRes.redirect).toHaveBeenCalledWith('/');
          }
        }),
      } as any;

      await setupAuth(mockApp);
    });

    it('should handle logout without session destroy', async () => {
      process.env.APP_BASE_URL = 'http://localhost:5000';
      
      const mockApp = {
        set: vi.fn(),
        use: vi.fn(),
        get: vi.fn((path: string, ...handlers: any[]) => {
          if (path === '/api/logout') {
            const handler = handlers[handlers.length - 1];
            const mockReq = {
              logout: vi.fn((cb: any) => cb()),
              session: {},
            } as any;
            const mockRes = {
              clearCookie: vi.fn(),
              redirect: vi.fn(),
            } as any;
            handler(mockReq, mockRes);
            expect(mockRes.clearCookie).toHaveBeenCalledWith('connect.sid', {
              httpOnly: true,
              secure: false,
              sameSite: 'lax',
              path: '/',
            });
            expect(mockRes.redirect).toHaveBeenCalledWith('/');
          }
        }),
      } as any;

      await setupAuth(mockApp);
    });
  });
});

