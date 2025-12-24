import { useRef, useEffect } from "react";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";
import { ScrollArea } from "@/components/ui/scroll-area";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  responseTime?: number;
}

interface ChatContainerProps {
  messages: Message[];
  isTyping?: boolean;
}

/**
 * Container component that displays chat messages and handles auto-scrolling.
 * Shows an empty state when there are no messages and displays a typing indicator when the AI is responding.
 * 
 * @param props - Component props
 * @param props.messages - Array of messages to display
 * @param props.isTyping - Whether to show the typing indicator (default: false)
 * @returns A React component rendering a scrollable message container
 */
export function ChatContainer({ messages, isTyping = false }: ChatContainerProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      const scrollElement = scrollAreaRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollElement) {
        scrollElement.scrollTop = scrollElement.scrollHeight;
      }
    }
  }, [messages, isTyping]);

  return (
    <ScrollArea className="flex-1 p-4" ref={scrollAreaRef} data-testid="chat-container">
      <div className="space-y-4 min-h-full">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-center">
            <div className="max-w-md space-y-2" data-testid="empty-state">
              <h3 className="text-lg font-semibold">Welcome to AI Chat</h3>
              <p className="text-muted-foreground">
                Ask me anything! I'm powered by LangChain and ready to help with your questions.
              </p>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
              timestamp={message.timestamp}
              responseTime={message.responseTime}
            />
          ))
        )}
        <TypingIndicator visible={isTyping} />
      </div>
    </ScrollArea>
  );
}