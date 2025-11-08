import { useState } from "react";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Sidebar } from "@/components/sidebar/sidebar";
import { ChatArea } from "@/components/chat/chat-area";
import { useIsMobile } from "@/hooks/use-mobile";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const isMobile = useIsMobile();

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const closeSidebar = () => {
    setSidebarOpen(false);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      <Sidebar isOpen={sidebarOpen || !isMobile} onClose={closeSidebar} />
      
      <div className="flex-1 flex flex-col">
        {/* Chat Header */}
        <header className="flex items-center justify-between p-4 border-b border-border bg-background">
          <div className="flex items-center gap-3">
            {isMobile && (
              <Button
                variant="ghost"
                size="sm"
                onClick={toggleSidebar}
                data-testid="menu-toggle"
              >
                <Menu className="w-4 h-4" />
              </Button>
            )}
            <h1 className="text-lg font-semibold text-foreground">
              Chat with your PDFs
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground hidden sm:block">
              Powered by OpenAI GPT
            </span>
            <div className="w-2 h-2 bg-primary rounded-full"></div>
          </div>
        </header>

        {/* Chat Area */}
        <ChatArea />
      </div>
    </div>
  );
}
