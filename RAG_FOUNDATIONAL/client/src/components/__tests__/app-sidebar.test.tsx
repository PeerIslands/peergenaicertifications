import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/__tests__/test-utils';
import { AppSidebar } from '../app-sidebar';
import { SidebarProvider } from '@/components/ui/sidebar';

// Mock wouter's useLocation
vi.mock('wouter', () => ({
  useLocation: () => ['/'],
  Link: ({ children, href }: any) => <a href={href}>{children}</a>,
}));

const createWrapper = () => {
  return ({ children }: { children: React.ReactNode }) => (
    <SidebarProvider>{children}</SidebarProvider>
  );
};

describe('AppSidebar', () => {
  it('should render sidebar with header', () => {
    render(<AppSidebar />, { wrapper: createWrapper() });
    
    expect(screen.getByTestId('sidebar-main')).toBeInTheDocument();
    expect(screen.getByText('RAG')).toBeInTheDocument();
  });

  it('should render navigation menu items', () => {
    render(<AppSidebar />, { wrapper: createWrapper() });
    
    // The test-id format uses lowercase and replaces space with dash, but "Upload PDF" becomes "nav-upload pdf"
    // Let's use text content instead for more reliable testing
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Upload PDF')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
  });

  it('should have correct navigation links', () => {
    render(<AppSidebar />, { wrapper: createWrapper() });
    
    const dashboardLink = screen.getByRole('link', { name: /dashboard/i });
    const uploadLink = screen.getByRole('link', { name: /upload pdf/i });
    const chatLink = screen.getByRole('link', { name: /chat/i });
    
    expect(dashboardLink).toHaveAttribute('href', '/');
    expect(uploadLink).toHaveAttribute('href', '/upload');
    expect(chatLink).toHaveAttribute('href', '/chat');
  });

  it('should show navigation labels', () => {
    render(<AppSidebar />, { wrapper: createWrapper() });
    
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Upload PDF')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Navigation')).toBeInTheDocument();
  });
});

