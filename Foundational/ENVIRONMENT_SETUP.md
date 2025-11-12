# Environment Variables Setup

## Required Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# OpenAI Configuration (for OpenRouter)
# REQUIRED for RAG search functionality
OPENROUTER_API_KEY=your-openrouter-api-key

# Server Configuration
NODE_ENV=development
PORT=3000
```

## How to Get OpenRouter API Key

**IMPORTANT**: The RAG search feature requires a valid OpenRouter API key. Without it, you'll get a "401 User not found" error.

1. Go to [OpenRouter](https://openrouter.ai/) and sign up for a free account
2. Navigate to [API Keys](https://openrouter.ai/keys)
3. Click "Create Key" to generate a new API key
4. Copy the API key and add it to your `.env` file as `OPENROUTER_API_KEY`
5. The free tier includes access to the `openai/gpt-oss-20b:free` model used by this application

**Note**: Make sure your `.env` file is in the project root directory (`peergenaicertifications/Foundational/.env`)

## How to Get Supabase Credentials

1. Go to [Supabase](https://supabase.com) and create a new project
2. In your project dashboard, go to Settings > API
3. Copy the Project URL and anon/public key
4. Use these values for `SUPABASE_URL` and `SUPABASE_KEY`

## Migration from MongoDB

If you're migrating from MongoDB, you can remove these variables:
- `MONGODB_URI`
- `MONGODB_DATABASE`

## Troubleshooting

### "401 User not found" Error

If you encounter this error when performing RAG searches:

1. **Check if `.env` file exists**: Make sure you have a `.env` file in the project root
2. **Verify API key is set**: Check that `OPENROUTER_API_KEY` is in your `.env` file
3. **Check API key validity**: Make sure your OpenRouter API key is valid and not expired
4. **Restart the server**: After updating `.env`, restart your development server
5. **Check file location**: Ensure `.env` is in `peergenaicertifications/Foundational/` directory

### Testing the Setup

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

To verify your OpenRouter API key is working, check the server logs when starting the application. You should see:
```
OpenRouter API Key loaded: Yes
API Key length: [number]
```
