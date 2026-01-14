import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import multer from "multer";
import pdf from "pdf-parse";
import { Ollama } from "ollama";
import { randomUUID } from "crypto";
import path from "path";
import fs from "fs";

// Initialize Ollama client
const ollama = new Ollama({
  host: process.env.OLLAMA_HOST || "http://localhost:11434",
});

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 10 * 1024 * 1024, // 10MB limit
  },
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'));
    }
  },
});

// Ensure uploads directory exists
if (!fs.existsSync('uploads')) {
  fs.mkdirSync('uploads');
}

export async function registerRoutes(app: Express): Promise<Server> {
  // PDF Upload endpoint
  app.post('/api/upload-pdf', upload.single('pdf'), async (req, res) => {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No PDF file uploaded' });
      }

      const { originalname, size, filename } = req.file;
      
      // Create PDF document record
      const pdfDoc = await storage.createPdfDocument({
        filename,
        originalName: originalname,
        size,
      });

      // Process PDF in background
      processPdfAsync(pdfDoc._id!, req.file.path);

      res.json({
        success: true,
        document: {
          id: pdfDoc._id,
          name: originalname,
          size,
          status: 'uploading'
        }
      });
    } catch (error) {
      console.error('PDF upload error:', error);
      res.status(500).json({ error: 'Failed to upload PDF' });
    }
  });

  // Get all PDF documents
  app.get('/api/documents', async (req, res) => {
    try {
      const documents = await storage.getAllPdfDocuments();
      res.json(documents);
    } catch (error) {
      console.error('Error fetching documents:', error);
      res.status(500).json({ error: 'Failed to fetch documents' });
    }
  });

  // Get conversations
  app.get('/api/conversations', async (req, res) => {
    try {
      const conversations = await storage.getAllConversations();
      res.json(conversations);
    } catch (error) {
      console.error('Error fetching conversations:', error);
      res.status(500).json({ error: 'Failed to fetch conversations' });
    }
  });

  // Create new conversation
  app.post('/api/conversations', async (req, res) => {
    try {
      const { title, pdfDocumentId } = req.body;
      
      if (!title) {
        return res.status(400).json({ error: 'Title is required' });
      }

      const conversation = await storage.createConversation({
        title,
        pdfDocumentId,
      });

      res.json(conversation);
    } catch (error) {
      console.error('Error creating conversation:', error);
      res.status(500).json({ error: 'Failed to create conversation' });
    }
  });

  // Get messages for a conversation
  app.get('/api/conversations/:id/messages', async (req, res) => {
    try {
      const { id } = req.params;
      const messages = await storage.getMessagesByConversation(id);
      res.json(messages);
    } catch (error) {
      console.error('Error fetching messages:', error);
      res.status(500).json({ error: 'Failed to fetch messages' });
    }
  });

  // Send message and get AI response
  app.post('/api/conversations/:id/messages', async (req, res) => {
    try {
      const { id } = req.params;
      const { content } = req.body;

      if (!content) {
        return res.status(400).json({ error: 'Message content is required' });
      }

      // Create user message
      const userMessage = await storage.createMessage({
        conversationId: id,
        role: 'user',
        content,
      });

      // Get conversation to find associated PDF
      const conversation = await storage.getConversation(id);
      if (!conversation) {
        return res.status(404).json({ error: 'Conversation not found' });
      }

      // Get AI response
      const aiResponse = await generateAIResponse(content, conversation.pdfDocumentId);
      
      // Create AI message
      const aiMessage = await storage.createMessage({
        conversationId: id,
        role: 'assistant',
        content: aiResponse.content,
        metadata: aiResponse.metadata,
      });

      // Update conversation timestamp
      await storage.updateConversation(id, { updatedAt: new Date() });

      res.json({
        userMessage,
        aiMessage,
      });
    } catch (error) {
      console.error('Error sending message:', error);
      res.status(500).json({ error: 'Failed to send message' });
    }
  });

  const httpServer = createServer(app);
  return httpServer;
}

// Helper function to process PDF asynchronously
async function processPdfAsync(documentId: string, filePath: string) {
  try {
    // Update status to processing
    await storage.updatePdfDocument(documentId, { status: 'processing' });

    // Read and parse PDF
    const dataBuffer = fs.readFileSync(filePath);
    const pdfData = await pdf(dataBuffer);
    
    // Extract text content
    const content = pdfData.text;
    
    // Create text chunks (simple chunking by paragraphs)
    const paragraphs = content.split('\n\n').filter(p => p.trim().length > 0);
    const chunks = paragraphs.map((text, index) => ({
      text: text.trim(),
      page: Math.floor(index / 5) + 1, // Rough page estimation
      startIndex: content.indexOf(text),
      endIndex: content.indexOf(text) + text.length,
    }));

    // Update document with processed content
    await storage.updatePdfDocument(documentId, {
      status: 'completed',
      content,
      chunks,
      processedDate: new Date(),
    });

    // Clean up uploaded file
    fs.unlinkSync(filePath);

    console.log(`PDF processed successfully: ${documentId}`);
  } catch (error) {
    console.error('PDF processing error:', error);
    await storage.updatePdfDocument(documentId, { status: 'error' });
  }
}

// Helper function to generate AI response
async function generateAIResponse(userMessage: string, pdfDocumentId?: string) {
  try {
    let context = '';
    let sources: Array<{ page: number; text: string }> = [];

    if (pdfDocumentId) {
      const pdfDoc = await storage.getPdfDocument(pdfDocumentId);
      if (pdfDoc && pdfDoc.status === 'completed' && pdfDoc.chunks) {
        // Simple keyword matching to find relevant chunks
        const keywords = userMessage.toLowerCase().split(' ').filter(word => word.length > 3);
        const relevantChunks = pdfDoc.chunks.filter(chunk => 
          keywords.some(keyword => chunk.text.toLowerCase().includes(keyword))
        ).slice(0, 3); // Limit to 3 most relevant chunks

        context = relevantChunks.map(chunk => chunk.text).join('\n\n');
        sources = relevantChunks.map(chunk => ({
          page: chunk.page,
          text: chunk.text.substring(0, 200) + '...'
        }));
      }
    }

    const systemPrompt = `You are a helpful AI assistant that answers questions based on PDF documents. 
    ${context ? `Here is relevant context from the PDF:\n\n${context}\n\n` : ''}
    Please provide accurate, helpful answers based on the provided context. If the context doesn't contain enough information to answer the question, please say so.`;

    const completion = await ollama.chat({
      model: "llama3:latest", // Using llama3 model
      messages: [
        { role: "system", content: systemPrompt },
        { role: "user", content: userMessage }
      ],
      options: {
        temperature: 0.7,
        num_predict: 1000, // Equivalent to max_tokens
      }
    });

    return {
      content: completion.message?.content || "I'm sorry, I couldn't generate a response.",
      metadata: {
        sources: sources.length > 0 ? sources : undefined,
      }
    };
  } catch (error) {
    console.error('AI response generation error:', error);
    return {
      content: "I'm sorry, I encountered an error while processing your request. Please try again.",
      metadata: {}
    };
  }
}