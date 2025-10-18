import { useState } from "react";
import ChatInput from "../ChatInput";

export default function ChatInputExample() {
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = (message: string) => {
    console.log("Message sent:", message);
    setIsLoading(true);
    setTimeout(() => setIsLoading(false), 2000);
  };

  return (
    <div className="p-4 bg-background">
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
}
