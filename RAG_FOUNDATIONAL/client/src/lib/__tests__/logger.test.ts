import { describe, it, expect, vi, beforeEach } from 'vitest';
import { clientLogger } from '../logger';
import log from 'loglevel';

// Mock loglevel
vi.mock('loglevel', () => ({
  default: {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    setLevel: vi.fn(),
  },
}));

describe('clientLogger', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('debug', () => {
    it('should log debug messages', () => {
      clientLogger.debug('Test debug message');
      expect(log.debug).toHaveBeenCalledWith('Test debug message');
    });

    it('should log debug messages with data', () => {
      const data = { key: 'value' };
      clientLogger.debug('Test debug', data);
      expect(log.debug).toHaveBeenCalledWith('Test debug', data);
    });
  });

  describe('info', () => {
    it('should log info messages', () => {
      clientLogger.info('Test info message');
      expect(log.info).toHaveBeenCalledWith('Test info message');
    });

    it('should log info messages with data', () => {
      const data = { key: 'value' };
      clientLogger.info('Test info', data);
      expect(log.info).toHaveBeenCalledWith('Test info', data);
    });
  });

  describe('warn', () => {
    it('should log warn messages', () => {
      clientLogger.warn('Test warn message');
      expect(log.warn).toHaveBeenCalledWith('Test warn message');
    });

    it('should log warn messages with data', () => {
      const data = { key: 'value' };
      clientLogger.warn('Test warn', data);
      expect(log.warn).toHaveBeenCalledWith('Test warn', data);
    });
  });

  describe('error', () => {
    it('should log error messages', () => {
      clientLogger.error('Test error message');
      expect(log.error).toHaveBeenCalledWith('Test error message');
    });

    it('should log error messages with data', () => {
      const data = { key: 'value' };
      clientLogger.error('Test error', data);
      expect(log.error).toHaveBeenCalledWith('Test error', data);
    });
  });
});

