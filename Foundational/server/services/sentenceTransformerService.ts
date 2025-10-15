import { pipeline, FeatureExtractionPipeline } from '@xenova/transformers';
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

export class SentenceTransformerService {
  private model: FeatureExtractionPipeline | null = null;
  private modelName: string = 'Xenova/all-MiniLM-L6-v2';
  private isInitialized: boolean = false;

  constructor(modelName?: string) {
    if (modelName) {
      this.modelName = modelName;
    }
  }

  async initialize(): Promise<void> {
    if (this.isInitialized) {
      return;
    }

    try {
      console.log(`🔄 Loading SentenceTransformer model: ${this.modelName}`);
      this.model = await pipeline('feature-extraction', this.modelName);
      this.isInitialized = true;
      console.log('✅ SentenceTransformer model loaded successfully');
    } catch (error) {
      console.error('❌ Failed to load SentenceTransformer model:', error);
      throw new Error(`Failed to initialize SentenceTransformer: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async generateEmbedding(text: string): Promise<number[]> {
    if (!this.isInitialized || !this.model) {
      await this.initialize();
    }

    try {
      // Clean and prepare the text
      const cleanText = text.trim();
      if (!cleanText) {
        throw new Error('Empty text provided for embedding generation');
      }

      // Generate embedding
      const result = await this.model!(cleanText, { pooling: 'mean', normalize: true });
      
      // Extract the embedding vector from Tensor object
      let embedding: number[];
      
      if (result && typeof result === 'object' && 'data' in result) {
        // Handle Tensor object from @xenova/transformers
        const tensorData = result.data;
        if (Array.isArray(tensorData) || tensorData instanceof Float32Array) {
          embedding = Array.from(tensorData);
        } else {
          throw new Error('Invalid tensor data format');
        }
      } else if (Array.isArray(result)) {
        // If result is an array, flatten it if needed
        if ((result as any[]).length === 1 && Array.isArray((result as any[])[0])) {
          embedding = (result as any[])[0];
        } else {
          embedding = result as number[];
        }
      } else if (result && typeof result === 'object') {
        // Check for other embedding result formats
        if ('embedding' in result && Array.isArray((result as any).embedding)) {
          embedding = (result as any).embedding;
        } else if ('last_hidden_state' in result && Array.isArray((result as any).last_hidden_state)) {
          // For transformer models, we might need to pool the last hidden state
          const hiddenState = (result as any).last_hidden_state;
          if (Array.isArray(hiddenState) && hiddenState.length > 0) {
            // Take the mean of all token embeddings
            const tokenEmbeddings = Array.isArray(hiddenState[0]) ? hiddenState : hiddenState;
            const embeddingDim = tokenEmbeddings[0].length;
            embedding = new Array(embeddingDim).fill(0);
            
            for (let i = 0; i < tokenEmbeddings.length; i++) {
              for (let j = 0; j < embeddingDim; j++) {
                embedding[j] += tokenEmbeddings[i][j];
              }
            }
            
            // Normalize by number of tokens
            for (let j = 0; j < embeddingDim; j++) {
              embedding[j] /= tokenEmbeddings.length;
            }
          } else {
            throw new Error('Invalid hidden state format');
          }
        } else {
          // Try to extract values from the object
          const values = Object.values(result).flat() as number[];
          if (Array.isArray(values) && values.length > 0) {
            embedding = values;
          } else {
            throw new Error('Could not extract embedding from result object');
          }
        }
      } else {
        throw new Error('Unexpected result format from SentenceTransformer');
      }

      // Ensure we have a valid array of numbers
      if (!Array.isArray(embedding) || embedding.length === 0) {
        throw new Error('Invalid embedding format received');
      }

      // Convert to regular numbers and filter out invalid values
      const numericEmbedding = embedding
        .map(val => typeof val === 'number' ? val : Number(val))
        .filter(val => !isNaN(val) && isFinite(val));
        
      if (numericEmbedding.length === 0) {
        throw new Error('No valid numeric values found in embedding');
      }
      
      console.log(`✅ Generated embedding with ${numericEmbedding.length} dimensions`);
      return numericEmbedding;

    } catch (error) {
      console.error('❌ SentenceTransformer embedding generation failed:', error);
      throw new Error(`Failed to generate embedding: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  async generateEmbeddings(texts: string[]): Promise<number[][]> {
    if (!this.isInitialized || !this.model) {
      await this.initialize();
    }

    try {
      const embeddings: number[][] = [];
      
      for (const text of texts) {
        const embedding = await this.generateEmbedding(text);
        embeddings.push(embedding);
      }

      console.log(`✅ Generated ${embeddings.length} embeddings`);
      return embeddings;

    } catch (error) {
      console.error('❌ Batch embedding generation failed:', error);
      throw new Error(`Failed to generate batch embeddings: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  }

  getModelInfo(): { name: string; initialized: boolean } {
    return {
      name: this.modelName,
      initialized: this.isInitialized
    };
  }
}

// Singleton instance
let sentenceTransformerService: SentenceTransformerService | null = null;

export function getSentenceTransformerService(): SentenceTransformerService {
  if (!sentenceTransformerService) {
    sentenceTransformerService = new SentenceTransformerService();
  }
  return sentenceTransformerService;
}

// The class is already exported above, no need to export again
