import "dotenv/config";
import { MongoClient, type Db } from "mongodb";

let client: MongoClient | undefined;
let dbInstance: Db | undefined;

function getDatabaseNameFromEnv(): string {
  const fromEnv = process.env.MONGODB_DB;
  if (fromEnv && fromEnv.trim().length > 0) return fromEnv.trim();
  // Fallback if DB name not specified in URI: use a sensible default
  return "rag_application";
}

export async function getDb(): Promise<Db> {
  if (dbInstance) return dbInstance;

  const mongoUrl = process.env.DATABASE_URL;
  if (!mongoUrl) {
    throw new Error("DATABASE_URL is not set");
  }

  if (!client) {
    client = new MongoClient(mongoUrl, { 
      // modern drivers handle SRV, keep defaults minimal
    });
  }

  // Idempotent connect; safe to call multiple times
  await client.connect();

  const dbName = getDatabaseNameFromEnv();
  dbInstance = client.db(dbName);

  // Ensure required collections and minimal indexes exist
  await ensureCollections(dbInstance);

  return dbInstance;
}

async function ensureCollections(db: Db): Promise<void> {
  const requiredCollections = ["users", "pdfs", "sessions", "vectors", "chat_queries", "chat_responses"] as const;
  const existing = await db.listCollections({}, { nameOnly: true }).toArray();
  const existingNames = new Set(existing.map((c) => c.name));

  for (const name of requiredCollections) {
    if (!existingNames.has(name)) {
      await db.createCollection(name);
    }
  }

  // Indexes
  const users = db.collection("users");
  await users.createIndex({ id: 1 }, { unique: true });
  await users.createIndex({ email: 1 }, { unique: false, sparse: true });

  const pdfs = db.collection("pdfs");
  await pdfs.createIndex({ id: 1 }, { unique: true });
  await pdfs.createIndex({ userId: 1 });
  await pdfs.createIndex({ uploadedAt: -1 });
  await pdfs.createIndex({ originalName: "text", extractedText: "text" });

  // Vector store (chunk embeddings)
  const vectors = db.collection("vectors");
  await vectors.createIndex({ userId: 1, pdfId: 1, index: 1 }, { unique: true });
  await vectors.createIndex({ pdfId: 1 });
  await vectors.createIndex({ userId: 1 });
  // Chat logs
  const chatQueries = db.collection("chat_queries");
  await chatQueries.createIndex({ userId: 1, createdAt: -1 });
  await chatQueries.createIndex({ sessionId: 1, createdAt: -1 });
  const chatResponses = db.collection("chat_responses");
  await chatResponses.createIndex({ userId: 1, createdAt: -1 });
  await chatResponses.createIndex({ sessionId: 1, createdAt: -1 });


  // NOTE: Atlas Vector Search index on field `embedding` must be created via Atlas UI/API.
  // Optionally set env MONGODB_VECTOR_SEARCH=true and MONGODB_VECTOR_INDEX_NAME=vector_index
  // to enable $vectorSearch queries at runtime.

  // sessions collection is managed by connect-mongo
}

export async function closeMongo(): Promise<void> {
  if (client) {
    await client.close();
    client = undefined;
    dbInstance = undefined;
  }
}


