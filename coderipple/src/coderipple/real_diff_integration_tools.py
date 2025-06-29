"""
Real Diff Integration Tools for CodeRipple Documentation System

This module provides tools for parsing git diffs to extract specific changes
and generate targeted, accurate documentation based on actual code modifications.
"""

import re
import ast
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from strands import tool


@dataclass
class CodeChange:
    """Represents a specific code change from git diff."""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    line_number: int
    old_content: str = ""
    new_content: str = ""
    context_lines: List[str] = field(default_factory=list)


@dataclass
class FunctionChange:
    """Represents a function or method change."""
    name: str
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted', 'signature_changed'
    old_signature: str = ""
    new_signature: str = ""
    old_body: str = ""
    new_body: str = ""
    line_number: int = 0
    docstring: str = ""
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""


@dataclass
class ClassChange:
    """Represents a class change."""
    name: str
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    old_definition: str = ""
    new_definition: str = ""
    methods_changed: List[FunctionChange] = field(default_factory=list)
    line_number: int = 0
    base_classes: List[str] = field(default_factory=list)
    docstring: str = ""


@dataclass
class ImportChange:
    """Represents an import statement change."""
    module: str
    change_type: str  # 'added', 'removed', 'modified'
    import_type: str  # 'import', 'from_import'
    imported_items: List[str] = field(default_factory=list)
    alias: str = ""
    line_number: int = 0


@dataclass
class DiffAnalysisResult:
    """Complete analysis of git diff changes."""
    file_changes: List[CodeChange] = field(default_factory=list)
    function_changes: List[FunctionChange] = field(default_factory=list)
    class_changes: List[ClassChange] = field(default_factory=list)
    import_changes: List[ImportChange] = field(default_factory=list)
    summary: str = ""
    total_lines_added: int = 0
    total_lines_removed: int = 0
    files_modified: List[str] = field(default_factory=list)


