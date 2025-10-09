# Foundational RAG

Document QA app with a TypeScript Express API and a Vite-powered React client. The server manages file ingestion, AI requests, and serves the bundled client in production.

## Prerequisites

- Node.js 18 or newer
- npm 9 or newer
- Access to a MongoDB deployment
- OpenAI API key

## Installation

1. Install dependencies: `npm install`
2. Create a `.env` file in the project root with values similar to:

```
OPENAI_API_KEY=sk-your-openai-key
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net
MONGODB_DB=RAG_POC
PORT=5000
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_CHAT_TEMPERATURE=0.2
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHUNK_SIZE=1200
CHUNK_OVERLAP=200
```

The `PORT` value defaults to 5000 when not provided. The OpenAI and chunk configuration values shown above are optional; omit or edit them to change models or tuning without touching code.

3. No database migrations are required; collections and indexes are created on startup.

## Running locally

- Start the development server with `npm run dev`. The script runs the Express API through tsx and attaches the Vite development middleware. After it starts you can visit http://127.0.0.1:5000 in the browser.
- Uploaded files are stored on disk under `uploads/` by default.

## Building for production

1. Build the client assets and bundled server with `npm run build`.
2. Launch the compiled server with `npm start`. The Express server serves the API and the static assets from `dist/public`.

## Additional scripts

- `npm run check` runs the TypeScript compiler in type check mode.

## Dependencies

Key runtime libraries include Express, React 18, Vite, the official MongoDB driver, and the OpenAI SDK. Refer to `package.json` for the full dependency list.

## Troubleshooting

- Ensure the required environment variables are in place before running any script.
- Verify that the MongoDB connection string allows connections from your development machine.

## Notes

- Current Q&A uses the full document content. Embeddings are generated and stored for future retrieval, but vector search is not yet wired into the answer flow.
