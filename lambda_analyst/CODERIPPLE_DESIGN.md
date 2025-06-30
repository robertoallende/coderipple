# CodeRipple Magic Mirror

## Overview

CodeRipple is an AI-powered code documentation system built on the Strands Agents framework. It automatically analyzes git repositories and generates comprehensive documentation using intelligent time management and progressive quality improvement.

## Core Design Principles

### 1. **Single Agent Architecture**
- One intelligent agent with specialized tools rather than multiple coordinated agents
- Simpler error handling, debugging, and deployment
- Self-managing workflow with built-in decision making

### 2. **Time-Aware Analysis**
- AWS Lambda 15-minute execution limit requires intelligent time management
- Progressive analysis with quality checkpoints
- Adaptive workflow based on time remaining vs. quality achieved

### 3. **Progressive Quality Improvement**
- Fast initial analysis followed by iterative improvements
- Quality assessment and gap identification
- Time-based decisions on whether to continue or finalize

## System Architecture

### Tool Categories

#### **Git Analysis Tools** (`git_tools.py`)
- `git_log()` - Commit history and development patterns
- `git_files()` - Repository structure and file organization
- `git_contributors()` - Team structure and activity levels
- `git_recent_files()` - Most actively developed components
- `git_branch_info()` - Development workflow and branching strategy
- `git_repo_stats()` - High-level repository statistics
- `find_key_files()` - Configuration and documentation files

#### **Time Management Tools** (`generic_tools.py`)
- `execution_time_status()` - Comprehensive time analysis with recommendations
- `quick_time_check()` - Fast decision making for continue/stop decisions
- `current_time()` - Timestamp logging and tracking
- `reset_execution_timer()` - Clean state for next Lambda invocation

#### **File Analysis Tools** (from Strands)
- `file_read` - Read and analyze source files and configuration

## Workflow Strategy

### Phase 1: Quick Analysis (2-3 minutes)
```
1. Check execution_time_status() - Establish time baseline
2. Run git_repo_stats() - Get project overview
3. Run find_key_files() - Identify critical files
4. Read README, package.json, or equivalent setup files
5. Run git_contributors() and git_branch_info() - Understand team/workflow
6. Generate initial draft documentation
```

### Phase 2: Quality Assessment
```
1. Agent evaluates its own documentation:
   - "Is the project purpose clear?"
   - "Are setup instructions complete?"
   - "Is the architecture explained?"
   - "Are there usage examples?"

2. Identify improvement opportunities:
   - Missing source file analysis
   - Incomplete architecture understanding
   - Lack of usage examples
   - Unclear setup instructions
```

### Phase 3: Adaptive Improvement
```
Based on execution_time_status() recommendations:

GOOD/CAUTION (>8 minutes remaining):
- Read main source files identified by git_recent_files()
- Analyze architecture patterns and design decisions
- Add detailed usage examples
- Enhance setup and configuration instructions

WARNING (4-8 minutes remaining):
- Focus on most critical gaps only
- Read 1-2 key source files
- Add essential missing information

URGENT/CRITICAL (<4 minutes remaining):
- Polish existing documentation
- Ensure all sections are coherent
- Prepare final output
```

## System Prompt Strategy

### Core Instructions
```
You are a code documentation expert with git repository access and time management capabilities.

WORKFLOW:
1. Always start by checking execution_time_status()
2. Perform quick repository analysis using git tools
3. Generate initial documentation draft
4. Assess quality and identify gaps
5. Use remaining time for iterative improvements
6. Monitor time and adapt strategy accordingly

DELIVERABLES:
- Project Overview (what it does, purpose)
- Setup Instructions (installation, configuration, dependencies)
- Architecture Description (structure, key components, patterns)
- Usage Examples (how to run, common operations)
- Key Files Reference (important files and their purposes)

QUALITY STANDARDS:
- Prioritize completeness over perfection
- Always deliver functional documentation within time limits
- Use git analysis to understand project context and history
- Focus on actionable information for developers
```

### Time Management Integration
```
TIME DECISION MATRIX:
- GOOD: Thorough analysis with detailed improvements
- CAUTION: Continue with focused analysis
- WARNING: Essential improvements only
- URGENT: Finalize current work
- CRITICAL: Stop immediately and deliver

PROGRESSIVE IMPROVEMENT:
After initial draft, iteratively enhance based on:
1. Time remaining
2. Documentation completeness
3. Identified knowledge gaps
4. File importance (from git analysis)
```

## Implementation Structure

### Main Agent File (`analyzer.py`)
```python
from strands import Agent
from strands_tools import file_read
from .git_tools import git_log, git_files, git_contributors, git_repo_stats, find_key_files
from .generic_tools import execution_time_status, quick_time_check

DOCUMENTATION_AGENT_PROMPT = """
[Comprehensive system prompt with workflow instructions]
"""

def create_documentation_agent():
    return Agent(
        system_prompt=DOCUMENTATION_AGENT_PROMPT,
        tools=[
            # Time management
            execution_time_status, quick_time_check,
            # Git analysis
            git_log, git_files, git_contributors, git_repo_stats, find_key_files,
            # File reading
            file_read
        ]
    )

def analyze_repository(repo_path: str) -> str:
    agent = create_documentation_agent()
    return agent(f"Generate comprehensive documentation for repository: {repo_path}")
```

### Lambda Handler
```python
from .analyzer import analyze_repository
from .generic_tools import reset_execution_timer

def lambda_handler(event, context):
    try:
        repo_path = event.get('repo_path', '.')
        documentation = analyze_repository(repo_path)
        
        return {
            'statusCode': 200,
            'body': documentation
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error generating documentation: {str(e)}'
        }
    finally:
        # Reset timer for next Lambda invocation
        reset_execution_timer()
```

## Quality Assurance Strategy

### Self-Assessment Criteria
The agent evaluates its own work against these standards:

1. **Completeness Checklist**
   - [ ] Project purpose clearly explained
   - [ ] Setup instructions provided
   - [ ] Architecture overview included
   - [ ] Usage examples present
   - [ ] Key files identified and explained

2. **Quality Indicators**
   - Specific rather than generic descriptions
   - Actionable setup instructions
   - Clear architecture explanations
   - Relevant usage examples
   - Recent development context included

3. **Improvement Priorities** (when time permits)
   - Read main source files for deeper architecture understanding
   - Add specific configuration examples
   - Include API documentation if applicable
   - Enhance troubleshooting information
   - Add development workflow details

## Deployment Considerations

### AWS Lambda Optimization
- **Memory**: Start with 512MB, adjust based on repository size
- **Timeout**: 14 minutes (safety margin for 15-minute limit)
- **Architecture**: ARM64 for cost efficiency
- **Dependencies**: Package git tools and Strands framework in Lambda layer

### Error Handling
- Repository access validation
- Git command error recovery
- Time limit graceful degradation
- Partial documentation delivery on errors

### Input/Output Format
```json
// Input
{
  "repo_path": "/path/to/repository",
  "focus_areas": ["setup", "architecture", "usage"]  // Optional
}

// Output
{
  "statusCode": 200,
  "body": "# Project Documentation\n\n## Overview\n..."
}
```

## Success Metrics

### Primary Goals
- **Always deliver documentation** within time limits
- **Adaptive quality** based on available time
- **Actionable content** that helps developers understand and use the project
- **Intelligent prioritization** of analysis based on git insights

### Quality Benchmarks
- 90%+ of documentation includes project setup instructions
- 80%+ includes clear architecture overview
- 70%+ includes specific usage examples
- 60%+ includes recent development context from git analysis

This design ensures robust, time-aware documentation generation that adapts to constraints while maintaining quality standards.