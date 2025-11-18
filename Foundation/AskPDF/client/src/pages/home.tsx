import { useState, useRef, useEffect } from "react";
import ChatHeader from "@/components/ChatHeader";
import ChatMessage, { type Message } from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import ParameterControls, { type ChatParameters } from "@/components/ParameterControls";
import EmptyState from "@/components/EmptyState";
import { ScrollArea } from "@/components/ui/scroll-area";
import { chatService } from "@/services/chatService";
import { useToast } from "@/hooks/use-toast";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [parameters, setParameters] = useState<ChatParameters>({
    temperature: 0.7,
    topP: 1.0,
    topK: 5,
    maxTokens: 2048,
    frequencyPenalty: 0,
    presencePenalty: 0,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [userId] = useState(() => `user_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const scrollRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const scrollToBottom = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(content, userId, parameters);
      
      const assistantMessage: Message = {
        id: response.id,
        role: "assistant",
        content: response.answer,
        timestamp: new Date(response.timestamp),
        sources: response.sources,
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error("Error sending message:", error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
      
      // Add error message
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "Sorry, I encountered an error while processing your request. Please try again.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptClick = (prompt: string) => {
    handleSendMessage(prompt);
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex h-screen flex-col lg:flex-row">
      <div className="flex flex-col flex-1 min-w-0">
        <ChatHeader onClearChat={handleClearChat} />
        
        <ScrollArea className="flex-1">
          <div className="max-w-3xl mx-auto px-4 py-6">
            {messages.length === 0 ? (
              <EmptyState onPromptClick={handlePromptClick} />
            ) : (
              <div className="space-y-6">
                {messages.map((message) => (
                  <ChatMessage key={message.id} message={message} />
                ))}
                {isLoading && (
                  <div className="flex gap-4 justify-start" data-testid="loading-indicator">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                    </div>
                    <div className="flex items-center gap-1">
                      <span className="text-sm text-muted-foreground">Thinking</span>
                      <span className="animate-pulse">...</span>
                    </div>
                  </div>
                )}
                <div ref={scrollRef} />
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="border-t border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 p-4">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSend={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </div>

      <div className="w-full lg:w-80 border-l border-border hidden lg:block">
        <ParameterControls parameters={parameters} onParametersChange={setParameters} />
      </div>
    </div>
  );
}
