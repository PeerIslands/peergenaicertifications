import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useEffect, useRef } from "react";
import { Bot } from "lucide-react";
import { Message } from "./message";
import { MessageInput } from "./message-input";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import { useParams } from "wouter";

interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  fileContext?: string[] | null;
}

const suggestions = [
  "Summarize this document",
  "What are the key points?",
  "Find specific information",
];

export function ChatArea() {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const { session } = useParams();

  console.log("session", session);

  const { data: messagesData, isLoading } = useQuery< ChatMessage[]>({
    queryKey: ["/api/messages", session],
  });

  const chatMutation = useMutation({
    mutationFn: async (message: string) => {
      const response = await apiRequest("POST", "/api/chat/" + session, { message });
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/messages", session] });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to send message",
        description: error.message || "Please try again.",
        variant: "destructive",
      });
    },
  });

  const messages = messagesData || [];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, chatMutation.isPending]);

  const handleSendMessage = (message: string) => {
    chatMutation.mutate(message);
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSendMessage(suggestion);
  };

  return (
    <div className="flex-1 flex flex-col h-full overflow-y-auto">
      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4" data-testid="chat-area">
        {isLoading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : messages.length === 0 ? (
          /* Welcome Message */
          <div className="flex justify-center">
            <div className="max-w-2xl text-center py-8">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <Bot className="w-8 h-8 text-primary" />
              </div>
              <h2 className="text-xl font-semibold text-foreground mb-2">
                Welcome to AI PDF Assistant
              </h2>
              <p className="text-muted-foreground mb-4">
                Upload PDF files and start chatting about their contents. I can help you 
                analyze, summarize, and answer questions about your documents.
              </p>
              <div className="flex flex-wrap gap-2 justify-center">
                {suggestions.map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="secondary"
                    size="sm"
                    onClick={() => handleSuggestionClick(suggestion)}
                    data-testid={`suggestion-${index}`}
                  >
                    "{suggestion}"
                  </Button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Chat Messages */
          messages.map((message) => (
            <Message
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={new Date(message.timestamp)}
            />
          ))
        )}

        {/* Typing Indicator */}
        {chatMutation.isPending && (
          <div className="flex gap-3">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
                <Bot className="w-4 h-4 text-primary-foreground" />
              </div>
            </div>
            <div className="flex-1">
              <div className="bg-card border border-border rounded-lg px-4 py-3 max-w-3xl">
                <div className="flex items-center gap-1">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <div
                      key={i}
                      className={`w-2 h-2 bg-muted-foreground rounded-full animate-bounce`}
                      style={{ animationDelay: `${i * 0.2}s` }}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Message Input */}
      <MessageInput 
        onSendMessage={handleSendMessage}
        disabled={chatMutation.isPending}
      />
    </div>
  );
}