class GitDiffParser:
    """Parser for git diff output to extract specific changes."""
    
    def __init__(self):
        self.function_pattern = re.compile(r'^(def\s+(\w+)\s*\([^)]*\).*?):', re.MULTILINE)
        self.class_pattern = re.compile(r'^class\s+(\w+)(?:\([^)]*\))?:', re.MULTILINE)
        self.import_pattern = re.compile(r'^(from\s+[\w.]+\s+)?import\s+.*', re.MULTILINE)
        
    def parse_diff(self, git_diff: str) -> DiffAnalysisResult:
        """Parse git diff and extract detailed change information."""
        result = DiffAnalysisResult()
        
        # Split diff into file sections
        file_sections = self._split_diff_by_files(git_diff)
        
        for file_path, file_diff in file_sections.items():
            result.files_modified.append(file_path)
            
            # Parse basic line changes
            file_changes = self._parse_file_changes(file_path, file_diff)
            result.file_changes.extend(file_changes)
            
            # For Python files, parse detailed changes
            if file_path.endswith('.py'):
                func_changes = self._parse_function_changes(file_path, file_diff)
                class_changes = self._parse_class_changes(file_path, file_diff)
                import_changes = self._parse_import_changes(file_path, file_diff)
                
                result.function_changes.extend(func_changes)
                result.class_changes.extend(class_changes)
                result.import_changes.extend(import_changes)
        
        # Calculate statistics
        result.total_lines_added = len([c for c in result.file_changes if c.change_type == 'added'])
        result.total_lines_removed = len([c for c in result.file_changes if c.change_type == 'deleted'])
        
        # Generate summary
        result.summary = self._generate_change_summary(result)
        
        return result
    
    def _split_diff_by_files(self, git_diff: str) -> Dict[str, str]:
        """Split git diff into sections by file."""
        file_sections = {}
        current_file = None
        current_content = []
        
        lines = git_diff.split('\n')
        for line in lines:
            # Look for file headers
            if line.startswith('diff --git'):
                # Save previous file
                if current_file and current_content:
                    file_sections[current_file] = '\n'.join(current_content)
                
                # Extract file path
                match = re.search(r'diff --git a/(.+) b/(.+)', line)
                if match:
                    current_file = match.group(2)  # Use the 'b/' version (new file)
                    current_content = [line]
                else:
                    current_file = None
                    current_content = []
            elif current_file:
                current_content.append(line)
        
        # Save the last file
        if current_file and current_content:
            file_sections[current_file] = '\n'.join(current_content)
        
        return file_sections
    
    def _parse_file_changes(self, file_path: str, file_diff: str) -> List[CodeChange]:
        """Parse basic line-by-line changes in a file."""
        changes = []
        lines = file_diff.split('\n')
        
        current_line_num = 0
        context_lines = []
        
        for line in lines:
            if line.startswith('@@'):
                # Parse hunk header to get line numbers
                match = re.search(r'@@\s*-\d+(?:,\d+)?\s*\+(\d+)(?:,\d+)?\s*@@', line)
                if match:
                    current_line_num = int(match.group(1))
                context_lines = []
                
            elif line.startswith('+') and not line.startswith('+++'):
                # Added line
                changes.append(CodeChange(
                    file_path=file_path,
                    change_type='added',
                    line_number=current_line_num,
                    new_content=line[1:],  # Remove the '+' prefix
                    context_lines=context_lines.copy()
                ))
                current_line_num += 1
                
            elif line.startswith('-') and not line.startswith('---'):
                # Deleted line
                changes.append(CodeChange(
                    file_path=file_path,
                    change_type='deleted',
                    line_number=current_line_num,
                    old_content=line[1:],  # Remove the '-' prefix
                    context_lines=context_lines.copy()
                ))
                # Don't increment line number for deleted lines
                
            elif line.startswith(' '):
                # Context line
                context_lines.append(line[1:])  # Remove the ' ' prefix
                if len(context_lines) > 3:  # Keep only recent context
                    context_lines = context_lines[-3:]
                current_line_num += 1
        
        return changes
    
    def _parse_function_changes(self, file_path: str, file_diff: str) -> List[FunctionChange]:
        """Parse function/method changes from diff."""
        function_changes = []
        
        # Extract added and removed functions
        added_functions = self._extract_functions_from_diff_section(file_diff, '+')
        removed_functions = self._extract_functions_from_diff_section(file_diff, '-')
        
        # Find new functions
        for func_name, func_content, line_num in added_functions:
            if not any(func_name == rf[0] for rf in removed_functions):
                # This is a new function
                function_changes.append(FunctionChange(
                    name=func_name,
                    file_path=file_path,
                    change_type='added',
                    new_signature=self._extract_function_signature(func_content),
                    new_body=func_content,
                    line_number=line_num,
                    docstring=self._extract_docstring(func_content),
                    parameters=self._extract_parameters(func_content)
                ))
        
        # Find removed functions
        for func_name, func_content, line_num in removed_functions:
            if not any(func_name == af[0] for af in added_functions):
                # This is a removed function
                function_changes.append(FunctionChange(
                    name=func_name,
                    file_path=file_path,
                    change_type='deleted',
                    old_signature=self._extract_function_signature(func_content),
                    old_body=func_content,
                    line_number=line_num
                ))
        
        # Find modified functions
        for func_name, new_content, new_line in added_functions:
            for old_name, old_content, old_line in removed_functions:
                if func_name == old_name:
                    # This function was modified
                    old_sig = self._extract_function_signature(old_content)
                    new_sig = self._extract_function_signature(new_content)
                    
                    change_type = 'signature_changed' if old_sig != new_sig else 'modified'
                    
                    function_changes.append(FunctionChange(
                        name=func_name,
                        file_path=file_path,
                        change_type=change_type,
                        old_signature=old_sig,
                        new_signature=new_sig,
                        old_body=old_content,
                        new_body=new_content,
                        line_number=new_line,
                        docstring=self._extract_docstring(new_content),
                        parameters=self._extract_parameters(new_content)
                    ))
                    break
        
        return function_changes
    
    def _parse_class_changes(self, file_path: str, file_diff: str) -> List[ClassChange]:
        """Parse class changes from diff."""
        class_changes = []
        
        # Extract added and removed classes
        added_classes = self._extract_classes_from_diff_section(file_diff, '+')
        removed_classes = self._extract_classes_from_diff_section(file_diff, '-')
        
        # Find new classes
        for class_name, class_content, line_num in added_classes:
            if not any(class_name == rc[0] for rc in removed_classes):
                class_changes.append(ClassChange(
                    name=class_name,
                    file_path=file_path,
                    change_type='added',
                    new_definition=class_content,
                    line_number=line_num,
                    base_classes=self._extract_base_classes(class_content),
                    docstring=self._extract_docstring(class_content)
                ))
        
        # Find removed classes
        for class_name, class_content, line_num in removed_classes:
            if not any(class_name == ac[0] for ac in added_classes):
                class_changes.append(ClassChange(
                    name=class_name,
                    file_path=file_path,
                    change_type='deleted',
                    old_definition=class_content,
                    line_number=line_num
                ))
        
        # Find modified classes
        for class_name, new_content, new_line in added_classes:
            for old_name, old_content, old_line in removed_classes:
                if class_name == old_name:
                    class_changes.append(ClassChange(
                        name=class_name,
                        file_path=file_path,
                        change_type='modified',
                        old_definition=old_content,
                        new_definition=new_content,
                        line_number=new_line,
                        base_classes=self._extract_base_classes(new_content),
                        docstring=self._extract_docstring(new_content)
                    ))
                    break
        
        return class_changes
    
    def _parse_import_changes(self, file_path: str, file_diff: str) -> List[ImportChange]:
        """Parse import statement changes from diff."""
        import_changes = []
        lines = file_diff.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            if line.startswith('+') and self.import_pattern.match(line[1:].strip()):
                # Added import
                import_info = self._parse_import_statement(line[1:].strip())
                if import_info:
                    import_changes.append(ImportChange(
                        module=import_info['module'],
                        change_type='added',
                        import_type=import_info['type'],
                        imported_items=import_info['items'],
                        alias=import_info['alias'],
                        line_number=line_num
                    ))
            
            elif line.startswith('-') and self.import_pattern.match(line[1:].strip()):
                # Removed import
                import_info = self._parse_import_statement(line[1:].strip())
                if import_info:
                    import_changes.append(ImportChange(
                        module=import_info['module'],
                        change_type='removed',
                        import_type=import_info['type'],
                        imported_items=import_info['items'],
                        alias=import_info['alias'],
                        line_number=line_num
                    ))
        
        return import_changes
    
    def _extract_functions_from_diff_section(self, file_diff: str, prefix: str) -> List[Tuple[str, str, int]]:
        """Extract function definitions from diff lines with specific prefix."""
        functions = []
        lines = file_diff.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith(prefix) and line[1:].strip().startswith('def '):
                func_line = line[1:].strip()
                match = re.match(r'def\s+(\w+)', func_line)
                if match:
                    func_name = match.group(1)
                    func_content = [func_line]
                    
                    # Collect function body
                    i += 1
                    while i < len(lines) and (lines[i].startswith(prefix) or lines[i].startswith(' ')):
                        if lines[i].startswith(prefix):
                            func_content.append(lines[i][1:])
                        i += 1
                    
                    functions.append((func_name, '\n'.join(func_content), i))
                    continue
            i += 1
        
        return functions
    
    def _extract_classes_from_diff_section(self, file_diff: str, prefix: str) -> List[Tuple[str, str, int]]:
        """Extract class definitions from diff lines with specific prefix."""
        classes = []
        lines = file_diff.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith(prefix) and line[1:].strip().startswith('class '):
                class_line = line[1:].strip()
                match = re.match(r'class\s+(\w+)', class_line)
                if match:
                    class_name = match.group(1)
                    class_content = [class_line]
                    
                    # Collect class body
                    i += 1
                    while i < len(lines) and (lines[i].startswith(prefix) or lines[i].startswith(' ')):
                        if lines[i].startswith(prefix):
                            class_content.append(lines[i][1:])
                        i += 1
                    
                    classes.append((class_name, '\n'.join(class_content), i))
                    continue
            i += 1
        
        return classes
    
    def _extract_function_signature(self, func_content: str) -> str:
        """Extract function signature from function content."""
        lines = func_content.split('\n')
        for line in lines:
            if line.strip().startswith('def '):
                return line.strip()
        return ""
    
    def _extract_docstring(self, content: str) -> str:
        """Extract docstring from function or class content."""
        lines = content.split('\n')
        in_docstring = False
        docstring_lines = []
        quote_type = None
        
        for line in lines:
            stripped = line.strip()
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    quote_type = stripped[:3]
                    in_docstring = True
                    if stripped.endswith(quote_type) and len(stripped) > 3:
                        # Single line docstring
                        return stripped[3:-3].strip()
                    else:
                        docstring_lines.append(stripped[3:])
            else:
                if stripped.endswith(quote_type):
                    docstring_lines.append(stripped[:-3])
                    break
                else:
                    docstring_lines.append(stripped)
        
        return '\n'.join(docstring_lines).strip()
    
    def _extract_parameters(self, func_content: str) -> List[str]:
        """Extract parameter names from function content."""
        signature = self._extract_function_signature(func_content)
        if not signature:
            return []
        
        # Extract parameters from signature
        match = re.search(r'def\s+\w+\s*\(([^)]*)\)', signature)
        if not match:
            return []
        
        params_str = match.group(1)
        if not params_str.strip():
            return []
        
        params = []
        for param in params_str.split(','):
            param = param.strip()
            if '=' in param:
                param = param.split('=')[0].strip()
            if ':' in param:
                param = param.split(':')[0].strip()
            if param and param not in ['self', 'cls']:
                params.append(param)
        
        return params
    
    def _extract_base_classes(self, class_content: str) -> List[str]:
        """Extract base classes from class definition."""
        lines = class_content.split('\n')
        for line in lines:
            if line.strip().startswith('class '):
                match = re.search(r'class\s+\w+\s*\(([^)]+)\)', line)
                if match:
                    bases_str = match.group(1)
                    return [base.strip() for base in bases_str.split(',')]
        return []
    
    def _parse_import_statement(self, import_line: str) -> Optional[Dict[str, Any]]:
        """Parse import statement into components."""
        import_line = import_line.strip()
        
        if import_line.startswith('from '):
            # from module import items
            match = re.match(r'from\s+([\w.]+)\s+import\s+(.+)', import_line)
            if match:
                module = match.group(1)
                items_str = match.group(2)
                items = [item.strip() for item in items_str.split(',')]
                return {
                    'module': module,
                    'type': 'from_import',
                    'items': items,
                    'alias': ''
                }
        elif import_line.startswith('import '):
            # import module [as alias]
            match = re.match(r'import\s+([\w.]+)(?:\s+as\s+(\w+))?', import_line)
            if match:
                module = match.group(1)
                alias = match.group(2) or ''
                return {
                    'module': module,
                    'type': 'import',
                    'items': [module],
                    'alias': alias
                }
        
        return None
    
    def _generate_change_summary(self, result: DiffAnalysisResult) -> str:
        """Generate a summary of all changes."""
        summary_parts = []
        
        if result.function_changes:
            func_counts = {}
            for func in result.function_changes:
                func_counts[func.change_type] = func_counts.get(func.change_type, 0) + 1
            
            func_summary = []
            for change_type, count in func_counts.items():
                func_summary.append(f"{count} {change_type}")
            summary_parts.append(f"Functions: {', '.join(func_summary)}")
        
        if result.class_changes:
            class_counts = {}
            for cls in result.class_changes:
                class_counts[cls.change_type] = class_counts.get(cls.change_type, 0) + 1
            
            class_summary = []
            for change_type, count in class_counts.items():
                class_summary.append(f"{count} {change_type}")
            summary_parts.append(f"Classes: {', '.join(class_summary)}")
        
        if result.import_changes:
            import_counts = {}
            for imp in result.import_changes:
                import_counts[imp.change_type] = import_counts.get(imp.change_type, 0) + 1
            
            import_summary = []
            for change_type, count in import_counts.items():
                import_summary.append(f"{count} {change_type}")
            summary_parts.append(f"Imports: {', '.join(import_summary)}")
        
        summary_parts.append(f"Lines: +{result.total_lines_added}, -{result.total_lines_removed}")
        summary_parts.append(f"Files: {len(result.files_modified)} modified")
        
        return "; ".join(summary_parts)


