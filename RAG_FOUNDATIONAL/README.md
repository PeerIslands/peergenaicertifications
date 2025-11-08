# DocuRAG – PDF Search & Analysis Application

## Overview

DocuRAG is a web application that lets users **upload, analyze, and search PDF documents** using AI-powered insights. It uses **Retrieval-Augmented Generation (RAG)** technology to enhance document processing and search, providing intelligent document querying capabilities through OpenAI integration.

## Technology Stack

### Frontend
- **Framework:** React 18 + TypeScript + Vite
- **UI Library:** shadcn/ui (built on Radix UI)
- **Styling:** Tailwind CSS with custom design system
- **State Management:** 
  - Server state: TanStack Query
  - Local state: React hooks
- **Routing:** Wouter (lightweight client-side routing)
- **Theme:** Custom theme provider supporting light/dark mode

### Backend
- **Runtime:** Node.js with Express.js
- **Language:** TypeScript (ES modules)
- **API:** RESTful endpoints for PDF management & search
- **File Processing:** LangChain PDFLoader for PDF text extraction
- **Development:** Hot reloading via Vite middleware

### Data & Storage
- **Database:** MongoDB
  - Stores user data, PDF metadata, and extracted PDF content
  - Supports MongoDB Atlas Vector Search for advanced AI-based retrieval
  - Collections: `users`, `pdfs`, `vectors`, `sessions`, `chat_queries`, `chat_responses`
- **File Storage:** Local filesystem (`uploads/` directory)

### Authentication & Security
- **Method:** Google OAuth 2.0
- **Session Management:** Express sessions with MongoDB store
- **User Model:** Email-based with optional avatar and profile information

### AI Integration
- **AI Provider:** OpenAI
- **Models:** 
  - Chat: GPT-4o-mini / GPT-5 (configurable via `OPENAI_CHAT_MODEL`)
  - Embeddings: text-embedding-3-large (configurable via `OPENAI_EMBEDDING_MODEL`)
- **Text Processing:** Server-side PDF text extraction, chunking, and vectorization
- **RAG Implementation:** Vector search with fallback strategies

### Testing
- **Framework:** Vitest 2.1.8
- **Coverage:** @vitest/coverage-v8
- **Test Environment:** 
  - Client tests: jsdom (browser simulation)
  - Server tests: node (Node.js environment)
- **Test Libraries:**
  - `@testing-library/react` - React component testing
  - `@testing-library/jest-dom` - DOM matchers
  - `@testing-library/user-event` - User interaction simulation
- **Test Files:** Comprehensive unit tests for all client-side and server-side modules

## Project Structure

```
RAG_FOUNDATIONAL/
├── client/                    # Frontend React application
│   ├── src/
│   │   ├── __tests__/        # Test utilities and setup
│   │   │   ├── setup.ts      # Test setup (mocks, cleanup)
│   │   │   ├── test-utils.tsx # Custom render with providers
│   │   │   └── App.test.tsx  # Main app tests
│   │   ├── components/       # React components
│   │   │   └── __tests__/    # Component tests
│   │   ├── pages/            # Page components
│   │   │   └── __tests__/    # Page tests
│   │   ├── hooks/            # Custom React hooks
│   │   │   └── __tests__/    # Hook tests
│   │   ├── lib/              # Utility libraries
│   │   │   │   └── __tests__/ # Utility tests
│   │   └── main.tsx          # Entry point
│   └── index.html
├── server/                    # Backend Express application
│   ├── __tests__/            # Server test setup
│   │   └── setup.ts          # Optional server test setup
│   ├── src/
│   │   ├── config/           # Configuration (auth, vite)
│   │   │   ├── auth.ts
│   │   │   ├── auth.test.ts
│   │   │   ├── vite.ts
│   │   │   └── vite.test.ts
│   │   ├── db/              # Database connection
│   │   │   ├── mongo.ts
│   │   │   └── mongo.test.ts
│   │   ├── routes/        # Express routes
│   │   │   ├── http-routes.ts
│   │   │   └── http-routes.test.ts
│   │   ├── services/     # Business logic
│   │   │   ├── rag.ts    # RAG implementation
│   │   │   ├── rag.test.ts
│   │   │   ├── storage.ts
│   │   │   └── storage.test.ts
│   │   ├── utils/        # Utilities
│   │   │   ├── logger.ts
│   │   │   └── logger.test.ts
│   │   ├── app.ts        # Express app factory
│   │   ├── app.test.ts
│   │   ├── server.ts     # Entry point
│   │   └── server.test.ts
│   ├── index.ts
│   └── index.test.ts
├── shared/                 # Shared TypeScript types/schemas
│   └── schema.ts
├── dist/                   # Build output
├── uploads/                # Uploaded PDF files
├── package.json
├── tsconfig.json
├── vite.config.ts
├── vitest.config.ts       # Test configuration
└── README.md
```

