import type { Express } from "express";
import { createServer, type Server } from "http";
import multer from "multer";
import fs from "fs";
import { storage } from "./storage";
import { FileProcessor } from "./services/fileProcessor";
import { aiService } from "./services/aiService";
import { chunkText } from "./utils/textChunker";

export async function registerRoutes(app: Express): Promise<Server> {
  // Configure multer for file uploads
  const upload = multer({
    dest: 'uploads/',
    limits: {
      fileSize: 10 * 1024 * 1024, // 10MB limit
    },
    fileFilter: (req, file, cb) => {
      if (FileProcessor.isValidFileType(file.mimetype)) {
        cb(null, true);
      } else {
        cb(new Error('Invalid file type. Only PDF, DOCX, and TXT files are allowed.'));
      }
    },
  });

  // Ensure uploads directory exists
  if (!fs.existsSync('uploads')) {
    fs.mkdirSync('uploads', { recursive: true });
  }

  // File upload endpoint
  app.post('/api/upload', upload.single('file'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      console.log(`Processing upload: ${req.file.originalname} (${req.file.mimetype})`);

      // Extract text from the uploaded file
      const content = await FileProcessor.extractText(req.file.path, req.file.mimetype);
      
      if (!content || content.trim().length === 0) {
        FileProcessor.cleanupFile(req.file.path);
        return res.status(400).json({ error: 'Could not extract text from the file' });
      }

      // Prepare vectors before persisting the document so we can fail fast if embedding fails
      const chunks = chunkText(content);
      //console.log("Chunks:", chunks)
      const embeddings = await aiService.generateEmbeddings(chunks);

      
      //console.log("embeddings:", embeddings)

      if (embeddings.length !== chunks.length) {
        throw new Error('Mismatch between generated embeddings and text chunks.');
      }

      // Create document in storage
      const documentData = {
        filename: req.file.filename,
        originalName: req.file.originalname,
        content,
        fileSize: req.file.size,
        mimeType: req.file.mimetype,
      };

      const document = await storage.createDocument(documentData);

      // Persist vectors for downstream retrieval use
      await storage.saveDocumentVectors(document.id, chunks, embeddings);

      // Clean up the uploaded file
      FileProcessor.cleanupFile(req.file.path);

      console.log(`Document created successfully: ${document.id}`);

      res.json({
        message: 'File uploaded successfully',
        document: {
          id: document.id,
          filename: document.originalName,
          uploadedAt: document.uploadedAt,
          fileSize: document.fileSize,
        },
      });
    } catch (error) {
      console.error('Upload error:', error);
      if (req.file) {
        FileProcessor.cleanupFile(req.file.path);
      }
      res.status(500).json({ 
        error: 'Upload failed', 
        details: error instanceof Error ? error.message : 'Unknown error' 
      });
    }
  });

  // Get all documents
  app.get('/api/documents', async (req, res) => {
    try {
      const documents = await storage.getAllDocuments();
      res.json(documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
      res.status(500).json({ error: 'Failed to fetch documents' });
    }
  });

  // Get specific document
  app.get('/api/documents/:id', async (req, res) => {
    try {
      const document = await storage.getDocument(req.params.id);
      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }
      res.json(document);
    } catch (error) {
      console.error('Error fetching document:', error);
      res.status(500).json({ error: 'Failed to fetch document' });
    }
  });

  // Delete document
  app.delete('/api/documents/:id', async (req, res) => {
    try {
      const success = await storage.deleteDocument(req.params.id);
      if (!success) {
        return res.status(404).json({ error: 'Document not found' });
      }
      res.json({ message: 'Document deleted successfully' });
    } catch (error) {
      console.error('Error deleting document:', error);
      res.status(500).json({ error: 'Failed to delete document' });
    }
  });

  // Ask question about document
  app.post('/api/ask', async (req, res) => {
    try {
      const { documentId, question } = req.body;

      if (!documentId || !question) {
        return res.status(400).json({ 
          error: 'Document ID and question are required' 
        });
      }

      console.log(`Processing question for document ${documentId}: ${question}`);

      const document = await storage.getDocument(documentId);
      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }

      const answer = await aiService.answerQuestion(
        document.content, 
        question, 
        document.originalName
      );

      console.log(`Generated answer for document ${documentId}`);

      res.json({ 
        answer,
        documentName: document.originalName 
      });
    } catch (error) {
      console.error('Question processing error:', error);
      res.status(500).json({ 
        error: 'Failed to process question',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  // Get document summary
  app.post('/api/summarize/:id', async (req, res) => {
    try {
      const document = await storage.getDocument(req.params.id);
      if (!document) {
        return res.status(404).json({ error: 'Document not found' });
      }

      const summary = await aiService.summarizeDocument(
        document.content, 
        document.originalName
      );

      res.json({ 
        summary,
        documentName: document.originalName 
      });
    } catch (error) {
      console.error('Summarization error:', error);
      res.status(500).json({ 
        error: 'Failed to generate summary',
        details: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}
