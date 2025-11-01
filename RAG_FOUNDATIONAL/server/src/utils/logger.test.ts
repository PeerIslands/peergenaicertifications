import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { logger } from './logger';

describe('logger', () => {
  const originalEnv = process.env.NODE_ENV;
  const originalLogLevel = process.env.LOG_LEVEL;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    process.env.NODE_ENV = originalEnv;
    process.env.LOG_LEVEL = originalLogLevel;
  });

  it('should create a logger instance', () => {
    expect(logger).toBeDefined();
    expect(typeof logger.info).toBe('function');
    expect(typeof logger.error).toBe('function');
    expect(typeof logger.warn).toBe('function');
    expect(typeof logger.debug).toBe('function');
  });

  it('should log info messages', () => {
    const spy = vi.spyOn(logger, 'info');
    logger.info({ test: 'data' }, 'test message');
    expect(spy).toHaveBeenCalledWith({ test: 'data' }, 'test message');
  });

  it('should log error messages', () => {
    const spy = vi.spyOn(logger, 'error');
    logger.error({ err: new Error('test') }, 'error message');
    expect(spy).toHaveBeenCalledWith({ err: new Error('test') }, 'error message');
  });

  it('should log debug messages', () => {
    const spy = vi.spyOn(logger, 'debug');
    logger.debug({ debug: 'data' }, 'debug message');
    expect(spy).toHaveBeenCalledWith({ debug: 'data' }, 'debug message');
  });

  it('should log warn messages', () => {
    const spy = vi.spyOn(logger, 'warn');
    logger.warn({ warn: 'data' }, 'warn message');
    expect(spy).toHaveBeenCalledWith({ warn: 'data' }, 'warn message');
  });
});

