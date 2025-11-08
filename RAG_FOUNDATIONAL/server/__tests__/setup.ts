import { vi } from 'vitest';

// Mock OpenAI to prevent browser environment errors in server tests
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

