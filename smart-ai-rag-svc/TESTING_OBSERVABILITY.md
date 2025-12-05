# Testing Observability

Complete guide to test all observability features of the Smart AI RAG Service.

## Overview

This guide provides comprehensive manual testing procedures for all observability features:
- Metrics collection and exposure
- Request correlation IDs
- Security headers
- Structured logging
- Prometheus/Grafana/Jaeger integration
- Document processing metrics
- Question answering metrics
- Cost tracking
- Error monitoring

## Testing Guide

### Prerequisites

1. **Service is running:**
   ```bash
   cd smart-ai-rag-svc
   source venv/bin/activate
   uvicorn main:app --reload
   ```

2. **Verify service is up:**
   ```bash
   curl http://localhost:8000/health
   ```

---

## Test 1: Metrics Endpoint

### Check metrics are exposed

```bash
# View all metrics
curl http://localhost:8000/metrics/

# Count total metrics
curl -s http://localhost:8000/metrics/ | grep -E "^[a-z_]+" | wc -l

# Check for specific metrics
curl -s http://localhost:8000/metrics/ | grep "smart_rag_app_info"
curl -s http://localhost:8000/metrics/ | grep "http_requests_total"
curl -s http://localhost:8000/metrics/ | grep "active_requests"
```

**Expected Output:**
```
# HELP smart_rag_app_info Smart AI RAG Service application info
# TYPE smart_rag_app_info gauge
smart_rag_app_info{service="smart-ai-rag-service",version="2.0.0"} 1.0

# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/health",method="GET",status="200"} 5.0
```

---

## Test 2: Generate Sample Traffic

### Create metrics data

```bash
# Make some requests to generate metrics
for i in {1..10}; do
  curl -s http://localhost:8000/health > /dev/null
  echo "Request $i sent"
done

# Check updated metrics
curl -s http://localhost:8000/metrics/ | grep "http_requests_total"
```

### Test different endpoints

```bash
# Health checks
curl http://localhost:8000/health

# Service stats
curl http://localhost:8000/stats

# API documentation
curl http://localhost:8000/docs
```

---

## Test 3: Request Correlation IDs

### Verify request tracking

```bash
# Make request and capture headers
curl -v http://localhost:8000/health 2>&1 | grep -i "x-request-id"
```

**Expected Output:**
```
< x-request-id: c557f5a0-5e7e-400d-b13d-a62c9849bae7
```

### Check logs for correlation ID

Look for the request ID in your server logs (in the terminal where uvicorn is running).

---

## Test 4: Security Headers

### Verify security headers are present

```bash
curl -I http://localhost:8000/health
```

**Expected Headers:**
```
x-content-type-options: nosniff
x-frame-options: DENY
x-xss-protection: 1; mode=block
strict-transport-security: max-age=31536000; includeSubDomains
```

---

## Test 5: Structured Logging

### Development Mode (Text Logs)

**Default behavior** - logs appear as text in the terminal:

```
INFO:     127.0.0.1:52345 - "GET /health HTTP/1.1" 200 OK
```

### Production Mode (JSON Logs)

```bash
# Start with production environment
export ENVIRONMENT=production
export LOG_LEVEL=INFO
uvicorn main:app --reload
```

**Expected Output:**
```json
{
  "timestamp": "2024-12-04T10:30:00.000Z",
  "level": "INFO",
  "message": "GET /health - 200",
  "request_id": "uuid-1234",
  "method": "GET",
  "path": "/health",
  "status_code": 200,
  "duration_seconds": 0.003
}
```

---

## Test 6: Full Observability Stack

### Start Prometheus, Grafana, and Jaeger

```bash
# Create network
docker network create rag-network || true

# Start observability stack
cd observability
docker-compose -f docker-compose-observability.yml up -d

# Verify services are running
docker-compose -f docker-compose-observability.yml ps
```

### Test Prometheus

1. **Access Prometheus:**
   ```bash
   open http://localhost:9090
   ```

2. **Check targets:**
   - Go to Status > Targets
   - Should see `smart-rag-service` endpoint

