import { useState } from "react";
import { Search, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface SearchInterfaceProps {
  onSearch: (query: string) => void;
}

const SUGGESTED_QUERIES = [
  "Summarize the main points",
  "What are the key recommendations?", 
  "Find methodology details",
];

export default function SearchInterface({ onSearch }: SearchInterfaceProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim());
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    onSearch(suggestion);
  };

  return (
    <div className="mb-8">
      <div className="max-w-4xl">
        <h2 className="text-2xl font-semibold text-foreground mb-2">
          Intelligent Document Search
        </h2>
        <p className="text-secondary mb-6">
          Ask questions about your documents. Our AI will search through the content and provide contextual answers with source attribution.
        </p>
        
        <form onSubmit={handleSubmit} className="relative mb-4" data-testid="search-form">
          <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
            <Search className="text-secondary w-5 h-5" />
          </div>
          <Input
            type="text"
            placeholder="Ask a question about your documents..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full pl-12 pr-16 py-4 border border-border rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-foreground placeholder-secondary"
            data-testid="input-search-query"
          />
          <Button
            type="submit"
            disabled={!query.trim()}
            className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors flex items-center space-x-2"
            data-testid="button-search"
          >
            <span className="text-sm font-medium">Search</span>
            <ArrowRight className="w-4 h-4" />
          </Button>
        </form>

        <div className="flex flex-wrap gap-2 mb-8">
          <span className="text-xs text-secondary mr-2">Try asking:</span>
          {SUGGESTED_QUERIES.map((suggestion, index) => (
            <Button
              key={index}
              variant="secondary"
              size="sm"
              className="bg-muted hover:bg-muted/80 text-foreground px-3 py-1 rounded-full text-xs transition-colors"
              onClick={() => handleSuggestionClick(suggestion)}
              data-testid={`button-suggestion-${index}`}
            >
              {suggestion}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
