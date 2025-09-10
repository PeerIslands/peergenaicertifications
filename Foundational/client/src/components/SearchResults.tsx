import { Bot, Link, Copy, Bookmark, Share, Clock, FileText, ExternalLink, Search, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface SearchResultsProps {
  query: string;
  response: any; // Changed to any to handle JSON response
  sources: Array<{
    document: string;
    page?: number;
    excerpt: string;
    relevance: number;
  }>;
}

export default function SearchResults({ query, response, sources }: SearchResultsProps) {
  const { toast } = useToast();
  const [selectedSource, setSelectedSource] = useState<{
    document: string;
    page?: number;
    excerpt: string;
    relevance: number;
  } | null>(null);

  const handleCopy = async () => {
    try {
      let textToCopy = response;
      if (typeof response === 'object' && response !== null) {
        if (response.answer) {
          textToCopy = response.answer;
        } else {
          textToCopy = JSON.stringify(response, null, 2);
        }
      }
      await navigator.clipboard.writeText(textToCopy);
      toast({
        title: "Copied to Clipboard",
        description: "The response has been copied to your clipboard.",
      });
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy the response.",
        variant: "destructive",
      });
    }
  };

  const handleSave = () => {
    toast({
      title: "Save Feature",
      description: "Save functionality would be implemented here.",
    });
  };

  const handleShare = () => {
    toast({
      title: "Share Feature", 
      description: "Share functionality would be implemented here.",
    });
  };

  const handleViewFullSection = (source: {
    document: string;
    page?: number;
    excerpt: string;
    relevance: number;
  }) => {
    setSelectedSource(source);
  };

  const handleCopySource = async (source: {
    document: string;
    page?: number;
    excerpt: string;
    relevance: number;
  }) => {
    try {
      const textToCopy = `Document: ${source.document}\nPage: ${source.page || 'N/A'}\nRelevance: ${source.relevance}%\n\nContent:\n${source.excerpt}`;
      await navigator.clipboard.writeText(textToCopy);
      toast({
        title: "Copied to Clipboard",
        description: "The source content has been copied to your clipboard.",
      });
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy the source content.",
        variant: "destructive",
      });
    }
  };

  const getRelevanceBadge = (relevance: number) => {
    if (relevance >= 90) {
      return <Badge className="bg-primary text-primary-foreground">{relevance}% match</Badge>;
    } else if (relevance >= 70) {
      return <Badge className="bg-yellow-500 text-white">{relevance}% match</Badge>;
    } else {
      return <Badge variant="secondary">{relevance}% match</Badge>;
    }
  };

  return (
    <div className="max-w-4xl" data-testid="search-results">
      {/* AI Response Card */}
      <div className="bg-card rounded-xl border border-border shadow-sm mb-6" data-testid="ai-response-card">
        <div className="p-6">
          <div className="flex items-start space-x-3 mb-4">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
              <Bot className="text-primary-foreground w-4 h-4" />
            </div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <h3 className="text-lg font-semibold text-foreground">AI Response</h3>
                <Badge className="bg-accent text-accent-foreground">Generated</Badge>
              </div>
              <div className="prose prose-slate max-w-none" data-testid="ai-response-content">
                {typeof response === 'object' && response !== null ? (
                  <div className="space-y-4">
                    {/* Main Answer */}
                    {response.answer && (
                      <div className="text-foreground leading-relaxed">
                        <h4 className="font-semibold text-lg mb-2">Answer:</h4>
                        <div className="whitespace-pre-wrap">{response.answer}</div>
                      </div>
                    )}
                    
                    {/* Confidence Level */}
                    {response.confidence && (
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">Confidence:</span>
                        <Badge 
                          variant={response.confidence === 'high' ? 'default' : 
                                  response.confidence === 'medium' ? 'secondary' : 'destructive'}
                        >
                          {response.confidence}
                        </Badge>
                      </div>
                    )}
                    
                    {/* Sources Used */}
                    {response.sources_used && response.sources_used.length > 0 && (
                      <div>
                        <h4 className="font-semibold mb-2">Sources Used:</h4>
                        <div className="flex flex-wrap gap-2">
                          {response.sources_used.map((source: string, index: number) => (
                            <Badge key={index} variant="outline">{source}</Badge>
                          ))}
                        </div>
                      </div>
                    )}
                    
                    {/* Additional Notes */}
                    {response.additional_notes && (
                      <div>
                        <h4 className="font-semibold mb-2">Additional Notes:</h4>
                        <div className="text-muted-foreground whitespace-pre-wrap">{response.additional_notes}</div>
                      </div>
                    )}
                    
                    {/* Fallback for other response types */}
                    {!response.answer && (
                      <div className="text-foreground leading-relaxed whitespace-pre-wrap">
                        {JSON.stringify(response, null, 2)}
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-foreground leading-relaxed whitespace-pre-wrap">
                    {response}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Source Attribution */}
          {sources.length > 0 && (
            <div className="border-t border-border pt-4">
              <h4 className="text-sm font-semibold text-foreground mb-3 flex items-center">
                <Link className="text-secondary mr-2 w-4 h-4" />
                Sources Referenced
              </h4>
              <div className="grid gap-3 sm:grid-cols-2" data-testid="source-list">
                {sources.map((source, index) => (
                  <div 
                    key={index} 
                    className="bg-muted rounded-lg p-3 border border-border hover:bg-muted/80 transition-colors cursor-pointer"
                    onClick={() => handleViewFullSection(source)}
                    data-testid={`source-${index}`}
                  >
                    <div className="flex items-center space-x-2 mb-2">
                      <FileText className="text-red-500 w-4 h-4" />
                      <span 
                        className="text-sm font-medium text-foreground truncate flex-1"
                        title={source.document}
                        data-testid={`text-source-document-${index}`}
                      >
                        {source.document}
                      </span>
                    </div>
                    <p 
                      className="text-xs text-secondary mb-2 line-clamp-2"
                      data-testid={`text-source-excerpt-${index}`}
                    >
                      "{source.excerpt}"
                    </p>
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-secondary" data-testid={`text-source-page-${index}`}>
                        {source.page ? `Page ${source.page}` : 'Page N/A'}
                      </span>
                      <div className="flex items-center space-x-2">
                        {getRelevanceBadge(source.relevance)}
                        <ExternalLink className="w-3 h-3 text-muted-foreground" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="border-t border-border pt-4 mt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCopy}
                  className="text-secondary hover:text-foreground transition-colors"
                  data-testid="button-copy-response"
                >
                  <Copy className="w-4 h-4 mr-1" />
                  <span className="text-sm">Copy</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleSave}
                  className="text-secondary hover:text-foreground transition-colors"
                  data-testid="button-save-response"
                >
                  <Bookmark className="w-4 h-4 mr-1" />
                  <span className="text-sm">Save</span>
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleShare}
                  className="text-secondary hover:text-foreground transition-colors"
                  data-testid="button-share-response"
                >
                  <Share className="w-4 h-4 mr-1" />
                  <span className="text-sm">Share</span>
                </Button>
              </div>
              <div className="flex items-center space-x-2 text-xs text-secondary">
                <Clock className="w-4 h-4" />
                <span data-testid="text-response-timestamp">Just now</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Related Documents */}
      {sources.length > 0 && (
        <div className="bg-card rounded-xl border border-border shadow-sm" data-testid="related-documents">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
              <Search className="text-primary mr-2 w-5 h-5" />
              Related Document Sections
            </h3>
            
            <div className="space-y-4">
              {sources.map((source, index) => (
                <div 
                  key={index}
                  className="border border-border rounded-lg p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                  data-testid={`related-section-${index}`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <FileText className="text-red-500 w-4 h-4" />
                      <span className="text-sm font-medium text-foreground" data-testid={`text-related-document-${index}`}>
                        {source.document}
                      </span>
                      <Badge variant="secondary" data-testid={`text-related-page-${index}`}>
                        {source.page ? `Page ${source.page}` : 'Page N/A'}
                      </Badge>
                    </div>
                    {getRelevanceBadge(source.relevance)}
                  </div>
                  <p className="text-sm text-secondary leading-relaxed" data-testid={`text-related-excerpt-${index}`}>
                    {source.excerpt}
                  </p>
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-border">
                    <span className="text-xs text-secondary">Relevant Section</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-primary hover:text-primary/80 text-xs font-medium"
                      onClick={() => handleViewFullSection(source)}
                      data-testid={`button-view-section-${index}`}
                    >
                      View Full Section <ExternalLink className="w-3 h-3 ml-1" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Full Section Dialog */}
      <Dialog open={!!selectedSource} onOpenChange={() => setSelectedSource(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <DialogTitle className="flex items-center space-x-2">
                <FileText className="w-5 h-5 text-primary" />
                <span>Full Section Content</span>
              </DialogTitle>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedSource(null)}
                className="h-8 w-8 p-0"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
            <DialogDescription>
              Complete content from the selected source
            </DialogDescription>
          </DialogHeader>
          
          {selectedSource && (
            <div className="flex-1 overflow-auto space-y-4">
              {/* Source Info */}
              <div className="bg-muted rounded-lg p-4 space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <FileText className="w-4 h-4 text-red-500" />
                    <span className="font-medium">{selectedSource.document}</span>
                    <Badge variant="secondary">
                      {selectedSource.page ? `Page ${selectedSource.page}` : 'Page N/A'}
                    </Badge>
                  </div>
                  {getRelevanceBadge(selectedSource.relevance)}
                </div>
              </div>

              {/* Full Content */}
              <div className="bg-background border rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h4 className="font-semibold">Content:</h4>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleCopySource(selectedSource)}
                    className="text-secondary hover:text-foreground"
                  >
                    <Copy className="w-4 h-4 mr-1" />
                    Copy
                  </Button>
                </div>
                <div className="prose prose-slate max-w-none text-sm leading-relaxed whitespace-pre-wrap">
                  {selectedSource.excerpt}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
