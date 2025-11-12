import type { Express } from "express";
import { createServer, type Server } from "http";
import multer from "multer";
import { getPostgresStorage } from "./postgres-storage";
import { processPDFDocument, performRAGSearch } from "./services/ragService";
import { insertSupabaseDocumentSchema } from "@shared/supabase-schema";

const upload = multer({ 
  storage: multer.memoryStorage(),
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
});

export async function registerRoutes(app: Express): Promise<Server> {
  
  // Get all documents
  app.get("/api/documents", async (req, res) => {
    try {
      const storage = await getPostgresStorage();
      const documents = await storage.getAllDocuments();
      res.json(documents);
    } catch (error) {
      console.error('Error in /api/documents:', error);
      res.status(500).json({ message: (error as Error).message });
    }
  });

  // Upload document
  app.post("/api/documents/upload", upload.single('pdf'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ message: "No PDF file provided" });
      }

      const storage = await getPostgresStorage();
      const documentData = {
        name: req.file.originalname,
        size: req.file.size,
        status: "uploading" as const,
      };

      const validatedData = insertSupabaseDocumentSchema.parse(documentData);
      const document = await storage.createDocument(validatedData);

      // Process PDF asynchronously
      processPDFDocument(document.id, req.file.buffer).catch(error => {
        console.error(`Failed to process document ${document.id}:`, error);
      });

      res.json(document);
    } catch (error) {
      res.status(500).json({ message: (error as Error).message });
    }
  });

  // Get document details
  app.get("/api/documents/:id", async (req, res) => {
    try {
      const storage = await getPostgresStorage();
      const document = await storage.getDocument(req.params.id);
      if (!document) {
        return res.status(404).json({ message: "Document not found" });
      }
      res.json(document);
    } catch (error) {
      res.status(500).json({ message: (error as Error).message });
    }
  });

  // Delete document
  app.delete("/api/documents/:id", async (req, res) => {
    try {
      const storage = await getPostgresStorage();
      
      // Check if document exists first
      const document = await storage.getDocument(req.params.id);
      if (!document) {
        return res.status(404).json({ message: "Document not found" });
      }
      
      // Prevent deletion of documents that are currently processing
      if (document.status === 'processing') {
        return res.status(400).json({ message: "Cannot delete document while it's being processed" });
      }
      
      await storage.deleteDocument(req.params.id);
      res.json({ message: "Document deleted successfully" });
    } catch (error) {
      console.error('Error deleting document:', error);
      res.status(500).json({ message: (error as Error).message });
    }
  });

  // Perform RAG search
  app.post("/api/search", async (req, res) => {
    try {
      const { query } = req.body;
      
      if (!query || typeof query !== 'string') {
        return res.status(400).json({ message: "Query is required and must be a string" });
      }

      const result = await performRAGSearch(query);
      res.json(result);
    } catch (error) {
      res.status(500).json({ message: (error as Error).message });
    }
  });

  // Get processing stats
  app.get("/api/stats", async (req, res) => {
    try {
      const storage = await getPostgresStorage();
      const stats = await storage.getStats();
      
      const documents = await storage.getAllDocuments();
      const enhancedStats = {
        ...stats,
        totalChunks: stats.chunksCount,
        readyDocuments: documents.filter(d => d.status === 'ready').length,
        processingDocuments: documents.filter(d => d.status === 'processing').length,
        totalSize: documents.reduce((sum, doc) => sum + doc.size, 0),
      };
      
      res.json(enhancedStats);
    } catch (error) {
      res.status(500).json({ message: (error as Error).message });
    }
  });



  const httpServer = createServer(app);
  return httpServer;
}
