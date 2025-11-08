import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/__tests__/test-utils';
import { PdfCard } from '../pdf-card';
import type { Pdf } from '@shared/schema';

const mockPdf: Pdf = {
  id: '1',
  originalName: 'test-document.pdf',
  fileSize: 1024000, // 1MB
  uploadedAt: new Date('2024-01-15'),
  processedAt: new Date('2024-01-15'),
  pageCount: 10,
  createdAt: new Date('2024-01-15'),
  updatedAt: new Date('2024-01-15'),
};

describe('PdfCard', () => {
  it('should render PDF card with basic information', () => {
    render(<PdfCard pdf={mockPdf} />);
    
    expect(screen.getByTestId('pdf-card-1')).toBeInTheDocument();
    expect(screen.getByText('test-document.pdf')).toBeInTheDocument();
    // File size should be displayed (format may vary)
    expect(screen.getByText(/KB|MB|Bytes/i)).toBeInTheDocument();
    expect(screen.getByText('Processed')).toBeInTheDocument();
  });

  it('should format file size correctly', () => {
    const smallPdf = { ...mockPdf, fileSize: 512 }; // 512 bytes
    render(<PdfCard pdf={smallPdf} />);
    
    expect(screen.getByText(/512 Bytes/i)).toBeInTheDocument();
  });

  it('should format date correctly', () => {
    render(<PdfCard pdf={mockPdf} />);
    
    expect(screen.getByText(/Jan 15, 2024/i)).toBeInTheDocument();
  });

  it('should show "Processing" badge when not processed', () => {
    const unprocessedPdf = { ...mockPdf, processedAt: null };
    render(<PdfCard pdf={unprocessedPdf} />);
    
    expect(screen.getByText('Processing')).toBeInTheDocument();
  });

  it('should call onDelete when delete button is clicked', () => {
    const onDelete = vi.fn();
    render(<PdfCard pdf={mockPdf} onDelete={onDelete} />);
    
    const deleteButton = screen.getByTestId('button-delete-1');
    deleteButton.click();
    
    expect(onDelete).toHaveBeenCalledWith('1');
  });

  it('should call onDownload when download button is clicked', () => {
    const onDownload = vi.fn();
    render(<PdfCard pdf={mockPdf} onDownload={onDownload} />);
    
    const downloadButton = screen.getByTestId('button-download-1');
    downloadButton.click();
    
    expect(onDownload).toHaveBeenCalledWith('1');
  });

  it('should not call callbacks when they are not provided', () => {
    render(<PdfCard pdf={mockPdf} />);
    
    const deleteButton = screen.getByTestId('button-delete-1');
    const downloadButton = screen.getByTestId('button-download-1');
    
    expect(() => {
      deleteButton.click();
      downloadButton.click();
    }).not.toThrow();
  });

  it('should handle missing pageCount gracefully', () => {
    const pdfWithoutPages = { ...mockPdf, pageCount: null };
    render(<PdfCard pdf={pdfWithoutPages} />);
    
    expect(screen.getByTestId('pdf-card-1')).toBeInTheDocument();
  });

  it('should handle missing uploadedAt date', () => {
    const pdfWithoutDate = { ...mockPdf, uploadedAt: null };
    render(<PdfCard pdf={pdfWithoutDate} />);
    
    // Should show "Unknown" for missing date
    expect(screen.getByText(/Unknown|Uploaded/i)).toBeInTheDocument();
  });

  it('should truncate long file names', () => {
    const longNamePdf = {
      ...mockPdf,
      originalName: 'very-long-document-name-that-should-be-truncated.pdf',
    };
    render(<PdfCard pdf={longNamePdf} />);
    
    const fileNameElement = screen.getByText(longNamePdf.originalName);
    expect(fileNameElement).toHaveClass('truncate');
  });
});

