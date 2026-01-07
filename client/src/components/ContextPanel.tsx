import { useState } from "react";
import { FileText, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { RetrievedChunk } from "@shared/schema";

interface ContextPanelProps {
  chunks?: RetrievedChunk[];
  highlightedChunkId?: string | null;
  onChunkClick?: (chunkId: string) => void;
}

export default function ContextPanel({ 
  chunks = [], 
  highlightedChunkId,
  onChunkClick 
}: ContextPanelProps) {
  const [expandedChunks, setExpandedChunks] = useState<Set<string>>(new Set());

  const toggleExpanded = (id: string) => {
    setExpandedChunks(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 0.9) return "bg-green-500/10 text-green-600 dark:text-green-400";
    if (similarity >= 0.7) return "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400";
    return "bg-muted text-muted-foreground";
  };

  if (chunks.length === 0) {
    return (
      <div className="h-full flex flex-col">
        <div className="p-4 border-b">
          <h2 className="font-semibold flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-primary" />
            Retrieved Context
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Relevant chunks will appear here
          </p>
        </div>
        <div className="flex-1 flex items-center justify-center p-4">
          <div className="text-center">
            <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center mx-auto mb-3">
              <FileText className="w-6 h-6 text-muted-foreground" />
            </div>
            <p className="text-sm text-muted-foreground">
              No context retrieved yet
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              Ask a question to see relevant chunks
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b">
        <h2 className="font-semibold flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-primary" />
          Retrieved Context
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          {chunks.length} relevant chunks found
        </p>
      </div>
      
      <ScrollArea className="flex-1">
        <div className="p-4 space-y-3">
          {chunks.map((chunk) => {
            const isExpanded = expandedChunks.has(chunk.id);
            const isHighlighted = highlightedChunkId === chunk.id;
            
            return (
              <Card 
                key={chunk.id} 
                className={`p-3 transition-all cursor-pointer ${
                  isHighlighted ? "ring-2 ring-primary" : ""
                }`}
                onClick={() => onChunkClick?.(chunk.id)}
                data-testid={`card-chunk-${chunk.id}`}
              >
                <div className="flex items-start justify-end gap-2 mb-2">
                  <Badge className={`text-xs ${getSimilarityColor(chunk.similarity)}`}>
                    {(chunk.similarity * 100).toFixed(0)}% match
                  </Badge>
                </div>
                
                <p className={`text-sm font-mono text-muted-foreground ${
                  isExpanded ? "" : "line-clamp-3"
                }`}>
                  {chunk.content}
                </p>
                
                <Button
                  size="sm"
                  variant="ghost"
                  className="w-full mt-2 h-7 text-xs"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleExpanded(chunk.id);
                  }}
                  data-testid={`button-expand-chunk-${chunk.id}`}
                >
                  {isExpanded ? (
                    <>
                      <ChevronUp className="w-3 h-3 mr-1" />
                      Show less
                    </>
                  ) : (
                    <>
                      <ChevronDown className="w-3 h-3 mr-1" />
                      Show more
                    </>
                  )}
                </Button>
              </Card>
            );
          })}
        </div>
      </ScrollArea>
    </div>
  );
}
