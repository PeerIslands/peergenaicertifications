import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { toast, useToast, reducer } from '../use-toast';
import type { State } from '../use-toast';

describe('useToast', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('toast function', () => {
    it('should create a new toast', () => {
    const result = toast({
      title: 'Test Toast',
      description: 'Test description',
    });

    expect(result.id).toBeDefined();
    expect(result.dismiss).toBeDefined();
    expect(result.update).toBeDefined();
  });

  it('should create toast with default open state', () => {
    const result = toast({ title: 'Test' });
    expect(result.id).toBeTruthy();
  });

  it('should allow dismissing a toast', () => {
    const result = toast({ title: 'Test' });
    expect(() => result.dismiss()).not.toThrow();
  });

  it('should allow updating a toast', () => {
    const result = toast({ title: 'Test' });
    expect(() => result.update({ title: 'Updated' })).not.toThrow();
  });
});

  describe('reducer', () => {
    it('should add a toast', () => {
      const state: State = { toasts: [] };
      const action = {
        type: 'ADD_TOAST' as const,
        toast: {
          id: '1',
          title: 'Test',
          open: true,
        },
      };

      const newState = reducer(state, action);
      expect(newState.toasts).toHaveLength(1);
      expect(newState.toasts[0].id).toBe('1');
    });

    it('should update a toast', () => {
      const state: State = {
        toasts: [{ id: '1', title: 'Test', open: true }],
      };
      const action = {
        type: 'UPDATE_TOAST' as const,
        toast: { id: '1', title: 'Updated' },
      };

      const newState = reducer(state, action);
      expect(newState.toasts[0].title).toBe('Updated');
    });

    it('should dismiss a toast', () => {
      const state: State = {
        toasts: [{ id: '1', title: 'Test', open: true }],
      };
      const action = {
        type: 'DISMISS_TOAST' as const,
        toastId: '1',
      };

      const newState = reducer(state, action);
      expect(newState.toasts[0].open).toBe(false);
    });

    it('should remove a toast', () => {
      const state: State = {
        toasts: [
          { id: '1', title: 'Test', open: true },
          { id: '2', title: 'Test 2', open: true },
        ],
      };
      const action = {
        type: 'REMOVE_TOAST' as const,
        toastId: '1',
      };

      const newState = reducer(state, action);
      expect(newState.toasts).toHaveLength(1);
      expect(newState.toasts[0].id).toBe('2');
    });

    it('should remove all toasts when toastId is undefined', () => {
      const state: State = {
        toasts: [
          { id: '1', title: 'Test', open: true },
          { id: '2', title: 'Test 2', open: true },
        ],
      };
      const action = {
        type: 'REMOVE_TOAST' as const,
        toastId: undefined,
      };

      const newState = reducer(state, action);
      expect(newState.toasts).toHaveLength(0);
    });
  });
});

