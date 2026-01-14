import { 
  type User, 
  type InsertUser, 
  type PdfDocument,
  type InsertPdfDocument,
  type Conversation,
  type InsertConversation,
  type Message,
  type InsertMessage,
  COLLECTIONS 
} from "@shared/schema";
import { connectToDatabase } from "./db";
import { ObjectId } from "mongodb";

// modify the interface with any CRUD methods
// you might need

export interface IStorage {
  // User methods
  getUser(id: string): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  
  // PDF Document methods
  createPdfDocument(pdf: InsertPdfDocument): Promise<PdfDocument>;
  getPdfDocument(id: string): Promise<PdfDocument | undefined>;
  updatePdfDocument(id: string, updates: Partial<PdfDocument>): Promise<PdfDocument | undefined>;
  getAllPdfDocuments(): Promise<PdfDocument[]>;
  
  // Conversation methods
  createConversation(conversation: InsertConversation): Promise<Conversation>;
  getConversation(id: string): Promise<Conversation | undefined>;
  getAllConversations(): Promise<Conversation[]>;
  updateConversation(id: string, updates: Partial<Conversation>): Promise<Conversation | undefined>;
  
  // Message methods
  createMessage(message: InsertMessage): Promise<Message>;
  getMessagesByConversation(conversationId: string): Promise<Message[]>;
}

export class MongoStorage implements IStorage {
  // User methods
  async getUser(id: string): Promise<User | undefined> {
    try {
      const db = await connectToDatabase();
      const user = await db.collection(COLLECTIONS.USERS).findOne({ _id: new ObjectId(id) });
      return user as unknown as User | undefined;
    } catch (error) {
      console.error('Error getting user:', error);
      return undefined;
    }
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    try {
      const db = await connectToDatabase();
      const user = await db.collection(COLLECTIONS.USERS).findOne({ username });
      return user as unknown as User | undefined;
    } catch (error) {
      console.error('Error getting user by username:', error);
      return undefined;
    }
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    try {
      const db = await connectToDatabase();
      const userDoc = {
        ...insertUser,
        createdAt: new Date(),
        updatedAt: new Date(),
      };
      
      const result = await db.collection(COLLECTIONS.USERS).insertOne(userDoc);
      
      const user: User = {
        _id: result.insertedId.toString(),
        ...insertUser,
        createdAt: userDoc.createdAt,
        updatedAt: userDoc.updatedAt,
      };
      
      return user;
    } catch (error) {
      console.error('Error creating user:', error);
      throw error;
    }
  }

  // PDF Document methods
  async createPdfDocument(pdf: InsertPdfDocument): Promise<PdfDocument> {
    try {
      const db = await connectToDatabase();
      const pdfDoc = {
        ...pdf,
        uploadDate: new Date(),
        status: 'uploading' as const,
      };
      
      const result = await db.collection(COLLECTIONS.PDF_DOCUMENTS).insertOne(pdfDoc);
      
      const document: PdfDocument = {
        _id: result.insertedId.toString(),
        ...pdfDoc,
      };
      
      return document;
    } catch (error) {
      console.error('Error creating PDF document:', error);
      throw error;
    }
  }

  async getPdfDocument(id: string): Promise<PdfDocument | undefined> {
    try {
      const db = await connectToDatabase();
      const document = await db.collection(COLLECTIONS.PDF_DOCUMENTS).findOne({ _id: new ObjectId(id) });
      return document as unknown as PdfDocument | undefined;
    } catch (error) {
      console.error('Error getting PDF document:', error);
      return undefined;
    }
  }

  async updatePdfDocument(id: string, updates: Partial<PdfDocument>): Promise<PdfDocument | undefined> {
    try {
      const db = await connectToDatabase();
      const result = await db.collection(COLLECTIONS.PDF_DOCUMENTS).findOneAndUpdate(
        { _id: new ObjectId(id) },
        { $set: updates },
        { returnDocument: 'after' }
      );
      return result as unknown as PdfDocument | undefined;
    } catch (error) {
      console.error('Error updating PDF document:', error);
      return undefined;
    }
  }

  async getAllPdfDocuments(): Promise<PdfDocument[]> {
    try {
      const db = await connectToDatabase();
      const documents = await db.collection(COLLECTIONS.PDF_DOCUMENTS).find({}).toArray();
      return documents as unknown as PdfDocument[];
    } catch (error) {
      console.error('Error getting all PDF documents:', error);
      return [];
    }
  }

  // Conversation methods
  async createConversation(conversation: InsertConversation): Promise<Conversation> {
    try {
      const db = await connectToDatabase();
      const convDoc = {
        ...conversation,
        createdAt: new Date(),
        updatedAt: new Date(),
        isActive: false,
      };
      
      const result = await db.collection(COLLECTIONS.CONVERSATIONS).insertOne(convDoc);
      
      const newConversation: Conversation = {
        _id: result.insertedId.toString(),
        ...convDoc,
      };
      
      return newConversation;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  }

  async getConversation(id: string): Promise<Conversation | undefined> {
    try {
      const db = await connectToDatabase();
      const conversation = await db.collection(COLLECTIONS.CONVERSATIONS).findOne({ _id: new ObjectId(id) });
      return conversation as unknown as Conversation | undefined;
    } catch (error) {
      console.error('Error getting conversation:', error);
      return undefined;
    }
  }

  async getAllConversations(): Promise<Conversation[]> {
    try {
      const db = await connectToDatabase();
      const conversations = await db.collection(COLLECTIONS.CONVERSATIONS).find({}).sort({ updatedAt: -1 }).toArray();
      return conversations as unknown as Conversation[];
    } catch (error) {
      console.error('Error getting all conversations:', error);
      return [];
    }
  }

  async updateConversation(id: string, updates: Partial<Conversation>): Promise<Conversation | undefined> {
    try {
      const db = await connectToDatabase();
      const result = await db.collection(COLLECTIONS.CONVERSATIONS).findOneAndUpdate(
        { _id: new ObjectId(id) },
        { $set: { ...updates, updatedAt: new Date() } },
        { returnDocument: 'after' }
      );
      return result as unknown as Conversation | undefined;
    } catch (error) {
      console.error('Error updating conversation:', error);
      return undefined;
    }
  }

  // Message methods
  async createMessage(message: InsertMessage): Promise<Message> {
    try {
      const db = await connectToDatabase();
      const messageDoc = {
        ...message,
        timestamp: new Date(),
      };
      
      const result = await db.collection(COLLECTIONS.MESSAGES).insertOne(messageDoc);
      
      const newMessage: Message = {
        _id: result.insertedId.toString(),
        ...messageDoc,
      };
      
      return newMessage;
    } catch (error) {
      console.error('Error creating message:', error);
      throw error;
    }
  }

  async getMessagesByConversation(conversationId: string): Promise<Message[]> {
    try {
      const db = await connectToDatabase();
      const messages = await db.collection(COLLECTIONS.MESSAGES)
        .find({ conversationId })
        .sort({ timestamp: 1 })
        .toArray();
      return messages as unknown as Message[];
    } catch (error) {
      console.error('Error getting messages by conversation:', error);
      return [];
    }
  }
}

export const storage = new MongoStorage();
