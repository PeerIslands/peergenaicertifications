# 🤖 LangGraph Chatbot POC

A smart chatbot that intelligently routes queries between specialized **tools** and **AI** using LangGraph for state management.

## ✨ Features

- 🔄 **LangGraph State Management** - Maintains conversation context
- 🧠 **AI-Powered Routing** - Intelligently decides tool vs LLM
- 🛠️ **6 Specialized Tools** - Calculator, Weather, Time/Date, Unit Converter, Wikipedia, Translation
- 📊 **Source Attribution** - See where each response came from
- 🎨 **Modern Web UI** - Beautiful, responsive interface with dark mode
- 💾 **Conversation Export** - Download chat history

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd langgraph-chatbot-poc
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# Required: Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_API_VERSION=2024-06-01
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your-deployment-name
AZURE_OPENAI_MODEL=gpt-4o

# Optional: Weather API
OPENWEATHERMAP_API_KEY=your-weather-api-key
```

### 3. Run the Application

```bash
python app.py
```

Visit `http://localhost:5002` in your browser.

## 📋 Requirements

- Python 3.8+
- Azure OpenAI API key (or OpenAI API key as fallback)
- OpenWeatherMap API key (optional, for weather tool)

## 🎯 How It Works

1. **User sends message** → Flask receives request
2. **LangGraph processes** → Routes to tool or LLM
3. **AI decides** → Analyzes query and extracts parameters
4. **Tool/LLM executes** → Generates response
5. **State updated** → Conversation history maintained
6. **Response returned** → With source attribution

## 🛠️ Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| 🔢 **Calculator** | Mathematical calculations | "calculate 25 * 4 + 10" |
| 🌤️ **Weather** | Weather information | "weather in London" |
| 🕐 **Time/Date** | Current time/date | "what time is it" |
| 📏 **Unit Converter** | Unit conversions | "convert 100 km to miles" |
| 📚 **Wikipedia** | Search Wikipedia | "wikipedia artificial intelligence" |
| 🌐 **Translation** | Language translation | "translate hello to spanish" |

## 📁 Project Structure

```
langgraph-chatbot-poc/
├── app.py                 # Flask web application
├── chatbot.py            # LangGraph state graph & routing
├── tools.py              # Tool implementations
├── config.py             # Configuration management
├── templates/            # HTML templates
│   └── index.html
├── static/               # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── requirements.txt      # Python dependencies
```

## 🏗️ Architecture

```
User → Flask API → LangGraph → Router → Tools/LLM → Response
                      ↓
                  State Management
```

- **LangGraph**: Manages conversation state and workflow
- **AI Router**: Decides tool vs LLM using Azure OpenAI
- **Tools**: Specialized functions for specific tasks
- **LLM**: Handles general queries and conversations

## 💡 Example Queries

**Calculator:**
- "calculate 25 * 4 + 10"
- "what is 100 / 5"
- "compute 22412435 % 343 - 2"

**Weather:**
- "what's the weather in New York"
- "temperature in London"
- "weather in andhra pradesh"

**Time/Date:**
- "what time is it"
- "current date"
- "what day is it"

**Unit Converter:**
- "convert 100 km to miles"
- "50 celsius to fahrenheit"
- "10 kg to pounds"

**Wikipedia:**
- "wikipedia artificial intelligence"
- "search wikipedia for python"

**Translation:**
- "translate hello to spanish"
- "translate bonjour to english"

**General (LLM):**
- "what is machine learning"
- "explain quantum computing"
- "tell me a joke"

## 📊 Response Sources

Each response shows its source:

- 🔧 **Tool** - Response from a specialized tool
- 🤖 **LLM** - Response from AI language model

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI endpoint | Yes |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | Yes |
| `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` | Deployment name | Yes |
| `AZURE_OPENAI_MODEL` | Model name (default: gpt-4o) | No |
| `OPENWEATHERMAP_API_KEY` | Weather API key | No |
| `FLASK_PORT` | Server port (default: 5002) | No |

## 📚 Documentation

- **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** - Detailed technical documentation
- **[REQUIREMENTS_CHECKLIST.md](REQUIREMENTS_CHECKLIST.md)** - Requirements fulfillment

## 🎨 UI Features

- **Dark Mode** - Toggle between light/dark themes
- **Source Attribution** - Visual badges showing response source
- **Export Conversations** - Download chat history as text
- **Example Queries** - Clickable examples for each tool
- **Message Counter** - Track conversation length
- **Responsive Design** - Works on desktop and mobile

## 🔍 Key Technologies

- **LangGraph** - Stateful workflow management
- **LangChain** - Tool definitions and LLM integration
- **Azure OpenAI** - GPT-4o for routing and responses
- **Flask** - Web framework
- **Pydantic** - Data validation

## ✅ Requirements Met

- ✅ LangGraph with state management
- ✅ Intelligent tool vs LLM routing
- ✅ Multiple specialized tools
- ✅ Source attribution for responses
- ✅ Modern web interface

## 🐛 Troubleshooting

**Issue: Import errors**
```bash
pip install -r requirements.txt
```

**Issue: Azure OpenAI connection failed**
- Check your `.env` file has correct credentials
- Verify endpoint URL ends with `/`
- Ensure deployment name is correct

**Issue: Weather tool not working**
- Weather tool is optional
- Add `OPENWEATHERMAP_API_KEY` to `.env` if needed
- Get free API key: https://home.openweathermap.org/users/sign_up

## 📝 License

This is a proof-of-concept project for educational purposes.

## 🤝 Contributing

This is a POC project. Feel free to fork and extend!

---

**Built with ❤️ using LangGraph, LangChain, and Azure OpenAI**
