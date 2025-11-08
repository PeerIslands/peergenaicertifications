// Lightweight browser logger built on loglevel
// - Avoids console.* in app code
// - Uses DEBUG level in development and INFO in production
import log from "loglevel";

const level = import.meta.env?.MODE !== "production" ? "debug" : (import.meta.env?.VITE_LOG_LEVEL || "info");
log.setLevel(level as log.LogLevelDesc);

export const clientLogger = {
  debug: (msg: string, data?: unknown) => (data ? log.debug(msg, data) : log.debug(msg)),
  info: (msg: string, data?: unknown) => (data ? log.info(msg, data) : log.info(msg)),
  warn: (msg: string, data?: unknown) => (data ? log.warn(msg, data) : log.warn(msg)),
  error: (msg: string, data?: unknown) => (data ? log.error(msg, data) : log.error(msg)),
};