@tool
def extract_specific_changes(git_diff: str, change_type: str) -> dict:
    """
    Extract specific changes for targeted documentation from git diff.
    
    Args:
        git_diff: Raw git diff output
        change_type: Type of change (feature, bugfix, etc.)
        
    Returns:
        Dictionary containing detailed analysis of specific changes
    """
    parser = GitDiffParser()
    analysis = parser.parse_diff(git_diff)
    
    return {
        'status': 'success',
        'change_type': change_type,
        'summary': analysis.summary,
        'total_lines_added': analysis.total_lines_added,
        'total_lines_removed': analysis.total_lines_removed,
        'files_modified': analysis.files_modified,
        'function_changes': [
            {
                'name': func.name,
                'file_path': func.file_path,
                'change_type': func.change_type,
                'old_signature': func.old_signature,
                'new_signature': func.new_signature,
                'line_number': func.line_number,
                'docstring': func.docstring,
                'parameters': func.parameters,
                'return_type': func.return_type
            }
            for func in analysis.function_changes
        ],
        'class_changes': [
            {
                'name': cls.name,
                'file_path': cls.file_path,
                'change_type': cls.change_type,
                'line_number': cls.line_number,
                'base_classes': cls.base_classes,
                'docstring': cls.docstring,
                'methods_changed': len(cls.methods_changed)
            }
            for cls in analysis.class_changes
        ],
        'import_changes': [
            {
                'module': imp.module,
                'change_type': imp.change_type,
                'import_type': imp.import_type,
                'imported_items': imp.imported_items,
                'alias': imp.alias,
                'line_number': imp.line_number
            }
            for imp in analysis.import_changes
        ]
    }


