"""
Content Generation Tools for Step 4B: Intelligent Content Generation

This module provides tools for generating context-aware documentation content
based on actual git changes rather than generic templates.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CodeExample:
    """Represents a code example extracted from git changes"""
    language: str
    code: str
    description: str
    file_path: str
    change_type: str  # 'added', 'modified', 'removed'


@dataclass
class DocumentationFocus:
    """Represents what type of documentation should be emphasized"""
    primary_focus: str  # 'api', 'cli', 'config', 'architecture', 'usage'
    affected_areas: List[str]
    user_impact_level: str  # 'high', 'medium', 'low'
    suggested_sections: List[str]


def analyze_change_patterns(file_paths: List[str], commit_messages: List[str]) -> DocumentationFocus:
    """
    Analyze file changes and commit messages to determine documentation focus.
    
    Args:
        file_paths: List of changed file paths
        commit_messages: List of commit messages for context
        
    Returns:
        DocumentationFocus indicating what type of documentation to prioritize
    """
    
    # Pattern matching for different change types
    api_patterns = ['api/', 'endpoints/', 'routes/', 'handlers/']
    cli_patterns = ['cli.py', 'cli/', 'command/', 'cmd/', 'bin/', 'commands/']
    config_patterns = ['config/', 'settings/', '.env', 'yaml', 'json', 'toml']
    architecture_patterns = ['core/', 'lib/', 'modules/']  # Removed 'src/' to be more specific
    test_patterns = ['test/', 'tests/', 'spec/', '__test__']
    doc_patterns = ['README', 'docs/', '.md', 'documentation/']
    
    # Analyze file paths
    focus_scores = {
        'api': 0,
        'cli': 0, 
        'config': 0,
        'architecture': 0,
        'usage': 0,
        'documentation': 0
    }
    
    affected_areas = []
    
    for file_path in file_paths:
        file_lower = file_path.lower()
        
        # API changes
        if any(pattern in file_lower for pattern in api_patterns):
            focus_scores['api'] += 2
            affected_areas.append('API')
            
        # CLI changes  
        if any(pattern in file_lower for pattern in cli_patterns):
            focus_scores['cli'] += 2
            affected_areas.append('CLI')
            
        # Configuration changes
        if any(pattern in file_lower for pattern in config_patterns):
            focus_scores['config'] += 1
            affected_areas.append('Configuration')
            
        # Core architecture changes
        if any(pattern in file_lower for pattern in architecture_patterns):
            focus_scores['architecture'] += 1
            affected_areas.append('Architecture')
            
        # Test changes (indicates usage patterns)
        if any(pattern in file_lower for pattern in test_patterns):
            focus_scores['usage'] += 1
            affected_areas.append('Testing')
            
        # Documentation changes
        if any(pattern in file_lower for pattern in doc_patterns):
            focus_scores['documentation'] += 1
            affected_areas.append('Documentation')
    
    # Analyze commit messages for additional context
    commit_text = ' '.join(commit_messages).lower()
    
    # Keywords that indicate user-facing changes
    user_facing_keywords = ['add', 'new feature', 'implement', 'cli', 'api', 'endpoint']
    breaking_keywords = ['breaking', 'remove', 'deprecate', 'change api']
    cli_keywords = ['command', 'cli', 'deploy', 'run', 'execute']
    
    user_impact_level = 'low'
    if any(keyword in commit_text for keyword in breaking_keywords):
        user_impact_level = 'high'
        focus_scores['api'] += 1
        focus_scores['cli'] += 1
    elif any(keyword in commit_text for keyword in user_facing_keywords):
        user_impact_level = 'medium'
        focus_scores['usage'] += 1
    
    # Additional CLI detection from commit messages
    if any(keyword in commit_text for keyword in cli_keywords):
        focus_scores['cli'] += 1
    
    # Determine primary focus
    primary_focus = max(focus_scores, key=focus_scores.get)
    
    # Suggest documentation sections based on focus
    section_mapping = {
        'api': ['API Reference', 'Integration Guide', 'Examples'],
        'cli': ['Command Reference', 'Getting Started', 'Usage Examples'],
        'config': ['Configuration', 'Setup Guide', 'Environment Variables'],  
        'architecture': ['System Architecture', 'Technical Overview', 'Design Decisions'],
        'usage': ['Usage Examples', 'Common Patterns', 'Best Practices'],
        'documentation': ['Getting Started', 'User Guide', 'Documentation Updates']
    }
    
    suggested_sections = section_mapping.get(primary_focus, ['General Updates'])
    
    return DocumentationFocus(
        primary_focus=primary_focus,
        affected_areas=list(set(affected_areas)),
        user_impact_level=user_impact_level,
        suggested_sections=suggested_sections
    )


def extract_code_examples_from_diff(git_diff: str, file_path: str) -> List[CodeExample]:
    """
    Extract usable code examples from git diff.
    
    Args:
        git_diff: Raw git diff content
        file_path: Path to the file being analyzed
        
    Returns:
        List of CodeExample objects with extracted code snippets
    """
    
    examples = []
    
    if not git_diff or not file_path:
        return examples
    
    # Determine language from file extension
    language_map = {
        '.py': 'python',
        '.js': 'javascript', 
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.sh': 'bash',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.md': 'markdown'
    }
    
    file_ext = '.' + file_path.split('.')[-1] if '.' in file_path else ''
    language = language_map.get(file_ext, 'text')
    
    # Split diff into lines
    lines = git_diff.split('\n')
    
    # Track current context
    current_function = None
    added_lines = []
    removed_lines = []
    
    for line in lines:
        # Function/class definition detection (Python example)
        if language == 'python':
            if line.startswith('+') and ('def ' in line or 'class ' in line):
                # Extract function/class name
                match = re.search(r'(def|class)\s+(\w+)', line)
                if match:
                    current_function = match.group(2)
        
        # Collect added lines (new code)
        if line.startswith('+') and not line.startswith('+++'):
            clean_line = line[1:].strip()
            if clean_line and not clean_line.startswith('#'):  # Skip comments
                added_lines.append(clean_line)
        
        # Collect removed lines (old code)  
        elif line.startswith('-') and not line.startswith('---'):
            clean_line = line[1:].strip()
            if clean_line and not clean_line.startswith('#'):
                removed_lines.append(clean_line)
    
    # Create examples for added code
    if added_lines:
        # Group related lines into code blocks
        code_block = '\n'.join(added_lines)
        
        description = "New code added"
        if current_function:
            description = f"New function: {current_function}"
        elif 'import' in code_block:
            description = "New imports and dependencies"
        elif 'class' in code_block:
            description = "New class definition"
        
        examples.append(CodeExample(
            language=language,
            code=code_block,
            description=description,
            file_path=file_path,
            change_type='added'
        ))
    
    # Create examples for removed code (for migration guides)
    if removed_lines:
        code_block = '\n'.join(removed_lines)
        examples.append(CodeExample(
            language=language,
            code=code_block, 
            description="Removed/deprecated code",
            file_path=file_path,
            change_type='removed'
        ))
    
    return examples


def generate_context_aware_content(section: str, git_analysis: Dict[str, Any], 
                                 file_changes: List[str], code_examples: List[CodeExample],
                                 doc_focus: DocumentationFocus) -> str:
    """
    Generate content based on actual changes rather than generic templates.
    
    Args:
        section: Documentation section to generate ('discovery', 'getting_started', etc.)
        git_analysis: Results from git analysis tool
        file_changes: List of changed files
        code_examples: Extracted code examples
        doc_focus: Documentation focus analysis
        
    Returns:
        Generated content string
    """
    
    change_type = git_analysis.get('change_type', 'unknown')
    affected_components = git_analysis.get('affected_components', [])
    summary = git_analysis.get('summary', 'Code changes detected')
    
    content_parts = []
    
    # Section-specific content generation
    if section == 'discovery':
        content_parts.append(f"## Recent Changes ({change_type.title()})")
        content_parts.append(f"{summary}")
        
        if doc_focus.user_impact_level == 'high':
            content_parts.append("\n⚠️ **Important**: This update includes breaking changes that may affect your usage.")
        
        if code_examples:
            content_parts.append("\n### New Features")
            for example in code_examples[:2]:  # Show first 2 examples
                if example.change_type == 'added':
                    content_parts.append(f"- {example.description}")
    
    elif section == 'getting_started':
        if doc_focus.primary_focus == 'cli':
            content_parts.append("## Command Line Interface")
            content_parts.append("The following commands are now available:")
            
            for example in code_examples:
                if 'def ' in example.code and example.language == 'python':
                    # Extract function name for CLI command
                    match = re.search(r'def\s+(\w+)', example.code)
                    if match:
                        cmd_name = match.group(1)
                        content_parts.append(f"- `{cmd_name}`: {example.description}")
        
        elif doc_focus.primary_focus == 'api':
            content_parts.append("## API Usage")
            content_parts.append("New API endpoints available:")
            
            for example in code_examples:
                if example.change_type == 'added':
                    content_parts.append(f"\n```{example.language}")
                    content_parts.append(example.code)
                    content_parts.append("```")
                    content_parts.append(f"*{example.description}*")
    
    elif section == 'architecture':
        content_parts.append(f"## System Changes ({change_type.title()})")
        content_parts.append(f"Recent modifications to system architecture:")
        
        content_parts.append(f"\n### Affected Components")
        for component in affected_components:
            content_parts.append(f"- {component}")
        
        if code_examples:
            content_parts.append(f"\n### Implementation Details")
            for example in code_examples:
                if 'class' in example.code:
                    content_parts.append(f"- New class: {example.description}")
                elif 'def' in example.code:
                    content_parts.append(f"- New function: {example.description}")
    
    # Add code examples section if we have them
    if code_examples and section in ['getting_started', 'patterns']:
        content_parts.append(f"\n### Code Examples")
        
        for i, example in enumerate(code_examples[:3]):  # Limit to 3 examples
            content_parts.append(f"\n#### Example {i+1}: {example.description}")
            content_parts.append(f"```{example.language}")
            content_parts.append(example.code)
            content_parts.append("```")
    
    # Fallback to basic content if no specific patterns matched
    if not content_parts:
        content_parts.append(f"## {section.replace('_', ' ').title()}")
        content_parts.append(f"This section has been updated based on recent {change_type} changes.")
        content_parts.append(f"\nAffected areas: {', '.join(doc_focus.affected_areas)}")
    
    return '\n'.join(content_parts)


def enhance_generic_content_with_context(generic_content: str, git_analysis: Dict[str, Any],
                                       code_examples: List[CodeExample]) -> str:
    """
    Enhance existing generic content with specific context from git changes.
    
    Args:
        generic_content: Existing generic template content
        git_analysis: Results from git analysis
        code_examples: Extracted code examples
        
    Returns:
        Enhanced content with specific details
    """
    
    enhanced_content = generic_content
    
    # Replace generic placeholders with specific information
    change_type = git_analysis.get('change_type', 'update')
    summary = git_analysis.get('summary', 'Recent changes')
    
    # Add specific change information
    if 'Recent Updates' in enhanced_content and code_examples:
        examples_section = "\n### Latest Changes\n"
        for example in code_examples[:2]:
            examples_section += f"- {example.description} in `{example.file_path}`\n"
        
        enhanced_content = enhanced_content.replace(
            '### Recent Updates', 
            examples_section + '\n### Recent Updates'
        )
    
    # Add specific feature information
    if code_examples:
        new_features = [ex for ex in code_examples if ex.change_type == 'added']
        if new_features:
            features_text = "\n### New Features\n"
            for feature in new_features[:3]:
                features_text += f"- {feature.description}\n"
            
            # Insert after first paragraph
            paragraphs = enhanced_content.split('\n\n')
            if len(paragraphs) > 1:
                paragraphs.insert(1, features_text)
                enhanced_content = '\n\n'.join(paragraphs)
    
    return enhanced_content