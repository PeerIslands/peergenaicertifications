"""
AI-Powered Query Converter
Uses Azure OpenAI GPT to convert natural language queries to MongoDB operations
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
from openai import AzureOpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIQueryConverter:
    """Uses AI model (Azure OpenAI GPT) to convert natural language to MongoDB operations"""
    
    def __init__(self, endpoint: str, api_key: str, api_version: str, 
                 deployment_name: str, model: str = "gpt-4o"):
        """
        Initialize AI query converter with Azure OpenAI
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            api_version: API version (e.g., "2024-06-01")
            deployment_name: Deployment name for the model
            model: Model name (default: "gpt-4o")
        """
        # Ensure endpoint doesn't have trailing slash (Azure OpenAI SDK handles it)
        endpoint_clean = endpoint.rstrip('/')
        
        self.client = AzureOpenAI(
            azure_endpoint=endpoint_clean,
            api_key=api_key,
            api_version=api_version
        )
        self.deployment_name = deployment_name
        self.model = model
    
    def convert_to_mongodb_query(self, query: str, database: str = "PeerGenAI_practice_db",
                                 available_collections: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Convert natural language query to MongoDB operation using AI
        
        Args:
            query: Natural language query
            database: Database name
            available_collections: List of available collections (optional)
            
        Returns:
            Dictionary with operation, collection, and parameters
        """
        logger.info(f"Converting query with AI: {query}")
        
        # Build system prompt
        collections_info = ""
        if available_collections:
            collections_info = f"\nAvailable collections: {', '.join(available_collections)}"
        
        system_prompt = f"""You are a MongoDB query expert. Convert natural language queries to MongoDB operations.

Database: {database}
{collections_info}

Return a JSON object with this structure:
{{
    "operation": "find|update|insert|delete",
    "collection": "collection_name",
    "filters": {{}},  // MongoDB filter object (for find/update/delete)
    "document": {{}},  // Document to insert (for insert)
    "updates": {{}},   // Fields to update with $set (for update)
    "limit": 10        // Limit for find operations
}}

Examples:
- "find all users where age is greater than 25" → {{"operation": "find", "collection": "users", "filters": {{"age": {{"$gt": 25}}}}, "limit": 10}}
- "insert new user with name John and age 28" → {{"operation": "insert", "collection": "users", "document": {{"name": "John", "age": 28}}}}
- "update users set status to active where age is 30" → {{"operation": "update", "collection": "users", "filters": {{"age": 30}}, "updates": {{"status": "active"}}}}

Be precise with MongoDB query syntax. Use $gt, $lt, $gte, $lte for comparisons."""

        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,  # Use deployment name for Azure
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Convert this query: {query}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1  # Low temperature for consistent results
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"AI converted query to: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error converting query with AI: {e}")
            raise
    
    def get_available_collections(self, mcp_client) -> List[str]:
        """
        Get available collections from MongoDB via MCP
        
        Args:
            mcp_client: MCP client instance
            
        Returns:
            List of collection names
        """
        try:
            # Use MCP to list collections
            resources = mcp_client.list_resources()
            collections = []
            for resource in resources:
                if 'collection' in resource.get('uri', ''):
                    collections.append(resource['name'])
            return collections
        except:
            # Fallback to common collection names
            return ['users', 'products', 'orders', 'items', 'documents']


class HybridQueryConverter:
    """Hybrid converter: tries regex first, falls back to AI for complex queries"""
    
    def __init__(self, regex_converter, ai_converter, use_ai: bool = True):
        """
        Initialize hybrid converter
        
        Args:
            regex_converter: NLQueryConverter instance
            ai_converter: AIQueryConverter instance
            use_ai: Whether to use AI (True) or regex (False)
        """
        self.regex_converter = regex_converter
        self.ai_converter = ai_converter
        self.use_ai = use_ai
    
    def convert_to_mongodb_query(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Convert query using hybrid approach
        
        Args:
            query: Natural language query
            **kwargs: Additional arguments for AI converter
            
        Returns:
            MongoDB operation dictionary
        """
        if self.use_ai:
            # Use AI for all queries
            return self.ai_converter.convert_to_mongodb_query(query, **kwargs)
        else:
            # Try regex first, fall back to AI if it fails
            try:
                result = self.regex_converter.convert_to_mongodb_query(query)
                # If regex extracted empty document, use AI
                if result.get('operation') == 'insert' and not result.get('document'):
                    logger.info("Regex failed for insert, using AI")
                    return self.ai_converter.convert_to_mongodb_query(query, **kwargs)
                return result
            except:
                logger.info("Regex conversion failed, using AI")
                return self.ai_converter.convert_to_mongodb_query(query, **kwargs)

