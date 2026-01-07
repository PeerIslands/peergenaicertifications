import { GoogleGenAI } from "@google/genai";

// DON'T DELETE THIS COMMENT
// Note that the newest Gemini model series is "gemini-2.5-flash" or "gemini-2.5-pro"
// do not change this unless explicitly requested by the user

const apiKey = process.env.GEMINI_API_KEY || "";

// Debug logging for API key
console.log("🔑 [GEMINI] API Key Status:");
console.log("   - Key exists:", apiKey ? "YES" : "NO");
console.log("   - Key length:", apiKey.length);
console.log("   - Key prefix:", apiKey ? `${apiKey.substring(0, 10)}...` : "N/A");
console.log("   - Key from env:", process.env.GEMINI_API_KEY ? "YES" : "NO");
console.log("   - All env keys with GEMINI:", Object.keys(process.env).filter(k => k.includes("GEMINI")));

if (!apiKey) {
  console.error("❌ ERROR: GEMINI_API_KEY is not set. Please add it to your .env file.");
  console.error("   Get your API key from: https://aistudio.google.com/app/apikey");
} else if (apiKey.length < 20) {
  console.warn("⚠️  WARNING: API key seems too short. Expected length: ~39 characters");
}

const ai = new GoogleGenAI({ apiKey });
console.log("✅ [GEMINI] GoogleGenAI client initialized");

// Generate embeddings for text using Gemini
export async function generateEmbedding(text: string): Promise<number[]> {
  console.log("🔍 [GEMINI] generateEmbedding called");
  console.log("   - Text length:", text.length);
  console.log("   - Text preview:", text.substring(0, 50) + "...");
  
  try {
    console.log("   - Calling embedContent API...");
    const response = await ai.models.embedContent({
      model: "text-embedding-004",
      contents: text,
    });
    
    console.log("   - ✅ Embedding generated successfully");
    console.log("   - Embedding dimensions:", response.embeddings?.[0]?.values?.length || 0);
    
    return response.embeddings?.[0]?.values || [];
  } catch (error: any) {
    console.error("   - ❌ Error generating embedding:");
    console.error("     - Error type:", error.constructor.name);
    console.error("     - Error message:", error.message);
    console.error("     - Error status:", error.status);
    console.error("     - Error code:", error.code);
    console.error("     - Full error:", JSON.stringify(error, null, 2));
    throw error;
  }
}

// Generate embeddings for multiple texts in batch
export async function generateEmbeddings(texts: string[]): Promise<number[][]> {
  console.log("🔍 [GEMINI] generateEmbeddings called");
  console.log("   - Number of texts:", texts.length);
  
  if (texts.length === 0) {
    console.log("   - ⚠️  No texts to process, returning empty array");
    return [];
  }
  
  const embeddings: number[][] = [];
  
  // Process in batches to avoid rate limits
  for (let i = 0; i < texts.length; i++) {
    const text = texts[i];
    console.log(`   - Processing text ${i + 1}/${texts.length} (length: ${text.length})`);
    
    try {
      const response = await ai.models.embedContent({
        model: "text-embedding-004",
        contents: text,
      });
      
      const embedding = response.embeddings?.[0]?.values || [];
      embeddings.push(embedding);
      console.log(`   - ✅ Text ${i + 1} embedded (dimensions: ${embedding.length})`);
    } catch (error: any) {
      console.error(`   - ❌ Error embedding text ${i + 1}:`);
      console.error("     - Error type:", error.constructor.name);
      console.error("     - Error message:", error.message);
      console.error("     - Error status:", error.status);
      console.error("     - Error code:", error.code);
      if (error.response) {
        console.error("     - Error response:", JSON.stringify(error.response, null, 2));
      }
      throw error;
    }
  }
  
  console.log(`   - ✅ All ${texts.length} embeddings generated successfully`);
  return embeddings;
}

// Chat with RAG context using Gemini
export async function chatWithContext(
  userMessage: string,
  contextChunks: { content: string; page: number; similarity: number }[]
): Promise<string> {
  const contextText = contextChunks
    .map((chunk, i) => `[Context ${i + 1} - Page ${chunk.page}]\n${chunk.content}`)
    .join("\n\n");

  const systemPrompt = `You are a helpful assistant that answers questions based on the provided document context. 
Use the context below to answer the user's question accurately and concisely.
If the context doesn't contain enough information to answer the question, say so.
Always cite which page the information comes from when relevant.

Context from the document:
${contextText}`;

  const response = await ai.models.generateContent({
    model: "gemini-2.5-flash",
    config: {
      systemInstruction: systemPrompt,
    },
    contents: userMessage,
  });

  return response.text || "I couldn't generate a response.";
}
