# AI Career Advisor (Groq + LangChain RAG)

This project provides an AI Career Advisor powered by Groq and LangChain's Retrieval-Augmented Generation (RAG) system. The backend is a Flask server that processes chat messages, retrieves context from PDF documents, and generates responses using the Llama 3.1 8B Instant model.

## ⚙️ Prerequisites

* Python 3.8+
* A Groq API Key

## 🛠️ Local Setup and Installation

Follow these steps to set up the project and run it locally.

### 1. Clone the Repository

```bash
git clone <your-repo-link>
cd <your-repo-name>

2. Create a Virtual Environment
python -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (Command Prompt):
# venv\Scripts\activate

3. Install Dependencies

pip install -r requirements.txt

4. Configure Environment Variables

# .env file (inside backend)
GROQ_API_KEY="your-groq-api-key-here"

5. Add PDF Documents (RAG Context)

Place the PDF documents you want the advisor to reference into the backend/pdfs folder.

▶️ Running the Application

# 1. Activate venv (if not already)
source venv/bin/activate

# 2. Navigate to the directory containing chatServer.py
cd backend

# 3. Set the Flask app entry point (Linux/macOS)
export FLASK_APP=chatServer
#(Windows/PowerShell)
# $env:FLASK_APP="chatServer.py"
#CMD in windows
#set FLASK_APP=chat_server.py


# 4. Run the server on port 8080 (as defined in chatServer.py)
flask run --host=0.0.0.0 --port=8080

# The server should start and display a message like:
# Running on [http://0.0.0.0:8080/](http://0.0.0.0:8080/) (Press CTRL+C to quit)

Accessing the Frontend

http://localhost:8080/

We should see the "AI Career Advisor" chat interface.

