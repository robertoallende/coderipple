"""
File System Tools for CodeRipple

This module provides file system navigation and inspection tools that complement
git-based analysis. These tools help agents explore the complete project structure,
including untracked files, build artifacts, and configuration files.

Usage:
    These tools work alongside git_tools to provide comprehensive project analysis.
    They're particularly useful for understanding build outputs, configuration files,
    and project structure beyond just source code.

Example:
    from strands import Agent
    from coderipple.file_system_tools import list_directory, peek_file, change_directory
    from coderipple.git_tools import git_files
    
    agent = Agent(
        system_prompt="You can explore the complete file system...",
        tools=[list_directory, peek_file, git_files, ...]
    )
"""

from strands import tool
import os
import subprocess
from pathlib import Path
from typing import Optional


def _validate_path(path: str) -> str:
    """Validate and sanitize file system paths to prevent security issues."""
    try:
        # Convert to Path object and resolve to absolute path
        resolved_path = Path(path).resolve()
        
        # Convert back to string for subprocess operations
        return str(resolved_path)
        
    except Exception:
        # If validation fails, default to current directory
        return str(Path.cwd())


@tool
def list_directory(path: str = ".", show_hidden: bool = False, detailed: bool = False) -> str:
    """List directory contents including both tracked and untracked files.
    
    This tool shows the complete file system view, including build artifacts,
    configuration files, and other items that might not be in git. Essential
    for understanding the full project structure.
    
    Args:
        path: Directory path to list (default: current directory)
        show_hidden: Include hidden files and directories (default: False)
        detailed: Show detailed information like file sizes and permissions (default: False)
    
    Returns:
        String containing directory listing or error message
    """
    try:
        safe_path = _validate_path(path)
        
        # Build ls command based on options
        cmd_parts = ["ls"]
        
        if detailed:
            cmd_parts.append("-la" if show_hidden else "-l")
        else:
            cmd_parts.append("-a" if show_hidden else "")
        
        # Add path
        cmd_parts.append(f'"{safe_path}"')
        
        command = " ".join(filter(None, cmd_parts))
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            if not output:
                return f"Directory is empty: {path}"
            
            # Add context about what directory we're listing
            header = f"Contents of {path}:\n" + "=" * (len(path) + 12) + "\n"
            return header + output
        else:
            return f"Error listing directory {path}: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Error: Directory listing timed out for {path}"
    except Exception as e:
        return f"Directory listing failed: {str(e)}"


@tool
def peek_file(file_path: str, lines: int = 20, from_end: bool = False) -> str:
    """Quick preview of file contents without full file reading.
    
    This tool is perfect for getting a quick sense of what's in a file before
    deciding whether to do a full file_read(). Much faster than reading entire
    large files when you just need to understand the file type and content.
    
    Args:
        file_path: Path to the file to preview
        lines: Number of lines to show (default: 20)
        from_end: Show lines from end of file instead of beginning (default: False)
    
    Returns:
        String containing file preview or error message
    """
    try:
        safe_path = _validate_path(file_path)
        
        # Check if file exists and is readable
        if not Path(safe_path).exists():
            return f"File does not exist: {file_path}"
        
        if not Path(safe_path).is_file():
            return f"Path is not a file: {file_path}"
        
        # Use head or tail based on from_end parameter
        command = f"tail -{lines}" if from_end else f"head -{lines}"
        command += f' "{safe_path}"'
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            
            # Add context about what we're showing
            direction = "last" if from_end else "first"
            header = f"{direction.title()} {lines} lines of {file_path}:\n" + "=" * 50 + "\n"
            
            if not output:
                return f"File appears to be empty: {file_path}"
            
            return header + output
        else:
            return f"Error reading file {file_path}: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Error: File preview timed out for {file_path}"
    except Exception as e:
        return f"File preview failed: {str(e)}"


@tool
def change_directory(path: str) -> str:
    """Change the working directory for subsequent file operations.
    
    This tool changes the current working directory, which affects all subsequent
    relative path operations. Useful for exploring different parts of a project
    or working within specific subdirectories.
    
    Args:
        path: Directory path to change to
    
    Returns:
        String confirming directory change or error message
    """
    try:
        safe_path = _validate_path(path)
        
        # Check if directory exists
        if not Path(safe_path).exists():
            return f"Directory does not exist: {path}"
        
        if not Path(safe_path).is_dir():
            return f"Path is not a directory: {path}"
        
        # Change directory
        os.chdir(safe_path)
        
        # Confirm the change
        current_dir = os.getcwd()
        return f"Changed working directory to: {current_dir}"
        
    except Exception as e:
        return f"Failed to change directory: {str(e)}"


