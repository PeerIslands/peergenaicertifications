"""
Test Generator - Generates comprehensive test suites for modernized code
"""
import os
from typing import Dict, List, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class TestGenerator:
    """Generates test suites for modernized code"""
    
    def __init__(self, modernized_code: Dict[str, str], coverage_target: int = 80, 
                 ai_model: str = "gpt-4o"):
        """
        Initialize test generator
        
        Args:
            modernized_code: Dictionary of modernized code files
            coverage_target: Target test coverage percentage
            ai_model: AI model to use for test generation
        """
        self.modernized_code = modernized_code
        self.coverage_target = coverage_target
        self.ai_model = ai_model
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM for test generation"""
        try:
            from langchain_openai import AzureChatOpenAI
            endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
            api_key = os.getenv('AZURE_OPENAI_API_KEY')
            deployment = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
            
            if endpoint and api_key and deployment:
                self.llm = AzureChatOpenAI(
                    azure_endpoint=endpoint,
                    api_key=api_key,
                    azure_deployment=deployment,
                    api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-06-01'),
                    model_name=os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o')
                )
            else:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.llm = ChatOpenAI(model=self.ai_model, api_key=api_key)
                else:
                    raise ValueError("No LLM API key configured")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def generate(self) -> Dict[str, str]:
        """
        Generate test suite for modernized code
        
        Returns:
            Dictionary mapping test file paths to test code content
        """
        logger.info(f"Generating tests with {self.coverage_target}% coverage target")
        
        test_files = {}
        
        # Generate tests for each source file
        for file_path, code_content in self.modernized_code.items():
            # Skip non-source files
            if not file_path.endswith('.py') or file_path in ['main.py', 'requirements.txt']:
                continue
            
            try:
                test_code = self._generate_test_file(file_path, code_content)
                test_file_path = self._get_test_path(file_path)
                test_files[test_file_path] = test_code
            except Exception as e:
                logger.warning(f"Failed to generate test for {file_path}: {e}")
        
        # Generate test configuration
        test_files['pytest.ini'] = self._generate_pytest_config()
        test_files['src/tests/conftest.py'] = self._generate_conftest()
        
        return test_files
    
    def _generate_test_file(self, source_path: str, source_code: str) -> str:
        """Generate test file for a source file"""
        if not self.llm:
            return self._generate_basic_test(source_path, source_code)
        
        try:
            prompt = f"""Generate comprehensive pytest tests for the following Python code.

Target coverage: {self.coverage_target}%

Requirements:
1. Test all functions and methods
2. Test edge cases and error scenarios
3. Use pytest fixtures where appropriate
4. Include integration tests if applicable
5. Mock external dependencies
6. Achieve at least {self.coverage_target}% coverage

Source file: {source_path}

Source code:
```python
{source_code[:6000]}  # Limit size
```

Generate complete test file:
```python
"""
        
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"AI test generation failed: {e}")
            return self._generate_basic_test(source_path, source_code)
    
    def _generate_basic_test(self, source_path: str, source_code: str) -> str:
        """Generate basic test template"""
        return f'''"""Tests for {source_path}"""
import pytest

# TODO: Add comprehensive tests
# Target coverage: {self.coverage_target}%

def test_placeholder():
    """Placeholder test"""
    assert True
'''
    
    def _get_test_path(self, source_path: str) -> str:
        """Get test file path for source file"""
        # Convert src/api/routes/users.py -> src/tests/test_users.py
        if 'src/' in source_path:
            parts = source_path.split('src/')
            if len(parts) > 1:
                module_path = parts[1].replace('.py', '')
                test_name = f"test_{module_path.replace('/', '_')}"
                return f"src/tests/{test_name}.py"
        return f"tests/test_{source_path.replace('/', '_').replace('.py', '')}.py"
    
    def _generate_pytest_config(self) -> str:
        """Generate pytest.ini configuration"""
        return f"""[pytest]
testpaths = src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=src
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under={self.coverage_target}
"""
    
    def _generate_conftest(self) -> str:
        """Generate pytest conftest.py"""
        return '''"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)
'''

