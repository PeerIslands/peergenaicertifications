// This file contains OpenAI integration utilities
// The actual API calls are handled on the backend for security

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  timestamp?: Date;
  fileContext?: string[];
}

export interface ChatResponse {
  response: string;
  hasFileContext: boolean;
}

// Client-side utilities for handling chat data
export const formatChatMessage = (message: ChatMessage): string => {
  return message.content;
};

export const isValidMessage = (content: string): boolean => {
  return content.trim().length > 0 && content.trim().length <= 4000;
};

export const sanitizeMessage = (content: string): string => {
  return content.trim().substring(0, 4000);
};
