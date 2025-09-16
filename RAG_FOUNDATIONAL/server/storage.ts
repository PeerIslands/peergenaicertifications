import { type User, type UpsertUser, type Pdf, type InsertPdf } from "@shared/schema";
import { randomUUID } from "crypto";
import { getDb } from "./mongo";

// modify the interface with any CRUD methods
// you might need

export interface IStorage {
  // User methods
  // (IMPORTANT) these user operations are mandatory for Replit Auth.
  getUser(id: string): Promise<User | undefined>;
  upsertUser(user: UpsertUser): Promise<User>;
  
  // PDF methods
  getPdfs(userId: string): Promise<Pdf[]>;
  getPdf(id: string): Promise<Pdf | undefined>;
  createPdf(pdf: InsertPdf): Promise<Pdf>;
  updatePdf(id: string, updates: Partial<Pdf>): Promise<Pdf | undefined>;
  deletePdf(id: string): Promise<boolean>;
  searchPdfs(userId: string, query: string): Promise<Pdf[]>;
}

export class MongoStorage implements IStorage {
  // User methods
  async getUser(id: string): Promise<User | undefined> {
    const db = await getDb();
    const doc = await db.collection("users").findOne({ id });
    return doc as unknown as User | undefined;
  }

  async upsertUser(userData: UpsertUser): Promise<User> {
    const db = await getDb();
    const id = userData.id!;
    const now = new Date();
    const existing = await db.collection("users").findOne({ id });
    const user: User = {
      id,
      email: userData.email ?? existing?.email,
      firstName: userData.firstName ?? existing?.firstName,
      lastName: userData.lastName ?? existing?.lastName,
      profileImageUrl: userData.profileImageUrl ?? existing?.profileImageUrl,
      createdAt: existing?.createdAt ?? now,
      updatedAt: now,
    } as User;
    await db.collection("users").updateOne(
      { id },
      { $set: user },
      { upsert: true }
    );
    return user;
  }

  // PDF methods
  async getPdfs(userId: string): Promise<Pdf[]> {
    const db = await getDb();
    const docs = await db.collection("pdfs").find({ userId }).sort({ uploadedAt: -1 }).toArray();
    return docs as unknown as Pdf[];
  }

  async getPdf(id: string): Promise<Pdf | undefined> {
    const db = await getDb();
    const doc = await db.collection("pdfs").findOne({ id });
    return doc as unknown as Pdf | undefined;
  }

  async createPdf(insertPdf: InsertPdf): Promise<Pdf> {
    const db = await getDb();
    const id = randomUUID();
    const pdf: Pdf = {
      ...insertPdf,
      id,
      uploadedAt: new Date(),
      processedAt: null,
    } as Pdf;
    await db.collection("pdfs").insertOne(pdf as any);
    return pdf;
  }

  async updatePdf(id: string, updates: Partial<Pdf>): Promise<Pdf | undefined> {
    const db = await getDb();
    const result = await db.collection("pdfs").findOneAndUpdate(
      { id },
      { $set: { ...updates } },
      { returnDocument: "after" }
    );
    const value = (result && "value" in result ? (result as any).value : null) as Pdf | null;
    return value ?? undefined;
  }

  async deletePdf(id: string): Promise<boolean> {
    const db = await getDb();
    const res = await db.collection("pdfs").deleteOne({ id });
    return res.deletedCount === 1;
  }

  async searchPdfs(userId: string, query: string): Promise<Pdf[]> {
    const db = await getDb();
    const docs = await db
      .collection("pdfs")
      .find({
        userId,
        $or: [
          { originalName: { $regex: query, $options: "i" } },
          { extractedText: { $regex: query, $options: "i" } },
          { metadata: { $regex: query, $options: "i" } },
        ],
      })
      .sort({ uploadedAt: -1 })
      .toArray();
    return docs as unknown as Pdf[];
  }
}

export const storage = new MongoStorage();