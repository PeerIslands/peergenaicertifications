import { type User, type InsertUser, type Document, type InsertDocument, type DocumentSummary } from "@shared/schema";
import { randomUUID } from "crypto";
import {
  documentsCollection,
  chunksCollection,
  usersCollection,
  type DocumentRecord,
  type ChunkRecord,
  type UserRecord,
} from "./db";

export interface DocumentVectors {
  chunks: string[];
  embeddings: number[][];
}

export interface IStorage {
  // User methods (keeping for future use)
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;

  // Document methods
  createDocument(document: InsertDocument): Promise<Document>;
  getDocument(id: string): Promise<Document | undefined>;
  getAllDocuments(): Promise<DocumentSummary[]>;
  deleteDocument(id: string): Promise<boolean>;

  // Vector methods
  saveDocumentVectors(documentId: string, chunks: string[], embeddings: number[][]): Promise<void>;
  getDocumentVectors(documentId: string): Promise<DocumentVectors | undefined>;
}

/*
export class MemStorage implements IStorage {
  private users: Map<string, User>;
  private documents: Map<string, Document>;
  private documentVectors: Map<string, DocumentVectors>;

  constructor() {
    this.users = new Map();
    this.documents = new Map();
    this.documentVectors = new Map();
  }

  // User methods
  async getUser(id: string): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = randomUUID();
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  // Document methods
  async createDocument(insertDocument: InsertDocument): Promise<Document> {
    const id = randomUUID();
    const document: Document = { 
      ...insertDocument, 
      id,
      uploadedAt: new Date()
    };
    this.documents.set(id, document);
    return document;
  }

  async getDocument(id: string): Promise<Document | undefined> {
    return this.documents.get(id);
  }

  async getAllDocuments(): Promise<DocumentSummary[]> {
    return Array.from(this.documents.values()).map(doc => ({
      id: doc.id,
      filename: doc.originalName,
      uploadedAt: doc.uploadedAt,
      fileSize: doc.fileSize
    }));
  }

  async deleteDocument(id: string): Promise<boolean> {
    const deleted = this.documents.delete(id);
    this.documentVectors.delete(id);
    return deleted;
  }

  // Vector methods
  async saveDocumentVectors(documentId: string, chunks: string[], embeddings: number[][]): Promise<void> {
    this.documentVectors.set(documentId, { chunks, embeddings });
  }

  async getDocumentVectors(documentId: string): Promise<DocumentVectors | undefined> {
    return this.documentVectors.get(documentId);
  }
}

export const storage = new MemStorage();
*/

class MongoStorage implements IStorage {
  // User methods
  async getUser(id: string): Promise<User | undefined> {
    const user = await usersCollection().findOne({ id }, { projection: { _id: 0 } });
    return user as User | undefined;
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    const user = await usersCollection().findOne({ username }, { projection: { _id: 0 } });
    return user as User | undefined;
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const record: UserRecord = {
      id: randomUUID(),
      username: insertUser.username,
      password: insertUser.password,
    };
    await usersCollection().insertOne(record);
    return record as User;
  }

  // Document methods
  async createDocument(insertDocument: InsertDocument): Promise<Document> {
    const record: DocumentRecord = {
      id: randomUUID(),
      filename: insertDocument.filename,
      originalName: insertDocument.originalName,
      content: insertDocument.content,
      fileSize: insertDocument.fileSize,
      mimeType: insertDocument.mimeType,
      uploadedAt: new Date(),
    };

    await documentsCollection().insertOne(record);
    return record as Document;
  }

  async getDocument(id: string): Promise<Document | undefined> {
    const document = await documentsCollection().findOne({ id }, { projection: { _id: 0 } });
    return document as Document | undefined;
  }

  async getAllDocuments(): Promise<DocumentSummary[]> {
    const documents = await documentsCollection()
      .find({}, { projection: { _id: 0, content: 0 } })
      .sort({ uploadedAt: -1 })
      .toArray();

    return documents.map((doc) => ({
      id: doc.id,
      filename: doc.originalName,
      uploadedAt: doc.uploadedAt,
      fileSize: doc.fileSize,
    }));
  }

  async deleteDocument(id: string): Promise<boolean> {
    const result = await documentsCollection().deleteOne({ id });
    if (!result.deletedCount) {
      return false;
    }

    await chunksCollection().deleteMany({ docId: id });
    return true;
  }

  // Vector methods
  async saveDocumentVectors(documentId: string, chunks: string[], embeddings: number[][]): Promise<void> {
    if (chunks.length !== embeddings.length) {
      throw new Error("Chunks and embeddings length mismatch");
    }

    await chunksCollection().deleteMany({ docId: documentId });

    if (chunks.length === 0) {
      return;
    }

    const records: ChunkRecord[] = chunks.map((text, index) => ({
      docId: documentId,
      chunkIndex: index,
      text,
      embedding: embeddings[index],
    }));

    await chunksCollection().insertMany(records);
  }

  async getDocumentVectors(documentId: string): Promise<DocumentVectors | undefined> {
    const records = await chunksCollection()
      .find({ docId: documentId }, { projection: { _id: 0 } })
      .sort({ chunkIndex: 1 })
      .toArray();

    if (records.length === 0) {
      return undefined;
    }

    return {
      chunks: records.map((record) => record.text),
      embeddings: records.map((record) => record.embedding),
    };
  }
}

export const storage = new MongoStorage();
