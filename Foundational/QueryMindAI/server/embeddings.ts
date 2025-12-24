import { OllamaEmbeddings } from '@langchain/ollama';

/**
 * Service for generating text embeddings using Ollama's embedding models.
 * Provides functionality to convert text into vector representations for semantic search.
 */
export class EmbeddingsService {
  private embeddings: OllamaEmbeddings;

  /**
   * Creates a new EmbeddingsService instance.
   * Initializes Ollama embeddings client with the embeddinggemma model.
   */
  constructor() {
    this.embeddings = new OllamaEmbeddings({
      model: 'embeddinggemma', // Using the existing embeddinggemma model
      baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
    });
  }

  /**
   * Generates an embedding vector for a single text string.
   * 
   * @param text - The text to generate an embedding for
   * @returns A promise that resolves to an array of numbers representing the embedding vector
   * @throws Will throw an error if embedding generation fails
   */
  async generateEmbedding(text: string): Promise<number[]> {
    try {
      const embedding = await this.embeddings.embedQuery(text);
      return embedding;
    } catch (error) {
      console.error('Failed to generate embedding:', error);
      throw error;
    }
  }

  /**
   * Generates embedding vectors for multiple text strings in batch.
   * 
   * @param texts - Array of text strings to generate embeddings for
   * @returns A promise that resolves to an array of embedding vectors (each vector is an array of numbers)
   * @throws Will throw an error if embedding generation fails
   */
  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    try {
      const embeddings = await this.embeddings.embedDocuments(texts);
      return embeddings;
    } catch (error) {
      console.error('Failed to generate embeddings:', error);
      throw error;
    }
  }

  /**
   * Checks if the embedding model (embeddinggemma) is available in the Ollama instance.
   * 
   * @returns A promise that resolves to true if the model is available, false otherwise
   * 
   * @remarks
   * Queries the Ollama API to check if the embeddinggemma model is installed.
   * Logs a warning if the model is not found.
   */
  async isModelAvailable(): Promise<boolean> {
    try {
      const baseUrl = process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
      const response = await fetch(`${baseUrl}/api/tags`);
      
      if (!response.ok) {
        return false;
      }

      const data = await response.json();
      const hasModel = data.models?.some((model: any) => 
        model.name.includes('embeddinggemma')
      );

      if (!hasModel) {
        console.warn('embeddinggemma model not found. Please pull it with: ollama pull embeddinggemma');
      }

      return hasModel;
    } catch (error) {
      console.error('Failed to check embedding model availability:', error);
      return false;
    }
  }
}

export const embeddingsService = new EmbeddingsService();
