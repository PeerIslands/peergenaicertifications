# AI Certification Projects

This repository contains AI-powered projects demonstrating advanced techniques in code modernization, agentic frameworks, and intelligent systems.

## 📁 Project Structure

### 🔍 Foundational Level

#### RAG Document Explorer

The complete codebase for the **RAG (Retrieval-Augmented Generation) SPA** is located in:

```
📂 rag-app-foundational/
```

**Built with:** LangChain • FAISS • Azure OpenAI (GPT-4o) • Flask • Deployed on Replit

🎬 **[Watch Demo Video](https://peerislandsio.sharepoint.com/:v:/s/Certifications/IQDWrMthLPvpRIEiGYZCjb98AVURbhumT-LQrCIfsTuwre0?nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D&e=yhyUyz)**

➡️ See [`rag-app-foundational/README.md`](rag-app-foundational/README.md) for full documentation.

---

### 🚀 Advanced Level

The **advanced-level** folder contains four sophisticated AI-powered solutions:

```
📂 advanced-level/
├── code-modernization-tool/      # Reusable AI tool for code modernization
├── java-to-python-modernization/ # Java Spring Boot → Python FastAPI conversion
├── langgraph-chatbot-poc/        # Intelligent chatbot with LangGraph
└── mcp-mongodb-search/          # MCP-based natural language MongoDB search
```

#### 📋 Projects Overview

| Project | Description | Port | Status |
|---------|-------------|------|--------|
| **Code Modernization Tool** | Reusable AI framework for modernizing any codebase | CLI | ✅ Complete |
| **Java→Python Modernization** | Specific Java Spring Boot to Python FastAPI conversion | 8000 | ✅ Complete |
| **LangGraph Chatbot** | AI-powered chatbot with tool routing and state management | 5002 | ✅ Complete |
| **MCP MongoDB Search** | Natural language MongoDB queries using MCP protocol | 5000 | ✅ Complete |

#### 🎯 Key Features

**Code Modernization:**
- ✅ AI-powered code analysis and conversion
- ✅ Auto-generated documentation
- ✅ Test suite generation (95.67% coverage)
- ✅ Original code preservation

**LangGraph Chatbot:**
- ✅ Intelligent tool vs LLM routing
- ✅ 6 specialized tools (Calculator, Weather, etc.)
- ✅ State management with LangGraph
- ✅ Source attribution

**MCP MongoDB Search:**
- ✅ Custom MCP server implementation
- ✅ Natural language to MongoDB conversion
- ✅ Full CRUD operations
- ✅ Web-based search interface

➡️ **See [`advanced-level/README.md`](advanced-level/README.md) for comprehensive documentation of all advanced projects.**

---

### 📄 Resources

#### Sample PDFs

Research papers used for RAG ingestion are in:

```
📂 pdfs/
```

---

## 🚀 Quick Start

### Foundational Project

```bash
cd rag-app-foundational
pip install -r requirements.txt
python app.py
```

### Advanced Projects

All advanced projects can run simultaneously:

```bash
# Terminal 1: MCP MongoDB Search (Port 5000)
cd advanced-level/mcp-mongodb-search
python web_app.py

# Terminal 2: LangGraph Chatbot (Port 5002)
cd advanced-level/langgraph-chatbot-poc
python app.py

# Terminal 3: Java→Python API (Port 8000)
cd advanced-level/java-to-python-modernization
python main.py

# Terminal 4: Code Modernization Tool (CLI)
cd advanced-level/code-modernization-tool
python -m src.main --source /path/to/code --target python
```

---

## 📚 Documentation

- **Foundational**: [`rag-app-foundational/README.md`](rag-app-foundational/README.md)
- **Advanced Level**: [`advanced-level/README.md`](advanced-level/README.md)

---

*Built with ❤️ using AI, LangGraph, MCP, RAG, LangChain, Azure OpenAI & modern Python frameworks*

