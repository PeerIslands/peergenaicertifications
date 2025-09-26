import { useState, useEffect } from "react";
import { ChatContainer } from "@/components/ChatContainer";
import { ChatInput } from "@/components/ChatInput";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";
import { ThemeToggle } from "@/components/ThemeToggle";
import { Button } from "@/components/ui/button";
import { Trash2, BarChart3, MessageSquare, AlertCircle } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { chatService, type ChatMessage, type AnalyticsData } from "@/lib/chatService";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  responseTime?: number;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [sessionId] = useState(() => crypto.randomUUID());
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData>({
    totalMessages: 0,
    averageResponseTime: 0,
    conversationCount: 0,
    totalResponseTime: 0,
  });

  // Load analytics data
  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        const analyticsData = await chatService.getAnalytics(sessionId);
        setAnalytics(analyticsData);
      } catch (error) {
        console.error('Failed to load analytics:', error);
      }
    };

    if (showAnalytics) {
      loadAnalytics();
    }
  }, [sessionId, showAnalytics, messages]);

  const handleSendMessage = async (content: string) => {
    setError(null);
    setIsTyping(true);

    try {
      // Send message to API
      const response = await chatService.sendMessage(content, sessionId, conversationId || undefined);
      
      // Update conversation ID if this is a new conversation
      if (!conversationId) {
        setConversationId(response.conversationId);
      }

      // Add both user and AI messages to the chat
      setMessages(prev => [
        ...prev,
        {
          id: response.userMessage.id,
          role: response.userMessage.role,
          content: response.userMessage.content,
          timestamp: new Date(response.userMessage.timestamp),
        },
        {
          id: response.aiMessage.id,
          role: response.aiMessage.role,
          content: response.aiMessage.content,
          timestamp: new Date(response.aiMessage.timestamp),
          responseTime: response.aiMessage.responseTime,
        },
      ]);

      console.log('AI response received with response time:', response.aiMessage.responseTime + 'ms');
    } catch (error) {
      console.error('Failed to send message:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
      
      // Add user message even if API call failed
      const userMessage: Message = {
        id: crypto.randomUUID(),
        role: "user",
        content,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleClearHistory = () => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    console.log('Chat history cleared');
  };

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <header className="border-b bg-card px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 bg-primary rounded-md flex items-center justify-center">
              <MessageSquare className="h-4 w-4 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-semibold" data-testid="app-title">AI Chat Assistant</h1>
              <p className="text-sm text-muted-foreground">Powered by   </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowAnalytics(!showAnalytics)}
              data-testid="button-toggle-analytics"
            >
              <BarChart3 className="h-4 w-4 mr-2" />
              {showAnalytics ? 'Hide' : 'Show'} Analytics
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleClearHistory}
              disabled={messages.length === 0}
              data-testid="button-clear-history"
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Clear History
            </Button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div className={`flex flex-col ${showAnalytics ? 'w-2/3' : 'w-full'} transition-all duration-300`}>
          {error && (
            <Alert variant="destructive" className="m-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          <ChatContainer messages={messages} isTyping={isTyping} />
          <ChatInput 
            onSendMessage={handleSendMessage}
            disabled={isTyping}
            placeholder="Ask me anything about AI, technology, or any topic..."
          />
        </div>

        {/* Analytics Sidebar */}
        {showAnalytics && (
          <div className="w-1/3 border-l bg-muted/20 overflow-y-auto transition-all duration-300">
            <AnalyticsDashboard 
              totalMessages={analytics.totalMessages}
              averageResponseTime={analytics.averageResponseTime}
              conversationCount={analytics.conversationCount}
              systemUptime={99.2}
            />
          </div>
        )}
      </div>
    </div>
  );
}