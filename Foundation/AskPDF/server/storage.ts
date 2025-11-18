import { MongoClient, ObjectId } from "mongodb";
import { type ChatHistory, type CreateChatHistory } from "@shared/schema";

export interface IStorage {
  createChatHistory(chatHistory: CreateChatHistory): Promise<ChatHistory>;
  getChatHistoryByUserId(userId: string): Promise<ChatHistory[]>;
  getChatHistory(id: string): Promise<ChatHistory | undefined>;
}

export class MongoStorage implements IStorage {
  private client: MongoClient;
  private dbName: string;
  private chatHistoryCollection: string;

  constructor(mongoUri: string, dbName: string, chatHistoryCollection: string = "chat_history") {
    this.client = new MongoClient(mongoUri);
    this.dbName = dbName;
    this.chatHistoryCollection = chatHistoryCollection;
  }

  async connect(): Promise<void> {
    await this.client.connect();
  }

  async disconnect(): Promise<void> {
    await this.client.close();
  }

  private getDb() {
    return this.client.db(this.dbName);
  }

  async createChatHistory(chatHistory: CreateChatHistory): Promise<ChatHistory> {
    const db = this.getDb();
    const collection = db.collection(this.chatHistoryCollection);
    
    const document = {
      ...chatHistory,
      createdAt: new Date().toISOString(),
    };

    const result = await collection.insertOne(document);
    
    return {
      _id: result.insertedId.toString(),
      ...document,
    };
  }

  async getChatHistoryByUserId(userId: string): Promise<ChatHistory[]> {
    const db = this.getDb();
    const collection = db.collection(this.chatHistoryCollection);
    
    const documents = await collection
      .find({ userId })
      .sort({ createdAt: -1 })
      .toArray();

    return documents.map(doc => ({
      _id: doc._id.toString(),
      userId: doc.userId,
      query: doc.query,
      response: doc.response,
      sources: doc.sources,
      createdAt: doc.createdAt,
    }));
  }

  async getChatHistory(id: string): Promise<ChatHistory | undefined> {
    const db = this.getDb();
    const collection = db.collection(this.chatHistoryCollection);
    
    const document = await collection.findOne({ _id: new ObjectId(id) });
    
    if (!document) {
      return undefined;
    }

    return {
      _id: document._id.toString(),
      userId: document.userId,
      query: document.query,
      response: document.response,
      sources: document.sources,
      createdAt: document.createdAt,
    };
  }
}

// Singleton instance
let mongoStorage: MongoStorage | null = null;

export function getMongoStorage(): MongoStorage {
  if (!mongoStorage) {
    const mongoUri = process.env.MONGODB_URI || "mongodb://localhost:27017";
    const dbName = process.env.MONGODB_DATABASE || "rag_database";
    const chatHistoryCollection = process.env.MONGODB_CHAT_HISTORY_COLLECTION || "chat_history";
    
    mongoStorage = new MongoStorage(mongoUri, dbName, chatHistoryCollection);
  }
  return mongoStorage;
}

// For backward compatibility, export as storage
export const storage = {
  createChatHistory: async (chatHistory: CreateChatHistory) => {
    const mongoStorage = getMongoStorage();
    await mongoStorage.connect();
    return mongoStorage.createChatHistory(chatHistory);
  },
  getChatHistoryByUserId: async (userId: string) => {
    const mongoStorage = getMongoStorage();
    await mongoStorage.connect();
    return mongoStorage.getChatHistoryByUserId(userId);
  },
  getChatHistory: async (id: string) => {
    const mongoStorage = getMongoStorage();
    await mongoStorage.connect();
    return mongoStorage.getChatHistory(id);
  },
};
