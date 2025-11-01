import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useIsMobile } from '../use-mobile';

describe('useIsMobile', () => {
  let originalInnerWidth: number;
  let matchMediaMock: any;

  beforeEach(() => {
    originalInnerWidth = window.innerWidth;
    matchMediaMock = vi.fn((query: string) => ({
      matches: query.includes('max-width: 767px') && window.innerWidth < 768,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));
    window.matchMedia = matchMediaMock;
  });

  afterEach(() => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  it('should return true when window width is less than 768px', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 600,
    });

    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(true);
  });

  it('should return false when window width is greater than or equal to 768px', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });

    const { result } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);
  });

  it('should update when window is resized', async () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 1024,
    });

    // Update matchMedia mock to reflect current width
    matchMediaMock.mockImplementation((query: string) => ({
      matches: query.includes('max-width: 767px') && window.innerWidth < 768,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn((event: string, handler: () => void) => {
        // Store handler to call later
        if (event === 'change') {
          (matchMediaMock as any)._handlers = (matchMediaMock as any)._handlers || [];
          (matchMediaMock as any)._handlers.push(handler);
        }
      }),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    const { result, rerender } = renderHook(() => useIsMobile());
    expect(result.current).toBe(false);

    // Change window width
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 600,
    });

    // Update matchMedia to return new matches value
    matchMediaMock.mockImplementation((query: string) => ({
      matches: query.includes('max-width: 767px') && 600 < 768,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }));

    // Trigger change event on matchMedia
    const handlers = (matchMediaMock as any)._handlers || [];
    handlers.forEach((handler: () => void) => handler());

    rerender();
    
    // Wait a bit for state to update
    await new Promise(resolve => setTimeout(resolve, 50));
    
    // The hook should now return true for mobile
    expect(result.current).toBe(true);
  });

  it('should clean up event listener on unmount', () => {
    let removeListenerCalled = false;
    
    matchMediaMock.mockImplementation((query: string) => ({
      matches: query.includes('max-width: 767px') && window.innerWidth < 768,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(() => {
        removeListenerCalled = true;
      }),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(() => {
        removeListenerCalled = true;
      }),
      dispatchEvent: vi.fn(),
    }));
    
    const { unmount } = renderHook(() => useIsMobile());

    unmount();
    
    // The hook should call removeEventListener on the matchMedia object
    expect(removeListenerCalled).toBe(true);
  });
});

