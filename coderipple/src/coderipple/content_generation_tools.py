"""
Content Generation Tools for Intelligent Documentation Creation

This module provides tools for generating context-aware documentation content
based on actual git changes rather than generic templates.
Enhanced with real diff integration for specific, targeted documentation.
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from strands import tool


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


@tool
def generate_targeted_content_from_diff(git_diff: str, section: str, change_type: str, 
                                      doc_type: str = "user") -> dict:
    """
    Generate targeted documentation content based on specific git diff analysis.
    Enhanced for real diff integration.
    
    Args:
        git_diff: Raw git diff output
        section: Documentation section to generate
        change_type: Type of change (feature, bugfix, etc.)
        doc_type: Type of documentation (user, api, system)
        
    Returns:
        Dictionary with generated content and metadata
    """
    try:
        # Import real diff integration tools
        from real_diff_integration_tools import extract_specific_changes, generate_code_examples_from_diff
        
        # Extract specific changes from diff
        changes_result = extract_specific_changes(git_diff, change_type)
        if changes_result['status'] != 'success':
            return {
                'status': 'error',
                'error': 'Failed to extract changes from diff',
                'content': ''
            }
        
        # Generate code examples from actual changes
        examples_result = generate_code_examples_from_diff(git_diff, "all", change_type)
        if examples_result['status'] != 'success':
            return {
                'status': 'error', 
                'error': 'Failed to generate code examples',
                'content': ''
            }
        
        # Generate content based on actual changes
        content = _generate_content_from_real_changes(
            section=section,
            changes=changes_result,
            examples=examples_result['examples'],
            change_type=change_type,
            doc_type=doc_type
        )
        
        return {
            'status': 'success',
            'content': content,
            'functions_changed': len(changes_result['function_changes']),
            'classes_changed': len(changes_result['class_changes']),
            'examples_generated': len(examples_result['examples']),
            'files_affected': len(changes_result['files_modified']),
            'change_summary': changes_result['summary']
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Error generating targeted content: {str(e)}",
            'content': ''
        }


@tool
def generate_api_documentation_from_diff(git_diff: str, file_path: str) -> dict:
    """
    Generate API documentation based on specific function/class changes in git diff.
    
    Args:
        git_diff: Raw git diff output
        file_path: Specific file to document
        
    Returns:
        Dictionary with API documentation content
    """
    try:
        from real_diff_integration_tools import generate_file_specific_documentation
        
        result = generate_file_specific_documentation(
            git_diff=git_diff,
            file_path=file_path,
            existing_docs="",
            doc_type="api"
        )
        
        return result
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Error generating API documentation: {str(e)}",
            'documentation': ''
        }


@tool 
def generate_migration_guide_from_diff(git_diff: str, change_type: str) -> dict:
    """
    Generate migration guide based on breaking changes detected in git diff.
    
    Args:
        git_diff: Raw git diff output
        change_type: Type of change
        
    Returns:
        Dictionary with migration guide content
    """
    try:
        from real_diff_integration_tools import extract_specific_changes
        
        changes_result = extract_specific_changes(git_diff, change_type)
        if changes_result['status'] != 'success':
            return {
                'status': 'error',
                'error': 'Failed to extract changes',
                'content': ''
            }
        
        # Look for breaking changes
        breaking_changes = []
        migration_steps = []
        
        # Check for signature changes
        for func in changes_result['function_changes']:
            if func['change_type'] == 'signature_changed':
                breaking_changes.append({
                    'type': 'function_signature',
                    'name': func['name'],
                    'file': func['file_path'],
                    'old_signature': func['old_signature'],
                    'new_signature': func['new_signature']
                })
                
                migration_steps.append(f"Update calls to `{func['name']}()` in {func['file_path']}")
            
            elif func['change_type'] == 'deleted':
                breaking_changes.append({
                    'type': 'function_removed',
                    'name': func['name'],
                    'file': func['file_path']
                })
                
                migration_steps.append(f"Replace usage of removed function `{func['name']}()`")
        
        # Check for removed classes
        for cls in changes_result['class_changes']:
            if cls['change_type'] == 'deleted':
                breaking_changes.append({
                    'type': 'class_removed',
                    'name': cls['name'],
                    'file': cls['file_path']
                })
                
                migration_steps.append(f"Replace usage of removed class `{cls['name']}`")
        
        # Generate migration guide content
        if breaking_changes:
            content = _generate_migration_guide_content(breaking_changes, migration_steps, change_type)
        else:
            content = f"# Migration Guide\n\nNo breaking changes detected in this {change_type} update."
        
        return {
            'status': 'success',
            'content': content,
            'breaking_changes': len(breaking_changes),
            'migration_steps': len(migration_steps),
            'has_breaking_changes': len(breaking_changes) > 0
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': f"Error generating migration guide: {str(e)}",
            'content': ''
        }


def _generate_content_from_real_changes(section: str, changes: dict, examples: list, 
                                      change_type: str, doc_type: str) -> str:
    """Generate content based on real changes extracted from git diff."""
    
    content_parts = []
    
    if section == 'discovery':
        content_parts.append(f"# Recent Changes: {change_type.title()}")
        content_parts.append(f"\n{changes['summary']}")
        
        if changes['function_changes']:
            content_parts.append(f"\n## New Functions ({len(changes['function_changes'])})")
            for func in changes['function_changes'][:3]:
                if func['change_type'] == 'added':
                    content_parts.append(f"- **{func['name']}()** in `{func['file_path']}`")
                    if func['docstring']:
                        content_parts.append(f"  {func['docstring']}")
        
        if changes['class_changes']:
            content_parts.append(f"\n## New Classes ({len(changes['class_changes'])})")
            for cls in changes['class_changes'][:3]:
                if cls['change_type'] == 'added':
                    content_parts.append(f"- **{cls['name']}** in `{cls['file_path']}`")
                    if cls['docstring']:
                        content_parts.append(f"  {cls['docstring']}")
    
    elif section == 'getting_started':
        content_parts.append(f"# Getting Started with {change_type.title()} Changes")
        
        if examples:
            content_parts.append(f"\n## Quick Start Examples")
            for i, example in enumerate(examples[:3], 1):
                if example['type'] == 'new_function':
                    content_parts.append(f"\n### {i}. {example['title']}")
                    content_parts.append(f"{example['description']}")
                    content_parts.append(f"\n```python\n{example['code']}\n```")
                    if 'usage_example' in example:
                        content_parts.append(f"\n**Usage:**\n```python\n{example['usage_example']}\n```")
    
    elif section == 'patterns':
        content_parts.append(f"# Usage Patterns")
        
        if examples:
            content_parts.append(f"\n## Code Examples from Recent Changes")
            for example in examples:
                if example['type'] in ['new_function', 'modified_function']:
                    content_parts.append(f"\n### {example['title']}")
                    content_parts.append(f"{example['description']}")
                    content_parts.append(f"\n```python\n{example['code']}\n```")
                    
                    if example['type'] == 'modified_function' and 'old_code' in example:
                        content_parts.append(f"\n**Before:**\n```python\n{example['old_code']}\n```")
                        content_parts.append(f"\n**After:**\n```python\n{example['new_code']}\n```")
    
    elif section == 'architecture':
        content_parts.append(f"# System Architecture Changes")
        content_parts.append(f"\nChanges from {change_type}: {changes['summary']}")
        
        if changes['files_modified']:
            content_parts.append(f"\n## Modified Files ({len(changes['files_modified'])})")
            for file_path in changes['files_modified']:
                content_parts.append(f"- `{file_path}`")
        
        if changes['function_changes']:
            func_by_type = {}
            for func in changes['function_changes']:
                change_type_key = func['change_type']
                if change_type_key not in func_by_type:
                    func_by_type[change_type_key] = []
                func_by_type[change_type_key].append(func)
            
            for change_type_key, funcs in func_by_type.items():
                content_parts.append(f"\n### Functions {change_type_key.title()} ({len(funcs)})")
                for func in funcs[:5]:  # Limit to 5 per type
                    content_parts.append(f"- `{func['name']}()` in {func['file_path']}")
    
    # Fallback content
    if not content_parts:
        content_parts.append(f"# {section.replace('_', ' ').title()}")
        content_parts.append(f"Updated based on {change_type} changes.")
        content_parts.append(f"\nSummary: {changes.get('summary', 'Changes detected')}")
    
    return '\n'.join(content_parts)


def _generate_migration_guide_content(breaking_changes: list, migration_steps: list, change_type: str) -> str:
    """Generate migration guide content for breaking changes."""
    
    content_parts = []
    content_parts.append(f"# Migration Guide: {change_type.title()}")
    content_parts.append(f"\n⚠️ **Breaking Changes Detected**")
    content_parts.append(f"\nThis {change_type} includes {len(breaking_changes)} breaking changes that require action.")
    
    content_parts.append(f"\n## Breaking Changes")
    
    for i, change in enumerate(breaking_changes, 1):
        content_parts.append(f"\n### {i}. {change['type'].replace('_', ' ').title()}: {change['name']}")
        content_parts.append(f"**File:** `{change['file']}`")
        
        if change['type'] == 'function_signature':
            content_parts.append(f"\n**Old signature:**\n```python\n{change['old_signature']}\n```")
            content_parts.append(f"\n**New signature:**\n```python\n{change['new_signature']}\n```")
        
        elif change['type'] in ['function_removed', 'class_removed']:
            content_parts.append(f"\n**Status:** Removed in this update")
    
    content_parts.append(f"\n## Migration Steps")
    content_parts.append(f"\nFollow these steps to update your code:")
    
    for i, step in enumerate(migration_steps, 1):
        content_parts.append(f"{i}. {step}")
    
    content_parts.append(f"\n## Timeline")
    content_parts.append(f"- **Immediate:** Review your code for usage of changed functions/classes")
    content_parts.append(f"- **Before upgrading:** Update your code according to the steps above")
    content_parts.append(f"- **After upgrading:** Test thoroughly to ensure everything works")
    
    return '\n'.join(content_parts)


@tool
def generate_context_rich_content(section: str, git_analysis: Dict[str, Any], 
                                file_changes: List[str], code_examples: List[CodeExample],
                                doc_focus: DocumentationFocus, change_type: str,
                                project_root: str = ".") -> str:
    """
    Generate context-rich content using comprehensive analysis tools for meaningful documentation.
    
    This function integrates:
    - Source code analysis for project understanding
    - Existing content discovery for context awareness
    - Content-aware update logic for intelligent merging
    
    Args:
        section: Documentation section to generate ('discovery', 'getting_started', etc.)
        git_analysis: Results from git analysis tool
        file_changes: List of changed files
        code_examples: Extracted code examples
        doc_focus: Documentation focus analysis
        change_type: Type of change (feature, bugfix, etc.)
        project_root: Root directory of the project
        
    Returns:
        Generated content string with rich context
    """
    try:
        # Get source code analysis for project understanding
        from source_code_analysis_tool import analyze_source_code
        source_analysis = analyze_source_code(project_root)
        
        # Discover existing content for context awareness
        from existing_content_discovery_tool import analyze_existing_content
        existing_content = analyze_existing_content(None, source_analysis)
        
        # Apply content-aware update logic
        from content_aware_update_logic import apply_content_aware_updates
        
        # Map section to documentation category
        category_mapping = {
            'discovery': 'user',
            'getting_started': 'user',
            'patterns': 'user',
            'advanced': 'user',
            'troubleshooting': 'user',
            'architecture': 'system',
            'capabilities': 'system',
            'tech_stack': 'system',
            'decisions': 'decisions'
        }
        
        target_category = category_mapping.get(section, 'user')
        
        # Get content-aware update recommendations
        git_diff = git_analysis.get('diff', '') or _reconstruct_diff_from_examples(code_examples)
        update_result = apply_content_aware_updates(
            change_type=change_type,
            affected_files=file_changes,
            git_diff=git_diff,
            target_category=target_category,
            source_analysis=source_analysis,
            existing_docs=existing_content
        )
        
        # Generate content based on update strategy
        if update_result['status'] == 'success':
            return _generate_rich_content_with_context(
                section=section,
                update_result=update_result,
                source_analysis=source_analysis,
                existing_content=existing_content,
                git_analysis=git_analysis,
                code_examples=code_examples,
                doc_focus=doc_focus
            )
        else:
            # Fallback to original method if content-aware updates fail
            return generate_context_aware_content(section, git_analysis, file_changes, code_examples, doc_focus)
            
    except Exception as e:
        # Fallback to original method on any error
        return generate_context_aware_content(section, git_analysis, file_changes, code_examples, doc_focus)


def _reconstruct_diff_from_examples(code_examples: List[CodeExample]) -> str:
    """Reconstruct a basic git diff from code examples for content-aware updates"""
    diff_lines = []
    
    for example in code_examples:
        if example.change_type == 'added':
            diff_lines.append(f"--- a/{example.file_path}")
            diff_lines.append(f"+++ b/{example.file_path}")
            for line in example.code.split('\n'):
                diff_lines.append(f"+{line}")
        elif example.change_type == 'removed':
            diff_lines.append(f"--- a/{example.file_path}")
            diff_lines.append(f"+++ b/{example.file_path}")
            for line in example.code.split('\n'):
                diff_lines.append(f"-{line}")
    
    return '\n'.join(diff_lines)


def _generate_rich_content_with_context(section: str, update_result: Dict[str, Any],
                                       source_analysis: Dict[str, Any], existing_content: Dict[str, Any],
                                       git_analysis: Dict[str, Any], code_examples: List[CodeExample],
                                       doc_focus: DocumentationFocus) -> str:
    """Generate rich content using all available context"""
    
    content_parts = []
    project_name = source_analysis.get('project_name', 'Project')
    project_purpose = source_analysis.get('main_purpose', 'Software project')
    change_type = git_analysis.get('change_type', 'update')
    
    # Check if we should update existing content or create new
    decision = update_result.get('update_decision', {})
    strategy = decision.get('strategy', 'create_new')
    
    if strategy == 'update_existing':
        # Generate content that enhances existing documentation
        content_parts.append(f"## {section.replace('_', ' ').title()} - Updated")
        content_parts.append(f"*Enhanced documentation for {project_name}*")
        
        # Mention what we're preserving
        preservation_notes = decision.get('preservation_notes', [])
        if preservation_notes:
            content_parts.append(f"\n> **Note**: This update preserves existing content while adding new information.")
        
    else:
        # Generate new content based on source analysis
        content_parts.append(f"## {section.replace('_', ' ').title()}")
        content_parts.append(f"*Documentation for {project_name} - {project_purpose}*")
    
    # Add section-specific content with rich context
    if section == 'discovery':
        content_parts.append(f"\n### What is {project_name}?")
        content_parts.append(project_purpose)
        
        # Add key technologies from source analysis
        technologies = source_analysis.get('key_technologies', [])
        if technologies:
            content_parts.append(f"\n**Key Technologies**: {', '.join(technologies)}")
        
        # Add recent changes
        if code_examples:
            content_parts.append(f"\n### Recent Updates ({change_type.title()})")
            for example in code_examples[:2]:
                if example.change_type == 'added':
                    content_parts.append(f"- ✅ {example.description}")
    
    elif section == 'getting_started':
        content_parts.append(f"\n### Quick Start with {project_name}")
        
        # Use actual entry points from source analysis
        entry_points = source_analysis.get('entry_points', [])
        if entry_points:
            content_parts.append(f"\n**Main Entry Points:**")
            for entry in entry_points[:3]:  # Show top 3
                content_parts.append(f"- `{entry}`")
        
        # Add installation context if available
        main_modules = source_analysis.get('main_modules', [])
        if main_modules:
            content_parts.append(f"\n**Core Modules:**")
            for module in main_modules[:5]:  # Show top 5
                content_parts.append(f"- {module}")
    
    elif section == 'patterns':
        content_parts.append(f"\n### Common Usage Patterns")
        
        # Use actual public APIs from source analysis
        public_apis = source_analysis.get('public_api', [])
        if public_apis:
            content_parts.append(f"\n**Available Functions:**")
            for api in public_apis[:5]:  # Show top 5
                api_name = api.get('name', 'unknown')
                api_desc = api.get('description', 'Function')
                content_parts.append(f"- `{api_name}()` - {api_desc}")
        
        # Add code examples from actual changes
        if code_examples:
            content_parts.append(f"\n### Code Examples")
            for example in code_examples[:2]:
                if example.change_type == 'added' and len(example.code) < 200:
                    content_parts.append(f"\n**{example.description}:**")
                    content_parts.append(f"```{example.language}")
                    content_parts.append(example.code)
                    content_parts.append("```")
    
    elif section == 'architecture':
        content_parts.append(f"\n### System Architecture")
        content_parts.append(f"Architecture overview for {project_name}:")
        
        # Use actual module structure from source analysis
        main_modules = source_analysis.get('main_modules', [])
        if main_modules:
            content_parts.append(f"\n**Main Components:**")
            for module in main_modules:
                content_parts.append(f"- **{module}**: Core functionality")
        
        # Add technology stack
        technologies = source_analysis.get('key_technologies', [])
        if technologies:
            content_parts.append(f"\n**Technology Stack:**")
            for tech in technologies:
                content_parts.append(f"- {tech}")
    
    # Add content updates from content-aware logic
    content_updates = update_result.get('content_updates', [])
    for update in content_updates:
        if update.get('confidence', 0) > 0.7:  # Only include high-confidence updates
            content_parts.append(f"\n### {update.get('target_section', 'Updates')}")
            content_parts.append(update.get('new_content', ''))
            content_parts.append(f"\n*Rationale: {update.get('rationale', 'Added based on recent changes')}*")
    
    # Add project statistics for context
    stats = source_analysis.get('statistics', {})
    if stats and section in ['discovery', 'architecture']:
        content_parts.append(f"\n### Project Statistics")
        content_parts.append(f"- **Files**: {stats.get('total_files', 'N/A')}")
        content_parts.append(f"- **Lines of Code**: {stats.get('total_lines', 'N/A')}")
        content_parts.append(f"- **Public APIs**: {len(source_analysis.get('public_api', []))}")
    
    # Fallback to basic content if nothing was generated
    if len(content_parts) <= 2:  # Only title and subtitle
        content_parts.append(f"\nThis section has been updated based on recent {change_type} changes.")
        content_parts.append(f"Project: {project_name}")
        content_parts.append(f"Purpose: {project_purpose}")
    
    return '\n'.join(content_parts)