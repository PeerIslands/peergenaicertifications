# Deployment Guide

This guide covers deploying the Foundational application to production environments.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment Options](#cloud-deployment-options)
- [Environment Configuration](#environment-configuration)
- [Monitoring and Logging](#monitoring-and-logging)
- [Backup and Recovery](#backup-and-recovery)
- [Scaling](#scaling)

## Prerequisites

Before deploying, ensure you have:

1. **Docker & Docker Compose** (v20.10+ and v2.0+ respectively)
2. **OpenAI API Key** from [OpenAI Platform](https://platform.openai.com/)
3. **Domain name** (optional, for production)
4. **SSL certificates** (recommended for production)
5. **MongoDB instance** (included in Docker Compose or external)

## Docker Deployment

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd peergenaicertifications/Foundational
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   nano .env
   ```

3. **Build and start services**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   docker-compose ps
   curl http://localhost:8000/health
   curl http://localhost:3000
   ```

### Production Deployment

For production, use optimized configurations:

```bash
# Build production images
docker-compose -f docker-compose.yml build

# Start with production settings
docker-compose -f docker-compose.yml up -d

# View logs
docker-compose logs -f

# Monitor services
docker-compose ps
```

### Development Deployment

For development with hot-reload:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up

# Run with rebuild
docker-compose -f docker-compose.dev.yml up --build
```

## Cloud Deployment Options

### AWS Deployment

#### Option 1: ECS with Fargate

1. **Push images to ECR**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com
   
   docker tag foundational-backend:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/foundational-backend:latest
   docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/foundational-backend:latest
   
   docker tag foundational-frontend:latest <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/foundational-frontend:latest
   docker push <aws-account-id>.dkr.ecr.us-east-1.amazonaws.com/foundational-frontend:latest
   ```

2. **Create ECS Task Definitions**
   - Use the provided task definitions in `deployment/aws/`
   - Configure environment variables in task definition

3. **Deploy services**
   - Create ECS Cluster
   - Create services for backend and frontend
   - Configure Application Load Balancer
   - Set up Auto Scaling

#### Option 2: EC2 with Docker Compose

1. **Launch EC2 instance**
   - Amazon Linux 2 or Ubuntu 22.04
   - t3.medium or larger
   - Security groups: 80, 443, 8000 (backend)

2. **Install Docker**
   ```bash
   # For Amazon Linux 2
   sudo yum update -y
   sudo yum install docker -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -a -G docker ec2-user
   
   # Install Docker Compose
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Deploy application**
   ```bash
   git clone <repository-url>
   cd peergenaicertifications/Foundational
   
   # Configure environment
   nano .env
   
   # Start services
   docker-compose up -d
   ```

### Google Cloud Platform (GCP)

#### Cloud Run Deployment

1. **Build and push to GCR**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/foundational-backend ./backend
   gcloud builds submit --tag gcr.io/PROJECT_ID/foundational-frontend ./frontend
   ```

2. **Deploy to Cloud Run**
   ```bash
   # Deploy backend
   gcloud run deploy foundational-backend \
     --image gcr.io/PROJECT_ID/foundational-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
   
   # Deploy frontend
   gcloud run deploy foundational-frontend \
     --image gcr.io/PROJECT_ID/foundational-frontend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Azure Deployment

#### Azure Container Instances

1. **Create resource group**
   ```bash
   az group create --name foundational-rg --location eastus
   ```

2. **Deploy containers**
   ```bash
   az container create \
     --resource-group foundational-rg \
     --name foundational-backend \
     --image <registry>/foundational-backend:latest \
     --dns-name-label foundational-backend \
     --ports 8000 \
     --environment-variables OPENAI_API_KEY=$OPENAI_API_KEY
   ```

### DigitalOcean App Platform

1. **Create app via doctl**
   ```bash
   doctl apps create --spec deployment/digitalocean/app.yaml
   ```

2. **Or use the web interface**
   - Connect GitHub repository
   - Configure build settings
   - Set environment variables
   - Deploy

## Environment Configuration

### Required Environment Variables

#### Backend (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Configuration
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# File Configuration
MAX_FILE_SIZE=10485760  # 10MB

# Database Configuration
MONGODB_URI=mongodb://mongodb:27017/chatpdf
```

#### Frontend
```bash
VITE_API_URL=https://api.yourdomain.com
```

### Security Best Practices

1. **Never commit .env files**
2. **Use secrets management**
   - AWS Secrets Manager
   - Google Cloud Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

3. **Enable HTTPS/TLS**
   - Use Let's Encrypt for free certificates
   - Configure reverse proxy (Nginx/Traefik)

4. **Configure CORS properly**
   - Restrict origins to your domain
   - Don't use wildcard (*) in production

## Monitoring and Logging

### Docker Compose Logging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Production Monitoring Tools

1. **Application Performance Monitoring (APM)**
   - New Relic
   - Datadog
   - Dynatrace
   - Elastic APM

2. **Log Aggregation**
   - ELK Stack (Elasticsearch, Logstash, Kibana)
   - Splunk
   - CloudWatch (AWS)
   - Stackdriver (GCP)

3. **Health Checks**
   ```bash
   # Backend health
   curl https://api.yourdomain.com/health
   
   # Frontend health
   curl https://yourdomain.com
   ```

### Metrics to Monitor

- **API Response Time**
- **Error Rate**
- **Request Rate**
- **Database Connection Pool**
- **Memory Usage**
- **CPU Usage**
- **Disk I/O**
- **OpenAI API Quota Usage**

## Backup and Recovery

### Database Backup (MongoDB)

```bash
# Create backup
docker-compose exec mongodb mongodump --out /data/backup

# Copy backup to host
docker cp foundational-mongodb:/data/backup ./mongodb-backup-$(date +%Y%m%d)

# Automated backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
docker-compose exec -T mongodb mongodump --archive > $BACKUP_DIR/backup_$DATE.archive
find $BACKUP_DIR -name "backup_*.archive" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab
# 0 2 * * * /path/to/backup.sh
```

### Restore Database

```bash
# Restore from backup
docker-compose exec -T mongodb mongorestore --archive < ./mongodb-backup-20231201/backup.archive
```

### Disaster Recovery Plan

1. **Regular Backups**: Daily automated backups
2. **Off-site Storage**: Store backups in S3, GCS, or Azure Blob
3. **Testing**: Regularly test restore procedures
4. **Documentation**: Maintain recovery procedures
5. **Multi-region**: Consider multi-region deployment for critical applications

## Scaling

### Horizontal Scaling

#### Backend Scaling

1. **Docker Compose scaling**
   ```bash
   docker-compose up -d --scale backend=3
   ```

2. **Kubernetes deployment**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: foundational-backend
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: backend
     template:
       metadata:
         labels:
           app: backend
       spec:
         containers:
         - name: backend
           image: foundational-backend:latest
           ports:
           - containerPort: 8000
   ```

#### Load Balancing

Use Nginx as a reverse proxy and load balancer:

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Vertical Scaling

Adjust Docker Compose resource limits:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### Database Scaling

1. **MongoDB Replica Set**
2. **Sharding for large datasets**
3. **Read replicas for read-heavy workloads**
4. **Connection pooling optimization**

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://frontend:80;
    }
}
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker-compose logs <service-name>
   docker-compose ps
   ```

2. **Database connection issues**
   ```bash
   docker-compose exec backend ping mongodb
   docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
   ```

3. **Out of memory**
   ```bash
   docker stats
   # Increase memory limits in docker-compose.yml
   ```

4. **Port conflicts**
   ```bash
   sudo lsof -i :8000
   # Change ports in docker-compose.yml
   ```

## Maintenance

### Updates and Patches

```bash
# Pull latest changes
git pull origin main

# Rebuild images
docker-compose build

# Restart services
docker-compose up -d

# Clean up old images
docker image prune -a
```

### Rolling Updates

```bash
# Update one service at a time
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

## Support

For issues and questions:
- Check logs: `docker-compose logs -f`
- Review health endpoints
- Check GitHub Issues
- Consult API documentation at `/docs`

---

**Note**: Always test deployment procedures in a staging environment before deploying to production.

