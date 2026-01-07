import { useState, useCallback } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Upload, MessageSquare, Play, RotateCcw, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { queryClient, apiRequest } from "@/lib/queryClient";
import { chunkText } from "@/lib/chunking";
import Header from "@/components/Header";
import UploadZone from "@/components/UploadZone";
import ProcessingPipeline from "@/components/ProcessingPipeline";
import ChatInterface from "@/components/ChatInterface";
import ContextPanel from "@/components/ContextPanel";
import DocumentSidebar from "@/components/DocumentSidebar";
import type { Document, Message, RetrievedChunk, ChunkSettings } from "@shared/schema";

interface UploadedFile {
  name: string;
  size: number;
  pages: number;
  file?: File;
}

export default function Home() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState("upload");
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isProcessed, setIsProcessed] = useState(false);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | null>(null);
  const [chunkSettings, setChunkSettings] = useState<ChunkSettings>({ 
    chunkSize: 500, 
    overlap: 50 
  });
  const [messages, setMessages] = useState<Message[]>([]);
  const [retrievedChunks, setRetrievedChunks] = useState<RetrievedChunk[]>([]);
  const [highlightedChunkId, setHighlightedChunkId] = useState<string | null>(null);
  const [extractedChunks, setExtractedChunks] = useState<string[]>([]);

  // Fetch documents
  const { data: documents = [] } = useQuery<Document[]>({
    queryKey: ["/api/documents"],
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: async ({ file, settings }: { file: File; settings: ChunkSettings }) => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("chunkSize", settings.chunkSize.toString());
      formData.append("overlap", settings.overlap.toString());

      const response = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Upload failed");
      }

      return response.json();
    },
    onSuccess: (document) => {
      queryClient.invalidateQueries({ queryKey: ["/api/documents"] });
      setSelectedDocumentId(document.id);
      setIsProcessing(false);
      setIsProcessed(true);
      toast({
        title: "Document processed",
        description: `${document.name} has been chunked and vectorized.`,
      });
      // Don't automatically redirect - user will click "Start Chatting" button
      setMessages([]);
      setRetrievedChunks([]);
    },
    onError: (error: Error) => {
      setIsProcessing(false);
      toast({
        title: "Processing failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: async (content: string) => {
      const response = await apiRequest("POST", "/api/chat", {
        content,
        documentId: selectedDocumentId,
      });
      return response.json();
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, data.userMessage, data.assistantMessage]);
      setRetrievedChunks(data.retrievedChunks);
    },
    onError: (error: Error) => {
      toast({
        title: "Chat failed",
        description: error.message,
        variant: "destructive",
      });
    },
  });

  // Delete document mutation
  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const response = await apiRequest("DELETE", `/api/documents/${id}`);
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["/api/documents"] });
      if (selectedDocumentId && documents.length <= 1) {
        setSelectedDocumentId(null);
      } else if (selectedDocumentId) {
        setSelectedDocumentId(documents.find(d => d.id !== selectedDocumentId)?.id || null);
      }
    },
  });

  const handleFileUpload = useCallback((file: UploadedFile & { file?: File }) => {
    setUploadedFile(file);
    setIsProcessed(false);
  }, []);

  const handleStartProcessing = useCallback(async () => {
    if (!uploadedFile?.file) return;
    setIsProcessing(true);
    
    // Extract text from PDF and chunk it
    try {
      const reader = new FileReader();
      reader.onload = async (e) => {
        try {
          const arrayBuffer = e.target?.result as ArrayBuffer;
          const response = await fetch("/api/extract-text", {
            method: "POST",
            headers: { "Content-Type": "application/octet-stream" },
            body: arrayBuffer,
          });
          
          if (response.ok) {
            const data = await response.json();
            const chunks = chunkText(data.text, chunkSettings.chunkSize, chunkSettings.overlap);
            setExtractedChunks(chunks.map(c => c.content));
          }
        } catch (error) {
          console.error("Failed to extract text:", error);
        }
      };
      reader.readAsArrayBuffer(uploadedFile.file);
    } catch (error) {
      console.error("Failed to process file:", error);
    }
  }, [uploadedFile, chunkSettings]);

  const handleProcessingComplete = useCallback(() => {
    if (uploadedFile?.file) {
      uploadMutation.mutate({ file: uploadedFile.file, settings: chunkSettings });
    }
  }, [uploadedFile, chunkSettings, uploadMutation]);

  const handleReset = useCallback(() => {
    setUploadedFile(null);
    setIsProcessing(false);
    setIsProcessed(false);
  }, []);

  const handleRemoveDocument = useCallback((id: string) => {
    deleteMutation.mutate(id);
  }, [deleteMutation]);

  const handleSendMessage = useCallback((message: string) => {
    if (!selectedDocumentId) {
      toast({
        title: "No document selected",
        description: "Please select a document to chat with.",
        variant: "destructive",
      });
      return;
    }
    chatMutation.mutate(message);
  }, [selectedDocumentId, chatMutation, toast]);

  const handleClearChat = useCallback(async () => {
    try {
      await apiRequest("DELETE", "/api/messages");
      setMessages([]);
      setRetrievedChunks([]);
    } catch (error) {
      console.error("Failed to clear chat:", error);
    }
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />
      
      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="h-full">
          <div className="flex items-center justify-between mb-6 gap-4 flex-wrap">
            <TabsList>
              <TabsTrigger value="upload" className="gap-2" data-testid="tab-upload">
                <Upload className="w-4 h-4" />
                Upload & Process
              </TabsTrigger>
              <TabsTrigger 
                value="chat" 
                className="gap-2" 
                disabled={documents.length === 0}
                data-testid="tab-chat"
              >
                <MessageSquare className="w-4 h-4" />
                Chat
              </TabsTrigger>
            </TabsList>

            {activeTab === "upload" && uploadedFile && !isProcessing && (
              <div className="flex items-center gap-2">
                {isProcessed ? (
                  <>
                    <Button variant="outline" onClick={handleReset} data-testid="button-reset">
                      <RotateCcw className="w-4 h-4 mr-2" />
                      Upload Another
                    </Button>
                    <Button onClick={() => setActiveTab("chat")} data-testid="button-go-to-chat">
                      <MessageSquare className="w-4 h-4 mr-2" />
                      Start Chatting
                    </Button>
                  </>
                ) : (
                  <Button 
                    onClick={handleStartProcessing} 
                    disabled={!uploadedFile.file}
                    data-testid="button-start-processing"
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start Processing
                  </Button>
                )}
              </div>
            )}

            {activeTab === "upload" && isProcessing && (
              <div className="flex items-center gap-2 text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Processing document...</span>
              </div>
            )}
          </div>

          <TabsContent value="upload" className="mt-0">
            <div className="grid lg:grid-cols-5 gap-6">
              <div className="lg:col-span-2">
                <h2 className="text-lg font-semibold mb-4">Upload PDF</h2>
                <UploadZone 
                  onFileUpload={handleFileUpload} 
                  uploadedFile={uploadedFile}
                />
              </div>
              
              <div className="lg:col-span-3">
                <h2 className="text-lg font-semibold mb-4">Processing Pipeline</h2>
                <ProcessingPipeline 
                  isProcessing={isProcessing}
                  onProcessingComplete={handleProcessingComplete}
                  chunks={extractedChunks}
                  chunkSize={chunkSettings.chunkSize}
                  overlap={chunkSettings.overlap}
                />
              </div>
            </div>
          </TabsContent>

          <TabsContent value="chat" className="mt-0 h-[calc(100vh-16rem)]">
            <div className="grid lg:grid-cols-12 gap-6 h-full">
              <div className="lg:col-span-2 hidden lg:block">
                <div className="h-full border rounded-lg overflow-hidden">
                  <DocumentSidebar
                    documents={documents}
                    selectedDocumentId={selectedDocumentId}
                    onSelectDocument={setSelectedDocumentId}
                    onRemoveDocument={handleRemoveDocument}
                  />
                </div>
              </div>
              
              <div className="lg:col-span-7 h-full">
                <div className="h-full border rounded-lg overflow-hidden bg-card">
                  <ChatInterface 
                    messages={messages}
                    isLoading={chatMutation.isPending}
                    onSendMessage={handleSendMessage}
                    onClearChat={handleClearChat}
                  />
                </div>
              </div>
              
              <div className="lg:col-span-3 hidden lg:block">
                <div className="h-full border rounded-lg overflow-hidden">
                  <ContextPanel
                    chunks={retrievedChunks}
                    highlightedChunkId={highlightedChunkId}
                    onChunkClick={setHighlightedChunkId}
                  />
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
