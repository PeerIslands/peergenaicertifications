# MCP-based MongoDB Search Solution

A complete implementation of an MCP (Model Context Protocol) based search solution for MongoDB that allows natural language queries to interact with MongoDB databases.

## 📋 Overview

This solution provides:
1. **MCP Client Connector** - Connects to MongoDB MCP server using the Model Context Protocol
2. **Natural Language Query Converter** - Converts natural language queries into MongoDB operations
3. **Search Interface** - Unified interface to fetch and update database content using natural language

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Natural Language Query                    │
│              "Find all users where age > 25"                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  Search Interface                           │
│  • Converts NL to MongoDB operations                        │
│  • Routes to appropriate MCP client methods                 │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                  MCP Client Connector                       │
│  • Communicates with MongoDB MCP Server                     │
│  • Handles JSON-RPC protocol                                │
│  • Manages connection lifecycle                             │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              MongoDB MCP Server                              │
│  • Executes MongoDB operations                              │
│  • Returns results via MCP protocol                         │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                    MongoDB Database                          │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
mcp-mongodb-search/
├── real_mcp_client.py     # Real MCP client connector for MongoDB MCP server
├── mcp_server.py           # MCP server implementation (Python-based)
├── real_search_interface.py # Search interface with AI integration
├── ai_query_converter.py   # Azure OpenAI query converter
├── nl_query_converter.py   # Regex-based query converter (fallback)
├── web_app.py              # Main Flask web application
├── config.py               # Configuration management
├── requirements.txt        # Python dependencies
├── static/                 # Web UI static files (CSS, JS)
├── templates/              # Web UI templates (HTML)
├── create_sample_data.py   # Script to create sample data
├── init_database.py         # Script to initialize database
├── test_connection.py       # Script to test MongoDB connection
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites

1. **MongoDB** - Running MongoDB instance or MongoDB Atlas connection
2. **Node.js** - For running MongoDB MCP server (if using official server)
3. **Python 3.8+** - For running the client application

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd mcp-mongodb-search
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install MongoDB MCP Server (if using official server):**
```bash
npm install -g @modelcontextprotocol/server-mongodb
```

4. **Configure environment variables:**
```bash
# Copy example file
cp .env.example .env

# Edit .env with your actual credentials
# Required: MongoDB connection string and database name
# Required: Azure OpenAI endpoint, API key, and deployment name
```

**Environment Variables** (see `.env.example`):
- `MONGODB_CONNECTION_STRING` - MongoDB connection string (required)
- `MONGODB_DATABASE` - Database name (required)
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint (required for AI)
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key (required for AI)
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` - Deployment name (required for AI)
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-06-01)
- `AZURE_OPENAI_MODEL` - Model name (default: gpt-4o)

### Running the Application

```bash
python web_app.py
```

The application will:
1. Initialize the MCP client connection
2. Set up the search interface
3. Run example queries
4. Enter interactive mode for custom queries

## 💡 Usage Examples

### Running the Web Application

The easiest way to use this solution is through the web UI:

```bash
python web_app.py
```

Then open your browser to `http://localhost:5000` and enter natural language queries like:
- "find all users where age is greater than 25"
- "get products from products collection where price is less than 100"
- "insert new user with name John and age 28"
- "show first 5 documents from orders collection"

### Using the Python API

```python
from real_mcp_client import RealMongoMCPClient
from real_search_interface import RealSearchInterface

# Initialize MCP client
client = RealMongoMCPClient(
    connection_string="mongodb://localhost:27017",
    database_name="PeerGenAI_practice_db"
)
client.connect()

# Create search interface with Azure OpenAI
search = RealSearchInterface(
    mcp_client=client,
    azure_endpoint="https://your-endpoint.openai.azure.com/",
    azure_api_key="your-api-key",
    azure_deployment_name="your-deployment"
)

# Execute natural language query
result = search.process_query("find all users where age is greater than 25")
print(result)
```

### Example 2: Insert Operation

```python
# Insert data using natural language
result = search.process_query("insert new user with name Alice and age 30")
print(result)
```

### Example 3: Update Operation

```python
# Update data using natural language
result = search.process_query("update users set status to active where name is Alice")
print(result)
```

### Example 4: Delete Operation

```python
# Delete data using natural language
result = search.process_query("delete users where age is less than 18")
print(result)
```
result = app.search("find products where price is less than 100")
print(result)

