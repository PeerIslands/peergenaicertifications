import { ChatSidebar } from "../ChatSidebar";

export default function ChatSidebarExample() {
  const conversations = [
    {
      id: "1",
      title: "AI Healthcare Research",
      timestamp: new Date(Date.now() - 86400000),
      isActive: true,
    },
    {
      id: "2",
      title: "Machine Learning Basics",
      timestamp: new Date(Date.now() - 172800000),
    },
  ];

  const documents = [
    { id: "1", name: "AI_Healthcare_2024.pdf" },
    { id: "2", name: "ML_Tutorial.pdf" },
  ];

  return (
    <div className="h-[600px] w-80 bg-background">
      <ChatSidebar
        conversations={conversations}
        documents={documents}
        onNewChat={() => console.log("New chat")}
        onSelectConversation={(id) => console.log("Select conversation:", id)}
      />
    </div>
  );
}
