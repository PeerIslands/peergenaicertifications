// Performance trade-offs: moderate chunking, batched embeddings, short history, minimal k, retry on 429
import OpenAI from "openai";
import { storage } from "./storage";
import { getDb } from "../db/mongo";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { logger } from "../utils/logger";
// LangChain vector store: MongoDBAtlasVectorSearch integrates Atlas Vector Search
import { MongoDBAtlasVectorSearch } from "@langchain/mongodb";
import { OpenAIEmbeddings } from "@langchain/openai";

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
  apiKey: process.env.OPENAI_API_KEY
});
const EMBEDDING_MODEL = process.env.OPENAI_EMBEDDING_MODEL || "text-embedding-3-large";
// Expected embedding dimensions based on model; used to detect mismatch and trigger reindex
const EXPECTED_EMBED_DIM = /text-embedding-3-small/i.test(EMBEDDING_MODEL) ? 1536 : 3072;
const COMPLETION_MODEL = process.env.OPENAI_CHAT_MODEL || "gpt-5";

// Tunables (with reasonable defaults)
// Performance trade-offs: tunables for chunking, batching, top-k and fallbacks
const CHUNK_SIZE = Math.max(1, Number(process.env.RAG_CHUNK_SIZE || 1000));
const CHUNK_OVERLAP = Math.max(0, Number(process.env.RAG_CHUNK_OVERLAP || 150));
const EMBED_BATCH_SIZE = Math.max(1, Number(process.env.RAG_EMBED_BATCH_SIZE || 64));
const RAG_TOP_K = Math.max(1, Number(process.env.RAG_TOP_K || 1));
const FULLTEXT_PDF_LIMIT = Math.max(1, Number(process.env.RAG_FULLTEXT_PDFS || 3));

const USE_ATLAS_VECTOR = String(process.env.MONGODB_VECTOR_SEARCH || "").toLowerCase() === "true";
let atlasVectorSearchAvailable = USE_ATLAS_VECTOR;
const VECTOR_INDEX_NAME = process.env.MONGODB_VECTOR_INDEX_NAME || "vector_index";

async function chunkText(text: string, chunkSize = CHUNK_SIZE, overlap = CHUNK_OVERLAP): Promise<string[]> {
  const cleaned = (text || "").replace(/\s+/g, " ").trim();
  if (!cleaned) return [];
  const splitter = new RecursiveCharacterTextSplitter({ chunkSize, chunkOverlap: overlap });
  return splitter.splitText(cleaned);
}

async function embedBatch(texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];
  const maxRetries = 3;
  let attempt = 0;
  // Exponential backoff with jitter for 429/insufficient_quota
  while (true) {
    try {
      const res = await openai.embeddings.create({ model: EMBEDDING_MODEL, input: texts });
      return res.data.map((d) => d.embedding as number[]);
    } catch (err: any) {
      const status = err?.status || err?.code;
      const code = err?.code || err?.error?.code;
      const message: string = err?.message || err?.error?.message || "";
      const isRateLimited = status === 429 || code === "insufficient_quota" || /quota|rate limit/i.test(message);
      if (!isRateLimited || attempt >= maxRetries) {
        logger.error({ err: message || err }, "Embedding failed");
        throw err;
      }
      const delayMs = Math.min(2000 * Math.pow(2, attempt), 15000) + Math.floor(Math.random() * 300);
      logger.warn({ attempt: attempt + 1, delayMs }, "Embedding rate limited, retrying with backoff");
      await new Promise((r) => setTimeout(r, delayMs));
      attempt++;
    }
  }
}

export async function indexPdfInVectorStore(userId: string, params: { pdfId: string; originalName?: string; text: string }): Promise<number> {
  const db = await getDb();
  const vectorsCol = db.collection<VectorDoc>("vectors");
  const chunks = await chunkText(params.text);
  if (chunks.length === 0) return 0;

  logger.info({ userId, pdfId: params.pdfId, chunks: chunks.length }, "Indexing PDF into vector store");

  // If Atlas Vector Search is enabled, use LangChain's MongoDBAtlasVectorSearch for indexing
  if (atlasVectorSearchAvailable) {
    try {
      // Clear existing vectors for this PDF to avoid duplicates
      // Pre-filter delete by userId + pdfId to avoid touching other tenants' data
      await vectorsCol.deleteMany({ userId, pdfId: params.pdfId } as any);

      const embeddings = new OpenAIEmbeddings({ apiKey: process.env.OPENAI_API_KEY, model: EMBEDDING_MODEL });
      await MongoDBAtlasVectorSearch.fromTexts(
        chunks,
        chunks.map((_, idx) => ({ userId, pdfId: params.pdfId, originalName: params.originalName, index: idx, createdAt: new Date() })),
        embeddings,
        { collection: vectorsCol as any, indexName: VECTOR_INDEX_NAME, textKey: "text", embeddingKey: "embedding" }
      );
      logger.info({ userId, pdfId: params.pdfId, chunkDocs: chunks.length }, "Indexed PDF into Atlas vector store via LangChain");
      return chunks.length;
    } catch (e: any) {
      const message = e?.message || String(e);
      logger.error({ err: message }, "LangChain Atlas indexing failed; falling back to local embeddings");
      // fall through to local embedding path
    }
  }

  // Local embedding + Mongo storage path (fallback when Atlas path is unavailable)
  const embeddings: number[][] = [];
  const batchSize = EMBED_BATCH_SIZE;
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
  logger.info({ userId, pdfId: params.pdfId, chunkDocs: docs.length }, "Indexed PDF into vector store");
  return docs.length;
}

