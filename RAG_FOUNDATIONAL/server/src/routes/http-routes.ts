import type { Express } from "express";
import { createServer, type Server } from "http";
import express from "express";
import multer from "multer";
import path from "path";
import fs from "fs";
import OpenAI from "openai";
// LangChain: using built-in PDFLoader instead of hand-rolled parsing
import { PDFLoader } from "@langchain/community/document_loaders/fs/pdf";
import { storage } from "../services/storage";
import { answerWithRag } from "../services/rag";
import { getDb } from "../db/mongo";
import { setupAuth, isAuthenticated } from "../config/auth";
import { z } from "zod";
import { logger } from "../utils/logger";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

async function extractTextFromPdf(filePath: string): Promise<{ text: string; pageCount: number }> {
  try {
    const loader = new PDFLoader(filePath, {
      splitPages: true,
    });
    const docs = await loader.load();
    const pageCount = docs.length;
    const fullText = docs
      .map((d: any) => (typeof d.pageContent === 'string' ? d.pageContent : String(d.pageContent)))
      .join('\n');
    const cleanedText = (fullText || '')
      .replace(/\s+/g, ' ')
      .replace(/\n\s*\n/g, '\n')
      .trim();
    return {
      text: cleanedText || `PDF document processed (${pageCount} pages). No extractable text found.`,
      pageCount: Math.max(1, pageCount),
    };
  } catch (error) {
    logger.error({ err: error }, 'Error extracting text from PDF');
    const stats = fs.statSync(filePath);
    const fileName = path.basename(filePath);
    return {
      text: `PDF document: ${fileName}. File size: ${Math.round(stats.size / 1024)}KB. Text extraction failed - file may be encrypted, corrupted, or contain only images.`,
      pageCount: Math.max(1, Math.ceil(stats.size / 50000)),
    };
  }
}

const searchQuerySchema = z.object({
  q: z.string().min(1, "Search query cannot be empty").max(500, "Search query too long")
});

const pdfIdSchema = z.object({ id: z.string().uuid("Invalid PDF ID") });

const uploadDir = path.join(process.cwd(), "uploads");
if (!fs.existsSync(uploadDir)) {
  fs.mkdirSync(uploadDir, { recursive: true });
}
const maxUploadMb = Number(process.env.UPLOAD_MAX_FILE_MB || process.env.MAX_UPLOAD_MB || 50);
const upload = multer({
  dest: uploadDir,
  limits: { fileSize: maxUploadMb * 1024 * 1024 },
  fileFilter: (_req, file, cb) => {
    if (file.mimetype === "application/pdf") {
      cb(null, true);
    } else {
      cb(new Error("Only PDF files are allowed"));
    }
  },
});

