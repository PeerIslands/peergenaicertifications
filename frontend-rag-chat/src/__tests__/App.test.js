import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../App';

// Mock the API service
jest.mock('../services/api', () => ({
  getStatus: jest.fn().mockResolvedValue({
    total_documents: 2,
    total_chunks: 10,
    status: 'ready'
  }),
}));

describe('App Component', () => {
  it('renders app header correctly', () => {
    render(<App />);
    
    expect(screen.getByText('RAG Chat App')).toBeInTheDocument();
    expect(screen.getByText('Chat with pre-loaded PDF documents using AI')).toBeInTheDocument();
  });

  it('shows spinner during loading', () => {
    render(<App />);
    
    const spinner = document.querySelector('.spinner');
    expect(spinner).toBeInTheDocument();
  });
});