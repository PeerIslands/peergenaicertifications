# RAGFlowChat

A RAG (Retrieval-Augmented Generation) application for chatting with PDF documents using Google Gemini AI.

## Features

- 📄 Upload and process PDF documents
- 🔍 Semantic search using vector embeddings
- 💬 Chat interface with context-aware responses
- 📊 Visual processing pipeline
- 🎯 Context panel showing retrieved chunks

## Prerequisites

- Node.js 20+ 
- npm or yarn
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

## Local Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
PORT=5000
```

**Note:** The application requires a valid `GEMINI_API_KEY` to function. Without it, document processing and chat features will not work.

### 3. Start the Development Server

```bash
npm run dev
```

The application will be available at:
- **Frontend & API:** http://localhost:5000

### 4. Build for Production

```bash
npm run build
npm start
```

## Usage

1. **Upload a PDF:** Go to the "Upload & Process" tab and upload a PDF file (max 10MB)
2. **Configure Chunking:** Adjust chunk size and overlap settings (default: 500/50)
3. **Process Document:** Click "Start Processing" to chunk and vectorize the document
4. **Chat:** Switch to the "Chat" tab and ask questions about your document
5. **View Context:** See which document chunks were used to answer your questions in the right panel

## Project Structure

```
├── client/          # React frontend (Vite + React)
├── server/          # Express backend
│   ├── routes.ts    # API endpoints
│   ├── gemini.ts    # Gemini AI integration
│   ├── pdf.ts       # PDF processing
│   └── storage.ts   # In-memory storage
├── shared/          # Shared TypeScript schemas
└── script/          # Build scripts
```

## API Endpoints

- `GET /api/documents` - List all documents
- `POST /api/documents/upload` - Upload and process a PDF
- `GET /api/documents/:id` - Get document details
- `DELETE /api/documents/:id` - Delete a document
- `POST /api/chat` - Send a chat message
- `GET /api/messages` - Get chat history
- `DELETE /api/messages` - Clear chat history

## Current Limitations

- **In-memory storage:** Data is lost on server restart
- **PDF only:** Currently supports PDF files only
- **Single document chat:** One document at a time
- **No authentication:** No user management

## Technology Stack

- **Frontend:** React, TypeScript, Vite, Tailwind CSS, Radix UI
- **Backend:** Express.js, TypeScript
- **AI:** Google Gemini (gemini-2.5-flash, text-embedding-004)
- **Vector Store:** In-memory (ChromaDB integration prepared)

## Development

```bash
# Type checking
npm run check

# Development server
npm run dev

# Production build
npm run build
```

## License

MIT

