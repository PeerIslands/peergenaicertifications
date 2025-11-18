import { Bot, Lightbulb, Code, BookOpen, Zap } from "lucide-react";
import { Card } from "@/components/ui/card";

interface EmptyStateProps {
  onPromptClick: (prompt: string) => void;
}

const SUGGESTED_PROMPTS = [
  {
    icon: BookOpen,
    title: "Attention Mechanism",
    prompt: "What is attention, and why did it replace older sequence models",
  },
  {
    icon: Zap,
    title: "Mercury Models",
    prompt: "What breakthrough performance metrics do the Mercury models achieve on GPUs?",
  },
  {
    icon: Lightbulb,
    title: "SAM 2 Capabilities",
    prompt: "What does SAM 2 let people do with images and videos?",
  },
  {
    icon: Code,
    title: "GAN Technology",
    prompt: "How do GANs make fake images look real?",
  },
];

export default function EmptyState({ onPromptClick }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      <div className="max-w-2xl w-full space-y-8">
        <div className="text-center space-y-3">
          <div className="flex justify-center">
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Bot className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h2 className="text-2xl font-semibold">Start a conversation</h2>
          <p className="text-muted-foreground">
            Ask me anything or try one of these prompts
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {SUGGESTED_PROMPTS.map((item, index) => {
            const Icon = item.icon;
            return (
              <Card
                key={index}
                className="p-4 cursor-pointer hover-elevate active-elevate-2 transition-all"
                onClick={() => onPromptClick(item.prompt)}
                data-testid={`card-prompt-${index}`}
              >
                <div className="flex items-start gap-3">
                  <div className="h-8 w-8 rounded-md bg-primary/10 flex items-center justify-center shrink-0">
                    <Icon className="h-4 w-4 text-primary" />
                  </div>
                  <div className="space-y-1">
                    <h3 className="font-medium text-sm">{item.title}</h3>
                    <p className="text-xs text-muted-foreground">{item.prompt}</p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
