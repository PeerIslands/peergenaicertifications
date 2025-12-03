# ============================================================================
# Production Dockerfile for Smart AI RAG Service
# ============================================================================
# Multi-stage build for optimized image size and security
# Usage:
#   docker build -t rag-service:latest .
#   docker run -p 8000:8000 --env-file .env rag-service:latest
# ============================================================================

# Stage 1: Builder - Install dependencies
FROM python:3.12-slim as builder

LABEL maintainer="Smart AI RAG Service"
LABEL description="RAG Service with LangChain and LlamaIndex - Python 3.12"

# Set working directory
WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in user space
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt && \
    pip install --user --no-cache-dir pytest pytest-asyncio pytest-mock

# ============================================================================
# Stage 2: Runtime - Minimal production image
# ============================================================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r appuser && \
    useradd -r -g appuser -u 1000 -m -s /bin/bash appuser && \
    chown -R appuser:appuser /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . /app

# Set environment variables
ENV PATH=/home/appuser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Create necessary directories
RUN mkdir -p /app/uploads /app/logs && \
    chown -R appuser:appuser /app/uploads /app/logs

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

