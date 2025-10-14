import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { FileUploadZone } from '@/components/FileUploadZone';
import { DocumentList } from '@/components/DocumentList';
import { ChatInterface } from '@/components/ChatInterface';
import { ThemeToggle } from '@/components/ThemeToggle';
import { FileText, Brain } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { queryClient } from '@/lib/queryClient';
import type { DocumentSummary, ChatMessage } from '@shared/schema';

export function HomePage() {
  const [selectedDocument, setSelectedDocument] = useState<DocumentSummary | null>(null);
  const [globalMode, setGlobalMode] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isChatLoading, setIsChatLoading] = useState(false);
  const { toast } = useToast();

  // Fetch documents from API
  const { data: documents = [], isLoading: documentsLoading } = useQuery({
    queryKey: ['/api/documents'],
    queryFn: async () => {
      const response = await fetch('/api/documents');
      if (!response.ok) {
        throw new Error('Failed to fetch documents');
      }
      return response.json() as Promise<DocumentSummary[]>;
    },
  });

  // Select first document when documents load (only when not in global mode)
  useEffect(() => {
    if (!globalMode && documents.length > 0 && !selectedDocument) {
      setSelectedDocument(documents[0]);
    }
  }, [documents, selectedDocument, globalMode]);

  const handleFileSelect = async (file: File) => {
    //console.log('Uploading file:', file.name);
    setIsUploading(true);
    
    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
      }

      const result = await response.json();
      //console.log('Upload successful:', result);

      // Refresh documents list
      await queryClient.invalidateQueries({ queryKey: ['/api/documents'] });

      // Select the newly uploaded document
      setSelectedDocument({
        id: result.document.id,
        filename: result.document.filename,
        uploadedAt: new Date(result.document.uploadedAt),
        fileSize: result.document.fileSize,
      });
      
      setMessages([]); // Clear messages for new document
      
      toast({
        title: 'Upload successful',
        description: `${file.name} has been uploaded and processed.`,
      });
    } catch (error) {
      console.error('Upload error:', error);
      toast({
        title: 'Upload failed',
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const handleDocumentSelect = (document: DocumentSummary) => {
    setGlobalMode(false);
    setSelectedDocument(document);
    setMessages([]); // Clear messages when switching documents
    // console.log('Document selected:', document.filename);
  };

  const handleDeleteDocument = async (document: DocumentSummary) => {
    const confirmed = window.confirm(`Delete "${document.filename}"? This action cannot be undone.`);
    if (!confirmed) return;

    try {
      const response = await fetch(`/api/documents/${document.id}`, { method: 'DELETE' });
      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || 'Failed to delete document');
      }

      // If the deleted doc is selected, clear selection before refetch
      if (selectedDocument?.id === document.id) {
        setSelectedDocument(null);
        setMessages([]);
      }

      await queryClient.invalidateQueries({ queryKey: ['/api/documents'] });

      toast({
        title: 'Document deleted',
        description: `${document.filename} was removed successfully.`,
      });
    } catch (error) {
      console.error('Delete error:', error);
      toast({
        title: 'Delete failed',
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        variant: 'destructive',
      });
    }
  };

  const handleSendMessage = async (message: string) => {
    if (!globalMode && !selectedDocument) return;

    // console.log('Sending message:', message);
    
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    setIsChatLoading(true);
    
    try {
      const isGlobal = globalMode;
      const url = isGlobal ? '/api/ask-global' : '/api/ask';
      const body = isGlobal
        ? { question: message }
        : { documentId: selectedDocument!.id, question: message };

      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to get answer');
      }

      const result = await response.json();
      
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: result.answer,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, aiMessage]);
      // console.log('Answer received successfully');
    } catch (error) {
      console.error('Question processing error:', error);
      
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        type: 'ai',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: 'Question failed',
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        variant: 'destructive',
      });
    } finally {
      setIsChatLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2">
                <Brain className="w-8 h-8 text-primary" />
                <h1 className="text-2xl font-bold">Document Q&A</h1>
              </div>
              <div className="text-sm text-muted-foreground">
                Upload documents and ask questions using AI
              </div>
            </div>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-200px)]">
          {/* Left Panel - Upload & Documents */}
          <div className="lg:col-span-1 space-y-6 flex flex-col h-full min-h-0">
            <FileUploadZone 
              onFileSelect={handleFileSelect}
              isUploading={isUploading}
            />
            <div className="flex-1 min-h-0">
              <DocumentList
                documents={documents}
                selectedDocumentId={selectedDocument?.id}
                onDocumentSelect={handleDocumentSelect}
                isLoading={documentsLoading}
                onDeleteDocument={handleDeleteDocument}
              />
            </div>
          </div>

          {/* Right Panel - Chat */}
          <div className="lg:col-span-2 h-full">
            {/* Mode switch */}
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-muted-foreground">
                {globalMode ? 'Asking across all documents' : selectedDocument ? `Asking about: ${selectedDocument.filename}` : 'Select a document or switch to global mode'}
              </div>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={globalMode}
                  onChange={(e) => {
                    setGlobalMode(e.target.checked);
                    setMessages([]);
                  }}
                />
                Ask across all documents
              </label>
            </div>

            {globalMode || selectedDocument ? (
              <ChatInterface
                documentName={globalMode ? undefined : selectedDocument?.filename}
                messages={messages}
                onSendMessage={handleSendMessage}
                isLoading={isChatLoading}
              />
            ) : (
              <div className="h-full flex items-center justify-center">
                <div className="text-center space-y-4">
                  <FileText className="w-16 h-16 text-muted-foreground mx-auto" />
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">No Document Selected</h3>
                    <p className="text-muted-foreground">
                      Upload a document or select one from the list to start asking questions
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
