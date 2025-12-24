import { MessageBubble } from '../MessageBubble';

export default function MessageBubbleExample() {
  const userMessage = {
    role: "user" as const,
    content: "What is the capital of France?",
    timestamp: new Date(),
  };

  const assistantMessage = {
    role: "assistant" as const,
    content: "The capital of France is Paris. It's located in the north-central part of the country and is known for its rich history, culture, and landmarks like the Eiffel Tower and Louvre Museum.",
    timestamp: new Date(Date.now() + 2000),
    responseTime: 1247,
  };

  return (
    <div className="space-y-4 max-w-2xl">
      <MessageBubble {...userMessage} />
      <MessageBubble {...assistantMessage} />
    </div>
  );
}