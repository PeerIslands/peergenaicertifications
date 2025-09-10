import { type Document, type InsertDocument, type DocumentChunk, type InsertDocumentChunk, type SearchQuery, type InsertSearchQuery } from "@shared/schema";
import { randomUUID } from "crypto";

export interface IStorage {
  // Document operations
  createDocument(document: InsertDocument): Promise<Document>;
  getDocument(id: string): Promise<Document | undefined>;
  getAllDocuments(): Promise<Document[]>;
  updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void>;
  updateDocumentContent(id: string, content: string): Promise<void>;
  
  // Document chunk operations
  createDocumentChunk(chunk: InsertDocumentChunk): Promise<DocumentChunk>;
  getDocumentChunks(documentId: string): Promise<DocumentChunk[]>;
  getAllChunks(): Promise<DocumentChunk[]>;
  
  // Search query operations
  createSearchQuery(query: InsertSearchQuery): Promise<SearchQuery>;
  getSearchQuery(id: string): Promise<SearchQuery | undefined>;
  getAllSearchQueries(): Promise<SearchQuery[]>;
}

export class MemStorage implements IStorage {
  private documents: Map<string, Document>;
  private documentChunks: Map<string, DocumentChunk>;
  private searchQueries: Map<string, SearchQuery>;

  constructor() {
    this.documents = new Map();
    this.documentChunks = new Map();
    this.searchQueries = new Map();
  }

  async createDocument(insertDocument: InsertDocument): Promise<Document> {
    const id = randomUUID();
    const now = new Date();
    const document: Document = { 
      ...insertDocument,
      status: insertDocument.status || "uploading",
      id, 
      uploadedAt: now,
      processedAt: null,
      chunks: 0,
      content: null
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

  async updateDocumentStatus(id: string, status: string, chunks?: number): Promise<void> {
    const document = this.documents.get(id);
    if (document) {
      const updatedDocument = { 
        ...document, 
        status, 
        processedAt: status === "ready" ? new Date() : document.processedAt,
        chunks: chunks ?? document.chunks
      };
      this.documents.set(id, updatedDocument);
    }
  }

  async updateDocumentContent(id: string, content: string): Promise<void> {
    const document = this.documents.get(id);
    if (document) {
      const updatedDocument = { ...document, content };
      this.documents.set(id, updatedDocument);
    }
  }

  async createDocumentChunk(insertChunk: InsertDocumentChunk): Promise<DocumentChunk> {
    const id = randomUUID();
    const chunk: DocumentChunk = { 
      ...insertChunk, 
      id,
      embedding: insertChunk.embedding || null,
      pageNumber: insertChunk.pageNumber || null
    };
    this.documentChunks.set(id, chunk);
    return chunk;
  }

  async getDocumentChunks(documentId: string): Promise<DocumentChunk[]> {
    return Array.from(this.documentChunks.values()).filter(
      chunk => chunk.documentId === documentId
    );
  }

  async getAllChunks(): Promise<DocumentChunk[]> {
    return Array.from(this.documentChunks.values());
  }

  async createSearchQuery(insertQuery: InsertSearchQuery): Promise<SearchQuery> {
    const id = randomUUID();
    const query: SearchQuery = { 
      ...insertQuery,
      response: insertQuery.response || null,
      sources: insertQuery.sources || null,
      id, 
      createdAt: new Date()
    };
    this.searchQueries.set(id, query);
    return query;
  }

  async getSearchQuery(id: string): Promise<SearchQuery | undefined> {
    return this.searchQueries.get(id);
  }

  async getAllSearchQueries(): Promise<SearchQuery[]> {
    return Array.from(this.searchQueries.values());
  }
}

export const storage = new MemStorage();
