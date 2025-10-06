import "dotenv/config";
import { logger } from "./utils/logger";
// Production grade project structure: server/src with config, services, routes, utils, app, server
import { createApp } from "./app";

// Note: Request logging middleware intentionally omitted for simplicity.
(async () => {
  logger.info({ env: process.env.NODE_ENV, level: process.env.LOG_LEVEL || (process.env.NODE_ENV !== "production" ? "debug" : "info") }, "Starting server");
  const { server } = await createApp();

  const port = parseInt(process.env.PORT || '5000', 10);
  server.listen({
    port,
    host: "0.0.0.0",
    reusePort: true,
  }, () => {
    logger.info({ port }, "Server listening");
  });
})();

