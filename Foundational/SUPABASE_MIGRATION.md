# MongoDB to Supabase Migration Guide

This guide explains how to migrate from MongoDB to Supabase for the PDF RAG application.

## Overview

The application has been migrated from MongoDB to Supabase, providing:
- PostgreSQL database with vector search capabilities
- Built-in authentication and authorization
- Real-time subscriptions
- Better scalability and performance

## Migration Steps

### 1. Set up Supabase Project

1. Go to [Supabase](https://supabase.com) and create a new project
2. Note down your project URL and API key
3. Run the SQL setup script in your Supabase SQL editor

### 2. Run Database Setup

Execute the SQL commands in `supabase-setup.sql` in your Supabase SQL editor:

```sql
-- This will create all necessary tables, indexes, and functions
-- See supabase-setup.sql for the complete script
```

### 3. Update Environment Variables

Add these environment variables to your `.env` file:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Remove or comment out MongoDB variables
# MONGODB_URI=mongodb://localhost:27017
# MONGODB_DATABASE=pdf_rag
```

### 4. Install Dependencies

The Supabase client has been added to package.json:

```bash
npm install @supabase/supabase-js
```

### 5. Code Changes Made

#### New Files Created:
- `shared/supabase-schema.ts` - Supabase database schema definitions
- `server/supabase-storage.ts` - Supabase storage service implementation
- `supabase-setup.sql` - Database setup script

#### Files Modified:
- `server/services/ragService.ts` - Updated to use Supabase storage
- `server/routes.ts` - Updated to use Supabase storage
- All MongoDB references replaced with Supabase equivalents

#### Files Removed/Deprecated:
- `server/mongodb-storage.ts` - Can be removed after migration
- `shared/mongodb-schema.ts` - Can be removed after migration

## Database Schema Changes

### Documents Table
```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  size INTEGER NOT NULL,
  status TEXT NOT NULL DEFAULT 'uploading',
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  chunks INTEGER NOT NULL DEFAULT 0,
  content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Document Chunks Table (with Vector Support)
```sql
CREATE TABLE document_chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  embedding VECTOR(384), -- 384-dimensional vector for embeddings
  page_number INTEGER,
  chunk_index INTEGER NOT NULL,
  metadata JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Search Queries Table
```sql
CREATE TABLE search_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query TEXT NOT NULL,
  response TEXT,
  sources JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## Key Features

### Vector Search
- Uses pgvector extension for efficient vector similarity search
- 384-dimensional embeddings for document chunks
- Cosine similarity search with configurable thresholds

### Row Level Security (RLS)
- All tables have RLS enabled
- Currently allows all operations (adjust based on your auth needs)

### Automatic Timestamps
- `created_at` and `updated_at` fields automatically managed
- Triggers update `updated_at` on record modifications

## API Compatibility

The API endpoints remain the same:
- `GET /api/documents` - Get all documents
- `POST /api/documents/upload` - Upload PDF document
- `GET /api/documents/:id` - Get specific document
- `DELETE /api/documents/:id` - Delete document
- `POST /api/search` - Perform RAG search
- `GET /api/stats` - Get processing statistics

## Testing the Migration

1. Start the application: `npm run dev`
2. Upload a PDF document
3. Wait for processing to complete
4. Perform a search query
5. Verify all functionality works as expected

## Troubleshooting

### Common Issues

1. **Vector search not working**: Ensure pgvector extension is enabled in Supabase
2. **Connection errors**: Verify SUPABASE_URL and SUPABASE_KEY are correct
3. **Permission errors**: Check RLS policies in Supabase dashboard

### Debugging

Enable debug logging by setting:
```env
DEBUG=supabase:*
```

## Performance Considerations

- Vector search is optimized with IVFFlat index
- Regular indexes on frequently queried fields
- JSONB for flexible metadata storage
- Automatic connection pooling via Supabase client

## Security

- All tables have RLS enabled
- API keys should be kept secure
- Consider implementing user-based access control
- Regular security updates for dependencies

## Next Steps

1. Test the migration thoroughly
2. Update any client-side code if needed
3. Remove old MongoDB files
4. Consider implementing user authentication
5. Set up monitoring and logging
6. Configure backup strategies
