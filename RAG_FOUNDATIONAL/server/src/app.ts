import "dotenv/config";
import express, { type Request, Response, NextFunction } from "express";
import multer from "multer";
import { registerRoutes } from "./routes/http-routes";
import { setupVite, serveStatic } from "./config/vite";
import { logger } from "./utils/logger";
import { getDb } from "./db/mongo";

export async function createApp() {
  const app = express();
  app.use(express.json());
  app.use(express.urlencoded({ extended: false }));

  await getDb();
  const server = await registerRoutes(app);

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    // Handle multer file size errors gracefully
    if (err instanceof multer.MulterError && err.code === 'LIMIT_FILE_SIZE') {
      const maxMb = Number(process.env.UPLOAD_MAX_FILE_MB || process.env.MAX_UPLOAD_MB || 50);
      return res.status(413).json({ error: `File too large. Max ${maxMb}MB allowed.` });
    }

    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ error: message });
    logger.error({ err: err, status }, "Unhandled error");
  });

  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  return { app, server };
}

