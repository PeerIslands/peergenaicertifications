# MCP-Based MongoDB Search Solution - Implementation Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [How It Works](#how-it-works)
5. [Requirements Implementation Details](#requirements-implementation-details)
6. [Setup Instructions](#setup-instructions)
7. [Usage Guide](#usage-guide)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This is a **complete MCP (Model Context Protocol) implementation** for MongoDB that allows users to query and update MongoDB databases using **natural language**. The solution uses:

- **Azure OpenAI GPT-4o** for natural language understanding
- **MCP Protocol (JSON-RPC 2.0)** for standardized communication
- **Python-based MCP Server** that connects directly to MongoDB
- **Flask Web UI** for easy interaction

### Key Features

✅ **Real MCP Implementation** - Uses actual Model Context Protocol (JSON-RPC 2.0)  
✅ **AI-Powered** - Azure OpenAI GPT-4o converts natural language to MongoDB queries  
✅ **Full CRUD Support** - Query, Insert, Update, and Delete operations  
✅ **Web Interface** - Beautiful, modern UI for easy interaction  
✅ **No npm Required** - Python-based MCP server (no Node.js needed)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User (Web Browser)                        │
│  "find users where age > 25"                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Flask Web Application (web_app.py)             │
│  • Receives HTTP requests                                   │
│  • Routes to search interface                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         RealSearchInterface (real_search_interface.py)       │
│  • Processes natural language queries                       │
│  • Routes to appropriate operations                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         AIQueryConverter (ai_query_converter.py)            │
│  • Uses Azure OpenAI GPT-4o                                │
│  • Converts: "find users where age > 25"                   │
│    → {'operation': 'find', 'collection': 'users',           │
│       'filters': {'age': {'$gt': 25}}}                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│    RealMongoMCPClient (real_mcp_client.py)                  │
│  • MCP Client Connector                                     │
│  • Communicates via stdio (JSON-RPC 2.0)                   │
│  • Calls MCP tools                                          │
└────────────────────┬────────────────────────────────────────┘
                     │ JSON-RPC 2.0 over stdio
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         MongoMCPServer (mcp_server.py)                     │
│  • MCP Server Implementation                                │
│  • Exposes MongoDB tools                                    │
│  • Handles MCP protocol                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         MongoDB Database (PeerGenAI_practice_db)             │
│  • Collections: users, products, orders                      │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. **MCP Server** (`mcp_server.py`)

**Purpose**: Implements the Model Context Protocol server that connects to MongoDB.

**Key Features**:
- Implements JSON-RPC 2.0 protocol
- Communicates via stdio (standard input/output)
- Exposes MongoDB operations as MCP tools
- Handles MCP methods: `initialize`, `tools/list`, `tools/call`, `resources/list`

**MCP Tools Exposed**:
- `mongodb_query` - Query documents from collections
- `mongodb_insert` - Insert documents into collections
- `mongodb_update` - Update documents in collections
- `mongodb_delete` - Delete documents from collections

**How It Works**:
1. Receives JSON-RPC requests via stdin
2. Parses the request and identifies the method
3. Executes the corresponding MongoDB operation
4. Returns JSON-RPC response via stdout

### 2. **MCP Client** (`real_mcp_client.py`)

**Purpose**: Connects to the MCP server and provides MongoDB-specific operations.

**Key Classes**:
- `RealMCPClient` - Base MCP client with JSON-RPC communication
- `RealMongoMCPClient` - MongoDB-specific MCP client

**Key Methods**:
- `connect()` - Initialize connection to MCP server
- `query_database()` - Query documents
- `insert_document()` - Insert documents
- `update_database()` - Update documents
- `delete_documents()` - Delete documents

**How It Works**:
1. Starts MCP server as subprocess
2. Sends JSON-RPC requests via stdin
3. Receives JSON-RPC responses via stdout
4. Handles MCP protocol handshake (`initialize`, `notifications/initialized`)

### 3. **Search Interface** (`real_search_interface.py`)

**Purpose**: Connects natural language queries to MCP client operations.

**Key Features**:
- Integrates Azure OpenAI for natural language understanding
- Routes operations to appropriate MCP client methods
- Handles all CRUD operations (Create, Read, Update, Delete)

**Key Methods**:
- `process_query()` - Main entry point for processing queries
- `_execute_find()` - Execute query operations
- `_execute_insert()` - Execute insert operations
- `_execute_update()` - Execute update operations
- `_execute_delete()` - Execute delete operations

### 4. **AI Query Converter** (`ai_query_converter.py`)

**Purpose**: Converts natural language queries to MongoDB operations using Azure OpenAI.

**Key Features**:
- Uses Azure OpenAI GPT-4o model
- Converts natural language to structured MongoDB operations
- Handles complex queries with filters, limits, and operations

**Example Conversion**:
```
Input:  "find all users where age is greater than 25"
Output: {
    'operation': 'find',
    'collection': 'users',
    'filters': {'age': {'$gt': 25}},
    'limit': 10
}
```

**How It Works**:
1. Sends natural language query to Azure OpenAI
2. Uses structured prompt with MongoDB operation schema
3. Receives JSON response with operation details
4. Parses and validates the response

### 5. **Web Application** (`web_app.py`)

**Purpose**: Flask web application providing UI for the MCP MongoDB search solution.

**Key Features**:
- RESTful API endpoints
- Web UI for natural language queries
- Health check endpoint
- Example queries endpoint

**API Endpoints**:
- `GET /` - Web UI
- `POST /api/query` - Execute natural language query
- `GET /api/health` - Health check
- `GET /api/examples` - Get example queries

### 6. **Configuration** (`config.py`)

**Purpose**: Centralized configuration management.

**Configuration Variables**:
- `MONGODB_CONNECTION_STRING` - MongoDB connection string
- `MONGODB_DATABASE` - Database name
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` - Deployment name
- `AZURE_OPENAI_MODEL` - Model name (default: gpt-4o)

---

## How It Works

### Step-by-Step Flow

1. **User enters natural language query** in web UI
   ```
   "find all users where age is greater than 25"
   ```

2. **Web app receives query** via `/api/query` endpoint

3. **Search interface processes query**:
   - Sends to Azure OpenAI GPT-4o
   - AI converts to MongoDB operation format

4. **AI returns structured operation**:
   ```json
   {
       "operation": "find",
       "collection": "users",
       "filters": {"age": {"$gt": 25}},
       "limit": 10
   }
   ```

5. **Search interface routes to MCP client**:
   - Calls `mcp_client.query_database()`

6. **MCP client sends JSON-RPC request** to MCP server:
   ```json
   {
       "jsonrpc": "2.0",
       "id": 1,
       "method": "tools/call",
       "params": {
           "name": "mongodb_query",
           "arguments": {
               "database": "PeerGenAI_practice_db",
               "collection": "users",
               "query": {"age": {"$gt": 25}},
               "limit": 10
           }
       }
   }
   ```

7. **MCP server executes MongoDB query**:
   - Connects to MongoDB
   - Executes `db.users.find({"age": {"$gt": 25}}).limit(10)`
   - Returns documents

8. **Response flows back** through the chain:
   - MCP server → MCP client → Search interface → Web app → User

9. **Results displayed** in web UI with:
   - Documents found
   - Filters applied
   - Operation details

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+**
2. **MongoDB** (local or Atlas)
3. **Azure OpenAI Account** with GPT-4o deployment

### Step 1: Install Dependencies

```bash
cd mcp-mongodb-search
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables

Create `.env` file:

```bash
# MongoDB Configuration
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=PeerGenAI_practice_db

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_MODEL=gpt-4o
```

### Step 3: Initialize Database (Optional)

Create sample data:

```bash
python create_sample_data.py
```

This creates:
- `users` collection with 6 sample users
- `products` collection with 7 sample products
- `orders` collection with 5 sample orders

### Step 4: Start the Web Application

```bash
python web_app.py
```

The application will start on `http://localhost:5000`

### Step 5: Access Web UI

Open your browser and navigate to:
```
http://localhost:5000
```

---

## Usage Guide

### Web UI Usage

1. **Open the web interface** at `http://localhost:5000`

2. **Enter a natural language query** in the text area:
   - "find all users where age is greater than 25"
   - "get products from products collection where price is less than 100"
   - "insert new user with name John and age 28"
   - "show first 5 documents from orders collection"

3. **Click "Execute Query"** button

4. **View results**:
   - Operation type
   - Collection name
   - Filters applied
   - Documents found
   - Success/error messages

### Example Queries

#### Query Operations

```
find all users where age is greater than 25
list users where status is active
get products from products collection where price is less than 100
show first 5 documents from orders collection
find users where city is New York
```

#### Insert Operations

```
insert new user with name Alice and age 30
add product with name Laptop and price 999.99
create new order with user Bob and product Phone
```

#### Update Operations

```
update users set status to active where name is Alice
update products set price to 799.99 where name is Phone
```

#### Delete Operations

```
delete users where age is less than 18
remove products where stock is 0
```

### Python API Usage

```python
from real_mcp_client import RealMongoMCPClient
from real_search_interface import RealSearchInterface
from config import Config

# Initialize MCP client
mcp_client = RealMongoMCPClient(
    connection_string=Config.MONGODB_CONNECTION_STRING,
    database_name=Config.MONGODB_DATABASE
)

# Connect to MCP server
mcp_client.connect()

# Create search interface
search_interface = RealSearchInterface(
    mcp_client=mcp_client,
    azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    azure_api_key=Config.AZURE_OPENAI_API_KEY,
    azure_deployment_name=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
)

# Process query
result = search_interface.process_query(
    "find all users where age is greater than 25"
)

print(result)
```

---

## API Reference

### RealMongoMCPClient

#### `query_database(collection, query, limit=10)`

Query documents from a collection.

**Parameters**:
- `collection` (str): Collection name
- `query` (dict): MongoDB query filter
- `limit` (int): Maximum number of documents to return

**Returns**: List of documents

**Example**:
```python
documents = mcp_client.query_database(
    collection="users",
    query={"age": {"$gt": 25}},
    limit=10
)
```

#### `insert_document(collection, document)`

Insert a document into a collection.

**Parameters**:
- `collection` (str): Collection name
- `document` (dict): Document to insert

**Returns**: Insert result with `inserted_id`

**Example**:
```python
result = mcp_client.insert_document(
    collection="users",
    document={"name": "John", "age": 28}
)
```

#### `update_database(collection, filter_query, update_operation)`

Update documents in a collection.

**Parameters**:
- `collection` (str): Collection name
- `filter_query` (dict): Documents to update
- `update_operation` (dict): Update operation (e.g., `{"$set": {...}}`)

**Returns**: Update result with `matched_count` and `modified_count`

**Example**:
```python
result = mcp_client.update_database(
    collection="users",
    filter_query={"name": "John"},
    update_operation={"$set": {"age": 29}}
)
```

#### `delete_documents(collection, filter_query)`

Delete documents from a collection.

**Parameters**:
- `collection` (str): Collection name
- `filter_query` (dict): Documents to delete

**Returns**: Delete result with `deleted_count`

**Example**:
```python
result = mcp_client.delete_documents(
    collection="users",
    filter_query={"age": {"$lt": 18}}
)
```

### RealSearchInterface

#### `process_query(natural_language_query)`

Process a natural language query and execute the corresponding MongoDB operation.

**Parameters**:
- `natural_language_query` (str): Natural language query

**Returns**: Dictionary with operation results

**Example**:
```python
result = search_interface.process_query(
    "find all users where age is greater than 25"
)
```

**Response Format**:
```json
{
    "success": true,
    "operation": "find",
    "collection": "users",
    "filters": {"age": {"$gt": 25}},
    "count": 3,
    "documents": [...]
}
```

---

## Troubleshooting

### Issue: "MCP server error: Database objects do not implement truth value testing"

**Solution**: This was fixed in the latest version. Make sure you're using the updated `mcp_server.py` that uses `is not None` instead of boolean checks.

### Issue: "Azure OpenAI configuration incomplete"

**Solution**: 
1. Check your `.env` file has all required Azure OpenAI variables
2. Verify your API key is correct
3. Ensure deployment name matches your Azure OpenAI deployment

### Issue: "Failed to connect to MCP server"

**Solution**:
1. Make sure MongoDB is running
2. Check MongoDB connection string in `.env`
3. Verify Python can execute `mcp_server.py`

### Issue: "No response from MCP server"

**Solution**:
1. Check if MCP server process is running
2. Look for errors in server logs
3. Verify stdio communication is working

### Issue: "Collection not found" or empty results

**Solution**:
1. Run `python create_sample_data.py` to create sample data
2. Verify database name in `.env` matches your MongoDB database
3. Check collection names are correct

### Issue: AI not converting queries correctly

**Solution**:
1. Verify Azure OpenAI credentials are correct
2. Check deployment name matches your Azure OpenAI deployment
3. Ensure GPT-4o model is available in your deployment
4. Review AI response in logs for debugging

---

## File Structure

```
mcp-mongodb-search/
├── real_mcp_client.py          # MCP client connector
├── mcp_server.py                # MCP server implementation
├── real_search_interface.py     # Search interface with AI
├── ai_query_converter.py        # Azure OpenAI query converter
├── nl_query_converter.py        # Regex fallback converter
├── web_app.py                   # Flask web application
├── config.py                    # Configuration management
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (create this)
├── static/                      # Web UI static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/                   # Web UI templates
│   └── index.html
├── create_sample_data.py        # Create sample data
├── init_database.py             # Initialize database
├── test_connection.py           # Test MongoDB connection
├── check_records.py             # Check records in collections
├── setup_local.sh               # Setup script
├── README.md                    # Main documentation
└── IMPLEMENTATION_GUIDE.md      # This file
```

---

## Requirements Implementation Details

This section explains **exactly how each requirement was implemented** with code references and technical details.

---

### Requirement 1: Implement a MCP-based search solution for MongoDB

**Status**: ✅ **Fully Implemented**

**Implementation Files**:
- `mcp_server.py` - MCP server implementation
- `real_mcp_client.py` - MCP client implementation
- `web_app.py` - Complete search solution with web UI

**How It Was Implemented**:

#### 1.1 MCP Server (`mcp_server.py`)

The MCP server implements the **Model Context Protocol** using **JSON-RPC 2.0** over **stdio**:

```python
class MongoMCPServer:
    """MCP Server implementation for MongoDB operations"""
    
    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle MCP protocol request or notification"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        # Implements MCP methods:
        # - initialize
        # - tools/list
        # - tools/call
        # - resources/list
        # - resources/read
        # - notifications/initialized
```

**Key Features**:
- ✅ Implements JSON-RPC 2.0 protocol (`"jsonrpc": "2.0"`)
- ✅ Uses MCP protocol version `2024-11-05`
- ✅ Communicates via stdio (standard input/output)
- ✅ Exposes MongoDB operations as MCP tools:
  - `mongodb_query` - Query documents
  - `mongodb_insert` - Insert documents
  - `mongodb_update` - Update documents
  - `mongodb_delete` - Delete documents

**MCP Protocol Implementation**:
```python
# JSON-RPC 2.0 Request Format
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "mongodb_query",
        "arguments": {
            "database": "PeerGenAI_practice_db",
            "collection": "users",
            "query": {"age": {"$gt": 25}},
            "limit": 10
        }
    }
}

# JSON-RPC 2.0 Response Format
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "documents": [...],
        "count": 3
    }
}
```

#### 1.2 Complete Solution Integration

The solution integrates all components:
- **MCP Server** ↔ **MCP Client** ↔ **Search Interface** ↔ **Web UI**

**Location**: `web_app.py` (lines 28-103)

```python
def init_app():
    """Initialize the MCP MongoDB search application"""
    # 1. Create MCP client
    mcp_client = RealMongoMCPClient(
        connection_string=connection_string,
        database_name=database_name
    )
    
    # 2. Connect to MCP server
    mcp_client.connect()
    
    # 3. Create search interface
    search_interface = RealSearchInterface(
        mcp_client=mcp_client,
        azure_endpoint=azure_endpoint,
        ...
    )
    
    # 4. Store in global app
    search_app = {
        'mcp_client': mcp_client,
        'search_interface': search_interface
    }
```

**Result**: A complete, working MCP-based search solution for MongoDB that can be accessed via web UI or Python API.

---

### Requirement 2: Build a MCP client connector to Mongo MCP server

**Status**: ✅ **Fully Implemented**

**Implementation File**: `real_mcp_client.py`

**How It Was Implemented**:

#### 2.1 Base MCP Client (`RealMCPClient`)

Implements the core MCP client functionality:

```python
class RealMCPClient:
    """Real MCP Client that communicates with MongoDB MCP Server"""
    
    def __init__(self, server_command: List[str]):
        """Initialize MCP client with server command"""
        self.server_command = server_command
        self.process = None  # Subprocess for MCP server
        self.request_id = 0
        self.initialized = False
```

**Key Methods**:

1. **`start_server()`** - Starts MCP server as subprocess:
```python
def start_server(self) -> bool:
    """Start the MCP server process"""
    self.process = subprocess.Popen(
        server_cmd,
        stdin=subprocess.PIPE,   # Write requests
        stdout=subprocess.PIPE,   # Read responses
        stderr=subprocess.PIPE,
        text=True
    )
```

2. **`_send_request_stdio()`** - Sends JSON-RPC requests:
```python
def _send_request_stdio(self, method: str, params: Dict[str, Any]):
    """Send JSON-RPC request via stdio to MCP server"""
    request = {
        "jsonrpc": "2.0",
        "id": self._get_next_request_id(),
        "method": method,
        "params": params
    }
    # Write to stdin
    self.process.stdin.write(json.dumps(request) + "\n")
    # Read from stdout
    response_line = self.process.stdout.readline()
    response = json.loads(response_line.strip())
    return response.get('result', {})
```

3. **`initialize()`** - MCP protocol handshake:
```python
def initialize(self, client_info: Dict[str, Any]) -> Dict[str, Any]:
    """Initialize connection with MCP server"""
    params = {
        "protocolVersion": "2024-11-05",
        "capabilities": {...},
        "clientInfo": client_info
    }
    result = self._send_request_stdio("initialize", params)
    # Send initialized notification
    notification = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }
    return result
```

#### 2.2 MongoDB-Specific MCP Client (`RealMongoMCPClient`)

Extends the base client with MongoDB-specific operations:

```python
class RealMongoMCPClient(RealMCPClient):
    """Real MongoDB MCP Client with MongoDB-specific operations"""
    
    def __init__(self, connection_string: str, database_name: str):
        """Initialize MongoDB MCP client"""
        # Use Python-based MCP server
        server_command = [sys.executable, mcp_server_path]
        super().__init__(server_command)
        self.connection_string = connection_string
        self.database_name = database_name
```

**MongoDB Operations via MCP**:

1. **`query_database()`** - Query documents:
```python
def query_database(self, collection: str, query: Dict, limit: int = 10):
    """Query MongoDB database through MCP server"""
    result = self.call_tool("mongodb_query", {
        "database": self.database_name,
        "collection": collection,
        "query": query,
        "limit": limit
    })
    return result.get("documents", [])
```

2. **`insert_document()`** - Insert documents:
```python
def insert_document(self, collection: str, document: Dict):
    """Insert document into MongoDB through MCP server"""
    result = self.call_tool("mongodb_insert", {
        "database": self.database_name,
        "collection": collection,
        "document": document
    })
    return result
```

3. **`update_database()`** - Update documents:
```python
def update_database(self, collection: str, filter_query: Dict, update_op: Dict):
    """Update MongoDB database through MCP server"""
    result = self.call_tool("mongodb_update", {
        "database": self.database_name,
        "collection": collection,
        "filter": filter_query,
        "update": update_op
    })
    return result
```

4. **`delete_documents()`** - Delete documents:
```python
def delete_documents(self, collection: str, filter_query: Dict):
    """Delete documents from MongoDB through MCP server"""
    result = self.call_tool("mongodb_delete", {
        "database": self.database_name,
        "collection": collection,
        "filter": filter_query
    })
    return result
```

**Result**: A complete MCP client connector that:
- ✅ Connects to MCP server via stdio
- ✅ Implements JSON-RPC 2.0 protocol
- ✅ Provides MongoDB-specific operations
- ✅ Handles MCP protocol handshake
- ✅ Manages subprocess communication

---

### Requirement 3: Develop a search interface to connect to MCP client connector and convert natural language queries into Mongo MCP server

**Status**: ✅ **Fully Implemented**

**Implementation Files**:
- `real_search_interface.py` - Search interface
- `ai_query_converter.py` - AI-powered natural language converter

**How It Was Implemented**:

#### 3.1 Search Interface (`RealSearchInterface`)

Connects to MCP client and processes natural language queries:

```python
class RealSearchInterface:
    """Search interface that uses Azure OpenAI AI model and real MCP client"""
    
    def __init__(self, mcp_client: RealMongoMCPClient, ...):
        """Initialize search interface with MCP client and AI"""
        self.mcp_client = mcp_client  # ✅ Connects to MCP client connector
        self.query_converter = AIQueryConverter(...)  # ✅ Converts NL to MongoDB
```

**Key Method - `process_query()`**:

```python
def process_query(self, natural_language_query: str) -> Dict[str, Any]:
    """
    Process natural language query using AI and execute via MCP
    
    Flow:
    1. Natural Language Query (input)
    2. AI Converter (converts to MongoDB operation)
    3. Route to appropriate MCP client method
    4. Execute via MCP server
    5. Return results
    """
    # Step 1: Convert natural language to MongoDB operation
    mongodb_operation = self.query_converter.convert_to_mongodb_query(
        natural_language_query
    )
    
    # Step 2: Extract operation details
    operation = mongodb_operation.get('operation')
    collection = mongodb_operation.get('collection')
    
    # Step 3: Route to appropriate MCP client method
    if operation == 'find':
        return self._execute_find(collection, mongodb_operation)
    elif operation == 'insert':
        return self._execute_insert(collection, mongodb_operation)
    elif operation == 'update':
        return self._execute_update(collection, mongodb_operation)
    elif operation == 'delete':
        return self._execute_delete(collection, mongodb_operation)
```

#### 3.2 AI Query Converter (`AIQueryConverter`)

Converts natural language to MongoDB operations using Azure OpenAI:

```python
class AIQueryConverter:
    """Convert natural language queries to MongoDB operations using Azure OpenAI"""
    
    def convert_to_mongodb_query(self, query: str) -> Dict[str, Any]:
        """
        Convert natural language query to MongoDB operation
        
        Example:
        Input:  "find all users where age is greater than 25"
        Output: {
            'operation': 'find',
            'collection': 'users',
            'filters': {'age': {'$gt': 25}},
            'limit': 10
        }
        """
        # Get available collections
        collections = self.get_available_collections()
        
        # Create prompt for Azure OpenAI
        prompt = f"""
        Convert the following natural language query to a MongoDB operation.
        Available collections: {', '.join(collections)}
        
        Query: {query}
        
        Return JSON with:
        - operation: 'find', 'insert', 'update', or 'delete'
        - collection: collection name
        - filters: MongoDB query filter (for find/update/delete)
        - document: document to insert (for insert)
        - update: update operation (for update)
        - limit: max documents to return (for find)
        """
        
        # Call Azure OpenAI GPT-4o
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a MongoDB query converter..."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        # Parse and return MongoDB operation
        return json.loads(response.choices[0].message.content)
```

**Conversion Examples**:

| Natural Language | MongoDB Operation |
|-----------------|-------------------|
| `"find all users where age is greater than 25"` | `{'operation': 'find', 'collection': 'users', 'filters': {'age': {'$gt': 25}}}` |
| `"insert new user with name John and age 28"` | `{'operation': 'insert', 'collection': 'users', 'document': {'name': 'John', 'age': 28}}` |
| `"update users set status to active where name is Alice"` | `{'operation': 'update', 'collection': 'users', 'filters': {'name': 'Alice'}, 'update': {'$set': {'status': 'active'}}}` |
| `"delete users where age is less than 18"` | `{'operation': 'delete', 'collection': 'users', 'filters': {'age': {'$lt': 18}}}` |

**Result**: A search interface that:
- ✅ Connects to MCP client connector (`RealMongoMCPClient`)
- ✅ Uses Azure OpenAI GPT-4o to convert natural language
- ✅ Converts queries to MongoDB operation format
- ✅ Routes operations to appropriate MCP client methods
- ✅ Handles all CRUD operations

---

### Requirement 4: Use search interface to fetch or update database content using Mongo MCP server

**Status**: ✅ **Fully Implemented**

**Implementation File**: `real_search_interface.py`

**How It Was Implemented**:

#### 4.1 Fetch Operations (`_execute_find`)

```python
def _execute_find(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
    """Execute find operation via MCP"""
    filters = operation.get('filters', {})
    limit = operation.get('limit', 10)
    
    # ✅ Use MCP client to fetch from MongoDB via MCP server
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
```

**Flow**:
1. Search interface receives MongoDB operation
2. Calls `mcp_client.query_database()`
3. MCP client sends JSON-RPC request to MCP server
4. MCP server executes MongoDB query
5. Results flow back through the chain

#### 4.2 Update Operations - Insert (`_execute_insert`)

```python
def _execute_insert(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
    """Execute insert operation via MCP"""
    document = operation.get('document', {})
    
    # ✅ Use MCP client to insert into MongoDB via MCP server
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
```

#### 4.3 Update Operations - Modify (`_execute_update`)

```python
def _execute_update(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
    """Execute update operation via MCP"""
    filters = operation.get('filters', {})
    update_op = operation.get('update', {})
    
    # ✅ Use MCP client to update MongoDB via MCP server
    result = self.mcp_client.update_database(
        collection=collection,
        filter_query=filters,
        update_operation=update_op
    )
    
    return {
        'success': True,
        'operation': 'update',
        'collection': collection,
        'filters': filters,
        'updates': update_op,
        'result': result
    }
```

#### 4.4 Update Operations - Delete (`_execute_delete`)

```python
def _execute_delete(self, collection: str, operation: Dict[str, Any]) -> Dict[str, Any]:
    """Execute delete operation via MCP"""
    filters = operation.get('filters', {})
    
    # ✅ Use MCP client to delete from MongoDB via MCP server
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
```

#### 4.5 Complete Flow Example

**Example: Fetching Data**

```
User Query: "find all users where age is greater than 25"
    ↓
Search Interface (process_query)
    ↓
AI Converter (convert_to_mongodb_query)
    → {'operation': 'find', 'collection': 'users', 'filters': {'age': {'$gt': 25}}}
    ↓
Search Interface (_execute_find)
    ↓
MCP Client (query_database)
    → JSON-RPC request to MCP server
    ↓
MCP Server (mongodb_query tool)
    → Executes: db.users.find({"age": {"$gt": 25}})
    ↓
MongoDB Database
    → Returns documents
    ↓
Results flow back through chain
    ↓
User sees results in web UI
```

**Example: Updating Data**

```
User Query: "insert new user with name John and age 28"
    ↓
Search Interface (process_query)
    ↓
AI Converter (convert_to_mongodb_query)
    → {'operation': 'insert', 'collection': 'users', 'document': {'name': 'John', 'age': 28}}
    ↓
Search Interface (_execute_insert)
    ↓
MCP Client (insert_document)
    → JSON-RPC request to MCP server
    ↓
MCP Server (mongodb_insert tool)
    → Executes: db.users.insert_one({"name": "John", "age": 28})
    ↓
MongoDB Database
    → Document inserted
    ↓
Results flow back through chain
    ↓
User sees success message
```

**Result**: The search interface successfully:
- ✅ **Fetches** data using `query_database()` via MCP server
- ✅ **Updates** data using:
  - `insert_document()` for creating new documents
  - `update_database()` for modifying existing documents
  - `delete_documents()` for removing documents
- ✅ All operations go through the MCP server
- ✅ All operations return results to the user

---

## Requirements Fulfillment Summary

| Requirement | Status | Implementation |
|------------|--------|----------------|
| **1. Implement MCP-based search solution** | ✅ Complete | `mcp_server.py` + `real_mcp_client.py` + `web_app.py` |
| **2. Build MCP client connector** | ✅ Complete | `real_mcp_client.py` (RealMongoMCPClient) |
| **3. Develop search interface with NL conversion** | ✅ Complete | `real_search_interface.py` + `ai_query_converter.py` |
| **4. Use search interface to fetch/update via MCP** | ✅ Complete | All CRUD operations in `real_search_interface.py` |

**All requirements are fully implemented and working!** ✅

---

## Additional Resources

- **MCP Protocol Specification**: [Model Context Protocol](https://modelcontextprotocol.io)
- **MongoDB Documentation**: [MongoDB Manual](https://docs.mongodb.com)
- **Azure OpenAI Documentation**: [Azure OpenAI Service](https://learn.microsoft.com/azure/ai-services/openai/)

---

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in the terminal where `web_app.py` is running
3. Verify all configuration in `.env` file
4. Test MongoDB connection: `python test_connection.py`
5. Test Azure OpenAI: Check API key and deployment name

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready ✅

