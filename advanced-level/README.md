# 🚀 Advanced Level Projects

This folder contains advanced AI-powered solutions demonstrating cutting-edge techniques in code modernization, agentic frameworks, and intelligent systems.

## 📁 Projects Overview

| Project | Description | Technology | Status |
|---------|-------------|------------|--------|
| **code-modernization-tool** | Reusable AI tool for modernizing legacy codebases | Python, FastAPI, AI | ✅ Complete |
| **java-to-python-modernization** | Specific modernization: Java Spring Boot → Python FastAPI | Python, FastAPI, SQLAlchemy | ✅ Complete |
| **langgraph-chatbot-poc** | Intelligent chatbot with LangGraph state management | LangGraph, LangChain, FastAPI | ✅ Complete |
| **mcp-mongodb-search** | MCP-based natural language MongoDB search solution | MCP, MongoDB, Azure OpenAI | ✅ Complete |

---

## 1. 🔧 Code Modernization Tool

**Location**: `code-modernization-tool/`

### Overview

A **reusable AI-powered framework** for automatically modernizing legacy codebases while preserving original code. This is the **general-purpose tool** that can modernize any codebase.

### Key Features

- 🔍 **AI-Powered Analysis** - Deep code structure and pattern analysis
- 🔄 **Automated Conversion** - Convert legacy code to modern stacks
- 🧪 **Test Generation** - Auto-generate test suites with 80%+ coverage
- 📚 **Auto Documentation** - Generate comprehensive documentation
- 💾 **Original Preservation** - Keep original code intact

### Technology Stack

- **Language**: Python 3.11+
- **AI**: Azure OpenAI GPT-4o / OpenAI
- **Frameworks**: LangChain, Pydantic
- **Analysis**: Tree-sitter, Pattern recognition

### Quick Start

```bash
cd code-modernization-tool
pip install -r requirements.txt
python -m src.main --source /path/to/legacy/code --target python --framework fastapi
```

### Use Cases

- Modernize any legacy codebase
- Convert between technology stacks
- Generate comprehensive documentation
- Create test suites automatically

### Documentation

- [README](code-modernization-tool/README.md) - Main documentation
- [Usage Guide](code-modernization-tool/USAGE.md) - How to use the tool
- [Architecture](code-modernization-tool/ARCHITECTURE.md) - Technical architecture

---

## 2. ☕→🐍 Java to Python Modernization

**Location**: `java-to-python-modernization/`

### Overview

A **specific implementation** of code modernization: converting a legacy Java Spring Boot REST API to modern Python FastAPI. This is the **actual modernization project** that demonstrates the tool's capabilities.

### Key Features

- ✅ **100% Feature Parity** - All endpoints and functionality preserved
- ✅ **95.67% Test Coverage** - Comprehensive test suite (exceeds 80% target)
- ✅ **Auto-generated API Docs** - OpenAPI/Swagger documentation
- ✅ **Modern Tech Stack** - FastAPI, SQLAlchemy, Pydantic
- ✅ **Type Safety** - Full Python type hints

### Technology Stack

| Legacy (Java) | Modern (Python) |
|---------------|-----------------|
| Spring Boot 2.7.18 | FastAPI 0.104+ |
| Java 8 | Python 3.11+ |
| Spring Data JPA | SQLAlchemy 2.0+ |
| H2 In-Memory | SQLite/PostgreSQL |
| Bean Validation | Pydantic v2 |

### Relationship to Code Modernization Tool

- **code-modernization-tool**: The reusable framework/tool
- **java-to-python-modernization**: Specific implementation using the tool's approach

Both demonstrate the same modernization process, but:
- **Tool**: General-purpose, can modernize any codebase
- **This Project**: Specific Java→Python conversion with complete implementation

### Quick Start

```bash
cd java-to-python-modernization
pip install -r requirements.txt
python main.py
# Visit http://localhost:8000/docs
```

### API Endpoints

- `GET /api/users` - Get all users
- `GET /api/users/{id}` - Get user by ID
- `GET /api/users/email/{email}` - Get user by email
- `POST /api/users` - Create user
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user
- `GET /health` - Health check

### Documentation

- [README](java-to-python-modernization/README.md) - Main documentation
- [Legacy Code Analysis](java-to-python-modernization/docs/LEGACY_CODE_ANALYSIS.md) - Original code analysis
- [Modernization Plan](java-to-python-modernization/docs/MODERNIZATION_PLAN.md) - Conversion strategy
- [AI Process](java-to-python-modernization/docs/AI_MODERNIZATION_PROCESS.md) - How AI was used
- [Modernization Summary](java-to-python-modernization/docs/MODERNIZATION_SUMMARY.md) - Project summary

---

## 3. 🤖 LangGraph Chatbot POC

**Location**: `langgraph-chatbot-poc/`

### Overview

An intelligent chatbot that uses **LangGraph** for state management and **AI-powered routing** to intelligently decide between specialized tools and LLM responses.

