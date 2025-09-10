import { Brain, CheckCircle, Clock, Circle } from "lucide-react";

export default function LoadingOverlay() {
  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center"
      data-testid="loading-overlay"
    >
      <div className="bg-card rounded-xl p-8 max-w-md w-full mx-4 text-center shadow-2xl">
        <div className="mb-6">
          <div className="relative mx-auto w-16 h-16">
            <div className="absolute inset-0 bg-primary rounded-xl opacity-20 animate-pulse"></div>
            <div className="absolute inset-2 bg-primary rounded-lg flex items-center justify-center">
              <Brain className="text-primary-foreground w-6 h-6" />
            </div>
          </div>
        </div>
        
        <h3 className="text-lg font-semibold text-foreground mb-2">Processing Your Query</h3>
        <p className="text-secondary text-sm mb-6">
          Our AI is analyzing your documents and generating a comprehensive response...
        </p>
        
        {/* Progress Steps */}
        <div className="space-y-3 text-left" data-testid="progress-steps">
          <div className="flex items-center space-x-3">
            <CheckCircle className="w-4 h-4 text-accent" />
            <span className="text-sm text-foreground">Vector search completed</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-4 h-4 bg-primary rounded-full animate-pulse" />
            <span className="text-sm text-foreground">Generating AI response...</span>
          </div>
          <div className="flex items-center space-x-3">
            <Circle className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-secondary">Preparing source attribution</span>
          </div>
        </div>
      </div>
    </div>
  );
}
