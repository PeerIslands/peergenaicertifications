import { ChatMessage } from "../ChatMessage";

export default function ChatMessageExample() {
  const messages = [
    {
      id: "1",
      role: "user" as const,
      content: "What is the main topic of this document?",
      timestamp: new Date(Date.now() - 300000),
    },
    {
      id: "2",
      role: "assistant" as const,
      content: "Based on the PDF you uploaded, the main topic is artificial intelligence and machine learning applications in healthcare. The document discusses various AI techniques used for medical diagnosis and treatment planning.",
      timestamp: new Date(Date.now() - 240000),
    },
    {
      id: "3",
      role: "system" as const,
      content: "PDF 'AI_Healthcare_2024.pdf' has been processed successfully",
      timestamp: new Date(Date.now() - 180000),
    },
  ];

  return (
    <div className="p-4 bg-background space-y-4">
      {messages.map((msg) => (
        <ChatMessage key={msg.id} message={msg} />
      ))}
    </div>
  );
}
