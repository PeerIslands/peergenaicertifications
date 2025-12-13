import type { Request, Response, NextFunction } from "express";
import { z, ZodError } from "zod";
import { fromZodError } from "zod-validation-error";

/**
 * Validation middleware factory that validates request data against a Zod schema
 * @param schema - Zod schema to validate against
 * @param source - Where to get the data from ('body', 'params', 'query', or 'all')
 */
export function validate(
  schema: z.ZodSchema,
  source: "body" | "params" | "query" | "all" = "body"
) {
  return async (req: Request, res: Response, next: NextFunction) => {
    try {
      let dataToValidate: any;

      if (source === "all") {
        dataToValidate = {
          body: req.body,
          params: req.params,
          query: req.query,
        };
      } else {
        dataToValidate = req[source];
      }

      const validated = await schema.parseAsync(dataToValidate);
      
      // Replace the original data with validated data
      if (source === "all") {
        req.body = validated.body || req.body;
        req.params = validated.params || req.params;
        req.query = validated.query || req.query;
      } else {
        req[source] = validated;
      }

      next();
    } catch (error) {
      if (error instanceof ZodError) {
        const validationError = fromZodError(error);
        return res.status(400).json({
          error: "Validation failed",
          message: validationError.message,
          details: error.errors.map((err) => ({
            path: err.path.join("."),
            message: err.message,
          })),
        });
      }

      return res.status(500).json({
        error: "Internal server error",
        message: "Validation error occurred",
      });
    }
  };
}

