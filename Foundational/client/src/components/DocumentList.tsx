import { FileText, CheckCircle, Clock, AlertCircle, RefreshCw, Trash2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import type { Document } from "@shared/schema";

interface DocumentListProps {
  documents: Document[];
  stats?: {
    totalDocuments: number;
    readyDocuments: number;
    processingDocuments: number;
    totalChunks: number;
    totalSize: number;
  };
  onManualRefetch?: () => void;
  onDocumentDeleted?: (documentId: string) => void;
}

export default function DocumentList({ documents, stats, onManualRefetch, onDocumentDeleted }: DocumentListProps) {
  const { toast } = useToast();
  const [deletingDocumentId, setDeletingDocumentId] = useState<string | null>(null);

  const handleDeleteDocument = async (documentId: string, documentName: string) => {
    setDeletingDocumentId(documentId);
    
    try {
      const response = await fetch(`/api/documents/${documentId}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Delete failed');
      }

      toast({
        title: "Document Deleted",
        description: `${documentName} has been deleted successfully.`,
      });

      // Notify parent component to refetch documents
      onDocumentDeleted?.(documentId);
    } catch (error) {
      toast({
        title: "Delete Failed",
        description: (error as Error).message || "An error occurred while deleting the document.",
        variant: "destructive",
      });
    } finally {
      setDeletingDocumentId(null);
    }
  };
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "ready":
        return <CheckCircle className="w-4 h-4 text-accent" />;
      case "processing":
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case "error":
        return <AlertCircle className="w-4 h-4 text-destructive" />;
      default:
        return <Clock className="w-4 h-4 text-secondary" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "ready":
        return <Badge className="bg-accent text-accent-foreground">Ready</Badge>;
      case "processing":
        return <Badge className="bg-yellow-500 text-white">Processing</Badge>;
      case "error":
        return <Badge variant="destructive">Error</Badge>;
      default:
        return <Badge variant="secondary">Uploading</Badge>;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  };

  return (
    <>
      <div className="mb-8">
        <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center justify-between">
          Processed Documents
          <div className="flex items-center space-x-2">
            <span className="text-xs bg-muted text-secondary px-2 py-1 rounded-full" data-testid="text-document-count">
              {documents.length}
            </span>
            {onManualRefetch && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onManualRefetch}
                className="h-6 w-6 p-0"
                title="Refresh documents"
              >
                <RefreshCw className="h-3 w-3" />
              </Button>
            )}
          </div>
        </h3>
        
        <div className="space-y-2" data-testid="document-list">
          {documents.length === 0 ? (
            <div className="text-center py-8 text-secondary">
              <FileText className="w-12 h-12 mx-auto mb-2 text-muted-foreground" />
              <p className="text-sm">No documents uploaded yet</p>
            </div>
          ) : (
            documents.map((document) => (
              <div 
                key={document.id} 
                className="bg-muted rounded-lg p-3 border border-border"
                data-testid={`card-document-${document.id}`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2 flex-1 min-w-0">
                    <FileText className="text-red-500 w-4 h-4 flex-shrink-0" />
                    <span 
                      className="text-sm font-medium text-foreground truncate"
                      title={document.name}
                      data-testid={`text-document-name-${document.id}`}
                    >
                      {document.name}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(document.status)}
                    <AlertDialog>
                      <AlertDialogTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 text-destructive hover:text-destructive hover:bg-destructive/10"
                          disabled={deletingDocumentId === document.id || document.status === 'processing'}
                          data-testid={`button-delete-${document.id}`}
                          title={document.status === 'processing' ? 'Cannot delete document while processing' : 'Delete document'}
                        >
                          <Trash2 className="h-3 w-3" />
                        </Button>
                      </AlertDialogTrigger>
                      <AlertDialogContent>
                        <AlertDialogHeader>
                          <AlertDialogTitle>Delete Document</AlertDialogTitle>
                          <AlertDialogDescription>
                            {document.status === 'processing' 
                              ? `Cannot delete "${document.name}" while it's being processed. Please wait for processing to complete.`
                              : `Are you sure you want to delete "${document.name}"? This action cannot be undone and will also delete all associated chunks and embeddings.`
                            }
                          </AlertDialogDescription>
                        </AlertDialogHeader>
                        <AlertDialogFooter>
                          <AlertDialogCancel>Cancel</AlertDialogCancel>
                          {document.status !== 'processing' && (
                            <AlertDialogAction
                              onClick={() => handleDeleteDocument(document.id, document.name)}
                              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                              disabled={deletingDocumentId === document.id}
                            >
                              {deletingDocumentId === document.id ? "Deleting..." : "Delete"}
                            </AlertDialogAction>
                          )}
                        </AlertDialogFooter>
                      </AlertDialogContent>
                    </AlertDialog>
                  </div>
                </div>
                
                <div className="flex items-center justify-between text-xs text-secondary mb-2">
                  <span data-testid={`text-document-size-${document.id}`}>
                    {formatFileSize(document.size)}
                  </span>
                  <span data-testid={`text-document-chunks-${document.id}`}>
                    {document.status === 'ready' ? `${document.chunks} chunks` : 'Processing...'}
                  </span>
                </div>
                
                <div className="bg-border rounded-full h-1">
                  <div 
                    className={`h-1 rounded-full transition-all duration-300 ${
                      document.status === 'ready' ? 'bg-accent w-full' : 
                      document.status === 'processing' ? 'bg-primary w-2/3' : 
                      document.status === 'error' ? 'bg-destructive w-1/4' : 
                      'bg-secondary w-1/3'
                    }`}
                  />
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {stats && (
        <div className="bg-muted rounded-lg p-4 border border-border" data-testid="processing-stats">
          <h4 className="text-sm font-semibold text-foreground mb-3">Processing Stats</h4>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-secondary">Total Documents:</span>
              <span className="font-medium text-foreground" data-testid="text-total-documents">
                {stats.totalDocuments}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-secondary">Ready Documents:</span>
              <span className="font-medium text-foreground" data-testid="text-ready-documents">
                {stats.readyDocuments}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-secondary">Vector Embeddings:</span>
              <span className="font-medium text-foreground" data-testid="text-total-chunks">
                {stats.totalChunks.toLocaleString()}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-secondary">Storage Used:</span>
              <span className="font-medium text-foreground" data-testid="text-storage-used">
                {formatFileSize(stats.totalSize)}
              </span>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
