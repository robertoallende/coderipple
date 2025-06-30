"""
Magic Mirror: CodeRipple's Intelligent Documentation Agent

"Mirror, mirror on the wall, tell me about this codebase, once and for all!"

Like the enchanted mirror from Snow White, Magic Mirror reflects back the truth
about code repositories - revealing their purpose, structure, and secrets through
intelligent analysis and progressive documentation generation.

Usage:
    from coderipple.magic_mirror import create_magic_mirror, analyze_repository
    
    # Create the magic mirror
    mirror = create_magic_mirror()
    
    # Ask it to reveal the truth about a repository
    documentation = mirror("Mirror, mirror, analyze this repository: /path/to/repo")
    
    # Or use the convenience function
    docs = analyze_repository("/path/to/repo")
"""

import logging
import os
import sys
from strands import Agent
from strands_tools import file_read, file_write

# Configure logging for AWS Lambda compatibility
def setup_logging():
    """Configure logging for both local development and AWS Lambda environments."""
    
    # Get log level from environment variable (default to INFO)
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure root logger
    logger = logging.getLogger('magic_mirror')
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # AWS Lambda automatically captures stdout/stderr to CloudWatch
    # So we just need a StreamHandler to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    # Prevent duplicate logging in Lambda
    logger.propagate = False
    
    return logger

# Initialize logger
logger = setup_logging()

# Import our specialized tools - handle both relative and absolute imports
try:
    # Try relative imports first (when used as module)
    from .git_tools import (
        git_log, git_files, git_contributors, git_recent_files,
        git_branch_info, git_repo_stats, find_key_files
    )
    from .generic_tools import (
        execution_time_status, quick_time_check, current_time, reset_execution_timer
    )
    from .file_system_tools import (
        list_directory, peek_file, change_directory, find_files_by_pattern,
        get_file_info, explore_project_structure
    )
    from .prompts import (
        GETTING_STARTED_PROMPT, ARCHITECTURE_PROMPT, EVOLUTION_PROMPT,
        GETTING_STARTED_QUALITY_CHECK, GETTING_STARTED_IMPROVEMENT,
        ARCHITECTURE_QUALITY_CHECK, ARCHITECTURE_IMPROVEMENT,
        DOCUMENTATION_COMBINER_PROMPT, PROMPT_TOOL_MAPPING
    )
    from .config import get_agent_config, CONSOLE_SEPARATOR, CONSOLE_HEADER, OUTPUT_FILE_SUFFIX, OUTPUT_FILE_ENCODING
except ImportError:
    # Fall back to absolute imports (when run as script)
    from git_tools import (
        git_log, git_files, git_contributors, git_recent_files,
        git_branch_info, git_repo_stats, find_key_files
    )
    from generic_tools import (
        execution_time_status, quick_time_check, current_time, reset_execution_timer
    )
    from file_system_tools import (
        list_directory, peek_file, change_directory, find_files_by_pattern,
        get_file_info, explore_project_structure
    )
    from prompts import (
        GETTING_STARTED_PROMPT, ARCHITECTURE_PROMPT, EVOLUTION_PROMPT,
        GETTING_STARTED_QUALITY_CHECK, GETTING_STARTED_IMPROVEMENT,
        ARCHITECTURE_QUALITY_CHECK, ARCHITECTURE_IMPROVEMENT,
        DOCUMENTATION_COMBINER_PROMPT, PROMPT_TOOL_MAPPING
    )
    from config import get_agent_config, CONSOLE_SEPARATOR, CONSOLE_HEADER, OUTPUT_FILE_SUFFIX, OUTPUT_FILE_ENCODING

# Import smart project type detection
try:
    from better_prompts import ProjectTypeDetector, enhance_coderipple_analysis
    SMART_DETECTION_AVAILABLE = True
    logger.info("🎯 Smart project detection enabled - better_prompts.py loaded")
except ImportError:
    SMART_DETECTION_AVAILABLE = False
    logger.warning("🚫 Smart project detection not available - better_prompts.py not found")


