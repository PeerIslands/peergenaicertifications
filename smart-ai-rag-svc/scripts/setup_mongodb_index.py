"""
Script to set up MongoDB Atlas Vector Search index.
Run this script after setting up your MongoDB Atlas cluster.

Note: This script provides instructions for manual index setup since
the vector store is now integrated directly with LangChain.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.config.settings import settings


def setup_vector_index():
    """Provide instructions for setting up the vector search index in MongoDB Atlas."""
    
    print("MongoDB Atlas Vector Search Index Setup Instructions")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print(f"Collection: {settings.mongodb_collection}")
    print("Index name: vector_index")
    print()
    
    print("MANUAL SETUP REQUIRED:")
    print("1. Log in to your MongoDB Atlas account")
    print("2. Navigate to your cluster")
    print("3. Go to the 'Search' tab")
    print("4. Click 'Create Search Index'")
    print("5. Choose 'Vector Search' as the index type")
    print("6. Use the following configuration:")
    print()
    
    index_config = {
        "fields": [
            {
                "numDimensions": 1536,
                "path": "embedding",
                "similarity": "cosine",
                "type": "vector"
            }
        ]
    }
    
    print("Index Configuration (JSON):")
    print("-" * 30)
    import json
    print(json.dumps(index_config, indent=2))
    print("-" * 30)
    print()
    
    print("7. Set the index name to: 'vector_index'")
    print(f"8. Select database: '{settings.mongodb_database}'")
    print(f"9. Select collection: '{settings.mongodb_collection}'")
    print("10. Click 'Create Search Index'")
    print()
    
    print("The vector search index will be ready in a few minutes.")
    print("You can then start using the RAG service!")


if __name__ == "__main__":
    setup_vector_index()
