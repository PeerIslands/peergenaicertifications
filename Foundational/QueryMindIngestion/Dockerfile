# Multi-stage Dockerfile for QueryMindIngestion
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/pdfs /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 ingestion && \
    chown -R ingestion:ingestion /app

# Switch to non-root user
USER ingestion

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "from mongodb_client import MongoDBClient; from embedding_generator import EmbeddingGenerator; m = MongoDBClient(); e = EmbeddingGenerator(); exit(0 if (m.test_connection() and e.test_connection()) else 1)" || exit 1

# Default command (can be overridden)
CMD ["python", "pdf_ingestion_tool.py"]