## Prerequisites

- Node.js 20+ 
- npm or yarn
- MongoDB instance (local or Atlas)
- OpenAI API key
- Google OAuth credentials (Client ID and Secret)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd RAG_FOUNDATIONAL
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Set up environment variables:**
   Create a `.env` file in the root directory with the following variables:

   ```env
   # Server Configuration
   PORT=5000
   NODE_ENV=development
   LOG_LEVEL=debug

   # Database
   DATABASE_URL=mongodb://localhost:27017/rag_application
   MONGODB_DB=rag_application
   MONGODB_VECTOR_SEARCH=false  # Set to true if using Atlas Vector Search
   MONGODB_VECTOR_INDEX_NAME=vector_index

   # Session
   SESSION_SECRET=your-session-secret-key-here

   # Google OAuth
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   APP_BASE_URL=http://localhost:5000

   # OpenAI
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_CHAT_MODEL=gpt-4o-mini
   OPENAI_EMBEDDING_MODEL=text-embedding-3-large
   OPENAI_TEMPERATURE=0.2
   OPENAI_MAX_TOKENS=220

   # File Upload
   UPLOAD_MAX_FILE_MB=50
   MAX_UPLOAD_MB=50

   # RAG Configuration
   RAG_CHUNK_SIZE=1000
   RAG_CHUNK_OVERLAP=150
   RAG_EMBED_BATCH_SIZE=64
   RAG_TOP_K=1
   RAG_FULLTEXT_PDFS=3
   RAG_EXTRACTED_TEXT_MAX_CHARS=50000
   ```

## Running the Application

### Development Mode

Run the development server with hot reloading:

```bash
npm run dev
```

This starts both the frontend (Vite) and backend (Express) servers with hot reloading enabled.

### Production Mode

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Start the production server:**
   ```bash
   npm start
   ```

### Other Commands

- **Type checking:**
  ```bash
  npm run check
  ```

- **Run tests:**
  ```bash
  npm test
  ```

- **Run tests in watch mode:**
  ```bash
  npm run test:watch
  ```

## Testing

This project includes comprehensive unit tests for both **client-side** and **server-side** modules using Vitest.

### Test Coverage Summary

**Total: 221 tests across 28 test files**
- ✅ **Client-side tests:** 154 tests in 17 files
- ✅ **Server-side tests:** 67 tests in 10 files
- ✅ **All tests passing:** 100% pass rate
- ✅ **Overall Coverage:** ~78% statements, ~75% branches, ~81% functions, ~78% lines

### Client-Side Test Coverage

#### Pages (5 test files, 30+ tests)
- ✅ **Chat Page** (`client/src/pages/__tests__/chat.test.tsx`) - Chat interface, message sending, sources display
- ✅ **Dashboard Page** (`client/src/pages/__tests__/dashboard.test.tsx`) - PDF listing, search, delete/download
- ✅ **Landing Page** (`client/src/pages/__tests__/landing.test.tsx`) - Landing page features and navigation
- ✅ **Upload Page** (`client/src/pages/__tests__/upload.test.tsx`) - File upload functionality
- ✅ **NotFound Page** (`client/src/pages/__tests__/not-found.test.tsx`) - 404 page rendering
- ✅ **App Component** (`client/src/__tests__/App.test.tsx`) - Main app routing and providers

