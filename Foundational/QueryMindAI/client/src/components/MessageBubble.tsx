import { Bot, User } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  responseTime?: number;
}

export function MessageBubble({ role, content, timestamp, responseTime }: MessageBubbleProps) {
  const isUser = role === "user";
  
  return (
    <div 
      className={`flex gap-3 max-w-[80%] ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`}
      data-testid={`message-${role}`}
    >
      <Avatar className="h-8 w-8 flex-shrink-0">
        <AvatarFallback className={isUser ? "bg-chart-2" : "bg-chart-1"}>
          {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
        </AvatarFallback>
      </Avatar>
      
      <Card className={`p-4 ${isUser ? 'bg-chart-2/10' : 'bg-chart-1/10'}`}>
        <div className="whitespace-pre-wrap text-sm leading-relaxed" data-testid="message-content">
          {content}
        </div>
        <div className="flex items-center gap-2 mt-2 text-xs text-muted-foreground">
          <span data-testid="message-timestamp">
            {timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
          {responseTime && (
            <span data-testid="message-response-time">
              • {responseTime}ms
            </span>
          )}
        </div>
      </Card>
    </div>
  );
}