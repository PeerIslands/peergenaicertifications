# QueryMindAI Production Deployment Guide

This guide provides comprehensive instructions for deploying QueryMindAI to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Monitoring and Logging](#monitoring-and-logging)
- [Scaling and Performance](#scaling-and-performance)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. **Node.js 20+** (if deploying without Docker)
2. **Docker and Docker Compose** (recommended)
3. **MongoDB** (Atlas or self-hosted)
4. **PostgreSQL** (for Drizzle ORM, optional)
5. **Ollama** (for embeddings, can be containerized)
6. **Azure OpenAI** account with API key
7. **Domain name** (optional, for production)
8. **SSL certificate** (for HTTPS)

## Deployment Options

### Option 1: Docker Compose (Recommended for Single Server)

Best for:
- Single server deployments
- Development/staging environments
- Quick setup

### Option 2: Kubernetes

Best for:
- Multi-server deployments
- High availability requirements
- Auto-scaling needs

### Option 3: Cloud Platform (AWS, Azure, GCP)

Best for:
- Managed services
- Enterprise deployments
- Integrated monitoring

## Docker Deployment

### Step 1: Prepare the Server

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

### Step 2: Clone and Configure

```bash
# Clone repository
git clone <repository-url>
cd QueryMindAI

# Create production environment file
cp env-template.txt .env.production

# Edit environment variables
nano .env.production
```

### Step 3: Configure Environment Variables

Edit `.env.production` with production values:

```env
# Server Configuration
PORT=5000
NODE_ENV=production
HOST=0.0.0.0

# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=your_production_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_OPENAI_MODEL_NAME=gpt-4o-mini
AZURE_OPENAI_API_VERSION=2024-07-18
AZURE_OPENAI_TEMPERATURE=0.5
AZURE_OPENAI_MAX_TOKENS=500

# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=query-mind
MONGODB_COLLECTION=knowledge-base

# PostgreSQL Configuration (Optional)
DATABASE_URL=postgresql://username:password@postgres:5432/querymind_db

# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434

# Security
SESSION_SECRET=generate-a-strong-random-secret-here
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Logging
LOG_LEVEL=info
```

**Important:** Generate a strong session secret:
```bash
openssl rand -base64 32
```

### Step 4: Build and Deploy

```bash
# Build and start services
docker-compose -f docker-compose.yml up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f app
```

### Step 5: Initialize Ollama Model

```bash
# Pull the embedding model
docker exec querymindai-ollama ollama pull embeddinggemma

# Verify model is available
docker exec querymindai-ollama ollama list
```

### Step 6: Verify Deployment

```bash
# Health check
curl http://localhost:5000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "rag": { "status": "ready", "documents": 123 },
#   "mongodb": "connected",
#   "timestamp": "2024-01-01T00:00:00.000Z"
# }
```

## Cloud Platform Deployment

### AWS Deployment

#### Using ECS (Elastic Container Service)

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name querymindai
```

2. **Build and Push Image**
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t querymindai .

# Tag image
docker tag querymindai:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/querymindai:latest

# Push image
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/querymindai:latest
```

3. **Create ECS Task Definition**
   - Use AWS Console or Terraform
   - Configure environment variables
   - Set up service discovery

4. **Create ECS Service**
   - Configure load balancer
   - Set desired count
   - Configure auto-scaling

#### Using Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB
eb init -p docker querymindai-app

# Create environment
eb create querymindai-prod

# Deploy
eb deploy
```

### Azure Deployment

#### Using Azure Container Instances

```bash
# Login to Azure
az login

# Create resource group
az group create --name querymindai-rg --location eastus

# Create container instance
az container create \
  --resource-group querymindai-rg \
  --name querymindai-app \
  --image <your-registry>/querymindai:latest \
  --dns-name-label querymindai \
  --ports 5000 \
  --environment-variables \
    NODE_ENV=production \
    PORT=5000 \
    MONGODB_URI=<your-mongodb-uri>
```

#### Using Azure App Service

1. Create App Service Plan
2. Create Web App for Containers
3. Configure environment variables
4. Set up continuous deployment

### Google Cloud Platform Deployment

#### Using Cloud Run

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/querymindai

# Deploy to Cloud Run
gcloud run deploy querymindai \
  --image gcr.io/YOUR_PROJECT_ID/querymindai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NODE_ENV=production
```

## Environment Configuration

### Production Environment Variables

| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `NODE_ENV` | Environment mode | Yes | `production` |
| `PORT` | Server port | Yes | `5000` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI key | Yes | `sk-...` |
| `AZURE_OPENAI_ENDPOINT` | Azure endpoint | Yes | `https://...` |
| `MONGODB_URI` | MongoDB connection | Yes | `mongodb+srv://...` |
| `OLLAMA_BASE_URL` | Ollama server URL | Yes | `http://ollama:11434` |
| `SESSION_SECRET` | Session encryption key | Yes | Random string |
| `CORS_ORIGINS` | Allowed origins | Recommended | `https://domain.com` |
| `LOG_LEVEL` | Logging level | No | `info` |

### Secrets Management

**Option 1: Environment Files (Docker)**
- Use `.env` files (never commit to git)
- Restrict file permissions: `chmod 600 .env`

**Option 2: Secret Management Services**
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## Database Setup

### MongoDB Atlas Setup

1. **Create Cluster**
   - Choose region closest to your app
   - Select M10 or higher for production

2. **Configure Network Access**
   - Add your server IP or `0.0.0.0/0` (less secure)
   - Use VPC peering for better security

3. **Create Database User**
   - Use strong password
   - Grant read/write permissions

4. **Create Vector Search Index**
```javascript
db.knowledge-base.createSearchIndex({
  "definition": {
    "mappings": {
      "dynamic": true,
      "fields": {
        "embedding": {
          "type": "knnVector",
          "dimensions": 768,
          "similarity": "cosine"
        }
      }
    }
  }
})
```

### PostgreSQL Setup (Optional)

```bash
# Using Docker
docker run -d \
  --name postgres \
  -e POSTGRES_USER=querymind \
  -e POSTGRES_PASSWORD=strong_password \
  -e POSTGRES_DB=querymind_db \
  -p 5432:5432 \
  postgres:16-alpine

# Run migrations
npm run db:push
```

## Monitoring and Logging

### Application Monitoring

**Option 1: Built-in Health Endpoint**
```bash
curl https://yourdomain.com/api/health
```

**Option 2: Prometheus Metrics**
- Add Prometheus client
- Expose `/metrics` endpoint
- Configure Grafana dashboards

**Option 3: APM Tools**
- New Relic
- Datadog
- Application Insights (Azure)

### Logging Setup

**Docker Logs**
```bash
# View logs
docker-compose logs -f app

# Export logs
docker-compose logs app > app.log
```

**Centralized Logging**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- CloudWatch Logs (AWS)
- Azure Monitor (Azure)
- Cloud Logging (GCP)

### Health Checks

Configure health checks in your deployment:

```yaml
# docker-compose.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

## Scaling and Performance

### Horizontal Scaling

**Docker Compose with Multiple Instances**
```yaml
# Scale app service
docker-compose up -d --scale app=3
```

**Load Balancer Configuration**
- Use Nginx or Traefik as reverse proxy
- Configure sticky sessions if needed
- Set up health checks

**Nginx Configuration Example**
```nginx
upstream querymindai {
    least_conn;
    server app1:5000;
    server app2:5000;
    server app3:5000;
}

server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://querymindai;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Vertical Scaling

- Increase container resources
- Upgrade database tier
- Optimize Ollama model size

### Performance Optimization

1. **Enable Caching**
   - Redis for session storage
   - Response caching for static content

2. **Database Optimization**
   - Create indexes on frequently queried fields
   - Use connection pooling
   - Monitor slow queries

3. **CDN for Static Assets**
   - Serve static files via CDN
   - Enable gzip compression

## Security Considerations

### 1. HTTPS/SSL

**Using Let's Encrypt with Certbot**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 2. Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. Security Headers

Add security headers in your reverse proxy:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000" always;
```

### 4. Rate Limiting

Implement rate limiting:
```javascript
// Using express-rate-limit
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});
```

### 5. Environment Variables Security

- Never commit `.env` files
- Use secret management services
- Rotate secrets regularly
- Use different secrets per environment

## Troubleshooting

### Common Issues

**1. Application Won't Start**
```bash
# Check logs
docker-compose logs app

