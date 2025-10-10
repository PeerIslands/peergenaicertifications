import { Bot } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-4">
      <Avatar className="h-8 w-8 shrink-0">
        <AvatarFallback className="bg-primary/10">
          <Bot className="h-4 w-4 text-primary" />
        </AvatarFallback>
      </Avatar>
      
      <div className="flex items-center gap-1 px-4 py-3 bg-card border border-card-border rounded-2xl">
        <div className="flex gap-1">
          <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce [animation-delay:-0.3s]" />
          <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce [animation-delay:-0.15s]" />
          <div className="w-2 h-2 bg-muted-foreground/60 rounded-full animate-bounce" />
        </div>
      </div>
    </div>
  );
}
