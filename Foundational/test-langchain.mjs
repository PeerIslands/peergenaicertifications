#!/usr/bin/env node

/**
 * Test script for LangChain integration
 * This script demonstrates the basic LangChain functionality integrated into the existing services
 */

import { ChatOpenAI } from "@langchain/openai";
import { OpenAIEmbeddings } from "@langchain/openai";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";
import { PromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";
import { RunnableSequence } from "@langchain/core/runnables";

// Check if API key is available
const apiKey = process.env.OPENROUTER_API_KEY;
if (!apiKey) {
  console.log("❌ OPENROUTER_API_KEY environment variable not set");
  console.log("Please set your OpenRouter API key to test LangChain functionality");
  process.exit(1);
}

console.log("🚀 Testing LangChain Integration...\n");

// Initialize LangChain components (same as in openaiService.ts)
const openai = new ChatOpenAI({ 
  apiKey: apiKey,
  configuration: {
    baseURL: "https://openrouter.ai/api/v1",
    defaultHeaders: {
      "HTTP-Referer": "https://replit.com",
      "X-Title": "RAG Intelligence"
    }
  },
  modelName: "openai/gpt-oss-20b:free",
  maxTokens: 500,
  temperature: 0.3,
});

const embeddings = new OpenAIEmbeddings({
  apiKey: apiKey,
  configuration: {
    baseURL: "https://openrouter.ai/api/v1",
    defaultHeaders: {
      "HTTP-Referer": "https://replit.com",
      "X-Title": "RAG Intelligence"
    }
  },
  modelName: "text-embedding-ada-002",
});

const textSplitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500,
  chunkOverlap: 100,
});

// Sample text for testing
const sampleText = `
LangChain is a framework for developing applications powered by language models. 
It provides a standard interface for chains, lots of integrations with other tools, 
and end-to-end chains for common applications. LangChain enables applications that are:
- Data-aware: connect a language model to other sources of data
- Agentic: allow a language model to interact with its environment
- Reasonable: rely on a language model to reason (about how to answer a question, what to do next, etc.)

The main value props of LangChain are:
1. Components: abstractions for working with language models, along with a collection of implementations for each abstraction
2. Off-the-shelf chains: built-in assemblages of components for common use cases
3. Agents: a flexible approach to reasoning that can use tools and make decisions
`;

async function testLangChain() {
  try {
    console.log("📝 Testing text splitting...");
    const chunks = await textSplitter.splitText(sampleText);
    console.log(`✅ Split text into ${chunks.length} chunks\n`);

    console.log("🔍 Testing embeddings...");
    const embedding = await embeddings.embedQuery("What is LangChain?");
    console.log(`✅ Generated embedding with ${embedding.length} dimensions\n`);

    console.log("🤖 Testing LLM response...");
    const prompt = PromptTemplate.fromTemplate("Answer this question: {question}");
    const chain = RunnableSequence.from([prompt, openai, new StringOutputParser()]);
    
    const response = await chain.invoke({
      question: "What is the main purpose of LangChain?"
    });
    console.log("✅ Generated LLM response:");
    console.log(response + "\n");

    console.log("🎯 Testing RAG prompt template...");
    const ragPrompt = PromptTemplate.fromTemplate(`
    Based on the following context, answer the question:
    
    Context: {context}
    
    Question: {question}
    
    Answer:`);
    
    const ragChain = RunnableSequence.from([
      {
        question: (input) => input.question,
        context: (input) => input.context
      },
      ragPrompt,
      openai,
      new StringOutputParser()
    ]);

    const ragResponse = await ragChain.invoke({
      question: "What are the main value propositions of LangChain?",
      context: chunks.slice(0, 2).join("\n\n")
    });
    
    console.log("✅ Generated RAG response:");
    console.log(ragResponse + "\n");

    console.log("🎉 All LangChain tests passed successfully!");
    console.log("\n📋 Summary of integrated features:");
    console.log("- ✅ Text splitting with RecursiveCharacterTextSplitter");
    console.log("- ✅ OpenAI embeddings (available for future use)");
    console.log("- ✅ Prompt templates and chains");
    console.log("- ✅ RunnableSequence for structured workflows");
    console.log("- ✅ Enhanced RAG prompts in openaiService.ts");
    
  } catch (error) {
    console.error("❌ Test failed:", error.message);
    process.exit(1);
  }
}

// Run the test
testLangChain();
