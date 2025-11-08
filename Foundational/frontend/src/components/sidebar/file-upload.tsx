import { useState, useRef } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Upload, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface UploadingFile {
  name: string;
  progress: number;
}

export function FileUpload() {
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState<UploadingFile[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const uploadMutation = useMutation({
    mutationFn: async (files: FileList) => {
      const formData = new FormData();
      // Backend expects a single file field named "file"
      // Upload first PDF only for now; extend if backend supports multiple
      formData.append("file", files[0]);

      // Simulate progress for each file
      const fileNames = Array.from(files).map(f => f.name);
      setUploadingFiles(fileNames.map(name => ({ name, progress: 0 })));

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setUploadingFiles(prev => 
          prev.map(file => ({
            ...file,
            progress: Math.min(file.progress + Math.random() * 30, 95)
          }))
        );
      }, 200);

      try {
        const response = await apiRequest("POST", "/api/upload", formData);
        const result = await response.json();
        clearInterval(progressInterval);
        setUploadingFiles([]);
        return result;
      } catch (error) {
        clearInterval(progressInterval);
        setUploadingFiles([]);
        throw error;
      }
    },
    onSuccess: () => {
      // If there is a files listing endpoint later, invalidate it
      queryClient.invalidateQueries({ queryKey: ["/api/files"] });
      toast({
        title: "Upload successful",
        description: "File uploaded and processed.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Upload failed",
        description: error.message || "Failed to upload files. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;

    const pdfFiles = Array.from(files).filter(file => file.type === "application/pdf");
    
    if (pdfFiles.length === 0) {
      toast({
        title: "Invalid file type",
        description: "Please select only PDF files.",
        variant: "destructive",
      });
      return;
    }

    if (pdfFiles.length !== files.length) {
      toast({
        title: "Some files skipped",
        description: "Only PDF files were selected for upload.",
      });
    }

    const fileList = new DataTransfer();
    pdfFiles.forEach(file => fileList.items.add(file));
    
    uploadMutation.mutate(fileList.files);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="p-4 border-b border-border">
      <h3 className="text-sm font-medium text-muted-foreground mb-3">Upload PDF Files</h3>
      
      <div
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
          isDragOver 
            ? "border-primary bg-primary/5" 
            : "border-border hover:border-primary"
        }`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleClick}
        data-testid="file-upload-area"
      >
        <Upload className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
        <p className="text-sm text-muted-foreground mb-1">
          Drag & drop PDF files here
        </p>
        <p className="text-xs text-muted-foreground">or click to browse</p>
        
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          multiple
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
          data-testid="file-input"
        />
      </div>

      {/* Upload Progress Modal */}
      {uploadingFiles.length > 0 && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card rounded-lg p-6 max-w-md w-full mx-4 border border-border">
            <div className="flex items-center gap-3 mb-4">
              <FileText className="text-primary w-5 h-5" />
              <h3 className="text-lg font-semibold text-foreground">Uploading Files</h3>
            </div>
            
            <div className="space-y-3">
              {uploadingFiles.map((file, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-foreground truncate">{file.name}</span>
                    <span className="text-muted-foreground">{Math.round(file.progress)}%</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${file.progress}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
