# Production Checklist

A comprehensive checklist for production deployment and operations.

## Pre-Deployment Checklist

### Security

- [ ] All environment variables stored securely (no hardcoded secrets)
- [ ] API keys rotated and stored in secrets manager
- [ ] HTTPS/TLS certificates configured
- [ ] CORS configured with specific origins (no wildcards)
- [ ] Security headers configured (CSP, HSTS, X-Frame-Options)
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] File upload restrictions in place
- [ ] MongoDB authentication enabled
- [ ] Database connection encrypted
- [ ] Dependency vulnerabilities scanned and resolved

### Configuration

- [ ] DEBUG=False in production
- [ ] Proper logging levels configured
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Environment-specific configurations verified
- [ ] Resource limits set (CPU, memory)
- [ ] Connection pool sizes optimized
- [ ] Timeouts configured appropriately
- [ ] CORS origins whitelisted
- [ ] File size limits configured

### Infrastructure

- [ ] Docker images built and tested
- [ ] Health checks configured
- [ ] Auto-restart policies enabled
- [ ] Load balancer configured
- [ ] Database backups automated
- [ ] Monitoring and alerting set up
- [ ] Log aggregation configured
- [ ] CDN configured for static assets (if applicable)
- [ ] DNS records configured
- [ ] SSL/TLS certificates valid

### Testing

- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] All E2E tests passing
- [ ] Load testing completed
- [ ] Security testing completed
- [ ] Performance benchmarks met
- [ ] Cross-browser testing done (frontend)
- [ ] Mobile responsiveness verified

### Documentation

- [ ] API documentation up to date
- [ ] Deployment guide completed
- [ ] Runbook created
- [ ] Disaster recovery plan documented
- [ ] Architecture diagrams updated
- [ ] Changelog maintained

## Deployment Process

### 1. Pre-Deployment

```bash
# Run all tests
cd backend && pytest
cd ../frontend && npm test

# Build production images
docker-compose -f docker-compose.yml build

# Run security scan
docker scan foundational-backend:latest
docker scan foundational-frontend:latest

# Test locally
docker-compose -f docker-compose.yml up
```

### 2. Deployment

```bash
# Tag release
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Deploy to production
docker-compose -f docker-compose.yml up -d

# Verify deployment
curl https://api.yourdomain.com/health
curl https://yourdomain.com
```

### 3. Post-Deployment

```bash
# Monitor logs
docker-compose logs -f

# Check service status
docker-compose ps

# Verify health checks
watch -n 5 'curl -s https://api.yourdomain.com/health | jq'

# Test critical user flows
npm run test:e2e:production
```

## Production Configuration

### Environment Variables

**Required:**
```bash
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb://...
DEBUG=False
```

**Recommended:**
```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Monitoring
SENTRY_DSN=https://...
APM_SERVER_URL=https://...

# Performance
WORKER_COUNT=4
MAX_CONNECTIONS=100
TIMEOUT=30

# Security
ALLOWED_ORIGINS=https://yourdomain.com
MAX_FILE_SIZE=10485760
RATE_LIMIT=100
```

### Docker Compose Production Override

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    restart: always
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    restart: always
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

  mongodb:
    restart: always
    command: mongod --auth
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

Use with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## Monitoring

### Key Metrics

**Application Metrics:**
- Request rate
- Response time (p50, p95, p99)
- Error rate
- Active sessions
- Queue depth

**System Metrics:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O
- Container restarts

**Database Metrics:**
- Connection count
- Query performance
- Replication lag
- Storage usage

### Health Checks

```bash
# Backend health
curl https://api.yourdomain.com/health
# Expected: {"status": "healthy", ...}

# Frontend health
curl https://yourdomain.com
# Expected: 200 OK

# Database health
docker-compose exec mongodb mongo --eval "db.adminCommand('ping')"
```

### Alerting Rules

Configure alerts for:
- [ ] Error rate > 1%
- [ ] Response time p95 > 2s
- [ ] CPU usage > 80%
- [ ] Memory usage > 85%
- [ ] Disk usage > 90%
- [ ] Service down
- [ ] Health check failures
- [ ] Certificate expiration < 30 days

## Backup Strategy

### Database Backups

**Automated Daily Backups:**
```bash
#!/bin/bash
# /usr/local/bin/backup-mongodb.sh

BACKUP_DIR="/backups/mongodb"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup
docker-compose exec -T mongodb mongodump \
  --archive=/data/backup/backup_$DATE.archive \
  --gzip

# Copy to backup location
docker cp foundational-mongodb:/data/backup/backup_$DATE.archive \
  $BACKUP_DIR/

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.archive \
  s3://your-bucket/backups/mongodb/

# Cleanup old backups
find $BACKUP_DIR -name "backup_*.archive" \
  -mtime +$RETENTION_DAYS -delete
```

**Cron Schedule:**
```bash
# Run daily at 2 AM
0 2 * * * /usr/local/bin/backup-mongodb.sh
```

