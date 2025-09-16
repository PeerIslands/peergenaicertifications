import OpenAI from "openai";
import { storage } from "./storage";
import { getDb } from "./mongo";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";

type VectorDoc = {
  userId: string;
  pdfId: string;
  originalName?: string;
  index: number;
  text: string;
  embedding: number[];
  createdAt: Date;
};

const openai = new OpenAI({ 
  apiKey: process.env.OPENAI_API_KEY,
  // Allow routing to OpenAI-compatible providers (e.g., VoyageAI/OpenRouter)
  baseURL: process.env.OPENAI_BASE_URL || undefined,
});
// Supports OpenAI and OpenAI-compatible providers. Example: OPENAI_EMBEDDING_MODEL=voyage-3-large
const EMBEDDING_MODEL = process.env.OPENAI_EMBEDDING_MODEL || "text-embedding-3-small";
const COMPLETION_MODEL = process.env.OPENAI_CHAT_MODEL || "gpt-5";

const USE_ATLAS_VECTOR = String(process.env.MONGODB_VECTOR_SEARCH || "").toLowerCase() === "true";
let atlasVectorSearchAvailable = USE_ATLAS_VECTOR;
const VECTOR_INDEX_NAME = process.env.MONGODB_VECTOR_INDEX_NAME || "vector_index";

/* -------------------------------------------------------------------------- */
/*                              1. LOAD & SPLIT                               */
/* -------------------------------------------------------------------------- */

/**
 * Splits long text into smaller overlapping chunks.
 * Ensures embeddings can be created efficiently while keeping context.
 *
 * Use case:
 * - A 20-page PDF is split into 1000-character chunks with 150-character overlap.
 */
async function chunkText(text: string, chunkSize = 1000, overlap = 150): Promise<string[]> {
  const cleaned = (text || "").replace(/\s+/g, " ").trim();
  if (!cleaned) return [];
  const splitter = new RecursiveCharacterTextSplitter({ chunkSize, chunkOverlap: overlap });
  return splitter.splitText(cleaned);
}

/* -------------------------------------------------------------------------- */
/*                                  2. EMBED                                  */
/* -------------------------------------------------------------------------- */

/**
 * Creates vector embeddings for an array of text chunks using OpenAI embeddings API.
 *
 * Use case:
 * - ["Bank offers loans", "Interest rate is 5%"] → [[0.3, 0.4, ...], [0.7, 1.4, ...]]
 */
async function embedBatch(texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];
  const res = await openai.embeddings.create({ model: EMBEDDING_MODEL, input: texts });
  return res.data.map((d) => d.embedding as number[]);
}


/* -------------------------------------------------------------------------- */
/*                                  3. STORE                                  */
/* -------------------------------------------------------------------------- */

/**
 * Splits text → embeds chunks → stores vectors in MongoDB with metadata.
 * Ensures re-indexing by upserting existing chunks.
 *
 * Use case:
 * - When a new PDF is uploaded, its text is chunked, embedded, and stored in DB.
 */
export async function indexPdfInVectorStore(userId: string, params: { pdfId: string; originalName?: string; text: string }): Promise<number> {
  const db = await getDb();
  const vectorsCol = db.collection<VectorDoc>("vectors");
  const chunks = await chunkText(params.text);
  if (chunks.length === 0) return 0;

  // Create embeddings in batches
  const embeddings: number[][] = [];
  const batchSize = 64;
  for (let i = 0; i < chunks.length; i += batchSize) {
    const batch = chunks.slice(i, i + batchSize);
    const batchEmbeds = await embedBatch(batch);
    embeddings.push(...batchEmbeds);
  }

  const docs: VectorDoc[] = chunks.map((c, idx) => ({
    userId,
    pdfId: params.pdfId,
    originalName: params.originalName,
    index: idx,
    text: c,
    embedding: embeddings[idx] || [],
    createdAt: new Date(),
  }));

  // Upsert each doc to allow re-indexing
  const ops = docs.map((d) => ({
    updateOne: {
      filter: { userId: d.userId, pdfId: d.pdfId, index: d.index },
      update: { $set: d },
      upsert: true,
    },
  }));
  if (ops.length > 0) {
    await vectorsCol.bulkWrite(ops as any, { ordered: false });
  }
  return docs.length;
}

/**
 * Ensures all uploaded PDFs for a user are embedded and stored.
 * If not already in DB, extracts text and indexes them.
 *
 * Use case:
 * - When answering a query, first check if embeddings exist. If not, create them.
 */
