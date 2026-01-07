import { randomUUID } from "crypto";
import type { 
  Document, 
  InsertDocument, 
  Chunk, 
  Message, 
  RetrievedChunk 
} from "@shared/schema";
import * as chromaStore from "./chroma";

export interface IStorage {
  // Document operations
  createDocument(doc: InsertDocument): Promise<Document>;
  getDocument(id: string): Promise<Document | undefined>;
  getAllDocuments(): Promise<Document[]>;
  deleteDocument(id: string): Promise<boolean>;
  updateDocumentChunkCount(id: string, chunks: number): Promise<void>;

  // Chunk operations
  createChunk(chunk: Omit<Chunk, "id">): Promise<Chunk>;
  getChunksByDocument(documentId: string): Promise<Chunk[]>;
  deleteChunksByDocument(documentId: string): Promise<void>;
  searchSimilarChunks(embedding: number[], documentId: string, topK: number): Promise<RetrievedChunk[]>;

  // Message operations
  createMessage(message: Omit<Message, "id">): Promise<Message>;
  getMessages(): Promise<Message[]>;
  clearMessages(): Promise<void>;
}

export class MemStorage implements IStorage {
  private documents: Map<string, Document>;
  private chunks: Map<string, Chunk>;
  private messages: Message[];

  constructor() {
    this.documents = new Map();
    this.chunks = new Map();
    this.messages = [];
    
    // Initialize Chroma
    chromaStore.initializeChroma().catch(err => {
      console.error("Failed to initialize Chroma:", err);
    });
  }

  // Document operations
  async createDocument(doc: InsertDocument): Promise<Document> {
    const id = randomUUID();
    const document: Document = {
      ...doc,
      id,
      chunks: 0,
      uploadedAt: new Date(),
    };
    this.documents.set(id, document);
    return document;
  }

  async getDocument(id: string): Promise<Document | undefined> {
    return this.documents.get(id);
  }

  async getAllDocuments(): Promise<Document[]> {
    return Array.from(this.documents.values());
  }

  async deleteDocument(id: string): Promise<boolean> {
    const deleted = this.documents.delete(id);
    if (deleted) {
      await this.deleteChunksByDocument(id);
    }
    return deleted;
  }

  async updateDocumentChunkCount(id: string, chunks: number): Promise<void> {
    const doc = this.documents.get(id);
    if (doc) {
      doc.chunks = chunks;
      this.documents.set(id, doc);
    }
  }

  // Chunk operations
  async createChunk(chunk: Omit<Chunk, "id">): Promise<Chunk> {
    const id = randomUUID();
    const newChunk: Chunk = { ...chunk, id };
    this.chunks.set(id, newChunk);
    
    // Add to Chroma vector store
    await chromaStore.addChunkToVectorStore(
      id,
      chunk.content,
      chunk.embedding,
      chunk.documentId,
      chunk.page
    );
    
    return newChunk;
  }

  async getChunksByDocument(documentId: string): Promise<Chunk[]> {
    return Array.from(this.chunks.values()).filter(
      (chunk) => chunk.documentId === documentId
    );
  }

  async deleteChunksByDocument(documentId: string): Promise<void> {
    // Delete from Chroma
    await chromaStore.deleteDocumentChunks(documentId);
    
    // Delete from memory
    const entriesToDelete = Array.from(this.chunks.entries())
      .filter(([, chunk]) => chunk.documentId === documentId)
      .map(([id]) => id);
    
    for (const id of entriesToDelete) {
      this.chunks.delete(id);
    }
  }

  async searchSimilarChunks(
    embedding: number[], 
    documentId: string, 
    topK: number
  ): Promise<RetrievedChunk[]> {
    // Use Chroma for vector search
    return chromaStore.searchSimilarChunks(embedding, documentId, topK);
  }

  // Message operations
  async createMessage(message: Omit<Message, "id">): Promise<Message> {
    const id = randomUUID();
    const newMessage: Message = { ...message, id };
    this.messages.push(newMessage);
    return newMessage;
  }

  async getMessages(): Promise<Message[]> {
    return [...this.messages];
  }

  async clearMessages(): Promise<void> {
    this.messages = [];
  }
}

export const storage = new MemStorage();
