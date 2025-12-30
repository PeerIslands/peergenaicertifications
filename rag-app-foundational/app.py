"""
Flask Backend for RAG Application with Azure OpenAI
Simple REST API for document ingestion and querying
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from rag_engine import rag_engine

app = Flask(__name__, static_folder='static')
CORS(app)


@app.route('/')
def index():
    """Serve the main SPA."""
    return send_from_directory('static', 'index.html')


@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files."""
    return send_from_directory('static', path)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "api_configured": rag_engine.is_configured(),
        "vector_store_loaded": rag_engine.vector_store is not None
    })


@app.route('/api/configure', methods=['POST'])
def configure():
    """Configure the Azure OpenAI API key."""
    data = request.get_json()
    
    if not data or 'api_key' not in data:
        return jsonify({
            "success": False,
            "message": "Please provide an 'api_key' in the request body"
        }), 400
    
    api_key = data['api_key'].strip()
    
    if not api_key:
        return jsonify({
            "success": False,
            "message": "API key cannot be empty"
        }), 400
    
    result = rag_engine.set_api_key(api_key)
    return jsonify(result)


@app.route('/api/ingest', methods=['POST'])
def ingest():
    """Ingest uploaded PDF documents into the vector store."""
    try:
        # Check if files were uploaded
        if 'files' not in request.files:
            return jsonify({
                "success": False,
                "message": "No PDF files uploaded"
            }), 400
        
        files = request.files.getlist('files')
        
        if not files or all(f.filename == '' for f in files):
            return jsonify({
                "success": False,
                "message": "No PDF files selected"
            }), 400
        
        # Filter only PDF files
        pdf_files = [f for f in files if f.filename.endswith('.pdf')]
        
        if not pdf_files:
            return jsonify({
                "success": False,
                "message": "No valid PDF files found"
            }), 400
        
        # Save uploaded files temporarily and ingest
        import tempfile
        import shutil
        
        temp_dir = tempfile.mkdtemp()
        saved_files = []
        
        try:
            for file in pdf_files:
                file_path = os.path.join(temp_dir, file.filename)
                file.save(file_path)
                saved_files.append(file.filename)
                print(f"Saved: {file.filename}")
            
            # Ingest from temp directory
            result = rag_engine.ingest_from_directory(temp_dir)
            
        finally:
            # Clean up temp directory
            shutil.rmtree(temp_dir, ignore_errors=True)
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"Ingestion error: {str(e)}"
        }), 500


@app.route('/api/query', methods=['POST'])
def query():
    """Query the RAG system."""
    data = request.get_json()
    
    if not data or 'question' not in data:
        return jsonify({
            "error": "Please provide a 'question' in the request body"
        }), 400
    
    question = data['question'].strip()
    
    if not question:
        return jsonify({
            "error": "Question cannot be empty"
        }), 400
    
    try:
        result = rag_engine.query(question)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": f"Query error: {str(e)}"
        }), 500


@app.route('/api/load', methods=['POST'])
def load_store():
    """Load existing vector store."""
    if not rag_engine.is_configured():
        return jsonify({
            "success": False,
            "message": "Please configure your Azure OpenAI API key first."
        })
    
    try:
        success = rag_engine.load_vector_store()
        if success:
            return jsonify({
                "success": True,
                "message": "Vector store loaded successfully"
            })
        else:
            return jsonify({
                "success": False,
                "message": "No existing vector store found. Please ingest documents first."
            })
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Load error: {str(e)}"
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_store():
    """Clear the vector store."""
    try:
        result = rag_engine.clear_vector_store()
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "success": False,
            "message": f"Clear error: {str(e)}"
        }), 500


if __name__ == '__main__':
    print("=" * 50)
    print("RAG Application with Azure OpenAI")
    print("=" * 50)
    print(f"Endpoint: {rag_engine.api_key and 'Configured' or 'Not configured'}")
    print("Please enter your Azure OpenAI API key in the UI to get started.")
    print("=" * 50)
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
