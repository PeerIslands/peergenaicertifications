import OpenAI from 'openai';

const DEFAULT_CHAT_MODEL = 'gpt-4o-mini';
const DEFAULT_CHAT_TEMPERATURE = 0.2;
const DEFAULT_EMBEDDING_MODEL = 'text-embedding-3-small';

function coerceNumberEnv(
  value: string | undefined,
  fallback: number,
  bounds: { min?: number; max?: number } = {},
): number {
  if (!value?.trim()) {
    return fallback;
  }

  const parsed = Number(value);
  if (!Number.isFinite(parsed)) {
    return fallback;
  }

  const { min, max } = bounds;
  let result = parsed;
  if (min !== undefined) {
    result = Math.max(result, min);
  }
  if (max !== undefined) {
    result = Math.min(result, max);
  }
  return result;
}

function coerceStringEnv(value: string | undefined, fallback: string): string {
  return value?.trim() || fallback;
}

export class AIService {
  private openai: OpenAI;
  private chatModel = coerceStringEnv(process.env.OPENAI_CHAT_MODEL, DEFAULT_CHAT_MODEL);
  private chatTemperature = coerceNumberEnv(
    process.env.OPENAI_CHAT_TEMPERATURE,
    DEFAULT_CHAT_TEMPERATURE,
    { min: 0, max: 2 },
  );
  private embeddingModel = coerceStringEnv(process.env.OPENAI_EMBEDDING_MODEL, DEFAULT_EMBEDDING_MODEL);

  constructor() {
    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
      throw new Error('OPENAI_API_KEY is missing');
    }

    this.openai = new OpenAI({
      apiKey: apiKey,
    });
  }

  async answerQuestion(documentContent: string, question: string, filename?: string): Promise<string> {
    try {
      const systemPrompt = `
        You are an AI assistant that answers questions strictly based on the provided document.
        Your responses must be:
        - Concise (max 2-3 sentences)
        - Clear, factual, and written in simple language
        - Based only on the document; do NOT add any external details or explanations.
        If the answer cannot be found in the document, reply exactly: "Not enough information in the document."
        `;

      const userPrompt = `
        Document Name: ${filename || 'Uploaded Document'}

        Document Content:
        ${documentContent}

        Question:
        ${question}

        Answer using only the above document content.
        `;

      const response = await this.openai.chat.completions.create({
        model: this.chatModel,
        messages: [
          {
            role: 'system',
            content: systemPrompt,
          },
          {
            role: 'user',
            content: userPrompt,
          },
        ],
        max_tokens: 220,
        temperature: this.chatTemperature,
      });

      return response.choices[0]?.message?.content || 'Sorry, I could not generate an answer.';
    } catch (error) {
      console.error('OpenAI API error:', error);
      if (error instanceof Error) {
        throw new Error(`Failed to generate answer: ${error.message}`);
      }
      throw new Error('Failed to generate answer due to an unknown error');
    }
  }

  async summarizeDocument(documentContent: string, filename?: string): Promise<string> {
    try {
      const response = await this.openai.chat.completions.create({
        model: this.chatModel,
        messages: [
          {
            role: 'system',
            content: 'You are a helpful AI assistant that creates concise summaries of documents.',
          },
          {
            role: 'user',
            content: `Please provide a brief summary of this document:\n\nDocument: ${filename || 'Uploaded Document'}\n\nContent:\n${documentContent}`,
          },
        ],
        max_tokens: 200,
        temperature: this.chatTemperature,
      });

      return response.choices[0]?.message?.content || 'Unable to generate summary.';
    } catch (error) {
      console.error('OpenAI API error:', error);
      throw new Error('Failed to generate document summary');
    }
  }

  async generateEmbeddings(chunks: string[]): Promise<number[][]> {
    if (chunks.length === 0) {
      return [];
    }

    try {
      const response = await this.openai.embeddings.create({
        model: this.embeddingModel,
        input: chunks,
      });

      return response.data.map(item => item.embedding);
    } catch (error) {
      console.error('OpenAI embeddings error:', error);
      if (error instanceof Error) {
        throw new Error(`Failed to generate embeddings: ${error.message}`);
      }
      throw new Error('Failed to generate embeddings due to an unknown error');
    }
  }
}

export const aiService = new AIService();
