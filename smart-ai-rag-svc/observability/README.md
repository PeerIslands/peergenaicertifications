# Observability for Smart AI RAG Service

This directory contains the complete observability stack for monitoring, tracing, and analyzing the Smart AI RAG Service.

## Table of Contents

- [Overview](#overview)
- [Components](#components)
- [Quick Start](#quick-start)
- [Metrics](#metrics)
- [Distributed Tracing](#distributed-tracing)
- [Logging](#logging)
- [Alerting](#alerting)
- [Dashboards](#dashboards)
- [Cost Tracking](#cost-tracking)

## Overview

The Smart AI RAG Service includes comprehensive observability features:

- **Structured Logging**: JSON-formatted logs with correlation IDs
- **Metrics (Prometheus)**: Performance, usage, and cost metrics
- **Distributed Tracing (OpenTelemetry/Jaeger)**: End-to-end request tracing
- **Dashboards (Grafana)**: Visual monitoring and analytics
- **Alerting**: Automated alerts for critical issues

## Components

### 1. Prometheus
- **Purpose**: Metrics collection and storage
- **Port**: 9090
- **Access**: http://localhost:9090

### 2. Grafana
- **Purpose**: Metrics visualization and dashboards
- **Port**: 3000
- **Access**: http://localhost:3000
- **Default Credentials**: admin/admin (change in production!)

### 3. Jaeger
- **Purpose**: Distributed tracing and trace visualization
- **Port**: 16686 (UI), 4317 (OTLP gRPC)
- **Access**: http://localhost:16686

## Quick Start

### Start Observability Stack

```bash
# 1. Make sure the main RAG service network exists
cd /path/to/smart-ai-rag-svc
docker network create rag-network || true

# 2. Start observability services
cd observability
docker-compose -f docker-compose-observability.yml up -d

# 3. Verify services are running
docker-compose -f docker-compose-observability.yml ps
```

### Start RAG Service with Observability

```bash
# Set environment variables for observability
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export OTLP_ENDPOINT=http://jaeger:4317

# Start the RAG service
cd ..
docker-compose up -d
```

### Access Dashboards

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Jaeger**: http://localhost:16686
- **RAG API Metrics**: http://localhost:8000/metrics
- **RAG API Swagger**: http://localhost:8000/docs

## Metrics

### Available Metrics

#### HTTP Metrics
- `http_requests_total` - Total HTTP requests (by method, endpoint, status)
- `http_request_duration_seconds` - HTTP request latency histogram
- `active_requests` - Current number of active requests

#### Document Processing
- `documents_processed_total` - Total documents processed (by framework, status)
- `document_processing_duration_seconds` - Document processing time
- `document_chunks_created_total` - Total chunks created

#### Question Answering
- `questions_answered_total` - Total questions answered (by framework, status)
- `question_answering_duration_seconds` - QA response time

#### LLM Metrics
- `llm_requests_total` - Total LLM API requests (by provider, model, status)
- `llm_request_duration_seconds` - LLM request latency
- `llm_tokens_used_total` - Total tokens consumed (prompt/completion)

#### Cost Tracking
- `openai_cost_dollars_total` - Cumulative OpenAI costs in USD

#### Evaluation
- `evaluations_total` - Total RAG evaluations
- `evaluation_scores` - Evaluation score distribution

#### Vector Store
- `vector_store_operations_total` - Vector store operations
- `vector_store_operation_duration_seconds` - Vector operation latency

#### Errors
- `errors_total` - Total errors (by type, component)

### Query Examples

```promql
# Request rate per second
rate(http_requests_total[5m])

# P95 latency by endpoint
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(errors_total[5m])

# OpenAI cost per hour
rate(openai_cost_dollars_total[1h])

# Success rate for questions
rate(questions_answered_total{status="success"}[5m]) / rate(questions_answered_total[5m])
```

## Distributed Tracing

### Enable Tracing

Tracing is automatically enabled when the `OTLP_ENDPOINT` environment variable is set:

```bash
export OTLP_ENDPOINT=http://jaeger:4317
```

### Trace Components

The service automatically traces:
- HTTP requests (via FastAPI instrumentation)
- Database operations (via PyMongo instrumentation)
- HTTP client calls (via HTTPX instrumentation)
- Custom operations (via `@trace_function` decorator)

### Custom Tracing

```python
from src.utils.tracing import trace_function, TracingContext, add_span_attributes

# Decorator approach
@trace_function(span_name="my_function", attributes={"key": "value"})
def my_function():
    pass

# Context manager approach
with TracingContext("my_operation", {"operation_type": "batch"}):
    # Your code here
    add_span_attributes(processed=100, status="success")
```

## Logging

### Structured Logging

The service uses structured JSON logging in production:

```json
{
  "timestamp": "2024-12-04T10:30:00.000Z",
  "level": "INFO",
  "logger": "src.services.enhanced_rag_service",
  "message": "Document processed successfully",
  "module": "enhanced_rag_service",
  "function": "load_and_index_documents",
  "line": 123,
  "request_id": "uuid-1234",
  "framework": "llamaindex",
  "chunks": 42
}
```

### Log Levels

- **DEBUG**: Detailed debugging information
- **INFO**: General informational messages
- **WARNING**: Warning messages (non-critical issues)
- **ERROR**: Error messages (failures)
- **CRITICAL**: Critical issues requiring immediate attention

### Configure Logging

```bash
# Set log level
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Set environment (affects log format)
export ENVIRONMENT=production  # production=JSON, development=text
```

### Custom Logging

```python
from src.utils.logging_config import get_logger

logger = get_logger(__name__)

# Add structured fields
logger.info("Processing document", 
            document_id="doc-123",
            pages=10,
            size_mb=5.2)

# Error with context
try:
    process_document()
except Exception as e:
    logger.error("Document processing failed",
                 error=str(e),
                 document_id="doc-123")
```

## Alerting

### Alert Rules

See `alerts.yml` for configured alert rules:

1. **HighErrorRate**: Error rate > 0.1/sec for 5 minutes
2. **HighAPILatency**: P95 latency > 10 seconds
3. **SlowDocumentProcessing**: P95 processing > 120 seconds
4. **HighOpenAICosts**: Costs > $10/hour
5. **ServiceDown**: Service unavailable for > 1 minute
6. **LowSuccessRate**: Success rate < 90%
7. **HighLLMFailures**: LLM failures > 0.05/sec
8. **LowEvaluationScores**: Evaluation scores < 0.7

### Configure Alertmanager (Optional)

```yaml
# alertmanager.yml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@example.com'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'password'

route:
  receiver: 'email'
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10m
  repeat_interval: 12h

receivers:
  - name: 'email'
    email_configs:
      - to: 'team@example.com'
```

## Dashboards

### Grafana Dashboard

The included Grafana dashboard (`grafana-dashboard.json`) provides:

1. **Request Rate** - Requests per second by endpoint
2. **Request Latency** - P95 latency by endpoint
3. **Active Requests** - Current concurrent requests
4. **Documents Processed** - Total documents indexed
5. **Questions Answered** - Total questions answered
6. **Processing Duration** - Document processing time
7. **QA Duration** - Question answering time
8. **Token Usage** - LLM token consumption
9. **OpenAI Costs** - Cumulative API costs
10. **Error Rate** - Errors per second
11. **Evaluation Scores** - RAG quality metrics
12. **Vector Store Ops** - Database operations
13. **LLM Latency** - LLM request duration
14. **HTTP Status Codes** - Request status distribution

### Import Dashboard

1. Open Grafana: http://localhost:3000
2. Login (admin/admin)
3. Navigate to Dashboards > Import
4. Upload `grafana-dashboard.json`
5. Select Prometheus as the data source

## Cost Tracking

### OpenAI Cost Monitoring

The service automatically tracks OpenAI API costs based on token usage:

```promql
# Total cost to date
openai_cost_dollars_total

# Cost per hour (last 1h)
rate(openai_cost_dollars_total[1h])

# Cost by model
sum by (model) (openai_cost_dollars_total)
```

### Pricing (Built-in)

| Model | Prompt | Completion |
|-------|--------|------------|
| gpt-3.5-turbo | $0.0005/1K | $0.0015/1K |
| gpt-4 | $0.03/1K | $0.06/1K |
| text-embedding-ada-002 | $0.0001/1K | N/A |

## Best Practices

### Production Deployment

1. **Enable JSON Logging**
   ```bash
   export ENVIRONMENT=production
   ```

2. **Configure OTLP Endpoint**
   ```bash
   export OTLP_ENDPOINT=http://your-jaeger:4317
   ```

3. **Set Appropriate Log Level**
   ```bash
   export LOG_LEVEL=INFO  # or WARNING
   ```

4. **Secure Grafana**
   - Change default admin password
   - Enable authentication
   - Use HTTPS

5. **Configure Alerts**
   - Set up Alertmanager
   - Configure notification channels
   - Test alert rules

6. **Monitor Costs**
   - Set up cost alerts
   - Review daily/weekly cost reports
   - Optimize token usage

### Development

For development, use text-based logging:

```bash
export ENVIRONMENT=development
export LOG_LEVEL=DEBUG
```

## Troubleshooting

### No Metrics Appearing

1. Check metrics endpoint: http://localhost:8000/metrics
2. Verify Prometheus is scraping: http://localhost:9090/targets
3. Check Prometheus logs: `docker logs smart-rag-prometheus`

### No Traces in Jaeger

1. Verify OTLP endpoint is set: `echo $OTLP_ENDPOINT`
2. Check Jaeger is running: http://localhost:16686
3. Check for trace data in Jaeger UI
4. Verify service name in traces

### High Memory Usage

1. Check Prometheus retention settings
2. Reduce scrape interval
3. Configure metric cardinality limits

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)

