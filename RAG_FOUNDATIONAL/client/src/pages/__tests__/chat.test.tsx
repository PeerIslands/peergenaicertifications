import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/__tests__/test-utils';
import { fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chat from '../chat';
import { api } from '@/lib/api';

vi.mock('@/lib/api');
vi.mock('wouter', () => ({
  useLocation: () => ['/chat'],
  Link: ({ children, href }: any) => <a href={href}>{children}</a>,
}));

describe('Chat', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render chat interface', () => {
    render(<Chat />);
    
    expect(screen.getByText('Chat With Your Files')).toBeInTheDocument();
    expect(screen.getByText(/Ask a question about your uploaded PDFs/i)).toBeInTheDocument();
  });

  it('should allow sending a message', async () => {
    const user = userEvent.setup();
    const mockReply = {
      reply: 'Test reply',
      sources: [],
    };
    
    (api.rag.chat as any).mockResolvedValueOnce(mockReply);
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Hello, test message');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    await waitFor(() => {
      expect(api.rag.chat).toHaveBeenCalledWith([
        { role: 'user', content: 'Hello, test message' },
      ]);
    });
  });

  it('should display messages in the chat', async () => {
    const user = userEvent.setup();
    const mockReply = {
      reply: 'Test assistant reply',
      sources: [],
    };
    
    (api.rag.chat as any).mockResolvedValueOnce(mockReply);
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'User message');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    await waitFor(() => {
      expect(screen.getByText('User message')).toBeInTheDocument();
      expect(screen.getByText('Test assistant reply')).toBeInTheDocument();
    });
  });

  it('should show loading state while processing', async () => {
    const user = userEvent.setup();
    let resolveChat: any;
    const promise = new Promise((resolve) => {
      resolveChat = resolve;
    });
    
    (api.rag.chat as any).mockReturnValueOnce(promise);
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    await waitFor(() => {
      expect(screen.getByText('Thinking...')).toBeInTheDocument();
    });
    
    resolveChat({ reply: 'Done', sources: [] });
  });

  it('should display error message on failure', async () => {
    const user = userEvent.setup();
    (api.rag.chat as any).mockRejectedValueOnce(new Error('API Error'));
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    await waitFor(() => {
      expect(screen.getByText(/API Error/i)).toBeInTheDocument();
    });
  });

  it('should display sources when available', async () => {
    const user = userEvent.setup();
    const mockReply = {
      reply: 'Test reply',
      sources: [
        {
          pdfId: '1',
          originalName: 'test.pdf',
          preview: 'Preview text from the document',
        },
      ],
    };
    
    (api.rag.chat as any).mockResolvedValueOnce(mockReply);
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test query');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    // Wait for the reply to appear
    await waitFor(() => {
      expect(screen.getByText('Test reply')).toBeInTheDocument();
    }, { timeout: 3000 });
    
    // Sources should appear after the reply - they might be rendered with brackets
    await waitFor(() => {
      expect(screen.getByText('Sources')).toBeInTheDocument();
    }, { timeout: 3000 });
    
    // Verify source details - the originalName might be wrapped with [1] prefix
    await waitFor(() => {
      // Look for test.pdf which might be part of "[1] test.pdf" or just "test.pdf"
      const pdfText = screen.getByText(/test\.pdf/i);
      expect(pdfText).toBeInTheDocument();
      
      // Verify preview text
      expect(screen.getByText(/Preview text from the document/i)).toBeInTheDocument();
    }, { timeout: 3000 });
  }, 10000); // Increase test timeout to 10 seconds

  it('should clear input after sending message', async () => {
    const user = userEvent.setup();
    const mockReply = {
      reply: 'Test reply',
      sources: [],
    };
    
    (api.rag.chat as any).mockResolvedValueOnce(mockReply);
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox') as HTMLTextAreaElement;
    await user.type(input, 'Test message');
    
    expect(input.value).toBe('Test message');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });

  it('should not send empty messages', async () => {
    const user = userEvent.setup();
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, '   '); // Only whitespace
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    // Wait a bit to ensure API wasn't called
    await new Promise((resolve) => setTimeout(resolve, 100));
    
    expect(api.rag.chat).not.toHaveBeenCalled();
  });

  it('should provide download links for sources', async () => {
    const user = userEvent.setup();
    const mockReply = {
      reply: 'Test reply',
      sources: [
        {
          pdfId: 'pdf-123',
          originalName: 'test.pdf',
          preview: 'Preview',
        },
      ],
    };
    
    (api.rag.chat as any).mockResolvedValueOnce(mockReply);
    
    render(<Chat />);
    
    const input = screen.getByRole('textbox');
    await user.type(input, 'Test');
    
    const form = input.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    await waitFor(() => {
      const downloadLink = screen.getByText('Download');
      expect(downloadLink).toHaveAttribute('href', '/api/pdfs/pdf-123/download');
    });
  });
});

