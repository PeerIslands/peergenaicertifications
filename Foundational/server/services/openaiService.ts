import { ChatOpenAI } from "@langchain/openai";
// import { OpenAIEmbeddings } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { RunnableSequence } from "@langchain/core/runnables";
import { JsonOutputParser } from "@langchain/core/output_parsers";

// Using OpenRouter with openai/gpt-oss-20b:free model
const openai = new ChatOpenAI({ 
  apiKey: process.env.OPENROUTER_API_KEY || "",
  configuration: {
    baseURL: "https://openrouter.ai/api/v1",
    defaultHeaders: {
      "HTTP-Referer": "https://replit.com",
      "X-Title": "RAG Intelligence"
    }
  },
  modelName: "openai/gpt-oss-20b:free",
  maxTokens: 1000,
  temperature: 0.3,
});


// Debug: Log API key status (remove in production)
console.log('OpenRouter API Key loaded:', process.env.OPENROUTER_API_KEY ? 'Yes' : 'No');
console.log('API Key length:', process.env.OPENROUTER_API_KEY ? process.env.OPENROUTER_API_KEY.length : 0);

export interface SearchContext {
  query: string;
  relevantChunks: Array<{
    content: string;
    documentName: string;
    pageNumber?: number;
    similarity: number;
  }>;
}

// Generate embeddings using hash-based method only
export async function generateEmbedding(text: string): Promise<number[]> {
  // Create a simple hash-based embedding
  // This is a basic implementation for demonstration - in production you'd want proper embeddings
  const words = text.toLowerCase().split(/\s+/);
  const embedding = new Array(384).fill(0); // 384-dimensional vector
  
  // Simple character-based hashing for embedding generation
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    for (let j = 0; j < word.length; j++) {
      const charCode = word.charCodeAt(j);
      const index = (charCode + i + j) % embedding.length;
      embedding[index] += Math.sin(charCode + i) * 0.1;
    }
  }
  
  // Normalize the vector
  const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
  return embedding.map(val => magnitude > 0 ? val / magnitude : 0);
}

// Create a LangChain prompt template for RAG responses
const ragPrompt = PromptTemplate.fromTemplate(`
You are an intelligent document analysis assistant. Based on the provided document excerpts, answer the user's question comprehensively and accurately.

User Question: {query}

Relevant Document Excerpts:
{context}

Instructions:
1. Provide a detailed, well-structured answer based solely on the provided document excerpts
2. If the documents don't contain enough information to fully answer the question, acknowledge this
3. Use specific details and examples from the documents when possible
4. Maintain a professional, informative tone
5. Do not make up information that isn't supported by the provided documents

IMPORTANT: Respond with a valid JSON object in the following format:
{{
  "answer": "Your detailed answer here",
  "confidence": "high|medium|low",
  "additional_notes": "Any additional context or limitations"
}}

JSON Response:`);

// Create a LangChain chain for RAG responses
const ragChain = RunnableSequence.from([
  ragPrompt,
  openai,
  new JsonOutputParser()
]);

// Helper function to safely parse JSON responses
function safeJsonParse(response: any): any {
  if (typeof response === 'object' && response !== null) {
    return response; // Already parsed
  }
  
  if (typeof response === 'string') {
    try {
      // Try to extract JSON from the response if it's wrapped in text
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return JSON.parse(response);
    } catch (error) {
      // If JSON parsing fails, return a structured fallback
      return {
        answer: response,
        confidence: "low",
        error: "Failed to parse JSON response",
        raw_response: response
      };
    }
  }
  
  return {
    answer: "Invalid response format",
    confidence: "low",
    error: "Unexpected response type"
  };
}

