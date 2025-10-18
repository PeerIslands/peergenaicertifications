import { useState } from "react";
import ParameterControls, { type ChatParameters } from "../ParameterControls";

export default function ParameterControlsExample() {
  const [parameters, setParameters] = useState<ChatParameters>({
    temperature: 0.7,
    topP: 1.0,
    topK: 5,
    maxTokens: 2048,
    frequencyPenalty: 0,
    presencePenalty: 0,
  });

  const handleParametersChange = (newParams: ChatParameters) => {
    console.log("Parameters changed:", newParams);
    setParameters(newParams);
  };

  return (
    <div className="h-screen bg-background">
      <ParameterControls parameters={parameters} onParametersChange={handleParametersChange} />
    </div>
  );
}