@tool
def find_files_by_pattern(pattern: str, path: str = ".", max_results: int = 50) -> str:
    """Find files matching a specific pattern in the directory tree.
    
    This tool helps discover files by name patterns, which is useful for finding
    configuration files, build outputs, or specific file types that might not
    be obvious from directory listings.
    
    Args:
        pattern: File pattern to search for (e.g., "*.json", "*.md", "build*")
        path: Directory to search in (default: current directory)
        max_results: Maximum number of results to return (default: 50)
    
    Returns:
        String containing list of matching files or error message
    """
    try:
        safe_path = _validate_path(path)
        
        # Use find command to search for pattern
        command = f'find "{safe_path}" -name "{pattern}" -type f | head -{max_results}'
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            output = result.stdout.strip()
            
            if not output:
                return f"No files found matching pattern '{pattern}' in {path}"
            
            # Count results and add header
            file_list = output.split('\n')
            count = len(file_list)
            
            header = f"Found {count} files matching '{pattern}' in {path}:\n" + "=" * 50 + "\n"
            return header + output
        else:
            return f"Error searching for pattern '{pattern}': {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Error: File search timed out for pattern '{pattern}'"
    except Exception as e:
        return f"File search failed: {str(e)}"


@tool
def get_file_info(file_path: str) -> str:
    """Get detailed information about a file or directory.
    
    This tool provides metadata about files including size, permissions, modification
    time, and file type. Useful for understanding file characteristics before
    deciding how to process them.
    
    Args:
        file_path: Path to the file or directory to inspect
    
    Returns:
        String containing file information or error message
    """
    try:
        safe_path = _validate_path(file_path)
        
        # Check if path exists
        if not Path(safe_path).exists():
            return f"Path does not exist: {file_path}"
        
        # Use ls -la to get detailed file information
        command = f'ls -la "{safe_path}"'
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Also get file type information
            file_command = f'file "{safe_path}"'
            file_result = subprocess.run(
                file_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            info = f"File information for {file_path}:\n" + "=" * 40 + "\n"
            info += result.stdout.strip() + "\n\n"
            
            if file_result.returncode == 0:
                info += "File type: " + file_result.stdout.strip()
            
            return info
        else:
            return f"Error getting file info for {file_path}: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return f"Error: File info request timed out for {file_path}"
    except Exception as e:
        return f"File info request failed: {str(e)}"


@tool
def explore_project_structure(path: str = ".", max_depth: int = 3) -> str:
    """Get a comprehensive overview of project structure including directories and key files.
    
    This tool provides a tree-like view of the project structure, helping agents
    understand the overall organization before diving into specific analysis.
    Combines directory exploration with file discovery.
    
    Args:
        path: Root directory to explore (default: current directory)
        max_depth: Maximum directory depth to explore (default: 3)
    
    Returns:
        String containing project structure overview or error message
    """
    try:
        safe_path = _validate_path(path)
        
        # Use tree command if available, otherwise use find
        tree_command = f'tree -L {max_depth} "{safe_path}"'
        
        result = subprocess.run(
            tree_command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            header = f"Project structure for {path} (depth {max_depth}):\n" + "=" * 60 + "\n"
            return header + result.stdout.strip()
        else:
            # Fallback to find if tree is not available
            find_command = f'find "{safe_path}" -maxdepth {max_depth} -type d | sort'
            
            find_result = subprocess.run(
                find_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if find_result.returncode == 0:
                header = f"Directory structure for {path} (depth {max_depth}):\n" + "=" * 60 + "\n"
                return header + find_result.stdout.strip()
            else:
                return f"Error exploring project structure: {find_result.stderr}"
                
    except subprocess.TimeoutExpired:
        return f"Error: Project structure exploration timed out for {path}"
    except Exception as e:
        return f"Project structure exploration failed: {str(e)}"


# Tool usage context and examples for LLM agents
FILE_SYSTEM_USAGE_GUIDE = """
File System Tool Usage Guide for LLM Agents:

1. **Project Exploration Workflow:**
   - explore_project_structure() to get overall layout
   - list_directory() to see contents of specific directories
   - find_files_by_pattern() to locate specific file types
   - peek_file() to quickly preview files before full analysis

2. **Navigation Strategy:**
   - Use change_directory() to move into subdirectories
   - All subsequent relative paths will be relative to new directory
   - Return to root with change_directory(".") or change_directory("/path/to/root")

3. **File Analysis:**
   - get_file_info() to understand file characteristics
   - peek_file() for quick content preview (faster than file_read)
   - Use file_read() from strands_tools for full file analysis

4. **Common Patterns:**
   - list_directory(".", show_hidden=True) to see all files including config
   - find_files_by_pattern("*.json") to find all configuration files
   - peek_file("package.json", lines=10) to quickly check project type
   - explore_project_structure(".", max_depth=2) for overview

5. **Integration with Git Tools:**
   - git_files() shows tracked files
   - list_directory() shows ALL files (including build artifacts, logs)
   - Use both to understand complete project ecosystem

6. **Performance Tips:**
   - Use peek_file() before file_read() for large files
   - Use find_files_by_pattern() instead of multiple list_directory() calls
   - explore_project_structure() gives quick overview without detailed analysis

These tools provide comprehensive file system access beyond git tracking,
essential for understanding build processes, configuration, and complete project structure.
"""