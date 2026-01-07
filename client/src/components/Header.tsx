import { FileText, Settings, HelpCircle, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";

export default function Header() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [isDark]);

  return (
    <header className="h-16 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="h-full max-w-7xl mx-auto px-6 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
            <FileText className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold tracking-tight" data-testid="text-app-title">RAG Explorer</h1>
            <p className="text-xs text-muted-foreground">PDF Document Intelligence</p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <Button
            size="icon"
            variant="ghost"
            onClick={() => setIsDark(!isDark)}
            data-testid="button-theme-toggle"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </Button>
          <Button size="icon" variant="ghost" data-testid="button-settings">
            <Settings className="w-4 h-4" />
          </Button>
          <Button size="icon" variant="ghost" data-testid="button-help">
            <HelpCircle className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
