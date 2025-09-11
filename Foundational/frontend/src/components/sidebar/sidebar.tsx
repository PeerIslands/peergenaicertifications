import { useState } from "react";
import { X, Plus, Moon, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";
import { FileUpload } from "./file-upload";
import { FileList } from "./file-list";
import { useTheme } from "@/hooks/use-theme";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useToast } from "@/hooks/use-toast";
import { apiRequest } from "@/lib/queryClient";
import { useIsMobile } from "@/hooks/use-mobile";

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const { theme, toggleTheme } = useTheme();
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const isMobile = useIsMobile();

  const newChatMutation = useMutation({
    mutationFn: async () => {
      const response = await apiRequest("POST", "/api/session");
      return response.json();
    },
    onSuccess: (session: any) => {
      // Redirect to new page 
      window.location.href = `/chat/${session}`;
      queryClient.invalidateQueries({ queryKey: ["/api/messages", session] });
      toast({
        title: "New chat started",
        description: "Chat history has been cleared.",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Failed to start new chat",
        description: error.message || "Please try again.",
        variant: "destructive",
      });
    },
  });

  const handleNewChat = () => {
    newChatMutation.mutate();
  };

  return (
    <>
      {/* Mobile backdrop */}
      {isMobile && isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 md:hidden"
          onClick={onClose}
        />
      )}
      
      <div
        className={`fixed md:relative inset-y-0 left-0 z-50 w-80 bg-muted border-r border-border flex flex-col transition-transform duration-300 ${
          isOpen ? "translate-x-0" : "-translate-x-full md:translate-x-0"
        }`}
        data-testid="sidebar"
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-border">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">AI PDF Assistant</h2>
            {isMobile && (
              <Button
                variant="ghost"
                size="sm"
                onClick={onClose}
                data-testid="close-sidebar"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>

        {/* Theme Toggle */}
        <div className="p-4 border-b border-border">
          <Button
            variant="ghost"
            onClick={toggleTheme}
            className="w-full justify-start gap-3"
            data-testid="theme-toggle"
          >
            {theme === "dark" ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
            <span className="text-sm font-medium">
              {theme === "dark" ? "Light Mode" : "Dark Mode"}
            </span>
          </Button>
        </div>

        {/* File Upload */}
        <FileUpload />

        {/* File List */}
        <FileList />

        {/* New Chat Button */}
        <div className="p-4 border-t border-border">
          <Button
            onClick={handleNewChat}
            disabled={newChatMutation.isPending}
            className="w-full"
            data-testid="new-chat-button"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Chat
          </Button>
        </div>
      </div>
    </>
  );
}
