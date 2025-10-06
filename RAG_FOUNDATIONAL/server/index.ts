// Deprecated: use server/src/server.ts
export * from "./src/server";

// Environment validation
const requiredEnvVars = [
  'DATABASE_URL',
  'SESSION_SECRET',
  'GOOGLE_CLIENT_ID',
  'GOOGLE_CLIENT_SECRET',
  'APP_BASE_URL',
];

// moved to server/src/server.ts

// Note: Request logging middleware removed as requested for simplicity.