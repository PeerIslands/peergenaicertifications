"""
Prometheus metrics for the Smart AI RAG Service.
Tracks performance, usage, costs, and errors.
"""
from prometheus_client import Counter, Histogram, Gauge, Info
from typing import Optional
import time
from functools import wraps
from contextlib import contextmanager

# Application info
app_info = Info('smart_rag_app', 'Smart AI RAG Service application info')
app_info.info({
    'version': '2.0.0',
    'service': 'smart-ai-rag-service'
})

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)

# Document processing metrics
documents_processed_total = Counter(
    'documents_processed_total',
    'Total documents processed',
    ['framework', 'status']
)

document_processing_duration_seconds = Histogram(
    'document_processing_duration_seconds',
    'Document processing duration',
    ['framework'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

document_chunks_created_total = Counter(
    'document_chunks_created_total',
    'Total document chunks created',
    ['framework']
)

# Question answering metrics
questions_answered_total = Counter(
    'questions_answered_total',
    'Total questions answered',
    ['framework', 'status']
)

question_answering_duration_seconds = Histogram(
    'question_answering_duration_seconds',
    'Question answering duration',
    ['framework'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
)

# LLM metrics
llm_requests_total = Counter(
    'llm_requests_total',
    'Total LLM API requests',
    ['provider', 'model', 'status']
)

llm_request_duration_seconds = Histogram(
    'llm_request_duration_seconds',
    'LLM API request duration',
    ['provider', 'model'],
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0]
)

llm_tokens_used_total = Counter(
    'llm_tokens_used_total',
    'Total tokens used',
    ['provider', 'model', 'type']
)

# Vector store metrics
vector_store_operations_total = Counter(
    'vector_store_operations_total',
    'Total vector store operations',
    ['operation', 'status']
)

vector_store_operation_duration_seconds = Histogram(
    'vector_store_operation_duration_seconds',
    'Vector store operation duration',
    ['operation'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Evaluation metrics
evaluations_total = Counter(
    'evaluations_total',
    'Total RAG evaluations',
    ['status']
)

evaluation_scores = Histogram(
    'evaluation_scores',
    'RAG evaluation scores',
    ['metric'],
    buckets=[0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
)

# Cost tracking metrics
openai_cost_dollars_total = Counter(
    'openai_cost_dollars_total',
    'Total OpenAI API costs in dollars',
    ['model', 'operation']
)

# System metrics
active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

conversation_history_size = Gauge(
    'conversation_history_size',
    'Current conversation history size'
)

indexed_documents_total = Gauge(
    'indexed_documents_total',
    'Total indexed documents',
    ['framework']
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['type', 'component']
)


# Cost calculation helpers (OpenAI pricing as of 2024)
OPENAI_PRICING = {
    'gpt-3.5-turbo': {
        'prompt': 0.0005 / 1000,  # $0.0005 per 1K tokens
        'completion': 0.0015 / 1000  # $0.0015 per 1K tokens
    },
    'gpt-4': {
        'prompt': 0.03 / 1000,  # $0.03 per 1K tokens
        'completion': 0.06 / 1000  # $0.06 per 1K tokens
    },
    'text-embedding-ada-002': {
        'prompt': 0.0001 / 1000,  # $0.0001 per 1K tokens
        'completion': 0.0
    }
}


def track_llm_cost(model: str, prompt_tokens: int, completion_tokens: int, operation: str = 'generation'):
    """
    Track LLM API costs.
    
    Args:
        model: Model name
        prompt_tokens: Number of prompt tokens used
        completion_tokens: Number of completion tokens used
        operation: Operation type (generation, embedding)
    """
    pricing = OPENAI_PRICING.get(model, {'prompt': 0.0, 'completion': 0.0})
    
    prompt_cost = prompt_tokens * pricing['prompt']
    completion_cost = completion_tokens * pricing['completion']
    total_cost = prompt_cost + completion_cost
    
    openai_cost_dollars_total.labels(model=model, operation=operation).inc(total_cost)
    
    llm_tokens_used_total.labels(provider='openai', model=model, type='prompt').inc(prompt_tokens)
    llm_tokens_used_total.labels(provider='openai', model=model, type='completion').inc(completion_tokens)


@contextmanager
def track_request_duration(method: str, endpoint: str):
    """
    Context manager to track HTTP request duration.
    
    Args:
        method: HTTP method
        endpoint: Endpoint path
    """
    active_requests.inc()
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
        active_requests.dec()


@contextmanager
def track_operation_duration(operation_name: str, labels: Optional[dict] = None):
    """
    Generic context manager to track operation duration.
    
    Args:
        operation_name: Name of the operation
        labels: Optional labels for the metric
    """
    start_time = time.time()
    
    try:
        yield
    finally:
        duration = time.time() - start_time
        
        # You can extend this to track different operations
        if operation_name == 'document_processing':
            framework = labels.get('framework', 'unknown') if labels else 'unknown'
            document_processing_duration_seconds.labels(framework=framework).observe(duration)
        elif operation_name == 'question_answering':
            framework = labels.get('framework', 'unknown') if labels else 'unknown'
            question_answering_duration_seconds.labels(framework=framework).observe(duration)
        elif operation_name == 'llm_request':
            provider = labels.get('provider', 'unknown') if labels else 'unknown'
            model = labels.get('model', 'unknown') if labels else 'unknown'
            llm_request_duration_seconds.labels(provider=provider, model=model).observe(duration)


def track_document_processed(framework: str, status: str = 'success', chunks: int = 0):
    """
    Track document processing.
    
    Args:
        framework: Framework used (langchain, llamaindex)
        status: Processing status (success, error)
        chunks: Number of chunks created
    """
    documents_processed_total.labels(framework=framework, status=status).inc()
    
    if chunks > 0:
        document_chunks_created_total.labels(framework=framework).inc(chunks)


def track_question_answered(framework: str, status: str = 'success'):
    """
    Track question answering.
    
    Args:
        framework: Framework used (langchain, llamaindex)
        status: Status (success, error)
    """
    questions_answered_total.labels(framework=framework, status=status).inc()


def track_evaluation(scores: dict, status: str = 'success'):
    """
    Track RAG evaluation.
    
    Args:
        scores: Dictionary of evaluation scores
        status: Evaluation status
    """
    evaluations_total.labels(status=status).inc()
    
    for metric, score in scores.items():
        if isinstance(score, (int, float)):
            evaluation_scores.labels(metric=metric).observe(score)


def track_error(error_type: str, component: str):
    """
    Track errors.
    
    Args:
        error_type: Type of error
        component: Component where error occurred
    """
    errors_total.labels(type=error_type, component=component).inc()

