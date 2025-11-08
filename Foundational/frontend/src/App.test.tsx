import { describe, it, expect } from 'vitest';
import { render, screen } from '@/tests/test-utils';
import App from './App';

describe('App', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(document.body).toBeInTheDocument();
  });

  it('renders main application container', () => {
    const { container } = render(<App />);
    expect(container.firstChild).toBeInTheDocument();
  });
});

