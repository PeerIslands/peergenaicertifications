# Semantic Threshold Guide for TextChunker

## Overview

The `semantic_threshold` parameter in `TextChunker` controls how aggressively text is split into chunks based on semantic similarity. This guide provides recommendations for choosing appropriate threshold values for different use cases.

## How Semantic Threshold Works

- **Range**: 0.0 to 1.0 (cosine similarity score)
- **Higher values (0.7-0.9)**: Less sensitive splitting, creates larger chunks
- **Lower values (0.1-0.3)**: More sensitive splitting, creates smaller chunks
- **Default**: 0.5 (balanced approach)

## Recommended Values

### For Academic/Research Papers (Your Use Case)
```python
chunker = TextChunker(semantic_threshold=0.35)
```
**Why**: Academic papers have complex structures with multiple concepts per section. A threshold of 0.35 provides good balance between granularity and context preservation.

### For Technical Documentation
```python
chunker = TextChunker(semantic_threshold=0.45)
```
**Why**: Technical docs need to maintain logical sections while allowing detailed chunking.

### For General Text Processing
```python
chunker = TextChunker(semantic_threshold=0.5)
```
**Why**: Default balanced approach suitable for most applications.

### For Large Document Summarization
```python
chunker = TextChunker(semantic_threshold=0.65)
```
**Why**: Creates larger chunks with more comprehensive context for summarization tasks.

### For Fine-grained Analysis
```python
chunker = TextChunker(semantic_threshold=0.25)
```
**Why**: Creates many small chunks for detailed analysis and precise retrieval.

## Implementation Changes Made

### 1. Simplified TextChunker
```python
def __init__(self):
    # Always uses config.semantic_chunking_threshold
    self.semantic_threshold = settings.semantic_chunking_threshold
```

### 2. Updated PDFIngestionTool
```python
def __init__(self):
    # TextChunker uses semantic_threshold from config
    self.text_chunker = TextChunker()
```

### 3. Updated Example Usage
```python
# Uses semantic_threshold from config
chunker = TextChunker()
```

### 4. Created Demonstration Script
Run `semantic_threshold_examples.py` to see how config affects chunking behavior.

## Testing Your Threshold

1. **Start with 0.35** for academic papers
2. **Test with sample documents** from your PDF collection
3. **Evaluate chunk quality**:
   - Are concepts properly grouped?
   - Are chunks appropriately sized?
   - Is context preserved?
4. **Adjust as needed**:
   - Lower threshold (0.25-0.3) for more granular chunks
   - Higher threshold (0.4-0.5) for larger chunks

## Environment Configuration

You can also set the threshold via environment variables:

```bash
# In your .env file
SEMANTIC_CHUNKING_THRESHOLD=0.35
```

## Best Practices

1. **Start conservative**: Begin with 0.35 for academic content
2. **Test thoroughly**: Use sample documents to validate chunk quality
3. **Consider downstream tasks**: Ensure chunks work well with your retrieval/QA system
4. **Monitor performance**: Balance chunk quality with processing speed
5. **Document your choice**: Record why you chose a specific threshold

## Troubleshooting

### Too Many Small Chunks
- **Problem**: Threshold too low (0.1-0.25)
- **Solution**: Increase to 0.35-0.45

### Too Few Large Chunks
- **Problem**: Threshold too high (0.7-0.9)
- **Solution**: Decrease to 0.4-0.5

### Inconsistent Chunking
- **Problem**: Threshold not optimized for content type
- **Solution**: Test with different values and choose based on content analysis

## Example Usage

```python
from pdf_ingestion_tool import PDFIngestionTool

# Uses config.semantic_chunking_threshold (0.35 for academic papers)
tool = PDFIngestionTool()

# To test different thresholds, modify config.py or use environment variables
# In .env file: SEMANTIC_CHUNKING_THRESHOLD=0.25
# Or modify config.py: settings.semantic_chunking_threshold = 0.25
```

## Conclusion

For your academic PDF ingestion project, **0.35** is the recommended starting point. This provides good balance between granularity and context preservation, which is ideal for research papers and technical documents.
