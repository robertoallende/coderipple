"""
CodeRipple: Git Repository Analysis Tools

This module provides specialized tools for analyzing git repositories to generate 
comprehensive code documentation. These tools are designed to be used by LLM agents
to understand codebases through git history, file structure, and repository metadata.

Usage:
    These tools are meant to be imported and used by Strands Agents for automated
    code documentation generation. Each tool is decorated with @tool to make it
    available to LLM agents.

Example:
    from strands import Agent
    from strands_tools import file_read
    from coderipple.git_tools import git_log, git_files, git_contributors
    
    agent = Agent(
        system_prompt="You are a code documentation expert...",
        tools=[git_log, git_files, git_contributors, file_read]
    )
"""

from strands import tool
import subprocess
import os
from typing import Optional
from pathlib import Path


def _validate_repo_path(repo_path: str) -> str:
    """Validate and sanitize repository path to prevent shell injection."""
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(repo_path).resolve()
        
        # Basic validation - must exist and be a directory
        if not path.exists():
            raise ValueError(f"Path does not exist: {repo_path}")
        if not path.is_dir():
            raise ValueError(f"Path is not a directory: {repo_path}")
            
        # Return absolute path as string
        return str(path)
        
    except Exception:
        # If validation fails, default to current directory
        return str(Path.cwd())


@tool
def git_log(repo_path: str = ".", max_entries: int = 20, format_type: str = "oneline") -> str:
    """Get git commit history to understand project evolution and recent changes.
    
    This tool helps agents understand what the project does by examining commit
    messages, development patterns, and recent activity. Useful for understanding
    project direction and identifying key features.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
        max_entries: Maximum number of commits to retrieve (default: 20)
        format_type: Git log format - 'oneline', 'detailed', or 'stats' (default: 'oneline')
    
    Returns:
        String containing git log output or error message if command fails
    """
    try:
        # Validate and sanitize the repository path
        safe_repo_path = _validate_repo_path(repo_path)
        
        # Define different log formats for different analysis needs
        formats = {
            'oneline': f'git log --oneline -{max_entries}',
            'detailed': f'git log --pretty=format:"%h %ad %s" --date=short -{max_entries}',
            'stats': f'git log --stat -{max_entries}'
        }
        
        command = formats.get(format_type, formats['oneline'])
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=safe_repo_path  # Use cwd instead of cd command
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"Error executing git log: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: Git log command timed out"
    except Exception as e:
        return f"Git log failed: {str(e)}"


