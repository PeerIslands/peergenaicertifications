import type { Express } from "express";
import { createServer, type Server } from "http";
import multer from "multer";
import { storage } from "./storage";
import { extractTextFromPDF, chunkText } from "./pdf";
import { generateEmbeddings, generateEmbedding, chatWithContext } from "./gemini";
import { insertDocumentSchema, insertMessageSchema } from "@shared/schema";

const upload = multer({ 
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype === "application/pdf") {
      cb(null, true);
    } else {
      cb(new Error("Only PDF files are allowed"));
    }
  }
});

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Get all documents
  app.get("/api/documents", async (req, res) => {
    try {
      const documents = await storage.getAllDocuments();
      res.json(documents);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch documents" });
    }
  });

  // Get single document
  app.get("/api/documents/:id", async (req, res) => {
    try {
      const document = await storage.getDocument(req.params.id);
      if (!document) {
        return res.status(404).json({ error: "Document not found" });
      }
      res.json(document);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch document" });
    }
  });

  // Extract text from PDF (for client-side visualization)
  app.post("/api/extract-text", async (req, res) => {
    try {
      const chunks: Buffer[] = [];
      req.on("data", (chunk) => chunks.push(chunk));
      req.on("end", async () => {
        try {
          const buffer = Buffer.concat(chunks);
          const pdfContent = await extractTextFromPDF(buffer);
          res.json({ text: pdfContent.text });
        } catch (error) {
          res.status(400).json({ error: "Failed to extract text from PDF" });
        }
      });
    } catch (error) {
      res.status(400).json({ error: "Failed to process PDF" });
    }
  });

  // Upload and process PDF
  app.post("/api/documents/upload", upload.single("file"), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }

      const chunkSize = parseInt(req.body.chunkSize) || 500;
      const overlap = parseInt(req.body.overlap) || 50;

      // Extract text from PDF
      const pdfContent = await extractTextFromPDF(req.file.buffer);

      // Create document record
      const docData = insertDocumentSchema.parse({
        name: req.file.originalname,
        size: req.file.size,
        pages: pdfContent.pages,
      });
      
      const document = await storage.createDocument(docData);

      // Chunk the text
      const textChunks = chunkText(pdfContent.text, chunkSize, overlap);

      // Generate embeddings in batches
      const batchSize = 20;
      let processedChunks = 0;

      console.log(`📊 [UPLOAD] Starting embedding generation for ${textChunks.length} chunks`);
      console.log(`   - Batch size: ${batchSize}`);
      console.log(`   - Total batches: ${Math.ceil(textChunks.length / batchSize)}`);

      for (let i = 0; i < textChunks.length; i += batchSize) {
        const batch = textChunks.slice(i, i + batchSize);
        const batchNum = Math.floor(i / batchSize) + 1;
        const totalBatches = Math.ceil(textChunks.length / batchSize);
        
        console.log(`📦 [UPLOAD] Processing batch ${batchNum}/${totalBatches} (chunks ${i + 1}-${Math.min(i + batchSize, textChunks.length)})`);
        
        try {
          const embeddings = await generateEmbeddings(batch.map(c => c.content));

          // Store chunks with embeddings
          for (let j = 0; j < batch.length; j++) {
            await storage.createChunk({
              documentId: document.id,
              content: batch[j].content,
              page: batch[j].page,
              embedding: embeddings[j],
            });
            processedChunks++;
          }
          console.log(`   - ✅ Batch ${batchNum} stored successfully`);
        } catch (error: any) {
          console.error(`   - ❌ Error processing batch ${batchNum}:`);
          console.error("     - Error:", error.message);
          console.error("     - Stack:", error.stack);
          throw error;
        }
      }
      
      console.log(`✅ [UPLOAD] All ${processedChunks} chunks processed and stored`);

      // Update document chunk count
      await storage.updateDocumentChunkCount(document.id, processedChunks);

      // Log vector store summary
      const { getCollectionStats } = await import("./chroma");
      const stats = await getCollectionStats();
      console.log(`✅ [UPLOAD] Document processing complete. Vector store now contains ${stats.vectorCount} total chunks.`);

      const updatedDoc = await storage.getDocument(document.id);
      res.json(updatedDoc);
    } catch (error) {
      console.error("Upload error:", error);
      res.status(500).json({ error: "Failed to process document" });
    }
  });

  // Delete document
  app.delete("/api/documents/:id", async (req, res) => {
    try {
      const deleted = await storage.deleteDocument(req.params.id);
      if (!deleted) {
        return res.status(404).json({ error: "Document not found" });
      }
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: "Failed to delete document" });
    }
  });

  // Get chunks for a document
  app.get("/api/documents/:id/chunks", async (req, res) => {
    try {
      const chunks = await storage.getChunksByDocument(req.params.id);
      res.json(chunks.map(c => ({
        id: c.id,
        content: c.content,
        page: c.page,
      })));
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch chunks" });
    }
  });

  // Chat with document
  app.post("/api/chat", async (req, res) => {
    try {
      const data = insertMessageSchema.parse(req.body);
      const documentId = data.documentId;

      if (!documentId) {
        return res.status(400).json({ error: "Document ID is required" });
      }

      // Store user message
      const userMessage = await storage.createMessage({
        role: "user",
        content: data.content,
        timestamp: new Date(),
      });

      // Generate embedding for the query
      const queryEmbedding = await generateEmbedding(data.content);

      // Search for similar chunks
      const similarChunks = await storage.searchSimilarChunks(
        queryEmbedding,
        documentId,
        5 // Top 5 chunks
      );

      // Generate response with context
      const responseText = await chatWithContext(data.content, similarChunks);

      // Store assistant message
      const assistantMessage = await storage.createMessage({
        role: "assistant",
        content: responseText,
        timestamp: new Date(),
        retrievedChunks: similarChunks,
      });

      res.json({
        userMessage,
        assistantMessage,
        retrievedChunks: similarChunks,
      });
    } catch (error) {
      console.error("Chat error:", error);
      res.status(500).json({ error: "Failed to process message" });
    }
  });

  // Get chat history
  app.get("/api/messages", async (req, res) => {
    try {
      const messages = await storage.getMessages();
      res.json(messages);
    } catch (error) {
      res.status(500).json({ error: "Failed to fetch messages" });
    }
  });

  // Clear chat history
  app.delete("/api/messages", async (req, res) => {
    try {
      await storage.clearMessages();
      res.json({ success: true });
    } catch (error) {
      res.status(500).json({ error: "Failed to clear messages" });
    }
  });

  return httpServer;
}
