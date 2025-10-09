import { FileText, Calendar, HardDrive, Trash2 } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow } from 'date-fns';
import type { DocumentSummary } from '@shared/schema';
import { Button } from '@/components/ui/button';

interface DocumentListProps {
  documents: DocumentSummary[];
  selectedDocumentId?: string;
  onDocumentSelect: (document: DocumentSummary) => void;
  isLoading?: boolean;
  onDeleteDocument?: (document: DocumentSummary) => void;
}

export function DocumentList({ 
  documents, 
  selectedDocumentId, 
  onDocumentSelect,
  isLoading = false,
  onDeleteDocument,
}: DocumentListProps) {
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium">Documents</h3>
        <div className="space-y-2">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-4">
                <div className="h-4 bg-muted rounded w-3/4 mb-2" />
                <div className="h-3 bg-muted rounded w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-medium">Documents</h3>
        <Card>
          <CardContent className="p-8 text-center">
            <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No documents uploaded yet</p>
            <p className="text-sm text-muted-foreground mt-1">
              Upload a document to get started
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium">Documents</h3>
        <Badge variant="secondary" data-testid="text-document-count">
          {documents.length} {documents.length === 1 ? 'document' : 'documents'}
        </Badge>
      </div>
      
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {documents.map((document) => (
          <Card
            key={document.id}
            className={`cursor-pointer transition-all hover-elevate ${
              selectedDocumentId === document.id 
                ? 'bg-primary/5 border-primary' 
                : 'hover:bg-muted/50'
            }`}
            onClick={() => onDocumentSelect(document)}
            data-testid={`card-document-${document.id}`}
          >
            <CardContent className="p-4">
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <FileText className="w-5 h-5 text-primary mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0 flex items-start justify-between gap-2">
                    <h4 className="font-medium truncate" data-testid="text-document-name">
                      {document.filename}
                    </h4>
                    {onDeleteDocument && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-muted-foreground hover:text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteDocument(document);
                        }}
                        aria-label="Delete document"
                        data-testid={`btn-delete-document-${document.id}`}
                        title="Delete document"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                </div>
                
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span data-testid="text-upload-time">
                      {formatDistanceToNow(new Date(document.uploadedAt), { addSuffix: true })}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    <HardDrive className="w-4 h-4" />
                    <span data-testid="text-file-size">
                      {formatFileSize(document.fileSize)}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