### Key Features

- 🔄 **LangGraph State Management** - Maintains conversation context
- 🧠 **AI-Powered Routing** - Intelligently routes queries to tools or LLM
- 🛠️ **6 Specialized Tools** - Calculator, Weather, Time/Date, Unit Converter, Wikipedia, Translation
- 📊 **Source Attribution** - Shows where each response came from
- 🎨 **Modern Web UI** - Beautiful interface with dark mode

### Technology Stack

- **Framework**: LangGraph, LangChain
- **AI**: Azure OpenAI GPT-4o
- **Web**: Flask
- **Tools**: 6 specialized tools with structured inputs

### Architecture

```
User Query
    ↓
LangGraph Router (AI-powered)
    ↓
    ├─→ Tools (Calculator, Weather, etc.)
    └─→ LLM (General queries)
    ↓
Response with Source Attribution
```

### Quick Start

```bash
cd langgraph-chatbot-poc
pip install -r requirements.txt
python app.py
# Visit http://localhost:5002
```

### Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| 🔢 Calculator | Math operations | "calculate 25 * 4 + 10" |
| 🌤️ Weather | Weather info | "weather in London" |
| 🕐 Time/Date | Current time | "what time is it" |
| 📏 Unit Converter | Unit conversions | "convert 100 km to miles" |
| 📚 Wikipedia | Search Wikipedia | "wikipedia AI" |
| 🌐 Translation | Language translation | "translate hello to spanish" |

### Documentation

- [README](langgraph-chatbot-poc/README.md) - Main documentation
- [Implementation Guide](langgraph-chatbot-poc/IMPLEMENTATION_GUIDE.md) - Detailed technical guide
- [Requirements Checklist](langgraph-chatbot-poc/REQUIREMENTS_CHECKLIST.md) - Requirements fulfillment

---

## 4. 🔍 MCP MongoDB Search

**Location**: `mcp-mongodb-search/`

### Overview

A **Model Context Protocol (MCP)** based solution for natural language MongoDB queries. Converts natural language to MongoDB operations using AI.

### Key Features

- 🔌 **MCP Protocol** - Custom Python MCP server implementation
- 🤖 **AI Query Conversion** - Natural language → MongoDB operations
- 🔄 **Full CRUD Support** - Query, Insert, Update, Delete operations
- 🌐 **Web Interface** - User-friendly search interface
- 📊 **Real-time Results** - Instant query execution and results

### Technology Stack

- **Protocol**: Model Context Protocol (MCP)
- **Database**: MongoDB
- **AI**: Azure OpenAI GPT-4o
- **Web**: Flask
- **Communication**: JSON-RPC 2.0

### Architecture

```
User Query (Natural Language)
    ↓
Search Interface (AI Converter)
    ↓
MCP Client Connector
    ↓
MCP Server (Python)
    ↓
MongoDB Database
    ↓
Results
```

### Quick Start

```bash
cd mcp-mongodb-search
pip install -r requirements.txt
# Configure MongoDB connection in .env
python web_app.py
# Visit http://localhost:5000
```

### Supported Operations

- **Query**: "Find all users with age > 25"
- **Insert**: "Add a new user named John"
- **Update**: "Update user email to new@example.com"
- **Delete**: "Delete user with id 123"

### Documentation

- [README](mcp-mongodb-search/README.md) - Main documentation
- [Implementation Guide](mcp-mongodb-search/IMPLEMENTATION_GUIDE.md) - Technical implementation details

---

## 🎯 Project Relationships

### Code Modernization Projects

```
code-modernization-tool (Reusable Framework)
         ↓
         ├─→ Can modernize any codebase
         └─→ Demonstrates general approach
         
java-to-python-modernization (Specific Implementation)
         ↓
         ├─→ Uses same modernization approach
         └─→ Complete Java→Python conversion
```

**Key Difference**:
- **Tool**: General-purpose, reusable framework
- **Project**: Specific implementation with full codebase

### AI-Powered Solutions

Both **LangGraph Chatbot** and **MCP MongoDB Search** demonstrate:
- AI-powered decision making
- Natural language processing
- Tool/LLM integration
- Real-world AI applications

---

## 📊 Comparison Matrix

| Feature | Code Modernization Tool | Java→Python | LangGraph Chatbot | MCP MongoDB |
|---------|------------------------|-------------|-------------------|-------------|
| **Purpose** | Reusable tool | Specific conversion | Intelligent chatbot | NL MongoDB search |
| **AI Usage** | Code analysis & conversion | Code conversion | Routing & responses | Query conversion |
| **Framework** | CLI Tool | FastAPI | LangGraph/Flask | MCP/Flask |
| **Test Coverage** | Generated | 95.67% | N/A | N/A |
| **Port** | N/A | 8000 | 5002 | 5000 |
| **Original Code** | Preserved | In `legacy_analysis/` | N/A | N/A |

---

## 🚀 Quick Start Guide

### Running All Projects Simultaneously

