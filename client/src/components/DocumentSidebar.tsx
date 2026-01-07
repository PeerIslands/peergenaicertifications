import { FileText, Trash2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { Document } from "@shared/schema";

interface DocumentSidebarProps {
  documents?: Document[];
  selectedDocumentId?: string | null;
  onSelectDocument?: (id: string) => void;
  onRemoveDocument?: (id: string) => void;
}

export default function DocumentSidebar({
  documents = [],
  selectedDocumentId,
  onSelectDocument,
  onRemoveDocument,
}: DocumentSidebarProps) {
  return (
    <div className="h-full flex flex-col bg-sidebar">
      <div className="p-4 border-b border-sidebar-border">
        <h2 className="font-semibold flex items-center gap-2 text-sidebar-foreground">
          <FileText className="w-4 h-4" />
          Documents
        </h2>
        {documents.length > 0 && (
          <p className="text-sm text-muted-foreground mt-1">
            {documents.length} uploaded
          </p>
        )}
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-2">
          {documents.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center mx-auto mb-3">
                <FileText className="w-5 h-5 text-muted-foreground" />
              </div>
              <p className="text-sm text-muted-foreground">
                No documents uploaded
              </p>
            </div>
          ) : (
            documents.map((doc) => (
              <Card
                key={doc.id}
                className={`p-3 cursor-pointer transition-all hover-elevate ${
                  selectedDocumentId === doc.id ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => onSelectDocument?.(doc.id)}
                data-testid={`card-document-${doc.id}`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-sm truncate">{doc.name}</p>
                  </div>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="h-7 w-7 flex-shrink-0"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveDocument?.(doc.id);
                    }}
                    data-testid={`button-remove-document-${doc.id}`}
                  >
                    <Trash2 className="w-3 h-3" />
                  </Button>
                </div>
              </Card>
            ))
          )}
        </div>
      </ScrollArea>
    </div>
  );
}