// Generate different types of prompts using LangChain templates
export function generatePrompt(promptType: 'rag' | 'summary' | 'analysis' | 'qa', context?: any): string {
  switch (promptType) {
    case 'rag':
      return `You are an intelligent document analysis assistant. Based on the provided document excerpts, answer the user's question comprehensively and accurately.

User Question: ${context?.query || '[QUERY]'}

Relevant Document Excerpts:
${context?.context || '[CONTEXT]'}

Instructions:
1. Provide a detailed, well-structured answer based solely on the provided document excerpts
2. If the documents don't contain enough information to fully answer the question, acknowledge this
3. Use specific details and examples from the documents when possible
4. Maintain a professional, informative tone
5. Do not make up information that isn't supported by the provided documents

IMPORTANT: Respond with a valid JSON object in the following format:
{
  "answer": "Your detailed answer here",
  "confidence": "high|medium|low",
  "sources_used": ["source1", "source2"],
  "additional_notes": "Any additional context or limitations"
}

JSON Response:`;

    case 'summary':
      return `Please provide a comprehensive summary of the following document content:

Document Content:
${context?.content || '[CONTENT]'}

Instructions:
1. Identify the main topics and key points
2. Provide a structured summary with clear sections
3. Highlight important findings or conclusions
4. Keep the summary concise but comprehensive
5. Maintain the original context and meaning

IMPORTANT: Respond with a valid JSON object in the following format:
{
  "summary": "Your comprehensive summary here",
  "main_topics": ["topic1", "topic2", "topic3"],
  "key_findings": ["finding1", "finding2"],
  "conclusions": "Main conclusions or takeaways"
}

JSON Response:`;

    case 'analysis':
      return `Please analyze the following document content and provide insights:

Document Content:
${context?.content || '[CONTENT]'}

Analysis Request: ${context?.request || '[ANALYSIS REQUEST]'}

Instructions:
1. Analyze the content based on the specific request
2. Identify patterns, trends, or key insights
3. Provide evidence from the document to support your analysis
4. Suggest implications or conclusions
5. Be objective and analytical in your approach

IMPORTANT: Respond with a valid JSON object in the following format:
{
  "analysis": "Your detailed analysis here",
  "patterns_identified": ["pattern1", "pattern2"],
  "key_insights": ["insight1", "insight2"],
  "evidence": ["evidence1", "evidence2"],
  "implications": "What this analysis means",
  "confidence_level": "high|medium|low"
}

JSON Response:`;

    case 'qa':
      return `Please answer the following question based on the provided document content:

Question: ${context?.question || '[QUESTION]'}

Document Content:
${context?.content || '[CONTENT]'}

Instructions:
1. Answer the question directly and clearly
2. Use specific information from the document
3. If the document doesn't contain enough information, state this clearly
4. Provide relevant quotes or references when possible
5. Keep the answer focused and relevant

IMPORTANT: Respond with a valid JSON object in the following format:
{
  "answer": "Your direct answer to the question",
  "confidence": "high|medium|low",
  "supporting_evidence": ["evidence1", "evidence2"],
  "quotes": ["relevant quote 1", "relevant quote 2"],
  "limitations": "Any limitations or missing information"
}

JSON Response:`;

    default:
      return `Please process the following request:

Request: ${context?.request || '[REQUEST]'}

Content: ${context?.content || '[CONTENT]'}

IMPORTANT: Respond with a valid JSON object in the following format:
{
  "response": "Your helpful response here",
  "status": "success|partial|error",
  "details": "Additional details or context"
}

JSON Response:`;
  }
}

export async function generateRAGResponse(context: SearchContext): Promise<{
  response: any; // Changed to any to handle JSON response
  sources: Array<{
    document: string;
    page?: number;
    excerpt: string;
    relevance: number;
  }>;
}> {
  try {
    const contextText = context.relevantChunks
      .map((chunk, index) => 
        `[Source ${index + 1}] Document: ${chunk.documentName}, Page: ${chunk.pageNumber || 'N/A'}\n${chunk.content}\n`
      )
      .join("\n");

    // Use LangChain chain for response generation
    const response = await ragChain.invoke({
      query: context.query,
      context: contextText
    });

    // Safely parse the JSON response
    const parsedResponse = safeJsonParse(response);

    // Format sources for frontend
    const sources = context.relevantChunks.map(chunk => ({
      document: chunk.documentName,
      page: chunk.pageNumber,
      excerpt: chunk.content.substring(0, 200) + (chunk.content.length > 200 ? "..." : ""),
      relevance: Math.round(chunk.similarity * 100),
    }));

    return {
      response: parsedResponse, // This will now be a safely parsed JSON object
      sources,
    };
  } catch (error) {
    throw new Error(`Failed to generate RAG response: ${(error as Error).message}`);
  }
}
