import type { Express } from "express";
import { createServer, type Server } from "http";
import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import OpenAI from "openai";
import { storage } from "./storage";
import { answerWithRag } from "./rag";
import { getDb } from "./mongo";
import { setupAuth, isAuthenticated } from "./googleAuth";
import { insertPdfSchema } from "@shared/schema";
import { z } from "zod";

// the newest OpenAI model is "gpt-5" which was released August 7, 2025. do not change this unless explicitly requested by the user
const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

// PDF text extraction function using pdfjs-dist
async function extractTextFromPdf(filePath: string): Promise<{ text: string; pageCount: number }> {
  try {
    // Use ESM import for pdfjs-dist legacy build to be compatible with ESM bundle
    const pdfjs: any = await import('pdfjs-dist/legacy/build/pdf.mjs');
    
    const data = new Uint8Array(fs.readFileSync(filePath));
    const loadingTask = pdfjs.getDocument({ data, useSystemFonts: true, disableWorker: true });
    const pdf = await loadingTask.promise;
    const pageCount = pdf.numPages;
    let fullText = '';

    // Extract text from all pages
    for (let pageNum = 1; pageNum <= pageCount; pageNum++) {
      try {
        const page = await pdf.getPage(pageNum);
        const textContent = await page.getTextContent();
        const pageText = textContent.items
          .filter((item: any) => item.str && typeof item.str === 'string')
          .map((item: any) => item.str)
          .join(' ');
        
        if (pageText.trim()) {
          fullText += pageText + '\n';
        }
      } catch (pageError) {
        console.error(`Error extracting text from page ${pageNum}:`, pageError);
        // Continue with other pages even if one fails
        fullText += `[Page ${pageNum}: Text extraction failed]\n`;
      }
    }

    // Clean up the text
    const cleanedText = fullText
      .replace(/\s+/g, ' ') // Replace multiple whitespace with single space
      .replace(/\n\s*\n/g, '\n') // Remove excessive line breaks
      .trim();

    return { 
      text: cleanedText || `PDF document processed (${pageCount} pages). No extractable text found.`,
      pageCount 
    };
  } catch (error) {
    console.error('Error extracting text from PDF:', error);
    
    // Fallback: return basic file info when text extraction fails
    const stats = fs.statSync(filePath);
    const fileName = path.basename(filePath);
    return { 
      text: `PDF document: ${fileName}. File size: ${Math.round(stats.size / 1024)}KB. Text extraction failed - file may be encrypted, corrupted, or contain only images.`,
      pageCount: Math.max(1, Math.ceil(stats.size / 50000)) // Rough estimate
    };
  }
}

// Validation schemas
const searchQuerySchema = z.object({
  q: z.string().min(1, "Search query cannot be empty").max(500, "Search query too long")
});

const pdfIdSchema = z.object({
  id: z.string().uuid("Invalid PDF ID")
});

// Configure multer for file uploads
const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}

// File size limit: configurable via env UPLOAD_MAX_FILE_MB (server) and VITE_MAX_UPLOAD_MB (client)
const maxUploadMb = Number(process.env.UPLOAD_MAX_FILE_MB || process.env.MAX_UPLOAD_MB || 50);

const upload = multer({
  dest: uploadDir,
  limits: {
    fileSize: maxUploadMb * 1024 * 1024,
  },
  fileFilter: (_req, file, cb) => {
    if (file.mimetype === "application/pdf") {
      cb(null, true);
    } else {
      cb(new Error("Only PDF files are allowed"));
    }
  },
});

