import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@/tests/test-utils';
import { MessageInput } from './message-input';

describe('MessageInput', () => {
  it('renders input field', () => {
    render(<MessageInput onSend={vi.fn()} disabled={false} />);
    expect(screen.getByPlaceholderText(/type.*message/i)).toBeInTheDocument();
  });

  it('calls onSend with message text', () => {
    const handleSend = vi.fn();
    render(<MessageInput onSend={handleSend} disabled={false} />);
    
    const input = screen.getByPlaceholderText(/type.*message/i);
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);
    
    expect(handleSend).toHaveBeenCalledWith('Test message');
  });

  it('clears input after sending', () => {
    const handleSend = vi.fn();
    render(<MessageInput onSend={handleSend} disabled={false} />);
    
    const input = screen.getByPlaceholderText(/type.*message/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'Test message' } });
    
    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);
    
    expect(input.value).toBe('');
  });

  it('disables input when disabled prop is true', () => {
    render(<MessageInput onSend={vi.fn()} disabled={true} />);
    const input = screen.getByPlaceholderText(/type.*message/i);
    expect(input).toBeDisabled();
  });

  it('does not send empty messages', () => {
    const handleSend = vi.fn();
    render(<MessageInput onSend={handleSend} disabled={false} />);
    
    const sendButton = screen.getByRole('button');
    fireEvent.click(sendButton);
    
    expect(handleSend).not.toHaveBeenCalled();
  });
});

