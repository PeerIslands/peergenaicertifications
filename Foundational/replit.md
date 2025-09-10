# Overview

This is a RAG (Retrieval-Augmented Generation) Intelligence system that allows users to upload PDF documents and perform intelligent search queries against them. The application uses AI-powered document analysis with vector embeddings and semantic search to provide contextual answers with source attribution.

The system is built as a full-stack web application with a React frontend and Express.js backend, featuring real-time document processing, vector-based similarity search, and OpenAI integration for generating comprehensive responses.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Framework**: React 18 with TypeScript in a single-page application architecture
- **Styling**: Tailwind CSS with shadcn/ui component library for consistent design system
- **State Management**: TanStack Query (React Query) for server state management and caching
- **Routing**: Wouter for lightweight client-side routing
- **Build Tool**: Vite for development and production builds with hot module replacement

## Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **API Design**: RESTful API with dedicated routes for document management and search operations
- **File Processing**: Multer for handling PDF uploads with memory storage and file validation
- **PDF Processing**: pdf-parse library for extracting text content from uploaded documents
- **Development**: Custom Vite integration for serving frontend in development mode

## Data Storage Solutions
- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Schema Design**: Three main tables - documents (metadata), document_chunks (text segments with embeddings), and search_queries (query history)
- **Vector Storage**: JSON-based storage of embeddings within PostgreSQL for similarity search
- **Session Management**: connect-pg-simple for PostgreSQL-backed session storage
- **Development Storage**: In-memory storage implementation for development/testing

## Authentication and Authorization
- **Session-based**: Express sessions with PostgreSQL session store
- **File Security**: Multer configuration with file type validation (PDF only) and size limits (10MB)
- **CORS**: Configured for cross-origin requests in development environment

## External Service Integrations
- **OpenAI API**: 
  - text-embedding-3-small model for generating vector embeddings
  - GPT-4o model for generating contextual responses
  - Integrated through official OpenAI SDK
- **Neon Database**: Serverless PostgreSQL database for production deployment
- **Vector Search**: Custom cosine similarity implementation for finding relevant document chunks
- **Text Processing**: Intelligent text chunking with sentence-aware segmentation and overlap for better context preservation

## Key Design Patterns
- **RAG Pipeline**: Document upload → PDF parsing → text chunking → embedding generation → vector storage → semantic search → LLM response generation
- **Async Processing**: Non-blocking document processing with status tracking (uploading → processing → ready → error)
- **Component Composition**: Modular React components with clear separation of concerns
- **Type Safety**: End-to-end TypeScript with shared schema definitions between frontend and backend
- **Error Handling**: Comprehensive error boundaries and user feedback through toast notifications
- **Real-time Updates**: Periodic polling for document processing status updates