#### Components (3 test files, 20+ tests)
- ✅ **PdfCard** (`client/src/components/__tests__/pdf-card.test.tsx`) - PDF card display, formatting, actions
- ✅ **UploadZone** (`client/src/components/__tests__/upload-zone.test.tsx`) - Drag & drop, file validation, progress
- ✅ **AppSidebar** (`client/src/components/__tests__/app-sidebar.test.tsx`) - Sidebar navigation and links

#### Hooks (3 test files, 15+ tests)
- ✅ **useAuth** (`client/src/hooks/__tests__/useAuth.test.tsx`) - Authentication state management
- ✅ **useToast** (`client/src/hooks/__tests__/use-toast.test.ts`) - Toast notification system
- ✅ **useIsMobile** (`client/src/hooks/__tests__/use-mobile.test.tsx`) - Responsive breakpoint detection

#### Library Utilities (5 test files, 35+ tests)
- ✅ **API Client** (`client/src/lib/__tests__/api.test.ts`) - API methods, error handling
- ✅ **Auth Utils** (`client/src/lib/__tests__/authUtils.test.ts`) - Authentication utility functions
- ✅ **Utils** (`client/src/lib/__tests__/utils.test.ts`) - Class name merging utility
- ✅ **Logger** (`client/src/lib/__tests__/logger.test.ts`) - Client-side logging
- ✅ **Query Client** (`client/src/lib/__tests__/queryClient.test.ts`) - Query configuration and API requests

#### Entry Point (1 test file)
- ✅ **Main** (`client/src/__tests__/main.test.tsx`) - React root initialization

### Server-Side Test Coverage

- ✅ **Logger Utility** (`server/src/utils/logger.test.ts`) - 5 tests
- ✅ **Database** (`server/src/db/mongo.test.ts`) - 6 tests
- ✅ **Storage Service** (`server/src/services/storage.test.ts`) - 15 tests
- ✅ **RAG Service** (`server/src/services/rag.test.ts`) - 11 tests
- ✅ **Authentication** (`server/src/config/auth.test.ts`) - 12 tests (includes OAuth routes and logout)
- ✅ **Vite Configuration** (`server/src/config/vite.test.ts`) - 7 tests (includes error handling)
- ✅ **Express App** (`server/src/app.test.ts`) - 5 tests
- ✅ **HTTP Routes** (`server/src/routes/http-routes.test.ts`) - 17 tests
- ✅ **Server Entry** (`server/src/server.test.ts`) - 3 tests
- ✅ **Index Module** (`server/index.test.ts`) - 2 tests

### Running Tests

```bash
# Run all tests (client + server)
npm test

# Run tests in watch mode (for development)
npm run test:watch

# Run tests with coverage report
npm test -- --coverage

# Run only client-side tests
npm test -- client

# Run only server-side tests
npm test -- server

# Run a specific test file
npm test -- client/src/pages/__tests__/chat.test.tsx
```

### Test Configuration

Tests are configured in `vitest.config.ts`:
- **Environment Separation:**
  - Client tests run in `jsdom` environment (browser simulation)
  - Server tests run in `node` environment (Node.js)
- **Setup Files:**
  - Client tests: `client/src/__tests__/setup.ts` (mocks window, DOM APIs)
  - Server tests: Environment-aware setup with OpenAI mocks
- **Coverage:**
  - Reports available in text, JSON, and HTML formats
  - Includes both client and server code coverage
- **Test Patterns:**
  - Client: `client/**/*.test.{ts,tsx}` and `client/**/*.spec.{ts,tsx}`
  - Server: `server/**/*.test.ts`

### Test Dependencies

Required testing packages (already installed):
- `vitest` - Test framework
- `@vitest/coverage-v8` - Coverage provider
- `@testing-library/react` - React component testing
- `@testing-library/jest-dom` - DOM matchers
- `@testing-library/user-event` - User interaction simulation
- `@testing-library/dom` - DOM testing utilities
- `jsdom` - Browser environment simulation

### Test Structure

