/**
 * New RAG Service - Refactored Architecture
 * 
 * This file provides a clean interface to the new service architecture.
 * It maintains backward compatibility while using the new modular design.
 */

import { RAGOrchestrator, ConfigService, type RAGResponse, type LLMParameters } from "./services";

// Singleton instance for backward compatibility
let ragOrchestrator: RAGOrchestrator | null = null;

/**
 * Get the RAG service instance (backward compatibility)
 * @deprecated Use RAGOrchestrator directly for new code
 */
export function getRAGService(): {
  initialize(): Promise<void>;
  search(query: string, k?: number, llmParams?: LLMParameters): Promise<RAGResponse>;
  close(): Promise<void>;
} {
  if (!ragOrchestrator) {
    const configService = ConfigService.getInstance();
    ragOrchestrator = new RAGOrchestrator(configService.getConfig());
  }

  return {
    async initialize(): Promise<void> {
      await ragOrchestrator!.initialize();
    },

    async search(query: string, k: number = 5, llmParams?: LLMParameters): Promise<RAGResponse> {
      return await ragOrchestrator!.search(query, k, llmParams);
    },

    async close(): Promise<void> {
      await ragOrchestrator!.close();
    }
  };
}

/**
 * Get the RAG orchestrator instance (recommended for new code)
 */
export function getRAGOrchestrator(): RAGOrchestrator {
  if (!ragOrchestrator) {
    const configService = ConfigService.getInstance();
    ragOrchestrator = new RAGOrchestrator(configService.getConfig());
  }
  return ragOrchestrator;
}

/**
 * Get the configuration service instance
 */
export function getConfigService(): ConfigService {
  return ConfigService.getInstance();
}

// Re-export types for backward compatibility
export type { RAGResponse, LLMParameters } from "./services";
export type { RAGConfig } from "./services/ragOrchestrator";
