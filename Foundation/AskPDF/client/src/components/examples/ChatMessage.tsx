import ChatMessage from "../ChatMessage";

export default function ChatMessageExample() {
  const userMessage = {
    id: "1",
    role: "user" as const,
    content: "What is the capital of France?",
    timestamp: new Date(),
  };

  const assistantMessage = {
    id: "2",
    role: "assistant" as const,
    content: "The capital of France is Paris. It's known for its iconic landmarks like the Eiffel Tower and the Louvre Museum.",
    timestamp: new Date(),
  };

  return (
    <div className="space-y-4 p-4 bg-background">
      <ChatMessage message={userMessage} />
      <ChatMessage message={assistantMessage} />
    </div>
  );
}