@tool
def generate_code_examples_from_diff(git_diff: str, file_path: str, change_type: str) -> dict:
    """
    Generate code examples from actual changes in git diff.
    
    Args:
        git_diff: Raw git diff output
        file_path: Specific file to focus on
        change_type: Type of change (feature, bugfix, etc.)
        
    Returns:
        Dictionary containing generated code examples
    """
    parser = GitDiffParser()
    analysis = parser.parse_diff(git_diff)
    
    examples = []
    
    # Generate examples from function changes
    for func in analysis.function_changes:
        if func.file_path == file_path or file_path == "all":
            if func.change_type == 'added':
                example = {
                    'type': 'new_function',
                    'title': f"New function: {func.name}",
                    'description': f"Added new function {func.name} in {func.file_path}",
                    'code': func.new_signature,
                    'usage_example': _generate_usage_example(func),
                    'parameters': func.parameters,
                    'docstring': func.docstring
                }
                examples.append(example)
                
            elif func.change_type == 'signature_changed':
                example = {
                    'type': 'modified_function',
                    'title': f"Modified function: {func.name}",
                    'description': f"Function signature changed in {func.file_path}",
                    'old_code': func.old_signature,
                    'new_code': func.new_signature,
                    'migration_example': _generate_migration_example(func),
                    'parameters': func.parameters
                }
                examples.append(example)
    
    # Generate examples from class changes
    for cls in analysis.class_changes:
        if cls.file_path == file_path or file_path == "all":
            if cls.change_type == 'added':
                example = {
                    'type': 'new_class',
                    'title': f"New class: {cls.name}",
                    'description': f"Added new class {cls.name} in {cls.file_path}",
                    'code': _extract_class_signature(cls.new_definition),
                    'usage_example': _generate_class_usage_example(cls),
                    'base_classes': cls.base_classes,
                    'docstring': cls.docstring
                }
                examples.append(example)
    
    # Generate examples from import changes
    for imp in analysis.import_changes:
        if imp.change_type == 'added':
            example = {
                'type': 'new_import',
                'title': f"New dependency: {imp.module}",
                'description': f"Added import of {imp.module}",
                'code': _reconstruct_import_statement(imp),
                'usage_hint': f"This enables use of {', '.join(imp.imported_items[:3])}"
            }
            examples.append(example)
    
    return {
        'status': 'success',
        'file_path': file_path,
        'change_type': change_type,
        'examples_count': len(examples),
        'examples': examples
    }


