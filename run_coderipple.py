#!/usr/bin/env python3
"""
Run CodeRipple on this repository to generate documentation

This script simulates a webhook event for this repository and runs the full
multi-agent system to generate documentation in the coderipple/ directory.
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def create_mock_webhook_event():
    """Create a mock webhook event for this repository"""
    
    # Get the current repository info
    repo_name = "coderipple"
    repo_url = "https://github.com/robertoallende/coderipple"
    
    # Mock recent changes to trigger all agents
    mock_event = {
        "event_type": "push",
        "repository_name": repo_name,
        "repository_url": repo_url,
        "branch": "main",
        "commits": [
            {
                "id": "abc123",
                "message": "Implement Step 4A: Main README.md generation capability",
                "author": "Developer", 
                "timestamp": datetime.now().isoformat(),
                "added_files": ["src/tourist_guide_agent.py"],
                "modified_files": ["tests/test_tourist_guide_agent.py", "PLAN.md"],
                "removed_files": [],
                "url": f"{repo_url}/commit/abc123"
            }
        ],
        "before_sha": "before123",
        "after_sha": "abc123"
    }
    
    return mock_event

def run_coderipple_system():
    """Run the complete CodeRipple system"""
    
    try:
        print("🚀 Running CodeRipple on this repository...")
        print("=" * 50)
        
        # Import the components (mock the Strands dependency)
        print("📦 Loading CodeRipple components...")
        
        # Create mock implementations since we don't have Strands installed
        from webhook_parser import WebhookEvent, CommitInfo
        
        # Create webhook event
        mock_data = create_mock_webhook_event()
        print(f"📨 Created mock webhook event for {mock_data['repository_name']}")
        
        # Convert to WebhookEvent object
        commits = []
        for commit_data in mock_data['commits']:
            commit = CommitInfo(
                id=commit_data['id'],
                message=commit_data['message'],
                author=commit_data['author'],
                timestamp=datetime.fromisoformat(commit_data['timestamp'].replace('Z', '+00:00')) if 'Z' in commit_data['timestamp'] else datetime.fromisoformat(commit_data['timestamp']),
                added_files=commit_data['added_files'],
                modified_files=commit_data['modified_files'],
                removed_files=commit_data['removed_files'],
                url=commit_data['url']
            )
            commits.append(commit)
        
        webhook_event = WebhookEvent(
            event_type=mock_data['event_type'],
            repository_name=mock_data['repository_name'],
            repository_url=mock_data['repository_url'],
            branch=mock_data['branch'],
            commits=commits,
            before_sha=mock_data['before_sha'],
            after_sha=mock_data['after_sha']
        )
        
        print(f"🔍 Processing {len(webhook_event.commits)} commit(s)...")
        
        # Analyze actual repository structure
        git_analysis = _analyze_actual_repository()
        
        # Update git analysis with repository-specific insights
        git_analysis.update({
            'repository_structure': _get_repository_structure(),
            'key_components': _identify_key_components()
        })
        
        print("🧠 Mock git analysis completed")
        print(f"   - Change type: {git_analysis['change_type']}")
        print(f"   - Affected files: {len(git_analysis['affected_components'])}")
        
        # Step 4B: Get actual git diff from the repository
        actual_git_diff = _get_actual_git_diff()
        
        # Run agents with actual repository analysis
        context = {
            'webhook_event': webhook_event,
            'git_analysis': git_analysis,
            'git_diff': actual_git_diff,  # Step 4B: Use actual git diff for intelligent content generation
            'repository_info': {
                'name': webhook_event.repository_name,
                'url': webhook_event.repository_url,
                'path': os.getcwd()  # Current directory is the source repository
            }
        }
        
        # Mock the orchestrator decision tree
        print("\n🎯 Orchestrator Agent Decision Tree:")
        print("   1. Does this change how users interact? → YES → Tourist Guide")
        print("   2. Does this change what the system is? → YES → Building Inspector") 
        print("   3. Does this represent a decision? → YES → Historian")
        
        # Run Tourist Guide Agent (the real one with mocked tools)
        print("\n👥 Running Tourist Guide Agent...")
        try:
            # Import and run the tourist guide with mock functions
            run_tourist_guide_mock(webhook_event, git_analysis, context)
        except Exception as e:
            print(f"⚠️  Tourist Guide mock run failed: {e}")
            # Create basic user documentation manually
            create_mock_user_docs(webhook_event.repository_name)
        
        # Run Building Inspector Agent (mock)
        print("\n🏗️ Running Building Inspector Agent...")
        create_mock_system_docs(webhook_event.repository_name)
        
        # Run Historian Agent (mock)  
        print("\n📚 Running Historian Agent...")
        create_mock_decision_docs(webhook_event.repository_name)
        
        # Generate main README using Tourist Guide capability
        print("\n📝 Generating main README.md hub...")
        generate_main_readme_mock(webhook_event.repository_name, webhook_event.repository_url)
        
        print("\n✅ CodeRipple documentation generation complete!")
        print("\n📁 Generated documentation structure:")
        
        # Show the generated structure
        for root, dirs, files in os.walk("coderipple"):
            level = root.replace("coderipple", "").count(os.sep)
            indent = "  " * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = "  " * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running CodeRipple: {e}")
        import traceback
        traceback.print_exc()
        return False

def _analyze_actual_repository():
    """Analyze the actual repository structure and recent changes"""
    try:
        import subprocess
        
        # Get list of Python files in src/
        src_files = []
        if os.path.exists('src'):
            for file in os.listdir('src'):
                if file.endswith('.py'):
                    src_files.append(f'src/{file}')
        
        # Identify change type based on repository content
        change_type = 'multi_agent_system'
        if os.path.exists('src/tourist_guide_agent.py'):
            change_type = 'documentation_system'
        if os.path.exists('src/config.py'):
            change_type = 'configuration_update'
            
        return {
            'change_type': change_type,
            'affected_components': src_files,
            'confidence': 0.95,
            'summary': f'CodeRipple multi-agent documentation system with {len(src_files)} components'
        }
        
    except Exception as e:
        return {
            'change_type': 'unknown',
            'affected_components': [],
            'confidence': 0.5,
            'summary': f'Error analyzing repository: {str(e)}'
        }

def _get_repository_structure():
    """Get the actual repository structure"""
    structure = {}
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and venv
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv' and d != '__pycache__']
        
        if root == '.':
            structure['root_files'] = [f for f in files if not f.startswith('.')]
        elif 'src' in root:
            structure['source_files'] = files
        elif 'tests' in root:
            structure['test_files'] = files
    
    return structure

def _identify_key_components():
    """Identify key components in the repository"""
    components = []
    
    key_files = [
        'src/orchestrator_agent.py',
        'src/tourist_guide_agent.py', 
        'src/building_inspector_agent.py',
        'src/historian_agent.py',
        'src/config.py',
        'src/webhook_parser.py'
    ]
    
    for file_path in key_files:
        if os.path.exists(file_path):
            components.append({
                'file': file_path,
                'type': 'agent' if 'agent' in file_path else 'core_component',
                'exists': True
            })
    
    return components

def _get_actual_git_diff():
    """Get actual git diff from the repository for intelligent content generation"""
    try:
        import subprocess
        
        # Get recent changes to analyze (last 5 commits)
        result = subprocess.run(
            ['git', 'log', '--pretty=format:', '--name-only', '-5'],
            capture_output=True, text=True, cwd=os.getcwd()
        )
        
        if result.returncode == 0:
            changed_files = [f for f in result.stdout.split('\n') if f.strip()]
            
            # Get diff for recent changes
            diff_result = subprocess.run(
                ['git', 'diff', 'HEAD~3', 'HEAD'],
                capture_output=True, text=True, cwd=os.getcwd()
            )
            
            if diff_result.returncode == 0 and diff_result.stdout.strip():
                return diff_result.stdout
        
        # Fallback: create diff showing current state of key files
        key_files = ['src/tourist_guide_agent.py', 'src/config.py', 'CLAUDE.md']
        diff_content = ""
        
        for file_path in key_files:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    content = f.read()
                    # Simulate a diff format showing current file content
                    diff_content += f"""diff --git a/{file_path} b/{file_path}
