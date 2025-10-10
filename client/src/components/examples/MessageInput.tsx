import { MessageInput } from "../MessageInput";

export default function MessageInputExample() {
  return (
    <div className="bg-background">
      <MessageInput
        onSendMessage={(msg) => console.log("Send message:", msg)}
        onUploadClick={() => console.log("Upload clicked")}
      />
    </div>
  );
}
