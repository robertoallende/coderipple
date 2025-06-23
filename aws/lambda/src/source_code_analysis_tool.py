"""
Source Code Analysis Tool

Analyzes project source code to understand functionality, structure, and purpose.
This tool provides the foundational understanding that agents need to generate
meaningful documentation, rather than relying solely on git diffs.

Source code analysis for intelligent documentation generation.
"""

import os
import ast
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

try:
    from strands import tool
except ImportError:
    def tool(func):
        return func


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, etc.)"""
    name: str
    type: str  # 'function', 'class', 'method'
    docstring: Optional[str]
    file_path: str
    line_number: int
    signature: Optional[str] = None
    complexity_score: int = 1


@dataclass
class ProjectAnalysis:
    """Complete analysis of project source code"""
    project_name: str
    main_purpose: str
    key_technologies: List[str]
    main_modules: List[str]
    public_api: List[CodeEntity]
    internal_functions: List[CodeEntity]
    entry_points: List[str]
    dependencies: List[str]
    project_structure: Dict[str, Any]
    total_files: int
    total_lines: int


class SourceCodeAnalyzer:
    """Analyzes Python source code to extract meaningful project information"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.src_dirs = ["src", "lib", "."]  # Common source directories
        
    def analyze_project(self) -> ProjectAnalysis:
        """
        Perform comprehensive project analysis
        
        Returns:
            ProjectAnalysis with complete project understanding
        """
        # Find actual source directory
        source_dir = self._find_source_directory()
        
        # Analyze all Python files
        python_files = self._find_python_files(source_dir)
        
        # Extract code entities
        all_entities = []
        total_lines = 0
        
        for file_path in python_files:
            entities, lines = self._analyze_file(file_path)
            all_entities.extend(entities)
            total_lines += lines
        
        # Categorize entities
        public_api = [e for e in all_entities if self._is_public_api(e)]
        internal_functions = [e for e in all_entities if not self._is_public_api(e)]
        
        # Determine project characteristics
        project_name = self._infer_project_name()
        main_purpose = self._infer_main_purpose(all_entities, python_files)
        key_technologies = self._detect_technologies(python_files)
        main_modules = self._identify_main_modules(python_files)
        entry_points = self._find_entry_points(python_files)
        dependencies = self._extract_dependencies()
        project_structure = self._analyze_structure()
        
        return ProjectAnalysis(
            project_name=project_name,
            main_purpose=main_purpose,
            key_technologies=key_technologies,
            main_modules=main_modules,
            public_api=public_api,
            internal_functions=internal_functions,
            entry_points=entry_points,
            dependencies=dependencies,
            project_structure=project_structure,
            total_files=len(python_files),
            total_lines=total_lines
        )
    
    def _find_source_directory(self) -> Path:
        """Find the main source directory"""
        for src_dir in self.src_dirs:
            path = self.project_root / src_dir
            if path.exists() and any(path.glob("*.py")):
                # Skip __pycache__ directories
                if src_dir != "__pycache__" and "__pycache__" not in str(path):
                    return path
        return self.project_root
    
    def _find_python_files(self, source_dir: Path) -> List[Path]:
        """Find all Python files in source directory"""
        python_files = []
        
        # Look for .py files, excluding test files and __pycache__
        for file_path in source_dir.rglob("*.py"):
            if "__pycache__" in str(file_path):
                continue
            if file_path.name.startswith("test_"):
                continue
            python_files.append(file_path)
        
        return python_files
    
    def _analyze_file(self, file_path: Path) -> tuple[List[CodeEntity], int]:
        """Analyze a single Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            entities = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    entity = CodeEntity(
                        name=node.name,
                        type='function',
                        docstring=ast.get_docstring(node),
                        file_path=str(file_path),
                        line_number=node.lineno,
                        signature=self._extract_function_signature(node)
                    )
                    entities.append(entity)
                
                elif isinstance(node, ast.ClassDef):
                    entity = CodeEntity(
                        name=node.name,
                        type='class',
                        docstring=ast.get_docstring(node),
                        file_path=str(file_path),
                        line_number=node.lineno
                    )
                    entities.append(entity)
            
            lines = len(content.splitlines())
            return entities, lines
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return [], 0
    
    def _extract_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract function signature as string"""
        try:
            args = []
            for arg in node.args.args:
                args.append(arg.arg)
            return f"{node.name}({', '.join(args)})"
        except:
            return node.name
    
    def _is_public_api(self, entity: CodeEntity) -> bool:
        """Determine if entity is part of public API"""
        # Public if: not starting with _, has docstring, in main modules
        if entity.name.startswith('_'):
            return False
        if entity.docstring:
            return True
        if 'main' in entity.file_path or 'api' in entity.file_path:
            return True
        return False
    
    def _infer_project_name(self) -> str:
        """Infer project name from directory structure"""
        # Get the actual directory name (resolve if it's relative)
        resolved_path = self.project_root.resolve()
        project_name = resolved_path.name
        
        # If project_name is not meaningful, try other sources
        if project_name in ['__pycache__', '.', '..'] or project_name.startswith('.'):
            # Check for package name in src directory
            src_path = resolved_path / "src"
            if src_path.exists():
                subdirs = [d for d in src_path.iterdir() 
                          if d.is_dir() and not d.name.startswith('.') and d.name != '__pycache__']
                if subdirs:
                    project_name = subdirs[0].name
        
        return project_name
    
    def _infer_main_purpose(self, entities: List[CodeEntity], files: List[Path]) -> str:
        """Infer main project purpose from code analysis"""
        # Analyze function names, docstrings, and file names for patterns
        keywords = []
        
        # Extract keywords from function names
        for entity in entities:
            words = re.findall(r'[A-Z][a-z]*|[a-z]+', entity.name)
            keywords.extend(words)
        
        # Extract from docstrings
        for entity in entities:
            if entity.docstring:
                words = re.findall(r'\b[a-z]{4,}\b', entity.docstring.lower())
                keywords.extend(words)
        
        # Extract from file names
        for file_path in files:
            words = re.findall(r'[a-z]+', file_path.stem.lower())
            keywords.extend(words)
        
        # Find most common meaningful keywords
        from collections import Counter
        all_word_counts = Counter(keywords)
        
        # Check for specific patterns in all keywords (not just top 10)
        webhook_mentions = sum(count for word, count in all_word_counts.items() if 'webhook' in word.lower())
        agent_mentions = sum(count for word, count in all_word_counts.items() if 'agent' in word.lower())
        doc_mentions = sum(count for word, count in all_word_counts.items() if any(d in word.lower() for d in ['doc', 'documentation']))
        
        # Get top words for fallback description
        common_words = all_word_counts.most_common(10)
        
        if webhook_mentions > 0 and agent_mentions > 0:
            return "Multi-agent documentation system that processes webhooks"
        elif agent_mentions >= 3:  # Significant agent presence
            return "Multi-agent coordination and automation system"
        elif doc_mentions > 0 and agent_mentions > 0:
            return "Agent-based documentation generation system"
        elif webhook_mentions > 0:
            return "Webhook processing and analysis system"
        elif any('api' in word.lower() for word, _ in common_words):
            return "API service and integration platform"
        else:
            return f"Python application with focus on {', '.join([w for w, _ in common_words[:3]])}"
    
    def _detect_technologies(self, files: List[Path]) -> List[str]:
        """Detect key technologies used in the project"""
        technologies = set()
        
        # Check imports in files
        for file_path in files:
            try:
                # Skip analyzing this analysis tool itself to avoid false positives
                if 'source_code_analysis_tool.py' in str(file_path):
                    continue
                    
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Look for actual imports, not just string mentions
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    
                    # Skip comments
                    if line.startswith('#'):
                        continue
                        
                    # Check for actual import statements
                    if 'import boto3' in line or 'from boto3' in line:
                        technologies.add('AWS SDK (boto3)')
                    if 'import requests' in line or 'from requests' in line:
                        technologies.add('HTTP Requests')
                    if 'from flask' in line or 'import flask' in line:
                        technologies.add('Flask')
                    if 'from fastapi' in line or 'import fastapi' in line:
                        technologies.add('FastAPI')
                    if 'from starlette' in line or 'import starlette' in line:
                        technologies.add('Starlette')
                    if 'import asyncio' in line or 'from asyncio' in line:
                        technologies.add('Async/Await')
                    if 'from strands' in line or 'import strands' in line:
                        technologies.add('AWS Strands')
                    if '@dataclass' in line:
                        technologies.add('Python Dataclasses')
                
                # Check for bedrock usage (case-insensitive, but exclude analysis tools)
                if 'bedrock' in content.lower() and 'bedrock_integration' in str(file_path):
                    technologies.add('Amazon Bedrock')
                    
            except Exception:
                continue
        
        return list(technologies)
    
    def _identify_main_modules(self, files: List[Path]) -> List[str]:
        """Identify main modules/components"""
        modules = []
        
        for file_path in files:
            module_name = file_path.stem
            if module_name != '__init__':
                modules.append(module_name)
        
        # Sort by likely importance (main modules first)
        def module_priority(name):
            if 'main' in name:
                return 0
            if 'agent' in name:
                return 1
            if 'webhook' in name:
                return 2
            return 3
        
        modules.sort(key=module_priority)
        return modules[:10]  # Top 10 modules
    
    def _find_entry_points(self, files: List[Path]) -> List[str]:
        """Find potential entry points (main functions, CLI commands)"""
        entry_points = []
        
        for file_path in files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Look for main patterns
                if 'if __name__ == "__main__"' in content:
                    entry_points.append(f"python {file_path.name}")
                
                # Look for CLI patterns
                if 'argparse' in content or 'click' in content:
                    entry_points.append(f"CLI in {file_path.name}")
                    
            except Exception:
                continue
        
        return entry_points
    
    def _extract_dependencies(self) -> List[str]:
        """Extract project dependencies"""
        dependencies = []
        
        # Check requirements.txt
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifiers)
                            package = re.split(r'[>=<!=]', line)[0].strip()
                            dependencies.append(package)
            except Exception:
                pass
        
        return dependencies
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """Analyze project structure"""
        structure = {
            'has_src_dir': (self.project_root / 'src').exists(),
            'has_tests': (self.project_root / 'tests').exists(),
            'has_docs': any((self.project_root / d).exists() for d in ['docs', 'doc', 'documentation']),
            'has_config': any((self.project_root / f).exists() for f in ['setup.py', 'pyproject.toml', 'requirements.txt']),
            'directories': [d.name for d in self.project_root.iterdir() if d.is_dir() and not d.name.startswith('.')]
        }
        
        return structure


