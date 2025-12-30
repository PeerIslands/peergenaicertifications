"""
Code Converter - Converts legacy code to modern technology stacks
"""
import os
from pathlib import Path
from typing import Dict, List, Any
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)


class CodeConverter:
    """Converts legacy code to modern technology stacks"""
    
    def __init__(self, analysis_result: Dict[str, Any], target_language: str, 
                 target_framework: str, ai_model: str = "gpt-4o"):
        """
        Initialize code converter
        
        Args:
            analysis_result: Result from CodeAnalyzer
            target_language: Target language (python, typescript, etc.)
            target_framework: Target framework (fastapi, flask, express, etc.)
            ai_model: AI model to use for conversion
        """
        self.analysis = analysis_result
        self.target_language = target_language
        self.target_framework = target_framework
        self.ai_model = ai_model
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM for code conversion"""
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
    
    def convert(self) -> Dict[str, str]:
        """
        Convert legacy code to modern stack
        
        Returns:
            Dictionary mapping file paths to converted code content
        """
        logger.info(f"Converting to {self.target_language} ({self.target_framework})")
        
        converted_files = {}
        
        # Convert each source file
        for file_info in self.analysis['files']:
            try:
                source_path = Path(file_info['absolute_path'])
                if not source_path.exists():
                    continue
                
                # Read source code
                source_code = source_path.read_text(encoding='utf-8', errors='ignore')
                
                # Convert using AI
                converted_code = self._convert_file(
                    source_code,
                    file_info['path'],
                    file_info['extension']
                )
                
                # Determine target file path
                target_path = self._get_target_path(file_info['path'], file_info['extension'])
                converted_files[target_path] = converted_code
                
            except Exception as e:
                logger.warning(f"Failed to convert {file_info['path']}: {e}")
        
        # Generate additional files (config, requirements, etc.)
        additional_files = self._generate_additional_files()
        converted_files.update(additional_files)
        
        return converted_files
    
    def _convert_file(self, source_code: str, file_path: str, extension: str) -> str:
        """Convert a single file using AI"""
        if not self.llm:
            return f"# Converted from {file_path}\n# LLM not configured\n{source_code}"
        
        try:
            # Build conversion prompt
            prompt = self._build_conversion_prompt(source_code, file_path, extension)
            
            # Get conversion from AI
            response = self.llm.invoke(prompt)
            converted_code = response.content
            
            return converted_code
        except Exception as e:
            logger.error(f"AI conversion failed for {file_path}: {e}")
            return f"# Conversion failed: {e}\n# Original code:\n{source_code}"
    
    def _build_conversion_prompt(self, source_code: str, file_path: str, extension: str) -> str:
        """Build prompt for code conversion"""
        source_lang = self._detect_source_language(extension)
        
        prompt = f"""Convert the following {source_lang} code to {self.target_language} using {self.target_framework}.

Source file: {file_path}
Target: {self.target_language} ({self.target_framework})

Requirements:
1. Maintain 100% feature parity
2. Use modern best practices for {self.target_language}
3. Add type hints/annotations where applicable
4. Follow {self.target_framework} conventions
5. Preserve all business logic
6. Add proper error handling

Source code:
```{source_lang}
{source_code[:8000]}  # Limit size
```

Converted code:
```{self.target_language}
"""
        return prompt
    
    def _detect_source_language(self, extension: str) -> str:
        """Detect source language from extension"""
        lang_map = {
            '.java': 'java',
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.cs': 'csharp'
        }
        return lang_map.get(extension, 'unknown')
    
    def _get_target_path(self, source_path: str, extension: str) -> str:
        """Get target file path for converted code"""
        # Map extensions
        ext_map = {
            '.java': '.py',
            '.js': '.ts',
            '.cs': '.py'
        }
        target_ext = ext_map.get(extension, extension)
        
        # Replace path components
        target_path = source_path.replace(extension, target_ext)
        
        # Adjust directory structure for target framework
        if self.target_framework == 'fastapi':
            # Convert Java package structure to Python module structure
            target_path = target_path.replace('src/main/java/', 'src/')
            target_path = target_path.replace('/', '/').replace('\\', '/')
        
        return target_path
    
    def _generate_additional_files(self) -> Dict[str, str]:
        """Generate additional files (requirements.txt, config files, etc.)"""
        files = {}
        
        if self.target_language == 'python':
            # Generate requirements.txt
            files['requirements.txt'] = self._generate_requirements_txt()
            
            # Generate main.py if FastAPI
            if self.target_framework == 'fastapi':
                files['main.py'] = self._generate_fastapi_main()
            
            # Generate config.py
            files['src/config/settings.py'] = self._generate_config_py()
        
        return files
    
    def _generate_requirements_txt(self) -> str:
        """Generate requirements.txt"""
        deps = {
            'fastapi': 'fastapi>=0.104.0',
            'flask': 'flask>=3.0.0',
        }
        
        base_deps = [
            'pydantic>=2.5.0',
            'sqlalchemy>=2.0.0',
            'pytest>=7.4.0',
            'pytest-cov>=4.1.0',
        ]
        
        framework_dep = deps.get(self.target_framework, '')
        all_deps = [framework_dep] + base_deps if framework_dep else base_deps
        
        return '\n'.join(all_deps) + '\n'
    
    def _generate_fastapi_main(self) -> str:
        """Generate FastAPI main.py"""
        return '''"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Modernized API",
    version="1.0.0",
    description="Auto-generated from legacy code"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
'''
    
    def _generate_config_py(self) -> str:
        """Generate config.py"""
        return '''"""Application configuration."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    app_name: str = "Modernized API"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
'''

