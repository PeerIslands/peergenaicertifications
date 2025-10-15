import { z } from "zod";

// Supabase Document Schema
export const supabaseDocumentSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  size: z.number(),
  status: z.enum(["uploading", "processing", "ready", "error"]).default("uploading"),
  uploaded_at: z.string().datetime().default(() => new Date().toISOString()),
  processed_at: z.string().datetime().nullable().default(null),
  chunks: z.number().default(0),
  content: z.string().nullable().default(null),
  created_at: z.string().datetime().default(() => new Date().toISOString()),
  updated_at: z.string().datetime().default(() => new Date().toISOString()),
});

// Supabase Document Chunk Schema with Vector Embedding
export const supabaseDocumentChunkSchema = z.object({
  id: z.string().uuid(),
  document_id: z.string().uuid(),
  content: z.string(),
  embedding: z.array(z.number()).optional(), // Vector embedding for similarity search
  page_number: z.number().nullable().optional(),
  chunk_index: z.number(),
  metadata: z.record(z.any()).optional(), // JSONB field for flexible metadata
  created_at: z.string().datetime().default(() => new Date().toISOString()),
  updated_at: z.string().datetime().default(() => new Date().toISOString()),
});

// Supabase Search Query Schema
export const supabaseSearchQuerySchema = z.object({
  id: z.string().uuid(),
  query: z.string(),
  response: z.string().nullable().default(null),
  sources: z.array(z.object({
    document_id: z.string().uuid(),
    document_name: z.string(),
    chunk_id: z.string().uuid(),
    content: z.string(),
    score: z.number(),
  })).nullable().default(null),
  created_at: z.string().datetime().default(() => new Date().toISOString()),
  updated_at: z.string().datetime().default(() => new Date().toISOString()),
});

// Insert schemas (without auto-generated fields)
export const insertSupabaseDocumentSchema = supabaseDocumentSchema.omit({
  id: true,
  uploaded_at: true,
  processed_at: true,
  created_at: true,
  updated_at: true,
});

export const insertSupabaseDocumentChunkSchema = supabaseDocumentChunkSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
});

export const insertSupabaseSearchQuerySchema = supabaseSearchQuerySchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
});

// Type exports
export type SupabaseDocument = z.infer<typeof supabaseDocumentSchema>;
export type SupabaseDocumentChunk = z.infer<typeof supabaseDocumentChunkSchema>;
export type SupabaseSearchQuery = z.infer<typeof supabaseSearchQuerySchema>;

export type InsertSupabaseDocument = z.infer<typeof insertSupabaseDocumentSchema>;
export type InsertSupabaseDocumentChunk = z.infer<typeof insertSupabaseDocumentChunkSchema>;
export type InsertSupabaseSearchQuery = z.infer<typeof insertSupabaseSearchQuerySchema>;

// Supabase Table Names
export const TABLES = {
  DOCUMENTS: 'documents',
  DOCUMENT_CHUNKS: 'document_chunks',
  SEARCH_QUERIES: 'search_queries',
} as const;

// Vector Search Configuration for Supabase
export const VECTOR_SEARCH_CONFIG = {
  VECTOR_FIELD: 'embedding',
  SIMILARITY_THRESHOLD: 0.1, // Lowered further for hash-based embeddings
  MAX_RESULTS: 10,
  INDEX_NAME: 'document_chunks_embedding_idx',
} as const;

// SQL for creating tables and indexes
export const CREATE_TABLES_SQL = `
-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  size INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'uploading' CHECK (status IN ('uploading', 'processing', 'ready', 'error')),
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  chunks INTEGER NOT NULL DEFAULT 0,
  content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create document_chunks table with vector support
CREATE TABLE IF NOT EXISTS document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding VECTOR(384), -- 384-dimensional vector for embeddings
  page_number INTEGER,
  chunk_index INTEGER NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create search_queries table
CREATE TABLE IF NOT EXISTS search_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query TEXT NOT NULL,
  response TEXT,
  sources JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_uploaded_at ON documents(uploaded_at);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_chunk_index ON document_chunks(document_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_search_queries_created_at ON search_queries(created_at);

-- Create vector similarity search index
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx ON document_chunks 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_chunks_updated_at BEFORE UPDATE ON document_chunks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_search_queries_updated_at BEFORE UPDATE ON search_queries
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
`;

// RLS (Row Level Security) policies
export const RLS_POLICIES_SQL = `
-- Enable RLS on all tables
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_queries ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust based on your authentication needs)
-- For now, allowing all operations - you may want to restrict based on user authentication
CREATE POLICY "Allow all operations on documents" ON documents FOR ALL USING (true);
CREATE POLICY "Allow all operations on document_chunks" ON document_chunks FOR ALL USING (true);
CREATE POLICY "Allow all operations on search_queries" ON search_queries FOR ALL USING (true);
`;
