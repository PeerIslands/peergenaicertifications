import { useState, useEffect } from "react";
import { Scissors, Cpu, Database, Check, Loader2, ChevronDown, ChevronUp } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";

interface ProcessingStage {
  id: string;
  name: string;
  description: string;
  status: "pending" | "processing" | "completed";
  progress: number;
  details?: Record<string, string | number>;
  samples?: string[];
}

interface ProcessingPipelineProps {
  isProcessing?: boolean;
  onProcessingComplete?: () => void;
  chunks?: string[];
  chunkSize?: number;
  overlap?: number;
}

export default function ProcessingPipeline({ 
  isProcessing = false, 
  onProcessingComplete,
  chunks = [],
  chunkSize = 500,
  overlap = 50,
}: ProcessingPipelineProps) {
  const [stages, setStages] = useState<ProcessingStage[]>([
    {
      id: "chunking",
      name: "Text Chunking",
      description: "Splitting document into semantic chunks",
      status: "pending",
      progress: 0,
      details: { chunkSize, overlap, totalChunks: 0 },
      samples: [],
    },
    {
      id: "vectorizing",
      name: "Vectorization",
      description: "Converting chunks to embeddings",
      status: "pending",
      progress: 0,
      details: { dimensions: 1536, model: "Gemini", vectorCount: 0 },
      samples: [],
    },
    {
      id: "storing",
      name: "Database Storage",
      description: "Storing vectors in memory database",
      status: "pending",
      progress: 0,
      details: { storedVectors: 0, indexType: "cosine" },
      samples: [],
    },
  ]);

  const [expandedStage, setExpandedStage] = useState<string | null>("chunking");

  useEffect(() => {
    if (!isProcessing) return;

    let currentStage = 0;
    const stageTimers: NodeJS.Timeout[] = [];

    const processStage = (stageIndex: number) => {
      if (stageIndex >= stages.length) {
        onProcessingComplete?.();
        return;
      }

      setStages(prev => prev.map((s, i) => 
        i === stageIndex ? { ...s, status: "processing" as const } : s
      ));
      setExpandedStage(stages[stageIndex].id);

      let progress = 0;
      const progressInterval = setInterval(() => {
        progress += Math.random() * 15 + 5;
        if (progress >= 100) {
          progress = 100;
          clearInterval(progressInterval);
          
          setStages(prev => prev.map((s, i) => {
            if (i === stageIndex) {
              const updates: Partial<ProcessingStage> = { 
                status: "completed" as const, 
                progress: 100 
              };
              
              if (stageIndex === 0) {
                updates.details = { ...s.details, totalChunks: chunks.length };
                updates.samples = chunks; // Show all chunks, not just 4
              } else if (stageIndex === 1) {
                updates.details = { ...s.details, vectorCount: chunks.length };
              } else {
                updates.details = { ...s.details, storedVectors: chunks.length };
              }
              
              return { ...s, ...updates };
            }
            return s;
          }));

          setTimeout(() => processStage(stageIndex + 1), 300);
        } else {
          setStages(prev => prev.map((s, i) => 
            i === stageIndex ? { ...s, progress } : s
          ));
        }
      }, 100);

      stageTimers.push(progressInterval as unknown as NodeJS.Timeout);
    };

    const startTimer = setTimeout(() => processStage(0), 500);
    stageTimers.push(startTimer);

    return () => {
      stageTimers.forEach(timer => clearTimeout(timer));
    };
  }, [isProcessing, chunks]);

  const getStageIcon = (stage: ProcessingStage) => {
    const icons = {
      chunking: Scissors,
      vectorizing: Cpu,
      storing: Database,
    };
    return icons[stage.id as keyof typeof icons] || Scissors;
  };

  // Component for individual chunk with collapse/expand
  const ChunkItem = ({ chunk, index }: { chunk: string; index: number }) => {
    const [isChunkExpanded, setIsChunkExpanded] = useState(false);
    const lines = chunk.split('\n').filter(line => line.trim().length > 0);
    const previewLines = lines.slice(0, 2);
    const previewText = previewLines.join('\n');
    const hasMore = lines.length > 2 || chunk.length > (previewText.length + 50);
    
    return (
      <Collapsible 
        open={isChunkExpanded} 
        onOpenChange={setIsChunkExpanded}
      >
        <div 
          className="p-3 bg-background rounded-lg border border-border"
          data-testid={`text-sample-chunk-${index}`}
        >
          <div className="flex items-start gap-2">
            <div className="flex-1 min-w-0">
              {isChunkExpanded ? (
                <div className="text-sm font-mono text-muted-foreground whitespace-pre-wrap break-words">
                  {chunk}
                </div>
              ) : (
                <div className="text-sm font-mono text-muted-foreground break-words">
                  {previewText || chunk.substring(0, 200)}
                  {hasMore && (
                    <span className="text-muted-foreground/60 italic">
                      {' '}...
                    </span>
                  )}
                </div>
              )}
              {hasMore && (
                <div className="mt-2">
                  <CollapsibleTrigger asChild>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 text-xs"
                    >
                      {isChunkExpanded ? (
                        <>
                          <ChevronUp className="w-3 h-3 mr-1" />
                          Show Less
                        </>
                      ) : (
                        <>
                          <ChevronDown className="w-3 h-3 mr-1" />
                          Show More
                        </>
                      )}
                    </Button>
                  </CollapsibleTrigger>
                </div>
              )}
            </div>
            <Badge variant="outline" className="text-xs shrink-0">
              #{index + 1}
            </Badge>
          </div>
        </div>
      </Collapsible>
    );
  };

  const getStatusBadge = (status: ProcessingStage["status"]) => {
    switch (status) {
      case "completed":
        return <Badge className="bg-green-500/10 text-green-600 dark:text-green-400 border-0"><Check className="w-3 h-3 mr-1" />Complete</Badge>;
      case "processing":
        return <Badge className="bg-primary/10 text-primary border-0"><Loader2 className="w-3 h-3 mr-1 animate-spin" />Processing</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
    }
  };

  return (
    <div className="space-y-4">
      {stages.map((stage, index) => {
        const Icon = getStageIcon(stage);
        const isExpanded = expandedStage === stage.id;
        
        return (
          <Card key={stage.id} className="overflow-visible" data-testid={`card-stage-${stage.id}`}>
            <div className="p-4">
              <div className="flex items-start gap-4">
                <div className="relative flex-shrink-0">
                  <div className={`
                    w-10 h-10 rounded-full flex items-center justify-center transition-colors
                    ${stage.status === "completed" ? "bg-green-500/10" : 
                      stage.status === "processing" ? "bg-primary/10" : "bg-muted"}
                  `}>
                    <Icon className={`w-5 h-5 ${
                      stage.status === "completed" ? "text-green-600 dark:text-green-400" : 
                      stage.status === "processing" ? "text-primary" : "text-muted-foreground"
                    }`} />
                  </div>
                  {index < stages.length - 1 && (
                    <div className={`
                      absolute top-10 left-1/2 w-0.5 h-8 -translate-x-1/2
                      ${stage.status === "completed" ? "bg-green-500" : "bg-border"}
                    `} />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-4 mb-1">
                    <h3 className="font-medium">{stage.name}</h3>
                    {getStatusBadge(stage.status)}
                  </div>
                  <p className="text-sm text-muted-foreground mb-3">{stage.description}</p>

                  {stage.status === "processing" && (
                    <div className="space-y-2">
                      <Progress value={stage.progress} className="h-2" />
                      <p className="text-xs text-muted-foreground">{Math.round(stage.progress)}% complete</p>
                    </div>
                  )}

                  {stage.status === "completed" && stage.details && (
                    <div className="flex flex-wrap gap-2 mt-2">
                      {Object.entries(stage.details).map(([key, value]) => (
                        <Badge key={key} variant="secondary" className="text-xs">
                          {key.replace(/([A-Z])/g, ' $1').trim()}: {value}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>

                {stage.samples && stage.samples.length > 0 && (
                  <Button
                    size="icon"
                    variant="ghost"
                    onClick={() => setExpandedStage(isExpanded ? null : stage.id)}
                    data-testid={`button-expand-${stage.id}`}
                  >
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                )}
              </div>
            </div>

            {isExpanded && stage.samples && stage.samples.length > 0 && (
              <div className="border-t bg-muted/30 p-4">
                <p className="text-sm font-medium mb-3">
                  All Chunks ({stage.samples.length})
                </p>
                <ScrollArea className="h-[400px]">
                  <div className="space-y-2 pr-4">
                    {stage.samples.map((sample, i) => (
                      <ChunkItem key={i} chunk={sample} index={i} />
                    ))}
                  </div>
                </ScrollArea>
              </div>
            )}
          </Card>
        );
      })}
    </div>
  );
}
