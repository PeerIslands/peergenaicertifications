import { useState, useRef, KeyboardEvent } from "react";
import { Send, Paperclip } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface MessageInputProps {
  onSendMessage: (message: string) => void;
  onUploadClick: () => void;
  disabled?: boolean;
}

export function MessageInput({ onSendMessage, onUploadClick, disabled }: MessageInputProps) {
  const [message, setMessage] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    e.target.style.height = "auto";
    e.target.style.height = Math.min(e.target.scrollHeight, 120) + "px";
  };

  return (
    <div className="border-t border-border bg-background/95 backdrop-blur-md">
      <div className="flex items-end gap-2 p-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={onUploadClick}
          disabled={disabled}
          data-testid="button-upload-pdf"
        >
          <Paperclip className="h-5 w-5" />
          <span className="sr-only">Upload PDF</span>
        </Button>
        
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your PDF..."
          className="min-h-[44px] max-h-[120px] resize-none text-[15px]"
          disabled={disabled}
          data-testid="input-message"
        />
        
        <Button
          onClick={handleSend}
          disabled={!message.trim() || disabled}
          size="icon"
          data-testid="button-send"
        >
          <Send className="h-5 w-5" />
          <span className="sr-only">Send message</span>
        </Button>
      </div>
    </div>
  );
}
