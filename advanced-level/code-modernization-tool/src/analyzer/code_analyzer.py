"""
Code Analyzer - Analyzes legacy codebases to extract structure, patterns, and dependencies
"""
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

logger = logging.getLogger(__name__)


class CodeAnalyzer:
    """Analyzes legacy code to extract structure and patterns"""
    
    def __init__(self, source_path: Path, ai_model: str = "gpt-4o"):
        """
        Initialize code analyzer
        
        Args:
            source_path: Path to source code directory
            ai_model: AI model to use for analysis
        """
        self.source_path = Path(source_path)
        self.ai_model = ai_model
        self.llm = None
        self._init_llm()
    
    def _init_llm(self):
        """Initialize LLM for code analysis"""
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
                logger.info("Using Azure OpenAI for code analysis")
            else:
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self.llm = ChatOpenAI(model=self.ai_model, api_key=api_key)
                    logger.info("Using OpenAI for code analysis")
                else:
                    raise ValueError("No LLM API key configured")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            raise
    
    def analyze(self) -> Dict[str, Any]:
        """
        Analyze the codebase and extract structure, patterns, and dependencies
        
        Returns:
            Dictionary containing analysis results
        """
        logger.info(f"Analyzing codebase at: {self.source_path}")
        
        # Step 1: Discover files
        files = self._discover_files()
        logger.info(f"Found {len(files)} source files")
        
        # Step 2: Extract file structure
        structure = self._extract_structure(files)
        
        # Step 3: Analyze code patterns
        patterns = self._analyze_patterns(files)
        
        # Step 4: Extract dependencies
        dependencies = self._extract_dependencies(files)
        
        # Step 5: Identify business logic
        business_logic = self._identify_business_logic(files)
        
        # Step 6: AI-powered analysis
        ai_analysis = self._ai_analysis(files, structure, patterns)
        
        return {
            'source_path': str(self.source_path),
            'files': files,
            'structure': structure,
            'patterns': patterns,
            'dependencies': dependencies,
            'business_logic': business_logic,
            'ai_analysis': ai_analysis,
            'summary': {
                'total_files': len(files),
                'languages': self._detect_languages(files),
                'frameworks': self._detect_frameworks(files),
            }
        }
    
    def _discover_files(self) -> List[Dict[str, Any]]:
        """Discover all source files in the codebase"""
        files = []
        
        for ext in ['.java', '.py', '.js', '.ts', '.cs', '.cpp', '.c']:
            for file_path in self.source_path.rglob(f'*{ext}'):
                if self._should_analyze_file(file_path):
                    files.append({
                        'path': str(file_path.relative_to(self.source_path)),
                        'absolute_path': str(file_path),
                        'extension': ext,
                        'size': file_path.stat().st_size,
                        'lines': self._count_lines(file_path)
                    })
        
        return files
    
    def _should_analyze_file(self, file_path: Path) -> bool:
        """Check if file should be analyzed"""
        # Skip test files, build artifacts, etc.
        skip_patterns = ['test', 'Test', '__pycache__', 'node_modules', 
                        'target', 'build', '.git', 'venv', 'env']
        path_str = str(file_path)
        return not any(pattern in path_str for pattern in skip_patterns)
    
    def _count_lines(self, file_path: Path) -> int:
        """Count lines in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def _extract_structure(self, files: List[Dict]) -> Dict[str, Any]:
        """Extract code structure (packages, modules, classes, etc.)"""
        structure = {
            'packages': [],
            'modules': [],
            'classes': [],
            'functions': [],
            'endpoints': []
        }
        
        for file_info in files:
            ext = file_info['extension']
            if ext == '.java':
                struct = self._parse_java_structure(file_info)
            elif ext == '.py':
                struct = self._parse_python_structure(file_info)
            else:
                struct = {}
            
            structure['packages'].extend(struct.get('packages', []))
            structure['modules'].extend(struct.get('modules', []))
            structure['classes'].extend(struct.get('classes', []))
            structure['functions'].extend(struct.get('functions', []))
            structure['endpoints'].extend(struct.get('endpoints', []))
        
        return structure
    
    def _parse_java_structure(self, file_info: Dict) -> Dict[str, List]:
        """Parse Java file structure"""
        # Basic parsing - can be enhanced with tree-sitter
        file_path = Path(file_info['absolute_path'])
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            struct = {
                'packages': [],
                'classes': [],
                'functions': [],
                'endpoints': []
            }
            
            # Extract package
            import re
            package_match = re.search(r'package\s+([\w.]+);', content)
            if package_match:
                struct['packages'].append(package_match.group(1))
            
            # Extract classes
            class_matches = re.findall(r'(?:public\s+)?(?:class|interface|enum)\s+(\w+)', content)
            struct['classes'].extend([{'name': name, 'file': file_info['path']} for name in class_matches])
            
            # Extract REST endpoints
            endpoint_matches = re.findall(r'@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|RequestMapping)\([^)]*\)', content)
            struct['endpoints'].extend([{'pattern': match, 'file': file_info['path']} for match in endpoint_matches])
            
            return struct
        except Exception as e:
            logger.warning(f"Failed to parse {file_info['path']}: {e}")
            return {}
    
    def _parse_python_structure(self, file_info: Dict) -> Dict[str, List]:
        """Parse Python file structure"""
        file_path = Path(file_info['absolute_path'])
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            struct = {
                'modules': [],
                'classes': [],
                'functions': []
            }
            
            import re
            # Extract classes
            class_matches = re.findall(r'class\s+(\w+)', content)
            struct['classes'].extend([{'name': name, 'file': file_info['path']} for name in class_matches])
            
            # Extract functions
            func_matches = re.findall(r'def\s+(\w+)', content)
            struct['functions'].extend([{'name': name, 'file': file_info['path']} for name in func_matches])
            
            return struct
        except Exception as e:
            logger.warning(f"Failed to parse {file_info['path']}: {e}")
            return {}
    
    def _analyze_patterns(self, files: List[Dict]) -> Dict[str, Any]:
        """Analyze code patterns and conventions"""
        patterns = {
            'architecture': 'unknown',
            'design_patterns': [],
            'conventions': {}
        }
        
        # Analyze architecture
        for file_info in files:
            if 'controller' in file_info['path'].lower():
                patterns['architecture'] = 'mvc'
            elif 'service' in file_info['path'].lower():
                patterns['architecture'] = 'layered'
        
        return patterns
    
    def _extract_dependencies(self, files: List[Dict]) -> Dict[str, List]:
        """Extract dependencies from build files"""
        dependencies = {
            'maven': [],
            'npm': [],
            'pip': []
        }
        
        # Check for pom.xml (Maven)
        pom_path = self.source_path / 'pom.xml'
        if pom_path.exists():
            dependencies['maven'] = self._parse_maven_dependencies(pom_path)
        
        # Check for package.json (npm)
        package_json = self.source_path / 'package.json'
        if package_json.exists():
            dependencies['npm'] = self._parse_npm_dependencies(package_json)
        
        # Check for requirements.txt (pip)
        requirements = self.source_path / 'requirements.txt'
        if requirements.exists():
            dependencies['pip'] = self._parse_pip_dependencies(requirements)
        
        return dependencies
    
    def _parse_maven_dependencies(self, pom_path: Path) -> List[Dict]:
        """Parse Maven dependencies from pom.xml"""
        # Simplified parsing - can use xml.etree.ElementTree for full parsing
        try:
            content = pom_path.read_text()
            import re
            deps = re.findall(r'<dependency>.*?</dependency>', content, re.DOTALL)
            return [{'type': 'maven', 'raw': dep} for dep in deps[:10]]  # Limit for brevity
        except:
            return []
    
    def _parse_npm_dependencies(self, package_json: Path) -> List[Dict]:
        """Parse npm dependencies"""
        try:
            import json
            data = json.loads(package_json.read_text())
            deps = []
            for name, version in data.get('dependencies', {}).items():
                deps.append({'name': name, 'version': version})
            return deps
        except:
            return []
    
    def _parse_pip_dependencies(self, requirements: Path) -> List[str]:
        """Parse pip requirements"""
        try:
            return [line.strip() for line in requirements.read_text().split('\n') 
                   if line.strip() and not line.startswith('#')]
        except:
            return []
    
    def _identify_business_logic(self, files: List[Dict]) -> Dict[str, Any]:
        """Identify business logic and key components"""
        return {
            'services': [f for f in files if 'service' in f['path'].lower()],
            'controllers': [f for f in files if 'controller' in f['path'].lower()],
            'models': [f for f in files if 'model' in f['path'].lower()],
            'repositories': [f for f in files if 'repository' in f['path'].lower()],
        }
    
    def _ai_analysis(self, files: List[Dict], structure: Dict, patterns: Dict) -> Dict[str, Any]:
        """Use AI to perform deep analysis"""
        if not self.llm:
            return {}
        
        try:
            # Sample a few key files for AI analysis
            sample_files = files[:5]  # Analyze first 5 files
            file_contents = {}
            for file_info in sample_files:
                try:
                    file_path = Path(file_info['absolute_path'])
                    content = file_path.read_text(encoding='utf-8', errors='ignore')[:5000]  # Limit size
                    file_contents[file_info['path']] = content
                except:
                    pass
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a code analysis expert. Analyze the provided code and extract:"),
                ("system", "1. Architecture patterns\n2. Key business logic\n3. API endpoints\n4. Data models\n5. Dependencies"),
                ("human", "Analyze this codebase:\n\n{code}\n\nStructure: {structure}\n\nProvide a JSON analysis.")
            ])
            
            parser = JsonOutputParser()
            chain = prompt | self.llm | parser
            
            result = chain.invoke({
                'code': str(file_contents),
                'structure': str(structure)
            })
            
            return result
        except Exception as e:
            logger.warning(f"AI analysis failed: {e}")
            return {}
    
    def _detect_languages(self, files: List[Dict]) -> List[str]:
        """Detect programming languages in codebase"""
        languages = set()
        for file_info in files:
            ext = file_info['extension']
            lang_map = {
                '.java': 'Java',
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.cs': 'C#',
                '.cpp': 'C++',
                '.c': 'C'
            }
            if ext in lang_map:
                languages.add(lang_map[ext])
        return list(languages)
    
    def _detect_frameworks(self, files: List[Dict]) -> List[str]:
        """Detect frameworks used"""
        frameworks = []
        
        # Check for Spring Boot
        if any('spring' in str(f['path']).lower() for f in files):
            frameworks.append('Spring Boot')
        
        # Check for FastAPI/Flask
        if any('fastapi' in str(f['path']).lower() or 'flask' in str(f['path']).lower() for f in files):
            frameworks.append('Flask/FastAPI')
        
        return frameworks

