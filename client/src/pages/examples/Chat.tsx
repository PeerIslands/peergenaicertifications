import { ThemeProvider } from "@/components/ThemeProvider";
import Chat from "../Chat";

export default function ChatExample() {
  return (
    <ThemeProvider>
      <Chat />
    </ThemeProvider>
  );
}
