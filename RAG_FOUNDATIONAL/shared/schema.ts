import { z } from "zod";

// login information schema 
export const userSchema = z.object({
  id: z.string(),
  email: z.string().email().optional().nullable(),
  firstName: z.string().optional().nullable(),
  lastName: z.string().optional().nullable(),
  profileImageUrl: z.string().url().optional().nullable(),
  createdAt: z.coerce.date(),
  updatedAt: z.coerce.date(),
});

export const insertUserSchema = z.object({
  email: z.string().email().optional(),
  firstName: z.string().optional(),
  lastName: z.string().optional(),
  profileImageUrl: z.string().url().optional(),
});

// PDF document schema
export const pdfSchema = z.object({
  id: z.string(),
  userId: z.string(),
  fileName: z.string(),
  originalName: z.string(),
  filePath: z.string(),
  fileSize: z.number(),
  pageCount: z.number().optional(),
  extractedText: z.string().optional().nullable(),
  metadata: z.any().optional(),
  uploadedAt: z.coerce.date(),
  processedAt: z.coerce.date().nullable(),
});

// Schema for inserting a new PDF document
export const insertPdfSchema = z.object({
  userId: z.string(),
  fileName: z.string(),
  originalName: z.string(),
  filePath: z.string(),
  fileSize: z.number(),
  pageCount: z.number().optional(),
  extractedText: z.string().optional(),
  metadata: z.any().optional(),
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type UpsertUser = Partial<z.infer<typeof userSchema>> & { id: string };
export type User = z.infer<typeof userSchema>;
export type InsertPdf = z.infer<typeof insertPdfSchema>;
export type Pdf = z.infer<typeof pdfSchema>;