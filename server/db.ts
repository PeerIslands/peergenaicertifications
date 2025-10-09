// server/db.ts
import { MongoClient, Db, Collection } from "mongodb";

export interface DocumentRecord {
  id: string;
  filename: string;
  originalName: string;
  content: string;
  fileSize: number;
  mimeType: string;
  uploadedAt: Date;
}

export interface ChunkRecord {
  docId: string;
  chunkIndex: number;
  text: string;
  embedding: number[];
}

export interface UserRecord {
  id: string;
  username: string;
  password: string;
}

let client: MongoClient;
let db: Db;

export async function connectToMongoDB(): Promise<void> {
  const uri = process.env.MONGODB_URI;
  const dbName = process.env.MONGODB_DB || "RAG_POC";

  if (!uri) throw new Error("MONGODB_URI is missing");

  try {
    client = new MongoClient(uri);
    await client.connect();
    db = client.db(dbName);

    // Ensure commonly used indexes exist before handling requests
    await Promise.all([
      documentsCollection().createIndex({ id: 1 }, { unique: true }),
      documentsCollection().createIndex({ uploadedAt: -1 }),
      chunksCollection().createIndex({ docId: 1, chunkIndex: 1 }, { unique: true }),
      usersCollection().createIndex({ id: 1 }, { unique: true }),
      usersCollection().createIndex({ username: 1 }, { unique: true }),
    ]);

    console.log(`Connected to MongoDB: ${dbName}`);
  } catch (err) {
    console.error("Failed to connect to MongoDB:", err);
    throw err;
  }
}

export function getDb(): Db {
  if (!db) throw new Error("MongoDB not initialized. Call connectToMongoDB() first.");
  return db;
}

export function documentsCollection(): Collection<DocumentRecord> {
  return getDb().collection<DocumentRecord>("documents");
}

export function chunksCollection(): Collection<ChunkRecord> {
  return getDb().collection<ChunkRecord>("chunks");
}

export function usersCollection(): Collection<UserRecord> {
  return getDb().collection<UserRecord>("users");
}
