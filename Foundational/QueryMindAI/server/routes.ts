import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { LangChainService } from "./langchain";
import { ragService } from "./rag";
import { mongodbService } from "./mongodb";
import { insertConversationSchema, insertMessageSchema, insertAnalyticsSchema } from "@shared/schema";
import {
  chatRequestSchema,
  conversationParamsSchema,
  analyticsParamsSchema,
  ragSearchQuerySchema,
} from "@shared/schema";
import { validate } from "./validation";

/**
 * Registers all API routes for the Express application.
 * Initializes services (LangChain, MongoDB) and sets up endpoints for chat, conversations, analytics, and RAG.
 * 
 * @param app - The Express application instance to register routes on
 * @returns A promise that resolves to the HTTP server instance
 * 
 * @remarks
 * This function sets up the following endpoints:
 * - POST /api/chat - Chat endpoint with RAG support
 * - GET /api/conversation/:conversationId - Get conversation history
 * - GET /api/analytics/:sessionId - Get session analytics
 * - GET /api/rag/search - Search the knowledge base
 * - GET /api/rag/status - Get RAG service status
 * - GET /api/health - Health check endpoint
 */
export async function registerRoutes(app: Express): Promise<Server> {
  // Initialize services
  const langchainService = new LangChainService();
  
  // Initialize MongoDB connection
  try {
    await mongodbService.connect();
    console.log('MongoDB connected successfully');
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    console.warn('RAG functionality will be limited without MongoDB connection');
  }

  // Chat API endpoint with RAG
  app.post("/api/chat", validate(chatRequestSchema, "body"), async (req, res) => {
    try {
      const { message, sessionId, conversationId } = req.body;

      // Create conversation if it doesn't exist
      let currentConversationId = conversationId;
      if (!currentConversationId) {
        const conversation = await storage.createConversation({
          sessionId,
        });
        currentConversationId = conversation.id;
      }

      // Get conversation history
      const conversationHistory = await storage.getMessagesByConversation(currentConversationId);

      // Create user message
      const userMessage = await storage.createMessage({
        conversationId: currentConversationId,
        role: "user",
        content: message,
      });

      // Track analytics
      await storage.createAnalyticsEvent({
        sessionId,
        eventType: "message_sent",
        data: JSON.stringify({ messageLength: message.length }),
      });

      // Generate AI response with RAG
      const aiResponse = await langchainService.generateResponse(message, {
        conversationId: currentConversationId,
        sessionId,
        messages: conversationHistory,
      });

      // Create AI message
      const aiMessage = await storage.createMessage({
        conversationId: currentConversationId,
        role: "assistant",
        content: aiResponse.content,
        responseTime: aiResponse.responseTime,
      });

      // Track response analytics
      await storage.createAnalyticsEvent({
        sessionId,
        eventType: "response_received",
        data: JSON.stringify({ 
          responseTime: aiResponse.responseTime,
          responseLength: aiResponse.content.length 
        }),
      });

      res.json({
        success: true,
        conversationId: currentConversationId,
        userMessage: {
          id: userMessage.id,
          role: userMessage.role,
          content: userMessage.content,
          timestamp: userMessage.timestamp,
        },
        aiMessage: {
          id: aiMessage.id,
          role: aiMessage.role,
          content: aiMessage.content,
          timestamp: aiMessage.timestamp,
          responseTime: aiMessage.responseTime,
        },
        sources: aiResponse.sources, // Include RAG sources in response
      });

    } catch (error) {
      console.error("Chat API error:", error);
      res.status(500).json({ 
        error: "Internal server error",
        message: "Failed to process chat message"
      });
    }
  });

  // Get conversation history
  app.get("/api/conversation/:conversationId", validate(conversationParamsSchema, "params"), async (req, res) => {
    try {
      const { conversationId } = req.params;
      const messages = await storage.getMessagesByConversation(conversationId);
      
      res.json({
        success: true,
        messages: messages.map(msg => ({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: msg.timestamp,
          responseTime: msg.responseTime,
        })),
      });
    } catch (error) {
      console.error("Get conversation error:", error);
      res.status(500).json({ 
        error: "Internal server error",
        message: "Failed to retrieve conversation"
      });
    }
  });

  // Get session analytics
  app.get("/api/analytics/:sessionId", validate(analyticsParamsSchema, "params"), async (req, res) => {
    try {
      const { sessionId } = req.params;
      const analytics = await storage.getAnalyticsSummary(sessionId);
      
      res.json({
        success: true,
        analytics,
      });
    } catch (error) {
      console.error("Get analytics error:", error);
      res.status(500).json({ 
        error: "Internal server error",
        message: "Failed to retrieve analytics"
      });
    }
  });

  // RAG endpoints
  app.get("/api/rag/search", validate(ragSearchQuerySchema, "query"), async (req, res) => {
    try {
      const { query, limit = 5 } = req.query;

      const results = await ragService.retrieveRelevantDocuments(query as string, limit as number);
      
      res.json({
        success: true,
        query,
        results: results.map(doc => ({
          content: doc.content,
          metadata: doc.metadata,
          similarity: (doc as any).similarity,
        })),
      });
    } catch (error) {
      console.error("RAG search error:", error);
      res.status(500).json({ 
        error: "Internal server error",
        message: "Failed to search knowledge base"
      });
    }
  });

  app.get("/api/rag/status", async (req, res) => {
    try {
      const stats = await ragService.getKnowledgeBaseStats();
      
      res.json({
        success: true,
        ragReady: stats.isReady,
        documentCount: stats.documentCount,
        mongodbConnected: true,
        message: stats.isReady ? "RAG service is ready" : "RAG service is not fully ready"
      });
    } catch (error) {
      console.error("RAG status error:", error);
      res.status(500).json({ 
        error: "Internal server error",
        message: "Failed to check RAG status"
      });
    }
  });

  // Health check endpoint
  app.get("/api/health", async (req, res) => {
    const isConfigured = await LangChainService.validateConfiguration();
    const ragStats = await ragService.getKnowledgeBaseStats();
    
    res.json({
      status: "ok",
      timestamp: new Date().toISOString(),
      llmConfigured: isConfigured,
      ragReady: ragStats.isReady,
      documentCount: ragStats.documentCount,
    });
  });

  const httpServer = createServer(app);

  return httpServer;
}
