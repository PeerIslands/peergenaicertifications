import { z } from "zod";

// MongoDB Document Schemas using Zod for validation

// Vectorized Documents Collection Schema (matches your structure)
export const vectorizedDocumentSchema = z.object({
  _id: z.string(),
  text: z.string(),
  page_number: z.number(),
  chunk_index: z.number(),
  char_count: z.number(),
  word_count: z.number(),
  is_complete_page: z.boolean(),
  document_id: z.string(),
  document_name: z.string(),
  document_path: z.string(),
  global_chunk_index: z.number(),
  embedding: z.array(z.number()),
});

// Chat History Collection Schema
export const chatHistorySchema = z.object({
  _id: z.string(),
  userId: z.string(),
  query: z.string(),
  response: z.string(),
  sources: z.array(z.object({
    content: z.string(),
    metadata: z.any().optional(),
    score: z.number().optional(),
  })).optional(),
  createdAt: z.string(),
});

// Input schemas for creating documents
export const createChatHistorySchema = chatHistorySchema.omit({ _id: true, createdAt: true });

// Type definitions
export type VectorizedDocument = z.infer<typeof vectorizedDocumentSchema>;
export type ChatHistory = z.infer<typeof chatHistorySchema>;
export type CreateChatHistory = z.infer<typeof createChatHistorySchema>;