```
RAG_FOUNDATIONAL/
├── client/src/
│   ├── __tests__/
│   │   ├── setup.ts           # Client test setup (mocks, cleanup)
│   │   ├── test-utils.tsx     # Custom render with providers
│   │   └── App.test.tsx       # Main app tests
│   ├── pages/__tests__/       # Page component tests
│   ├── components/__tests__/   # Component tests
│   ├── hooks/__tests__/       # Hook tests
│   └── lib/__tests__/         # Utility tests
├── server/
│   ├── __tests__/
│   │   └── setup.ts           # Server test setup (optional)
│   └── src/
│       ├── **/*.test.ts       # Server module tests
│       └── index.test.ts      # Entry point tests
└── vitest.config.ts           # Test configuration
```

### Code Coverage Report

#### Overall Coverage
- **Statements:** 78.19%
- **Branches:** 75%
- **Functions:** 81.25%
- **Lines:** 78.19%

#### Client-Side Coverage

| Module | Statements | Branches | Functions | Lines |
|--------|-----------|----------|-----------|-------|
| `client/src` | 52.17% | 62.5% | 60% | 52.17% |
| `client/src/App.tsx` | 55.38% | 71.42% | 75% | 55.38% |
| `client/src/main.tsx` | 0% | 0% | 0% | 0% |
| `client/src/components` | 95.44% | 78.68% | 80.95% | 95.44% |
| - `app-sidebar.tsx` | 100% | 100% | 100% | 100% |
| - `pdf-card.tsx` | 100% | 92.3% | 100% | 100% |
| - `upload-zone.tsx` | 92.56% | 72.97% | 88.88% | 92.56% |
| `client/src/hooks` | 90.25% | 82.14% | 84.61% | 90.25% |
| - `use-mobile.tsx` | 100% | 100% | 100% | 100% |
| - `useAuth.ts` | 100% | 100% | 100% | 100% |
| `client/src/lib` | 75% | 90% | 88.88% | 75% |
| - `api.ts` | 100% | 85.71% | 100% | 100% |
| - `authUtils.ts` | 100% | 100% | 100% | 100% |
| - `logger.ts` | 100% | 92.3% | 100% | 100% |
| - `queryClient.ts` | 38.29% | 100% | 33.33% | 38.29% |
| `client/src/pages` | 97.39% | 89.85% | 77.27% | 97.39% |
| - `chat.tsx` | 100% | 84.61% | 100% | 100% |
| - `dashboard.tsx` | 89.16% | 96% | 50% | 89.16% |
| - `landing.tsx` | 100% | 100% | 100% | 100% |
| - `not-found.tsx` | 100% | 100% | 100% | 100% |
| - `upload.tsx` | 100% | 84.61% | 80% | 100% |

#### Server-Side Coverage

| Module | Statements | Branches | Functions | Lines |
|--------|-----------|----------|-----------|-------|
| `server` | 100% | 100% | 100% | 100% |
| `server/src` | 100% | 68.75% | 100% | 100% |
| - `app.ts` | 100% | 72.72% | 100% | 100% |
| - `server.ts` | 100% | 60% | 100% | 100% |
| `server/src/config` | 51.42% | 81.81% | 62.5% | 51.42% |
| - `auth.ts` | 48.71% | 75% | 60% | 48.71% |
| - `vite.ts` | 56.89% | 100% | 66.66% | 56.89% |
| `server/src/db` | 96.61% | 92.85% | 100% | 96.61% |
| - `mongo.ts` | 96.61% | 92.85% | 100% | 96.61% |
| `server/src/routes` | 15.51% | 50% | 33.33% | 15.51% |
| - `http-routes.ts` | 15.51% | 50% | 33.33% | 15.51% |
| `server/src/services` | 84.97% | 58.87% | 100% | 84.97% |
| - `rag.ts` | 81.11% | 54.94% | 100% | 81.11% |
| - `storage.ts` | 100% | 81.25% | 100% | 100% |
| `server/src/utils` | 94.44% | 33.33% | 100% | 94.44% |
| - `logger.ts` | 94.44% | 33.33% | 100% | 94.44% |

#### Coverage Notes

