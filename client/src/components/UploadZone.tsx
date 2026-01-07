import { useState, useCallback } from "react";
import { Upload, FileText, X, Check } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

interface UploadedFile {
  name: string;
  size: number;
  pages: number;
  file?: File;
}

interface UploadZoneProps {
  onFileUpload?: (file: UploadedFile) => void;
  uploadedFile?: UploadedFile | null;
}

export default function UploadZone({ onFileUpload, uploadedFile }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [localFile, setLocalFile] = useState<UploadedFile | null>(uploadedFile || null);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDragIn = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragOut = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const processFile = useCallback((file: File) => {
    if (file.type === "application/pdf") {
      const uploadedFile: UploadedFile = {
        name: file.name,
        size: file.size,
        pages: 0, // Will be determined by backend
        file: file,
      };
      setLocalFile(uploadedFile);
      onFileUpload?.(uploadedFile);
    }
  }, [onFileUpload]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  }, [processFile]);

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      processFile(files[0]);
    }
  }, [processFile]);

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const clearFile = () => {
    setLocalFile(null);
  };

  return (
    <div className="space-y-4">
      <label
        className={`
          relative min-h-64 rounded-lg border-2 border-dashed transition-all duration-200 block cursor-pointer
          ${isDragging 
            ? "border-primary bg-primary/5" 
            : "border-muted-foreground/25 hover:border-primary/50"
          }
          ${localFile ? "bg-muted/30" : ""}
        `}
        onDragEnter={handleDragIn}
        onDragLeave={handleDragOut}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        data-testid="upload-dropzone"
      >
        <input
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="hidden"
          data-testid="input-file-upload"
        />
        
        <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
          <div className={`
            w-16 h-16 rounded-full flex items-center justify-center mb-4 transition-colors
            ${isDragging ? "bg-primary/20" : "bg-muted"}
          `}>
            <Upload className={`w-8 h-8 ${isDragging ? "text-primary" : "text-muted-foreground"}`} />
          </div>
          
          <h3 className="text-lg font-medium mb-2">
            {isDragging ? "Drop your PDF here" : "Upload your PDF"}
          </h3>
          <p className="text-sm text-muted-foreground text-center max-w-xs">
            Drag and drop a PDF file here, or click to browse
          </p>
          
          <Badge variant="secondary" className="mt-4">
            PDF files only (max 10MB)
          </Badge>
        </div>
      </label>

      {localFile && (
        <Card className="p-4">
          <div className="flex items-start justify-between gap-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-primary" />
              </div>
              <div className="min-w-0">
                <p className="font-medium truncate" data-testid="text-file-name">{localFile.name}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-muted-foreground" data-testid="text-file-size">
                    {formatFileSize(localFile.size)}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500/10 text-green-600 dark:text-green-400 border-0">
                <Check className="w-3 h-3 mr-1" />
                Ready
              </Badge>
              <Button
                size="icon"
                variant="ghost"
                onClick={clearFile}
                data-testid="button-clear-file"
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
