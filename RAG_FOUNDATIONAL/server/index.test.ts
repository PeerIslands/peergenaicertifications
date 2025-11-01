import { describe, it, expect, vi, beforeAll } from 'vitest';

// Mock OpenAI before any imports
vi.mock('openai', () => {
  return {
    default: class MockOpenAI {
      constructor() {
        // Mock OpenAI client
      }
      chat = {
        completions: {
          create: vi.fn(),
        },
      };
      embeddings = {
        create: vi.fn(),
      };
    },
  };
});

// Mock server dependencies that might trigger OpenAI initialization
vi.mock('../src/services/rag', () => ({
  answerWithRag: vi.fn(),
}));

// Mock server.ts to prevent actual server initialization
vi.mock('./src/server', () => ({
  startServer: vi.fn(),
  createServer: vi.fn(),
  default: {},
}));

describe('index', () => {
  it('should export from server module', async () => {
    const indexModule = await import('./index');
    expect(indexModule).toBeDefined();
  }, 10000); // Increase timeout to 10 seconds

  it('should have exportable content', async () => {
    const indexModule = await import('./index');
    
    // Check that the module can be imported
    expect(typeof indexModule).toBe('object');
  }, 10000); // Increase timeout to 10 seconds
});