@tool
def git_files(repo_path: str = ".", file_pattern: Optional[str] = None) -> str:
    """List all tracked files in the repository to understand project structure.
    
    This tool helps agents understand the codebase organization, identify main
    source files, configuration files, and documentation. Essential for mapping
    out the architecture and determining which files to examine.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
        file_pattern: Optional pattern to filter files (e.g., '*.py', '*.js')
    
    Returns:
        String containing list of tracked files or error message if command fails
    """
    try:
        base_command = "git ls-files"
        
        # Add file pattern filter if specified
        if file_pattern:
            command = f"{base_command} | grep '{file_pattern}'"
        else:
            command = base_command
        
        result = subprocess.run(
            f"cd {repo_path} && {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            files = result.stdout.strip()
            if not files:
                return f"No files found matching pattern: {file_pattern}" if file_pattern else "No tracked files found"
            return files
        else:
            return f"Error listing git files: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: Git ls-files command timed out"
    except Exception as e:
        return f"Git ls-files failed: {str(e)}"


@tool
def git_contributors(repo_path: str = ".", since: str = "6 months ago", max_contributors: int = 10) -> str:
    """Get list of contributors and their commit counts to understand team structure.
    
    This tool helps agents understand who is working on the project, identify
    main contributors, and gauge project activity levels. Useful for understanding
    project maintenance status and team size.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
        since: Time period to analyze (default: '6 months ago')
        max_contributors: Maximum number of contributors to show (default: 10)
    
    Returns:
        String containing contributor statistics or error message if command fails
    """
    try:
        result = subprocess.run(
            f"cd {repo_path} && git shortlog -sn --since='{since}' | head -{max_contributors}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            contributors = result.stdout.strip()
            if not contributors:
                return f"No contributors found since {since}"
            return contributors
        else:
            return f"Error getting contributors: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: Git contributors command timed out"
    except Exception as e:
        return f"Git contributors analysis failed: {str(e)}"


@tool
def git_recent_files(repo_path: str = ".", since: str = "3 months ago", max_files: int = 20) -> str:
    """Get most frequently changed files to identify core components.
    
    This tool helps agents identify the most actively developed files, which
    are typically the core components of the project. These files should be
    prioritized when analyzing the codebase architecture.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
        since: Time period to analyze (default: '3 months ago')
        max_files: Maximum number of files to return (default: 20)
    
    Returns:
        String containing frequently changed files with change counts
    """
    try:
        # Get files changed since specified time, count occurrences, sort by frequency
        command = (
            f"git log --name-only --since='{since}' --pretty=format: | "
            f"grep -v '^$' | sort | uniq -c | sort -nr | head -{max_files}"
        )
        
        result = subprocess.run(
            f"cd {repo_path} && {command}",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            files = result.stdout.strip()
            if not files:
                return f"No file changes found since {since}"
            return files
        else:
            return f"Error analyzing recent files: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: Recent files analysis timed out"
    except Exception as e:
        return f"Recent files analysis failed: {str(e)}"


@tool
def git_branch_info(repo_path: str = ".") -> str:
    """Get branch information to understand development workflow and release strategy.
    
    This tool helps agents understand the project's branching strategy, identify
    main development branches, and understand the release workflow. Important for
    documenting how the project is developed and maintained.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        String containing branch information or error message if command fails
    """
    try:
        # Get both local and remote branches with current branch indicator
        result = subprocess.run(
            f"cd {repo_path} && git branch -a",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            branches = result.stdout.strip()
            if not branches:
                return "No branches found"
            return branches
        else:
            return f"Error getting branch info: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Error: Branch info command timed out"
    except Exception as e:
        return f"Branch info analysis failed: {str(e)}"


@tool
def git_repo_stats(repo_path: str = ".") -> str:
    """Get comprehensive repository statistics for project overview.
    
    This tool provides high-level statistics about the repository including
    total commits, contributors, and time span. Useful for understanding
    project maturity and scale.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        String containing repository statistics or error message if command fails
    """
    try:
        # Get various repository statistics
        commands = {
            'total_commits': 'git rev-list --all --count',
            'first_commit': 'git log --reverse --pretty=format:"%ad" --date=short | head -1',
            'last_commit': 'git log -1 --pretty=format:"%ad" --date=short',
            'total_contributors': 'git shortlog -sn | wc -l',
            'total_files': 'git ls-files | wc -l'
        }
        
        stats = {}
        for stat_name, command in commands.items():
            result = subprocess.run(
                f"cd {repo_path} && {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                stats[stat_name] = result.stdout.strip()
            else:
                stats[stat_name] = "unknown"
        
        # Format the statistics into a readable summary
        summary = f"""Repository Statistics:
- Total commits: {stats['total_commits']}
- Total contributors: {stats['total_contributors']}
- Total tracked files: {stats['total_files']}
- First commit: {stats['first_commit']}
- Last commit: {stats['last_commit']}"""
        
        return summary
        
    except subprocess.TimeoutExpired:
        return "Error: Repository stats command timed out"
    except Exception as e:
        return f"Repository stats analysis failed: {str(e)}"


@tool
def find_key_files(repo_path: str = ".") -> str:
    """Find key configuration and documentation files in the repository.
    
    This tool identifies important files like README, package.json, requirements.txt,
    Dockerfile, etc. These files are crucial for understanding how to set up and
    run the project.
    
    Args:
        repo_path: Path to the git repository (default: current directory)
    
    Returns:
        String containing list of found key files or message if none found
    """
    try:
        # Define patterns for key files that are important for documentation
        key_patterns = [
            "README*", "readme*",
            "package.json", "package-lock.json",
            "requirements.txt", "requirements*.txt", "pyproject.toml", "setup.py",
            "Dockerfile", "docker-compose*",
            "Makefile", "makefile",
            "*.config.js", "*.config.ts", "*.json",
            "LICENSE", "license*",
            ".env*", "env*",
            "yarn.lock", "pnpm-lock.yaml",
            "go.mod", "Cargo.toml",
            "pom.xml", "build.gradle"
        ]
        
        found_files = []
        
        for pattern in key_patterns:
            result = subprocess.run(
                f"cd {repo_path} && find . -maxdepth 2 -name '{pattern}' -type f",
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                files = result.stdout.strip().split('\n')
                found_files.extend([f.strip() for f in files if f.strip()])
        
        if found_files:
            # Remove duplicates and sort
            unique_files = sorted(list(set(found_files)))
            return '\n'.join(unique_files)
        else:
            return "No key configuration or documentation files found"
            
    except subprocess.TimeoutExpired:
        return "Error: Find key files command timed out"
    except Exception as e:
        return f"Find key files failed: {str(e)}"


# Tool usage context and examples for LLM agents
TOOL_USAGE_GUIDE = """
CodeRipple Tool Usage Guide for LLM Agents:

1. Start with git_repo_stats() to get project overview
2. Use git_branch_info() to understand development workflow
3. Use find_key_files() to identify important configuration files
4. Use git_contributors() to understand team and activity level
5. Use git_recent_files() to identify core/active components
6. Use git_files() to get full file structure
7. Use git_log() to understand recent development and features

Example workflow:
1. Get repository overview and statistics
2. Identify and read key configuration files (README, package.json, etc.)
3. Find most important source files through git analysis
4. Read and analyze core source files
5. Generate comprehensive documentation

Each tool includes error handling and timeouts for robust operation.
"""