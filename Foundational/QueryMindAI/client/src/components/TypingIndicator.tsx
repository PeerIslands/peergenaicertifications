interface TypingIndicatorProps {
  visible: boolean;
}

/**
 * Component that displays an animated typing indicator when the AI is generating a response.
 * 
 * @param props - Component props
 * @param props.visible - Whether the typing indicator should be visible
 * @returns A React component rendering animated dots and "AI is thinking..." text, or null if not visible
 */
export function TypingIndicator({ visible }: TypingIndicatorProps) {
  if (!visible) return null;

  return (
    <div className="flex items-center space-x-1 p-4" data-testid="typing-indicator">
      <div className="flex space-x-1">
        <div className="h-2 w-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <div className="h-2 w-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <div className="h-2 w-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm text-muted-foreground ml-2">AI is thinking...</span>
    </div>
  );
}