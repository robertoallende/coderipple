"""
Content Validation Tools for CodeRipple Documentation System

This module provides comprehensive validation for generated documentation content,
including markdown syntax, code examples, cross-references, and quality standards.
"""

import re
import os
import ast
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from markdown_it import MarkdownIt
from strands import tool


@dataclass
class ValidationResult:
    """Results from content validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    quality_score: float = 0.0
    suggestions: List[str] = field(default_factory=list)


@dataclass
class DetailedValidationResult:
    """Enhanced validation results with detailed breakdowns."""
    is_valid: bool
    overall_quality_score: float
    category_scores: Dict[str, float] = field(default_factory=dict)
    category_details: Dict[str, Dict] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    improvement_actions: List[str] = field(default_factory=list)
    threshold_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeExample:
    """Represents a code example found in documentation."""
    content: str
    language: str
    line_number: int
    context: str


@dataclass
class CrossReference:
    """Represents a cross-reference link in documentation."""
    text: str
    target: str
    line_number: int
    link_type: str  # 'file', 'section', 'external'


class ContentValidator:
    """Core validation logic for documentation content."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.md_parser = MarkdownIt()
        
    def validate_markdown_syntax(self, content: str, file_path: str = None) -> ValidationResult:
        """Validate markdown syntax and formatting."""
        result = ValidationResult(is_valid=True)
        
        if not content.strip():
            result.errors.append("Content is empty")
            result.is_valid = False
            return result
        
        try:
            # Parse markdown to check for syntax errors
            tokens = self.md_parser.parse(content)
            
            # Check for common markdown issues
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                # Check for malformed headers
                if line.strip().startswith('#'):
                    if not re.match(r'^#{1,6}\s+.+', line):
                        result.errors.append(f"Line {i}: Malformed header - missing space after #")
                        result.is_valid = False
                    # Check for too many hash symbols
                    if line.strip().startswith('#######'):
                        result.errors.append(f"Line {i}: Too many # symbols (max 6 for headers)")
                        result.is_valid = False
                
                # Check for severely unmatched brackets
                bracket_diff = abs(line.count('[') - line.count(']'))
                if bracket_diff > 2:  # Allow some tolerance, but flag severe mismatches
                    result.errors.append(f"Line {i}: Severely unmatched square brackets")
                    result.is_valid = False
                elif bracket_diff > 0:
                    result.warnings.append(f"Line {i}: Unmatched square brackets")
                
                paren_diff = abs(line.count('(') - line.count(')'))
                if paren_diff > 2:  # Allow some tolerance
                    result.errors.append(f"Line {i}: Severely unmatched parentheses")
                    result.is_valid = False
                elif paren_diff > 0:
                    result.warnings.append(f"Line {i}: Unmatched parentheses")
                
                # Check for trailing whitespace
                if line.endswith(' ') or line.endswith('\t'):
                    result.warnings.append(f"Line {i}: Trailing whitespace")
                    
            # Check for unclosed code blocks
            code_block_count = content.count('```')
            if code_block_count % 2 != 0:
                result.errors.append("Unclosed code block detected")
                result.is_valid = False
                    
            # Check for empty code blocks
            code_block_pattern = r'```[\w]*\n\s*\n```'
            if re.search(code_block_pattern, content):
                result.warnings.append("Found empty code blocks")
                
            # Check for missing alt text in images
            img_pattern = r'!\[\]\([^)]+\)'
            if re.search(img_pattern, content):
                result.warnings.append("Images missing alt text")
                
        except Exception as e:
            result.errors.append(f"Markdown parsing error: {str(e)}")
            result.is_valid = False
            
        return result
    
    def extract_code_examples(self, content: str) -> List[CodeExample]:
        """Extract code examples from markdown content."""
        examples = []
        lines = content.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Look for fenced code blocks
            if line.strip().startswith('```'):
                language = line.strip()[3:].strip() or 'text'
                code_lines = []
                i += 1
                start_line = i
                
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                    
                if code_lines:
                    # Get context (previous line)
                    context = lines[start_line - 2] if start_line > 1 else ""
                    examples.append(CodeExample(
                        content='\n'.join(code_lines),
                        language=language,
                        line_number=start_line,
                        context=context
                    ))
            i += 1
            
        return examples
    
    def validate_code_examples(self, examples: List[CodeExample], project_root: str = None) -> ValidationResult:
        """Validate that code examples reference current system capabilities."""
        result = ValidationResult(is_valid=True)
        
        # Get current system capabilities
        capabilities = self._get_system_capabilities(project_root or str(self.project_root))
        
        for example in examples:
            # Validate Python code syntax
            if example.language.lower() in ['python', 'py']:
                try:
                    ast.parse(example.content)
                except SyntaxError as e:
                    result.errors.append(f"Line {example.line_number}: Python syntax error - {str(e)}")
                    result.is_valid = False
                    
                # Check if imports reference existing modules
                imports = self._extract_imports(example.content)
                for imp in imports:
                    if not self._check_import_exists(imp, capabilities):
                        result.warnings.append(f"Line {example.line_number}: Import '{imp}' may not exist in current system")
                        
            # Validate shell commands
            elif example.language.lower() in ['bash', 'sh', 'shell']:
                commands = self._extract_shell_commands(example.content)
                for cmd in commands:
                    if not self._check_command_exists(cmd, capabilities):
                        result.warnings.append(f"Line {example.line_number}: Command '{cmd}' may not be available")
                        
            # Check for references to project files/functions
            file_refs = self._extract_file_references(example.content)
            for ref in file_refs:
                if not self._check_file_reference(ref, capabilities):
                    result.warnings.append(f"Line {example.line_number}: File reference '{ref}' may not exist")
                    
        return result
    
    def extract_cross_references(self, content: str) -> List[CrossReference]:
        """Extract cross-reference links from markdown content."""
        references = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Find markdown links [text](url)
            link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
            matches = re.finditer(link_pattern, line)
            
            for match in matches:
                text, target = match.groups()
                link_type = self._classify_link_type(target)
                references.append(CrossReference(
                    text=text,
                    target=target,
                    line_number=i,
                    link_type=link_type
                ))
                
        return references
    
    def validate_cross_references(self, references: List[CrossReference], project_root: str = None) -> ValidationResult:
        """Validate that cross-reference links work correctly."""
        result = ValidationResult(is_valid=True)
        root_path = Path(project_root) if project_root else self.project_root
        
        for ref in references:
            if ref.link_type == 'file':
                # Check if file exists
                target_path = root_path / ref.target.lstrip('./')
                if not target_path.exists():
                    result.errors.append(f"Line {ref.line_number}: File '{ref.target}' does not exist")
                    result.is_valid = False
                    
            elif ref.link_type == 'section':
                # Check if section anchor exists (basic check)
                if '#' in ref.target:
                    file_part, anchor = ref.target.split('#', 1)
                    if file_part:
                        target_path = root_path / file_part.lstrip('./')
                        if target_path.exists():
                            # Check if anchor exists in target file
                            if not self._check_anchor_exists(target_path, anchor):
                                result.warnings.append(f"Line {ref.line_number}: Anchor '#{anchor}' may not exist in {file_part}")
                        else:
                            result.errors.append(f"Line {ref.line_number}: File '{file_part}' does not exist")
                            result.is_valid = False
                            
        return result
    
    def calculate_quality_score(self, content: str, validation_results: List[ValidationResult]) -> float:
        """Calculate overall quality score for content."""
        if not content.strip():
            return 0.0
            
        # Base score
        score = 50.0  # Start with neutral score
        
        # Penalize for validation errors and warnings
        for result in validation_results:
            score -= len(result.errors) * 15  # -15 points per error (more severe)
            score -= len(result.warnings) * 3  # -3 points per warning
            
        # Content quality factors
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Score based on content length
        if len(non_empty_lines) < 3:
            score -= 30  # Very short content penalty
        elif len(non_empty_lines) < 5:
            score -= 15  # Short content penalty
        elif len(non_empty_lines) >= 10:
            score += 15  # Good length bonus
        elif len(non_empty_lines) >= 20:
            score += 25  # Substantial content bonus
            
        # Reward good structure (headers, lists, code blocks)
        structure_bonus = 0
        if re.search(r'^#{1,6}\s+', content, re.MULTILINE):
            structure_bonus += 10  # Has headers
        if re.search(r'^[-*+]\s+', content, re.MULTILINE):
            structure_bonus += 8  # Has lists
        if '```' in content:
            structure_bonus += 12  # Has code blocks
        if re.search(r'\[.*\]\(.*\)', content):
            structure_bonus += 5  # Has links
            
        score += structure_bonus
        
        # Penalize obvious quality issues
        if len(content) < 50:
            score -= 25  # Too short
        if not re.search(r'^#', content, re.MULTILINE):
            score -= 10  # No headers
            
        # Normalize to 0-100 range
        return max(0.0, min(100.0, score))
    
    def calculate_detailed_quality_scores(self, content: str, validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """
        Calculate detailed quality scores broken down by category.
        
        Returns detailed breakdown for enhanced diagnostics.
        """
        if not content.strip():
            return {
                'overall_score': 0.0,
                'category_scores': {
                    'content_structure': 0.0,
                    'markdown_syntax': 0.0,
                    'code_examples': 0.0,
                    'cross_references': 0.0,
                    'completeness': 0.0,
                    'readability': 0.0
                },
                'detailed_breakdown': {
                    'content_structure': {'score': 0.0, 'issues': ['Content is empty'], 'suggestions': ['Add meaningful content']},
                    'markdown_syntax': {'score': 0.0, 'issues': ['No content to analyze'], 'suggestions': []},
                    'code_examples': {'score': 0.0, 'issues': ['No content to analyze'], 'suggestions': []},
                    'cross_references': {'score': 0.0, 'issues': ['No content to analyze'], 'suggestions': []},
                    'completeness': {'score': 0.0, 'issues': ['Content is empty'], 'suggestions': ['Add comprehensive content']},
                    'readability': {'score': 0.0, 'issues': ['No content to analyze'], 'suggestions': []}
                }
            }
        
        # Initialize category scores
        scores = {}
        details = {}
        
        # 1. Content Structure (25% weight)
        structure_score, structure_details = self._analyze_content_structure(content)
        scores['content_structure'] = structure_score
        details['content_structure'] = structure_details
        
        # 2. Markdown Syntax (20% weight) 
        syntax_score, syntax_details = self._analyze_markdown_syntax(content, validation_results)
        scores['markdown_syntax'] = syntax_score
        details['markdown_syntax'] = syntax_details
        
        # 3. Code Examples (15% weight)
        code_score, code_details = self._analyze_code_examples(content)
        scores['code_examples'] = code_score
        details['code_examples'] = code_details
        
        # 4. Cross References (10% weight)
        ref_score, ref_details = self._analyze_cross_references(content)
        scores['cross_references'] = ref_score
        details['cross_references'] = ref_details
        
        # 5. Completeness (20% weight)
        completeness_score, completeness_details = self._analyze_completeness(content)
        scores['completeness'] = completeness_score
        details['completeness'] = completeness_details
        
        # 6. Readability (10% weight)
        readability_score, readability_details = self._analyze_readability(content)
        scores['readability'] = readability_score
        details['readability'] = readability_details
        
        # Calculate weighted overall score
        weights = {
            'content_structure': 0.25,
            'markdown_syntax': 0.20,
            'code_examples': 0.15,
            'cross_references': 0.10,
            'completeness': 0.20,
            'readability': 0.10
        }
        
        overall_score = sum(scores[category] * weights[category] for category in scores)
        
        return {
            'overall_score': overall_score,
            'category_scores': scores,
            'detailed_breakdown': details,
            'weights_used': weights
        }
    
    def _analyze_content_structure(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze content structure quality."""
        score = 100.0
        issues = []
        suggestions = []
        
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Check for proper headers
        headers = [line for line in lines if re.match(r'^#{1,6}\s+', line)]
        if not headers:
            score -= 30
            issues.append("No headers found")
            suggestions.append("Add section headers using # markdown syntax")
        elif len(headers) == 1:
            score -= 10
            suggestions.append("Consider adding subsection headers for better organization")
        
        # Check for proper introduction
        if not re.search(r'^[A-Z].*[.!?]$', content[:200], re.MULTILINE):
            score -= 15
            issues.append("Missing clear introduction")
            suggestions.append("Start with a clear introductory paragraph")
        
        # Check content length
        if len(non_empty_lines) < 5:
            score -= 25
            issues.append(f"Content too short ({len(non_empty_lines)} lines)")
            suggestions.append("Expand content with more detailed information")
        elif len(non_empty_lines) < 10:
            score -= 10
            suggestions.append("Consider adding more detail for comprehensive coverage")
        
        # Check for lists and organization
        has_lists = bool(re.search(r'^[-*+]\s+', content, re.MULTILINE))
        if not has_lists and len(non_empty_lines) > 10:
            score -= 10
            suggestions.append("Consider organizing information into lists for better readability")
        
        return max(0.0, score), {
            'score': max(0.0, score),
            'issues': issues,
            'suggestions': suggestions,
            'metrics': {
                'header_count': len(headers),
                'line_count': len(non_empty_lines),
                'has_lists': has_lists
            }
        }
    
    def _analyze_markdown_syntax(self, content: str, validation_results: List[ValidationResult]) -> Tuple[float, Dict[str, Any]]:
        """Analyze markdown syntax quality."""
        score = 100.0
        issues = []
        suggestions = []
        
        # Count syntax errors from validation results
        syntax_errors = []
        for result in validation_results:
            syntax_errors.extend([err for err in result.errors if 'syntax' in err.lower() or 'markdown' in err.lower()])
        
        # Penalize for syntax errors
        if syntax_errors:
            score -= len(syntax_errors) * 20
            issues.extend(syntax_errors)
            suggestions.append("Fix markdown syntax errors")
        
        # Check for common markdown issues
        if '```' in content and content.count('```') % 2 != 0:
            score -= 15
            issues.append("Unclosed code block")
            suggestions.append("Ensure all code blocks are properly closed")
        
        # Check for proper link formatting
        broken_links = re.findall(r'\[([^\]]*)\]\s*\(([^)]*)\)', content)
        if any(not url.strip() for text, url in broken_links):
            score -= 10
            issues.append("Broken or empty links found")
            suggestions.append("Fix broken link references")
        
        return max(0.0, score), {
            'score': max(0.0, score),
            'issues': issues,
            'suggestions': suggestions,
            'metrics': {
                'syntax_errors_count': len(syntax_errors),
                'code_blocks_balanced': '```' not in content or content.count('```') % 2 == 0,
                'link_count': len(broken_links)
            }
        }
    
    def _analyze_code_examples(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze code examples quality."""
        score = 80.0  # Start at 80 since code examples are optional for some docs
        issues = []
        suggestions = []
        
        code_blocks = re.findall(r'```(\w*)\n(.*?)\n```', content, re.DOTALL)
        
        if not code_blocks:
            score = 60.0  # Not critical but reduces score
            suggestions.append("Consider adding code examples to illustrate concepts")
        else:
            # Check for language specification
            unspecified_blocks = [block for lang, code in code_blocks if not lang.strip()]
            if unspecified_blocks:
                score -= 10
                issues.append(f"{len(unspecified_blocks)} code blocks missing language specification")
                suggestions.append("Specify programming language for code blocks (e.g., ```python)")
            
            # Check for meaningful content in code blocks
            empty_blocks = [block for lang, code in code_blocks if not code.strip()]
            if empty_blocks:
                score -= 15
                issues.append(f"{len(empty_blocks)} empty code blocks")
                suggestions.append("Remove empty code blocks or add meaningful examples")
            
            # Bonus for good code examples
            if len(code_blocks) >= 2:
                score += 10
                
        return max(0.0, score), {
            'score': max(0.0, score),
            'issues': issues,
            'suggestions': suggestions,
            'metrics': {
                'code_blocks_count': len(code_blocks),
                'specified_language_count': len([1 for lang, code in code_blocks if lang.strip()]),
                'non_empty_count': len([1 for lang, code in code_blocks if code.strip()])
            }
        }
    
    def _analyze_cross_references(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze cross-references quality."""
        score = 80.0  # Start at 80 since cross-refs are nice to have
        issues = []
        suggestions = []
        
        links = re.findall(r'\[([^\]]*)\]\(([^)]*)\)', content)
        internal_links = [(text, url) for text, url in links if not url.startswith(('http://', 'https://'))]
        external_links = [(text, url) for text, url in links if url.startswith(('http://', 'https://'))]
        
        if not links:
            score = 70.0
            suggestions.append("Consider adding links to related documentation or external resources")
        else:
            # Check for descriptive link text
            poor_link_text = [text for text, url in links if text.lower().strip() in ['click here', 'here', 'link']]
            if poor_link_text:
                score -= 10
                issues.append(f"{len(poor_link_text)} links with non-descriptive text")
                suggestions.append("Use descriptive text for links instead of 'click here' or 'here'")
            
            # Bonus for having both internal and external links
            if internal_links and external_links:
                score += 10
        
        return max(0.0, score), {
            'score': max(0.0, score),
            'issues': issues,
            'suggestions': suggestions,
            'metrics': {
                'total_links': len(links),
                'internal_links': len(internal_links),
                'external_links': len(external_links)
            }
        }
    
    def _analyze_completeness(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze content completeness."""
        score = 100.0
        issues = []
        suggestions = []
        
        # Check for placeholder content
        placeholders = re.findall(r'TODO|FIXME|XXX|\[placeholder\]|\.\.\.|TBD', content, re.IGNORECASE)
        if placeholders:
            score -= len(placeholders) * 15
            issues.append(f"{len(placeholders)} placeholder items found")
            suggestions.append("Replace placeholder content with actual information")
        
        # Check for minimum content depth
        paragraphs = re.split(r'\n\s*\n', content.strip())
        substantial_paragraphs = [p for p in paragraphs if len(p.strip()) > 50]
        
        if len(substantial_paragraphs) < 2:
            score -= 20
            issues.append("Content lacks depth - too few substantial paragraphs")
            suggestions.append("Expand content with more detailed explanations")
        elif len(substantial_paragraphs) < 3:
            score -= 10
            suggestions.append("Consider adding more detail for comprehensive coverage")
        
        # Check for conclusion or next steps
        has_conclusion = bool(re.search(r'(conclusion|summary|next steps?|what\'s next)', content, re.IGNORECASE))
        if len(content) > 500 and not has_conclusion:
            score -= 5
            suggestions.append("Consider adding a conclusion or next steps section")
        
        return max(0.0, score), {
            'score': max(0.0, score),
            'issues': issues,
            'suggestions': suggestions,
            'metrics': {
                'placeholder_count': len(placeholders),
                'paragraph_count': len(paragraphs),
                'substantial_paragraphs': len(substantial_paragraphs),
                'has_conclusion': has_conclusion
            }
        }
    
    def _analyze_readability(self, content: str) -> Tuple[float, Dict[str, Any]]:
        """Analyze content readability."""
        score = 100.0
        issues = []
        suggestions = []
        
        # Check sentence length
        sentences = re.split(r'[.!?]+', content)
        long_sentences = [s for s in sentences if len(s.strip().split()) > 25]
        if long_sentences:
            score -= len(long_sentences) * 5
            if len(long_sentences) > 3:
                issues.append(f"{len(long_sentences)} very long sentences found")
                suggestions.append("Break down long sentences for better readability")
        
        # Check for overly technical jargon without explanation
        technical_terms = re.findall(r'\b[A-Z]{2,}\b', content)  # All-caps technical terms
        if len(technical_terms) > 5:
            score -= 5
            suggestions.append("Consider explaining technical abbreviations and acronyms")
        
        # Check paragraph length
        paragraphs = re.split(r'\n\s*\n', content.strip())
        long_paragraphs = [p for p in paragraphs if len(p.split()) > 100]
        if long_paragraphs:
            score -= len(long_paragraphs) * 3
            if len(long_paragraphs) > 2:
                suggestions.append("Consider breaking up long paragraphs for better readability")
        
        return max(0.0, score), {
            'score': max(0.0, score),
            'issues': issues,
            'suggestions': suggestions,
            'metrics': {
                'long_sentences_count': len(long_sentences),
                'technical_terms_count': len(technical_terms),
                'long_paragraphs_count': len(long_paragraphs),
                'avg_sentence_length': sum(len(s.split()) for s in sentences) / max(1, len(sentences))
            }
        }
    
    def _get_system_capabilities(self, project_root: str) -> Dict[str, Any]:
        """Extract current system capabilities from project structure."""
        capabilities = {
            'modules': set(),
            'functions': set(),
            'classes': set(),
            'files': set(),
            'commands': set()
        }
        
        root_path = Path(project_root)
        
        # Scan Python files for imports, functions, classes
        for py_file in root_path.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Parse AST to extract definitions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        capabilities['functions'].add(node.name)
                    elif isinstance(node, ast.ClassDef):
                        capabilities['classes'].add(node.name)
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            capabilities['modules'].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            capabilities['modules'].add(node.module)
                            
                capabilities['files'].add(str(py_file.relative_to(root_path)))
                
            except Exception:
                continue  # Skip files that can't be parsed
                
        # Check for common commands in scripts
        for script_file in root_path.rglob('*.sh'):
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    commands = re.findall(r'^\s*([a-zA-Z_][a-zA-Z0-9_-]*)', content, re.MULTILINE)
                    capabilities['commands'].update(commands)
            except Exception:
                continue
                
        return capabilities
    
    def _extract_imports(self, code: str) -> List[str]:
        """Extract import statements from Python code."""
        imports = []
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception:
            pass
        return imports
    
    def _extract_shell_commands(self, code: str) -> List[str]:
        """Extract commands from shell code."""
        commands = []
        lines = code.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                # Extract first word as command
                cmd = line.split()[0] if line.split() else ''
                if cmd:
                    commands.append(cmd)
        return commands
    
    def _extract_file_references(self, code: str) -> List[str]:
        """Extract file path references from code."""
        # Look for common file path patterns
        patterns = [
            r'["\']([^"\']*\.py)["\']',  # Python files
            r'["\']([^"\']*\.md)["\']',  # Markdown files
            r'["\']([^"\']*\.json)["\']',  # JSON files
            r'["\']([^"\']*\.yaml?)["\']',  # YAML files
            r'["\']([^"\']*\.txt)["\']',  # Text files
        ]
        
        references = []
        for pattern in patterns:
            matches = re.findall(pattern, code)
            references.extend(matches)
            
        return references
    
    def _check_import_exists(self, import_name: str, capabilities: Dict[str, Any]) -> bool:
        """Check if an import exists in current system."""
        return import_name in capabilities['modules']
    
    def _check_command_exists(self, command: str, capabilities: Dict[str, Any]) -> bool:
        """Check if a command exists in current system."""
        # Check in project capabilities
        if command in capabilities['commands']:
            return True
            
        # Check if it's a common system command
        try:
            result = subprocess.run(['which', command], capture_output=True, text=True)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_file_reference(self, file_path: str, capabilities: Dict[str, Any]) -> bool:
        """Check if a file reference exists in current system."""
        return file_path in capabilities['files']
    
    def _classify_link_type(self, target: str) -> str:
        """Classify the type of a link target."""
        if target.startswith(('http://', 'https://')):
            return 'external'
        elif '#' in target:
            return 'section'
        else:
            return 'file'
    
    def _check_anchor_exists(self, file_path: Path, anchor: str) -> bool:
        """Check if an anchor exists in a markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Convert anchor to expected header format
            expected_headers = [
                f"# {anchor.replace('-', ' ').title()}",
                f"## {anchor.replace('-', ' ').title()}",
                f"### {anchor.replace('-', ' ').title()}",
                f"#### {anchor.replace('-', ' ').title()}",
                f"##### {anchor.replace('-', ' ').title()}",
                f"###### {anchor.replace('-', ' ').title()}",
            ]
            
            for header in expected_headers:
                if header.lower() in content.lower():
                    return True
                    
            return False
            
        except Exception:
            return False


@tool
def validate_documentation_quality(file_path: str, content: str, project_root: str = None) -> dict:
    """
    Validate generated documentation content for quality and correctness.
    
    Performs comprehensive validation including:
    - Markdown syntax and formatting
    - Code example validation
    - Cross-reference link validation
    - Overall quality scoring
    
    Args:
        file_path: Path to the documentation file being validated
        content: The content to validate
        project_root: Root directory of the project (optional)
        
    Returns:
        Dictionary containing validation results with errors, warnings, and quality score
    """
    validator = ContentValidator(project_root)
    
    # Perform all validations
    markdown_result = validator.validate_markdown_syntax(content, file_path)
    
    code_examples = validator.extract_code_examples(content)
    code_result = validator.validate_code_examples(code_examples, project_root)
    
    cross_refs = validator.extract_cross_references(content)
    ref_result = validator.validate_cross_references(cross_refs, project_root)
    
    # Calculate overall quality score
    all_results = [markdown_result, code_result, ref_result]
    quality_score = validator.calculate_quality_score(content, all_results)
    
    # Combine all results
    combined_result = ValidationResult(
        is_valid=all(r.is_valid for r in all_results),
        errors=sum([r.errors for r in all_results], []),
        warnings=sum([r.warnings for r in all_results], []),
        quality_score=quality_score
    )
    
    # Add suggestions for improvement
    if quality_score < 70:
        combined_result.suggestions.append("Consider adding more detailed content and examples")
    if not code_examples:
        combined_result.suggestions.append("Consider adding code examples to illustrate concepts")
    if not cross_refs:
        combined_result.suggestions.append("Consider adding cross-references to related documentation")
        
    return {
        'is_valid': combined_result.is_valid,
        'errors': combined_result.errors,
        'warnings': combined_result.warnings,
        'quality_score': combined_result.quality_score,
        'suggestions': combined_result.suggestions,
        'code_examples_count': len(code_examples),
        'cross_references_count': len(cross_refs),
        'file_path': file_path
    }


@tool
def enforce_quality_standards(content: str, file_path: str, min_quality_score: float = 70.0, project_root: str = None) -> dict:
    """
    Enforce quality standards before writing documentation files.
    
    Args:
        content: The content to validate
        file_path: Path where the file will be written
        min_quality_score: Minimum acceptable quality score (default: 70.0)
        project_root: Root directory of the project (optional)
        
    Returns:
        Dictionary with validation results and write_approved boolean
    """
    validation_result = validate_documentation_quality(file_path, content, project_root)
    
    # Determine if content meets quality standards
    write_approved = (
        validation_result['is_valid'] and
        validation_result['quality_score'] >= min_quality_score and
        len(validation_result['errors']) == 0
    )
    
    return {
        **validation_result,
        'write_approved': write_approved,
        'min_quality_score': min_quality_score,
        'meets_standards': write_approved
    }


@tool
def validate_and_improve_content(content: str, file_path: str, project_root: str = None) -> dict:
    """
    Validate content and provide specific improvement suggestions.
    
    Args:
        content: The content to validate and improve
        file_path: Path to the documentation file
        project_root: Root directory of the project (optional)
        
    Returns:
        Dictionary with validation results and improvement suggestions
    """
    validation_result = validate_documentation_quality(file_path, content, project_root)
    
    # Generate specific improvement suggestions
    improvements = []
    
    if validation_result['quality_score'] < 50:
        improvements.append("Content needs significant improvement - consider complete rewrite")
    elif validation_result['quality_score'] < 70:
        improvements.append("Content needs moderate improvement")
        
    if validation_result['code_examples_count'] == 0:
        improvements.append("Add practical code examples to illustrate concepts")
        
    if validation_result['cross_references_count'] == 0:
        improvements.append("Add cross-references to related documentation sections")
        
    if len(validation_result['errors']) > 0:
        improvements.append("Fix critical errors before publishing")
        
    if len(validation_result['warnings']) > 5:
        improvements.append("Address multiple formatting warnings")
        
    return {
        **validation_result,
        'improvement_suggestions': improvements,
        'priority_level': 'high' if validation_result['quality_score'] < 50 else 'medium' if validation_result['quality_score'] < 70 else 'low'
    }


@tool
def validate_documentation_quality_detailed(file_path: str, content: str, project_root: str = None, min_quality_score: float = 70.0) -> dict:
    """
    Enhanced validation with detailed diagnostic breakdown.
    
    Provides comprehensive analysis of why content fails validation,
    broken down by category with specific improvement suggestions.
    
    Args:
        file_path: Path to the documentation file being validated
        content: The content to validate
        project_root: Root directory of the project (optional)
        min_quality_score: Minimum quality score required for approval
        
    Returns:
        Dictionary containing detailed validation results with category breakdowns,
        specific failure reasons, and actionable improvement suggestions
    """
    validator = ContentValidator(project_root)
    
    # Perform standard validations
    markdown_result = validator.validate_markdown_syntax(content, file_path)
    code_examples = validator.extract_code_examples(content)
    code_result = validator.validate_code_examples(code_examples, project_root)
    cross_refs = validator.extract_cross_references(content)
    ref_result = validator.validate_cross_references(cross_refs, project_root)
    
    # Get detailed quality breakdown
    detailed_scores = validator.calculate_detailed_quality_scores(content, [markdown_result, code_result, ref_result])
    
    # Calculate legacy score for compatibility
    legacy_score = validator.calculate_quality_score(content, [markdown_result, code_result, ref_result])
    
    # Determine if content passes validation
    passes_validation = detailed_scores['overall_score'] >= min_quality_score
    
    # Create improvement actions based on detailed analysis
    improvement_actions = []
    priority_fixes = []
    
    for category, details in detailed_scores['detailed_breakdown'].items():
        if details['score'] < 70:  # Category needs improvement
            priority_fixes.extend(details['issues'])
            improvement_actions.extend(details['suggestions'])
    
    # Add category-specific guidance
    category_guidance = {}
    for category, score in detailed_scores['category_scores'].items():
        weight = detailed_scores['weights_used'][category]
        impact = score * weight
        
        if score < 70:
            guidance = f"⚠️ LOW ({score:.1f}/100) - High priority for improvement (contributes {impact:.1f} to overall score)"
        elif score < 85:
            guidance = f"🔶 MEDIUM ({score:.1f}/100) - Room for improvement (contributes {impact:.1f} to overall score)"
        else:
            guidance = f"✅ GOOD ({score:.1f}/100) - Meeting standards (contributes {impact:.1f} to overall score)"
        
        category_guidance[category] = guidance
    
    # Create threshold information
    threshold_info = {
        'required_score': min_quality_score,
        'actual_score': detailed_scores['overall_score'],
        'score_difference': detailed_scores['overall_score'] - min_quality_score,
        'passes_threshold': passes_validation,
        'legacy_score': legacy_score,  # For comparison with old system
        'score_explanation': f"Weighted average of {len(detailed_scores['category_scores'])} categories"
    }
    
    # Create failure reason summary
    failure_reasons = []
    if not passes_validation:
        failure_reasons.append(f"Overall score {detailed_scores['overall_score']:.1f} below required {min_quality_score}")
        
        worst_categories = sorted(
            [(cat, score) for cat, score in detailed_scores['category_scores'].items()],
            key=lambda x: x[1]
        )[:3]
        
        for category, score in worst_categories:
            if score < 70:
                failure_reasons.append(f"{category.replace('_', ' ').title()}: {score:.1f}/100 - {detailed_scores['detailed_breakdown'][category]['issues'][0] if detailed_scores['detailed_breakdown'][category]['issues'] else 'Below standards'}")
    
    return {
        'is_valid': passes_validation,
        'validation_type': 'detailed_enhanced',
        'overall_quality_score': detailed_scores['overall_score'],
        'legacy_quality_score': legacy_score,  # For debugging score differences
        'category_scores': detailed_scores['category_scores'],
        'category_guidance': category_guidance,
        'detailed_breakdown': detailed_scores['detailed_breakdown'],
        'weights_used': detailed_scores['weights_used'],
        'threshold_info': threshold_info,
        'failure_reasons': failure_reasons,
        'priority_fixes': priority_fixes,
        'improvement_actions': improvement_actions,
        'errors': sum([r.errors for r in [markdown_result, code_result, ref_result]], []),
        'warnings': sum([r.warnings for r in [markdown_result, code_result, ref_result]], []),
        'suggestions': improvement_actions,
        'code_examples_count': len(code_examples),
        'cross_references_count': len(cross_refs),
        'file_path': file_path,
        'content_stats': {
            'character_count': len(content),
            'line_count': len(content.split('\n')),
            'word_count': len(content.split()),
            'paragraph_count': len([p for p in content.split('\n\n') if p.strip()])
        }
    }