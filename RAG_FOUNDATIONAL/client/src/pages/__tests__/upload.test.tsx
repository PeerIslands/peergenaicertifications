import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/__tests__/test-utils';
import userEvent from '@testing-library/user-event';
import Upload from '../upload';
import { api } from '@/lib/api';

vi.mock('@/lib/api');
vi.mock('@/lib/logger', () => ({
  clientLogger: {
    error: vi.fn(),
  },
}));
vi.mock('wouter', () => ({
  useLocation: () => ['/upload'],
  Link: ({ children, href }: any) => <a href={href}>{children}</a>,
}));
vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQueryClient: () => ({
      invalidateQueries: vi.fn(),
    }),
  };
});

describe('Upload', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render upload page with title', () => {
    render(<Upload />);
    
    expect(screen.getByTestId('text-page-title')).toBeInTheDocument();
    expect(screen.getByText('Upload Documents')).toBeInTheDocument();
  });

  it('should render upload zone', () => {
    render(<Upload />);
    
    expect(screen.getByTestId('upload-zone')).toBeInTheDocument();
  });

  it('should display features section', () => {
    render(<Upload />);
    
    expect(screen.getByText('How it works')).toBeInTheDocument();
    expect(screen.getByText('PDF Processing')).toBeInTheDocument();
    expect(screen.getByText('AI-Powered')).toBeInTheDocument();
    expect(screen.getByText('Smart Search')).toBeInTheDocument();
    expect(screen.getByText('Secure Storage')).toBeInTheDocument();
  });

  it('should display upload guidelines', () => {
    render(<Upload />);
    
    expect(screen.getByText('Upload Guidelines')).toBeInTheDocument();
    expect(screen.getByText(/PDF files only/i)).toBeInTheDocument();
    expect(screen.getByText(/Text-based PDFs work best/i)).toBeInTheDocument();
  });

  it('should handle file upload', async () => {
    const user = userEvent.setup();
    const mockPdf = {
      id: '1',
      originalName: 'test.pdf',
      fileSize: 1000,
      uploadedAt: new Date(),
      processedAt: new Date(),
      pageCount: 5,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    (api.pdfs.upload as any).mockResolvedValueOnce(mockPdf);
    
    render(<Upload />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    await waitFor(() => {
      expect(api.pdfs.upload).toHaveBeenCalledWith(file);
    });
  });

  it('should display recently uploaded files', async () => {
    const user = userEvent.setup();
    const mockPdf = {
      id: '1',
      originalName: 'test.pdf',
      fileSize: 1000,
      uploadedAt: new Date(),
      processedAt: new Date(),
      pageCount: 5,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    (api.pdfs.upload as any).mockResolvedValueOnce(mockPdf);
    
    render(<Upload />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    await waitFor(() => {
      expect(screen.getByText('Recently Uploaded')).toBeInTheDocument();
      const testPdfElements = screen.getAllByText('test.pdf');
      expect(testPdfElements.length).toBeGreaterThan(0);
    });
  });

  it('should show view dashboard button after upload', async () => {
    const user = userEvent.setup();
    const mockPdf = {
      id: '1',
      originalName: 'test.pdf',
      fileSize: 1000,
      uploadedAt: new Date(),
      processedAt: new Date(),
      pageCount: 5,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    (api.pdfs.upload as any).mockResolvedValueOnce(mockPdf);
    
    render(<Upload />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    await waitFor(() => {
      const viewDashboardButton = screen.getByTestId('button-view-dashboard');
      expect(viewDashboardButton).toBeInTheDocument();
    });
  });

  it('should handle upload errors gracefully', async () => {
    const user = userEvent.setup();
    const error = new Error('Upload failed');
    
    (api.pdfs.upload as any).mockRejectedValueOnce(error);
    
    render(<Upload />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    await waitFor(() => {
      expect(api.pdfs.upload).toHaveBeenCalledWith(file);
    });
  });

  it('should show max upload size in guidelines', () => {
    render(<Upload />);
    
    // Default max upload is 50MB from env or code
    expect(screen.getByText(/up to 50MB each/i)).toBeInTheDocument();
  });

  it('should handle multiple file uploads', async () => {
    const user = userEvent.setup();
    const mockPdf1 = {
      id: '1',
      originalName: 'test1.pdf',
      fileSize: 1000,
      uploadedAt: new Date(),
      processedAt: new Date(),
      pageCount: 5,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    const mockPdf2 = {
      id: '2',
      originalName: 'test2.pdf',
      fileSize: 2000,
      uploadedAt: new Date(),
      processedAt: new Date(),
      pageCount: 10,
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    
    (api.pdfs.upload as any)
      .mockResolvedValueOnce(mockPdf1)
      .mockResolvedValueOnce(mockPdf2);
    
    render(<Upload />);
    
    const file1 = new File(['test1'], 'test1.pdf', { type: 'application/pdf' });
    const file2 = new File(['test2'], 'test2.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, [file1, file2]);
    
    await waitFor(() => {
      expect(api.pdfs.upload).toHaveBeenCalledTimes(2);
    });
  });
});

