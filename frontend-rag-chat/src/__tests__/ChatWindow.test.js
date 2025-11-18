import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ChatWindow from '../components/ChatWindow';

// Mock scrollIntoView for JSDOM
beforeAll(() => {
  Element.prototype.scrollIntoView = jest.fn();
});

describe('ChatWindow Component', () => {
  const mockMessages = [
    {
      sender: 'user',
      text: 'Hello, how are you?',
      timestamp: '2024-01-01T00:00:00Z'
    },
    {
      sender: 'ai',
      text: 'I am doing well, thank you!',
      sources: ['document1.pdf', 'document2.pdf'],
      timestamp: '2024-01-01T00:00:01Z'
    }
  ];

  it('renders messages correctly', () => {
    render(<ChatWindow messages={mockMessages} isLoading={false} />);
    
    expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
    expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument();
  });

  it('displays sources when available', () => {
    render(<ChatWindow messages={mockMessages} isLoading={false} />);
    
    expect(screen.getByText('Sources:')).toBeInTheDocument();
    expect(screen.getByText('document1.pdf')).toBeInTheDocument();
    expect(screen.getByText('document2.pdf')).toBeInTheDocument();
  });

  it('shows loading message when no messages and not loading', () => {
    render(<ChatWindow messages={[]} isLoading={false} />);
    
    expect(screen.getByText('Start a conversation by asking a question about the loaded documents.')).toBeInTheDocument();
    expect(screen.getByText('Documents are automatically loaded from the files directory.')).toBeInTheDocument();
  });

  it('shows loading animation when loading', () => {
    render(<ChatWindow messages={[]} isLoading={true} />);
    
    expect(screen.getByText('AI is thinking...')).toBeInTheDocument();
  });
});