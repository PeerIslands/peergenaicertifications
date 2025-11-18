import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

export interface ChatParameters {
  temperature: number;
  topP: number; // Nucleus sampling parameter
  topK: number; // Number of documents to retrieve
  maxTokens: number;
  frequencyPenalty: number;
  presencePenalty: number;
}

interface ParameterControlsProps {
  parameters: ChatParameters;
  onParametersChange: (parameters: ChatParameters) => void;
}


export default function ParameterControls({ parameters, onParametersChange }: ParameterControlsProps) {
  const updateParameter = <K extends keyof ChatParameters>(key: K, value: ChatParameters[K]) => {
    onParametersChange({ ...parameters, [key]: value });
  };

  return (
    <Card className="border-l-2 border-l-primary h-full overflow-y-auto">
      <CardHeader className="space-y-0 pb-4">
        <CardTitle className="text-sm font-semibold uppercase tracking-wider">
          Model Parameters
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="temperature" className="text-sm font-medium">
              Temperature
            </Label>
            <span className="text-sm font-medium text-muted-foreground" data-testid="text-temperature">
              {parameters.temperature.toFixed(2)}
            </span>
          </div>
          <Slider
            id="temperature"
            min={0}
            max={2}
            step={0.01}
            value={[parameters.temperature]}
            onValueChange={([value]) => updateParameter("temperature", value)}
            data-testid="slider-temperature"
          />
          <p className="text-xs text-muted-foreground">
            Higher values make output more random, lower values more focused
          </p>
        </div>

        <Separator />

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="top-p" className="text-sm font-medium">
              Top-P (Nucleus Sampling)
            </Label>
            <span className="text-sm font-medium text-muted-foreground" data-testid="text-top-p">
              {parameters.topP.toFixed(2)}
            </span>
          </div>
          <Slider
            id="top-p"
            min={0}
            max={1}
            step={0.01}
            value={[parameters.topP]}
            onValueChange={([value]) => updateParameter("topP", value)}
            data-testid="slider-top-p"
          />
          <p className="text-xs text-muted-foreground">
            Controls diversity via nucleus sampling (0.1 = very focused, 1.0 = diverse)
          </p>
        </div>

        <Separator />

        <div className="space-y-2">
          <Label htmlFor="top-k" className="text-sm font-medium">
            Top K Documents
          </Label>
          <Input
            id="top-k"
            type="number"
            min={1}
            max={20}
            value={parameters.topK}
            onChange={(e) => updateParameter("topK", parseInt(e.target.value) || 1)}
            data-testid="input-top-k"
          />
          <p className="text-xs text-muted-foreground">
            Number of most relevant documents to retrieve (1-20)
          </p>
        </div>

        <Separator />

        <div className="space-y-2">
          <Label htmlFor="max-tokens" className="text-sm font-medium">
            Max Tokens
          </Label>
          <Input
            id="max-tokens"
            type="number"
            min={1}
            max={4096}
            value={parameters.maxTokens}
            onChange={(e) => updateParameter("maxTokens", parseInt(e.target.value) || 1)}
            data-testid="input-max-tokens"
          />
          <p className="text-xs text-muted-foreground">
            Maximum length of generated response
          </p>
        </div>

        <Separator />

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="frequency-penalty" className="text-sm font-medium">
              Frequency Penalty
            </Label>
            <span className="text-sm font-medium text-muted-foreground" data-testid="text-frequency-penalty">
              {parameters.frequencyPenalty.toFixed(2)}
            </span>
          </div>
          <Slider
            id="frequency-penalty"
            min={-2}
            max={2}
            step={0.01}
            value={[parameters.frequencyPenalty]}
            onValueChange={([value]) => updateParameter("frequencyPenalty", value)}
            data-testid="slider-frequency-penalty"
          />
          <p className="text-xs text-muted-foreground">
            Reduces repetition of token sequences
          </p>
        </div>

        <Separator />

        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label htmlFor="presence-penalty" className="text-sm font-medium">
              Presence Penalty
            </Label>
            <span className="text-sm font-medium text-muted-foreground" data-testid="text-presence-penalty">
              {parameters.presencePenalty.toFixed(2)}
            </span>
          </div>
          <Slider
            id="presence-penalty"
            min={-2}
            max={2}
            step={0.01}
            value={[parameters.presencePenalty]}
            onValueChange={([value]) => updateParameter("presencePenalty", value)}
            data-testid="slider-presence-penalty"
          />
          <p className="text-xs text-muted-foreground">
            Encourages talking about new topics
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
