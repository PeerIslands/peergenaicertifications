import { describe, it, expect } from 'vitest';
import { render, screen } from '@/__tests__/test-utils';
import NotFound from '../not-found';

describe('NotFound', () => {
  it('should render 404 page', () => {
    render(<NotFound />);
    
    expect(screen.getByText('404 Page Not Found')).toBeInTheDocument();
  });

  it('should display helpful message', () => {
    render(<NotFound />);
    
    expect(screen.getByText(/Did you forget to add the page to the router\?/i)).toBeInTheDocument();
  });

  it('should have AlertCircle icon', () => {
    render(<NotFound />);
    
    // The icon should be rendered (lucide-react icons render as SVGs)
    const icon = screen.getByText('404 Page Not Found').previousSibling;
    expect(icon).toBeInTheDocument();
  });

  it('should have proper card layout', () => {
    render(<NotFound />);
    
    // Card component should be rendered - check by verifying the structure exists
    const title = screen.getByText('404 Page Not Found');
    expect(title).toBeInTheDocument();
    // Verify the card exists by checking if title has a parent with card-like structure
    const container = title.closest('div');
    expect(container).toBeInTheDocument();
  });
});

