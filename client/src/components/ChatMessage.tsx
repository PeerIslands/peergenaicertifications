import { Bot, User } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export interface Message {
  _id?: string;
  conversationId: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp?: string | Date;
  metadata?: {
    pdfChunks?: string[];
    sources?: Array<{
      page: number;
      text: string;
    }>;
  };
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="flex justify-center my-4">
        <div className="px-4 py-2 bg-muted rounded-md text-sm text-muted-foreground italic border-l-4 border-primary">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className={`flex gap-3 mb-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className="bg-primary/10">
            <Bot className="h-4 w-4 text-primary" />
          </AvatarFallback>
        </Avatar>
      )}
      
      <div className={`flex flex-col gap-1 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-card text-card-foreground border border-card-border"
          }`}
        >
          <p className="text-[15px] leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
          </p>
          
          {/* Show sources if available */}
          {message.metadata?.sources && message.metadata.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-border/50">
              <p className="text-xs text-muted-foreground mb-2">Sources:</p>
              <div className="space-y-1">
                {message.metadata.sources.map((source, index) => (
                  <div key={index} className="text-xs text-muted-foreground bg-muted/50 p-2 rounded">
                    <span className="font-medium">Page {source.page}:</span> {source.text}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <span className="text-xs text-muted-foreground px-1">
          {message.timestamp ? new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
        </span>
      </div>

      {isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
