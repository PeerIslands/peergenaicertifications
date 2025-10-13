import ChatHeader from "../ChatHeader";

export default function ChatHeaderExample() {
  const handleClearChat = () => {
    console.log("Chat cleared");
  };

  return (
    <div className="bg-background">
      <ChatHeader  onClearChat={handleClearChat} />
    </div>
  );
}