3. **Run queries:**
   ```promql
   # Request rate
   rate(http_requests_total[5m])
   
   # Active requests
   active_requests
   
   # P95 latency
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

### Test Grafana

1. **Access Grafana:**
   ```bash
   open http://localhost:3000
   ```

2. **Login:** admin/admin

3. **Import dashboard:**
   - Go to Dashboards > Import
   - Upload `observability/grafana-dashboard.json`
   - Select Prometheus as data source

4. **View dashboard:**
   - Should see 14 panels with metrics
   - Request rate, latency, costs, errors, etc.

### Test Jaeger

1. **Access Jaeger:**
   ```bash
   open http://localhost:16686
   ```

2. **Enable tracing:**
   ```bash
   export OTLP_ENDPOINT=http://jaeger:4317
   # Restart service
   ```

3. **Generate traffic:**
   ```bash
   curl http://localhost:8000/health
   curl http://localhost:8000/stats
   ```

4. **View traces:**
   - In Jaeger UI, select "smart-ai-rag-service"
   - Click "Find Traces"
   - Should see traces for your requests

---

## Test 7: Document Processing Metrics

### Upload a document and track metrics

```bash
# Upload a test document
curl -X POST "http://localhost:8000/documents/upload-file?use_llamaindex=true" \
  -F "file=@test_document.pdf"

# Check document processing metrics
curl -s http://localhost:8000/metrics/ | grep "documents_processed_total"
curl -s http://localhost:8000/metrics/ | grep "document_processing_duration_seconds"
curl -s http://localhost:8000/metrics/ | grep "document_chunks_created_total"
```

**Expected Metrics:**
```
documents_processed_total{framework="llamaindex",status="success"} 1.0
document_chunks_created_total{framework="llamaindex"} 42.0
```

---

## Test 8: Question Answering Metrics

### Ask questions and track metrics

```bash
# Ask a question
curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this about?", "k": 5}'

# Check QA metrics
curl -s http://localhost:8000/metrics/ | grep "questions_answered_total"
curl -s http://localhost:8000/metrics/ | grep "question_answering_duration_seconds"
```

**Expected Metrics:**
```
questions_answered_total{framework="llamaindex",status="success"} 1.0
question_answering_duration_seconds_count{framework="llamaindex"} 1.0
```

---

## Test 9: Cost Tracking

### Verify OpenAI cost tracking

```bash
# Make requests that use OpenAI API
curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "Summarize this document", "k": 5}'

# Check cost metrics
curl -s http://localhost:8000/metrics/ | grep "openai_cost_dollars_total"
curl -s http://localhost:8000/metrics/ | grep "llm_tokens_used_total"
```

**Expected Metrics:**
```
openai_cost_dollars_total{model="gpt-3.5-turbo",operation="generation"} 0.0015
llm_tokens_used_total{model="gpt-3.5-turbo",provider="openai",type="prompt"} 100.0
llm_tokens_used_total{model="gpt-3.5-turbo",provider="openai",type="completion"} 50.0
```

---

## Test 10: Error Tracking

### Generate errors and verify tracking

```bash
# Try to upload an invalid file
curl -X POST "http://localhost:8000/documents/upload-file" \
  -F "file=@nonexistent.pdf"

# Check error metrics
curl -s http://localhost:8000/metrics/ | grep "errors_total"
```

**Expected Metrics:**
```
errors_total{component="api",type="FileNotFoundError"} 1.0
```

---

## Test 11: Alert Rules

### Test Prometheus alerts

```bash
# Check alerts in Prometheus
open http://localhost:9090/alerts

# Trigger alert by generating errors
for i in {1..20}; do
  curl -X POST "http://localhost:8000/invalid-endpoint" 2>/dev/null
done

# Check if HighErrorRate alert fires
```

---

## Test 12: Load Testing

### Stress test with multiple concurrent requests

```bash
# Install Apache Bench (if not installed)
# macOS: brew install httpd
# Ubuntu: sudo apt-get install apache2-utils

# Run load test
ab -n 100 -c 10 http://localhost:8000/health

# Check metrics after load test
curl -s http://localhost:8000/metrics/ | grep "http_request_duration_seconds"
```

### Using Python for load testing

```python
# load_test.py
import requests
import concurrent.futures
import time

BASE_URL = "http://localhost:8000"

def make_request(i):
    try:
        response = requests.get(f"{BASE_URL}/health")
        return response.status_code
    except Exception as e:
        return str(e)

# Run 100 concurrent requests
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    futures = [executor.submit(make_request, i) for i in range(100)]
    results = [f.result() for f in concurrent.futures.as_completed(futures)]