def create_magic_mirror(quiet: bool = False) -> Agent:
    """Create the Magic Mirror agent with full analytical capabilities.
    
    Returns:
        Agent configured with comprehensive tools and intelligent system prompt
    """
    
    # The Magic Mirror's core system prompt
    MAGIC_MIRROR_PROMPT = """You are the Magic Mirror - an enchanted agent that reveals the truth about code repositories through intelligent analysis.

**Your Identity:**
Just like the magical mirror from Snow White, you reflect back the clear truth about what you observe. When asked "Mirror, mirror, tell me about this codebase," you provide comprehensive, honest, and insightful documentation.

**Your Mission:**
Transform any code repository into crystal-clear documentation that helps developers understand, setup, and work with the project effectively.

**Time-Aware Intelligence:**
You operate under AWS Lambda constraints (14-minute limit) and must be strategic:

1. **Always start by checking execution_time_status()** to understand your time constraints
2. **Adapt your analysis depth** based on time available
3. **Prioritize essential information** when time is limited
4. **Always deliver valuable documentation** within time limits

**Comprehensive Analysis Strategy:**

**ALWAYS complete ALL phases - this is a thorough analysis, not a quick summary.**

**IMPORTANT: Be verbose about your progress. When starting each phase, say:**
- "🔍 PHASE 1: Getting Started Analysis - gathering project overview..."
- "🏗️ PHASE 2: Architecture Analysis - examining project structure..." 
- "📈 PHASE 3: Project Evolution Analysis - studying development patterns..."

**Phase 1: Getting Started (REQUIRED)**
- Start by saying "🔍 PHASE 1: Getting Started Analysis"
- Use git_repo_stats() for project overview
- Use find_key_files() to locate setup documentation  
- Use peek_file() and file_read() to understand setup process
- Generate clear setup instructions that get developers from "git clone" to "it works"

**Phase 2: Architecture Analysis (REQUIRED)**
- Start by saying "🏗️ PHASE 2: Architecture Analysis"
- Use git_files() and git_recent_files() to understand structure
- Use explore_project_structure() for detailed layout overview
- Use file_read() on key source files, main entry points, and core modules
- Identify design patterns, data flow, and component relationships
- **CREATE an ASCII diagram** showing the architecture and component relationships
- Generate comprehensive architecture documentation with:
  * Project structure breakdown
  * Key components and their responsibilities
  * Data flow and execution paths
  * Technology stack and frameworks
  * **ASCII architecture diagram**

**Phase 3: Project Evolution (REQUIRED)**
- Start by saying "📈 PHASE 3: Project Evolution Analysis"
- Use git_log(), git_contributors(), git_branch_info() for project history
- Analyze development patterns and project health
- Generate insights about project trajectory and maintenance

**Quality Improvement Phase:**
- Say "✨ QUALITY IMPROVEMENT: Reviewing and enhancing documentation..."
- Review generated sections for completeness and clarity
- Add missing details or explanations where needed

**Quality Improvement Strategy:**
When time permits, assess and improve your documentation:
1. Review your generated documentation for completeness
2. Identify gaps or unclear sections
3. Use additional file analysis to fill gaps
4. Enhance with specific examples and details

**Tool Usage Guidelines:**

*Time Management:*
- execution_time_status() - Check time and get strategic recommendations
- quick_time_check() - Fast decisions during analysis

*Repository Intelligence:*
- git_repo_stats() - Overall project statistics and health
- git_files() - Complete file structure from git perspective
- git_recent_files() - Identify most important/active components
- git_log() - Understand recent development and features
- git_contributors() - Team structure and activity
- git_branch_info() - Development workflow patterns

*File System Exploration:*
- explore_project_structure() - Get visual project layout
- list_directory() - See all files including build artifacts
- find_files_by_pattern() - Locate specific file types
- peek_file() - Quick previews before detailed analysis
- change_directory() - Navigate project structure

*File Analysis:*
- file_read() - Detailed file content analysis
- get_file_info() - File metadata and characteristics

**Execution Guidelines:**
- Complete ALL three phases thoroughly
- Use execution_time_status() to monitor progress, but don't skip phases
- If running low on time, make sections more concise but still complete
- Read multiple source files for deep understanding
- Always include the architecture diagram

**Documentation Standards:**
- Write for developers who are new to the project
- Include specific, copy-pasteable commands
- Explain the "why" behind architectural decisions
- Use git insights to provide development context
- Always be honest about what you found (or didn't find)

**Required Response Format:**
Generate comprehensive markdown documentation with ALL these sections. 

**IMPORTANT: Do NOT wrap your response in code blocks. Return the markdown content directly.**

Your response should follow this structure:

# Project Name

## Project Overview
Brief description and purpose

## Getting Started  
Complete setup instructions and prerequisites

## Architecture
Detailed architecture analysis including:
- Project structure breakdown
- Key components and responsibilities  
- Technology stack
- **ASCII Architecture Diagram** 
- Data flow and design patterns

## Project Evolution
Development history and project health analysis

**Architecture Diagram Requirements:**
Create an ASCII diagram using characters like:
```
┌─────────┐    ┌─────────┐    ┌─────────┐
│Component│────│Component│────│Component│
└─────────┘    └─────────┘    └─────────┘
     │              │              │
     ▼              ▼              ▼
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Module  │    │ Module  │    │ Module  │
└─────────┘    └─────────┘    └─────────┘
```

Remember: Like the magic mirror, you reveal truth through careful observation. Your documentation should be the honest reflection of what the repository really is and how it really works."""

    # Get agent configuration from config file
    agent_config = get_agent_config()
    
    # Configure callback handler based on quiet mode
    if quiet:
        from strands.handlers import null_callback_handler
        callback_handler = null_callback_handler
    else:
        callback_handler = None  # Use default PrintingCallbackHandler
    
    # Create the Magic Mirror with comprehensive tool access
    mirror = Agent(
        system_prompt=MAGIC_MIRROR_PROMPT,
        callback_handler=callback_handler,
        **agent_config,
        tools=[
            # Time management - essential for Lambda execution
            execution_time_status, quick_time_check, current_time,
            
            # Git repository intelligence
            git_repo_stats, git_files, git_recent_files, git_log,
            git_contributors, git_branch_info, find_key_files,
            
            # File system exploration
            explore_project_structure, list_directory, peek_file,
            change_directory, find_files_by_pattern, get_file_info,
            
            # File analysis and manipulation
            file_read, file_write
        ]
    )
    
    return mirror


