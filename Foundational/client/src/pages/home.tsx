import { useState } from "react";
import Header from "@/components/Header";
import DocumentUpload from "@/components/DocumentUpload";
import DocumentList from "@/components/DocumentList";
import SearchInterface from "@/components/SearchInterface";
import SearchResults from "@/components/SearchResults";
import LoadingOverlay from "@/components/LoadingOverlay";
import { useQuery } from "@tanstack/react-query";
import type { Document } from "@shared/schema";

export default function Home() {
  const [searchResults, setSearchResults] = useState<{
    response: string;
    sources: Array<{
      document: string;
      page?: number;
      excerpt: string;
      relevance: number;
    }>;
  } | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [currentQuery, setCurrentQuery] = useState("");

  const { data: documents = [], refetch: refetchDocuments } = useQuery<Document[]>({
    queryKey: ["/api/documents"],
    refetchInterval: (query) => {
      // Only refetch if there are documents in processing state
      const data = query.state.data;
      const hasProcessingDocs = data?.some((doc: Document) => doc.status === 'processing');
      console.log('Documents refetch check:', { 
        hasProcessingDocs, 
        documents: data?.map((d: Document) => ({ id: d.id, status: d.status })) 
      });
      return hasProcessingDocs ? 2000 : false;
    },
  });

  const { data: stats } = useQuery<{
    totalDocuments: number;
    readyDocuments: number;
    processingDocuments: number;
    totalChunks: number;
    totalSize: number;
  }>({
    queryKey: ["/api/stats"],
    refetchInterval: 2000, // Refresh every 2 seconds to show processing updates
  });

  const handleSearch = async (query: string) => {
    setIsSearching(true);
    setCurrentQuery(query);
    
    try {
      const response = await fetch("/api/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || "Search failed");
      }

      const results = await response.json();
      setSearchResults(results);
    } catch (error) {
      console.error("Search failed:", error);
      setSearchResults({
        response: `Sorry, I encountered an error while searching: ${(error as Error).message}`,
        sources: [],
      });
    } finally {
      setIsSearching(false);
    }
  };

  const handleDocumentUploaded = () => {
    refetchDocuments();
  };

  const handleManualRefetch = () => {
    refetchDocuments();
  };

  const handleDocumentDeleted = (documentId: string) => {
    // Refetch documents to update the list
    refetchDocuments();
  };

  return (
    <div className="min-h-screen bg-background font-sans" data-testid="home-page">
      <Header />
      
      <div className="flex max-w-7xl mx-auto">
        <aside className="w-80 bg-card shadow-sm border-r border-border min-h-screen" data-testid="sidebar">
          <div className="p-6">
            <DocumentUpload onDocumentUploaded={handleDocumentUploaded} />
            <DocumentList 
              documents={documents} 
              stats={stats} 
              onManualRefetch={handleManualRefetch}
              onDocumentDeleted={handleDocumentDeleted}
            />
          </div>
        </aside>

        <main className="flex-1 p-6" data-testid="main-content">
          <SearchInterface onSearch={handleSearch} />
          
          {searchResults && (
            <SearchResults 
              query={currentQuery}
              response={searchResults.response}
              sources={searchResults.sources}
            />
          )}
        </main>
      </div>

      {isSearching && <LoadingOverlay />}
    </div>
  );
}
