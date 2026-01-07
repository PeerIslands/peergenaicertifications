import ChatInterface from "../ChatInterface";

export default function ChatInterfaceExample() {
  return (
    <div className="h-[500px] border rounded-lg overflow-hidden">
      <ChatInterface
        messages={[
          {
            id: "1",
            role: "user",
            content: "What is machine learning?",
            timestamp: new Date(Date.now() - 60000),
          },
          {
            id: "2",
            role: "assistant",
            content: "Based on the document, machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.",
            timestamp: new Date(Date.now() - 30000),
          },
        ]}
        onSendMessage={(msg) => console.log("Message sent:", msg)}
      />
    </div>
  );
}
