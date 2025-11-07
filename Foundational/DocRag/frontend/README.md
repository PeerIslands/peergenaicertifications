# RAG PDF Query Frontend

React frontend for the RAG PDF Query System with a modern, user-friendly interface.

## Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Run the development server:**
```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## Features

- **PDF Upload**: Upload multiple PDF files for ingestion
- **Real-time Status**: View system status and document count
- **Sample Questions**: Quick-access buttons for common questions
- **Query Interface**: Ask questions and get AI-powered answers
- **Source Attribution**: See which documents and pages were used
- **System Reset**: Clear all ingested documents

## Usage

1. **Upload PDFs**: Click "Upload & Ingest PDFs" to add documents to the system
2. **Ask Questions**: Type your question or use a sample question
3. **View Results**: See the AI-generated answer with source references

## Tech Stack

- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client
- **CSS3**: Modern styling with gradients and animations

## API Integration

The frontend connects to the FastAPI backend at `http://localhost:8000`. Make sure the backend is running before starting the frontend.

## Build for Production

```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