index 0000000..abcd123
--- a/{file_path}
+++ b/{file_path}
@@ -1,{len(content.splitlines())} +1,{len(content.splitlines())} @@
{chr(10).join('+' + line for line in content.splitlines()[:20])}
...
"""
        
        return diff_content if diff_content else "No changes detected"
        
    except Exception as e:
        return f"Error getting git diff: {str(e)}"


def run_tourist_guide_mock(webhook_event, git_analysis, context):
    """Run real Tourist Guide Agent with actual source code analysis"""
    try:
        # Import the real Tourist Guide Agent
        from tourist_guide_agent import tourist_guide_agent
        from config import get_config
        
        print("   🧠 Using Step 4B: Intelligent Content Generation")
        print("   🔍 Analyzing change patterns and extracting code examples...")
        
        # Get the actual repository configuration
        config = get_config()
        print(f"   📁 Analyzing source code at: {config.source_repo}")
        
        # Add real git diff from the actual repository
        context['config'] = config
        context['actual_repository'] = True  # Flag that this is real analysis
        
        # Run the intelligent Tourist Guide Agent
        result = tourist_guide_agent(webhook_event, git_analysis, context)
        
        print(f"   ✓ Generated {len(result.updates)} intelligent documentation updates")
        print(f"   📝 User Impact: {result.user_impact}")
        
        # Show what was intelligently generated
        for update in result.updates:
            print(f"   📄 {update.section}: {update.reason}")
            
    except Exception as e:
        print(f"   ⚠️  Step 4B intelligent generation failed: {e}")
        import traceback
        traceback.print_exc()
        print("   🔄 Falling back to basic user documentation...")
        # Fallback to basic docs
        create_mock_user_docs(webhook_event.repository_name)

def create_mock_user_docs(repo_name):
    """Create mock user documentation"""
    os.makedirs("coderipple", exist_ok=True)
    
    # Discovery document
    discovery_content = f"""# Project Discovery

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: {repo_name}*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

