import { useState, useCallback } from "react";
import { Upload, FileText, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { ChatAPI } from "@/lib/api";

interface PDFFile {
  id: string;
  name: string;
  size: number;
}

interface PDFUploadProps {
  onUploadComplete: (files: PDFFile[]) => void;
  onClose: () => void;
}

export function PDFUpload({ onUploadComplete, onClose }: PDFUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadError, setUploadError] = useState<string | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const processFiles = (files: FileList | null) => {
    if (!files) return;
    
    const pdfFiles = Array.from(files).filter(file => file.type === "application/pdf");
    
    if (pdfFiles.length > 0) {
      setSelectedFiles(pdfFiles);
      setUploadError(null);
    } else {
      setUploadError("Please select only PDF files.");
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    processFiles(e.dataTransfer.files);
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    processFiles(e.target.files);
  };

  const uploadFiles = async () => {
    if (selectedFiles.length === 0) return;

    setIsUploading(true);
    setUploadProgress(0);
    setUploadError(null);

    try {
      const uploadPromises = selectedFiles.map(async (file, index) => {
        const response = await ChatAPI.uploadPDF(file);
        
        // Update progress
        setUploadProgress((index + 1) / selectedFiles.length * 100);
        
        return {
          id: response.document._id || '',
          name: response.document.originalName || '',
          size: response.document.size,
        };
      });

      const uploadedFiles = await Promise.all(uploadPromises);
      
      setTimeout(() => {
        onUploadComplete(uploadedFiles);
        onClose();
      }, 500);
    } catch (error) {
      console.error('Upload error:', error);
      setUploadError("Failed to upload files. Please try again.");
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (index: number) => {
    setSelectedFiles(files => files.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          isDragging
            ? "border-primary bg-primary/5"
            : "border-border hover:border-primary/50"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
        <h3 className="text-lg font-semibold mb-2">Upload PDF Documents</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Drag and drop your PDFs here, or click to browse
        </p>
        <input
          type="file"
          id="pdf-upload"
          accept=".pdf"
          multiple
          onChange={handleFileSelect}
          className="hidden"
          data-testid="input-pdf-file"
        />
        <Button asChild variant="outline">
          <label htmlFor="pdf-upload" className="cursor-pointer">
            Select Files
          </label>
        </Button>
      </div>

      {uploadError && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-lg">
          <p className="text-sm text-destructive">{uploadError}</p>
        </div>
      )}

      {selectedFiles.length > 0 && (
        <div className="space-y-2">
          {selectedFiles.map((file, index) => (
            <div
              key={index}
              className="flex items-center gap-3 p-3 bg-card border border-card-border rounded-lg"
            >
              <FileText className="h-5 w-5 text-primary shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(2)} KB
                </p>
              </div>
              {!isUploading && (
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => removeFile(index)}
                  data-testid={`button-remove-${index}`}
                >
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          ))}
        </div>
      )}

      {isUploading && (
        <div className="space-y-2">
          <Progress value={uploadProgress} data-testid="progress-upload" />
          <p className="text-sm text-center text-muted-foreground">
            Uploading... {Math.round(uploadProgress)}%
          </p>
        </div>
      )}

      {selectedFiles.length > 0 && !isUploading && (
        <div className="flex gap-2">
          <Button onClick={uploadFiles} className="flex-1">
            Upload {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''}
          </Button>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      )}
    </div>
  );
}