export async function registerRoutes(app: Express): Promise<Server> {
  app.use(express.json());
  await setupAuth(app);

  app.get('/api/auth/user', isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const user = await storage.getUser(userId);
      res.json(user);
    } catch (error) {
      logger.error({ err: error }, "Error fetching user");
      res.status(500).json({ message: "Failed to fetch user" });
    }
  });

  app.get("/api/pdfs", isAuthenticated, async (req: any, res) => {
    try {
      const userId = req.user.claims.sub;
      const pdfs = await storage.getPdfs(userId);
      res.json(pdfs);
    } catch (error) {
      logger.error({ err: error }, "Error fetching PDFs");
      res.status(500).json({ error: "Failed to fetch PDFs" });
    }
  });

  app.post("/api/pdfs/upload", isAuthenticated, upload.single("pdf"), async (req: any, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: "No file uploaded" });
      }
      const file = req.file;
      const userId = req.user.claims.sub;
      let extractedText = "";
      let pageCount = 0;
      try {
        const extraction = await extractTextFromPdf(file.path);
        extractedText = extraction.text;
        pageCount = extraction.pageCount;
      } catch (extractError) {
        logger.error({ err: extractError }, "PDF text extraction failed");
        extractedText = "Text extraction failed - file may be corrupted or protected";
      }
      // MongoDB design principles:
      // 1) Don’t save full file content in a single document
      // 2) Respect 16MB document limit — persist only a preview slice here
      //    Full text is represented as small chunk documents in `vectors`
      const maxPreviewChars = Math.max(0, Number(process.env.RAG_EXTRACTED_TEXT_MAX_CHARS || 50000));
      const previewText = (extractedText || "").slice(0, maxPreviewChars);
      const wasTruncated = (extractedText || "").length > maxPreviewChars;

      const pdfRecord = await storage.createPdf({
        userId,
        fileName: file.filename,
        originalName: file.originalname,
        filePath: file.path,
        fileSize: file.size,
        pageCount,
        extractedText: previewText,
        metadata: { mimeType: file.mimetype, uploadDate: new Date().toISOString() },
      });
      await storage.updatePdf(pdfRecord.id, { processedAt: new Date() });
      try {
        // LangChain vector store: index chunks for retrieval (kept separate from PDF preview)
        if (extractedText && extractedText.trim()) {
          const { indexPdfInVectorStore } = await import('../services/rag');
          await indexPdfInVectorStore(userId, { pdfId: pdfRecord.id, originalName: pdfRecord.originalName, text: extractedText });
        }
      } catch (e) {
        logger.warn({ err: e }, 'Vector indexing failed');
      }
      res.json({ ...pdfRecord, metadata: { ...(pdfRecord as any).metadata, extractedTextTruncated: wasTruncated } });
    } catch (error) {
      logger.error({ err: error }, "Error uploading PDF");
      res.status(500).json({ error: "Failed to upload PDF" });
    }
  });

  app.get("/api/pdfs/search", isAuthenticated, async (req: any, res) => {
    try {
      const validation = searchQuerySchema.safeParse(req.query);
      if (!validation.success) {
        return res.status(400).json({ error: "Invalid search query", details: validation.error.errors });
      }
      const { q: query } = validation.data;
      const userId = req.user.claims.sub;
      const pdfs = await storage.searchPdfs(userId, query);
      res.json(pdfs);
    } catch (error) {
      logger.error({ err: error }, "Error searching PDFs");
      res.status(500).json({ error: "Failed to search PDFs" });
    }
  });

  app.post("/api/rag/chat", isAuthenticated, async (req: any, res) => {
    try {
      const { messages, pdfId } = req.body ?? {};
      if (!Array.isArray(messages) || messages.length === 0) {
        return res.status(400).json({ error: "messages array is required" });
      }
      const userId = req.user.claims.sub;
      let scopedPdfId: string | undefined = undefined;
      if (typeof pdfId === 'string' && pdfId.trim().length > 0) {
        const pdf = await storage.getPdf(pdfId);
        if (!pdf) {
          return res.status(404).json({ error: "PDF not found" });
        }
        if (pdf.userId !== userId) {
          return res.status(403).json({ error: "Forbidden" });
        }
        scopedPdfId = pdfId;
      }
      const result = await answerWithRag({ userId, messages, pdfId: scopedPdfId });
      try {
        const db = await getDb();
        const sessionId = req.sessionID || `${userId}-${new Date().toISOString().slice(0,10)}`;
        const lastUser = [...messages].reverse().find((m: any) => m.role === 'user');
        const question = lastUser?.content ?? '';
        await db.collection('chat_queries').insertOne({ userId, sessionId, question, messages, pdfId: scopedPdfId, createdAt: new Date() });
        await db.collection('chat_responses').insertOne({ userId, sessionId, answer: result.reply, sources: result.sources, pdfId: scopedPdfId, createdAt: new Date() });
      } catch (logErr) {
        logger.warn({ err: logErr }, 'Failed to persist chat logs');
      }
      res.json(result);
    } catch (error) {
      logger.error({ err: error }, "/api/rag/chat error");
      res.status(500).json({ error: "RAG chat failed" });
    }
  });

  app.get("/api/pdfs/:id", isAuthenticated, async (req: any, res) => {
    try {
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
      logger.error({ err: error }, "Error fetching PDF");
      res.status(500).json({ error: "Failed to fetch PDF" });
    }
  });

  app.get("/api/pdfs/:id/download", isAuthenticated, async (req: any, res) => {
    try {
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
      const safeFilename = pdf.originalName.replace(/[^\w\s.-]/g, '_');
      res.setHeader("Content-Disposition", `attachment; filename="${safeFilename}"`);
      const fileStream = fs.createReadStream(pdf.filePath);
      fileStream.pipe(res);
    } catch (error) {
      logger.error({ err: error }, "Error downloading PDF");
      res.status(500).json({ error: "Failed to download PDF" });
    }
  });

  app.delete("/api/pdfs/:id", isAuthenticated, async (req: any, res) => {
    try {
      const validation = pdfIdSchema.safeParse({ id: req.params.id });
      if (!validation.success) {
        return res.status(400).json({ error: "Invalid PDF ID format" });
      }
      const pdf = await storage.getPdf(req.params.id);
      if (!pdf) {
        return res.status(404).json({ error: "PDF not found" });
      }
      const userId = req.user.claims.sub;
      if (pdf.userId !== userId) {
        return res.status(403).json({ error: "Forbidden" });
      }
      if (fs.existsSync(pdf.filePath)) {
        fs.unlinkSync(pdf.filePath);
      }
      try {
        const db = await getDb();
        const vecRes = await db.collection('vectors').deleteMany({ pdfId: req.params.id, userId });
        const deleted = await storage.deletePdf(req.params.id);
        if (deleted) {
          res.json({ success: true, vectorsDeleted: vecRes.deletedCount ?? 0 });
        } else {
          res.status(500).json({ error: "Failed to delete PDF metadata", vectorsDeleted: vecRes.deletedCount ?? 0 });
        }
      } catch (dbErr) {
        logger.error({ err: dbErr }, "Error deleting PDF vectors/metadata");
        res.status(500).json({ error: "Failed to delete PDF data" });
      }
    } catch (error) {
      logger.error({ err: error }, "Error deleting PDF");
      res.status(500).json({ error: "Failed to delete PDF" });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}