import { Bot, User, FileText } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { useState } from "react";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  sources?: Array<{
    content: string;
    metadata?: any;
    score?: number;
    searchType?: string;
  }>;
}

interface ChatMessageProps {
  message: Message;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div
      className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}
      data-testid={`message-${message.id}`}
    >
      {!isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className="bg-primary text-primary-foreground">
            <Bot className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
      <div className={`flex flex-col gap-1 max-w-[70%] ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-primary text-primary-foreground"
              : "bg-card border border-card-border"
          }`}
        >
          <p className="text-base leading-relaxed whitespace-pre-wrap break-words">
            {message.content}
          </p>
        </div>
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <Collapsible open={sourcesOpen} onOpenChange={setSourcesOpen}>
            <CollapsibleTrigger className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors">
              <FileText className="h-3 w-3" />
              {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2 space-y-2">
              {message.sources.map((source, index) => (
                <div key={index} className="text-xs bg-muted/50 rounded-lg p-3 border">
                  <div className="font-medium mb-1 flex justify-between items-center">
                    <span>Source {index + 1}</span>
                    {source.metadata?.document_name && (
                      <span className="text-xs text-blue-600 font-normal">
                        {source.metadata.document_name}
                      </span>
                    )}
                  </div>
                  <p className="text-muted-foreground line-clamp-3">
                    {source.content}
                  </p>
                  <div className="text-xs text-muted-foreground mt-2 space-y-1">
                    <div className="flex justify-between">
                      {source.score && (
                        <span>Relevance: {(source.score * 100).toFixed(1)}%</span>
                      )}
                      {source.searchType && (
                        <span className={`px-1 py-0.5 rounded text-xs ${
                          source.searchType === 'semantic' 
                            ? 'bg-blue-100 text-blue-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {source.searchType}
                        </span>
                      )}
                    </div>
                    {source.metadata && (
                      <div className="flex gap-2 text-xs">
                        {source.metadata.page_number && (
                          <span>Page {source.metadata.page_number}</span>
                        )}
                        {source.metadata.chunk_index !== undefined && (
                          <span>Chunk {source.metadata.chunk_index}</span>
                        )}
                        {source.metadata.word_count && (
                          <span>{source.metadata.word_count} words</span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}
        
        <span className="text-xs text-muted-foreground opacity-60">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </span>
      </div>
      {isUser && (
        <Avatar className="h-8 w-8 shrink-0">
          <AvatarFallback className="bg-muted">
            <User className="h-4 w-4" />
          </AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
