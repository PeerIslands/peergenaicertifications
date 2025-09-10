import { Brain, Settings, HelpCircle, User } from "lucide-react";

export default function Header() {
  return (
    <header className="bg-card shadow-sm border-b border-border sticky top-0 z-40" data-testid="header">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <Brain className="text-white w-4 h-4" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-foreground">RAG Intelligence</h1>
              <p className="text-xs text-secondary">Document Search & Analysis</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <button 
              className="text-secondary hover:text-foreground transition-colors"
              data-testid="button-settings"
            >
              <Settings className="w-5 h-5" />
            </button>
            <button 
              className="text-secondary hover:text-foreground transition-colors"
              data-testid="button-help"
            >
              <HelpCircle className="w-5 h-5" />
            </button>
            <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
              <User className="text-secondary w-4 h-4" />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