# Update
result = app.update("update products set discount to 10 where category is electronics")
print(result)
```

## 🔧 Components

### 1. MCP Client Connector (`mcp_client.py`)

The `MCPClient` class provides:
- Connection management to MongoDB MCP server
- JSON-RPC protocol communication
- Tool calling (query, update, insert, delete)
- Resource management

The `MongoMCPClient` class extends this with MongoDB-specific operations:
- `query_database()` - Query MongoDB collections
- `update_database()` - Update documents
- `insert_document()` - Insert new documents
- `delete_documents()` - Delete documents

### 2. Natural Language Query Converter (`nl_query_converter.py`)

The `NLQueryConverter` class:
- Detects operation type (find, update, insert, delete)
- Extracts collection names from queries
- Parses filter conditions
- Converts natural language to MongoDB query format

**Supported Query Patterns:**
- "find all users where age is greater than 25"
- "update users collection set status to active where age is 30"
- "insert new user with name John and age 25"
- "delete users where status is inactive"

### 3. Search Interface (`search_interface.py`)

The `SearchInterface` class:
- Connects natural language queries to MCP client
- Routes operations to appropriate handlers
- Provides `fetch_data()` and `update_data()` methods
- Handles errors and returns structured results

## 📝 Supported Query Types

### Find/Search Queries
- "find all users"
- "search for products where price is less than 100"
- "get documents from orders collection"
- "show first 5 users"
- "list products where category is electronics"

### Update Queries
- "update users set status to active where age is 30"
- "change product price to 50 where id is 123"
- "modify user email to new@example.com where name is John"

### Insert Queries
- "insert new user with name John and age 25"
- "add product {name: 'Widget', price: 29.99}"
- "create user in users collection"

### Delete Queries
- "delete users where status is inactive"
- "remove products where price is 0"
- "clear all documents from temp collection"

## 🔌 MCP Protocol Integration

The solution uses the Model Context Protocol (MCP) to communicate with the MongoDB MCP server:

### MCP Methods Used

1. **initialize** - Initialize connection with server
2. **tools/list** - List available MongoDB tools
3. **tools/call** - Execute MongoDB operations
4. **resources/list** - List available resources
5. **resources/read** - Read resources

### MongoDB Tools

- `mongodb_query` - Query documents
- `mongodb_update` - Update documents
- `mongodb_insert` - Insert documents
- `mongodb_delete` - Delete documents

## ⚙️ Configuration

### Environment Variables

The project uses environment variables for configuration. A `.env.example` file is provided as a template.

**Setup**:
```bash
# Copy example file
cp .env.example .env

# Edit .env with your actual credentials
nano .env  # or use your preferred editor
```

**Required Variables**:
- `MONGODB_CONNECTION_STRING` - MongoDB connection string
  - Local: `mongodb://localhost:27017`
  - Atlas: `mongodb+srv://username:password@cluster.mongodb.net/`
- `MONGODB_DATABASE` - Database name
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` - Deployment name

**Optional Variables**:
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-06-01)
- `AZURE_OPENAI_MODEL` - Model name (default: gpt-4o)
- `LOG_LEVEL` - Logging level (default: INFO)
- `DEFAULT_QUERY_LIMIT` - Default query limit (default: 10)
- `PORT` - Server port (default: 5000)
- `FLASK_DEBUG` - Debug mode (default: False)

See `.env.example` for the complete template with all available options.

## 🧪 Testing

Run example queries:

```bash
python web_app.py
```

The application includes several example queries demonstrating:
- Finding documents with filters
- Updating documents
- Different collection queries
- Limit operations

## 📚 API Reference

### MCPMongoDBSearchApp

Main application class.

**Methods:**
- `initialize()` - Initialize MCP client and search interface
- `search(query)` - Execute search query
- `update(query)` - Execute update query
- `process_query(query)` - Process any type of query

### SearchInterface

Search interface for natural language queries.

**Methods:**
- `process_query(query)` - Process and execute query
- `fetch_data(query, collection=None)` - Fetch data
- `update_data(query, collection=None)` - Update data

### MongoMCPClient

MongoDB MCP client connector.

**Methods:**
- `connect()` - Connect to MCP server
- `query_database(collection, query, limit)` - Query database
- `update_database(collection, filter_query, update_operation)` - Update database
- `insert_document(collection, document)` - Insert document
- `delete_documents(collection, filter_query)` - Delete documents

## 🔒 Security Considerations

1. **Connection Strings** - Store MongoDB connection strings securely (use environment variables)
2. **Authentication** - Ensure MongoDB authentication is properly configured
3. **Query Validation** - Validate natural language queries before execution
4. **Access Control** - Implement proper access control for database operations

## 🐛 Troubleshooting

### Connection Issues

If you encounter connection issues:
1. Verify MongoDB is running
2. Check connection string format
3. Ensure MongoDB MCP server is installed and running
4. Check network connectivity

### Query Parsing Issues

If queries aren't parsed correctly:
1. Use more explicit query syntax
2. Specify collection names explicitly
3. Check query format matches supported patterns

## 📄 License

MIT License - Feel free to use and modify for your projects.

## 🙏 Credits

- **Model Context Protocol** - Protocol for AI-tool integration
- **MongoDB** - NoSQL database
- **Python** - Programming language

## 🎯 Summary

This solution provides a complete implementation of:
1. ✅ MCP client connector to MongoDB MCP server
2. ✅ Search interface connecting to MCP client
3. ✅ Natural language to MongoDB query conversion
4. ✅ Fetch and update database content functionality

The solution is ready to use and can be extended with additional features like:
- Advanced NLP for better query understanding
- Query caching
- Result pagination
- Batch operations
- Transaction support