@tool
def generate_file_specific_documentation(git_diff: str, file_path: str, 
                                       existing_docs: str = "", 
                                       doc_type: str = "api") -> dict:
    """
    Generate file-specific documentation updates based on git diff analysis.
    
    Args:
        git_diff: Raw git diff output
        file_path: Specific file to document
        existing_docs: Existing documentation for the file
        doc_type: Type of documentation (api, user_guide, etc.)
        
    Returns:
        Dictionary containing file-specific documentation updates
    """
    # Extract specific changes for this file
    changes_result = extract_specific_changes(git_diff, "unknown")
    if changes_result['status'] != 'success':
        return {'status': 'error', 'error': 'Failed to extract changes'}
    
    # Filter changes for specific file
    file_functions = [f for f in changes_result['function_changes'] if f['file_path'] == file_path]
    file_classes = [c for c in changes_result['class_changes'] if c['file_path'] == file_path]
    file_imports = [i for i in changes_result['import_changes'] if i.get('file_path') == file_path]
    
    if not file_functions and not file_classes and not file_imports:
        return {
            'status': 'success',
            'file_path': file_path,
            'documentation': existing_docs,
            'changes_detected': False,
            'message': 'No significant changes detected for this file'
        }
    
    # Generate documentation sections
    doc_sections = []
    
    # Document new/modified functions
    if file_functions:
        func_docs = _generate_function_documentation(file_functions, doc_type)
        doc_sections.append(func_docs)
    
    # Document new/modified classes
    if file_classes:
        class_docs = _generate_class_documentation(file_classes, doc_type)
        doc_sections.append(class_docs)
    
    # Document new imports/dependencies
    if file_imports:
        import_docs = _generate_import_documentation(file_imports, doc_type)
        doc_sections.append(import_docs)
    
    # Combine with existing documentation
    updated_docs = _merge_with_existing_docs(existing_docs, doc_sections, file_path)
    
    return {
        'status': 'success',
        'file_path': file_path,
        'documentation': updated_docs,
        'changes_detected': True,
        'functions_updated': len(file_functions),
        'classes_updated': len(file_classes),
        'imports_updated': len(file_imports),
        'sections_added': len(doc_sections)
    }


