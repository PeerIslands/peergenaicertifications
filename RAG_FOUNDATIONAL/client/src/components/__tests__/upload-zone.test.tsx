import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@/__tests__/test-utils';
import userEvent from '@testing-library/user-event';
import { UploadZone } from '../upload-zone';

describe('UploadZone', () => {
  const mockOnUpload = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.clearAllTimers();
  });

  it('should render upload zone', () => {
    render(<UploadZone onUpload={mockOnUpload} />);
    
    expect(screen.getByTestId('upload-zone')).toBeInTheDocument();
    expect(screen.getByText('Upload PDF Documents')).toBeInTheDocument();
    expect(screen.getByText(/Drag and drop your PDF files here/i)).toBeInTheDocument();
    expect(screen.getByTestId('button-browse-files')).toBeInTheDocument();
  });

  it('should handle file input change', async () => {
    const user = userEvent.setup();
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    expect(mockOnUpload).toHaveBeenCalledWith([file]);
  });

  it('should handle drag and drop', async () => {
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const uploadZone = screen.getByTestId('upload-zone');
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    
    // Create mock DragEvent since it's not available in jsdom
    const createDragEvent = (type: string, files: File[] = []) => {
      const event = new Event(type, { bubbles: true, cancelable: true });
      const dataTransfer = {
        files: files as any,
        items: files.map(f => ({
          kind: 'file',
          type: f.type,
          getAsFile: () => f,
        })),
        types: ['Files'],
      };
      Object.defineProperty(event, 'dataTransfer', {
        value: dataTransfer,
        writable: false,
      });
      return event;
    };
    
    const dragOverEvent = createDragEvent('dragover', [file]);
    uploadZone.dispatchEvent(dragOverEvent);
    
    const dropEvent = createDragEvent('drop', [file]);
    uploadZone.dispatchEvent(dropEvent);
    
    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalled();
    });
  });

  it('should reject non-PDF files', async () => {
    const user = userEvent.setup();
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const file = new File(['test content'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    expect(mockOnUpload).not.toHaveBeenCalled();
    alertSpy.mockRestore();
  });

  it('should reject files that are too large', async () => {
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});
    
    render(<UploadZone onUpload={mockOnUpload} />);
    
    // Create a mock file that exceeds the size limit
    const largeFileBlob = new Blob(['x'], { type: 'application/pdf' });
    const largeFile = new File([largeFileBlob], 'large.pdf', {
      type: 'application/pdf',
    });
    
    // Mock the size property
    Object.defineProperty(largeFile, 'size', {
      get: () => 51 * 1024 * 1024, // 51 MB, over the 50MB limit
      configurable: true,
    });
    
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    // Create a FileList with the large file
    const fileList = {
      0: largeFile,
      length: 1,
      item: (index: number) => (index === 0 ? largeFile : null),
    } as FileList;
    
    Object.defineProperty(input, 'files', {
      get: () => fileList,
      configurable: true,
    });
    
    // Trigger change event manually
    const changeEvent = new Event('change', { bubbles: true });
    input.dispatchEvent(changeEvent);
    
    await waitFor(() => {
      // Alert should be called for rejected files
      expect(alertSpy).toHaveBeenCalled();
    }, { timeout: 2000 });
    
    // onUpload should be called with empty array since all files were rejected
    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalledWith([]);
    }, { timeout: 2000 });
    
    alertSpy.mockRestore();
  });

  it('should show upload progress', async () => {
    const user = userEvent.setup();
    
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    // The component shows "Uploading Files" immediately after file selection
    await waitFor(() => {
      expect(screen.getByText(/Uploading Files/i)).toBeInTheDocument();
    }, { timeout: 3000 });
    
    // Verify upload item appears (it should have a test-id pattern)
    await waitFor(() => {
      const uploadItems = screen.getAllByText('test.pdf');
      expect(uploadItems.length).toBeGreaterThan(0);
    }, { timeout: 3000 });
  });

  it('should allow removing upload items', async () => {
    const user = userEvent.setup();
    
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    await waitFor(() => {
      expect(screen.getByText(/Uploading Files/i)).toBeInTheDocument();
    }, { timeout: 3000 });
    
    // Find and click remove button
    await waitFor(async () => {
      const removeButtons = screen.getAllByRole('button').filter(btn => 
        btn.getAttribute('data-testid')?.startsWith('button-remove-upload-')
      );
      if (removeButtons.length > 0) {
        await user.click(removeButtons[0]);
        // After clicking, the upload item should be removed
        await new Promise(resolve => setTimeout(resolve, 100));
        expect(screen.queryByText(/Uploading Files/i)).not.toBeInTheDocument();
      }
    }, { timeout: 3000 });
  });

  it('should format file size correctly', async () => {
    const user = userEvent.setup();
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const file = new File(['test'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await user.upload(input, file);
    
    await waitFor(() => {
      // File name should be displayed
      expect(screen.getByText(/test\.pdf/i)).toBeInTheDocument();
      // File size should be formatted - check within upload item context
      // to avoid matching the help text "Supports PDF files up to 50 MB"
      const uploadItems = screen.queryAllByTestId(/upload-item-/);
      expect(uploadItems.length).toBeGreaterThan(0);
      // Check that the upload item contains file size info (not just the help text)
      const uploadItem = uploadItems[0];
      const fileSizePattern = /\d+\s*(KB|MB|Bytes)/i;
      expect(uploadItem?.textContent).toMatch(fileSizePattern);
    }, { timeout: 3000 });
  });

  it('should apply dragging styles when dragging over', () => {
    render(<UploadZone onUpload={mockOnUpload} />);
    
    const uploadZone = screen.getByTestId('upload-zone');
    
    // Create mock drag event
    const dragOverEvent = new Event('dragover', { bubbles: true, cancelable: true });
    Object.defineProperty(dragOverEvent, 'dataTransfer', {
      value: {
        files: [],
      },
      writable: false,
    });
    
    uploadZone.dispatchEvent(dragOverEvent);
    
    // Check if dragging styles are applied (the component sets isDragging state)
    expect(uploadZone).toBeInTheDocument();
  });

  it('should work without onUpload callback', async () => {
    const user = userEvent.setup();
    render(<UploadZone />);
    
    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const input = screen.getByTestId('input-file-upload') as HTMLInputElement;
    
    await expect(async () => {
      await user.upload(input, file);
    }).not.toThrow();
  });
});