**High Coverage Areas (90%+):**
- ✅ Client components (95.44%)
- ✅ Client hooks (90.25%)
- ✅ Client pages (97.39%)
- ✅ Server database layer (96.61%)
- ✅ Server utilities (94.44%)
- ✅ Server storage service (100%)

**Areas for Improvement:**
- 🔄 `client/src/main.tsx` (0%) - Entry point, minimal logic
- 🔄 `client/src/lib/queryClient.ts` (38.29%) - Some edge cases not covered
- 🔄 `server/src/routes/http-routes.ts` (15.51%) - Route handlers need more integration tests
- 🔄 `server/src/config/auth.ts` (48.71%) - OAuth callback flows need more coverage
- 🔄 `server/src/config/vite.ts` (56.89%) - Error paths need more testing

### Writing Tests

#### Client-Side Test Example

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@/__tests__/test-utils';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('should render correctly', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

#### Server-Side Test Example

```typescript
import { describe, it, expect, vi } from 'vitest';
import { myFunction } from './myModule';

describe('myModule', () => {
  it('should work correctly', () => {
    const result = myFunction('input');
    expect(result).toBe('expected');
  });
});
```

### Running Coverage Reports

To generate a detailed coverage report:

```bash
# Run tests with coverage
npm test -- --coverage

# View coverage in HTML format (opens in browser)
npm test -- --coverage && open coverage/index.html
```

Coverage reports are generated in multiple formats:
- **Text:** Console output
- **JSON:** `coverage/coverage-final.json`
- **HTML:** `coverage/index.html` (interactive browser report)

## API Endpoints

### Authentication
- `GET /api/login` - Initiate Google OAuth login
- `GET /api/callback` - OAuth callback handler
- `GET /api/logout` - Logout user
- `GET /api/auth/user` - Get current authenticated user

### PDF Management
- `GET /api/pdfs` - Get all PDFs for authenticated user
- `GET /api/pdfs/:id` - Get specific PDF by ID
- `GET /api/pdfs/:id/download` - Download PDF file
- `POST /api/pdfs/upload` - Upload new PDF file
- `POST /api/pdfs/search` - Search PDFs by query string
- `DELETE /api/pdfs/:id` - Delete PDF and associated vectors

### RAG Chat
- `POST /api/rag/chat` - Chat with RAG system using PDF context
  - Body: `{ messages: Array<{role: string, content: string}>, pdfId?: string }`
  - Returns: `{ reply: string, sources: Array<{pdfId, originalName, preview}> }`

## Features

### Core Functionality
1. **PDF Upload & Storage**
   - Secure file upload with size limits
   - Automatic text extraction using LangChain PDFLoader
   - Metadata storage in MongoDB

2. **Vector Search**
   - Automatic chunking and embedding of PDF content
   - Vector storage with MongoDB Atlas Vector Search support
   - Similarity search with configurable top-k retrieval

3. **RAG Chat**
   - Context-aware chat responses based on uploaded PDFs
   - Multi-PDF or single-PDF context modes
   - Source citation in responses

4. **Search Capabilities**
   - Full-text search across PDF names and content
   - Vector similarity search for semantic queries
   - Fallback mechanisms for robust retrieval

### Advanced Features
- **Multi-tenant Isolation:** All data filtered by `userId` for security
- **Pre-filtering in Vector Search:** Reduces latency by filtering before scoring
- **Error Handling:** Graceful fallbacks with retry logic for rate limits
- **Performance Optimization:** Batch processing, configurable chunk sizes, and indexing strategies
- **Structured Logging:** Pino for server logs, object-first logging pattern

## MongoDB Design Principles

### Document Structure
- **Users Collection:** User profiles with OAuth data
- **PDFs Collection:** 
  - Stores metadata and truncated preview text (max 50KB)
  - Full text not stored here to respect 16MB document limit
- **Vectors Collection:**
  - Stores chunked text with embeddings
  - Each chunk is a separate document
  - Composite unique index on `(userId, pdfId, index)`

### Indexes
- **Users:** `id` (unique), `email` (sparse)
- **PDFs:** `id` (unique), `userId`, `uploadedAt`, text index on `originalName` and `extractedText`
- **Vectors:** `(userId, pdfId, index)` (unique), `pdfId`, `userId`
- **Chat Queries/Responses:** `userId + createdAt`, `sessionId + createdAt`

