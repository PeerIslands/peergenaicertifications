export type InsertUser = {
  username: string;
  password: string;
};

export type User = InsertUser & {
  id: string;
};

export type InsertDocument = {
  filename: string;
  originalName: string;
  content: string;
  fileSize: number;
  mimeType: string;
};

export type Document = InsertDocument & {
  id: string;
  uploadedAt: Date;
};

// Question/Answer interface for frontend
export interface ChatMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
}

export interface DocumentSummary {
  id: string;
  filename: string;
  uploadedAt: Date;
  fileSize: number;
}
