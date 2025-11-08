import { describe, it, expect } from 'vitest';
import { isUnauthorizedError } from '../authUtils';

describe('authUtils', () => {
  describe('isUnauthorizedError', () => {
    it('should return true for 401 Unauthorized error message', () => {
      const error = new Error('401: Unauthorized');
      expect(isUnauthorizedError(error)).toBe(true);
    });

    it('should return true for 401 error with additional text', () => {
      const error = new Error('401: Unauthorized - Please login');
      expect(isUnauthorizedError(error)).toBe(true);
    });

    it('should return false for non-401 errors', () => {
      const error = new Error('404: Not Found');
      expect(isUnauthorizedError(error)).toBe(false);
    });

    it('should return false for errors without status code', () => {
      const error = new Error('Something went wrong');
      expect(isUnauthorizedError(error)).toBe(false);
    });

    it('should return false for empty error message', () => {
      const error = new Error('');
      expect(isUnauthorizedError(error)).toBe(false);
    });
  });
});

