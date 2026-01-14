import { z } from "zod";

// MongoDB User Schema
export const userSchema = z.object({
  _id: z.string().optional(),
  username: z.string().min(1, "Username is required"),
  password: z.string().min(1, "Password is required"),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
});

export const insertUserSchema = userSchema.pick({
  username: true,
  password: true,
});

export type User = z.infer<typeof userSchema>;
export type InsertUser = z.infer<typeof insertUserSchema>;

// MongoDB PDF Document Schema
export const pdfDocumentSchema = z.object({
  _id: z.string().optional(),
  filename: z.string().min(1, "Filename is required"),
  originalName: z.string().min(1, "Original name is required"),
  size: z.number().min(1, "Size must be positive"),
  uploadDate: z.date().optional(),
  processedDate: z.date().optional(),
  status: z.enum(['uploading', 'processing', 'completed', 'error']).default('uploading'),
  content: z.string().optional(), // Extracted text content
  chunks: z.array(z.object({
    text: z.string(),
    page: z.number(),
    startIndex: z.number(),
    endIndex: z.number(),
  })).optional(), // Text chunks for embedding
  userId: z.string().optional(), // Optional user association
});

export const insertPdfDocumentSchema = pdfDocumentSchema.pick({
  filename: true,
  originalName: true,
  size: true,
  userId: true,
});

export type PdfDocument = z.infer<typeof pdfDocumentSchema>;
export type InsertPdfDocument = z.infer<typeof insertPdfDocumentSchema>;

// MongoDB Conversation Schema
export const conversationSchema = z.object({
  _id: z.string().optional(),
  title: z.string().min(1, "Title is required"),
  createdAt: z.date().optional(),
  updatedAt: z.date().optional(),
  pdfDocumentId: z.string().optional(), // Associated PDF
  userId: z.string().optional(), // Optional user association
  isActive: z.boolean().default(false),
});

export const insertConversationSchema = conversationSchema.pick({
  title: true,
  pdfDocumentId: true,
  userId: true,
});

export type Conversation = z.infer<typeof conversationSchema>;
export type InsertConversation = z.infer<typeof insertConversationSchema>;

// MongoDB Message Schema
export const messageSchema = z.object({
  _id: z.string().optional(),
  conversationId: z.string().min(1, "Conversation ID is required"),
  role: z.enum(['user', 'assistant', 'system']),
  content: z.string().min(1, "Content is required"),
  timestamp: z.date().optional(),
  metadata: z.object({
    pdfChunks: z.array(z.string()).optional(), // Referenced PDF chunks
    sources: z.array(z.object({
      page: z.number(),
      text: z.string(),
    })).optional(),
  }).optional(),
});

export const insertMessageSchema = messageSchema.pick({
  conversationId: true,
  role: true,
  content: true,
  metadata: true,
});

export type Message = z.infer<typeof messageSchema>;
export type InsertMessage = z.infer<typeof insertMessageSchema>;

// MongoDB Collection Names
export const COLLECTIONS = {
  USERS: 'users',
  PDF_DOCUMENTS: 'pdf_documents',
  CONVERSATIONS: 'conversations',
  MESSAGES: 'messages',
} as const;
