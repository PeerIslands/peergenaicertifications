import { Plus, MessageSquare, FileText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";

interface Conversation {
  _id?: string;
  title: string;
  createdAt?: string | Date;
  updatedAt?: string | Date;
  isActive?: boolean;
}

interface PDFDocument {
  _id?: string;
  originalName: string;
  status: 'uploading' | 'processing' | 'completed' | 'error';
}

interface ChatSidebarProps {
  conversations: Conversation[];
  documents: PDFDocument[];
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
}

export function ChatSidebar({
  conversations,
  documents,
  onNewChat,
  onSelectConversation,
}: ChatSidebarProps) {
  return (
    <div className="flex flex-col h-full border-r border-sidebar-border bg-sidebar">
      <div className="p-4">
        <Button
          onClick={onNewChat}
          className="w-full"
          data-testid="button-new-chat"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Chat
        </Button>
      </div>

      <ScrollArea className="flex-1">
        <div className="p-4 space-y-4">
          <div>
            <h3 className="text-sm font-semibold mb-2 text-sidebar-foreground">Conversations</h3>
            <div className="space-y-1">
              {conversations.length === 0 ? (
                <p className="text-sm text-muted-foreground p-3">No conversations yet</p>
              ) : (
                conversations.map((conv) => (
                  <button
                    key={conv._id}
                    onClick={() => onSelectConversation(conv._id!)}
                    className={`w-full text-left p-3 rounded-md transition-colors hover-elevate ${
                      conv.isActive
                        ? "bg-sidebar-accent text-sidebar-accent-foreground"
                        : "text-sidebar-foreground"
                    }`}
                    data-testid={`button-conversation-${conv._id}`}
                  >
                    <div className="flex items-start gap-2">
                      <MessageSquare className="h-4 w-4 mt-0.5 shrink-0" />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate">{conv.title}</p>
                        <p className="text-xs text-muted-foreground">
                          {conv.updatedAt ? new Date(conv.updatedAt).toLocaleDateString() : conv.createdAt ? new Date(conv.createdAt).toLocaleDateString() : ''}
                        </p>
                      </div>
                    </div>
                  </button>
                ))
              )}
            </div>
          </div>

          <Separator />

          <div>
            <h3 className="text-sm font-semibold mb-2 text-sidebar-foreground">PDF Documents</h3>
            <div className="space-y-1">
              {documents.length === 0 ? (
                <p className="text-sm text-muted-foreground p-3">No documents uploaded</p>
              ) : (
                documents.map((doc) => (
                  <div
                    key={doc._id}
                    className="flex items-center gap-2 p-2 rounded-md text-sm text-sidebar-foreground"
                  >
                    <FileText className="h-4 w-4 text-primary shrink-0" />
                    <div className="flex-1 min-w-0">
                      <span className="truncate">{doc.originalName}</span>
                      <div className="text-xs text-muted-foreground">
                        {doc.status === 'completed' && '✓ Ready'}
                        {doc.status === 'processing' && '⏳ Processing...'}
                        {doc.status === 'uploading' && '📤 Uploading...'}
                        {doc.status === 'error' && '❌ Error'}
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </ScrollArea>
    </div>
  );
}