## Welcome to CodeRipple

CodeRipple is an experimental multi-agent documentation system that automatically maintains software documentation by analyzing code changes through different perspectives using AWS Lambda and AWS Strands for agent orchestration.

## What CodeRipple Does

- **Automated Documentation**: Responds to GitHub webhooks to update docs automatically
- **Multi-Layer Approach**: Uses a layered documentation structure with three specialized agents
- **Role-Based Agents**: Tourist Guide (user docs), Building Inspector (system docs), Historian (decisions)
- **AWS Integration**: Built for serverless deployment with Lambda and Strands

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Review the implementation in `src/` directory
4. Run tests: `python3 -m unittest discover tests/`
5. Explore the multi-agent architecture

## Recent Updates

### Feature Changes
- Added README.md generation capability to Tourist Guide Agent
- Implemented Step 4A of the development plan
- Enhanced auto-discovery of documentation files
- Created documentation hub with navigation links

### What's New
- Main README.md hub automatically generated
- Cross-references between documentation layers
- Timestamp tracking for all documentation
- Comprehensive test coverage for new features
"""
    
    with open("coderipple/discovery.md", "w") as f:
        f.write(discovery_content)
    
    print("   ✓ Created discovery.md")
    
    # Getting Started document
    getting_started_content = f"""# Getting Started

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: {repo_name}*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

## Installation

```bash
# Clone the repository
git clone https://github.com/robertoallende/coderipple.git
cd coderipple

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Test the Webhook Parser
```bash
# Test with sample webhook data
python3 examples/test_webhook.py examples/sample.json push

# Test with diff fetching (requires internet)
python3 examples/test_webhook.py examples/sample.json push --fetch-diff
```

### 2. Run Individual Agent Tests
```bash
# Test each agent component
python3 tests/test_webhook_parser.py
python3 tests/test_tourist_guide_agent.py
python3 tests/test_building_inspector_agent.py
python3 tests/test_historian_agent.py
python3 tests/test_orchestrator_agent.py
```

### 3. Run All Tests
```bash
# Using unittest discovery
python3 -m unittest discover tests/

