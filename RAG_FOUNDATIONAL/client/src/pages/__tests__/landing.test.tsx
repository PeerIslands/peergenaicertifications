import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@/__tests__/test-utils';
import userEvent from '@testing-library/user-event';
import Landing from '../landing';

describe('Landing', () => {
  beforeEach(() => {
    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: {
        href: '',
      },
      writable: true,
    });
    
    // Mock scrollIntoView
    Element.prototype.scrollIntoView = vi.fn();
  });

  it('should render landing page with title', () => {
    render(<Landing />);
    
    expect(screen.getByText('RAG')).toBeInTheDocument();
    expect(screen.getByText(/AI-Powered PDF Search & Analysis/i)).toBeInTheDocument();
  });

  it('should render get started button', () => {
    render(<Landing />);
    
    const getStartedButton = screen.getByTestId('button-get-started');
    expect(getStartedButton).toBeInTheDocument();
    expect(getStartedButton).toHaveTextContent('Get Started with Google');
  });

  it('should render learn more button', () => {
    render(<Landing />);
    
    const learnMoreButton = screen.getByTestId('button-learn-more');
    expect(learnMoreButton).toBeInTheDocument();
    expect(learnMoreButton).toHaveTextContent('Learn More');
  });

  it('should redirect to login when get started is clicked', async () => {
    const user = userEvent.setup();
    render(<Landing />);
    
    const getStartedButton = screen.getByTestId('button-get-started');
    await user.click(getStartedButton);
    
    expect(window.location.href).toBe('/api/login');
  });

  it('should scroll to features when learn more is clicked', async () => {
    const user = userEvent.setup();
    const scrollIntoViewMock = vi.fn();
    document.getElementById = vi.fn(() => ({
      scrollIntoView: scrollIntoViewMock,
    } as any));

    render(<Landing />);
    
    const learnMoreButton = screen.getByTestId('button-learn-more');
    await user.click(learnMoreButton);
    
    expect(scrollIntoViewMock).toHaveBeenCalledWith({ behavior: 'smooth' });
  });

  it('should display all features', () => {
    render(<Landing />);
    
    expect(screen.getByText('Upload PDFs')).toBeInTheDocument();
    expect(screen.getByText('AI-Powered Search')).toBeInTheDocument();
    expect(screen.getByText('Chat with Documents')).toBeInTheDocument();
    expect(screen.getByText('Organized Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Fast Processing')).toBeInTheDocument();
    expect(screen.getByText('Secure Access')).toBeInTheDocument();
  });

  it('should display feature descriptions', () => {
    render(<Landing />);
    
    expect(screen.getByText(/Easily upload and organize your PDF documents/i)).toBeInTheDocument();
    expect(screen.getByText(/Find specific information across all your documents/i)).toBeInTheDocument();
    expect(screen.getByText(/Ask questions about your documents/i)).toBeInTheDocument();
  });

  it('should display how it works section', () => {
    render(<Landing />);
    
    expect(screen.getByText('How DocuRAG Works')).toBeInTheDocument();
    expect(screen.getByText('Upload Documents')).toBeInTheDocument();
    expect(screen.getByText('AI Processing')).toBeInTheDocument();
    expect(screen.getByText('Search & Chat')).toBeInTheDocument();
  });

  it('should display CTA section', () => {
    render(<Landing />);
    
    expect(screen.getByText('Ready to get started?')).toBeInTheDocument();
    const ctaButton = screen.getByTestId('button-sign-up-cta');
    expect(ctaButton).toBeInTheDocument();
    expect(ctaButton).toHaveTextContent('Sign Up with Google');
  });

  it('should redirect to login when CTA button is clicked', async () => {
    const user = userEvent.setup();
    render(<Landing />);
    
    const ctaButton = screen.getByTestId('button-sign-up-cta');
    await user.click(ctaButton);
    
    expect(window.location.href).toBe('/api/login');
  });

  it('should have features section with id', () => {
    render(<Landing />);
    
    const featuresSection = document.getElementById('features');
    expect(featuresSection).not.toBeNull();
    if (featuresSection) {
      expect(featuresSection).toBeTruthy();
    }
  });

  it('should display main description', () => {
    render(<Landing />);
    
    expect(screen.getByText(/Upload your PDF documents and unlock the power/i)).toBeInTheDocument();
  });
});

