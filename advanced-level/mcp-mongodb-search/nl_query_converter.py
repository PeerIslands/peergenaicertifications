"""
Natural Language Query Converter
Converts natural language queries into MongoDB query operations
"""

import re
from typing import Dict, List, Any, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLQueryConverter:
    """Converts natural language queries to MongoDB operations"""
    
    def __init__(self):
        """Initialize the query converter"""
        self.operation_patterns = {
            'find': [
                r'find|search|get|show|list|fetch|retrieve|display',
                r'what|which|where|who|when|how many'
            ],
            'update': [
                r'update|modify|change|edit|set|alter',
                r'replace|fix|correct'
            ],
            'insert': [
                r'insert|add|create|new|save|store',
                r'insert|add new'
            ],
            'delete': [
                r'delete|remove|drop|clear|erase',
                r'remove all|delete all'
            ]
        }
        
        self.comparison_operators = {
            'equals': '$eq',
            'not equals': '$ne',
            'greater than': '$gt',
            'greater than or equal': '$gte',
            'less than': '$lt',
            'less than or equal': '$lte',
            'contains': '$regex',
            'in': '$in',
            'not in': '$nin'
        }
    
    def detect_operation(self, query: str) -> str:
        """
        Detect the operation type from natural language query
        
        Args:
            query: Natural language query
            
        Returns:
            Operation type: 'find', 'update', 'insert', or 'delete'
        """
        query_lower = query.lower()
        
        # Check for each operation type
        for operation, patterns in self.operation_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    logger.info(f"Detected operation: {operation}")
                    return operation
        
        # Default to find
        return 'find'
    
    def extract_collection_name(self, query: str) -> Optional[str]:
        """
        Extract collection name from query
        
        Args:
            query: Natural language query
            
        Returns:
            Collection name if found, None otherwise
        """
        # Common patterns for collection names
        patterns = [
            r'in\s+(\w+)\s+collection',
            r'from\s+(\w+)\s+collection',
            r'collection\s+(\w+)',
            r'table\s+(\w+)',
            r'(\w+)\s+where',
            r'(\w+)\s+with'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Try to find common collection names
        common_collections = ['users', 'products', 'orders', 'items', 'documents', 'data']
        query_lower = query.lower()
        for collection in common_collections:
            if collection in query_lower:
                return collection
        
        return None
    
    def extract_filters(self, query: str) -> Dict[str, Any]:
        """
        Extract MongoDB filter conditions from natural language query
        
        Args:
            query: Natural language query
            
        Returns:
            MongoDB filter dictionary
        """
        filters = {}
        query_lower = query.lower()
        
        # Extract field-value pairs
        # Pattern: "field is value", "field equals value", "field = value"
        field_patterns = [
            r'(\w+)\s+(?:is|equals?|=\s*)(?:a\s+)?(["\']?[\w\s]+["\']?)',
            r'(\w+)\s+(?:greater than|>)\s*([\d.]+)',
            r'(\w+)\s+(?:less than|<)\s*([\d.]+)',
            r'(\w+)\s+(?:contains?|has|includes?)\s+(["\']?[\w\s]+["\']?)',
            r'(\w+)\s+(?:in|within)\s+\[([^\]]+)\]',
        ]
        
        for pattern in field_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                field = match.group(1)
                value = match.group(2).strip('"\'')
                
                # Try to convert to appropriate type
                if value.isdigit():
                    value = int(value)
                elif re.match(r'^\d+\.\d+$', value):
                    value = float(value)
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                filters[field] = value
        
        # Extract comparison operators
        if 'greater than' in query_lower or '>' in query:
            # Already handled in patterns
            pass
        elif 'less than' in query_lower or '<' in query:
            # Already handled in patterns
            pass
        elif 'not equal' in query_lower or '!=' in query:
            # Handle not equal
            pass
        
        return filters
    
    def extract_update_fields(self, query: str) -> Dict[str, Any]:
        """
        Extract update fields from natural language query
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary of fields to update
        """
        updates = {}
        
        # Pattern: "set field to value", "change field to value"
        patterns = [
            r'set\s+(\w+)\s+to\s+(["\']?[\w\s]+["\']?)',
            r'change\s+(\w+)\s+to\s+(["\']?[\w\s]+["\']?)',
            r'update\s+(\w+)\s+to\s+(["\']?[\w\s]+["\']?)',
            r'modify\s+(\w+)\s+to\s+(["\']?[\w\s]+["\']?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, query.lower())
            for match in matches:
                field = match.group(1)
                value = match.group(2).strip('"\'')
                
                # Try to convert to appropriate type
                if value.isdigit():
                    value = int(value)
                elif re.match(r'^\d+\.\d+$', value):
                    value = float(value)
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                updates[field] = value
        
        return updates
    
    def extract_insert_data(self, query: str) -> Dict[str, Any]:
        """
        Extract document data from insert query
        
        Args:
            query: Natural language query
            
        Returns:
            Document data dictionary
        """
        document = {}
        query_lower = query.lower()
        
        # Pattern: "add {field: value, field2: value2}"
        json_pattern = r'\{[^}]+\}'
        json_match = re.search(json_pattern, query)
        if json_match:
            try:
                import json
                document = json.loads(json_match.group(0))
                return document
            except:
                pass
        
        # Pattern: "with name John and age 28" or "with field1 value1 and field2 value2"
        # Find the "with" keyword and extract all field-value pairs after it
        with_match = re.search(r'with\s+(.+)', query_lower)
        if with_match:
            # Get everything after "with"
            data_part = with_match.group(1)
            
            # Split by "and" to get individual field-value pairs
            # Pattern: "name John and age 28" -> ["name John", "age 28"]
            pairs = re.split(r'\s+and\s+', data_part)
            
            for pair in pairs:
                pair = pair.strip()
                # Match "field value" pattern
                match = re.match(r'(\w+)\s+(.+)', pair)
                if match:
                    field = match.group(1)
                    value = match.group(2).strip().strip('"\'.,')
                    
                    # Try to convert to appropriate type
                    if value.isdigit():
                        value = int(value)
                    elif re.match(r'^\d+\.\d+$', value):
                        value = float(value)
                    elif value.lower() in ['true', 'false']:
                        value = value.lower() == 'true'
                    
                    document[field] = value
        
        # Also try simpler patterns: "name John", "age 28"
        if 'name' in query_lower and 'name' not in document:
            name_match = re.search(r'name\s+(\w+)', query_lower)
            if name_match:
                document['name'] = name_match.group(1)
        
        if 'age' in query_lower and 'age' not in document:
            age_match = re.search(r'age\s+(\d+)', query_lower)
            if age_match:
                document['age'] = int(age_match.group(1))
        
        # Extract other field-value pairs with common patterns
        patterns = [
            r'(\w+):\s*(["\']?[\w\s]+["\']?)',
            r'(\w+)\s+is\s+(["\']?[\w\s]+["\']?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                field = match.group(1)
                # Skip if already extracted
                if field in document:
                    continue
                    
                value = match.group(2).strip('"\'')
                
                # Try to convert to appropriate type
                if value.isdigit():
                    value = int(value)
                elif re.match(r'^\d+\.\d+$', value):
                    value = float(value)
                elif value.lower() in ['true', 'false']:
                    value = value.lower() == 'true'
                
                document[field] = value
        
        return document
    
    def convert_to_mongodb_query(self, query: str) -> Dict[str, Any]:
        """
        Convert natural language query to MongoDB operation
        
        Args:
            query: Natural language query
            
        Returns:
            Dictionary with operation, collection, and parameters
        """
        operation = self.detect_operation(query)
        collection = self.extract_collection_name(query) or 'default'
        
        result = {
            'operation': operation,
            'collection': collection,
            'query': query
        }
        
        if operation == 'find':
            filters = self.extract_filters(query)
            result['filters'] = filters
            result['limit'] = self._extract_limit(query)
        
        elif operation == 'update':
            filters = self.extract_filters(query)
            updates = self.extract_update_fields(query)
            result['filters'] = filters
            result['updates'] = updates
        
        elif operation == 'insert':
            document = self.extract_insert_data(query)
            result['document'] = document
        
        elif operation == 'delete':
            filters = self.extract_filters(query)
            result['filters'] = filters
        
        return result
    
    def _extract_limit(self, query: str) -> int:
        """Extract limit from query"""
        limit_patterns = [
            r'limit\s+(\d+)',
            r'first\s+(\d+)',
            r'top\s+(\d+)',
            r'(\d+)\s+results?'
        ]
        
        for pattern in limit_patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        
        return 10  # Default limit

