# PeerGenAI Certifications
Repository for submitting the code deliverables as part of hands-on exercises in Peer GenAI Certifications

**Overview**

In this git, participants will submit their code deliverables built as part of hands-on exercises in Peer GenAI Certifications. Users can create branches with their names from main, push their code and raise PRs. PRs will be reviewed but not approved. See below for details.

**Branch Creation**

•	Participants can create branches with their full name. For example, if your name is John Doe, you can create branch name as /johndoe

•	Participants submit their code inside this branch. 

•	Participants should raise PR to indicate their submission. Only one PR will be allowed per person for submission.

•	PRs will be reviewed but not approved and merged into main branch.

**Code Submission**

•	Ensure code follows proper standards based on the technology used.

•	Include unit test cases and test results where applicable.

•	Code should follow proper structure for folders such as common, frontend, backend etc and files such as readme, build and deployment scripts.

•	Readme should include instructions on how to build and run the code locally including any dependencies.

# DocuRAG – PDF Search & Analysis Application

## Overview

DocuRAG is a web application that lets users **upload, analyze, and search PDF documents** using AI-powered insights. It uses **Retrieval-Augmented Generation (RAG)** technology to enhance document processing and search.

![RAG](https://github.com/user-attachments/assets/b6a5626e-1414-4cbb-a9f3-feb2ca5d6f0f)


* **Frontend:** React 18 + TypeScript
* **Backend:** Node.js + Express
* **Database:** MongoDB
* **File Storage:** Local filesystem
* **Authentication:** Google OAuth
* **AI Integration:** OpenAI GPT models

## User Preferences

* **Communication Style:** Simple, everyday language.

## System Architecture

### Frontend

* **Framework:** React 18 + TypeScript + Vite
* **UI Library:** shadcn/ui (built on Radix UI)
* **Styling:** Tailwind CSS, custom design system inspired by Fluent/Material Design
* **State Management:**

  * Server state: TanStack Query
  * Local state: React hooks
* **Routing:** Wouter (lightweight client-side routing)
* **Theme:** Custom theme provider supporting light/dark mode

### Backend

* **Runtime:** Node.js with Express.js
* **Language:** TypeScript (ES modules)
* **API:** RESTful endpoints for PDF management & search
* **File Processing:** pdfjs-dist for PDF text extraction
* **Development:** Hot reloading via Vite middleware

## Data Storage

* **Database:** MongoDB

  * Stores user data, PDF metadata, and extracted PDF content for search
  * Supports vector search for advanced AI-based retrieval
* **File Storage:** Local filesystem

## Authentication & Authorization

* **Method:** Google OAuth
* **User Model:** Email-based with optional avatar
* **Session Management:** Express sessions using SESSION\_SECRET

## AI & Search Integration

* **AI Provider:** OpenAI (GPT-4o-mini, optionally GPT-5)
* **Text Processing:** Server-side PDF text extraction, cleanup, and validation
* **Search:** Database-driven PDF search with vector search enabled
* **RAG:** Foundation in place for future retrieval-augmented generation

## RAG 
<img width="790" height="413" alt="image" src="https://github.com/user-attachments/assets/fe0f9d59-ae82-4d4f-a002-48cebb451e33" />
<img width="838" height="668" alt="image" src="https://github.com/user-attachments/assets/4348a136-458a-4265-a1ae-24f7aadc787e" />

## Better logging

- Server uses pino for structured logs: pretty in development, compact JSON in production.
- Client uses loglevel with INFO default in production and DEBUG in development.
- Configure verbosity:
  - Set `LOG_LEVEL=debug` for server (e.g., in `.env`).
  - Set `VITE_LOG_LEVEL=debug` for client (Vite reloads it in dev).
- Where logs are emitted:
  - Server startup and listening port
  - RAG pipeline: indexing start/end, retrieval path, candidate/selected counts, model used, and answer size
  - Warnings on retries for rate limits (429) and fallback paths

How to view logs
- Development (pretty): `npm run dev` → terminal output
- Production (JSON): `npm start` → terminal JSON lines
- Browser client logs: open DevTools Console

## Production-grade project structure
### MongoDB vector search pre-filtering

- We pre-filter inside `$vectorSearch` using `filter: { userId }` to reduce candidate sets before scoring.
- This lowers latency and avoids post-filtering large result sets.

Example pipeline snippet:

```json
[
  {
    "$vectorSearch": {
      "index": "vector_index",
      "path": "embedding",
      "queryVector": "<queryEmbedding>",
      "numCandidates": 200,
      "limit": 20,
      "filter": { "userId": "<currentUserId>" }
    }
  },
  { "$project": { "userId": 1, "pdfId": 1, "originalName": 1, "index": 1, "text": 1, "embedding": 1, "score": { "$meta": "vectorSearchScore" } } }
]
```

### MongoDB design principles

- **Don’t save entire file content in MongoDB**: store only a short preview (truncated `extractedText`) in `pdfs`. Full content is chunked and stored as multiple small documents in the `vectors` collection.
- **16MB document limit**: enforced by truncating preview text (via `RAG_EXTRACTED_TEXT_MAX_CHARS`) and keeping vector chunks small. This prevents documents approaching the 16MB cap.
- **Indexes**: ensure indexes on `users`, `pdfs` (e.g., `userId`, `uploadedAt`, text index), and composite indexes in `vectors` (`userId`, `pdfId`, `index`).

Server side is organized for clarity and maintainability, avoiding unnecessary middleware:

```
server/src/
 config/ # Environment-bound setup (auth, vite)
 db/ # Database connections (mongo)
 routes/ # Express routes
 services/ # Business/domain logic (rag, storage)
 utils/ # Reusable utilities (logger)
 app.ts # Express app factory + error handler
 server.ts # Entrypoint (boot + listen)
```

## Points to Consider (what this repo demonstrates)

1. LangChain
   - a) PDFLoader is available and used (`@langchain/community/document_loaders/fs/pdf`) in `server/src/routes/http-routes.ts`.
   - b) Vector store is available and used (`MongoDBAtlasVectorSearch`) in `server/src/services/rag.ts`.

2. MongoDB design principles
   - a) Don’t save entire file content in MongoDB; only a preview is stored in `pdfs`, while full text is chunked into `vectors`.
   - b) 16MB document limit respected by truncation (`RAG_EXTRACTED_TEXT_MAX_CHARS`) and small chunk docs.

3. Vector search pre‑filtering
   - Pre‑filter in `$vectorSearch` with `{ userId }` or `{ userId, pdfId }`, and apply the same filters in local/full‑text fallbacks.

4. Better logging
   - Pino for structured server logs; loglevel on client. Object‑first logging used throughout.

5. Production‑grade structure
   - `server/src/` split into `config/`, `db/`, `routes/`, `services/`, `utils/`, with `app.ts` and `server.ts` entrypoints.

6. Performance trade‑offs
   - Tunables for chunking, batch size, top‑k, and fallbacks via `RAG_*` envs; retries with backoff on 429.

## How to Run 
Add your credentials:
MongoDB connection string
OpenAI API key
Google OAuth credentials

Install dependencies:
npm install

Build the project:
npm run build

Start the application:
npm run dev & npm run start