def _generate_usage_example(func: FunctionChange) -> str:
    """Generate usage example for a function."""
    if not func.parameters:
        return f"{func.name}()"
    
    # Create example parameters
    example_params = []
    for param in func.parameters:
        if 'path' in param.lower():
            example_params.append('"path/to/file"')
        elif 'content' in param.lower():
            example_params.append('"example content"')
        elif 'data' in param.lower():
            example_params.append('{"key": "value"}')
        elif param.endswith('_id') or param == 'id':
            example_params.append('123')
        else:
            example_params.append(f'"{param}_value"')
    
    return f"{func.name}({', '.join(example_params)})"


def _generate_migration_example(func: FunctionChange) -> str:
    """Generate migration example for changed function."""
    return f"""# Before:
{func.old_signature}

# After:
{func.new_signature}

# Migration:
# Update calls to {func.name} to use new signature"""


def _generate_class_usage_example(cls: ClassChange) -> str:
    """Generate usage example for a class."""
    instance_name = cls.name.lower()
    example = f"# Create instance\n{instance_name} = {cls.name}()"
    
    if cls.base_classes:
        example += f"\n# Inherits from: {', '.join(cls.base_classes)}"
    
    return example


def _extract_class_signature(class_definition: str) -> str:
    """Extract class signature from full definition."""
    lines = class_definition.split('\n')
    for line in lines:
        if line.strip().startswith('class '):
            return line.strip()
    return class_definition.split('\n')[0]


def _reconstruct_import_statement(imp: ImportChange) -> str:
    """Reconstruct import statement from ImportChange."""
    if imp.import_type == 'from_import':
        items = ', '.join(imp.imported_items)
        return f"from {imp.module} import {items}"
    else:
        if imp.alias:
            return f"import {imp.module} as {imp.alias}"
        else:
            return f"import {imp.module}"


def _generate_function_documentation(functions: List[Dict], doc_type: str) -> str:
    """Generate documentation for function changes."""
    if doc_type == "api":
        return _generate_api_function_docs(functions)
    else:
        return _generate_user_function_docs(functions)


def _generate_class_documentation(classes: List[Dict], doc_type: str) -> str:
    """Generate documentation for class changes."""
    if doc_type == "api":
        return _generate_api_class_docs(classes)
    else:
        return _generate_user_class_docs(classes)


def _generate_import_documentation(imports: List[Dict], doc_type: str) -> str:
    """Generate documentation for import changes."""
    docs = "## Dependencies\n\n"
    
    for imp in imports:
        if imp['change_type'] == 'added':
            docs += f"### New Dependency: {imp['module']}\n\n"
            docs += f"Added import: `{_reconstruct_import_statement_dict(imp)}`\n\n"
            if imp['imported_items']:
                docs += f"Provides: {', '.join(imp['imported_items'])}\n\n"
    
    return docs


