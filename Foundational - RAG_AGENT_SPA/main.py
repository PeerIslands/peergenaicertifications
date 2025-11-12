import subprocess
import sys
import os

# Install dependencies first
print("Installing dependencies...")
try:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("✅ Dependencies installed successfully")
except subprocess.CalledProcessError as e:
    print(f"❌ Error installing dependencies: {e}")
    sys.exit(1)

# Now import the modules
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import google.generativeai as genai
import PyPDF2

app = FastAPI(title="RAG Document QA System with Gemini", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple document storage
documents = []


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    confidence: float


def initialize_gemini():
    """Initialize Google Gemini API"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is required")

    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>RAG Document QA System </title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #333;
                text-align: center;
                margin-bottom: 10px;
            }
            .gemini-banner {
                background: linear-gradient(45deg, #4285f4, #34a853);
                color: white;
                padding: 15px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
                font-weight: bold;
                box-shadow: 0 4px 15px rgba(66,133,244,0.3);
            }
            .upload-area {
                border: 3px dashed #4285f4;
                padding: 40px;
                text-align: center;
                margin: 20px 0;
                border-radius: 15px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                transition: all 0.3s ease;
            }
            .upload-area:hover {
                background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
                transform: translateY(-2px);
            }
            input[type="file"] {
                margin: 10px 0;
                padding: 10px;
                border: 2px solid #4285f4;
                border-radius: 8px;
                background: white;
            }
            button {
                background: linear-gradient(45deg, #4285f4, #34a853);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                cursor: pointer;
                margin: 5px;
                font-weight: bold;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(66,133,244,0.3);
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(66,133,244,0.4);
            }
            .query-area {
                margin: 20px 0;
            }
            textarea {
                width: 100%;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                margin: 10px 0;
                font-size: 16px;
                transition: border-color 0.3s ease;
            }
            textarea:focus {
                border-color: #4285f4;
                outline: none;
            }
            .result {
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
                border-left: 5px solid #4285f4;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            .status {
                padding: 15px;
                margin: 10px 0;
                border-radius: 10px;
                font-weight: bold;
            }
            .success {
                background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
                color: #155724;
                border: 2px solid #c3e6cb;
            }
            .error {
                background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
                color: #721c24;
                border: 2px solid #f5c6cb;
            }
            .sample-questions {
                background: linear-gradient(135deg, #e7f3ff 0%, #d1ecf1 100%);
                padding: 20px;
                border-radius: 15px;
                margin: 20px 0;
                border: 2px solid #bee5eb;
            }
            .sample-questions h4 {
                margin-top: 0;
                color: #0066cc;
                text-align: center;
            }
            .sample-questions button {
                background: linear-gradient(45deg, #28a745, #20c997);
                margin: 3px;
                padding: 8px 16px;
                font-size: 14px;
                box-shadow: 0 3px 10px rgba(40,167,69,0.3);
            }
            .sample-questions button:hover {
                box-shadow: 0 5px 15px rgba(40,167,69,0.4);
            }
            .stats {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
            }
            .stat-item {
                text-align: center;
                padding: 15px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border-radius: 10px;
                flex: 1;
                margin: 0 5px;
            }
            .stat-number {
                font-size: 24px;
                font-weight: bold;
                color: #4285f4;
            }
        </style>
    </head>
    <body>
        <div class="container">
            

            <h1>📚 RAG Document QA System</h1>

            <div class="stats">
                <div class="stat-item">
                    <div class="stat-number" id="docCount">0</div>
                    <div>Documents</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number" id="queryCount">0</div>
                    <div>Queries</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">100%</div>
                    <div>Uptime</div>
                </div>
            </div>

            <div class="upload-area">
                <h3>📁 Upload Documents</h3>
                <input type="file" id="fileInput" multiple accept=".pdf,.txt">
                <br>
                <button onclick="uploadFiles()">📤 Upload Files</button>
                <div id="uploadStatus"></div>
            </div>

            <div class="query-area">
                <h3>❓ Ask Questions</h3>
                <textarea id="queryInput" placeholder="Ask any question about your uploaded documents..." rows="4"></textarea>
                <br>
                <button onclick="askQuestion()">Ask</button>
                <div id="queryResult"></div>
            </div>

            <div class="sample-questions">
                <h4>💡 Try These Sample Questions:</h4>
                <button onclick="setQuestion('What is the main topic of the document?')">Main Topic</button>
                <button onclick="setQuestion('Summarize the key points')">Summarize</button>
                <button onclick="setQuestion('What are the important findings?')">Key Findings</button>
                <button onclick="setQuestion('What are the main conclusions?')">Conclusions</button>
                <button onclick="setQuestion('What methodology was used?')">Methodology</button>
                <button onclick="setQuestion('What are the recommendations?')">Recommendations</button>
                <button onclick="setQuestion('Who are the main authors?')">Authors</button>
                <button onclick="setQuestion('What data sources were used?')">Data Sources</button>
            </div>

            <div>
                <h3>📊 System Management</h3>
                <button onclick="checkStatus()">📊 Check Status</button>
                <button onclick="clearDocuments()">🗑️ Clear Documents</button>
                <button onclick="showDocumentList()">📋 Show Documents</button>
                <div id="statusResult"></div>
            </div>
        </div>

        <script>
            const API_BASE = window.location.origin;
            let queryCount = 0;

            function setQuestion(question) {
                document.getElementById('queryInput').value = question;
            }

            function updateStats() {
                document.getElementById('queryCount').textContent = queryCount;
            }

            async function uploadFiles() {
                const fileInput = document.getElementById('fileInput');
                const files = fileInput.files;

                if (files.length === 0) {
                    showStatus('uploadStatus', 'Please select files to upload', 'error');
                    return;
                }

                const formData = new FormData();
                for (let file of files) {
                    formData.append('files', file);
                }

                try {
                    showStatus('uploadStatus', '📤 Uploading files...', 'success');
                    const response = await fetch(`${API_BASE}/upload`, {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    if (response.ok) {
                        showStatus('uploadStatus', `✅ ${result.message}`, 'success');
                        fileInput.value = '';
                        updateDocumentCount();
                    } else {
                        showStatus('uploadStatus', `❌ Upload failed: ${result.detail}`, 'error');
                    }
                } catch (error) {
                    showStatus('uploadStatus', `❌ Upload error: ${error.message}`, 'error');
                }
            }

            async function askQuestion() {
                const query = document.getElementById('queryInput').value.trim();

                if (!query) {
                    showStatus('queryResult', 'Please enter a question', 'error');
                    return;
                }

                queryCount++;
                updateStats();

                try {
                    showStatus('queryResult', '🤔 Agent is thinking...', 'success');
                    const response = await fetch(`${API_BASE}/query`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ query: query })
                    });

                    const result = await response.json();
                    if (response.ok) {
                        showResult('queryResult', result.answer, result.confidence);
                    } else {
                        showStatus('queryResult', `❌ Query failed: ${result.detail}`, 'error');
                    }
                } catch (error) {
                    showStatus('queryResult', `❌ Query error: ${error.message}`, 'error');
                }
            }

            async function checkStatus() {
                try {
                    const response = await fetch(`${API_BASE}/documents/count`);
                    const result = await response.json();
                    showStatus('statusResult', `📄 Documents in system: ${result.document_count}`, 'success');
                    updateDocumentCount();
                } catch (error) {
                    showStatus('statusResult', `❌ Status check failed: ${error.message}`, 'error');
                }
            }

            async function updateDocumentCount() {
                try {
                    const response = await fetch(`${API_BASE}/documents/count`);
                    const result = await response.json();
                    document.getElementById('docCount').textContent = result.document_count;
                } catch (error) {
                    console.log('Could not update document count');
                }
            }

            async function clearDocuments() {
                try {
                    const response = await fetch(`${API_BASE}/documents`, {
                        method: 'DELETE'
                    });
                    const result = await response.json();
                    showStatus('statusResult', `✅ ${result.message}`, 'success');
                    updateDocumentCount();
                } catch (error) {
                    showStatus('statusResult', `❌ Clear failed: ${error.message}`, 'error');
                }
            }

            async function showDocumentList() {
                try {
                    const response = await fetch(`${API_BASE}/documents/list`);
                    const result = await response.json();
                    if (response.ok) {
                        let docList = '📋 Uploaded Documents:<br>';
                        result.documents.forEach((doc, index) => {
                            docList += `${index + 1}. ${doc.filename}<br>`;
                        });
                        showStatus('statusResult', docList, 'success');
                    } else {
                        showStatus('statusResult', 'No documents found', 'error');
                    }
                } catch (error) {
                    showStatus('statusResult', `❌ Could not fetch document list`, 'error');
                }
            }

            function showStatus(elementId, message, type) {
                const element = document.getElementById(elementId);
                element.innerHTML = `<div class="status ${type}">${message}</div>`;
            }

            function showResult(elementId, answer, confidence) {
                const element = document.getElementById(elementId);
                element.innerHTML = `
                    <div class="result">
                        <h4>🤖 Agent Response:</h4>
                        <p>${answer}</p>
                        <small>Confidence: ${Math.round(confidence * 100)}% | Powered by Google Gemini</small>
                    </div>
                `;
            }

            // Check system status on page load
            window.onload = function() {
                checkStatus();
                updateStats();
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    global documents
    try:
        processed_count = 0
        for file in files:
            # Accept both PDF and text files
            if file.filename.endswith(('.pdf', '.txt')):
                # Save file temporarily
                file_path = f"temp_{file.filename}"
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # Extract text content
                if file.filename.endswith('.txt'):
                    with open(file_path, 'r', encoding='utf-8') as text_file:
                        text = text_file.read()
                else:
                    # Extract text from PDF
                    with open(file_path, 'rb') as pdf_file:
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        text = ""
                        for page in pdf_reader.pages:
                            text += page.extract_text() + "\n"

                documents.append({"filename": file.filename, "content": text})

                # Clean up
                os.remove(file_path)
                processed_count += 1

        return {
            "message": f"Successfully processed {processed_count} documents",
            "documents_processed": processed_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    try:
        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No documents uploaded. Please upload documents first.")

        # Initialize Gemini
        model = initialize_gemini()

        # Create context from documents
        context = ""
        for doc in documents:
            context += f"Document: {doc['filename']}\n{doc['content']}\n\n"

        # Create prompt for Gemini
        prompt = f"""
        You are an intelligent document analysis assistant. Based on the following documents, please answer the user's question accurately and comprehensively.

        Documents:
        {context}

        User Question: {request.query}

        Please provide a detailed, accurate answer based on the document content. If the information is not available in the documents, please state that clearly.
        """

        # Get response from Gemini
        response = model.generate_content(prompt)
        answer = response.text

        return QueryResponse(answer=answer, confidence=0.9)

    except Exception as e:
        print(f"Error in query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/count")
async def get_document_count():
    return {"document_count": len(documents)}


@app.get("/documents/list")
async def get_document_list():
    return {"documents": [{"filename": doc["filename"]} for doc in documents]}


@app.delete("/documents")
async def clear_documents():
    global documents
    documents = []
    return {"message": "All documents cleared successfully"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "documents": len(documents)}


if __name__ == "__main__":
    print("🚀 Starting RAG Document QA System with Google Gemini...")
    print("✅ Free API with generous quotas!")
    uvicorn.run(app, host="0.0.0.0", port=8000)
