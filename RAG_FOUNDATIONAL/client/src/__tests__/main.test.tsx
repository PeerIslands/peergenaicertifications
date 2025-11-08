import { describe, it, expect, vi, beforeEach } from 'vitest';
import { createRoot } from 'react-dom/client';
import App from '../App';

// Mock react-dom/client
vi.mock('react-dom/client', () => ({
  createRoot: vi.fn(() => ({
    render: vi.fn(),
  })),
}));

// Mock App component
vi.mock('../App', () => ({
  default: vi.fn(() => <div>Mock App</div>),
}));

// Mock index.css import
vi.mock('../index.css', () => ({}));

describe('main.tsx', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup document.getElementById mock
    document.getElementById = vi.fn(() => {
      const mockDiv = document.createElement('div');
      mockDiv.id = 'root';
      return mockDiv;
    }) as any;
  });

  it('should render App to root element', async () => {
    const mockRoot = {
      render: vi.fn(),
    };
    vi.mocked(createRoot).mockReturnValueOnce(mockRoot as any);
    
    document.getElementById = vi.fn(() => {
      const mockDiv = document.createElement('div');
      mockDiv.id = 'root';
      return mockDiv;
    }) as any;

    // Import main.tsx which will execute the render code
    await import('../main');
    
    expect(document.getElementById).toHaveBeenCalledWith('root');
    expect(createRoot).toHaveBeenCalled();
    expect(mockRoot.render).toHaveBeenCalledWith(expect.anything());
  });
});

