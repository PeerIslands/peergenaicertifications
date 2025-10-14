import { storage } from "../storage";
import { chunksCollection } from "../db";
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { BaseRetriever } from "@langchain/core/retrievers";
import { Document as LCDocument } from "@langchain/core/documents";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RunnableMap, RunnableSequence } from "@langchain/core/runnables";
import { StringOutputParser } from "@langchain/core/output_parsers";

function coerceNumberEnv(
  value: string | undefined,
  fallback: number,
  bounds: { min?: number; max?: number } = {}
): number {
  if (!value?.trim()) return fallback;
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) return fallback;
  const { min, max } = bounds;
  let result = parsed;
  if (min !== undefined) result = Math.max(result, min);
  if (max !== undefined) result = Math.min(result, max);
  return result;
}

function coerceStringEnv(value: string | undefined, fallback: string): string {
  return value?.trim() || fallback;
}

function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let na = 0;
  let nb = 0;
  const len = Math.min(a.length, b.length);
  for (let i = 0; i < len; i++) {
    const va = a[i];
    const vb = b[i];
    dot += va * vb;
    na += va * va;
    nb += vb * vb;
  }
  if (na === 0 || nb === 0) return 0;
  return dot / (Math.sqrt(na) * Math.sqrt(nb));
}

class MongoChunkRetriever extends BaseRetriever {
  private documentId: string;
  private topK: number;
  private embeddings: OpenAIEmbeddings;

  constructor(opts: {
    documentId: string;
    topK?: number;
    embeddingModel?: string;
  }) {
    super();
    this.documentId = opts.documentId;
    this.topK = opts.topK ?? 4;
    this.embeddings = new OpenAIEmbeddings({
      model: coerceStringEnv(
        process.env.OPENAI_EMBEDDING_MODEL,
        "text-embedding-3-small"
      ),
    });
  }

  async _getRelevantDocuments(query: string): Promise<LCDocument[]> {
    const vectors = await storage.getDocumentVectors(this.documentId);
    if (!vectors || vectors.embeddings.length === 0) {
      return [];
    }

    const [q] = await this.embeddings.embedDocuments([query]);

    const scored = vectors.embeddings.map((vec, idx) => ({
      idx,
      score: cosineSimilarity(vec, q),
    }));

    scored.sort((a, b) => b.score - a.score);
    const top = scored.slice(0, Math.min(this.topK, scored.length));

    return top.map(
      ({ idx, score }) =>
        new LCDocument({
          pageContent: vectors.chunks[idx],
          metadata: { docId: this.documentId, chunkIndex: idx, score },
        })
    );
  }
}

function formatDocsAsContext(docs: LCDocument[]): string {
  return docs
    .map((d) => `Chunk #${d.metadata?.chunkIndex}\n${d.pageContent}`)
    .join("\n\n---\n\n");
}

export class RAGService {
  private chatModelName = coerceStringEnv(
    process.env.OPENAI_CHAT_MODEL,
    "gpt-4o-mini"
  );
  private chatTemperature = coerceNumberEnv(
    process.env.OPENAI_CHAT_TEMPERATURE,
    0.2,
    { min: 0, max: 2 }
  );

  private buildChain(retriever: BaseRetriever) {
    const prompt = ChatPromptTemplate.fromMessages([
      [
        "system",
        [
          "You are an AI assistant that answers questions based on the provided document context.",
          "Use only information that can be supported by the context, but you may infer or summarize ideas in your own clear words.",
          "Keep answers short (1-3 sentences), simple, and easy to understand.",
          "Do not add outside facts.",
          "If the answer truly cannot be inferred or found, reply exactly: Not enough information in the document.",
          "Cite chunk numbers inline when helpful (e.g., [#2]).",
        ].join(" \n"),
      ],
      ["human", ["Context:\n{context}", "\nQuestion: {question}"].join("")],
    ]);

    const model = new ChatOpenAI({
      model: this.chatModelName,
      temperature: this.chatTemperature,
    });

    const setup = RunnableMap.from<
      { question: string },
      { context: string; question: string }
    >({
      context: RunnableSequence.from([
        (input: { question: string }) => input.question,
        retriever,
        formatDocsAsContext,
      ]),
      question: (input) => input.question,
    });

    return RunnableSequence.from([
      setup,
      prompt,
      model,
      new StringOutputParser(),
    ]);
  }

  async answer(
    documentId: string,
    question: string,
    topK: number = 4
  ): Promise<{
    answer: string;
    sources: Array<{ chunkIndex: number; score: number }>;
  }> {
    const retriever = new MongoChunkRetriever({ documentId, topK });

    // Run chain for answer
    const chain = this.buildChain(retriever);
    const answer = await chain.invoke({ question });

    // Also fetch sources
    const docs = await retriever.getRelevantDocuments(question);
    const sources = docs.map((d) => ({
      chunkIndex: Number(d.metadata?.chunkIndex ?? -1),
      score: Number(d.metadata?.score ?? 0),
    }));

    return { answer, sources };
  }


  async answerGlobal(
    question: string,
    topK: number = 6,
    docIds?: string[]
  ): Promise<{
    answer: string;
    sources: Array<{ docId: string; chunkIndex: number; score: number }>;
  }> {
    class GlobalChunkRetriever extends BaseRetriever {
      private topK: number;
      private embeddings: OpenAIEmbeddings;
      private filterDocIds?: Set<string>;
      constructor(opts: {
        topK: number;
        embeddingModel?: string;
        docIds?: string[];
      }) {
        super();
        this.topK = opts.topK;
        this.embeddings = new OpenAIEmbeddings({
          model: coerceStringEnv(
            process.env.OPENAI_EMBEDDING_MODEL,
            "text-embedding-3-small"
          ),
        });
        this.filterDocIds =
          opts.docIds && opts.docIds.length ? new Set(opts.docIds) : undefined;
      }
      async _getRelevantDocuments(query: string): Promise<LCDocument[]> {
        const [q] = await this.embeddings.embedDocuments([query]);
        const cursor = chunksCollection().find({}, { projection: { _id: 0 } });
        const all: Array<{
          docId: string;
          chunkIndex: number;
          text: string;
          embedding: number[];
        }> = [];
        for await (const rec of cursor) {
          if (this.filterDocIds && !this.filterDocIds.has(rec.docId)) continue;
          all.push({
            docId: rec.docId,
            chunkIndex: rec.chunkIndex,
            text: rec.text,
            embedding: rec.embedding,
          });
        }
        const scored = all.map((r) => ({
          r,
          score: cosineSimilarity(r.embedding, q),
        }));
        scored.sort((a, b) => b.score - a.score);
        const top = scored.slice(0, Math.min(this.topK, scored.length));
        return top.map(
          ({ r, score }) =>
            new LCDocument({
              pageContent: r.text,
              metadata: { docId: r.docId, chunkIndex: r.chunkIndex, score },
            })
        );
      }
    }

    const retriever = new GlobalChunkRetriever({ topK, docIds });
    const chain = this.buildChain(retriever);
    const answer = await chain.invoke({ question });
    const docs = await retriever.getRelevantDocuments(question);
    const sources = docs.map((d) => ({
      docId: String(d.metadata?.docId ?? ""),
      chunkIndex: Number(d.metadata?.chunkIndex ?? -1),
      score: Number(d.metadata?.score ?? 0),
    }));
    return { answer, sources };
  }
}

export const ragService = new RAGService();