export async function registerRoutes(app: Express): Promise<Server> {
  // Enable JSON parsing
  app.use(express.json());

  // Auth middleware
  await setupAuth(app);

  // Auth routes
  app.get('/api/auth/user', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      res.json(user);
    } catch (error) {
      console.error("Error fetching user:", error);
      res.status(500).json({ message: "Failed to fetch user" });
    }
  });

  // Get all PDFs for user
  app.get("/api/pdfs", isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const pdfs = await storage.getPdfs(userId);
      res.json(pdfs);
    } catch (error) {
      console.error("Error fetching PDFs:", error);
      res.status(500).json({ error: "Failed to fetch PDFs" });
    }
  });

  // Upload PDF
  app.post("/api/pdfs/upload", isAuthenticated, upload.single("pdf"), async (req: any, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }

      const file = req.file;
      const userId = req.user.claims.sub;
      
      // Extract text from PDF
      let extractedText = "";
      let pageCount = 0;
      
      try {
        const extraction = await extractTextFromPdf(file.path);
        extractedText = extraction.text;
        pageCount = extraction.pageCount;
      } catch (extractError) {
        console.error("PDF text extraction failed:", extractError);
        // Continue with upload but log the error
        extractedText = "Text extraction failed - file may be corrupted or protected";
      }
      
      const pdfRecord = await storage.createPdf({
        userId,
        fileName: file.filename,
        originalName: file.originalname,
        filePath: file.path,
        fileSize: file.size,
        pageCount,
        extractedText,
        metadata: {
          mimeType: file.mimetype,
          uploadDate: new Date().toISOString(),
        },
      });

      // Mark as processed immediately since we already extracted the text
      await storage.updatePdf(pdfRecord.id, {
        processedAt: new Date(),
      });

      // Index into Mongo vector store (best-effort; won't block upload)
      try {
        if (extractedText && extractedText.trim()) {
          const { indexPdfInVectorStore } = await import('./rag');
          await indexPdfInVectorStore(userId, { pdfId: pdfRecord.id, originalName: pdfRecord.originalName, text: extractedText });
        }
      } catch (e) {
        console.warn('Vector indexing failed:', e);
      }

      res.json(pdfRecord);
    } catch (error) {
      console.error("Error uploading PDF:", error);
      res.status(500).json({ error: "Failed to upload PDF" });
    }
  });

  // Search PDFs - MUST come before /api/pdfs/:id route
  app.get("/api/pdfs/search", isAuthenticated, async (req: any, res) => {
    try {
      // Validate search query
      const validation = searchQuerySchema.safeParse(req.query);
      if (!validation.success) {
        return res.status(400).json({ 
          error: "Invalid search query", 
          details: validation.error.errors 
        });
      }

      const { q: query } = validation.data;
      const userId = req.user.claims.sub;
      const pdfs = await storage.searchPdfs(userId, query);
      res.json(pdfs);
    } catch (error) {
      console.error("Error searching PDFs:", error);
      res.status(500).json({ error: "Failed to search PDFs" });
    }
  });

  // RAG chat endpoint
  app.post("/api/rag/chat", isAuthenticated, async (req: any, res) => {
    try {
      const { messages } = req.body ?? {};
      if (!Array.isArray(messages) || messages.length === 0) {
        return res.status(400).json({ error: "messages array is required" });
      }

      const userId = req.user.claims.sub;
      const result = await answerWithRag({ userId, messages });

      // Persist chat logs
      try {
        const db = await getDb();
        const sessionId = req.sessionID || `${userId}-${new Date().toISOString().slice(0,10)}`;
        const lastUser = [...messages].reverse().find((m: any) => m.role === 'user');
        const question = lastUser?.content ?? '';

        await db.collection('chat_queries').insertOne({
          userId,
          sessionId,
          question,
          messages,
          createdAt: new Date(),
        });

        await db.collection('chat_responses').insertOne({
          userId,
          sessionId,
          answer: result.reply,
          sources: result.sources,
          createdAt: new Date(),
        });
      } catch (logErr) {
        console.warn('Failed to persist chat logs:', logErr);
      }

      res.json(result);
    } catch (error) {
      console.error("/api/rag/chat error:", error);
      res.status(500).json({ error: "RAG chat failed" });
    }
  });

  // Get specific PDF
  app.get("/api/pdfs/:id", isAuthenticated, async (req: any, res) => {
    try {
      // Validate PDF ID
      const validation = pdfIdSchema.safeParse({ id: req.params.id });
      if (!validation.success) {
        return res.status(400).json({ error: "Invalid PDF ID format" });
      }
      
      const pdf = await storage.getPdf(req.params.id);
      if (!pdf) {
        return res.status(404).json({ error: "PDF not found" });
      }
      res.json(pdf);
    } catch (error) {
      console.error("Error fetching PDF:", error);
      res.status(500).json({ error: "Failed to fetch PDF" });
    }
  });

  // Download PDF
  app.get("/api/pdfs/:id/download", isAuthenticated, async (req: any, res) => {
    try {
      // Validate PDF ID
      const validation = pdfIdSchema.safeParse({ id: req.params.id });
      if (!validation.success) {
        return res.status(400).json({ error: "Invalid PDF ID format" });
      }
      
      const pdf = await storage.getPdf(req.params.id);
      if (!pdf) {
        return res.status(404).json({ error: "PDF not found" });
      }

      if (!fs.existsSync(pdf.filePath)) {
        return res.status(404).json({ error: "File not found on disk" });
      }

      res.setHeader("Content-Type", "application/pdf");
      // Sanitize filename to prevent header injection
      const safeFilename = pdf.originalName.replace(/[^\w\s.-]/g, '_');
      res.setHeader("Content-Disposition", `attachment; filename="${safeFilename}"`);
      
      const fileStream = fs.createReadStream(pdf.filePath);
      fileStream.pipe(res);
    } catch (error) {
      console.error("Error downloading PDF:", error);
      res.status(500).json({ error: "Failed to download PDF" });
    }
  });

  // Delete PDF
  app.delete("/api/pdfs/:id", isAuthenticated, async (req: any, res) => {
    try {
      // Validate PDF ID
      const validation = pdfIdSchema.safeParse({ id: req.params.id });
      if (!validation.success) {
        return res.status(400).json({ error: "Invalid PDF ID format" });
      }
      
      const pdf = await storage.getPdf(req.params.id);
      if (!pdf) {
        return res.status(404).json({ error: "PDF not found" });
      }
      // Enforce ownership
      const userId = req.user.claims.sub;
      if (pdf.userId !== userId) {
        return res.status(403).json({ error: "Forbidden" });
      }

      // Delete file from disk
      if (fs.existsSync(pdf.filePath)) {
        fs.unlinkSync(pdf.filePath);
      }

      // Delete vectors and PDF metadata
      try {
        const db = await getDb();
        const vecRes = await db.collection('vectors').deleteMany({ pdfId: req.params.id, userId });
        const deleted = await storage.deletePdf(req.params.id);

        if (deleted) {
          res.json({ success: true, vectorsDeleted: vecRes.deletedCount ?? 0 });
        } else {
          // If vectors deleted but metadata failed, report error
          res.status(500).json({ error: "Failed to delete PDF metadata", vectorsDeleted: vecRes.deletedCount ?? 0 });
        }
      } catch (dbErr) {
        console.error("Error deleting PDF vectors/metadata:", dbErr);
        res.status(500).json({ error: "Failed to delete PDF data" });
      }
    } catch (error) {
      console.error("Error deleting PDF:", error);
      res.status(500).json({ error: "Failed to delete PDF" });
    }
  });


  const httpServer = createServer(app);
  return httpServer;
}