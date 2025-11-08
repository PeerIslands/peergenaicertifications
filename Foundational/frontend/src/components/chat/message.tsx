import { User, Bot } from "lucide-react";

interface MessageProps {
  role: "user" | "ai";
  content: string;
  timestamp?: Date;
}

export function Message({ role, content, timestamp }: MessageProps) {
  const isUser = role === "user";
  const time = timestamp 
    ? timestamp.toLocaleTimeString("en-US", {
        hour: "numeric",
        minute: "2-digit",
        hour12: true,
      })
    : "";

  return (
    <div className="chat-message flex gap-3 animate-in slide-in-from-bottom-2" data-testid={`message-${role}`}>
      <div className="flex-shrink-0">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
          isUser ? "bg-accent" : "bg-primary"
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-accent-foreground" />
          ) : (
            <Bot className="w-4 h-4 text-primary-foreground" />
          )}
        </div>
      </div>
      
      <div className="flex-1">
        <div className={`rounded-lg px-4 py-3 max-w-3xl ${
          isUser 
            ? "bg-accent text-accent-foreground" 
            : "bg-card border border-border"
        }`}>
          <div className="whitespace-pre-wrap text-sm leading-relaxed">
            {content}
          </div>
        </div>
        {time && (
          <p className="text-xs text-muted-foreground mt-1">{time}</p>
        )}
      </div>
    </div>
  );
}
