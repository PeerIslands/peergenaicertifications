import { sql } from "drizzle-orm";
import { pgTable, text, varchar, jsonb, real, timestamp } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const documents = pgTable("documents", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  name: text("name").notNull(),
  size: real("size").notNull(),
  status: text("status").notNull().default("uploading"), // uploading, processing, ready, error
  uploadedAt: timestamp("uploaded_at").defaultNow(),
  processedAt: timestamp("processed_at"),
  chunks: real("chunks").default(0),
  content: text("content"),
});

export const documentChunks = pgTable("document_chunks", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  documentId: varchar("document_id").notNull().references(() => documents.id, { onDelete: "cascade" }),
  content: text("content").notNull(),
  embedding: jsonb("embedding"), // Store vector embeddings as JSON
  pageNumber: real("page_number"),
  chunkIndex: real("chunk_index").notNull(),
});

export const searchQueries = pgTable("search_queries", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  query: text("query").notNull(),
  response: text("response"),
  sources: jsonb("sources"), // Array of source references
  createdAt: timestamp("created_at").defaultNow(),
});

export const insertDocumentSchema = createInsertSchema(documents).omit({
  id: true,
  uploadedAt: true,
  processedAt: true,
});

export const insertDocumentChunkSchema = createInsertSchema(documentChunks).omit({
  id: true,
});

export const insertSearchQuerySchema = createInsertSchema(searchQueries).omit({
  id: true,
  createdAt: true,
});

export type InsertDocument = z.infer<typeof insertDocumentSchema>;
export type InsertDocumentChunk = z.infer<typeof insertDocumentChunkSchema>;
export type InsertSearchQuery = z.infer<typeof insertSearchQuerySchema>;

export type Document = typeof documents.$inferSelect;
export type DocumentChunk = typeof documentChunks.$inferSelect;
export type SearchQuery = typeof searchQueries.$inferSelect;
