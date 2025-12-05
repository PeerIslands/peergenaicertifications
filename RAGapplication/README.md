#Run commands
python -m venv venv1
venv1\Scripts\activate
pip install -r requirements.txt
streamlit run app.py

#Workflow

User uploads PDF or ZIP (code repo)
Extract text
Split text into chunks
Convert chunks into embeddings (vectors) using free HuggingFace models
Store embeddings locally using ChromaDB
When user asks a question → retrieve the most relevant chunks
Pass retrieved chunks + question into a Groq LLaMA-3.3 model
LLM Groq answers ONLY from your document
Streamlit displays the answer


                 ┌─────────────────┐
                 │    User Input    │
                 │ (PDF / ZIP / Q&A)│
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │ Document Loader │
                 │ (PDF / ZIP)     │
                 └────────┬────────┘
                          │
                          ▼
                 ┌─────────────────┐
                 │   Text Splitter │
                 │ (Chunking)      │
                 └────────┬────────┘
                          │
                          ▼
              ┌───────────────────────────┐
              │  Embedding Model (HF)     │
              │  SentenceTransformers      │
              └──────────┬────────────────┘
                          │  (Vectors)
                          ▼
                ┌─────────────────────┐
                │  Vector Database     │
                │     (ChromaDB)       │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Retriever          │
                │ (Similar chunks)     │
                └──────────┬──────────┘
                           │
             ┌─────────────▼─────────────┐
             │    RAG Prompt Builder      │
             │ (Context + Question → LLM) │
             └─────────────┬─────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   LLM (Groq Llama)  │
                └──────────┬──────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   Final Answer       │
                │ (Shown in Streamlit) │
                └─────────────────────┘
