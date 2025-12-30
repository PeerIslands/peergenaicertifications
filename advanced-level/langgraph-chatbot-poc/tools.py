"""
Tools for LangGraph Chatbot - Multiple Tools
"""

from typing import Dict, Any, Optional
import requests
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class CalculatorTool:
    """Calculator tool for performing mathematical operations"""
    
    name = "calculator"
    description = """
    Use this tool to perform mathematical calculations.
    Supports: addition (+), subtraction (-), multiplication (*), division (/), 
    power (^), modulo (%), and parentheses.
    Example: "calculate 2 + 3 * 4" or "what is 100 / 5"
    """
    
    @staticmethod
    def execute(expression: str) -> Dict[str, Any]:
        """
        Execute a mathematical expression
        
        Args:
            expression: Mathematical expression as string
            
        Returns:
            Dictionary with result and metadata
        """
        try:
            # Clean the expression
            expression = expression.strip()
            
            # Replace common text with operators
            expression = expression.replace('plus', '+')
            expression = expression.replace('minus', '-')
            expression = expression.replace('times', '*')
            expression = expression.replace('multiply', '*')
            expression = expression.replace('divided by', '/')
            expression = expression.replace('divide', '/')
            expression = expression.replace('to the power of', '**')
            expression = expression.replace('power', '**')
            expression = expression.replace('modulo', '%')
            expression = expression.replace('mod', '%')
            
            # Remove non-math characters (keep only numbers, operators, spaces, parentheses)
            import re
            # Allow: digits, +, -, *, /, %, ^, **, (, ), ., spaces
            cleaned = re.sub(r'[^0-9+\-*/%^().\s]', '', expression)
            # Replace ^ with ** for power operation
            cleaned = cleaned.replace('^', '**')
            
            # Evaluate safely
            result = eval(cleaned)
            
            return {
                'success': True,
                'result': result,
                'expression': expression,
                'source': 'calculator_tool'
            }
        except Exception as e:
            logger.error(f"Calculator error: {e}")
            return {
                'success': False,
                'error': str(e),
                'expression': expression,
                'source': 'calculator_tool'
            }


