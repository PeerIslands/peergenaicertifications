# QueryMindIngestion Production Deployment Guide

This guide provides comprehensive instructions for deploying the QueryMindIngestion PDF processing tool to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deployment Options](#deployment-options)
- [Docker Deployment](#docker-deployment)
- [Cloud Platform Deployment](#cloud-platform-deployment)
- [Environment Configuration](#environment-configuration)
- [Database Setup](#database-setup)
- [Scheduling and Automation](#scheduling-and-automation)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have:

1. **Python 3.9+** (if deploying without Docker)
2. **Docker and Docker Compose** (recommended)
3. **MongoDB** (Atlas or self-hosted)
4. **Ollama** (for embeddings, can be containerized)
5. **Storage** for PDF files (local or cloud storage)
6. **Network access** to MongoDB and Ollama services

## Deployment Options

### Option 1: Docker Compose (Recommended)

Best for:
- Single server deployments
- Development/staging environments
- Quick setup with all dependencies

### Option 2: Kubernetes Jobs/CronJobs

Best for:
- Scheduled batch processing
- Multi-server deployments
- Auto-scaling needs

### Option 3: Cloud Functions/Serverless

Best for:
- Event-driven processing
- Cost-effective for sporadic workloads
- Managed scaling

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

### Step 2: Create Dockerfile

Create `QueryMindIngestion/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create PDFs directory
RUN mkdir -p /app/pdfs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run the ingestion tool
CMD ["python", "pdf_ingestion_tool.py"]
```

### Step 3: Create Docker Compose File

Create `QueryMindIngestion/docker-compose.yml`:

```yaml
version: '3.8'

services:
  ingestion:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: querymindingestion
    volumes:
      - ./pdfs:/app/pdfs
      - ./logs:/app/logs
    environment:
      - PDF_FOLDER_PATH=/app/pdfs
      - MONGODB_URI=${MONGODB_URI}
      - MONGODB_DATABASE=${MONGODB_DATABASE:-query-mind}
      - MONGODB_COLLECTION=${MONGODB_COLLECTION:-knowledge-base}
      - OLLAMA_BASE_URL=${OLLAMA_BASE_URL:-http://ollama:11434}
      - EMBEDDING_MODEL=${EMBEDDING_MODEL:-embeddinggemma}
      - CHUNK_SIZE=${CHUNK_SIZE:-1000}
      - CHUNK_OVERLAP=${CHUNK_OVERLAP:-200}
    depends_on:
      ollama:
        condition: service_started
    restart: unless-stopped
    networks:
      - ingestion-network

  ollama:
    image: ollama/ollama:latest
    container_name: querymindingestion-ollama
    ports:
      - "${OLLAMA_PORT:-11434}:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped
    networks:
      - ingestion-network

volumes:
  ollama_data:
    driver: local

networks:
  ingestion-network:
    driver: bridge
```

### Step 4: Configure Environment

Create `.env` file:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=query-mind
MONGODB_COLLECTION=knowledge-base

# Ollama Configuration
OLLAMA_BASE_URL=http://ollama:11434
EMBEDDING_MODEL=embeddinggemma
OLLAMA_PORT=11434

# Chunking Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# PDF Configuration
PDF_FOLDER_PATH=./pdfs
```

### Step 5: Build and Deploy

```bash
# Navigate to ingestion directory
cd QueryMindIngestion

# Build and start services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f ingestion
```

### Step 6: Initialize Ollama Model

```bash
# Pull the embedding model
docker exec querymindingestion-ollama ollama pull embeddinggemma

# Verify model is available
docker exec querymindingestion-ollama ollama list
```

### Step 7: Run Ingestion

**Option 1: One-time Run**
```bash
# Place PDFs in ./pdfs directory
docker exec querymindingestion python pdf_ingestion_tool.py
```

**Option 2: Continuous Monitoring**
```bash
# The container will process PDFs automatically if configured
# Or use a cron job to trigger periodically
```

## Cloud Platform Deployment

### AWS Deployment

#### Using ECS with Scheduled Tasks

1. **Create ECR Repository**
```bash
aws ecr create-repository --repository-name querymindingestion
```

2. **Build and Push Image**
```bash
# Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t querymindingestion .

# Tag and push
docker tag querymindingestion:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/querymindingestion:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/querymindingestion:latest
```

3. **Create ECS Task Definition**
   - Configure environment variables
   - Set up IAM roles
   - Configure resource limits

4. **Create Scheduled Task**
   - Use EventBridge (CloudWatch Events)
   - Set cron expression: `0 2 * * ? *` (daily at 2 AM)
   - Configure target as ECS task

#### Using Lambda (Serverless)

1. **Package as Lambda Layer**
```bash
# Create deployment package
pip install -r requirements.txt -t python/
zip -r ingestion-layer.zip python/
```

2. **Create Lambda Function**
   - Use Python 3.11 runtime
   - Attach layer with dependencies
   - Configure environment variables
   - Set timeout (15 minutes max)

3. **Trigger Options**
   - S3 event (when PDF uploaded)
   - EventBridge schedule
   - API Gateway (manual trigger)

### Azure Deployment

#### Using Container Instances with Logic Apps

```bash
# Create resource group
az group create --name ingestion-rg --location eastus

# Create container instance
az container create \
  --resource-group ingestion-rg \
  --name querymindingestion \
  --image <your-registry>/querymindingestion:latest \
  --environment-variables \
    MONGODB_URI=<your-mongodb-uri> \
    OLLAMA_BASE_URL=<ollama-url>
```

#### Using Azure Functions

1. Create Function App
2. Configure Python runtime
3. Set up timer trigger or blob trigger
4. Deploy function code

### Google Cloud Platform Deployment

#### Using Cloud Run Jobs

```bash
# Build and push
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/querymindingestion

# Create Cloud Run job
gcloud run jobs create querymindingestion \
  --image gcr.io/YOUR_PROJECT_ID/querymindingestion \
  --region us-central1 \
  --set-env-vars MONGODB_URI=<uri>,OLLAMA_BASE_URL=<url>

# Execute job
gcloud run jobs execute querymindingestion --region us-central1

# Schedule with Cloud Scheduler
gcloud scheduler jobs create http ingestion-job \
  --schedule="0 2 * * *" \
  --uri="https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/PROJECT_ID/jobs/querymindingestion:run" \
  --http-method=POST \
  --oauth-service-account-email=<service-account>@<project>.iam.gserviceaccount.com
```

## Environment Configuration

### Production Environment Variables

| Variable | Description | Required | Default | Example |
|----------|-------------|----------|---------|---------|
| `PDF_FOLDER_PATH` | Path to PDF files | Yes | `./pdfs` | `/app/pdfs` |
| `MONGODB_URI` | MongoDB connection | Yes | - | `mongodb+srv://...` |
| `MONGODB_DATABASE` | Database name | Yes | `query-mind` | `query-mind` |
| `MONGODB_COLLECTION` | Collection name | Yes | `knowledge-base` | `knowledge-base` |
| `OLLAMA_BASE_URL` | Ollama server URL | Yes | `http://localhost:11434` | `http://ollama:11434` |
| `EMBEDDING_MODEL` | Embedding model name | Yes | `embeddinggemma` | `embeddinggemma` |
| `CHUNK_SIZE` | Text chunk size | No | `1000` | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | No | `200` | `200` |
| `LOG_LEVEL` | Logging level | No | `INFO` | `DEBUG` |

### Secrets Management

**Option 1: Environment Files**
- Use `.env` files (never commit to git)
- Restrict permissions: `chmod 600 .env`

**Option 2: Secret Management Services**
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Kubernetes Secrets

## Database Setup

### MongoDB Atlas Setup

1. **Create Cluster**
   - Choose appropriate tier (M5+ for production)
   - Select region close to your processing location

2. **Configure Network Access**
   - Add server IP addresses
   - Use VPC peering for better security

3. **Create Database User**
   - Use strong password
   - Grant read/write permissions to target database

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

5. **Verify Index Creation**
```javascript
db.knowledge-base.listSearchIndexes()
```

## Scheduling and Automation

### Cron Job (Linux)

```bash
# Edit crontab
crontab -e

# Run daily at 2 AM
0 2 * * * cd /path/to/QueryMindIngestion && docker-compose exec -T ingestion python pdf_ingestion_tool.py >> /var/log/ingestion.log 2>&1

# Run every 6 hours
0 */6 * * * cd /path/to/QueryMindIngestion && docker-compose exec -T ingestion python pdf_ingestion_tool.py
```

### Systemd Timer (Linux)

Create `/etc/systemd/system/ingestion.service`:
```ini
[Unit]
Description=QueryMind Ingestion Service
After=docker.service

[Service]
Type=oneshot
ExecStart=/usr/bin/docker exec querymindingestion python pdf_ingestion_tool.py
User=root
```

Create `/etc/systemd/system/ingestion.timer`:
```ini
[Unit]
Description=Run ingestion daily
Requires=ingestion.service

[Timer]
OnCalendar=daily
OnCalendar=02:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable timer:
```bash
sudo systemctl enable ingestion.timer
sudo systemctl start ingestion.timer
```

### Watchdog Script

Create a monitoring script that watches for new PDFs:

```python
#!/usr/bin/env python3
import os
import time
from pathlib import Path
from pdf_ingestion_tool import PDFIngestionTool

PDF_DIR = Path(os.getenv('PDF_FOLDER_PATH', './pdfs'))
PROCESSED_DIR = PDF_DIR / 'processed'
PROCESSED_DIR.mkdir(exist_ok=True)

def watch_and_process():
    tool = PDFIngestionTool()
    
    while True:
        pdf_files = list(PDF_DIR.glob('*.pdf'))
        
        for pdf_file in pdf_files:
            if pdf_file not in PROCESSED_DIR.iterdir():
                print(f"Processing {pdf_file.name}...")
                try:
                    # Process single file
                    tool.process_pdf(pdf_file)
                    # Move to processed
                    pdf_file.rename(PROCESSED_DIR / pdf_file.name)
                except Exception as e:
                    print(f"Error processing {pdf_file.name}: {e}")
        
        time.sleep(60)  # Check every minute

if __name__ == '__main__':
    watch_and_process()
```

## Monitoring and Logging

### Application Logging

**Configure Logging in Application**
```python
import logging
import os

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ingestion.log'),
        logging.StreamHandler()
    ]
)
```

**Docker Logs**
```bash
# View logs
docker-compose logs -f ingestion

# Export logs
docker-compose logs ingestion > ingestion.log

# Log rotation
docker-compose logs --tail=1000 ingestion
```

### Monitoring Metrics

**Key Metrics to Monitor:**
- PDFs processed per day
- Processing time per PDF
- Chunks created
- Embeddings generated
- MongoDB write operations
- Error rates
- Ollama response times

**Create Monitoring Script**
```python
from mongodb_client import MongoDBClient
import json

def get_processing_stats():
    mongo = MongoDBClient()
    collection = mongo.get_collection()
    
    stats = {
        'total_documents': collection.count_documents({}),
        'documents_with_embeddings': collection.count_documents({'embedding': {'$exists': True}}),
        'unique_sources': len(collection.distinct('metadata.source_file')),
        'avg_chunk_size': collection.aggregate([
            {'$group': {'_id': None, 'avg': {'$avg': '$chunk_size'}}}
        ]).next()['avg'] if collection.count_documents({}) > 0 else 0
    }
    
    return stats

if __name__ == '__main__':
    print(json.dumps(get_processing_stats(), indent=2))
```

### Health Checks

**Create Health Check Endpoint**
```python
def health_check():
    checks = {
        'mongodb': test_mongodb_connection(),
        'ollama': test_ollama_connection(),
        'pdf_folder': os.path.exists(PDF_FOLDER_PATH)
    }
    
    return {
        'status': 'healthy' if all(checks.values()) else 'unhealthy',
        'checks': checks
    }
```

## Security Considerations

### 1. File Access Security

```bash
# Restrict PDF directory permissions
chmod 700 pdfs/
chown root:root pdfs/

# Scan uploaded PDFs for malware
# Use ClamAV or similar
```

### 2. Network Security

- Use VPN or private networks
- Restrict MongoDB access to specific IPs
- Use TLS/SSL for MongoDB connections
- Secure Ollama endpoint

### 3. Credentials Management

- Never hardcode credentials
- Use environment variables or secret managers
- Rotate credentials regularly
- Use different credentials per environment

### 4. Input Validation

```python
# Validate PDF files before processing
import magic

def is_valid_pdf(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path) == 'application/pdf'
```

## Troubleshooting

### Common Issues

**1. MongoDB Connection Errors**
```bash
# Test connection
python -c "from mongodb_client import MongoDBClient; m = MongoDBClient(); print(m.test_connection())"

# Check network connectivity
ping <mongodb-host>

# Verify credentials
mongosh "<mongodb-uri>"
```

**2. Ollama Connection Issues**
```bash
# Check Ollama service
curl http://localhost:11434/api/tags

# Verify model is available
docker exec querymindingestion-ollama ollama list

# Test embedding generation
docker exec querymindingestion-ollama ollama run embeddinggemma "test"
```

**3. PDF Reading Errors**
```bash
# Check file permissions
ls -la pdfs/

# Verify PDF is not corrupted
file pdfs/document.pdf

# Test with PyPDF2
python -c "from PyPDF2 import PdfReader; r = PdfReader('pdfs/test.pdf'); print(len(r.pages))"
```

**4. Memory Issues**
```bash
# Monitor memory usage
docker stats querymindingestion

# Reduce chunk size
export CHUNK_SIZE=500

# Process PDFs one at a time
# Modify script to process sequentially
```

**5. Slow Processing**
- Check Ollama response times
- Monitor MongoDB write performance
- Consider batch processing embeddings
- Use faster embedding models

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

### Performance Optimization

1. **Batch Processing**
   - Process multiple PDFs in parallel
   - Batch embedding generation

2. **Caching**
   - Cache processed PDFs
   - Skip already processed files

3. **Resource Allocation**
   - Increase container memory
   - Use faster CPU instances
   - Optimize Ollama model size

## Backup and Recovery

### MongoDB Backup

```bash
# Backup before major operations
mongodump --uri="<mongodb-uri>" --out=/backup/$(date +%Y%m%d)

# Restore if needed
mongorestore --uri="<mongodb-uri>" /backup/YYYYMMDD
```

### Application Backup

- Backup configuration files
- Backup processed PDF list
- Document environment variables

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip list --outdated
   pip install --upgrade -r requirements.txt
   ```

2. **Monitor Logs**
   - Review error logs daily
   - Check processing statistics

3. **Database Maintenance**
   - Regular backups
   - Cleanup duplicate documents
   - Optimize indexes

4. **Ollama Updates**
   ```bash
   docker pull ollama/ollama:latest
   docker-compose up -d ollama
   ```

### Update Deployment

```bash
# Pull latest code
git pull origin main

# Rebuild container
docker-compose up -d --build ingestion

# Verify
docker-compose logs -f ingestion
```

## Best Practices

1. **Idempotency**
   - Check if PDF already processed
   - Skip duplicate processing
   - Maintain processing log

2. **Error Handling**
   - Retry failed operations
   - Log all errors
   - Send alerts for critical failures

3. **Resource Management**
   - Set memory limits
   - Monitor CPU usage
   - Clean up temporary files

4. **Testing**
   - Test with sample PDFs
   - Verify embeddings quality
   - Check database integrity

## Support and Resources

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Logs**: `docker-compose logs -f`
- **Health Check**: Run health check script

---

**Last Updated**: 2024
**Version**: 1.0.0