# Verify environment variables
docker-compose config

# Test database connection
docker exec querymindai-app node -e "require('./dist/mongodb').test()"
```

**2. MongoDB Connection Issues**
- Verify MongoDB URI format
- Check network connectivity
- Verify IP whitelist (Atlas)
- Check authentication credentials

**3. Ollama Embedding Errors**
```bash
# Check Ollama service
docker exec querymindai-ollama ollama list

# Pull model if missing
docker exec querymindai-ollama ollama pull embeddinggemma

# Test embedding generation
docker exec querymindai-ollama ollama run embeddinggemma "test"
```

**4. High Memory Usage**
- Monitor container resources: `docker stats`
- Increase memory limits in docker-compose
- Optimize chunk sizes in RAG configuration
- Consider using smaller embedding models

**5. Slow Response Times**
- Check database query performance
- Monitor Ollama response times
- Review Azure OpenAI API latency
- Check network connectivity

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=debug
NODE_ENV=development
```

### Backup and Recovery

**MongoDB Backup**
```bash
# Backup
mongodump --uri="mongodb+srv://..." --out=/backup

# Restore
mongorestore --uri="mongodb+srv://..." /backup
```

**Application Backup**
- Backup environment files
- Backup Docker volumes
- Document configuration

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   npm audit
   npm update
   ```

2. **Monitor Logs**
   - Review error logs daily
   - Check performance metrics

3. **Database Maintenance**
   - Regular backups
   - Index optimization
   - Cleanup old data

4. **Security Updates**
   - Update base images
   - Patch vulnerabilities
   - Rotate secrets

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose up -d --build

# Verify health
curl http://localhost:5000/api/health
```

## Support and Resources

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Health Check**: `/api/health`
- **Logs**: `docker-compose logs -f`

---

**Last Updated**: 2024
**Version**: 1.0.0

