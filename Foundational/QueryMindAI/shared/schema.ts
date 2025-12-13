import { sql } from "drizzle-orm";
import { pgTable, text, varchar, timestamp, integer } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod";

export const users = pgTable("users", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  username: text("username").notNull().unique(),
  password: text("password").notNull(),
});

export const conversations = pgTable("conversations", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  sessionId: text("session_id").notNull(),
  createdAt: timestamp("created_at").defaultNow().notNull(),
});

export const messages = pgTable("messages", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  conversationId: varchar("conversation_id").references(() => conversations.id),
  role: text("role", { enum: ["user", "assistant"] }).notNull(),
  content: text("content").notNull(),
  timestamp: timestamp("timestamp").defaultNow().notNull(),
  responseTime: integer("response_time"), // in milliseconds
});

export const analytics = pgTable("analytics", {
  id: varchar("id").primaryKey().default(sql`gen_random_uuid()`),
  sessionId: text("session_id").notNull(),
  eventType: text("event_type").notNull(), // "message_sent", "response_received", "conversation_started"
  data: text("data"), // JSON string for additional data
  timestamp: timestamp("timestamp").defaultNow().notNull(),
});

export const insertUserSchema = createInsertSchema(users).pick({
  username: true,
  password: true,
});

export const insertConversationSchema = createInsertSchema(conversations).omit({
  id: true,
  createdAt: true,
});

export const insertMessageSchema = createInsertSchema(messages).omit({
  id: true,
  timestamp: true,
});

export const insertAnalyticsSchema = createInsertSchema(analytics).omit({
  id: true,
  timestamp: true,
});

export type InsertUser = z.infer<typeof insertUserSchema>;
export type User = typeof users.$inferSelect;
export type InsertConversation = z.infer<typeof insertConversationSchema>;
export type Conversation = typeof conversations.$inferSelect;
export type InsertMessage = z.infer<typeof insertMessageSchema>;
export type Message = typeof messages.$inferSelect;
export type InsertAnalytics = z.infer<typeof insertAnalyticsSchema>;
export type Analytics = typeof analytics.$inferSelect;

// API Request Validation Schemas
export const chatRequestSchema = z.object({
  message: z.string().min(1, "Message cannot be empty").max(10000, "Message is too long"),
  sessionId: z.string().min(1, "Session ID is required").max(255, "Session ID is too long"),
  conversationId: z.string().uuid("Invalid conversation ID format").optional(),
});

export const conversationParamsSchema = z.object({
  conversationId: z.string().uuid("Invalid conversation ID format"),
});

export const analyticsParamsSchema = z.object({
  sessionId: z.string().min(1, "Session ID is required").max(255, "Session ID is too long"),
});

export const ragSearchQuerySchema = z.object({
  query: z.string().min(1, "Query cannot be empty").max(1000, "Query is too long"),
  limit: z
    .union([z.string(), z.number()])
    .optional()
    .transform((val) => {
      if (val === undefined) return 5;
      const num = typeof val === "string" ? parseInt(val, 10) : val;
      return isNaN(num) ? 5 : num;
    })
    .pipe(z.number().int().min(1).max(100)),
});