def detect_project_type(repo_path: str) -> dict:
    """Detect project type and get specialized analysis config.
    
    Returns:
        dict: Contains project_type, specialized_prompt, wow_factor, etc.
    """
    if not SMART_DETECTION_AVAILABLE:
        return {
            'project_type': 'generic',
            'specialized_prompt': None,
            'wow_factor': 'comprehensive project analysis',
            'analysis_focus': 'General project analysis'
        }
    
    try:
        # Get file list from git and file system
        from pathlib import Path
        from subprocess import run, PIPE
        
        repo_path_obj = Path(repo_path)
        
        # Get file list from git if available
        result = run(['git', 'ls-files'], cwd=repo_path, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            file_list = result.stdout.strip().split('\n')
        else:
            # Fallback to file system
            file_list = [str(f.relative_to(repo_path_obj)) for f in repo_path_obj.rglob('*') if f.is_file()]
        
        # Read key files for content analysis
        file_contents = {}
        key_files = ['package.json', 'requirements.txt', 'manage.py', 'Dockerfile', 'Cargo.toml', 'pom.xml', 'pubspec.yaml']
        
        for key_file in key_files:
            file_path = repo_path_obj / key_file
            if file_path.exists() and file_path.is_file():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_contents[key_file] = f.read()[:2000]  # Limit content size
                except:
                    continue
        
        # Use smart detection
        enhanced_analysis = enhance_coderipple_analysis(file_list, file_contents)
        logger.info(f"🎯 Detected project type: {enhanced_analysis['project_type']}")
        if enhanced_analysis['project_type'] != 'generic':
            logger.info(f"🌟 Wow factor: {enhanced_analysis['wow_factor']}")
        
        return enhanced_analysis
        
    except Exception as e:
        logger.warning(f"🚫 Smart detection failed: {e}")
        return {
            'project_type': 'generic',
            'specialized_prompt': None,
            'wow_factor': 'comprehensive project analysis',
            'analysis_focus': 'General project analysis'
        }


def analyze_repository(repo_path: str, quiet: bool = False) -> str:
    """Ask the Magic Mirror to analyze a repository and generate documentation.
    
    This is the main entry point for repository analysis. The Magic Mirror will
    perform time-aware, progressive analysis to generate the best possible
    documentation within execution constraints.
    
    Args:
        repo_path: Path to the git repository to analyze
        quiet: Whether to suppress console output during analysis
        
    Returns:
        String containing comprehensive markdown documentation
        
    Raises:
        ValueError: If repo_path is invalid or doesn't exist
    """
    from pathlib import Path
    
    # Validate repository path
    repo_path_obj = Path(repo_path)
    if not repo_path_obj.exists():
        error_msg = f"Repository path does not exist: {repo_path}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    if not repo_path_obj.is_dir():
        error_msg = f"Repository path is not a directory: {repo_path}"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    logger.info(f"🪞 Magic Mirror: Starting analysis of repository: {repo_path}")
    
    # Detect project type for specialized analysis
    project_analysis = detect_project_type(repo_path)
    
    # Create the Magic Mirror (potentially with specialized prompt)
    if project_analysis['project_type'] != 'generic' and project_analysis['specialized_prompt']:
        logger.info(f"🎯 Using specialized {project_analysis['project_type']} analysis")
        # Create mirror with specialized prompt
        mirror = create_magic_mirror(quiet=quiet)
        # We'll update the system prompt for this analysis
        specialized_query = True
    else:
        logger.info("🔧 Using comprehensive generic analysis")
        mirror = create_magic_mirror(quiet=quiet)
        specialized_query = False
    
    # Ask the Magic Mirror to reveal the truth about this repository
    if specialized_query and project_analysis['specialized_prompt']:
        # Use specialized prompt for detected framework
        base_query = f"""Mirror, mirror, reveal the truth about this {project_analysis['project_type']} codebase!

🎯 SPECIALIZED ANALYSIS DETECTED: {project_analysis['project_type'].upper()}
🌟 Focus Area: {project_analysis['wow_factor']}

{project_analysis['specialized_prompt']}

**IMPORTANT: Log your progress as you work by mentioning what phase you're in.**

Repository location: {repo_path}

**Analysis Process:**
1. Start with "🔍 PHASE 1: {project_analysis['project_type'].title()} Getting Started Analysis" 
2. Then "🏗️ PHASE 2: {project_analysis['project_type'].title()} Architecture Analysis"
3. Then "📈 PHASE 3: Project Evolution Analysis"
4. Apply quality improvements focusing on {project_analysis['project_type']} best practices

Use your tools strategically and highlight {project_analysis['project_type']}-specific features and patterns."""
        query = base_query
    else:
        # Use generic comprehensive analysis
        query = f"""Mirror, mirror, reveal the truth about this codebase!

Analyze the repository at: {repo_path}

**IMPORTANT: Log your progress as you work by mentioning what phase you're in.**

Provide comprehensive documentation that helps developers understand:
1. What this project does and how to get it running
2. How the project is structured and organized  
3. The development context and project evolution

**Analysis Process:**
1. Start with "🔍 PHASE 1: Getting Started Analysis" 
2. Then "🏗️ PHASE 2: Architecture Analysis"
3. Then "📈 PHASE 3: Project Evolution Analysis"
4. Apply quality improvements as needed

Use your tools strategically and mention which tools you're using.
Always deliver comprehensive documentation with all required sections."""

    logger.info("🪞 Magic Mirror: Beginning comprehensive analysis...")
    logger.info("📋 Analysis will include: Getting Started → Architecture → Evolution → Quality Improvements")
    logger.info("⏱️ Expected phases: ~3-5 minutes each, plus quality improvements")
    
    # The Magic Mirror reflects back the truth
    result = str(mirror(query))
    
    logger.info("🏁 Magic Mirror: Raw analysis complete, now cleaning response...")
    
    # Clean up the response - remove leading/trailing whitespace and unwanted prefixes
    cleaned_result = result.strip()
    
    # Remove markdown code block wrapper if present
    if cleaned_result.startswith('```markdown'):
        lines = cleaned_result.split('\n')
        # Remove first line (```markdown) and last line if it's closing backticks
        if lines and lines[0].strip() == '```markdown':
            lines = lines[1:]
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        cleaned_result = '\n'.join(lines)
    
    # Remove everything before the first markdown header and clean artifacts
    lines = cleaned_result.split('\n')
    cleaned_lines = []
    found_first_header = False
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Look for the first markdown header to start the real documentation
        if not found_first_header:
            if stripped_line.startswith('#'):
                found_first_header = True
            else:
                continue  # Skip everything before the first header
        
        # Skip phase announcements and log artifacts anywhere in the document
        if (stripped_line.startswith("🔍 PHASE") or
            stripped_line.startswith("🏗️ PHASE") or
            stripped_line.startswith("📈 PHASE") or
            stripped_line.startswith("✨ QUALITY") or
            stripped_line.startswith("Based on") or
            stripped_line.startswith("Let me") or
            stripped_line.startswith("I'll") or
            "information we've gathered" in stripped_line.lower()):
            continue
            
        # Skip empty lines at the beginning only
        if not cleaned_lines and not stripped_line:
            continue
            
        cleaned_lines.append(line)
    
    final_result = '\n'.join(cleaned_lines).strip()
    
    logger.info("🪞 Magic Mirror: Analysis complete, documentation generated")
    return final_result


def create_focused_mirror(analysis_type: str = "getting_started") -> Agent:
    """Create a specialized Magic Mirror focused on a specific type of analysis.
    
    This function creates Magic Mirrors with specialized prompts for specific
    analysis phases, useful for targeted documentation generation or testing.
    
    Args:
        analysis_type: Type of analysis - 'getting_started', 'architecture', or 'evolution'
        
    Returns:
        Agent configured for the specific analysis type
    """
    if analysis_type not in PROMPT_TOOL_MAPPING:
        raise ValueError(f"Unknown analysis type: {analysis_type}. "
                        f"Available types: {list(PROMPT_TOOL_MAPPING.keys())}")
    
    config = PROMPT_TOOL_MAPPING[analysis_type]
    
    # Map tool names to actual tool functions
    tool_map = {
        'execution_time_status': execution_time_status,
        'quick_time_check': quick_time_check,
        'git_repo_stats': git_repo_stats,
        'git_files': git_files,
        'git_recent_files': git_recent_files,
        'git_log': git_log,
        'git_contributors': git_contributors,
        'git_branch_info': git_branch_info,
        'find_key_files': find_key_files,
        'file_read': file_read,
        'list_directory': list_directory,
        'peek_file': peek_file,
        'explore_project_structure': explore_project_structure
    }
    
    # Get the required tools for this analysis type
    required_tools = [tool_map[tool_name] for tool_name in config['tools'] if tool_name in tool_map]
    
    # Get agent configuration from config file
    agent_config = get_agent_config()
    
    # Create specialized mirror
    mirror = Agent(
        system_prompt=config['prompt'],
        **agent_config,
        tools=required_tools
    )
    
    return mirror


def progressive_analysis(repo_path: str) -> dict:
    """Perform progressive analysis using specialized Magic Mirrors for each phase.
    
    This function demonstrates the multi-phase approach using different Magic Mirrors
    for each analysis phase, with time-based decisions between phases.
    
    Args:
        repo_path: Path to the repository to analyze
        
    Returns:
        Dictionary containing results from each completed analysis phase
    """
    logger.info(f"🪞 Magic Mirror: Starting progressive analysis of {repo_path}")
    results = {}
    
    # Phase 1: Getting Started (Always do this)
    logger.info("🪞 Magic Mirror: Phase 1 - Analyzing Getting Started...")
    getting_started_mirror = create_focused_mirror('getting_started')
    results['getting_started'] = getting_started_mirror(
        f"Generate Getting Started documentation for repository: {repo_path}"
    )
    logger.info("🪞 Magic Mirror: Phase 1 complete - Getting Started analysis finished")
    
    # Check if we should continue
    time_check = quick_time_check()
    if "STOP" in str(time_check):
        logger.warning("🪞 Magic Mirror: Stopping after Getting Started due to time constraints")
        results['time_status'] = "Stopped after Getting Started due to time constraints"
        return results
    
    # Phase 2: Architecture
    logger.info("🪞 Magic Mirror: Phase 2 - Analyzing Architecture...")
    architecture_mirror = create_focused_mirror('architecture')
    results['architecture'] = architecture_mirror(
        f"Generate Architecture documentation for repository: {repo_path}"
    )
    logger.info("🪞 Magic Mirror: Phase 2 complete - Architecture analysis finished")
    
    # Check time again
    time_check = quick_time_check()
    if "STOP" in str(time_check):
        logger.warning("🪞 Magic Mirror: Stopping after Architecture due to time constraints")
        results['time_status'] = "Stopped after Architecture due to time constraints"
        return results
    
    # Phase 3: Evolution
    logger.info("🪞 Magic Mirror: Phase 3 - Analyzing Project Evolution...")
    evolution_mirror = create_focused_mirror('evolution')
    results['evolution'] = evolution_mirror(
        f"Generate Project Evolution documentation for repository: {repo_path}"
    )
    logger.info("🪞 Magic Mirror: Phase 3 complete - Project Evolution analysis finished")
    
    logger.info("🪞 Magic Mirror: Progressive analysis completed successfully - all phases finished")
    results['time_status'] = "Completed all phases successfully"
    return results


# Lambda handler for AWS deployment
def lambda_handler(event, context):
    """AWS Lambda handler for Magic Mirror documentation generation.
    
    Expected event format:
    {
        "repo_path": "/path/to/repository",
        "analysis_type": "complete"  # or "getting_started", "architecture", "evolution"
    }
    
    Returns:
        API Gateway compatible response with generated documentation
    """
    try:
        # Extract parameters from event
        repo_path = event.get('repo_path', '.')
        analysis_type = event.get('analysis_type', 'complete')
        
        logger.info(f"🪞 Lambda Handler: Starting Magic Mirror analysis")
        logger.info(f"📁 Repository: {repo_path}")
        logger.info(f"🔍 Analysis Type: {analysis_type}")
        
        # Record start time for logging
        start_time = current_time()
        logger.info(f"⏰ Start Time: {start_time}")
        
        # Perform analysis based on type
        if analysis_type == 'complete':
            logger.info("🔄 Performing complete analysis...")
            documentation = analyze_repository(repo_path)
        elif analysis_type == 'progressive':
            logger.info("🔄 Performing progressive analysis...")
            results = progressive_analysis(repo_path)
            documentation = str(results)
        else:
            logger.info(f"🔄 Performing focused {analysis_type} analysis...")
            # Focused analysis
            mirror = create_focused_mirror(analysis_type)
            documentation = str(mirror(f"Analyze {analysis_type} for repository: {repo_path}"))
        
        # Log final status
        final_time_status = str(execution_time_status())
        logger.info(f"⏰ Final Time Status: {final_time_status}")
        logger.info("✅ Magic Mirror analysis completed successfully")
        
        # Return successful response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'success': True,
                'documentation': documentation,
                'analysis_type': analysis_type,
                'repo_path': repo_path,
                'execution_info': {
                    'start_time': start_time,
                    'final_time_status': final_time_status
                }
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Magic Mirror analysis failed: {str(e)}", exc_info=True)
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': {
                'success': False,
                'error': str(e),
                'analysis_type': event.get('analysis_type', 'unknown'),
                'repo_path': event.get('repo_path', 'unknown')
            }
        }
        
    finally:
        # Always reset timer for next Lambda invocation
        logger.info("🔄 Resetting execution timer for next invocation...")
        reset_execution_timer()
        logger.info("🏁 Lambda execution complete")


