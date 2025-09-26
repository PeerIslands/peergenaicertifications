import { OllamaEmbeddings } from '@langchain/ollama';

export class EmbeddingsService {
  private embeddings: OllamaEmbeddings;

  constructor() {
    this.embeddings = new OllamaEmbeddings({
      model: 'embeddinggemma', // Using the existing embeddinggemma model
      baseUrl: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
    });
  }

  async generateEmbedding(text: string): Promise<number[]> {
    try {
      const embedding = await this.embeddings.embedQuery(text);
      return embedding;
    } catch (error) {
      console.error('Failed to generate embedding:', error);
      throw error;
    }
  }

  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    try {
      const embeddings = await this.embeddings.embedDocuments(texts);
      return embeddings;
    } catch (error) {
      console.error('Failed to generate embeddings:', error);
      throw error;
    }
  }

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
