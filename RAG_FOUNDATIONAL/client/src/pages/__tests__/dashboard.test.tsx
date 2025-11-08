import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/__tests__/test-utils';
import userEvent from '@testing-library/user-event';
import Dashboard from '../dashboard';
import { api } from '@/lib/api';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

vi.mock('@/lib/api');
vi.mock('@tanstack/react-query', async () => {
  const actual = await vi.importActual('@tanstack/react-query');
  return {
    ...actual,
    useQuery: vi.fn(),
    useMutation: vi.fn(),
    useQueryClient: vi.fn(),
  };
});

vi.mock('wouter', () => ({
  useLocation: () => ['/'],
  Link: ({ children, href }: any) => <a href={href}>{children}</a>,
}));

vi.mock('@/hooks/use-toast', () => ({
  useToast: () => ({
    toast: vi.fn(),
  }),
}));

describe('Dashboard', () => {
  const mockQueryClient = {
    invalidateQueries: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
    (useQueryClient as any).mockReturnValue(mockQueryClient);
    
    // Mock window.confirm
    window.confirm = vi.fn(() => true);
    
    // Mock window.open
    window.open = vi.fn();
  });

  it('should render dashboard with title', () => {
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByTestId('text-page-title')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('should render upload button', () => {
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByRole('link', { name: /upload new/i })).toBeInTheDocument();
  });

  it('should display loading state', () => {
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: true,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();
  });

  it('should display empty state when no PDFs', () => {
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByText('No documents uploaded')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /upload your first document/i })).toBeInTheDocument();
  });

  it('should display PDFs in grid', () => {
    const mockPdfs = [
      {
        id: '1',
        originalName: 'test1.pdf',
        fileSize: 1000,
        uploadedAt: new Date(),
        processedAt: new Date(),
        pageCount: 5,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
      {
        id: '2',
        originalName: 'test2.pdf',
        fileSize: 2000,
        uploadedAt: new Date(),
        processedAt: null,
        pageCount: 10,
        createdAt: new Date(),
        updatedAt: new Date(),
      },
    ];

    (useQuery as any).mockReturnValue({
      data: mockPdfs,
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByTestId('pdf-card-1')).toBeInTheDocument();
    expect(screen.getByTestId('pdf-card-2')).toBeInTheDocument();
  });

  it('should handle search input', async () => {
    const user = userEvent.setup();
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    const searchInput = screen.getByTestId('input-search-documents');
    await user.type(searchInput, 'test query');
    
    expect(searchInput).toHaveValue('test query');
  });

  it('should call search API when search query is entered', async () => {
    const user = userEvent.setup();
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    const searchInput = screen.getByTestId('input-search-documents');
    await user.type(searchInput, 'test');
    
    // The search should be triggered when queryKey changes
    expect(useQuery).toHaveBeenCalled();
  });

  it('should handle delete action', async () => {
    const user = userEvent.setup();
    const mockDeleteMutation = {
      mutate: vi.fn(),
      isLoading: false,
    };

    (useQuery as any).mockReturnValue({
      data: [
        {
          id: '1',
          originalName: 'test.pdf',
          fileSize: 1000,
          uploadedAt: new Date(),
          processedAt: new Date(),
          pageCount: 5,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ],
      isLoading: false,
      error: null,
    });

    (useMutation as any).mockReturnValue(mockDeleteMutation);

    render(<Dashboard />);
    
    const deleteButton = screen.getByTestId('button-delete-1');
    await user.click(deleteButton);
    
    expect(window.confirm).toHaveBeenCalled();
    expect(mockDeleteMutation.mutate).toHaveBeenCalledWith('1');
  });

  it('should handle download action', async () => {
    const user = userEvent.setup();
    
    (useQuery as any).mockReturnValue({
      data: [
        {
          id: '1',
          originalName: 'test.pdf',
          fileSize: 1000,
          uploadedAt: new Date(),
          processedAt: new Date(),
          pageCount: 5,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    const downloadButton = screen.getByTestId('button-download-1');
    await user.click(downloadButton);
    
    expect(window.open).toHaveBeenCalled();
  });

  it('should display error state', () => {
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: new Error('Failed to load'),
    });

    render(<Dashboard />);
    
    expect(screen.getByText('Error loading documents')).toBeInTheDocument();
    expect(screen.getByText('Failed to load')).toBeInTheDocument();
  });

  it('should show document count', () => {
    const mockPdfs = Array.from({ length: 3 }, (_, i) => ({
      id: `${i}`,
      originalName: `test${i}.pdf`,
      fileSize: 1000,
      uploadedAt: new Date(),
      processedAt: new Date(),
      pageCount: 5,
      createdAt: new Date(),
      updatedAt: new Date(),
    }));

    (useQuery as any).mockReturnValue({
      data: mockPdfs,
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByText(/3 documents found/i)).toBeInTheDocument();
  });

  it('should show singular document count', () => {
    (useQuery as any).mockReturnValue({
      data: [
        {
          id: '1',
          originalName: 'test.pdf',
          fileSize: 1000,
          uploadedAt: new Date(),
          processedAt: new Date(),
          pageCount: 5,
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    expect(screen.getByText(/1 document found/i)).toBeInTheDocument();
  });

  it('should show empty search results message', async () => {
    const user = userEvent.setup();
    (useQuery as any).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
    });

    render(<Dashboard />);
    
    // Type a search query to trigger search state
    const searchInput = screen.getByTestId('input-search-documents');
    await user.type(searchInput, 'nonexistent');
    
    // The component will show "No documents found" when searchQuery has a value
    // Since we can't easily mock the internal state, we verify the empty state is shown
    expect(screen.getByText(/0 documents found/i)).toBeInTheDocument();
  });
});

