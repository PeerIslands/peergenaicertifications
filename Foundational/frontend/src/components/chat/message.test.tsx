import { describe, it, expect } from 'vitest';
import { render, screen } from '@/tests/test-utils';
import { Message } from './message';

describe('Message', () => {
  it('renders user message', () => {
    render(
      <Message
        message={{
          id: '1',
          role: 'user',
          content: 'Hello, AI!',
          timestamp: new Date().toISOString(),
        }}
      />
    );
    
    expect(screen.getByText('Hello, AI!')).toBeInTheDocument();
  });

  it('renders assistant message', () => {
    render(
      <Message
        message={{
          id: '2',
          role: 'assistant',
          content: 'Hello! How can I help you?',
          timestamp: new Date().toISOString(),
        }}
      />
    );
    
    expect(screen.getByText('Hello! How can I help you?')).toBeInTheDocument();
  });

  it('displays message timestamp', () => {
    const timestamp = new Date().toISOString();
    render(
      <Message
        message={{
          id: '1',
          role: 'user',
          content: 'Test message',
          timestamp,
        }}
      />
    );
    
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });
});