@tool
def analyze_source_code(project_root: str = ".") -> Dict[str, Any]:
    """
    Analyze project source code to understand functionality and structure.
    
    This tool provides foundational understanding of what the project actually does,
    enabling agents to generate meaningful documentation based on real code analysis
    rather than just git diffs.
    
    Args:
        project_root: Path to project root directory
        
    Returns:
        Dictionary containing comprehensive project analysis including:
        - Project purpose and main functionality
        - Key technologies and dependencies
        - Public API and internal structure
        - Entry points and usage patterns
    """
    try:
        analyzer = SourceCodeAnalyzer(project_root)
        analysis = analyzer.analyze_project()
        
        # Convert to dictionary for easy consumption by agents
        return {
            'status': 'success',
            'project_name': analysis.project_name,
            'main_purpose': analysis.main_purpose,
            'key_technologies': analysis.key_technologies,
            'main_modules': analysis.main_modules,
            'public_api': [
                {
                    'name': entity.name,
                    'type': entity.type,
                    'description': entity.docstring or f"{entity.type.title()} in {os.path.basename(entity.file_path)}",
                    'file': os.path.basename(entity.file_path),
                    'signature': entity.signature
                }
                for entity in analysis.public_api[:20]  # Top 20 public APIs
            ],
            'entry_points': analysis.entry_points,
            'dependencies': analysis.dependencies,
            'project_structure': analysis.project_structure,
            'statistics': {
                'total_files': analysis.total_files,
                'total_lines': analysis.total_lines,
                'public_api_count': len(analysis.public_api),
                'internal_functions_count': len(analysis.internal_functions)
            },
            'summary': f"'{analysis.project_name}' is a {analysis.main_purpose} with {len(analysis.main_modules)} main modules, using {', '.join(analysis.key_technologies[:3])}."
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'project_name': 'unknown',
            'main_purpose': 'Unable to analyze project structure',
            'summary': f"Source code analysis failed: {str(e)}"
        }


if __name__ == "__main__":
    # Test the tool on current project
    result = analyze_source_code(".")
    
    print("=== Source Code Analysis Test ===")
    print(f"Status: {result['status']}")
    print(f"Project: {result['project_name']}")
    print(f"Purpose: {result['main_purpose']}")
    print(f"Technologies: {', '.join(result['key_technologies'])}")
    print(f"Main Modules: {', '.join(result['main_modules'][:5])}")
    print(f"Statistics: {result['statistics']}")
    print(f"Summary: {result['summary']}")
    
    if result['public_api']:
        print(f"\nPublic API (first 5):")
        for api in result['public_api'][:5]:
            print(f"  - {api['name']} ({api['type']}): {api['description'][:60]}...")