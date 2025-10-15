# Environment Variables Setup

## Required Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# OpenAI Configuration (for OpenRouter)
OPENROUTER_API_KEY=your-openrouter-api-key

# Server Configuration
NODE_ENV=development
PORT=3000
```

## How to Get Supabase Credentials

1. Go to [Supabase](https://supabase.com) and create a new project
2. In your project dashboard, go to Settings > API
3. Copy the Project URL and anon/public key
4. Use these values for `SUPABASE_URL` and `SUPABASE_KEY`

## Migration from MongoDB

If you're migrating from MongoDB, you can remove these variables:
- `MONGODB_URI`
- `MONGODB_DATABASE`

## Testing the Setup

Run the test script to verify your Supabase connection:

```bash
npm run test:supabase
```

This will test:
- Database connection
- Document creation
- Chunk creation
- Search functionality
- Data cleanup
