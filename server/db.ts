import { MongoClient, Db } from 'mongodb';

const MONGODB_URI = process.env.DATABASE_URL || 'mongodb+srv://test-readwrite:VEANPK8wpW0A7Wcx7QA69uVb4h0TT19i@lumen-perftest-tst.qzczj.mongodb.net/demo?readPreference=primary';

if (!MONGODB_URI) {
  throw new Error(
    "DATABASE_URL must be set. Did you forget to provision a database?",
  );
}

let client: MongoClient;
let db: Db;

export async function connectToDatabase(): Promise<Db> {
  if (db) {
    return db;
  }

  try {
    client = new MongoClient(MONGODB_URI);
    await client.connect();
    db = client.db('demo'); // Using 'demo' as the database name from the connection string
    console.log('Connected to MongoDB');
    return db;
  } catch (error) {
    console.error('Failed to connect to MongoDB:', error);
    throw error;
  }
}

export async function closeDatabaseConnection(): Promise<void> {
  if (client) {
    await client.close();
    console.log('Disconnected from MongoDB');
  }
}

// Export the database instance for use in other modules
export { db };
