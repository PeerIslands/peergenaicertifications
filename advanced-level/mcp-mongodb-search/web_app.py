"""
Flask Web Application for MCP MongoDB Search Solution
Provides a web UI for natural language MongoDB queries
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import logging
from dotenv import load_dotenv
from config import Config
# Use real MCP client and search interface with Azure OpenAI
from real_mcp_client import RealMongoMCPClient
from real_search_interface import RealSearchInterface

# Load environment variables from .env file FIRST, before importing Config
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reload config after ensuring .env is loaded
Config.reload()

app = Flask(__name__)
CORS(app)

# Global application instance
search_app = None


def init_app():
    """Initialize the real MCP MongoDB search application with Azure OpenAI"""
    global search_app
    
    try:
        connection_string = Config.MONGODB_CONNECTION_STRING
        database_name = Config.MONGODB_DATABASE
        
        # Get Azure OpenAI configuration
        azure_endpoint = Config.AZURE_OPENAI_ENDPOINT
        azure_api_key = Config.AZURE_OPENAI_API_KEY
        azure_api_version = Config.AZURE_OPENAI_API_VERSION
        azure_deployment_name = Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        azure_model = Config.AZURE_OPENAI_MODEL
        
        if not azure_endpoint or not azure_api_key or not azure_deployment_name:
            logger.warning("Azure OpenAI configuration not complete. AI features will be disabled.")
            logger.warning("Required: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
            use_ai = False
        else:
            use_ai = True
        
        logger.info("=" * 60)
        logger.info("Initializing Real MCP MongoDB client with Azure OpenAI...")
        logger.info(f"Database: {database_name}")
        logger.info(f"Using AI: {use_ai}")
        if use_ai:
            logger.info(f"Azure OpenAI Endpoint: {azure_endpoint}")
            logger.info(f"Azure OpenAI Deployment: {azure_deployment_name}")
            logger.info(f"Azure OpenAI Model: {azure_model}")
        logger.info("=" * 60)
        
        # Create real MCP client
        mcp_client = RealMongoMCPClient(
            connection_string=connection_string,
            database_name=database_name
        )
        
        # Connect to MCP server
        if not mcp_client.connect():
            logger.error("Failed to connect to MCP server")
            logger.error("Make sure MongoDB MCP server is installed:")
            logger.error("  npm install -g @modelcontextprotocol/server-mongodb")
            return False
        
        logger.info("MCP server connected successfully")
        
        # List available tools
        try:
            tools = mcp_client.list_tools()
            logger.info(f"Available MCP tools: {[tool.get('name') for tool in tools]}")
        except Exception as e:
            logger.warning(f"Could not list tools: {e}")
        
        # Create search interface with Azure OpenAI AI
        logger.info("Initializing search interface with Azure OpenAI AI...")
        search_interface = RealSearchInterface(
            mcp_client=mcp_client,
            azure_endpoint=azure_endpoint,
            azure_api_key=azure_api_key,
            azure_api_version=azure_api_version,
            azure_deployment_name=azure_deployment_name,
            azure_model=azure_model,
            use_ai=use_ai
        )
        
        search_app = {
            'mcp_client': mcp_client,
            'search_interface': search_interface,
            'use_ai': use_ai
        }
        
        logger.info("Application initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        return False


@app.route('/')
def index():
    """Serve the main UI page"""
    return render_template('index.html')


@app.route('/api/query', methods=['POST'])
def process_query():
    """Process a natural language query"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query is required'
            }), 400
        
        if not search_app or not search_app.get('search_interface'):
            return jsonify({
                'success': False,
                'error': 'Search interface not initialized'
            }), 500
        
        logger.info(f"Processing query with {'Azure OpenAI AI' if search_app.get('use_ai') else 'regex'}: {query}")
        result = search_app['search_interface'].process_query(query)
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    health_info = {
        'status': 'healthy',
        'initialized': search_app is not None,
        'database': Config.MONGODB_DATABASE,
        'using_ai': search_app.get('use_ai', False) if search_app else False,
        'mcp_connected': search_app.get('mcp_client', {}).initialized if search_app else False
    }
    
    if search_app and search_app.get('use_ai'):
        health_info['ai_provider'] = 'Azure OpenAI'
        health_info['ai_model'] = Config.AZURE_OPENAI_MODEL
        health_info['ai_deployment'] = Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
    
    return jsonify(health_info)


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """Get example queries"""
    examples = [
        {
            'type': 'find',
            'query': 'find all users where age is greater than 25',
            'description': 'Find users older than 25'
        },
        {
            'type': 'find',
            'query': 'get products from products collection where price is less than 100',
            'description': 'Get products under $100'
        },
        {
            'type': 'find',
            'query': 'show first 5 documents from orders collection',
            'description': 'Show first 5 orders'
        },
        {
            'type': 'find',
            'query': 'list users where status is active',
            'description': 'List active users'
        },
        {
            'type': 'update',
            'query': 'update users collection set status to active where age is 30',
            'description': 'Update user status'
        },
        {
            'type': 'insert',
            'query': 'insert new user with name John and age 28',
            'description': 'Insert new user'
        }
    ]
    return jsonify(examples)


if __name__ == '__main__':
    # Validate configuration
    try:
        Config.validate()
        logger.info("=" * 60)
        logger.info("MCP MongoDB Search - Web Application")
        logger.info("=" * 60)
        logger.info(f"Database: {Config.MONGODB_DATABASE}")
        logger.info(f"Connection: {Config.MONGODB_CONNECTION_STRING}")
        logger.info("=" * 60)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        exit(1)
    
    # Check for Azure OpenAI configuration
    azure_endpoint = Config.AZURE_OPENAI_ENDPOINT
    azure_api_key = Config.AZURE_OPENAI_API_KEY
    azure_deployment = Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
    
    if not azure_endpoint or not azure_api_key or not azure_deployment:
        logger.warning("=" * 60)
        logger.warning("WARNING: Azure OpenAI configuration incomplete!")
        logger.warning("Required environment variables:")
        logger.warning("  - AZURE_OPENAI_ENDPOINT")
        logger.warning("  - AZURE_OPENAI_API_KEY")
        logger.warning("  - AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
        logger.warning("AI features will be disabled. Set these in .env file.")
        logger.warning("=" * 60)
    
    # Initialize application
    if not init_app():
        logger.error("Failed to initialize application")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure MongoDB is running")
        logger.error("2. Install MongoDB MCP server: npm install -g @modelcontextprotocol/server-mongodb")
        logger.error("3. Check MongoDB connection string in .env")
        logger.error("4. Verify Azure OpenAI credentials in .env")
        exit(1)
    
    # Run Flask app
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Flask app on port {port}")
    logger.info(f"Web UI available at: http://localhost:{port}")
    if search_app.get('use_ai'):
        logger.info(f"AI Model: Azure OpenAI GPT-4o (Enabled)")
    else:
        logger.info(f"AI Model: Disabled (regex mode)")
    
    try:
        app.run(host='0.0.0.0', port=port, debug=debug)
    finally:
        # Clean up MCP client on exit
        if search_app and search_app.get('mcp_client'):
            search_app['mcp_client'].close()