All projects can run simultaneously on different ports:

```bash
# Terminal 1: MCP MongoDB Search
cd mcp-mongodb-search
python web_app.py
# http://localhost:5000

# Terminal 2: LangGraph Chatbot
cd langgraph-chatbot-poc
python app.py
# http://localhost:5002

# Terminal 3: Java→Python Modernization
cd java-to-python-modernization
python main.py
# http://localhost:8000

# Terminal 4: Code Modernization Tool (CLI)
cd code-modernization-tool
python -m src.main --source /path/to/code --target python
```

### Port Summary

| Project | Port | URL |
|---------|------|-----|
| MCP MongoDB Search | 5000 | http://localhost:5000 |
| LangGraph Chatbot | 5002 | http://localhost:5002 |
| Java→Python API | 8000 | http://localhost:8000 |

---

## 📚 Documentation Index

### Code Modernization

- [Code Modernization Tool README](code-modernization-tool/README.md)
- [Code Modernization Tool Usage](code-modernization-tool/USAGE.md)
- [Java→Python README](java-to-python-modernization/README.md)
- [Java→Python Legacy Analysis](java-to-python-modernization/docs/LEGACY_CODE_ANALYSIS.md)
- [Java→Python Modernization Plan](java-to-python-modernization/docs/MODERNIZATION_PLAN.md)

### AI Solutions

- [LangGraph Chatbot README](langgraph-chatbot-poc/README.md)
- [LangGraph Implementation Guide](langgraph-chatbot-poc/IMPLEMENTATION_GUIDE.md)
- [MCP MongoDB README](mcp-mongodb-search/README.md)
- [MCP MongoDB Implementation Guide](mcp-mongodb-search/IMPLEMENTATION_GUIDE.md)

---

## 🎓 Learning Outcomes

These projects demonstrate:

1. **AI-Powered Code Analysis** - Understanding legacy codebases
2. **Automated Code Conversion** - Modernizing technology stacks
3. **State Management** - LangGraph for complex workflows
4. **AI Routing** - Intelligent tool vs LLM decisions
5. **Protocol Implementation** - Custom MCP server
6. **Natural Language Processing** - Converting NL to operations
7. **Test Generation** - Automated test suite creation
8. **Documentation Generation** - AI-powered documentation

---

## ✅ Requirements Fulfillment

### Code Modernization
- ✅ Extract functionality from legacy code
- ✅ Auto-generate documentation using AI
- ✅ Convert to modern technology stack
- ✅ Generate tests with 80%+ coverage
- ✅ Preserve original code

### LangGraph Chatbot
- ✅ LangGraph with state management
- ✅ Intelligent tool vs LLM routing
- ✅ Multiple specialized tools
- ✅ Source attribution

### MCP MongoDB Search
- ✅ MCP-based search solution
- ✅ MCP client connector
- ✅ Natural language query conversion
- ✅ Full CRUD operations

---

## 🔧 Common Setup

### Prerequisites

- Python 3.11+
- MongoDB (for MCP MongoDB Search)
- Azure OpenAI API key (or OpenAI API key)

### Environment Variables

All projects use `.env` files. See each project's README for specific configuration.

**Common variables**:
```env
# Azure OpenAI (Preferred)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-deployment

# MongoDB (for MCP MongoDB Search)
MONGODB_CONNECTION_STRING=mongodb://localhost:27017
MONGODB_DATABASE=your-database
```

---

## 📈 Project Statistics

| Project | Files | Test Coverage | Documentation |
|---------|-------|---------------|----------------|
| Code Modernization Tool | 10+ Python files | N/A (Tool) | 4 docs |
| Java→Python | 20 Python files | 95.67% | 4 docs |
| LangGraph Chatbot | 8 Python files | N/A | 2 docs |
| MCP MongoDB | 10+ Python files | N/A | 2 docs |

---

## 🎯 Use Cases

### Code Modernization Tool
- Modernize legacy Java applications
- Convert C# to Python
- Migrate between frameworks
- Generate documentation for any codebase

### Java→Python Modernization
- Reference implementation
- Learning example
- Production-ready API
- Test coverage example

### LangGraph Chatbot
- Customer support chatbot
- Multi-tool assistant
- Stateful conversations
- AI routing examples

### MCP MongoDB Search
- Natural language database queries
- MCP protocol implementation
- AI-powered data access
- Search interface examples

---

## 🤝 Contributing

These are advanced-level demonstration projects. Each project includes:
- Complete source code
- Comprehensive documentation
- Test suites (where applicable)
- Usage examples

---

## 📝 Notes

- **Original Code Preservation**: Code modernization projects preserve original code
- **AI-Powered**: All projects use AI (Azure OpenAI/OpenAI) for intelligent operations
- **Production Ready**: All projects are functional and can be deployed
- **Well Documented**: Comprehensive documentation for each project

---

**Built with ❤️ using AI, LangGraph, MCP, and modern Python frameworks**

