# Docker Setup for QueryMindAI

This document provides instructions for running QueryMindAI using Docker and Docker Compose.

## Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- Environment variables configured (see `env-template.txt`)

## Quick Start

### Production Setup

1. **Create a `.env` file** from the template:
   ```bash
   cp env-template.txt .env
   ```

2. **Update the `.env` file** with your configuration:
   - Set `AZURE_OPENAI_API_KEY` and related Azure OpenAI settings
   - Update `MONGODB_URI` if using external MongoDB (or leave default for containerized MongoDB)
   - Update `DATABASE_URL` if using external PostgreSQL (or leave default for containerized PostgreSQL)
   - Set `SESSION_SECRET` to a secure random string

3. **Build and start all services**:
   ```bash
   docker-compose up -d
   ```

4. **Initialize Ollama embedding model** (first time only):
   ```bash
   docker exec querymindai-ollama ollama pull embeddinggemma
   ```

5. **Access the application**:
   - Application: http://localhost:5000
   - MongoDB: localhost:27017
   - PostgreSQL: localhost:5432
   - Ollama: http://localhost:11434

### Development Setup

For development, you can run only the supporting services (MongoDB, PostgreSQL, Ollama) in Docker while running the app locally:

1. **Start supporting services**:
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Update your `.env` file** to point to the Docker services:
   ```env
   MONGODB_URI=mongodb://localhost:27017/
   DATABASE_URL=postgresql://querymind:querymind123@localhost:5432/querymind_db
   OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Run the application locally**:
   ```bash
   npm install
   npm run dev
   ```

## Docker Commands

### Build the application image
```bash
docker-compose build
```

### Start services
```bash
docker-compose up -d
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes data)
```bash
docker-compose down -v
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Execute commands in containers
```bash
# Access app container shell
docker exec -it querymindai-app sh

# Run database migrations
docker exec querymindai-app npm run db:push

# Pull Ollama model
docker exec querymindai-ollama ollama pull embeddinggemma
```

## Service Details

### Application Service (`app`)
- **Image**: Built from `Dockerfile`
- **Port**: 5000 (configurable via `PORT` env var)
- **Health Check**: `/api/health` endpoint
- **Dependencies**: MongoDB, PostgreSQL, Ollama

### MongoDB Service (`mongodb`)
- **Image**: `mongo:7.0`
- **Port**: 27017
- **Data Volume**: `mongodb_data`
- **Health Check**: MongoDB ping command

### PostgreSQL Service (`postgres`)
- **Image**: `postgres:16-alpine`
- **Port**: 5432
- **Credentials**: 
  - User: `querymind`
  - Password: `querymind123`
  - Database: `querymind_db`
- **Data Volume**: `postgres_data`
- **Health Check**: `pg_isready`

### Ollama Service (`ollama`)
- **Image**: `ollama/ollama:latest`
- **Port**: 11434
- **Data Volume**: `ollama_data`
- **Note**: You need to pull the embedding model manually after first start

## Environment Variables

Key environment variables for Docker:

- `PORT`: Application port (default: 5000)
- `NODE_ENV`: Set to `production` in Docker
- `AZURE_OPENAI_API_KEY`: Required for chat functionality
- `MONGODB_URI`: MongoDB connection string (defaults to containerized MongoDB)
- `DATABASE_URL`: PostgreSQL connection string (defaults to containerized PostgreSQL)
- `OLLAMA_BASE_URL`: Ollama service URL (defaults to containerized Ollama)

## Troubleshooting

### Application won't start
- Check logs: `docker-compose logs app`
- Verify all environment variables are set
- Ensure MongoDB and PostgreSQL are healthy: `docker-compose ps`

### MongoDB connection issues
- Verify MongoDB is running: `docker-compose ps mongodb`
- Check MongoDB logs: `docker-compose logs mongodb`
- Ensure `MONGODB_URI` points to `mongodb://mongodb:27017/` in Docker

### Ollama model not found
- Pull the model: `docker exec querymindai-ollama ollama pull embeddinggemma`
- Check Ollama logs: `docker-compose logs ollama`

### Port conflicts
- Change port mappings in `docker-compose.yml`
- Update `PORT` environment variable accordingly

### Data persistence
- Data is stored in Docker volumes
- Volumes persist even after `docker-compose down`
- Use `docker-compose down -v` to remove volumes (⚠️ deletes data)

## Production Considerations

1. **Security**:
   - Change default PostgreSQL password
   - Use strong `SESSION_SECRET`
   - Don't commit `.env` file
   - Use Docker secrets for sensitive data

2. **Performance**:
   - Configure resource limits in `docker-compose.yml`
   - Use external managed databases for production
   - Consider using Docker Swarm or Kubernetes for orchestration

3. **Monitoring**:
   - Set up health checks (already configured)
   - Use logging aggregation
   - Monitor container resources

4. **Backup**:
   - Regularly backup Docker volumes
   - Export MongoDB and PostgreSQL data
   - Document backup and restore procedures

