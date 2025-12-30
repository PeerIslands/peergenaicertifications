"""
LangGraph Chatbot with State Management and Tool Routing
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool, StructuredTool
from pydantic import BaseModel, Field
import logging
from tools import (
    CalculatorTool, WeatherTool, TimeDateTool, UnitConverterTool,
    WikipediaTool, TranslationTool, get_available_tools
)
from config import Config

logger = logging.getLogger(__name__)


# Define the state structure
class ChatbotState(TypedDict):
    """State structure for the chatbot"""
    messages: Annotated[list, "List of messages in the conversation"]
    source: Annotated[str, "Source of the response (tool or llm)"]
    tool_used: Annotated[str, "Tool name if tool was used"]


def create_llm():
    """Create LLM instance - Prioritizes Azure OpenAI"""
    # Prioritize Azure OpenAI if configured
    if Config.AZURE_OPENAI_ENDPOINT and Config.AZURE_OPENAI_API_KEY and Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME:
        from langchain_openai import AzureChatOpenAI
        logger.info("Using Azure OpenAI")
        logger.info(f"Endpoint: {Config.AZURE_OPENAI_ENDPOINT}")
        logger.info(f"Deployment: {Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME}")
        logger.info(f"Model: {Config.AZURE_OPENAI_MODEL}")
        return AzureChatOpenAI(
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            deployment_name=Config.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
            model_name=Config.AZURE_OPENAI_MODEL,
            temperature=0.7
        )
    elif Config.OPENAI_API_KEY:
        logger.info("Using OpenAI (fallback)")
        return ChatOpenAI(
            api_key=Config.OPENAI_API_KEY,
            model=Config.OPENAI_MODEL,
            temperature=0.7
        )
    else:
        raise ValueError(
            "No LLM configuration found. Please set Azure OpenAI credentials "
            "(AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME) "
            "or OPENAI_API_KEY in .env file"
        )


def create_tools_for_llm():
    """Create LangChain tools for LLM to use"""
    # Calculator tool
    class CalculatorInput(BaseModel):
        expression: str = Field(description="Mathematical expression to evaluate (e.g., '2+2', '10*5', '100%3')")
    
    calculator_tool = StructuredTool.from_function(
        func=lambda expr: CalculatorTool.execute(expr),
        name="calculator",
        description="Use this tool to perform mathematical calculations. Supports: addition (+), subtraction (-), multiplication (*), division (/), modulo (%), and parentheses. Example: '2+3*4' or '100%3'",
        args_schema=CalculatorInput
    )
    
    # Weather tool
    class WeatherInput(BaseModel):
        city: str = Field(description="City name to get weather for")
    
    weather_tool = StructuredTool.from_function(
        func=lambda city: WeatherTool(api_key=Config.OPENWEATHERMAP_API_KEY).execute(city),
        name="weather",
        description="Use this tool to get current weather information for a city. Example: 'New York' or 'London'",
        args_schema=WeatherInput
    )
    
    # Time/Date tool
    class TimeDateInput(BaseModel):
        query: str = Field(description="Query about time or date (e.g., 'current time', 'what day is it')", default="")
    
    time_date_tool = StructuredTool.from_function(
        func=lambda q: TimeDateTool.execute(q),
        name="time_date",
        description="Use this tool to get current time, date, or timezone information. Example: 'what time is it', 'current date'",
        args_schema=TimeDateInput
    )
    
    # Unit Converter tool
    class UnitConverterInput(BaseModel):
        value: float = Field(description="Numeric value to convert")
        from_unit: str = Field(description="Source unit (e.g., 'km', 'celsius', 'kg')")
        to_unit: str = Field(description="Target unit (e.g., 'miles', 'fahrenheit', 'pounds')")
    
    unit_converter_tool = StructuredTool.from_function(
        func=lambda v, f, t: UnitConverterTool.execute(v, f, t),
        name="unit_converter",
        description="Use this tool to convert between different units (length, weight, temperature). Example: '100 km to miles', '50 celsius to fahrenheit'",
        args_schema=UnitConverterInput
    )
    
    # Wikipedia tool
    class WikipediaInput(BaseModel):
        query: str = Field(description="Topic to search on Wikipedia")
    
    wikipedia_tool = StructuredTool.from_function(
        func=lambda q: WikipediaTool.execute(q),
        name="wikipedia",
        description="Use this tool to search Wikipedia for information about a topic. Example: 'artificial intelligence', 'python programming'",
        args_schema=WikipediaInput
    )
    
    # Translation tool
    class TranslationInput(BaseModel):
        text: str = Field(description="Text to translate")
        target_language: str = Field(description="Target language (e.g., 'spanish', 'french', 'es', 'fr')")
    
    translation_tool = StructuredTool.from_function(
        func=lambda t, lang: TranslationTool.execute(t, lang),
        name="translation",
        description="Use this tool to translate simple words between languages. Example: 'hello to spanish', 'bonjour to english'",
        args_schema=TranslationInput
    )
    
    return [calculator_tool, weather_tool, time_date_tool, unit_converter_tool, wikipedia_tool, translation_tool]


def should_use_tool(state: ChatbotState) -> Literal["tools", "llm"]:
    """
    Router function to decide whether to use tools or LLM
    Uses AI to intelligently determine if tools are needed
    
    Args:
        state: Current chatbot state
        
    Returns:
        "tools" or "llm"
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        try:
            # Use LLM to determine if tools are needed
            llm = create_llm()
            tools = create_tools_for_llm()
            llm_with_tools = llm.bind_tools(tools)
            
            # Create a prompt to check if tools are needed
            system_prompt = SystemMessage(content=(
                "You are a routing assistant. Analyze the user's query and determine if it requires "
                "using a tool (calculator or weather) or should be handled by the LLM directly. "
                "If the query is a mathematical calculation or weather request, respond with 'tools'. "
                "Otherwise, respond with 'llm'. Only respond with 'tools' or 'llm'."
            ))
            
            # Get LLM's decision
            response = llm_with_tools.invoke([system_prompt, last_message])
            
            # Check if LLM wants to use tools
            if hasattr(response, 'tool_calls') and response.tool_calls:
                logger.info("AI routing: Using tools")
                return "tools"
            else:
                # Check response content for routing decision
                content = response.content.lower().strip()
                if 'tools' in content:
                    logger.info("AI routing: Using tools")
                    return "tools"
                else:
                    logger.info("AI routing: Using LLM")
                    return "llm"
        except Exception as e:
            logger.warning(f"Error in AI routing, falling back to keyword matching: {e}")
            # Fallback to keyword matching
            content = last_message.content.lower()
            calc_keywords = ['calculate', 'compute', 'math', 'arithmetic', 'add', 'subtract', 'multiply', 'divide']
            weather_keywords = ['weather', 'temperature', 'forecast', 'climate']
            
            if any(keyword in content for keyword in calc_keywords + weather_keywords):
                logger.info("Fallback routing: Using tools")
                return "tools"
    
    logger.info("Routing to LLM")
    return "llm"


