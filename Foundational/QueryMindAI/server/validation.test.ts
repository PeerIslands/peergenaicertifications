import { describe, it, expect, vi, beforeEach } from 'vitest';
import type { Request, Response, NextFunction } from 'express';
import { z } from 'zod';
import { validate } from './validation';

describe('validate middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let mockNext: NextFunction;

  beforeEach(() => {
    mockRequest = {
      body: {},
      params: {},
      query: {},
    };
    mockResponse = {
      status: vi.fn().mockReturnThis(),
      json: vi.fn().mockReturnThis(),
    };
    mockNext = vi.fn();
  });

  it('should validate body data successfully', async () => {
    const schema = z.object({
      message: z.string().min(1),
      sessionId: z.string(),
    });

    mockRequest.body = {
      message: 'Hello',
      sessionId: 'test-session',
    };

    const middleware = validate(schema, 'body');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
  });

  it('should reject invalid body data', async () => {
    const schema = z.object({
      message: z.string().min(1),
      sessionId: z.string(),
    });

    mockRequest.body = {
      message: '', // Invalid: empty string
      sessionId: 'test-session',
    };

    const middleware = validate(schema, 'body');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).not.toHaveBeenCalled();
    expect(mockResponse.status).toHaveBeenCalledWith(400);
    expect(mockResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        error: 'Validation failed',
      })
    );
  });

  it('should validate params data successfully', async () => {
    const schema = z.object({
      conversationId: z.string().uuid(),
    });

    mockRequest.params = {
      conversationId: '123e4567-e89b-12d3-a456-426614174000',
    };

    const middleware = validate(schema, 'params');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
  });

  it('should reject invalid params data', async () => {
    const schema = z.object({
      conversationId: z.string().uuid(),
    });

    mockRequest.params = {
      conversationId: 'invalid-uuid',
    };

    const middleware = validate(schema, 'params');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).not.toHaveBeenCalled();
    expect(mockResponse.status).toHaveBeenCalledWith(400);
  });

  it('should validate query data successfully', async () => {
    const schema = z.object({
      query: z.string().min(1),
      limit: z.string().optional(),
    });

    mockRequest.query = {
      query: 'test query',
      limit: '5',
    };

    const middleware = validate(schema, 'query');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
  });

  it('should validate all sources (body, params, query)', async () => {
    const schema = z.object({
      body: z.object({ message: z.string() }),
      params: z.object({ id: z.string() }),
      query: z.object({ limit: z.string().optional() }),
    });

    mockRequest.body = { message: 'test' };
    mockRequest.params = { id: '123' };
    mockRequest.query = { limit: '10' };

    const middleware = validate(schema, 'all');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).toHaveBeenCalled();
    expect(mockResponse.status).not.toHaveBeenCalled();
  });

  it('should replace original data with validated data', async () => {
    const schema = z.object({
      message: z.string().min(1).transform((val) => val.trim()),
    });

    mockRequest.body = {
      message: '  Hello  ',
    };

    const middleware = validate(schema, 'body');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockRequest.body.message).toBe('Hello');
    expect(mockNext).toHaveBeenCalled();
  });

  it('should handle non-Zod errors', async () => {
    const schema = {
      parseAsync: vi.fn().mockRejectedValue(new Error('Unexpected error')),
    } as any;

    mockRequest.body = { message: 'test' };

    const middleware = validate(schema, 'body');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockNext).not.toHaveBeenCalled();
    expect(mockResponse.status).toHaveBeenCalledWith(500);
    expect(mockResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        error: 'Internal server error',
      })
    );
  });

  it('should include validation details in error response', async () => {
    const schema = z.object({
      message: z.string().min(5, 'Message must be at least 5 characters'),
      sessionId: z.string().min(1, 'Session ID is required'),
    });

    mockRequest.body = {
      message: 'hi',
      sessionId: '',
    };

    const middleware = validate(schema, 'body');
    await middleware(mockRequest as Request, mockResponse as Response, mockNext);

    expect(mockResponse.json).toHaveBeenCalledWith(
      expect.objectContaining({
        error: 'Validation failed',
        details: expect.arrayContaining([
          expect.objectContaining({
            path: expect.any(String),
            message: expect.any(String),
          }),
        ]),
      })
    );
  });
});

