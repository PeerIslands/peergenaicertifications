FROM python:3.11-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1

# Install runtime deps
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY src ./src

ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


