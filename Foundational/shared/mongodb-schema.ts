import { z } from "zod";

// MongoDB Document Schema
export const mongoDocumentSchema = z.object({
  _id: z.string().optional(),
  id: z.string(),
  name: z.string(),
  size: z.number(),
  status: z.enum(["uploading", "processing", "ready", "error"]).default("uploading"),
  uploadedAt: z.date().default(() => new Date()),
  processedAt: z.date().nullable().default(null),
  chunks: z.number().default(0),
  content: z.string().nullable().default(null),
});

// MongoDB Document Chunk Schema with Vector Embedding
export const mongoDocumentChunkSchema = z.object({
  _id: z.string().optional(),
  id: z.string(),
  documentId: z.string(),
  content: z.string(),
  embedding: z.array(z.number()).optional(), // Vector embedding for similarity search
  pageNumber: z.number().nullable().optional(),
  chunkIndex: z.number(),
  metadata: z.object({
    documentName: z.string(),
    chunkType: z.string().default("text"),
  }).optional(),
});

// MongoDB Search Query Schema
export const mongoSearchQuerySchema = z.object({
  _id: z.string().optional(),
  id: z.string(),
  query: z.string(),
  response: z.string().nullable().default(null),
  sources: z.array(z.object({
    documentId: z.string(),
    documentName: z.string(),
    chunkId: z.string(),
    content: z.string(),
    score: z.number(),
  })).nullable().default(null),
  createdAt: z.date().default(() => new Date()),
});

// Insert schemas (without _id and auto-generated fields)
export const insertMongoDocumentSchema = mongoDocumentSchema.omit({
  _id: true,
  id: true,
  uploadedAt: true,
  processedAt: true,
});

export const insertMongoDocumentChunkSchema = mongoDocumentChunkSchema.omit({
  _id: true,
  id: true,
});

export const insertMongoSearchQuerySchema = mongoSearchQuerySchema.omit({
  _id: true,
  id: true,
  createdAt: true,
});

// Type exports
export type MongoDocument = z.infer<typeof mongoDocumentSchema>;
export type MongoDocumentChunk = z.infer<typeof mongoDocumentChunkSchema>;
export type MongoSearchQuery = z.infer<typeof mongoSearchQuerySchema>;

export type InsertMongoDocument = z.infer<typeof insertMongoDocumentSchema>;
export type InsertMongoDocumentChunk = z.infer<typeof insertMongoDocumentChunkSchema>;
export type InsertMongoSearchQuery = z.infer<typeof insertMongoSearchQuerySchema>;

// MongoDB Collection Names
export const COLLECTIONS = {
  DOCUMENTS: 'documents',
  DOCUMENT_CHUNKS: 'document_chunks',
  SEARCH_QUERIES: 'search_queries',
} as const;

// Vector Search Configuration
export const VECTOR_SEARCH_CONFIG = {
  VECTOR_FIELD: 'embedding',
  SIMILARITY_THRESHOLD: 0.7,
  MAX_RESULTS: 10,
  INDEX_NAME: 'vector_index',
} as const;