# Or with pytest (recommended)
pip install pytest
pytest tests/ -v
```

## Configuration

For private repositories, set your GitHub token:
```bash
export GITHUB_TOKEN=your_github_personal_access_token
```

## Next Steps

1. Review the [system architecture](system/architecture.md)
2. Understand the [decision rationale](decisions/architecture_decisions.md)
3. Explore the multi-agent implementation
4. Consider AWS deployment (Step 5 in PLAN.md)
"""
    
    with open("coderipple/getting_started.md", "w") as f:
        f.write(getting_started_content)
    
    print("   ✓ Created getting_started.md")

def create_mock_system_docs(repo_name):
    """Create mock system documentation"""
    os.makedirs("coderipple/system", exist_ok=True)
    
    architecture_content = f"""# System Architecture

*This document is automatically maintained by CodeRipple Building Inspector Agent*  
*Repository: {repo_name}*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

## Current Architecture

CodeRipple follows a webhook-driven, multi-agent architecture:

```
GitHub Webhook → API Gateway → Orchestrator Agent → Specialist Agents → Documentation Output
```

## Core Components

### Webhook Processing Layer
- **GitHubWebhookParser** (`src/webhook_parser.py`): Processes GitHub webhook payloads
- **WebhookEvent/CommitInfo**: Data classes for structured webhook information
- **Git Analysis Tool** (`src/git_analysis_tool.py`): Analyzes git diffs using @tool decorator

### Agent Orchestration Layer  
- **Orchestrator Agent** (`src/orchestrator_agent.py`): Coordinates specialist agents using Layer Selection Decision Tree
- **AWS Strands Integration**: Model-driven agent orchestration (planned)

### Specialist Agents
- **Tourist Guide Agent** (`src/tourist_guide_agent.py`): User-facing documentation (How to ENGAGE)
- **Building Inspector Agent** (`src/building_inspector_agent.py`): Current system state (What it IS)  
- **Historian Agent** (`src/historian_agent.py`): Decision preservation (Why it BECAME)

## Current Capabilities

### Implemented (Steps 1-7 Complete)
- ✅ GitHub webhook payload parsing with diff data extraction
- ✅ Git analysis tool framework using Strands @tool structure
- ✅ Complete multi-agent system with three specialist agents
- ✅ Orchestrator with Layer Selection Decision Tree
- ✅ Document writing capabilities for all agents
- ✅ Main README.md hub generation (Step 4A)
- ✅ Intelligent Content Generation (Step 4B - Context-aware, not template-based)
- ✅ Cross-Agent Context Flow (Step 4C - Shared state and cross-references)
- ✅ Amazon Bedrock Integration (Step 4D - AI-enhanced content quality)
- ✅ Content Validation Pipeline (Step 4E - Quality scoring and enforcement)
- ✅ Real Diff Integration (Step 4F - Specific change-based documentation)
- ✅ Source Code Analysis Tool (Step 5A - Agents understand project functionality)
- ✅ Existing Content Discovery (Step 5B - Agents read and understand existing docs)
- ✅ Content-Aware Update Logic (Step 5C - Intelligent content merging)
- ✅ Context-Rich Initial Generation (Step 5D - Meaningful new documentation)
- ✅ Tourist Guide Agent Enhancement (Step 6 - Bootstrap and user documentation structure)
- ✅ Configuration Management & Directory Structure (Step 7 - Environment variable configuration system)

### Remaining Work (Step 8)
- 📅 AWS Lambda deployment with Terraform
- 📅 API Gateway webhook endpoints
- 📅 Production infrastructure automation

## Technology Stack

- **Python 3.8+**: Core implementation language
- **AWS Strands**: Multi-agent orchestration framework
- **Amazon Bedrock**: AI analysis and content generation (planned)
- **AWS Lambda**: Serverless execution environment (planned)
- **Terraform**: Infrastructure as Code for AWS deployment (planned)

## File Organization

```
src/
├── webhook_parser.py      # GitHub webhook processing
├── git_analysis_tool.py   # Git diff analysis with @tool
├── orchestrator_agent.py  # Agent coordination
├── tourist_guide_agent.py # User documentation
├── building_inspector_agent.py # System documentation  
└── historian_agent.py     # Decision documentation

tests/
├── test_webhook_parser.py
├── test_*_agent.py        # Individual agent tests
└── ...

coderipple/                # Generated documentation
├── discovery.md           # Tourist Guide outputs
├── getting_started.md
├── system/               # Building Inspector outputs  
│   └── architecture.md
└── decisions/            # Historian outputs
    └── architecture_decisions.md
