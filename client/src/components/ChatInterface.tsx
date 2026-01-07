import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import type { Message } from "@shared/schema";

interface ChatInterfaceProps {
  messages?: Message[];
  isLoading?: boolean;
  onSendMessage?: (message: string) => void;
  onClearChat?: () => void;
}

export default function ChatInterface({ 
  messages = [], 
  isLoading = false, 
  onSendMessage,
  onClearChat,
}: ChatInterfaceProps) {
  const [inputValue, setInputValue] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = () => {
    if (!inputValue.trim() || isLoading) return;
    onSendMessage?.(inputValue.trim());
    setInputValue("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between p-3 border-b">
        <h3 className="font-medium text-sm">Chat with Document</h3>
        {messages.length > 0 && (
          <Button 
            size="sm" 
            variant="ghost" 
            onClick={onClearChat}
            data-testid="button-clear-chat"
          >
            <Trash2 className="w-3 h-3 mr-1" />
            Clear
          </Button>
        )}
      </div>
      
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="space-y-4 max-w-3xl mx-auto">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mb-4">
                <Bot className="w-8 h-8 text-primary" />
              </div>
              <h3 className="text-lg font-medium mb-2">Start a conversation</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Ask questions about your uploaded PDF document. The AI will retrieve relevant information and provide accurate answers.
              </p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex gap-3 ${message.role === "user" ? "flex-row-reverse" : ""}`}
              data-testid={`message-${message.role}-${message.id}`}
            >
              <Avatar className="w-8 h-8 flex-shrink-0">
                <AvatarFallback className={message.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"}>
                  {message.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                </AvatarFallback>
              </Avatar>
              <div
                className={`
                  max-w-[80%] rounded-2xl px-4 py-3
                  ${message.role === "user" 
                    ? "bg-primary text-primary-foreground" 
                    : "bg-muted"
                  }
                `}
              >
                <p className={`text-sm ${message.role === "assistant" ? "text-base leading-relaxed" : ""}`}>
                  {message.content}
                </p>
                <p className={`text-xs mt-2 ${message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"}`}>
                  {new Date(message.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                </p>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <Avatar className="w-8 h-8 flex-shrink-0">
                <AvatarFallback className="bg-muted">
                  <Bot className="w-4 h-4" />
                </AvatarFallback>
              </Avatar>
              <div className="bg-muted rounded-2xl px-4 py-3 flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm text-muted-foreground">Searching document and generating response...</span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      <div className="border-t p-4">
        <div className="max-w-3xl mx-auto flex gap-2">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your document..."
            className="min-h-[44px] max-h-32 resize-none"
            rows={1}
            disabled={isLoading}
            data-testid="input-chat-message"
          />
          <Button 
            onClick={handleSend} 
            disabled={!inputValue.trim() || isLoading}
            data-testid="button-send-message"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </Button>
        </div>
      </div>
    </div>
  );
}
