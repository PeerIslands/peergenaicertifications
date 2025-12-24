import { useState } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

/**
 * Chat input component that allows users to type and send messages.
 * Supports Enter key to submit and Shift+Enter for new lines.
 * 
 * @param props - Component props
 * @param props.onSendMessage - Callback function called when a message is submitted
 * @param props.disabled - Whether the input is disabled (default: false)
 * @param props.placeholder - Placeholder text for the input (default: "Type your question here...")
 * @returns A React component rendering a textarea and send button
 */
export function ChatInput({ 
  onSendMessage, 
  disabled = false,
  placeholder = "Type your question here..." 
}: ChatInputProps) {
  const [message, setMessage] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
      console.log('Message sent:', message.trim());
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <Card className="p-4 border-t">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          disabled={disabled}
          className="resize-none min-h-[44px] max-h-32"
          rows={1}
          data-testid="input-chat-message"
        />
        <Button 
          type="submit" 
          size="icon"
          disabled={!message.trim() || disabled}
          data-testid="button-send-message"
        >
          <Send className="h-4 w-4" />
          <span className="sr-only">Send message</span>
        </Button>
      </form>
    </Card>
  );
}