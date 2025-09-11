import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { FileText, X } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";

interface UploadedFile {
  id: string;
  file_id: string;
  filename: string;
  originalName: string;
  size: string;
  uploadedAt: string;
}

export function FileList() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data, isLoading } = useQuery<UploadedFile[]>({
    queryKey: ["/api/files"],
  });

  const deleteMutation = useMutation({
    mutationFn: async (fileId: string) => {
      const response = await apiRequest("DELETE", `/api/files/${fileId}`);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/files"] });
      toast({
        title: "File deleted",
        description: "The file has been removed successfully.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Delete failed",
        description: error.message || "Failed to delete file. Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleDeleteFile = (fileId: string) => {
    deleteMutation.mutate(fileId);
  };

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-sm font-medium text-muted-foreground mb-3">Uploaded Files</h3>
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex items-center gap-3 p-3 bg-card rounded-lg border border-border">
                <div className="w-4 h-4 bg-muted rounded animate-pulse" />
                <div className="flex-1">
                  <div className="h-4 bg-muted rounded w-3/4 mb-1 animate-pulse" />
                  <div className="h-3 bg-muted rounded w-1/2 animate-pulse" />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  const files = data || [];

  return (
    <div className="flex-1 overflow-y-auto">
      <div className="p-4">
        <h3 className="text-sm font-medium text-muted-foreground mb-3">Uploaded Files</h3>
        
        {files.length === 0 ? (
          <div className="text-center py-8">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
            <p className="text-sm text-muted-foreground">No files uploaded yet</p>
            <p className="text-xs text-muted-foreground mt-1">
              Upload PDF files to start chatting about their contents
            </p>
          </div>
        ) : (
          <div className="space-y-2" data-testid="file-list">
            {files.map((file) => (
              <div
                key={file.file_id}
                className="flex items-center gap-3 p-3 bg-card rounded-lg border border-border hover:bg-accent transition-colors"
                data-testid={`file-item-${file.id}`}
              >
                <FileText className="text-destructive w-5 h-5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {file.filename}
                  </p>
                  <p className="text-xs text-muted-foreground">{ (Number(file.size) / 1024 / 1024).toFixed(2)} MB</p>
                </div>
                <button
                  onClick={() => handleDeleteFile(file.file_id)}
                  className="p-1 hover:bg-muted rounded transition-colors"
                  disabled={deleteMutation.isPending}
                  data-testid={`delete-file-${file.id}`}
                >
                  <X className="w-3 h-3 text-muted-foreground" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
