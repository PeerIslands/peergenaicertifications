import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { RAGOrchestrator, ConfigService, type LLMParameters } from "./services";

export async function registerRoutes(app: Express): Promise<Server> {
  // Initialize configuration service
  const configService = ConfigService.getInstance();
  
  // Validate configuration
  const validation = configService.validateConfig();
  if (!validation.isValid) {
    throw new Error(`Configuration validation failed: ${validation.errors.join(', ')}`);
  }

  // Initialize RAG orchestrator
  const ragOrchestrator = new RAGOrchestrator(configService.getConfig());
  await ragOrchestrator.initialize();

  // RAG API routes
  app.post("/api/chat", async (req, res) => {
    try {
      const { 
        query, 
        userId, 
        topK = 5,
        temperature = 0.7,
        topP = 1.0,
        maxTokens = 2048,
        frequencyPenalty = 0,
        presencePenalty = 0
      } = req.body;

      if (!query || !userId) {
        return res.status(400).json({ 
          error: "Query and userId are required" 
        });
      }

      // Validate parameters
      const validTopK = Math.max(1, Math.min(20, parseInt(topK) || 5));
      const validTemperature = Math.max(0, Math.min(2, parseFloat(temperature) || 0.7));
      const validTopP = Math.max(0, Math.min(1, parseFloat(topP) || 1.0));
      const validMaxTokens = Math.max(1, Math.min(4096, parseInt(maxTokens) || 2048));
      const validFrequencyPenalty = Math.max(-2, Math.min(2, parseFloat(frequencyPenalty) || 0));
      const validPresencePenalty = Math.max(-2, Math.min(2, parseFloat(presencePenalty) || 0));

      // Perform RAG search with specified parameters
      const ragResponse = await ragOrchestrator.search(query, validTopK, {
        temperature: validTemperature,
        topP: validTopP,
        maxTokens: validMaxTokens,
        frequencyPenalty: validFrequencyPenalty,
        presencePenalty: validPresencePenalty,
      });

      // Save the prompt and response to storage
      const chatHistory = await storage.createChatHistory({
        userId,
        query,
        response: ragResponse.answer,
        sources: ragResponse.sources,
      });

      res.json({
        id: chatHistory._id,
        answer: ragResponse.answer,
        sources: ragResponse.sources,
        timestamp: chatHistory.createdAt,
      });
    } catch (error) {
      console.error("Error in chat endpoint:", error);
      res.status(500).json({ 
        error: "Failed to process chat request" 
      });
    }
  });

  // Get user's chat history
  app.get("/api/chat/history/:userId", async (req, res) => {
    try {
      const { userId } = req.params;
      const chatHistory = await storage.getChatHistoryByUserId(userId);
      
      res.json(chatHistory);
    } catch (error) {
      console.error("Error fetching chat history:", error);
      res.status(500).json({ 
        error: "Failed to fetch chat history" 
      });
    }
  });

  // Get specific chat history entry
  app.get("/api/chat/history/entry/:id", async (req, res) => {
    try {
      const { id } = req.params;
      const chatHistory = await storage.getChatHistory(id);
      
      if (!chatHistory) {
        return res.status(404).json({ 
          error: "Chat history entry not found" 
        });
      }
      
      res.json(chatHistory);
    } catch (error) {
      console.error("Error fetching chat history entry:", error);
      res.status(500).json({ 
        error: "Failed to fetch chat history entry" 
      });
    }
  });

  // Health check endpoint
  app.get("/api/health", (req, res) => {
    res.json({ 
      status: "healthy", 
      timestamp: new Date().toISOString() 
    });
  });

  // System configuration endpoint
  app.get("/api/config", (req, res) => {
    try {
      const configSummary = configService.getConfigSummary();
      const systemStats = ragOrchestrator.getSystemStats();
      
      res.json({
        config: configSummary,
        stats: systemStats,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error("Error fetching configuration:", error);
      res.status(500).json({ 
        error: "Failed to fetch configuration" 
      });
    }
  });

  // Semantic search only endpoint
  app.post("/api/search/semantic", async (req, res) => {
    try {
      const { query, k = 5 } = req.body;

      if (!query) {
        return res.status(400).json({ 
          error: "Query is required" 
        });
      }

      const results = await ragOrchestrator.semanticSearch(query, k);
      res.json({ results });
    } catch (error) {
      console.error("Error in semantic search:", error);
      res.status(500).json({ 
        error: "Failed to perform semantic search" 
      });
    }
  });

  // Keyword search only endpoint
  app.post("/api/search/keyword", async (req, res) => {
    try {
      const { query, k = 5 } = req.body;

      if (!query) {
        return res.status(400).json({ 
          error: "Query is required" 
        });
      }

      const results = await ragOrchestrator.keywordSearch(query, k);
      res.json({ results });
    } catch (error) {
      console.error("Error in keyword search:", error);
      res.status(500).json({ 
        error: "Failed to perform keyword search" 
      });
    }
  });

  // Query expansion endpoint
  app.post("/api/expand-query", async (req, res) => {
    try {
      const { query } = req.body;

      if (!query) {
        return res.status(400).json({ 
          error: "Query is required" 
        });
      }

      const expandedQuery = await ragOrchestrator.expandQuery(query);
      res.json({ 
        originalQuery: query,
        expandedQuery 
      });
    } catch (error) {
      console.error("Error expanding query:", error);
      res.status(500).json({ 
        error: "Failed to expand query" 
      });
    }
  });

  // Direct LLM response endpoint (without RAG)
  app.post("/api/llm/direct", async (req, res) => {
    try {
      const { 
        query, 
        temperature = 0.7,
        topP = 1.0,
        maxTokens = 2048,
        frequencyPenalty = 0,
        presencePenalty = 0
      } = req.body;

      if (!query) {
        return res.status(400).json({ 
          error: "Query is required" 
        });
      }

      // Validate parameters
      const validTemperature = Math.max(0, Math.min(2, parseFloat(temperature) || 0.7));
      const validTopP = Math.max(0, Math.min(1, parseFloat(topP) || 1.0));
      const validMaxTokens = Math.max(1, Math.min(4096, parseInt(maxTokens) || 2048));
      const validFrequencyPenalty = Math.max(-2, Math.min(2, parseFloat(frequencyPenalty) || 0));
      const validPresencePenalty = Math.max(-2, Math.min(2, parseFloat(presencePenalty) || 0));

      const response = await ragOrchestrator.generateDirectResponse(query, {
        temperature: validTemperature,
        topP: validTopP,
        maxTokens: validMaxTokens,
        frequencyPenalty: validFrequencyPenalty,
        presencePenalty: validPresencePenalty,
      });

      res.json({ 
        query,
        response,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.error("Error generating direct response:", error);
      res.status(500).json({ 
        error: "Failed to generate direct response" 
      });
    }
  });

  const httpServer = createServer(app);

  return httpServer;
}
