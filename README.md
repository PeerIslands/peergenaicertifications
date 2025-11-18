📌 1. Install Required Software
🔹 Install Python 3.10+

Download from:
https://www.python.org/downloads/

Select:
✔ Add to PATH
✔ Install pip

🔹 Install Ollama (Local LLM Runner)

Download from:
https://ollama.com/download

After install, verify:

ollama --version

🔹 Install Any LLM You Want (example: Gemma 3:1B)
ollama pull gemma3:1b


📌 2. Clone Project & Enter Backend Folder
git clone <your-repo-url>
cd backend

📌 3. Create & Activate Virtual Environment
Windows
python -m venv venv
venv\Scripts\activate

macOS/Linux
python3 -m venv venv
source venv/bin/activate

📌 4. Install Backend Dependencies
pip install -r requirements.txt


Make sure your requirements.txt contains:

flask                         # Web framework for building the API backend / routes
pypdf                         # Used to read and extract text from PDF files
langchain                     # Framework to build LLM apps (RAG, chains, prompts)
chromadb                      # Vector database to store embeddings for retrieval
sentence-transformers         # To generate embeddings for text/PDF content
ollama                        # Local LLM runner (Gemma, Llama, etc.)
faiss-cpu  


📌 5. Run Ingestion for Any PDF
python ingest.py 


This will:

✔ Load PDF
✔ Split text
✔ Store into a Chroma collection
✔ Ready for querying

📌 6. Start Backend Server
python app.py


Backend will run at:

http://127.0.0.1:5000/query

🟩 FRONTEND SETUP (Normal .html file)

This is a simple UI with:

✔ Ask question
✔ Display Answer
