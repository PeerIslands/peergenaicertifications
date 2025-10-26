// Mock axios globally
jest.mock('axios', () => ({
  create: jest.fn(() => ({
    post: jest.fn(),
    get: jest.fn(),
  })),
  post: jest.fn(),
  get: jest.fn(),
}));
