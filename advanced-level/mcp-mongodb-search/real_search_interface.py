"""
Real Search Interface with AI and MCP Integration
Uses Azure OpenAI AI model to understand queries and MCP client to execute operations
"""

from typing import Dict, List, Any, Optional
import logging
import os
from real_mcp_client import RealMongoMCPClient
from ai_query_converter import AIQueryConverter, HybridQueryConverter
from nl_query_converter import NLQueryConverter
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealSearchInterface:
    """Search interface that uses Azure OpenAI AI model and real MCP client"""
    
    def __init__(self, mcp_client: RealMongoMCPClient, 
                 azure_endpoint: Optional[str] = None,
                 azure_api_key: Optional[str] = None,
                 azure_api_version: Optional[str] = None,
                 azure_deployment_name: Optional[str] = None,
                 azure_model: Optional[str] = None,
                 use_ai: bool = True):
        """
        Initialize search interface with Azure OpenAI
        
        Args:
            mcp_client: Real MongoDB MCP client connector
            azure_endpoint: Azure OpenAI endpoint (or from Config)
            azure_api_key: Azure OpenAI API key (or from Config)
            azure_api_version: Azure OpenAI API version (or from Config)
            azure_deployment_name: Azure OpenAI deployment name (or from Config)
            azure_model: Azure OpenAI model name (or from Config)
            use_ai: Whether to use AI model (True) or regex (False)
        """
        self.mcp_client = mcp_client
        self.use_ai = use_ai
        
        if use_ai:
            # Get Azure OpenAI config from parameters or Config
            endpoint = azure_endpoint or Config.AZURE_OPENAI_ENDPOINT
            api_key = azure_api_key or Config.AZURE_OPENAI_API_KEY
            api_version = azure_api_version or Config.AZURE_OPENAI_API_VERSION
            deployment_name = azure_deployment_name or Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
            model = azure_model or Config.AZURE_OPENAI_MODEL
            
            if not endpoint or not api_key or not deployment_name:
                raise ValueError(
                    "Azure OpenAI configuration required. Set AZURE_OPENAI_ENDPOINT, "
                    "AZURE_OPENAI_API_KEY, and AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"
                )
            
            logger.info(f"Initializing Azure OpenAI with endpoint: {endpoint}")
            logger.info(f"Using deployment: {deployment_name}, model: {model}")
            
            ai_converter = AIQueryConverter(
                endpoint=endpoint,
                api_key=api_key,
                api_version=api_version,
                deployment_name=deployment_name,
                model=model
            )
            regex_converter = NLQueryConverter()
            self.query_converter = HybridQueryConverter(regex_converter, ai_converter, use_ai=True)
        else:
            self.query_converter = NLQueryConverter()
    
    def process_query(self, natural_language_query: str) -> Dict[str, Any]:
        """
        Process natural language query using AI and execute via MCP
        
        Args:
            natural_language_query: User's natural language query
            
        Returns:
            Result of the operation
        """
        logger.info(f"Processing query: {natural_language_query}")
        
        try:
            # Get available collections for AI context
            available_collections = self._get_collections()
            
            # Convert natural language to MongoDB operation using AI
            mongodb_operation = self.query_converter.convert_to_mongodb_query(
                natural_language_query,
                database=self.mcp_client.database_name,
                available_collections=available_collections
            )
            
            logger.info(f"Converted to MongoDB operation: {mongodb_operation}")
            
            # Execute the operation via MCP
            operation = mongodb_operation['operation']
            collection = mongodb_operation['collection']
            
            if operation == 'find':
                return self._execute_find(collection, mongodb_operation)
            elif operation == 'update':
                return self._execute_update(collection, mongodb_operation)
            elif operation == 'insert':
                return self._execute_insert(collection, mongodb_operation)
            elif operation == 'delete':
                return self._execute_delete(collection, mongodb_operation)
            else:
                return {
                    'success': False,
                    'error': f'Unknown operation: {operation}'
                }
        except Exception as e:
            logger.error(f"Error executing operation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_collections(self) -> List[str]:
        """Get list of available collections"""
        try:
            resources = self.mcp_client.list_resources()
            collections = []
            for resource in resources:
                uri = resource.get('uri', '')
                if 'collection' in uri.lower():
                    collections.append(resource.get('name', ''))
            return collections if collections else ['users', 'products', 'orders']
        except:
            return ['users', 'products', 'orders']
    
    def _execute_find(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute find operation via MCP"""
        filters = operation.get('filters', {})
        limit = operation.get('limit', 10)
        
        try:
            documents = self.mcp_client.query_database(
                collection=collection,
                query=filters,
                limit=limit
            )
            
            return {
                'success': True,
                'operation': 'find',
                'collection': collection,
                'filters': filters,
                'count': len(documents),
                'documents': documents
            }
        except Exception as e:
            return {
                'success': False,
                'operation': 'find',
                'error': str(e)
            }
    
    def _execute_update(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute update operation via MCP"""
        filters = operation.get('filters', {})
        updates = operation.get('updates', {})
        
        if not updates:
            return {
                'success': False,
                'error': 'No update fields specified'
            }
        
        try:
            update_operation = {'$set': updates}
            result = self.mcp_client.update_database(
                collection=collection,
                filter_query=filters,
                update_operation=update_operation
            )
            
            return {
                'success': True,
                'operation': 'update',
                'collection': collection,
                'filters': filters,
                'updates': updates,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'operation': 'update',
                'error': str(e)
            }
    
    def _execute_insert(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute insert operation via MCP"""
        document = operation.get('document', {})
        
        if not document:
            return {
                'success': False,
                'error': 'No document data specified'
            }
        
        try:
            result = self.mcp_client.insert_document(
                collection=collection,
                document=document
            )
            
            return {
                'success': True,
                'operation': 'insert',
                'collection': collection,
                'document': document,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'operation': 'insert',
                'error': str(e)
            }
    
    def _execute_delete(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delete operation via MCP"""
        filters = operation.get('filters', {})
        
        try:
            result = self.mcp_client.delete_documents(
                collection=collection,
                filter_query=filters
            )
            
            return {
                'success': True,
                'operation': 'delete',
                'collection': collection,
                'filters': filters,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'operation': 'delete',
                'error': str(e)
            }
    
    def fetch_data(self, query: str, collection: Optional[str] = None) -> Dict[str, Any]:
        """Fetch data from MongoDB using natural language query"""
        if collection:
            query = f"{query} from {collection} collection"
        return self.process_query(query)
    
    def update_data(self, query: str, collection: Optional[str] = None) -> Dict[str, Any]:
        """Update data in MongoDB using natural language query"""
        if collection:
            query = f"{query} in {collection} collection"
        return self.process_query(query)

