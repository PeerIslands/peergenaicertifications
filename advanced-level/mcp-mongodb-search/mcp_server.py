"""
MCP Server Implementation for MongoDB
A Python-based MCP server that implements the Model Context Protocol
and connects directly to MongoDB
"""

import json
import sys
import logging
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MongoMCPServer:
    """MCP Server implementation for MongoDB operations"""
    
    def __init__(self, connection_string: str, database_name: str):
        """
        Initialize MongoDB MCP server
        
        Args:
            connection_string: MongoDB connection string
            database_name: Default database name
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self.client = None
        self.db = None
        self.initialized = False
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.initialized = True
            logger.info(f"Connected to MongoDB: {self.database_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            return False
    
    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle MCP protocol request or notification
        
        Args:
            request: JSON-RPC request or notification
            
        Returns:
            JSON-RPC response (None for notifications)
        """
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        # Check if this is a notification (no id field)
        is_notification = 'id' not in request
        
        try:
            if method == 'initialize':
                result = self._handle_initialize(params)
            elif method == 'tools/list':
                result = self._handle_tools_list()
            elif method == 'tools/call':
                result = self._handle_tools_call(params)
            elif method == 'resources/list':
                result = self._handle_resources_list()
            elif method == 'resources/read':
                result = self._handle_resources_read(params)
            elif method == 'notifications/initialized':
                # Handle initialization notification (no response needed)
                logger.debug("Received initialized notification")
                return None
            else:
                if is_notification:
                    # Unknown notification - silently ignore
                    logger.debug(f"Ignoring unknown notification: {method}")
                    return None
                raise ValueError(f"Unknown method: {method}")
            
            # Notifications don't get responses
            if is_notification:
                return None
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            # Don't send error responses for notifications
            if is_notification:
                logger.warning(f"Error in notification {method}: {e}")
                return None
            
            logger.error(f"Error handling request: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        if not self.initialized:
            self.connect()
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {}
            },
            "serverInfo": {
                "name": "mongodb-mcp-server",
                "version": "1.0.0"
            }
        }
    
    def _handle_tools_list(self) -> Dict[str, Any]:
        """List available MCP tools"""
        tools = [
            {
                "name": "mongodb_query",
                "description": "Query documents from a MongoDB collection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "collection": {"type": "string"},
                        "query": {"type": "object"},
                        "limit": {"type": "integer", "default": 10}
                    },
                    "required": ["database", "collection"]
                }
            },
            {
                "name": "mongodb_insert",
                "description": "Insert a document into a MongoDB collection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "collection": {"type": "string"},
                        "document": {"type": "object"}
                    },
                    "required": ["database", "collection", "document"]
                }
            },
            {
                "name": "mongodb_update",
                "description": "Update documents in a MongoDB collection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "collection": {"type": "string"},
                        "filter": {"type": "object"},
                        "update": {"type": "object"}
                    },
                    "required": ["database", "collection", "filter", "update"]
                }
            },
            {
                "name": "mongodb_delete",
                "description": "Delete documents from a MongoDB collection",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string"},
                        "collection": {"type": "string"},
                        "filter": {"type": "object"}
                    },
                    "required": ["database", "collection", "filter"]
                }
            }
        ]
        return {"tools": tools}
    
    def _handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool call"""
        tool_name = params.get('name')
        arguments = params.get('arguments', {})
        
        if tool_name == 'mongodb_query':
            return self._tool_mongodb_query(arguments)
        elif tool_name == 'mongodb_insert':
            return self._tool_mongodb_insert(arguments)
        elif tool_name == 'mongodb_update':
            return self._tool_mongodb_update(arguments)
        elif tool_name == 'mongodb_delete':
            return self._tool_mongodb_delete(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _tool_mongodb_query(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute MongoDB query"""
        if not self.initialized or self.client is None:
            raise RuntimeError("MongoDB client not initialized")
        
        database = args.get('database', self.database_name)
        collection = args.get('collection')
        query = args.get('query', {})
        limit = args.get('limit', 10)
        
        if not collection:
            raise ValueError("Collection name is required")
        
        db = self.client[database]
        coll = db[collection]
        
        documents = list(coll.find(query).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for doc in documents:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        
        return {
            "documents": documents,
            "count": len(documents)
        }
    
    def _tool_mongodb_insert(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Insert document into MongoDB"""
        if not self.initialized or self.client is None:
            raise RuntimeError("MongoDB client not initialized")
        
        database = args.get('database', self.database_name)
        collection = args.get('collection')
        document = args.get('document')
        
        if not collection:
            raise ValueError("Collection name is required")
        if not document:
            raise ValueError("Document is required")
        
        db = self.client[database]
        coll = db[collection]
        
        result = coll.insert_one(document)
        
        return {
            "inserted_id": str(result.inserted_id),
            "acknowledged": result.acknowledged
        }
    
    def _tool_mongodb_update(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Update documents in MongoDB"""
        if not self.initialized or self.client is None:
            raise RuntimeError("MongoDB client not initialized")
        
        database = args.get('database', self.database_name)
        collection = args.get('collection')
        filter_query = args.get('filter', {})
        update_operation = args.get('update', {})
        
        if not collection:
            raise ValueError("Collection name is required")
        if not update_operation:
            raise ValueError("Update operation is required")
        
        db = self.client[database]
        coll = db[collection]
        
        result = coll.update_many(filter_query, update_operation)
        
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
            "acknowledged": result.acknowledged
        }
    
    def _tool_mongodb_delete(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Delete documents from MongoDB"""
        if not self.initialized or self.client is None:
            raise RuntimeError("MongoDB client not initialized")
        
        database = args.get('database', self.database_name)
        collection = args.get('collection')
        filter_query = args.get('filter', {})
        
        if not collection:
            raise ValueError("Collection name is required")
        
        db = self.client[database]
        coll = db[collection]
        
        result = coll.delete_many(filter_query)
        
        return {
            "deleted_count": result.deleted_count,
            "acknowledged": result.acknowledged
        }
    
    def _handle_resources_list(self) -> Dict[str, Any]:
        """List available resources"""
        resources = []
        
        if self.initialized and self.db is not None:
            collections = self.db.list_collection_names()
            for collection in collections:
                resources.append({
                    "uri": f"mongodb://collection/{collection}",
                    "name": collection,
                    "mimeType": "application/json"
                })
        
        return {"resources": resources}
    
    def _handle_resources_read(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Read a resource"""
        uri = params.get('uri', '')
        
        if uri.startswith('mongodb://collection/'):
            collection_name = uri.replace('mongodb://collection/', '')
            collection = self.db[collection_name]
            count = collection.count_documents({})
            return {
                "contents": [{
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps({"collection": collection_name, "count": count})
                }]
            }
        
        raise ValueError(f"Unknown resource URI: {uri}")


def main():
    """Run MCP server in stdio mode"""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment (set by MCP client)
    connection_string = os.getenv('MONGODB_URI') or os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017')
    database_name = os.getenv('MONGODB_DATABASE', 'PeerGenAI_practice_db')
    
    logger.info(f"Starting MCP server with database: {database_name}")
    
    server = MongoMCPServer(connection_string, database_name)
    
    # Read from stdin, write to stdout
    for line in sys.stdin:
        try:
            if not line.strip():
                continue
            request = json.loads(line.strip())
            response = server.handle_request(request)
            
            # Only send response if it's not a notification (response is not None)
            if response is not None:
                print(json.dumps(response))
                sys.stdout.flush()
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON: {e}")
            continue
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
            # Only send error if it was a request (has id), not a notification
            if 'request' in locals() and 'id' in request:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get('id'),
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()


if __name__ == '__main__':
    main()

