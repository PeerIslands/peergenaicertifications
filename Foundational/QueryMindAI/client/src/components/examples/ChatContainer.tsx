import { ChatContainer } from '../ChatContainer';
import { useState } from 'react';
import { Button } from '@/components/ui/button';

export default function ChatContainerExample() {
  const [isTyping, setIsTyping] = useState(false);
  
  // Mock messages
  const mockMessages = [
    {
      id: '1',
      role: 'user' as const,
      content: 'Hello! How can AI help with data analysis?',
      timestamp: new Date(Date.now() - 5000),
    },
    {
      id: '2', 
      role: 'assistant' as const,
      content: 'AI can help with data analysis in many ways:\\n\\n1. **Pattern Recognition**: Identify trends and correlations in large datasets\\n2. **Predictive Analytics**: Forecast future outcomes based on historical data\\n3. **Data Cleaning**: Automatically detect and fix inconsistencies\\n4. **Visualization**: Generate insightful charts and dashboards\\n\\nWhat specific data analysis challenge are you working on?',
      timestamp: new Date(Date.now() - 3000),
      responseTime: 1247,
    },
    {
      id: '3',
      role: 'user' as const,
      content: 'That\\'s very helpful! Can you explain machine learning algorithms?',
      timestamp: new Date(Date.now() - 1000),
    }
  ];

  const emptyMessages: any[] = [];

  const [messages, setMessages] = useState(mockMessages);

  return (
    <div className="space-y-4 h-96">
      <div className="flex gap-2">
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => setMessages(messages.length ? emptyMessages : mockMessages)}
        >
          {messages.length ? 'Clear Messages' : 'Load Messages'}
        </Button>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={() => setIsTyping(!isTyping)}
        >
          {isTyping ? 'Stop Typing' : 'Start Typing'}
        </Button>
      </div>
      <div className="border rounded-md h-80">
        <ChatContainer messages={messages} isTyping={isTyping} />
      </div>
    </div>
  );
}