# Example usage and testing
if __name__ == "__main__":
    import sys
    import argparse
    from pathlib import Path
    
    parser = argparse.ArgumentParser(description="Magic Mirror - Intelligent Code Documentation Generator")
    parser.add_argument("repo_path", help="Path to the repository to analyze")
    parser.add_argument("--output", "-o", help="Output directory to save documentation (default: print to console)")
    
    # Exit with help if no arguments provided
    if len(sys.argv) == 1:
        parser.print_help()
        print("\nEnvironment variables:")
        print("  LOG_LEVEL=DEBUG|INFO|WARNING|ERROR  (default: INFO)")
        sys.exit(1)  # Exit with error code
    
    args = parser.parse_args()
    
    logger.info(f"🪞 CLI: Starting Magic Mirror analysis of {args.repo_path}")
    
    try:
        # Generate documentation (quiet mode when saving to file)
        quiet_mode = args.output is not None
        docs = analyze_repository(args.repo_path, quiet=quiet_mode)
    except ValueError as e:
        # Path validation failed
        logger.error(f"❌ {str(e)}")
        sys.exit(1)
    
    # Handle output
    if args.output:
        # Create output directory if it doesn't exist
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename based on repository name
        repo_name = Path(args.repo_path).name
        if repo_name == "." or repo_name == "":
            repo_name = Path.cwd().name
        
        output_file = output_dir / f"{repo_name}{OUTPUT_FILE_SUFFIX}"
        
        # Save documentation
        with open(output_file, 'w', encoding=OUTPUT_FILE_ENCODING) as f:
            f.write(docs)
        
        logger.info(f"🪞 CLI: Documentation saved to {output_file}")
        print(f"📄 Documentation saved to: {output_file}")
        
    else:
        # Output to console
        print("\n" + CONSOLE_SEPARATOR)
        print(CONSOLE_HEADER)
        print(CONSOLE_SEPARATOR)
        print(docs)
        
        logger.info("🪞 CLI: Analysis complete, results displayed")