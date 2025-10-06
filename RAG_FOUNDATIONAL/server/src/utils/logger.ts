import pino from "pino";

const isProd = process.env.NODE_ENV === "production";
const level = process.env.LOG_LEVEL || (isProd ? "info" : "debug");

export const logger = pino({
  level,
  base: undefined,
  timestamp: pino.stdTimeFunctions.isoTime,
  transport: isProd
    ? undefined
    : {
        target: "pino-pretty",
        options: {
          colorize: true,
          translateTime: "SYS:standard",
          singleLine: true,
        },
      },
});


