import { z } from "zod";

// Document schema
export const insertDocumentSchema = z.object({
  name: z.string(),
  size: z.number(),
  pages: z.number(),
});

export type InsertDocument = z.infer<typeof insertDocumentSchema>;

export interface Document {
  id: string;
  name: string;
  size: number;
  pages: number;
  chunks: number;
  uploadedAt: Date;
}

// Chunk schema
export interface Chunk {
  id: string;
  documentId: string;
  content: string;
  page: number;
  embedding: number[];
}

// Message schema
export const insertMessageSchema = z.object({
  content: z.string().min(1),
  documentId: z.string().optional(),
});

export type InsertMessage = z.infer<typeof insertMessageSchema>;

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  retrievedChunks?: RetrievedChunk[];
}

// Retrieved chunk with similarity score
export interface RetrievedChunk {
  id: string;
  content: string;
  similarity: number;
  page: number;
}

// Chunk settings
export interface ChunkSettings {
  chunkSize: number;
  overlap: number;
}

// Processing status
export interface ProcessingStatus {
  stage: "idle" | "chunking" | "vectorizing" | "storing" | "completed";
  progress: number;
  totalChunks: number;
  processedChunks: number;
}
