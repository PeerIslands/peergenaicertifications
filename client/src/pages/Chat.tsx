import { useState, useEffect } from "react";
import { ChatMessage, type Message } from "@/components/ChatMessage";
import { MessageInput } from "@/components/MessageInput";
import { PDFUpload } from "@/components/PDFUpload";
import { ChatSidebar } from "@/components/ChatSidebar";
import { TypingIndicator } from "@/components/TypingIndicator";
import { ThemeToggle } from "@/components/ThemeToggle";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ChatAPI, type Document, type Conversation } from "@/lib/api";

export default function Chat() {
  const [showUpload, setShowUpload] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [loading, setLoading] = useState(true);
  
  // State for real data
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);

  // Load initial data
  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [conversationsData, documentsData] = await Promise.all([
        ChatAPI.getConversations(),
        ChatAPI.getDocuments(),
      ]);
      
      setConversations(conversationsData);
      setDocuments(documentsData);
      
      // If there are conversations, load the first one
      if (conversationsData.length > 0) {
        await selectConversation(conversationsData[0]._id!);
      }
    } catch (error) {
      console.error('Error loading initial data:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = async (conversationId: string) => {
    try {
      const messagesData = await ChatAPI.getMessages(conversationId);
      setMessages(messagesData);
      setCurrentConversationId(conversationId);
      
      // Update active conversation
      setConversations(prev => 
        prev.map(conv => ({
          ...conv,
          isActive: conv._id === conversationId
        }))
      );
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!currentConversationId) {
      console.error('No active conversation');
      return;
    }

    const userMessage: Message = {
      _id: Date.now().toString(),
      conversationId: currentConversationId,
      role: "user",
      content,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setIsTyping(true);

    try {
      const response = await ChatAPI.sendMessage(currentConversationId, content);
      setMessages(prev => [...prev, response.aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage: Message = {
        _id: (Date.now() + 1).toString(),
        conversationId: currentConversationId,
        role: "system",
        content: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleUploadComplete = async (files: Array<{ id: string; name: string; size: number }>) => {
    try {
      // Create a new conversation for the uploaded PDF
      const conversation = await ChatAPI.createConversation(
        `Chat about ${files[0].name}`,
        files[0].id
      );
      
      setConversations(prev => [conversation, ...prev]);
      
      // Select the new conversation
      await selectConversation(conversation._id!);
      
      // Add system message
      const systemMessage: Message = {
        _id: Date.now().toString(),
        conversationId: conversation._id!,
        role: "system",
        content: `PDF '${files[0].name}' has been uploaded and is being processed. You can start asking questions about it.`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, systemMessage]);
      
      // Refresh documents list
      const documentsData = await ChatAPI.getDocuments();
      setDocuments(documentsData);
    } catch (error) {
      console.error('Error handling upload:', error);
    }
  };

  const handleNewChat = async () => {
    try {
      const conversation = await ChatAPI.createConversation("New Chat");
      setConversations(prev => [conversation, ...prev]);
      await selectConversation(conversation._id!);
    } catch (error) {
      console.error('Error creating new chat:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen w-full bg-background items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen w-full bg-background">
      <div className="w-80 shrink-0">
        <ChatSidebar
          conversations={conversations}
          documents={documents}
          onNewChat={handleNewChat}
          onSelectConversation={selectConversation}
        />
      </div>

      <div className="flex-1 flex flex-col">
        <header className="flex items-center justify-between px-6 py-3 border-b border-border">
          <h1 className="text-lg font-semibold">PDF Chat Assistant</h1>
          <ThemeToggle />
        </header>

        <ScrollArea className="flex-1 px-6 py-4">
          <div className="max-w-4xl mx-auto">
            {messages.map((message) => (
              <ChatMessage key={message._id} message={message} />
            ))}
            {isTyping && <TypingIndicator />}
          </div>
        </ScrollArea>

        <MessageInput
          onSendMessage={handleSendMessage}
          onUploadClick={() => setShowUpload(true)}
          disabled={isTyping || !currentConversationId}
        />
      </div>

      <Dialog open={showUpload} onOpenChange={setShowUpload}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload PDF Documents</DialogTitle>
          </DialogHeader>
          <PDFUpload
            onUploadComplete={handleUploadComplete}
            onClose={() => setShowUpload(false)}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
