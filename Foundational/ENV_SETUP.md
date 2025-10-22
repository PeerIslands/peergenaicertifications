# Environment Setup Guide

Instructions for setting up environment variables for the Foundational application.

## Environment Variables

### Backend Configuration

Create a `.env` file in the `backend/` directory:

```bash
# OpenAI Configuration (Required)
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Configuration
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# File Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/chatpdf
```

### Frontend Configuration

Create a `.env` file in the `frontend/` directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
```

### Docker Configuration

Create a `.env` file in the root `Foundational/` directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Environment
DEBUG=False

# Model Configuration (optional)
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7
MAX_FILE_SIZE=10485760
```

## Getting OpenAI API Key

1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

**Important:** Never commit your API key to version control!

## Environment-Specific Configurations

### Development

```bash
# backend/.env.development
DEBUG=True
LOG_LEVEL=DEBUG
MONGODB_URI=mongodb://localhost:27017/chatpdf_dev
```

### Testing

```bash
# backend/.env.test
DEBUG=False
MONGODB_URI=mongodb://localhost:27017/test_chatpdf
OPENAI_API_KEY=test-key-12345
```

### Production

```bash
# backend/.env.production
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
MONGODB_URI=mongodb://production-host:27017/chatpdf
# Use secrets manager for OPENAI_API_KEY
```

## Verification

### Backend

```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### Docker

```bash
docker-compose config
# This will show the resolved configuration with environment variables
```

## Troubleshooting

### Issue: Environment variables not loading

**Solution:**
- Ensure `.env` file is in the correct directory
- Check file permissions
- Verify no syntax errors in `.env` file
- Make sure python-dotenv is installed: `pip install python-dotenv`

### Issue: OpenAI API errors

**Solution:**
- Verify API key is valid
- Check OpenAI account has credits
- Ensure no extra spaces in API key
- Test API key: `curl https://api.openai.com/v1/models -H "Authorization: Bearer YOUR_API_KEY"`

### Issue: Database connection errors

**Solution:**
- Verify MongoDB is running: `docker-compose ps`
- Check MONGODB_URI format
- Ensure MongoDB port is not in use
- Test connection: `mongosh mongodb://localhost:27017/chatpdf`

## Security Best Practices

1. **Never commit `.env` files**
   - Add `.env` to `.gitignore`
   - Use `.env.example` as a template

2. **Use secrets management in production**
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Rotate API keys regularly**
   - Set reminders to rotate keys
   - Use different keys for different environments
   - Revoke old keys after rotation

4. **Restrict API key permissions**
   - Use the minimum required permissions
   - Monitor API usage
   - Set rate limits

## Additional Configuration

### Logging

```bash
# Advanced logging configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json  # json or text
LOG_FILE=/var/log/foundational/app.log
```

### Performance

```bash
# Worker configuration
WORKER_COUNT=4
MAX_CONNECTIONS=100
TIMEOUT=30
KEEP_ALIVE=5
```

### Security

```bash
# CORS configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
ALLOWED_METHODS=GET,POST,DELETE
ALLOWED_HEADERS=*

# Rate limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

## Template Files

### .env.example (Backend)

```bash
# Copy this file to .env and fill in your values

# OpenAI Configuration (Required)
OPENAI_API_KEY=

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Configuration
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# File Configuration
MAX_FILE_SIZE=10485760

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/chatpdf
```

Save this as `backend/.env.example` and commit to version control.

