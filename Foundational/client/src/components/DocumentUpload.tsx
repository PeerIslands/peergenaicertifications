import { useState, useRef } from "react";
import { CloudUpload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface DocumentUploadProps {
  onDocumentUploaded: () => void;
}

export default function DocumentUpload({ onDocumentUploaded }: DocumentUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const handleFileSelect = async (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const file = files[0];
    
    if (file.type !== 'application/pdf') {
      toast({
        title: "Invalid File Type",
        description: "Only PDF files are supported.",
        variant: "destructive",
      });
      return;
    }

    if (file.size > 10 * 1024 * 1024) { // 10MB limit
      toast({
        title: "File Too Large",
        description: "File size must be less than 10MB.",
        variant: "destructive",
      });
      return;
    }

    setIsUploading(true);

    try {
      const formData = new FormData();
      formData.append('pdf', file);

      const response = await fetch('/api/documents/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Upload failed');
      }

      toast({
        title: "Upload Successful",
        description: `${file.name} has been uploaded and is being processed.`,
      });

      onDocumentUploaded();
      
      // Clear file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      toast({
        title: "Upload Failed",
        description: (error as Error).message || "An error occurred during upload.",
        variant: "destructive",
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    handleFileSelect(e.dataTransfer.files);
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
  };

  return (
    <div className="mb-8">
      <h2 className="text-lg font-semibold text-foreground mb-4 flex items-center">
        <CloudUpload className="text-primary mr-2 w-5 h-5" />
        Document Upload
      </h2>
      
      <div 
        className="border-2 border-dashed border-border rounded-xl p-6 text-center hover:border-primary transition-colors cursor-pointer"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
        data-testid="upload-area"
      >
        <div className="mb-4">
          <CloudUpload className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
        </div>
        <p className="text-sm font-medium text-foreground mb-1">
          {isUploading ? "Uploading..." : "Drop PDF files here"}
        </p>
        <p className="text-xs text-secondary mb-4">or click to browse</p>
        <Button 
          disabled={isUploading}
          data-testid="button-select-files"
        >
          {isUploading ? "Uploading..." : "Select Files"}
        </Button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf"
        onChange={(e) => handleFileSelect(e.target.files)}
        className="hidden"
        data-testid="input-file"
      />
    </div>
  );
}