def call_tools(state: ChatbotState) -> ChatbotState:
    """
    Call appropriate tool based on AI's decision
    Uses LLM with tool binding to intelligently extract parameters and call tools
    
    Args:
        state: Current chatbot state
        
    Returns:
        Updated state with tool response
    """
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, HumanMessage):
        try:
            # Use LLM with tools to intelligently call the right tool
            llm = create_llm()
            tools = create_tools_for_llm()
            llm_with_tools = llm.bind_tools(tools)
            
            # Add system message - be more explicit about calling tools
            system_message = SystemMessage(content=(
                "You MUST use tools to answer the user's question. "
                "For any mathematical calculation, use the calculator tool. "
                "For any weather query, use the weather tool. "
                "Extract the necessary parameters and call the appropriate tool. "
                "DO NOT just respond with text - you MUST call a tool."
            ))
            
            # Get LLM's tool call decision
            response = llm_with_tools.invoke([system_message, last_message])
            
            # Check if LLM wants to call a tool
            # Try different ways to access tool_calls
            tool_calls = None
            if hasattr(response, 'tool_calls'):
                tool_calls = response.tool_calls
            elif hasattr(response, 'tool_calls') and response.tool_calls:
                tool_calls = response.tool_calls
            elif hasattr(response, 'additional_kwargs') and 'tool_calls' in response.additional_kwargs:
                tool_calls = response.additional_kwargs['tool_calls']
            
            logger.info(f"Response type: {type(response)}, has tool_calls attr: {hasattr(response, 'tool_calls')}")
            if tool_calls:
                logger.info(f"Tool calls found: {tool_calls}")
            
            if tool_calls and len(tool_calls) > 0:
                # Add the tool call message
                messages.append(response)
                
                tool_name = None
                tool_result = None
                
                # Execute the tool calls
                for tool_call in tool_calls:
                    # Handle different tool_call formats
                    if isinstance(tool_call, dict):
                        tool_name = tool_call.get('name') or tool_call.get('function', {}).get('name')
                        tool_args = tool_call.get('args') or tool_call.get('function', {}).get('arguments', {})
                        if isinstance(tool_args, str):
                            import json
                            tool_args = json.loads(tool_args)
                    else:
                        # Try to access as object
                        tool_name = getattr(tool_call, 'name', None) or getattr(tool_call, 'function', {}).get('name', None)
                        tool_args = getattr(tool_call, 'args', None) or getattr(tool_call, 'function', {}).get('arguments', {})
                        if isinstance(tool_args, str):
                            import json
                            tool_args = json.loads(tool_args)
                    
                    logger.info(f"AI calling tool: {tool_name} with args: {tool_args}")
                    
                    # Find and execute the tool
                    for tool in tools:
                        if tool.name == tool_name:
                            if tool_name == 'calculator':
                                expression = tool_args.get('expression', '') if isinstance(tool_args, dict) else ''
                                result = CalculatorTool.execute(expression)
                                tool_result = result
                            elif tool_name == 'weather':
                                city = tool_args.get('city', '') if isinstance(tool_args, dict) else ''
                                result = WeatherTool(api_key=Config.OPENWEATHERMAP_API_KEY).execute(city)
                                tool_result = result
                            elif tool_name == 'time_date':
                                query = tool_args.get('query', '') if isinstance(tool_args, dict) else ''
                                result = TimeDateTool.execute(query)
                                tool_result = result
                            elif tool_name == 'unit_converter':
                                value = tool_args.get('value', 0) if isinstance(tool_args, dict) else 0
                                from_unit = tool_args.get('from_unit', '') if isinstance(tool_args, dict) else ''
                                to_unit = tool_args.get('to_unit', '') if isinstance(tool_args, dict) else ''
                                result = UnitConverterTool.execute(value, from_unit, to_unit)
                                tool_result = result
                            elif tool_name == 'wikipedia':
                                query = tool_args.get('query', '') if isinstance(tool_args, dict) else ''
                                result = WikipediaTool.execute(query)
                                tool_result = result
                            elif tool_name == 'translation':
                                text = tool_args.get('text', '') if isinstance(tool_args, dict) else ''
                                target_lang = tool_args.get('target_language', '') if isinstance(tool_args, dict) else ''
                                result = TranslationTool.execute(text, target_lang)
                                tool_result = result
                            break
                    
                    if tool_result:
                        break
                
                # Format tool response
                if tool_result and tool_result.get('success'):
                    if tool_name == 'calculator':
                        response_text = f"Calculation result: {tool_result['result']}"
                    elif tool_name == 'weather':
                        weather_data = tool_result
                        response_text = (
                            f"Weather in {weather_data['city']}, {weather_data['country']}:\n"
                            f"Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)\n"
                            f"Description: {weather_data['description']}\n"
                            f"Humidity: {weather_data['humidity']}%\n"
                            f"Wind Speed: {weather_data['wind_speed']} m/s\n"
                            f"Pressure: {weather_data['pressure']} hPa"
                        )
                    elif tool_name == 'time_date':
                        time_data = tool_result
                        response_text = (
                            f"Current Time: {time_data['current_time']}\n"
                            f"Current Date: {time_data['current_date']}\n"
                            f"Day of Week: {time_data['day_of_week']}\n"
                            f"Full DateTime: {time_data['full_datetime']}\n"
                            f"Timezone: {time_data['timezone']}"
                        )
                    elif tool_name == 'unit_converter':
                        response_text = tool_result.get('formatted', f"{tool_result.get('value')} {tool_result.get('from_unit')} = {tool_result.get('result')} {tool_result.get('to_unit')}")
                    elif tool_name == 'wikipedia':
                        wiki_data = tool_result
                        response_text = (
                            f"**{wiki_data['title']}**\n\n"
                            f"{wiki_data['extract']}\n\n"
                            f"Source: {wiki_data.get('url', 'N/A')}"
                        )
                    elif tool_name == 'translation':
                        trans_data = tool_result
                        response_text = f"Translation: '{trans_data['original']}' → '{trans_data['translated']}' ({trans_data['target_language']})"
                    else:
                        response_text = str(tool_result)
                    
                    # Add tool response to messages
                    messages.append(AIMessage(content=response_text))
                    
                    return {
                        "messages": messages,
                        "source": "tool",
                        "tool_used": tool_name
                    }
                else:
                    # Tool failed, fallback to LLM
                    error_msg = tool_result.get('error', 'Tool execution failed') if tool_result else 'No tool matched'
                    logger.warning(f"Tool execution failed: {error_msg}, falling back to LLM")
                    return {
                        "messages": messages,
                        "source": "llm",
                        "tool_used": None
                    }
            else:
                # LLM didn't call a tool - try to extract parameters directly from query
                content = last_message.content.lower()
                logger.info(f"No tool calls detected. Attempting direct extraction from: {content}")
                
                # Try direct extraction for weather
                if any(word in content for word in ['weather', 'temperature', 'temp', 'climate']):
                    import re
                    # Extract location - remove weather keywords
                    location = re.sub(r'weather|temperature|temp|climate|in|for|at|what|is|the', '', content, flags=re.IGNORECASE)
                    location = location.strip()
                    if location:
                        logger.info(f"Directly extracting weather for: {location}")
                        result = WeatherTool(api_key=Config.OPENWEATHERMAP_API_KEY).execute(location)
                        if result and result.get('success'):
                            weather_data = result
                            response_text = (
                                f"Weather in {weather_data['city']}, {weather_data['country']}:\n"
                                f"Temperature: {weather_data['temperature']}°C (feels like {weather_data['feels_like']}°C)\n"
                                f"Description: {weather_data['description']}\n"
                                f"Humidity: {weather_data['humidity']}%\n"
                                f"Wind Speed: {weather_data['wind_speed']} m/s\n"
                                f"Pressure: {weather_data['pressure']} hPa"
                            )
                            messages.append(AIMessage(content=response_text))
                            return {
                                "messages": messages,
                                "source": "tool",
                                "tool_used": "weather"
                            }
                
                # Try direct extraction for calculator
                calc_keywords = ['calculate', 'compute', 'math', 'add', 'subtract', 'multiply', 'divide', '+', '-', '*', '/', '%']
                if any(keyword in content for keyword in calc_keywords):
                    import re
                    # Extract expression
                    expression = re.sub(r'[^0-9+\-*/%().\s]', ' ', content)
                    expression = expression.strip()
                    if expression:
                        logger.info(f"Directly extracting calculation for: {expression}")
                        result = CalculatorTool.execute(expression)
                        if result and result.get('success'):
                            response_text = f"Calculation result: {result['result']}"
                            messages.append(AIMessage(content=response_text))
                            return {
                                "messages": messages,
                                "source": "tool",
                                "tool_used": "calculator"
                            }
                
                # If direct extraction failed, route to LLM
                logger.info("No tool calls detected and direct extraction failed, routing to LLM")
                return {
                    "messages": messages,
                    "source": "llm",
                    "tool_used": None
                }
        except Exception as e:
            logger.error(f"Error in call_tools: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to LLM on error
            return {
                "messages": messages,
                "source": "llm",
                "tool_used": None
            }
    
    return state


def call_llm(state: ChatbotState) -> ChatbotState:
    """
    Call LLM for general queries
    
    Args:
        state: Current chatbot state
        
    Returns:
        Updated state with LLM response
    """
    try:
        llm = create_llm()
        messages = state["messages"]
        
        # Add system message if not present
        if not messages or not isinstance(messages[0], SystemMessage):
            system_message = SystemMessage(content=(
                "You are a helpful AI assistant. "
                "You can answer general questions, have conversations, and provide information. "
                "For mathematical calculations or weather queries, tools will be used automatically."
            ))
            messages = [system_message] + messages
        
        # Get LLM response
        response = llm.invoke(messages)
        
        # Add LLM response to messages
        messages.append(response)
        
        return {
            "messages": messages,
            "source": "llm",
            "tool_used": None
        }
    except Exception as e:
        logger.error(f"LLM error: {e}")
        error_message = AIMessage(content=f"I apologize, but I encountered an error: {str(e)}")
        messages = state["messages"]
        messages.append(error_message)
        
        return {
            "messages": messages,
            "source": "llm",
            "tool_used": None
        }


def create_chatbot_graph():
    """
    Create LangGraph state graph for the chatbot
    
    Returns:
        Compiled graph
    """
    # Create the graph
    workflow = StateGraph(ChatbotState)
    
    # Add nodes
    workflow.add_node("tools", call_tools)
    workflow.add_node("llm", call_llm)
    
    # Add edges
    workflow.set_entry_point("router")
    
    # Add conditional routing
    workflow.add_conditional_edges(
        "router",
        should_use_tool,
        {
            "tools": "tools",
            "llm": "llm"
        }
    )
    
    # Both tools and llm nodes go to END
    workflow.add_edge("tools", END)
    workflow.add_edge("llm", END)
    
    # Compile the graph
    app = workflow.compile()
    
    return app


def router(state: ChatbotState) -> ChatbotState:
    """Router node - passes state through for conditional routing"""
    return state


# Global chatbot instance
_chatbot_app = None


def get_chatbot_app():
    """Get or create chatbot app instance"""
    global _chatbot_app
    if _chatbot_app is None:
        # Create the graph
        workflow = StateGraph(ChatbotState)
        
        # Add nodes
        workflow.add_node("router", router)
        workflow.add_node("tools", call_tools)
        workflow.add_node("llm", call_llm)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional routing
        workflow.add_conditional_edges(
            "router",
            should_use_tool,
            {
                "tools": "tools",
                "llm": "llm"
            }
        )
        
        # Both tools and llm nodes go to END
        workflow.add_edge("tools", END)
        workflow.add_edge("llm", END)
        
        # Compile the graph
        _chatbot_app = workflow.compile()
    
    return _chatbot_app


def serialize_messages(messages: list) -> list:
    """
    Convert LangChain message objects to serializable dictionaries
    
    Args:
        messages: List of LangChain message objects
        
    Returns:
        List of serializable dictionaries
    """
    serialized = []
    for msg in messages:
        if hasattr(msg, 'content') and hasattr(msg, '__class__'):
            msg_type = msg.__class__.__name__
            serialized.append({
                'type': msg_type,
                'content': msg.content
            })
        else:
            # Fallback for already serialized messages
            serialized.append(msg)
    return serialized


def process_message(user_message: str, conversation_history: list = None) -> dict:
    """
    Process a user message through the chatbot
    
    Args:
        user_message: User's message
        conversation_history: Previous conversation messages (serialized format)
        
    Returns:
        Dictionary with response and metadata
    """
    try:
        app = get_chatbot_app()
        
        # Convert serialized history back to LangChain messages if needed
        messages = []
        if conversation_history:
            for msg_dict in conversation_history:
                if isinstance(msg_dict, dict):
                    msg_type = msg_dict.get('type', 'HumanMessage')
                    content = msg_dict.get('content', '')
                    
                    if msg_type == 'HumanMessage':
                        messages.append(HumanMessage(content=content))
                    elif msg_type == 'AIMessage':
                        messages.append(AIMessage(content=content))
                    elif msg_type == 'SystemMessage':
                        messages.append(SystemMessage(content=content))
                elif hasattr(msg_dict, 'content'):
                    # Already a LangChain message object
                    messages.append(msg_dict)
        
        # Add new user message
        messages.append(HumanMessage(content=user_message))
        
        # Initial state
        initial_state = {
            "messages": messages,
            "source": "unknown",
            "tool_used": None
        }
        
        # Run the graph
        result = app.invoke(initial_state)
        
        # Get the last message (AI response)
        response_messages = result["messages"]
        ai_response = response_messages[-1]
        
        # Serialize messages for JSON response
        serialized_history = serialize_messages(response_messages)
        
        return {
            "success": True,
            "response": ai_response.content,
            "source": result["source"],
            "tool_used": result.get("tool_used"),
            "conversation_history": serialized_history
        }
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "response": f"I apologize, but I encountered an error: {str(e)}",
            "source": "error",
            "tool_used": None
        }