### Vector Search Pre-filtering

Example pipeline with user pre-filtering:

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
  {
    "$project": {
      "userId": 1,
      "pdfId": 1,
      "originalName": 1,
      "index": 1,
      "text": 1,
      "score": { "$meta": "vectorSearchScore" }
    }
  }
]
```

## Logging

### Server Logging (Pino)
- **Development:** Pretty-printed logs with colors
- **Production:** Compact JSON format
- **Configuration:** Set `LOG_LEVEL=debug` in `.env` for verbose logging

### What Gets Logged
- Server startup and listening port
- RAG pipeline: indexing start/end, retrieval path, candidate counts
- Model usage and answer sizes
- Warnings on retries (rate limits) and fallback paths
- Error details with context

### Viewing Logs
- **Development:** Terminal output (pretty format)
- **Production:** Terminal JSON lines or redirect to log file
- **Client:** Browser DevTools Console

## Performance Tuning

Configure these environment variables to optimize performance:

- `RAG_CHUNK_SIZE`: Text chunk size (default: 1000)
- `RAG_CHUNK_OVERLAP`: Overlap between chunks (default: 150)
- `RAG_EMBED_BATCH_SIZE`: Batch size for embedding requests (default: 64)
- `RAG_TOP_K`: Number of top results to retrieve (default: 1)
- `RAG_FULLTEXT_PDFS`: Max PDFs for full-text fallback (default: 3)
- `UPLOAD_MAX_FILE_MB`: Maximum file upload size in MB (default: 50)

## Production Considerations

1. **Security**
   - Use strong `SESSION_SECRET` in production
   - Enable HTTPS (`APP_BASE_URL` should start with `https://`)
   - Secure MongoDB connection strings
   - Validate and sanitize all user inputs

2. **Scalability**
   - Consider MongoDB Atlas for managed database
   - Enable Atlas Vector Search for better performance
   - Use CDN for static assets in production
   - Implement file storage service (S3, etc.) instead of local filesystem

3. **Monitoring**
   - Set up log aggregation (e.g., Datadog, CloudWatch)
   - Monitor OpenAI API usage and costs
   - Track vector search performance metrics

4. **Error Handling**
   - Implement proper error boundaries
   - Set up alerting for critical errors
   - Monitor rate limit retries

## Development Tips

1. **Hot Reloading:** Both frontend and backend support hot reloading in development
2. **Type Safety:** Full TypeScript support with strict mode enabled
3. **Testing:** Write tests alongside features; use `npm run test:watch` during development
4. **Code Structure:** Follow the existing folder structure for consistency

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Verify `DATABASE_URL` is correct
   - Ensure MongoDB is running (if local)
   - Check network connectivity for Atlas

2. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` is set correctly
   - Check API quota and rate limits
   - Review error logs for specific error messages

3. **File Upload Fails**
   - Check `UPLOAD_MAX_FILE_MB` setting
   - Ensure `uploads/` directory exists and is writable
   - Verify file is a valid PDF

4. **Tests Not Running**
   - Ensure all dependencies are installed: `npm install`
   - Check that test files follow `*.test.ts` naming convention
   - Verify Vitest configuration in `vitest.config.ts`
   - For client tests, ensure `jsdom` is installed: `npm install --save-dev jsdom`
   - For client tests, ensure testing libraries are installed: `npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event`

5. **Client Tests Failing with "window is not defined"**
   - Verify `vitest.config.ts` uses `environmentMatchGlobs` to separate client (jsdom) and server (node) tests
   - Ensure setup file checks for window existence before using browser APIs

6. **Server Tests Failing with OpenAI Errors**
   - Ensure OpenAI is properly mocked in server test files
   - Check that mocks are placed before module imports

## License

MIT

## Contributing

1. Create a branch with your name (e.g., `/johndoe`)
2. Make your changes
3. Ensure all tests pass: `npm test`
4. Submit a PR for review

---

**Note:** This is a submission repository for PeerGenAI Certifications. PRs will be reviewed but not merged into main.