export async function ensureUserVectors(userId: string): Promise<void> {
  const db = await getDb();
  const vectorsCol = db.collection("vectors");
  const pdfs = await storage.getPdfs(userId);
  for (const pdf of pdfs) {
    const existing = await vectorsCol.findOne({ userId, pdfId: pdf.id });
    const needsReindex = existing && Array.isArray((existing as any).embedding) && ((existing as any).embedding.length !== EXPECTED_EMBED_DIM);
    if (!existing || needsReindex) {
      const text = (pdf as any).extractedText || "";
      if (text.trim()) {
        // Remove old vectors (if any) for this pdf to avoid dimension mismatch and duplicates
        if (needsReindex) {
          await vectorsCol.deleteMany({ userId, pdfId: pdf.id } as any);
        }
        await indexPdfInVectorStore(userId, { pdfId: pdf.id, originalName: (pdf as any).originalName, text });
      }
    }
  }
}

export async function retrieveContextForQuery(userId: string, query: string, k = RAG_TOP_K, pdfId?: string) {
  const db = await getDb();
  const vectorsCol = db.collection<VectorDoc>("vectors");
  const [queryEmbedding] = await embedBatch([query]);

  if (atlasVectorSearchAvailable) {
    try {
      logger.info({ userId, k, pdfId }, "Retrieving context using Atlas Vector Search");
      const cursor = vectorsCol.aggregate([
        {
          // Pre-filter by userId (and optional pdfId) inside $vectorSearch
          // to reduce candidates before cosine similarity scoring
          $vectorSearch: {
            index: VECTOR_INDEX_NAME,
            path: "embedding",
            queryVector: queryEmbedding,
            numCandidates: 200,
            limit: Math.max(k * 4, 20),
            filter: pdfId ? { userId, pdfId } : { userId },
          },
        },
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
      logger.debug({ candidates: docs.length }, "Atlas vector search returned candidates");
      const limited = docs.slice(0, Math.max(1, Math.min(k, docs.length)));
      logger.info({ returned: limited.length }, "Atlas vector search selected results");
      if (limited.length > 0) {
        return limited.map((d) => ({
          id: `${d.pdfId}:${d.index}`,
          text: d.text,
          metadata: { pdfId: d.pdfId, originalName: d.originalName, index: d.index },
          embedding: d.embedding,
        }));
      }
      // If Atlas returned no results, fall through to local similarity
      logger.info({ userId, k, pdfId }, "Atlas returned 0 results, falling back to local similarity");
    } catch (err) {
      atlasVectorSearchAvailable = false;
      const message = (err as any)?.message || String(err);
      logger.error({ message }, "Vector search disabled after error; using local similarity");
    }
  }

  logger.info({ userId, k, pdfId }, "Retrieving context using local similarity");
  // Pre-filter local similarity pool by userId (and optional pdfId)
  const all = await vectorsCol.find(pdfId ? { userId, pdfId } : { userId }).toArray();
  const scored = all.map((c) => ({ c, score: cosineSimilarity(queryEmbedding, c.embedding as number[]) }));
  scored.sort((a, b) => b.score - a.score);
  const selected = scored.slice(0, Math.max(0, Math.min(k, scored.length)));
  logger.debug({ pool: all.length, selected: selected.length, topScore: selected[0]?.score }, "Local similarity results");

  if (selected.length > 0 && (selected[0].score ?? 0) >= 0.2) {
    return selected.map((s) => ({
      id: `${s.c.pdfId}:${s.c.index}`,
      text: s.c.text,
      metadata: { pdfId: s.c.pdfId, originalName: s.c.originalName, index: s.c.index },
      embedding: s.c.embedding as number[],
    }));
  }

  try {
    logger.info({ userId, pdfId }, "Retrieving context using full-text fallback");
    const pdfsCol = db.collection<any>("pdfs");
    let pdfs: Array<{ id: string; originalName?: string; extractedText?: string }>; 
    if (pdfId) {
      // Pre-filter full-text to a specific PDF owned by the user
      const one = await pdfsCol.findOne({ id: pdfId, userId });
      pdfs = one ? [one] : [];
    } else {
      // Text search pre-filtered by userId for multi-tenant isolation
      const cursor = pdfsCol
        .find(
          { userId, $text: { $search: query } },
          { projection: { id: 1, originalName: 1, extractedText: 1, score: { $meta: "textScore" } } } as any,
        )
        .sort({ score: { $meta: "textScore" } })
        .limit(FULLTEXT_PDF_LIMIT);
      pdfs = await cursor.toArray();
    }
    logger.debug({ matchedPdfs: pdfs.length }, "Full-text search PDF matches");

    const chunkCandidates: Array<{ pdfId: string; originalName?: string; index: number; text: string; score: number; embedding: number[] }>= [];
    for (const pdf of pdfs) {
      const text: string = (pdf?.extractedText || "").toString();
      if (!text.trim()) continue;
      const chunks = await chunkText(text);
      if (chunks.length === 0) continue;

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
      logger.info({ candidates: chunkCandidates.length, returned: topChunks.length }, "Full-text fallback selected results");
      return topChunks.map((c) => ({
        id: `${c.pdfId}:${c.index}`,
        text: c.text,
        metadata: { pdfId: c.pdfId, originalName: c.originalName, index: c.index },
        embedding: c.embedding,
      }));
    }
  } catch (e) {
    logger.error({ err: e }, "Full-text fallback search failed");
  }

  return [] as Array<{ id: string; text: string; metadata: any; embedding: number[] }>;
}

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

export async function answerWithRag(params: {
  userId: string;
  messages: Array<{ role: string; content: string }>;
  pdfId?: string;
}) {
  const { userId, messages, pdfId } = params;
  const lastUser = [...messages].reverse().find((m) => m.role === "user");
  const question = lastUser?.content?.trim() || "";
  logger.info({ userId, qlen: question.length, pdfId }, "RAG answering started");
  await ensureUserVectors(userId);
  const top = await retrieveContextForQuery(userId, question, 1, pdfId);
  logger.debug({ sources: top.length }, "RAG retrieved context sources");

  const contextBlocks = top.map((t, i) => `# Source ${i + 1} (${t.metadata.originalName || t.metadata.pdfId})\n${t.text}`).join("\n\n");
  const historyStr = messages
    .slice(-8)
    .map((m) => `${m.role}: ${m.content}`)
    .join("\n");

  const prompt = [
    { role: "system", content: "You are a helpful RAG assistant. Use the provided sources to answer. Respond in a compact narrative style (2–4 sentences), with no bullet points or headings. Be concise and direct. Cite source numbers like [1], [2]. If the sources do not contain the answer, say you don't know." },
    { role: "user", content: `Context sources (may be partial):\n\n${contextBlocks}\n\nConversation so far:\n${historyStr}\n\nUser question: ${question}\n\nAnswer grounded in the context, cite [n].` },
  ] as const;

  const normalizedPrimary = COMPLETION_MODEL;
  const candidateModels = Array.from(new Set([
    normalizedPrimary
  ]));

  let completion: any | undefined;
  let lastError: any;
  for (const model of candidateModels) {
    try {
      const shouldPassControls = !/^gpt-5$/i.test(model);
      const params: any = { model, messages: prompt as any };
      if (shouldPassControls) {
        params.temperature = Number(process.env.OPENAI_TEMPERATURE ?? 0.2);
        params.max_tokens = Number(process.env.OPENAI_MAX_TOKENS ?? 220);
      }
      logger.info({ model }, "Calling chat completion");
      completion = await createChatCompletionWithRetry(params);
      break;
    } catch (err: any) {
      lastError = err;
      const status = err?.status || err?.code;
      const msg = err?.message || "";
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
  logger.info({ chars: reply.length, sources: top.length }, "RAG answer ready");
  const sources = top.map((t) => ({
    pdfId: t.metadata.pdfId,
    originalName: t.metadata.originalName,
    preview: t.text.slice(0, 300),
  }));

  return { reply, sources };
}

async function createChatCompletionWithRetry(params: any): Promise<any> {
  const maxRetries = 3;
  let attempt = 0;
  while (true) {
    try {
      return await openai.chat.completions.create(params);
    } catch (err: any) {
      const status = err?.status || err?.code;
      const code = err?.code || err?.error?.code;
      const message: string = err?.message || err?.error?.message || "";
      const isRateLimited = status === 429 || code === "insufficient_quota" || /quota|rate limit/i.test(message);
      if (!isRateLimited || attempt >= maxRetries) {
        throw err;
      }
      const delayMs = Math.min(2000 * Math.pow(2, attempt), 15000) + Math.floor(Math.random() * 300);
      logger.warn({ attempt: attempt + 1, delayMs }, "Chat rate limited, retrying with backoff");
      await new Promise((r) => setTimeout(r, delayMs));
      attempt++;
    }
  }
}