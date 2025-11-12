import dotenv from 'dotenv';
import { ChatOpenAI, OpenAIEmbeddings } from "@langchain/openai";
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { RunnableSequence } from "@langchain/core/runnables";
import { JsonOutputParser } from "@langchain/core/output_parsers";
import { getSentenceTransformerService } from './sentenceTransformerService';

// Load environment variables
dotenv.config();

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

// Initialize OpenAI Embeddings for proper vector generation
// Note: OpenRouter may not support standard OpenAI embedding models
// We'll use a fallback approach with better hash-based embeddings
const embeddings = new OpenAIEmbeddings({
  apiKey: process.env.OPENROUTER_API_KEY || "",
  configuration: {
    baseURL: "https://openrouter.ai/api/v1",
    defaultHeaders: {
      "HTTP-Referer": "https://replit.com",
      "X-Title": "RAG Intelligence"
    }
  },
  modelName: "text-embedding-ada-002",
  openAIApiKey: process.env.OPENROUTER_API_KEY || "",
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

// Generate embeddings using SentenceTransformer (primary) with fallbacks
export async function generateEmbedding(text: string): Promise<number[]> {
  try {
    // Try SentenceTransformer first (best quality, local, no API costs)
    const sentenceTransformer = getSentenceTransformerService();
    const embedding = await sentenceTransformer.generateEmbedding(text);
    console.log('✅ Using SentenceTransformer embeddings');
    return embedding;
  } catch (error) {
    console.warn('⚠️ SentenceTransformer failed, trying OpenAI embeddings:', error instanceof Error ? error.message : 'Unknown error');
    
    try {
      // Check if we're using OpenRouter (which doesn't support embeddings)
      if (process.env.OPENROUTER_API_KEY && !process.env.OPENAI_API_KEY) {
        console.log('⚠️ OpenRouter detected - embeddings not supported, using hash-based method');
        return generateImprovedHashEmbedding(text);
      }
      
      // Try OpenAI embeddings as fallback
      const embedding = await embeddings.embedQuery(text);
      console.log('✅ Using OpenAI embeddings');
      return embedding;
    } catch (openaiError) {
      console.warn('⚠️ OpenAI embedding failed, using hash-based method:', openaiError instanceof Error ? openaiError.message : 'Unknown error');
      
      // Final fallback to hash-based method
      return generateImprovedHashEmbedding(text);
    }
  }
}

// Improved hash-based embedding with better semantic features
function generateImprovedHashEmbedding(text: string): number[] {
  const words = text.toLowerCase()
    .replace(/[^\w\s]/g, ' ') // Remove punctuation
    .split(/\s+/)
    .filter(word => word.length > 2); // Filter short words
  
  const embedding = new Array(384).fill(0);
  
  // Word-level features
  for (let i = 0; i < words.length; i++) {
    const word = words[i];
    const wordHash = hashString(word);
    
    // Distribute word features across multiple dimensions
    for (let j = 0; j < 8; j++) {
      const index = (wordHash + j) % embedding.length;
      embedding[index] += Math.sin(wordHash + i + j) * 0.15;
    }
    
    // Character-level features for better semantic understanding
    for (let j = 0; j < word.length; j++) {
      const charCode = word.charCodeAt(j);
      const index = (charCode + i + j) % embedding.length;
      embedding[index] += Math.cos(charCode + i) * 0.1;
    }
  }
  
  // Add document-level features
  const docLength = text.length;
  const wordCount = words.length;
  const avgWordLength = wordCount > 0 ? text.length / wordCount : 0;
  
  // Distribute document features
  for (let i = 0; i < 16; i++) {
    const index = (docLength + i) % embedding.length;
    embedding[index] += Math.sin(docLength + i) * 0.05;
  }
  
  for (let i = 0; i < 16; i++) {
    const index = (wordCount + i + 100) % embedding.length;
    embedding[index] += Math.cos(wordCount + i) * 0.05;
  }
  
  for (let i = 0; i < 16; i++) {
    const index = (Math.floor(avgWordLength) + i + 200) % embedding.length;
    embedding[index] += Math.sin(avgWordLength + i) * 0.05;
  }
  
  // Normalize the vector
  const magnitude = Math.sqrt(embedding.reduce((sum, val) => sum + val * val, 0));
  return embedding.map(val => magnitude > 0 ? val / magnitude : 0);
}

// Simple hash function for strings
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
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

// Create a LangChain chain for RAG responses (without JsonOutputParser to handle parsing ourselves)
const ragChain = RunnableSequence.from([
  ragPrompt,
  openai
]);

// Helper function to safely parse JSON responses
function safeJsonParse(response: any): any {
  if (typeof response === 'object' && response !== null) {
    return response; // Already parsed
  }
  
  if (typeof response === 'string') {
    try {
      // Clean the response string to fix common JSON issues
      let cleanedResponse = response
        .replace(/\\n/g, '\\n')  // Fix newline escapes
        .replace(/\\t/g, '\\t')  // Fix tab escapes
        .replace(/\\"/g, '\\"')  // Fix quote escapes
        .replace(/\\\\/g, '\\\\'); // Fix backslash escapes
      
      // Try to extract JSON from the response if it's wrapped in text
      const jsonMatch = cleanedResponse.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }
      return JSON.parse(cleanedResponse);
    } catch (error) {
      // If JSON parsing still fails, try to extract just the answer text
      const answerMatch = response.match(/"answer":\s*"([^"]*(?:\\.[^"]*)*)"/);
      if (answerMatch) {
        return {
          answer: answerMatch[1].replace(/\\n/g, '\n').replace(/\\"/g, '"'),
          confidence: "medium",
          error: "Partial JSON parsing - extracted answer only"
        };
      }
      
      // Final fallback
      return {
        answer: response.replace(/\\n/g, '\n').replace(/\\"/g, '"'),
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
    // Validate API key before making the request
    if (!process.env.OPENROUTER_API_KEY || process.env.OPENROUTER_API_KEY.trim() === '') {
      throw new Error('OPENROUTER_API_KEY is not set. Please set it in your .env file. Get your API key from https://openrouter.ai/keys');
    }

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

    // Extract the content from the response (it might be wrapped in a message object)
    const responseContent = response?.content || response?.text || response || '';
    
    // Safely parse the JSON response
    const parsedResponse = safeJsonParse(responseContent);

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
    const errorMessage = (error as Error).message;
    
    // Provide more helpful error messages for common authentication issues
    if (errorMessage.includes('401') || errorMessage.includes('User not found') || errorMessage.includes('authentication')) {
      throw new Error(`Authentication failed: Invalid or missing OPENROUTER_API_KEY. Please check your .env file and ensure your API key is valid. Get your API key from https://openrouter.ai/keys`);
    }
    
    if (errorMessage.includes('OPENROUTER_API_KEY is not set')) {
      throw error; // Re-throw our custom error as-is
    }
    
    throw new Error(`Failed to generate RAG response: ${errorMessage}`);
  }
}
