import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatInput from '../components/ChatInput';

// Mock the API service
jest.mock('../services/api', () => ({
  sendMessage: jest.fn().mockResolvedValue({
    response: 'Test response',
    sources: ['test.pdf'],
    session_id: 'test-session-id'
  }),
}));

describe('ChatInput Component', () => {
  const mockProps = {
    onNewMessage: jest.fn(),
    sessionId: 'test-session-id',
    setSessionId: jest.fn(),
    setIsLoading: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders input field and send button', () => {
    render(<ChatInput {...mockProps} />);
    
    expect(screen.getByPlaceholderText('Ask a question about the loaded documents...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send' })).toBeInTheDocument();
  });

  it('updates input value when typing', () => {
    render(<ChatInput {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Ask a question about the loaded documents...');
    fireEvent.change(input, { target: { value: 'Test question' } });
    
    expect(input).toHaveValue('Test question');
  });

  it('disables send button when input is empty', () => {
    render(<ChatInput {...mockProps} />);
    
    const sendButton = screen.getByRole('button', { name: 'Send' });
    expect(sendButton).toBeDisabled();
  });

  it('enables send button when input has text', () => {
    render(<ChatInput {...mockProps} />);
    
    const input = screen.getByPlaceholderText('Ask a question about the loaded documents...');
    const sendButton = screen.getByRole('button', { name: 'Send' });
    
    fireEvent.change(input, { target: { value: 'Test question' } });
    
    expect(sendButton).not.toBeDisabled();
  });
});