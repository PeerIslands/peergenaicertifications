import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@/tests/test-utils';
import { FileUpload } from './file-upload';

describe('FileUpload', () => {
  it('renders upload button', () => {
    render(<FileUpload onUpload={vi.fn()} />);
    expect(screen.getByText(/upload/i)).toBeInTheDocument();
  });

  it('accepts file input', () => {
    const handleUpload = vi.fn();
    render(<FileUpload onUpload={handleUpload} />);
    
    const input = screen.getByLabelText(/upload/i);
    expect(input).toHaveAttribute('type', 'file');
    expect(input).toHaveAttribute('accept', '.pdf');
  });

  it('calls onUpload with selected file', () => {
    const handleUpload = vi.fn();
    render(<FileUpload onUpload={handleUpload} />);
    
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByLabelText(/upload/i) as HTMLInputElement;
    
    fireEvent.change(input, { target: { files: [file] } });
    
    expect(handleUpload).toHaveBeenCalledWith(file);
  });

  it('only accepts PDF files', () => {
    render(<FileUpload onUpload={vi.fn()} />);
    const input = screen.getByLabelText(/upload/i);
    expect(input).toHaveAttribute('accept', '.pdf');
  });
});

