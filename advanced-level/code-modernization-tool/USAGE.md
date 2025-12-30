# Code Modernization Tool - Usage Guide

## Quick Start

### 1. Setup

```bash
cd code-modernization-tool
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 2. Basic Usage

```bash
# Modernize a Java codebase to Python FastAPI
python -m src.main \
  --source /path/to/java/code \
  --target python \
  --framework fastapi \
  --output ./output
```

## Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `--source`, `-s` | Path to source code directory | Required |
| `--target`, `-t` | Target language (python, typescript) | python |
| `--framework`, `-f` | Target framework (fastapi, flask) | fastapi |
| `--output`, `-o` | Output directory | ./output |
| `--preserve-original` | Keep original code in output | True |
| `--coverage`, `-c` | Target test coverage % | 80 |
| `--ai-model` | AI model to use | gpt-4o |

## Example Workflows

### Example 1: Modernize Java Spring Boot

```bash
python -m src.main \
  --source ../temp_repo/src/main/java \
  --target python \
  --framework fastapi \
  --output ./modernized-java-app \
  --coverage 85
```

**Output Structure:**
```
modernized-java-app/
├── original_code/        # Original Java code (preserved)
├── modernized_code/     # Converted Python code
├── tests/              # Generated test suite
└── docs/               # Auto-generated documentation
```

### Example 2: Modernize with Custom Settings

```bash
python -m src.main \
  --source ./legacy-project \
  --target python \
  --framework flask \
  --output ./flask-version \
  --coverage 90 \
  --ai-model gpt-4o
```

## Output Structure

After running the tool, you'll get:

```
output/
├── original_code/          # Original source code (preserved)
│   └── [original structure]
├── modernized_code/        # Modernized code
│   ├── src/
│   ├── main.py
│   └── requirements.txt
├── tests/                  # Generated test suite
│   ├── src/tests/
│   └── pytest.ini
└── docs/                   # Documentation
    ├── LEGACY_CODE_ANALYSIS.md
    ├── MODERNIZATION_PLAN.md
    ├── MODERNIZATION_SUMMARY.md
    └── CODE_MAPPING.md
```

## Features

### ✅ What It Does

1. **Analyzes** legacy code structure and patterns
2. **Generates** comprehensive documentation
3. **Converts** code to modern technology stack
4. **Creates** test suites with target coverage
5. **Preserves** original code intact

### 🔧 Configuration

Set environment variables in `.env`:

```env
# Azure OpenAI (Preferred)
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-deployment

# OR OpenAI (Fallback)
OPENAI_API_KEY=your-key
```

## Troubleshooting

### Issue: LLM not configured
**Solution**: Set API keys in `.env` file

### Issue: Source path not found
**Solution**: Use absolute path or check path exists

### Issue: Low test coverage
**Solution**: Increase `--coverage` target or review generated tests

## Next Steps

After modernization:

1. Review generated documentation in `docs/`
2. Check modernized code in `modernized_code/`
3. Run tests: `cd output/modernized_code && pytest`
4. Compare with original in `original_code/`

---

**Note**: This tool preserves original code. The modernized version is in `modernized_code/` directory.

