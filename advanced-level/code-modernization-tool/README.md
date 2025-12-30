# 🔧 Code Modernization Tool

An AI-powered tool for automatically modernizing legacy codebases while preserving the original code.

## 🎯 Overview

This tool provides an automated framework for:
- **Analyzing** legacy codebases
- **Generating** comprehensive documentation
- **Converting** code to modern technology stacks
- **Creating** test suites with high coverage
- **Preserving** original code intact

## ✨ Features

- 🔍 **Code Analysis** - Deep analysis of legacy code structure, patterns, and dependencies
- 📚 **Auto Documentation** - Generate comprehensive documentation using AI
- 🔄 **Code Conversion** - Convert to modern stacks (Java→Python, etc.)
- 🧪 **Test Generation** - Auto-generate test suites with 80%+ coverage
- 💾 **Original Preservation** - Keep original code untouched
- 🎨 **Multiple Targets** - Support for various modernization targets

## 🚀 Quick Start

### Installation

```bash
cd code-modernization-tool
pip install -r requirements.txt
```

### Basic Usage

```bash
# Analyze and modernize a codebase
python -m src.main --source /path/to/legacy/code --target python --output ./output

# Modernize Java Spring Boot to Python FastAPI
python -m src.main --source ../temp_repo --target python --framework fastapi --output ./modernized

# With custom test coverage target
python -m src.main --source ./legacy-code --target python --framework fastapi --coverage 90 --output ./output
```

### Example: Using Existing Java Project

```bash
# Modernize the Java REST API from temp_repo
python -m src.main \
  --source ../temp_repo/src/main/java \
  --target python \
  --framework fastapi \
  --output ./output/java-modernized \
  --preserve-original \
  --coverage 80
```

## 📋 Supported Conversions

| Source | Target | Framework | Status |
|--------|--------|-----------|--------|
| Java | Python | FastAPI | ✅ Supported |
| Java | Python | Flask | 🚧 Planned |
| Java | TypeScript | Express | 🚧 Planned |
| C# | Python | FastAPI | 🚧 Planned |

## 🏗️ Architecture

```
code-modernization-tool/
├── src/
│   ├── analyzer/          # Code analysis engine
│   ├── converter/         # Code conversion engine
│   ├── test_generator/    # Test generation engine
│   └── documentation/     # Documentation generator
├── templates/            # Code templates
├── output/               # Generated modernized code
└── examples/            # Example projects
```

## 🔧 Configuration

Create a `config.yaml` file:

```yaml
source:
  language: java
  framework: spring-boot
  path: ./legacy-code

target:
  language: python
  framework: fastapi
  version: 3.11+

modernization:
  preserve_original: true
  test_coverage: 80
  generate_docs: true
  ai_model: gpt-4o
```

## 📚 Documentation

- [User Guide](docs/USER_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Examples](examples/)

## 🤝 Contributing

This is a tool for automated code modernization. Contributions welcome!

---

**Built with AI-powered code analysis and conversion**