def _generate_api_function_docs(functions: List[Dict]) -> str:
    """Generate API documentation for functions."""
    docs = "## API Functions\n\n"
    
    for func in functions:
        if func['change_type'] == 'added':
            docs += f"### `{func['name']}()`\n\n"
            if func['docstring']:
                docs += f"{func['docstring']}\n\n"
            
            if func['parameters']:
                docs += "**Parameters:**\n"
                for param in func['parameters']:
                    docs += f"- `{param}`: Parameter description\n"
                docs += "\n"
            
            docs += f"**Example:**\n```python\n{_generate_usage_example_dict(func)}\n```\n\n"
            
        elif func['change_type'] == 'signature_changed':
            docs += f"### `{func['name']}()` (Modified)\n\n"
            docs += "**Signature changed:**\n\n"
            docs += f"```python\n# Old:\n{func['old_signature']}\n\n# New:\n{func['new_signature']}\n```\n\n"
    
    return docs


def _generate_user_function_docs(functions: List[Dict]) -> str:
    """Generate user-friendly documentation for functions."""
    docs = "## Updated Functions\n\n"
    
    for func in functions:
        if func['change_type'] == 'added':
            docs += f"### New Function: {func['name']}\n\n"
            if func['docstring']:
                docs += f"{func['docstring']}\n\n"
            docs += f"Example usage:\n```python\n{_generate_usage_example_dict(func)}\n```\n\n"
            
        elif func['change_type'] == 'signature_changed':
            docs += f"### Updated: {func['name']}\n\n"
            docs += "The function signature has been updated. "
            docs += "Please update your code accordingly.\n\n"
    
    return docs


def _generate_api_class_docs(classes: List[Dict]) -> str:
    """Generate API documentation for classes."""
    docs = "## API Classes\n\n"
    
    for cls in classes:
        if cls['change_type'] == 'added':
            docs += f"### `{cls['name']}`\n\n"
            if cls['docstring']:
                docs += f"{cls['docstring']}\n\n"
            
            if cls['base_classes']:
                docs += f"**Inherits from:** {', '.join(cls['base_classes'])}\n\n"
            
            docs += f"**Example:**\n```python\n{_generate_class_usage_example_dict(cls)}\n```\n\n"
    
    return docs


def _generate_user_class_docs(classes: List[Dict]) -> str:
    """Generate user-friendly documentation for classes."""
    docs = "## New Classes\n\n"
    
    for cls in classes:
        if cls['change_type'] == 'added':
            docs += f"### {cls['name']}\n\n"
            if cls['docstring']:
                docs += f"{cls['docstring']}\n\n"
            docs += f"Usage:\n```python\n{_generate_class_usage_example_dict(cls)}\n```\n\n"
    
    return docs


def _merge_with_existing_docs(existing_docs: str, new_sections: List[str], file_path: str) -> str:
    """Merge new documentation sections with existing documentation."""
    if not existing_docs.strip():
        # Create new documentation
        header = f"# {file_path} Documentation\n\n"
        header += f"*Auto-generated documentation based on recent changes*\n\n"
        return header + "\n\n".join(new_sections)
    
    # Append to existing documentation
    timestamp = _get_current_timestamp()
    update_section = f"\n\n---\n\n## Recent Changes ({timestamp})\n\n"
    update_section += "\n\n".join(new_sections)
    
    return existing_docs + update_section


def _generate_usage_example_dict(func_dict: Dict) -> str:
    """Generate usage example from function dictionary."""
    if not func_dict['parameters']:
        return f"{func_dict['name']}()"
    
    example_params = []
    for param in func_dict['parameters']:
        if 'path' in param.lower():
            example_params.append('"path/to/file"')
        elif 'content' in param.lower():
            example_params.append('"example content"')
        else:
            example_params.append(f'"{param}_value"')
    
    return f"{func_dict['name']}({', '.join(example_params)})"


def _generate_class_usage_example_dict(cls_dict: Dict) -> str:
    """Generate class usage example from class dictionary."""
    instance_name = cls_dict['name'].lower()
    return f"{instance_name} = {cls_dict['name']}()"


def _reconstruct_import_statement_dict(imp_dict: Dict) -> str:
    """Reconstruct import statement from dictionary."""
    if imp_dict['import_type'] == 'from_import':
        items = ', '.join(imp_dict['imported_items'])
        return f"from {imp_dict['module']} import {items}"
    else:
        if imp_dict['alias']:
            return f"import {imp_dict['module']} as {imp_dict['alias']}"
        else:
            return f"import {imp_dict['module']}"


def _get_current_timestamp() -> str:
    """Get current timestamp."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")