export async function ensureUserVectors(userId: string): Promise<void> {
  const db = await getDb();
  const vectorsCol = db.collection("vectors");
  const pdfs = await storage.getPdfs(userId);
  for (const pdf of pdfs) {
    const existing = await vectorsCol.findOne({ userId, pdfId: pdf.id });
    if (!existing) {
      const text = (pdf as any).extractedText || "";
      if (text.trim()) {
        await indexPdfInVectorStore(userId, { pdfId: pdf.id, originalName: (pdf as any).originalName, text });
      }
    }
  }
}

/* -------------------------------------------------------------------------- */
/*                                 4. RETRIEVE                                */
/* -------------------------------------------------------------------------- */

/**
 * Retrieves the top-k most relevant chunks for a given query.
 * Uses Atlas vector search if available, otherwise falls back to local cosine similarity.
 *
 * Use case:
 * - Query: "What is the interest rate?" → retrieves top 2 relevant chunks mentioning rates.
 */
export async function retrieveContextForQuery(userId: string, query: string, k = 2) {
  const db = await getDb();
  const vectorsCol = db.collection<VectorDoc>("vectors");
  const [queryEmbedding] = await embedBatch([query]);

  // Prefer Atlas vector search if enabled
  if (atlasVectorSearchAvailable) {
    try {
      const cursor = vectorsCol.aggregate([
        {
          $vectorSearch: {
            index: VECTOR_INDEX_NAME,
            path: "embedding",
            queryVector: queryEmbedding,
            numCandidates: 200,
            limit: Math.max(k * 4, 20),
          },
        },
        // Post-filter by userId to avoid requiring tokenized filter fields in the index
        { $match: { userId } },
        {
          $project: {
            userId: 1,
            pdfId: 1,
            originalName: 1,
            index: 1,
            text: 1,
            embedding: 1,
            score: { $meta: "vectorSearchScore" },
          },
        },
      ] as any);
      const docs = await cursor.toArray();
      const limited = docs.slice(0, Math.max(1, Math.min(k, docs.length)));
      return limited.map((d) => ({
        id: `${d.pdfId}:${d.index}`,
        text: d.text,
        metadata: { pdfId: d.pdfId, originalName: d.originalName, index: d.index },
        embedding: d.embedding,
      }));
    } catch (err) {
      atlasVectorSearchAvailable = false;
      const message = (err as any)?.message || String(err);
      console.warn("Vector search disabled after error; using local similarity:", message);
    }
  }

  // Fallback: local similarity over existing vectors
  const all = await vectorsCol.find({ userId }).toArray();
  const scored = all.map((c) => ({ c, score: cosineSimilarity(queryEmbedding, c.embedding as number[]) }));
  scored.sort((a, b) => b.score - a.score);
  const selected = scored.slice(0, Math.max(0, Math.min(k, scored.length)));

  // If vectors exist and are reasonably relevant, return them
  if (selected.length > 0 && (selected[0].score ?? 0) >= 0.2) {
    return selected.map((s) => ({
      id: `${s.c.pdfId}:${s.c.index}`,
      text: s.c.text,
      metadata: { pdfId: s.c.pdfId, originalName: s.c.originalName, index: s.c.index },
      embedding: s.c.embedding as number[],
    }));
  }

  // Final fallback: full-text search over PDF extracted text, then pick best-matching chunks
  try {
    const pdfsCol = db.collection<any>("pdfs");
    const cursor = pdfsCol
      .find(
        { userId, $text: { $search: query } },
        { projection: { id: 1, originalName: 1, extractedText: 1, score: { $meta: "textScore" } } } as any,
      )
      .sort({ score: { $meta: "textScore" } })
      .limit(3);
    const pdfs = await cursor.toArray();

    const chunkCandidates: Array<{ pdfId: string; originalName?: string; index: number; text: string; score: number; embedding: number[] }>= [];
    for (const pdf of pdfs) {
      const text: string = (pdf?.extractedText || "").toString();
      if (!text.trim()) continue;
      const chunks = await chunkText(text);
      if (chunks.length === 0) continue;

      // Score chunks by embedding similarity
      // Batch embeddings for efficiency
      const embeddings = await embedBatch(chunks);
      for (let i = 0; i < chunks.length; i++) {
        const emb = embeddings[i] || [];
        const sim = emb.length ? cosineSimilarity(queryEmbedding, emb) : 0;
        chunkCandidates.push({
          pdfId: pdf.id,
          originalName: pdf.originalName,
          index: i,
          text: chunks[i],
          score: sim,
          embedding: emb,
        });
      }
    }

    if (chunkCandidates.length > 0) {
      chunkCandidates.sort((a, b) => b.score - a.score);
      const topChunks = chunkCandidates.slice(0, Math.max(1, Math.min(k, chunkCandidates.length)));
      return topChunks.map((c) => ({
        id: `${c.pdfId}:${c.index}`,
        text: c.text,
        metadata: { pdfId: c.pdfId, originalName: c.originalName, index: c.index },
        embedding: c.embedding,
      }));
    }
  } catch (e) {
    console.warn("Full-text fallback search failed:", e);
  }

  // Nothing found
  return [] as Array<{ id: string; text: string; metadata: any; embedding: number[] }>;
}