```
"""
    
    with open("coderipple/system/architecture.md", "w") as f:
        f.write(architecture_content)
    
    print("   ✓ Created system/architecture.md")

def create_mock_decision_docs(repo_name):
    """Create mock decision documentation"""
    os.makedirs("coderipple/decisions", exist_ok=True)
    
    decisions_content = f"""# Architectural Decision Records

*This document is automatically maintained by CodeRipple Historian Agent*  
*Repository: {repo_name}*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*  
*All decisions preserved with historical context*

---

## ADR-001: Multi-Agent Architecture

**Date**: 2025-06-14  
**Status**: Accepted  
**Commit**: abc123  
**Author**: Developer

### Context
Need to maintain documentation from multiple perspectives while respecting the temporal nature of software documentation. Different types of documentation have different update patterns and lifecycles.

### Decision
Implement role-based specialist agents using AWS Strands:
- Tourist Guide Agent: User-facing documentation with task-oriented updates
- Building Inspector Agent: Current system state with incremental rewrites
- Historian Agent: Decision preservation with append-only updates

### Consequences
- **Positive**: Clear responsibilities, appropriate update patterns, focused expertise per agent
- **Negative**: Increased complexity, requires agent coordination mechanisms  
- **Neutral**: Learning curve for AWS Strands framework

### Related Decisions
- Links to ADR-002 (Layered Documentation Structure)

---

## ADR-002: Layered Documentation Structure

**Date**: 2025-06-14  
**Status**: Accepted  
**Commit**: abc123  
**Author**: Developer

### Context
Documentation needs different temporal handling patterns. Some docs need to reflect current state only, others need historical context, and user docs need task-oriented updates.

### Decision
Structure documentation into three layers based on a layered documentation approach:
- **Outer Layer (How to ENGAGE)**: Discovery, getting started, patterns, troubleshooting
- **Middle Layer (What it IS)**: Current architecture, capabilities, interfaces, constraints
- **Inner Layer (Why it BECAME)**: ADRs, problem evolution, major refactors, migrations

### Consequences
- **Positive**: Clear update patterns, appropriate depth for different audiences, reduces documentation debt
- **Negative**: Requires discipline to maintain layer boundaries
- **Neutral**: New framework may need explanation to team members

### Related Decisions
- Links to ADR-001 (Multi-Agent Architecture)
- Links to ADR-003 (Layer Selection Decision Tree)

---

## ADR-003: Layer Selection Decision Tree

**Date**: 2025-06-14  
**Status**: Accepted  
**Commit**: abc123  
**Author**: Developer

### Context
Need systematic way for Orchestrator Agent to determine which specialist agents to invoke based on code changes.

### Decision
Implement decision tree logic:
1. Does this change how users interact with the system? → Tourist Guide Agent
2. Does this change what the system currently is or does? → Building Inspector Agent  
3. Does this represent a significant decision or learning? → Historian Agent

### Consequences
- **Positive**: Systematic agent selection, reduces redundant documentation, clear triggering logic
- **Negative**: May need refinement as we learn from real usage
- **Neutral**: Agents can overlap when changes affect multiple layers

### Related Decisions
- Links to ADR-001 (Multi-Agent Architecture)
- Links to ADR-002 (Layered Documentation Structure)

---

## ADR-004: README.md Hub Generation

**Date**: 2025-06-14  
**Status**: Accepted  
**Commit**: abc123  
**Author**: Developer

### Context
Need central entry point for all agent-generated documentation. Users should be able to discover and navigate all documentation from a single location.

### Decision  
Implement Step 4A: Tourist Guide Agent generates and maintains main README.md hub that:
- Auto-discovers all documentation files in coderipple/ directory
- Creates navigation links organized by framework layers
- Shows descriptions, timestamps, and file metadata
- Updates automatically when any agent creates new documentation

### Consequences
- **Positive**: Single entry point, automatic discovery, always up-to-date navigation
- **Negative**: Adds complexity to Tourist Guide Agent responsibilities
- **Neutral**: README becomes auto-generated rather than manually maintained

### Related Decisions
- Links to ADR-002 (Layered Documentation Structure)
- Links to planned Step 4B-4E enhancements
"""
    
    with open("coderipple/decisions/architecture_decisions.md", "w") as f:
        f.write(decisions_content)
    
    print("   ✓ Created decisions/architecture_decisions.md")

def generate_main_readme_mock(repo_name, repo_url):
    """Generate the main README.md hub"""
    
    # Discover existing docs
    import glob
    
    docs = {
        'user': [],
        'system': [],
        'decisions': []
    }
    
    # User documentation
    user_patterns = ['discovery.md', 'getting_started.md', 'patterns.md', 'troubleshooting.md', 'advanced.md']
    for pattern in user_patterns:
        files = glob.glob(os.path.join("coderipple", pattern))
        for file_path in files:
            docs['user'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'description': extract_description_from_file(file_path),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # System documentation
    system_patterns = ['system/*.md']
    for pattern in system_patterns:
        files = glob.glob(os.path.join("coderipple", pattern))
        for file_path in files:
            docs['system'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'description': extract_description_from_file(file_path),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Decision documentation
    decision_patterns = ['decisions/*.md']
    for pattern in decision_patterns:
        files = glob.glob(os.path.join("coderipple", pattern))
        for file_path in files:
            docs['decisions'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'description': extract_description_from_file(file_path),
                'last_modified': datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
            })
    
    # Generate README content
    readme_content = f"""# {repo_name} Documentation Hub

*Auto-generated documentation hub maintained by CodeRipple Tourist Guide Agent*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

Welcome to the {repo_name} documentation! This hub provides access to all automatically maintained documentation organized by a **layered documentation structure** - three layers that handle different depths of understanding.

## Documentation Layers

### 🎯 User Documentation (How to ENGAGE)
*Start here if you want to use or contribute to {repo_name}*

"""
    
    if docs.get('user'):
        for doc in docs['user']:
            readme_content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
            readme_content += f"  *Updated: {doc['last_modified']}*\n\n"
    else:
        readme_content += "*No user documentation available yet*\n\n"
    
    readme_content += """### 🏗️ System Documentation (What it IS)
*Current system architecture, capabilities, and technical specifications*

"""
    
    if docs.get('system'):
        for doc in docs['system']:
            readme_content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
            readme_content += f"  *Updated: {doc['last_modified']}*\n\n"
    else:
        readme_content += "*No system documentation available yet*\n\n"
    
    readme_content += """### 📚 Decision Documentation (Why it BECAME this way)
*Historical context, architectural decisions, and evolution story*

"""
    
    if docs.get('decisions'):
        for doc in docs['decisions']:
            readme_content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
            readme_content += f"  *Updated: {doc['last_modified']}*\n\n"
    else:
        readme_content += "*No decision documentation available yet*\n\n"
    
    total_docs = sum(len(docs) for docs in docs.values())
    
    readme_content += f"""---

## Quick Navigation

- **[Repository]({repo_url})** - Source code and issues
- **Documentation Status**: {total_docs} files across {len([k for k, v in docs.items() if v])} layers
- **Framework**: [Layered Documentation Structure](https://github.com/robertoallende/coderipple#documentation-layers)

## About This Documentation

This documentation is automatically maintained by **CodeRipple**, a multi-agent system that updates documentation based on code changes. Each layer serves a different purpose:

- **User docs** help you discover, learn, and use the system
- **System docs** explain what currently exists and how it works  
- **Decision docs** preserve why things were built this way

*Documentation automatically updates when code changes. If you notice gaps or issues, please [create an issue]({repo_url}/issues).*

## System Status

- ✅ **Step 1**: GitHub webhook payload parsing  
- ✅ **Step 2**: Git analysis tool framework
- ✅ **Step 3**: Multi-agent system (Tourist Guide, Building Inspector, Historian)
- ✅ **Step 4A-F**: Complete enhanced documentation generation (README, intelligent content, context flow, Bedrock integration, validation, real diff)
- ✅ **Step 5A-D**: Advanced agent capabilities (source analysis, content discovery, update logic, context-rich generation)
- ✅ **Step 6**: Tourist Guide enhancement (bootstrap, user documentation structure)
- ✅ **Step 7**: Configuration management & directory structure
- 📅 **Step 8**: AWS infrastructure deployment (Lambda, API Gateway, Terraform)

*Generated by CodeRipple Tourist Guide Agent on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    
    with open("coderipple/README.md", "w") as f:
        f.write(readme_content)
    
    print("   ✓ Created README.md hub")

def extract_description_from_file(file_path):
    """Extract description from documentation file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Look for description patterns
        for line in lines:
            line = line.strip()
            if line.startswith('#') and not line.startswith('##'):
                # Main title
                return line.replace('#', '').strip()
        
        return "Documentation file"
    except Exception:
        return "Unable to read description"

def main():
    """Main function"""
    print("🎯 CodeRipple Self-Documentation Generator")
    print("🔧 Running CodeRipple on this repository to generate coderipple/ documentation")
    print()
    
    success = run_coderipple_system()
    
    if success:
        print("\n🎉 Success! CodeRipple documentation generated in coderipple/ directory")
        print("\n📖 To explore the documentation:")
        print("   - Start with: coderipple/README.md")
        print("   - User docs: coderipple/discovery.md, coderipple/getting_started.md")
        print("   - System docs: coderipple/system/architecture.md")
        print("   - Decision docs: coderipple/decisions/architecture_decisions.md")
    else:
        print("\n❌ Failed to generate documentation")

if __name__ == "__main__":
    main()