class WeatherTool:
    """Weather tool for getting weather information"""
    
    name = "weather"
    description = """
    Use this tool to get current weather information for a city.
    Example: "what's the weather in New York" or "weather in London"
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize weather tool
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def execute(self, city: str) -> Dict[str, Any]:
        """
        Get weather for a city
        
        Args:
            city: City name
            
        Returns:
            Dictionary with weather information
        """
        if not self.api_key:
            return {
                'success': False,
                'error': 'OpenWeatherMap API key not configured',
                'source': 'weather_tool'
            }
        
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'  # Celsius
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            weather_info = {
                'success': True,
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'pressure': data['main']['pressure'],
                'source': 'weather_tool'
            }
            
            return weather_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather API error: {e}")
            return {
                'success': False,
                'error': f'Failed to fetch weather: {str(e)}',
                'city': city,
                'source': 'weather_tool'
            }
        except Exception as e:
            logger.error(f"Weather error: {e}")
            return {
                'success': False,
                'error': str(e),
                'city': city,
                'source': 'weather_tool'
            }


class TimeDateTool:
    """Time and Date tool for getting current time/date information"""
    
    name = "time_date"
    description = """
    Use this tool to get current time, date, or timezone information.
    Example: "what time is it", "current date", "what day is it"
    """
    
    @staticmethod
    def execute(query: str = "") -> Dict[str, Any]:
        """
        Get current time and date information
        
        Args:
            query: Optional query about time/date
            
        Returns:
            Dictionary with time/date information
        """
        try:
            now = datetime.now()
            
            return {
                'success': True,
                'current_time': now.strftime('%H:%M:%S'),
                'current_date': now.strftime('%Y-%m-%d'),
                'day_of_week': now.strftime('%A'),
                'full_datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
                'timezone': str(now.astimezone().tzinfo),
                'source': 'time_date_tool'
            }
        except Exception as e:
            logger.error(f"Time/Date error: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': 'time_date_tool'
            }


class UnitConverterTool:
    """Unit Converter tool for converting between different units"""
    
    name = "unit_converter"
    description = """
    Use this tool to convert between different units (length, weight, temperature, etc.).
    Example: "convert 100 km to miles", "50 celsius to fahrenheit", "10 kg to pounds"
    """
    
    @staticmethod
    def execute(value: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
        """
        Convert between units
        
        Args:
            value: Numeric value to convert
            from_unit: Source unit
            to_unit: Target unit
            
        Returns:
            Dictionary with conversion result
        """
        try:
            from_unit = from_unit.lower().strip()
            to_unit = to_unit.lower().strip()
            
            # Temperature conversions
            if from_unit in ['celsius', 'c'] and to_unit in ['fahrenheit', 'f']:
                result = (value * 9/5) + 32
                return {
                    'success': True,
                    'value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit,
                    'result': round(result, 2),
                    'formatted': f"{value}°C = {round(result, 2)}°F",
                    'source': 'unit_converter_tool'
                }
            elif from_unit in ['fahrenheit', 'f'] and to_unit in ['celsius', 'c']:
                result = (value - 32) * 5/9
                return {
                    'success': True,
                    'value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit,
                    'result': round(result, 2),
                    'formatted': f"{value}°F = {round(result, 2)}°C",
                    'source': 'unit_converter_tool'
                }
            
            # Length conversions (to meters first, then to target)
            length_to_meters = {
                'mm': 0.001, 'millimeter': 0.001, 'millimeters': 0.001,
                'cm': 0.01, 'centimeter': 0.01, 'centimeters': 0.01,
                'm': 1, 'meter': 1, 'meters': 1, 'metre': 1, 'metres': 1,
                'km': 1000, 'kilometer': 1000, 'kilometers': 1000, 'kilometre': 1000, 'kilometres': 1000,
                'in': 0.0254, 'inch': 0.0254, 'inches': 0.0254,
                'ft': 0.3048, 'foot': 0.3048, 'feet': 0.3048,
                'yd': 0.9144, 'yard': 0.9144, 'yards': 0.9144,
                'mi': 1609.34, 'mile': 1609.34, 'miles': 1609.34
            }
            
            # Weight conversions (to kg first, then to target)
            weight_to_kg = {
                'g': 0.001, 'gram': 0.001, 'grams': 0.001,
                'kg': 1, 'kilogram': 1, 'kilograms': 1,
                'oz': 0.0283495, 'ounce': 0.0283495, 'ounces': 0.0283495,
                'lb': 0.453592, 'pound': 0.453592, 'pounds': 0.453592,
                'ton': 1000, 'tons': 1000
            }
            
            # Check if it's a length conversion
            if from_unit in length_to_meters and to_unit in length_to_meters:
                meters = value * length_to_meters[from_unit]
                result = meters / length_to_meters[to_unit]
                return {
                    'success': True,
                    'value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit,
                    'result': round(result, 4),
                    'formatted': f"{value} {from_unit} = {round(result, 4)} {to_unit}",
                    'source': 'unit_converter_tool'
                }
            
            # Check if it's a weight conversion
            if from_unit in weight_to_kg and to_unit in weight_to_kg:
                kg = value * weight_to_kg[from_unit]
                result = kg / weight_to_kg[to_unit]
                return {
                    'success': True,
                    'value': value,
                    'from_unit': from_unit,
                    'to_unit': to_unit,
                    'result': round(result, 4),
                    'formatted': f"{value} {from_unit} = {round(result, 4)} {to_unit}",
                    'source': 'unit_converter_tool'
                }
            
            return {
                'success': False,
                'error': f'Unsupported conversion from {from_unit} to {to_unit}',
                'source': 'unit_converter_tool'
            }
        except Exception as e:
            logger.error(f"Unit converter error: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': 'unit_converter_tool'
            }


class WikipediaTool:
    """Wikipedia search tool for getting information from Wikipedia"""
    
    name = "wikipedia"
    description = """
    Use this tool to search Wikipedia for information about a topic.
    Example: "search wikipedia for artificial intelligence", "wikipedia python programming"
    """
    
    @staticmethod
    def execute(query: str) -> Dict[str, Any]:
        """
        Search Wikipedia for information
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with Wikipedia information
        """
        try:
            # Use Wikipedia API
            url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(' ', '_')
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'title': data.get('title', query),
                    'extract': data.get('extract', 'No summary available'),
                    'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                    'source': 'wikipedia_tool'
                }
            else:
                # Try search API
                search_url = "https://en.wikipedia.org/api/rest_v1/page/summary/" + query.replace(' ', '_')
                return {
                    'success': False,
                    'error': f'Wikipedia page not found for: {query}',
                    'source': 'wikipedia_tool'
                }
        except Exception as e:
            logger.error(f"Wikipedia error: {e}")
            return {
                'success': False,
                'error': f'Failed to fetch Wikipedia information: {str(e)}',
                'query': query,
                'source': 'wikipedia_tool'
            }


class TranslationTool:
    """Translation tool for translating text between languages"""
    
    name = "translation"
    description = """
    Use this tool to translate text between languages.
    Note: This is a simple word-based translation. For complex translations, use LLM.
    Example: "translate hello to spanish", "translate bonjour to english"
    """
    
    # Simple translation dictionary (basic words)
    translations = {
        'hello': {'es': 'hola', 'fr': 'bonjour', 'de': 'hallo', 'it': 'ciao', 'pt': 'olá', 'ja': 'こんにちは', 'zh': '你好'},
        'goodbye': {'es': 'adiós', 'fr': 'au revoir', 'de': 'auf wiedersehen', 'it': 'arrivederci', 'pt': 'adeus', 'ja': 'さようなら', 'zh': '再见'},
        'thank you': {'es': 'gracias', 'fr': 'merci', 'de': 'danke', 'it': 'grazie', 'pt': 'obrigado', 'ja': 'ありがとう', 'zh': '谢谢'},
    }
    
    @staticmethod
    def execute(text: str, target_language: str) -> Dict[str, Any]:
        """
        Translate text to target language
        
        Args:
            text: Text to translate
            target_language: Target language code (e.g., 'es', 'fr', 'de')
            
        Returns:
            Dictionary with translation result
        """
        try:
            text_lower = text.lower().strip()
            target_lang = target_language.lower().strip()
            
            # Language name mapping
            lang_map = {
                'spanish': 'es', 'español': 'es', 'es': 'es',
                'french': 'fr', 'français': 'fr', 'fr': 'fr',
                'german': 'de', 'deutsch': 'de', 'de': 'de',
                'italian': 'it', 'italiano': 'it', 'it': 'it',
                'portuguese': 'pt', 'português': 'pt', 'pt': 'pt',
                'japanese': 'ja', '日本語': 'ja', 'ja': 'ja',
                'chinese': 'zh', '中文': 'zh', 'zh': 'zh'
            }
            
            target_lang = lang_map.get(target_lang, target_lang)
            
            # Check if we have a translation
            if text_lower in TranslationTool.translations:
                if target_lang in TranslationTool.translations[text_lower]:
                    return {
                        'success': True,
                        'original': text,
                        'translated': TranslationTool.translations[text_lower][target_lang],
                        'target_language': target_language,
                        'source': 'translation_tool'
                    }
            
            # For complex translations, suggest using LLM
            return {
                'success': False,
                'error': f'Complex translation not supported. Please use LLM for translating: "{text}" to {target_language}',
                'suggestion': 'Try asking the LLM directly for translation',
                'source': 'translation_tool'
            }
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'source': 'translation_tool'
            }


def get_available_tools(weather_api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Get all available tools
    
    Args:
        weather_api_key: OpenWeatherMap API key
        
    Returns:
        Dictionary of available tools
    """
    tools = {
        'calculator': CalculatorTool(),
        'weather': WeatherTool(api_key=weather_api_key),
        'time_date': TimeDateTool(),
        'unit_converter': UnitConverterTool(),
        'wikipedia': WikipediaTool(),
        'translation': TranslationTool()
    }
    return tools

