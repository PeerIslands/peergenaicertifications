"""
Flask Web Application for LangGraph Chatbot POC
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import logging
from dotenv import load_dotenv
from config import Config
from chatbot import process_message

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    logger.error("Please set OPENAI_API_KEY or Azure OpenAI credentials in .env file")

app = Flask(__name__)
CORS(app)

# Store conversation history per session (simple in-memory storage)
conversations = {}


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        
        if not user_message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        # Get conversation history for this session
        conversation_history = conversations.get(session_id, [])
        
        # Process message through LangGraph chatbot
        result = process_message(user_message, conversation_history)
        
        # Update conversation history
        if result.get('success') and 'conversation_history' in result:
            conversations[session_id] = result['conversation_history']
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/clear', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a session"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in conversations:
            del conversations[session_id]
        
        return jsonify({
            'success': True,
            'message': 'Conversation cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing conversation: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    has_azure = (
        Config.AZURE_OPENAI_ENDPOINT and 
        Config.AZURE_OPENAI_API_KEY and 
        Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
    )
    has_openai = bool(Config.OPENAI_API_KEY)
    
    return jsonify({
        'status': 'healthy',
        'llm_configured': has_azure or has_openai,
        'llm_provider': 'Azure OpenAI' if has_azure else ('OpenAI' if has_openai else 'None'),
        'azure_openai_configured': has_azure,
        'openai_configured': has_openai,
        'weather_api_configured': bool(Config.OPENWEATHERMAP_API_KEY)
    })


if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("LangGraph Chatbot POC - Starting Flask App")
    logger.info("=" * 60)
    
    # Check Azure OpenAI (preferred)
    has_azure = (
        Config.AZURE_OPENAI_ENDPOINT and 
        Config.AZURE_OPENAI_API_KEY and 
        Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
    )
    has_openai = bool(Config.OPENAI_API_KEY)
    
    if has_azure:
        logger.info("LLM Provider: Azure OpenAI (Preferred)")
        logger.info(f"  Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
        logger.info(f"  Deployment: {Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME}")
        logger.info(f"  Model: {Config.AZURE_OPENAI_MODEL}")
    elif has_openai:
        logger.info("LLM Provider: OpenAI (Fallback)")
        logger.info(f"  Model: {Config.OPENAI_MODEL}")
    else:
        logger.warning("LLM: Not Configured")
    
    logger.info(f"Weather API: {'Configured' if Config.OPENWEATHERMAP_API_KEY else 'Not Configured (optional)'}")
    logger.info("=" * 60)
    
    port = Config.FLASK_PORT
    debug = Config.FLASK_DEBUG
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Web UI available at: http://localhost:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)