### Restore Procedure

```bash
# Stop application
docker-compose stop backend

# Restore database
docker-compose exec -T mongodb mongorestore \
  --archive=/data/backup/backup_20231201_020000.archive \
  --gzip \
  --drop

# Restart application
docker-compose start backend
```

## Scaling Guidelines

### Horizontal Scaling

**When to scale:**
- CPU usage consistently > 70%
- Response times increasing
- Queue depth growing
- Concurrent users > capacity

**Backend scaling:**
```bash
docker-compose up -d --scale backend=3
```

**Frontend scaling:**
Use CDN for static assets and multiple replicas behind load balancer.

### Vertical Scaling

Increase resources in docker-compose:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

### Database Scaling

1. **Optimize queries and indexes**
2. **Enable caching**
3. **Use read replicas**
4. **Consider sharding** (if needed)

## Incident Response

### Runbook

**Service Down:**
1. Check service status: `docker-compose ps`
2. View logs: `docker-compose logs backend`
3. Check health endpoint
4. Restart if needed: `docker-compose restart backend`
5. Escalate if issue persists

**High Error Rate:**
1. Check recent deployments
2. Review error logs
3. Check external service status (OpenAI)
4. Rollback if necessary

**High Response Time:**
1. Check resource usage
2. Review database performance
3. Check for slow queries
4. Scale if needed

**Database Connection Issues:**
1. Check MongoDB status
2. Verify connection string
3. Check connection pool
4. Restart database if needed

### Rollback Procedure

```bash
# Tag current state
docker-compose down
git checkout <previous-version-tag>

# Rebuild and deploy
docker-compose build
docker-compose up -d

# Verify
curl https://api.yourdomain.com/health
```

## Maintenance Windows

### Regular Maintenance

**Weekly:**
- [ ] Review logs for errors
- [ ] Check disk usage
- [ ] Review monitoring dashboards
- [ ] Update dependencies (minor versions)

**Monthly:**
- [ ] Security updates
- [ ] Certificate renewal check
- [ ] Backup verification
- [ ] Performance review
- [ ] Cost optimization review

**Quarterly:**
- [ ] Disaster recovery drill
- [ ] Security audit
- [ ] Capacity planning review
- [ ] Documentation update

### Update Procedure

```bash
# 1. Notify users (if applicable)
# 2. Take backup
./backup-mongodb.sh

# 3. Pull latest changes
git pull origin main

# 4. Run tests
cd backend && pytest
cd ../frontend && npm test

# 5. Build new images
docker-compose build

# 6. Rolling update
docker-compose up -d --no-deps backend
docker-compose up -d --no-deps frontend

# 7. Verify deployment
curl https://api.yourdomain.com/health

# 8. Monitor for issues
docker-compose logs -f
```

## Performance Optimization

### Backend

- [ ] Enable response caching
- [ ] Optimize database queries
- [ ] Use connection pooling
- [ ] Enable compression (gzip)
- [ ] Implement request queuing
- [ ] Profile slow endpoints

### Frontend

- [ ] Enable code splitting
- [ ] Optimize bundle size
- [ ] Use lazy loading
- [ ] Enable asset compression
- [ ] Implement service worker
- [ ] Use CDN for static assets
- [ ] Optimize images

### Database

- [ ] Create appropriate indexes
- [ ] Optimize query patterns
- [ ] Enable query caching
- [ ] Monitor slow queries
- [ ] Regular maintenance (compact, reindex)

## Security Hardening

### Application

```python
# backend - Add security middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com"])
app.add_middleware(HTTPSRedirectMiddleware)
```

### Nginx Configuration

```nginx
# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Content-Security-Policy "default-src 'self'" always;

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20 nodelay;
```

### MongoDB

```bash
# Enable authentication
docker-compose exec mongodb mongo admin
> db.createUser({
    user: "admin",
    pwd: "strong-password",
    roles: ["root"]
  })

# Update connection string
MONGODB_URI=mongodb://admin:strong-password@mongodb:27017/chatpdf?authSource=admin
```

## Compliance

### GDPR (if applicable)

- [ ] Data processing agreement
- [ ] User consent mechanism
- [ ] Data export functionality
- [ ] Data deletion functionality
- [ ] Privacy policy
- [ ] Cookie consent

### Data Retention

- [ ] Define retention policies
- [ ] Implement automatic cleanup
- [ ] Document data handling
- [ ] Regular audits

## Cost Optimization

### Resource Optimization

- [ ] Right-size containers
- [ ] Use spot instances (if applicable)
- [ ] Implement auto-scaling
- [ ] Use reserved instances for stable load
- [ ] Monitor and optimize API usage (OpenAI)
- [ ] Implement caching to reduce API calls

### Monitoring Costs

- [ ] Track monthly costs
- [ ] Set up billing alerts
- [ ] Review usage patterns
- [ ] Optimize inefficient operations

---

**Last Updated:** [Date]  
**Reviewed By:** [Name]  
**Next Review:** [Date]

