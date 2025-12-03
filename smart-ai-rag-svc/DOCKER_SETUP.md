# Docker Setup Guide

## Configuration Updated

The Docker configuration has been updated to use **Python 3.12** for LlamaIndex compatibility.

## Prerequisites

1. **Install Docker Desktop**
   - Download from: https://www.docker.com/products/docker-desktop/
   - Install and start Docker Desktop
   - Verify installation:
     ```bash
     docker --version
     docker-compose --version
     ```

## Configuration Files

### Dockerfile
- Uses Python 3.12 (required for LlamaIndex)
- Multi-stage build for smaller image size
- Non-root user for security
- Health checks configured
- Optimized layer caching

### docker-compose.yml
- RAG API service
- MongoDB 7 database
- Volume persistence
- Health checks
- Network isolation
- Auto-restart policies

## Quick Start

### 1. Prepare Environment

```bash
# Copy environment template
cp env.template .env

# Edit with your API keys
nano .env  # or use your preferred editor
```

**Required environment variables:**
```bash
OPENAI_API_KEY=your-openai-api-key-here
MONGODB_URI=mongodb://mongodb:27017  # Auto-configured in docker-compose
MONGODB_DATABASE=rag_database
MONGODB_COLLECTION=documents
```

### 2. Build and Start Services

```bash
# Build the image
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f rag-api
```

### 3. Verify Installation

```bash
# Check service status
docker-compose ps

# Test health endpoint
curl http://localhost:8000/health

# Access Swagger docs
open http://localhost:8000/docs
```

## Docker Commands

### Service Management

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart rag-api

# View logs
docker-compose logs -f rag-api
docker-compose logs -f mongodb

# Check status
docker-compose ps
```

### Development

```bash
# Access container shell
docker-compose exec rag-api bash

# Run tests inside container
docker-compose exec rag-api pytest -v

# View environment variables
docker-compose exec rag-api env

# Rebuild after code changes
docker-compose build rag-api
docker-compose up -d rag-api
```

### Database Management

```bash
# Access MongoDB shell
docker-compose exec mongodb mongosh

# Backup database
docker-compose exec mongodb mongodump --out=/data/backup

# View MongoDB logs
docker-compose logs -f mongodb
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes (WARNING: deletes data)
docker-compose down -v

# Remove unused images
docker image prune -a

# Complete cleanup
docker-compose down -v --rmi all
```

## Production Deployment

### Build Optimized Image

```bash
# Build production image
docker build -t rag-service:1.0.0 -t rag-service:latest .

# Run with specific configuration
docker run -d \
  --name rag-api \
  -p 8000:8000 \
  --env-file .env \
  --restart unless-stopped \
  rag-service:latest
```

### Docker Compose Production

```bash
# Use production compose file
docker-compose -f docker-compose.yml up -d

# Scale services (if needed)
docker-compose up -d --scale rag-api=3
```

### Environment Variables

**Production .env example:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-production-key
OPENAI_MODEL=gpt-4
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# MongoDB Configuration
MONGODB_URI=mongodb://mongodb:27017
MONGODB_DATABASE=rag_database
MONGODB_COLLECTION=documents
MONGODB_VECTOR_INDEX=vector_index

# Application Settings
LOG_LEVEL=info
MAX_UPLOAD_SIZE=10485760
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Feature Flags
ENABLE_EVALUATION=true
ENABLE_CONVERSATION_HISTORY=true
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs rag-api

# Check MongoDB connection
docker-compose exec rag-api ping mongodb

# Verify environment variables
docker-compose config
```

### Database connection issues

```bash
# Check MongoDB health
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Restart MongoDB
docker-compose restart mongodb

# Check network
docker network inspect smart-ai-rag-svc_rag-network
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different port in docker-compose.yml
ports:
  - "8001:8000"
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a

# Remove old volumes
docker volume prune

# Check disk usage
docker system df
```

## Health Checks

The application includes health checks:

**API Health:**
```bash
curl http://localhost:8000/health
```

**Container Health:**
```bash
docker inspect --format='{{.State.Health.Status}}' rag-api
```

**MongoDB Health:**
```bash
docker inspect --format='{{.State.Health.Status}}' rag-mongodb
```

## Monitoring

### View Resource Usage

```bash
# Real-time stats
docker stats

# Specific container
docker stats rag-api

# All compose services
docker-compose top
```

### Logs

```bash
# Tail logs
docker-compose logs -f --tail=100 rag-api

# Save logs to file
docker-compose logs > logs/docker-compose.log

# Filter by time
docker-compose logs --since 30m rag-api
```

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   RAG API    │    │   MongoDB    │  │
│  │  (Python     │◄───┤   Database   │  │
│  │   3.12)      │    │   (Mongo 7)  │  │
│  └──────┬───────┘    └──────────────┘  │
│         │                               │
└─────────┼───────────────────────────────┘
          │
    ┌─────▼─────┐
    │  Port     │
    │  8000     │
    │  (Host)   │
    └───────────┘
```

## Security Best Practices

1. **Non-root user** in container
2. **Multi-stage build** for smaller attack surface
3. **Environment variables** for secrets
4. **Health checks** for reliability
5. **Volume mounts** limited to necessary directories

**Additional recommendations:**
- Use Docker secrets for production
- Enable TLS/HTTPS
- Implement rate limiting
- Use container scanning tools
- Regular security updates

## Testing

### Run Tests in Container

```bash
# Run all tests
docker-compose exec rag-api pytest -v

# Run specific test file
docker-compose exec rag-api pytest tests/unit/test_settings.py -v

# Run with coverage
docker-compose exec rag-api pytest --cov=src tests/
```

## Summary

**Dockerfile**: Python 3.12, multi-stage, optimized  
**docker-compose.yml**: Full stack with MongoDB  
**.dockerignore**: Optimized build context  
**Health checks**: Automatic restart on failure  
**Volumes**: Persistent data storage  
**Networks**: Isolated communication  
**Security**: Non-root user, minimal image  

**Status**: Production Ready

---

**Updated**: December 3, 2025  
**Python Version**: 3.12.9  
**Docker Base**: python:3.12-slim  
**MongoDB Version**: 7