/**
 * Computes cosine similarity between two embeddings.
 *
 * Use case:
 * - Compare user query embedding with document chunk embedding → higher score = more relevant.
 */
function cosineSimilarity(a: number[], b: number[]): number {
  let dot = 0;
  let na = 0;
  let nb = 0;
  for (let i = 0; i < a.length; i++) {
    const va = a[i];
    const vb = b[i];
    dot += va * vb;
    na += va * va;
    nb += vb * vb;
  }
  return dot / (Math.sqrt(na) * Math.sqrt(nb) + 1e-12);
}


/* -------------------------------------------------------------------------- */
/*                               5. GENERATION                                */
/* -------------------------------------------------------------------------- */

/**
 * Answers user queries with Retrieval-Augmented Generation (RAG).
 * - Ensures embeddings exist
 * - Retrieves top chunks
 * - Builds grounded prompt with citations
 * - Calls GPT to generate final answer
 *
 * Use case:
 * - User: "What is the interest rate?"
 * - Answer: "The interest rate is 5% [1]."
 */
export async function answerWithRag(params: {
  userId: string;
  messages: Array<{ role: string; content: string }>;
}) {
  const { userId, messages } = params;
  const lastUser = [...messages].reverse().find((m) => m.role === "user");
  const question = lastUser?.content?.trim() || "";
  
  await ensureUserVectors(userId);
  const top = await retrieveContextForQuery(userId, question, 1);

  const contextBlocks = top.map((t, i) => `# Source ${i + 1} (${t.metadata.originalName || t.metadata.pdfId})\n${t.text}`).join("\n\n");
  const historyStr = messages
    .slice(-8)
    .map((m) => `${m.role}: ${m.content}`)
    .join("\n");

  const prompt = [
    {
      role: "system",
      content:
        "You are a helpful RAG assistant. Use the provided sources to answer. Respond in a compact narrative style (2–4 sentences), with no bullet points or headings. Be concise and direct. Cite source numbers like [1], [2]. If the sources do not contain the answer, say you don't know.",
    },
    {
      role: "user",
      content: `Context sources (may be partial):\n\n${contextBlocks}\n\nConversation so far:\n${historyStr}\n\nUser question: ${question}\n\nAnswer grounded in the context, cite [n].`,
    },
  ] as const;

  // Normalize common typos (e.g., "gpt-o4-mini" -> "gpt-4o-mini") and try fallbacks
  const normalizedPrimary = COMPLETION_MODEL;
  const candidateModels = Array.from(new Set([
    normalizedPrimary
  ]));

  let completion: any | undefined;
  let lastError: any;
  for (const model of candidateModels) {
    try {
      const shouldPassControls = !/^gpt-5$/i.test(model);
      const params: any = {
        model,
        messages: prompt as any,
      };
      if (shouldPassControls) {
        params.temperature = Number(process.env.OPENAI_TEMPERATURE ?? 0.2);
        params.max_tokens = Number(process.env.OPENAI_MAX_TOKENS ?? 220);
      }
      completion = await openai.chat.completions.create(params);
      break;
    } catch (err: any) {
      lastError = err;
      const status = err?.status || err?.code;
      const msg = err?.message || "";
      // If model not found/accessible, try next candidate; otherwise rethrow
      if (status === 404 || /does not exist|not found|no access/i.test(msg)) {
        continue;
      }
      throw err;
    }
  }

  if (!completion) {
    throw lastError || new Error("OpenAI chat completion failed with all fallback models");
  }

  const reply = completion.choices?.[0]?.message?.content ?? "";
  const sources = top.map((t) => ({
    pdfId: t.metadata.pdfId,
    originalName: t.metadata.originalName,
    preview: t.text.slice(0, 300),
  }));

  return { reply, sources };
}
