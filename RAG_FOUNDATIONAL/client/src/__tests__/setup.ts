import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';

// Only run client-specific setup if we're in a jsdom environment
if (typeof window !== 'undefined') {
  // Cleanup after each test
  afterEach(() => {
    cleanup();
  });

  // Mock window.matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });

  // Mock scrollIntoView
  Element.prototype.scrollIntoView = vi.fn();

  // Mock ScrollArea scrollTo method
  const mockScrollTo = vi.fn();
  HTMLDivElement.prototype.scrollTo = mockScrollTo;

  // Mock IntersectionObserver
  global.IntersectionObserver = class IntersectionObserver {
    constructor() {}
    disconnect() {}
    observe() {}
    takeRecords() {
      return [];
    }
    unobserve() {}
  } as any;
} else {
  // Server-side cleanup only
  afterEach(() => {
    cleanup();
  });
}

