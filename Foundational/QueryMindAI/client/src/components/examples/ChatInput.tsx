import { ChatInput } from '../ChatInput';
import { useState } from 'react';

export default function ChatInputExample() {
  const [lastMessage, setLastMessage] = useState<string>('');
  const [isDisabled, setIsDisabled] = useState(false);

  const handleSendMessage = (message: string) => {
    setLastMessage(message);
    setIsDisabled(true);
    // Simulate processing
    setTimeout(() => setIsDisabled(false), 2000);
  };

  return (
    <div className="space-y-4">
      {lastMessage && (
        <div className="p-4 bg-muted rounded-md">
          <p className="text-sm text-muted-foreground">Last message sent:</p>
          <p className="font-medium">{lastMessage}</p>
        </div>
      )}
      <ChatInput 
        onSendMessage={handleSendMessage}
        disabled={isDisabled}
      />
    </div>
  );
}