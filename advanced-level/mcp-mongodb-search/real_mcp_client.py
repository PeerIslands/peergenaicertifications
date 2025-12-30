"""
Real MCP Client for MongoDB MCP Server
Implements actual MCP protocol communication via stdio or HTTP
"""

import json
import subprocess
import sys
import os
from typing import Dict, List, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CLIENT_NOT_INITIALIZED_MSG = "Client not initialized. Call connect() first."


class RealMCPClient:
    """Real MCP Client that communicates with MongoDB MCP Server"""
    
    def __init__(self, server_command: List[str], server_args: Optional[Dict] = None):
        """
        Initialize MCP client
        
        Args:
            server_command: Command to start the MCP server
                           e.g., ['npx', '-y', '@modelcontextprotocol/server-mongodb']
            server_args: Additional arguments for the server
        """
        self.server_command = server_command
        self.server_args = server_args or {}
        self.process = None
        self.request_id = 0
        self.initialized = False
        self.capabilities = {}
        
    def _get_next_request_id(self) -> int:
        """Get next request ID for JSON-RPC"""
        self.request_id += 1
        return self.request_id
    
    def _send_request_stdio(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send JSON-RPC request via stdio to MCP server
        
        Args:
            method: MCP method name
            params: Method parameters
            
        Returns:
            Response from server
        """
        if not self.process:
            raise RuntimeError("MCP server process not started")
        
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_request_id(),
            "method": method,
            "params": params
        }
        
        try:
            # Write request to stdin (text mode)
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response from stdout (text mode)
            response_line = self.process.stdout.readline()
            if not response_line:
                raise RuntimeError("No response from MCP server")
            
            response = json.loads(response_line.strip())
            
            if 'error' in response:
                error_msg = response['error'].get('message', 'Unknown error')
                raise RuntimeError(f"MCP server error: {error_msg}")
            
            logger.debug(f"MCP response: {response}")
            return response.get('result', {})
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP server response: {e}")
            logger.error(f"Response was: {response_line}")
            raise RuntimeError(f"Invalid JSON response from MCP server: {e}")
        except Exception as e:
            logger.error(f"Error communicating with MCP server: {e}")
            raise
    
    def start_server(self) -> bool:
        """
        Start the MCP server process
        
        Returns:
            True if server started successfully
        """
        try:
            logger.info(f"Starting MCP server: {' '.join(self.server_command)}")
            
            # Get the directory of mcp_server.py
            script_dir = os.path.dirname(os.path.abspath(__file__))
            mcp_server_path = os.path.join(script_dir, 'mcp_server.py')
            
            # Use Python to run the MCP server script directly
            server_cmd = [sys.executable, mcp_server_path]
            
            # Start server process with stdio communication
            # Use text mode for line buffering support
            self.process = subprocess.Popen(
                server_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,  # Use text mode for line buffering
                bufsize=1,  # Line buffered
                cwd=script_dir
            )
            
            logger.info("MCP server process started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start MCP server: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initialize connection with MCP server
        
        Args:
            client_info: Client information
            
        Returns:
            Server capabilities
        """
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "experimental": {},
                "sampling": {}
            },
            "clientInfo": client_info
        }
        
        result = self._send_request_stdio("initialize", params)
        self.capabilities = result.get("capabilities", {})
        self.initialized = True
        
        # Send initialized notification (text mode)
        notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        self.process.stdin.write(json.dumps(notification) + "\n")
        self.process.stdin.flush()
        
        return result
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """
        List available tools from MongoDB MCP server
        
        Returns:
            List of available tools
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        result = self._send_request_stdio("tools/list", {})
        return result.get("tools", [])
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        result = self._send_request_stdio("tools/call", params)
        return result
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """
        List available resources from MongoDB MCP server
        
        Returns:
            List of available resources
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        result = self._send_request_stdio("resources/list", {})
        return result.get("resources", [])
    
    def read_resource(self, uri: str) -> Dict[str, Any]:
        """
        Read a resource from MongoDB MCP server
        
        Args:
            uri: Resource URI
            
        Returns:
            Resource content
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        params = {"uri": uri}
        result = self._send_request_stdio("resources/read", params)
        return result
    
    def close(self):
        """Close connection to MCP server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
        self.initialized = False


class RealMongoMCPClient(RealMCPClient):
    """Real MongoDB MCP Client with MongoDB-specific operations"""
    
    def __init__(self, connection_string: str, database_name: str, 
                 server_command: Optional[List[str]] = None):
        """
        Initialize MongoDB MCP client
        
        Args:
            connection_string: MongoDB connection string
            database_name: Name of the database
            server_command: Optional custom server command (defaults to Python MCP server)
        """
        if server_command is None:
            # Use Python-based MCP server instead of npm package
            import sys
            server_command = [sys.executable, '-m', 'mcp_server']
        
        # Set environment variables for MCP server
        os.environ['MONGODB_URI'] = connection_string
        os.environ['MONGODB_DATABASE'] = database_name
        
        super().__init__(server_command)
        self.connection_string = connection_string
        self.database_name = database_name
    
    def connect(self) -> bool:
        """
        Connect to MongoDB MCP server
        
        Returns:
            True if connection successful
        """
        try:
            # Start the MCP server
            if not self.start_server():
                return False
            
            # Initialize connection
            client_info = {
                "name": "mongodb-mcp-search-client",
                "version": "1.0.0"
            }
            self.initialize(client_info)
            
            logger.info("Successfully connected to MongoDB MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB MCP server: {e}")
            return False
    
    def query_database(self, collection: str, query: Dict[str, Any], 
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query MongoDB database through MCP server
        
        Args:
            collection: Collection name
            query: MongoDB query filter
            limit: Maximum number of results
            
        Returns:
            List of documents
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        arguments = {
            "database": self.database_name,
            "collection": collection,
            "query": query,
            "limit": limit
        }
        
        logger.info(f"Querying database: {self.database_name}, collection: {collection}")
        result = self.call_tool("mongodb_query", arguments)
        return result.get("documents", [])
    
    def update_database(self, collection: str, filter_query: Dict[str, Any],
                       update_operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update MongoDB database through MCP server
        
        Args:
            collection: Collection name
            filter_query: MongoDB filter query
            update_operation: MongoDB update operation
            
        Returns:
            Update result
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        arguments = {
            "database": self.database_name,
            "collection": collection,
            "filter": filter_query,
            "update": update_operation
        }
        
        logger.info(f"Updating database: {self.database_name}, collection: {collection}")
        return self.call_tool("mongodb_update", arguments)
    
    def insert_document(self, collection: str, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert document into MongoDB through MCP server
        
        Args:
            collection: Collection name
            document: Document to insert
            
        Returns:
            Insert result
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        arguments = {
            "database": self.database_name,
            "collection": collection,
            "document": document
        }
        
        logger.info(f"Inserting into database: {self.database_name}, collection: {collection}")
        return self.call_tool("mongodb_insert", arguments)
    
    def delete_documents(self, collection: str, filter_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete documents from MongoDB through MCP server
        
        Args:
            collection: Collection name
            filter_query: MongoDB filter query
            
        Returns:
            Delete result
        """
        if not self.initialized:
            raise RuntimeError(CLIENT_NOT_INITIALIZED_MSG)
        
        arguments = {
            "database": self.database_name,
            "collection": collection,
            "filter": filter_query
        }
        
        logger.info(f"Deleting from database: {self.database_name}, collection: {collection}")
        return self.call_tool("mongodb_delete", arguments)