print(f"Completed {len(results)} requests")
print(f"Success: {results.count(200)}")
```

---

## Verification Checklist

Use this checklist to verify all observability features:

- [ ] Metrics endpoint accessible (`/metrics/`)
- [ ] App info metric present (`smart_rag_app_info`)
- [ ] HTTP metrics tracked (`http_requests_total`)
- [ ] Request correlation IDs generated (`x-request-id` header)
- [ ] Security headers present (XSS, CSRF, Frame Options)
- [ ] Structured logging works (check terminal output)
- [ ] Document processing metrics tracked
- [ ] Question answering metrics tracked
- [ ] LLM token usage tracked
- [ ] Cost metrics calculated (`openai_cost_dollars_total`)
- [ ] Error metrics tracked
- [ ] Prometheus can scrape metrics (if stack running)
- [ ] Grafana dashboard displays data (if stack running)
- [ ] Jaeger shows traces (if tracing enabled)

---

## Troubleshooting

### Metrics not appearing

```bash
# Check if service is running
curl http://localhost:8000/health

# Check metrics endpoint (note the trailing slash)
curl http://localhost:8000/metrics/

# Restart service
lsof -ti:8000 | xargs kill -9
uvicorn main:app --reload
```

### Prometheus not scraping

```bash
# Check Prometheus targets
open http://localhost:9090/targets

# Check if service is accessible from Prometheus container
docker exec smart-rag-prometheus wget -O- http://rag-api:8000/metrics/
```

### No traces in Jaeger

```bash
# Verify OTLP endpoint is set
echo $OTLP_ENDPOINT  # Should show: http://jaeger:4317

# Check Jaeger is running
curl http://localhost:16686

# Restart service with tracing enabled
export OTLP_ENDPOINT=http://jaeger:4317
uvicorn main:app --reload
```

---

## Next Steps

1. **Integrate with CI/CD:**
   - Add `test_observability.sh` to your CI pipeline
   - Set up automated alerts

2. **Custom Dashboards:**
   - Create business-specific dashboards in Grafana
   - Add custom metrics for your use cases

3. **Production Deployment:**
   - Enable JSON logging (`ENVIRONMENT=production`)
   - Set up log aggregation (ELK, Loki)
   - Configure Alertmanager for notifications

4. **Monitor Costs:**
   - Set up daily cost reports
   - Create budget alerts
   - Optimize token usage

---

---

## Summary Checklist

Use this checklist to verify you've tested all observability features:

### Core Features
- [ ] Service health check works
- [ ] Metrics endpoint accessible at `/metrics/`
- [ ] Request correlation IDs generated
- [ ] Security headers present (4 headers)
- [ ] Structured logging active

### Metrics
- [ ] `smart_rag_app_info` present
- [ ] `http_requests_total` tracked
- [ ] `http_request_duration_seconds` recorded
- [ ] `active_requests` gauge working
- [ ] Document processing metrics
- [ ] Question answering metrics
- [ ] LLM token usage metrics
- [ ] Cost tracking metrics
- [ ] Error tracking metrics

### Optional Stack
- [ ] Prometheus running and scraping
- [ ] Grafana dashboard imported
- [ ] Jaeger showing traces
- [ ] Alert rules configured

### Production Readiness
- [ ] JSON logging tested (ENVIRONMENT=production)
- [ ] OpenTelemetry tracing enabled (OTLP_ENDPOINT set)
- [ ] Load testing performed
- [ ] All 12 test scenarios completed

---

## Resources

- **Observability Guide:** [observability/README.md](observability/README.md)
- **Main README:** [README.md](README.md)
- **Prometheus Docs:** https://prometheus.io/docs/
- **Grafana Docs:** https://grafana.com/docs/
- **Jaeger Docs:** https://www.jaegertracing.io/docs/
- **OpenTelemetry Python:** https://opentelemetry.io/docs/instrumentation/python/

---

## Quick Reference Commands

### Essential Commands

```bash
# View metrics
curl http://localhost:8000/metrics/

# Check service health
curl http://localhost:8000/health

# Count metrics
curl -s http://localhost:8000/metrics/ | grep -E "^[a-z_]+" | wc -l

# Generate traffic for testing
for i in {1..10}; do curl -s http://localhost:8000/health > /dev/null; done

# View updated request count
curl -s http://localhost:8000/metrics/ | grep "http_requests_total"
```

### Observability Stack Commands

```bash
# Start full stack
cd observability
docker-compose -f docker-compose-observability.yml up -d

# Check stack status
docker-compose -f docker-compose-observability.yml ps

# View logs
docker-compose -f docker-compose-observability.yml logs -f

# Stop stack
docker-compose -f docker-compose-observability.yml down
```

### Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| RAG API Docs | http://localhost:8000/docs | - |
| Metrics | http://localhost:8000/metrics/ | - |
| Health | http://localhost:8000/health | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Jaeger | http://localhost:16686 | - |

---

**Last Updated:** December 2024  
**Status:** Production-Ready Testing Guide

