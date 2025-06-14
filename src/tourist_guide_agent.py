"""
Tourist Guide Agent for CodeRipple

This agent focuses on the outer layer of documentation - "How to ENGAGE".
Shows visitors around the system, explains how to get started, points out features, 
and helps when users are lost. Updates based on user workflows and feedback.

Core Elements:
- Discovery: How users find and learn about the system
- Getting Started: Step-by-step onboarding
- Common Patterns: Typical usage workflows
- Advanced Usage: Power user features
- Troubleshooting: Common issues and solutions
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from strands import tool
from webhook_parser import WebhookEvent


@dataclass
class DocumentationUpdate:
    """Represents a documentation update decision"""
    section: str  # 'discovery', 'getting_started', 'patterns', 'advanced', 'troubleshooting'
    action: str   # 'create', 'update', 'append'
    content: str
    reason: str
    priority: int  # 1=high, 2=medium, 3=low


@dataclass
class TouristGuideResult:
    """Result of Tourist Guide analysis"""
    updates: List[DocumentationUpdate]
    summary: str
    user_impact: str  # Description of how this affects users


@tool
def analyze_user_workflow_impact(change_type: str, affected_files: List[str], commit_messages: List[str]) -> Dict[str, Any]:
    """
    Analyze how code changes impact user workflows and determine documentation updates needed.
    
    Args:
        change_type: Type of change (feature, bugfix, etc.)
        affected_files: List of files that were changed
        commit_messages: List of commit messages for context
        
    Returns:
        Dictionary with workflow impact analysis and documentation recommendations
    """
    
    # Analyze user-facing impact
    user_facing_changes = _identify_user_facing_changes(change_type, affected_files, commit_messages)
    workflow_impact = _assess_workflow_impact(change_type, user_facing_changes)
    doc_updates = _recommend_documentation_updates(change_type, user_facing_changes, workflow_impact)
    
    return {
        'user_facing_changes': user_facing_changes,
        'workflow_impact': workflow_impact,
        'documentation_updates': doc_updates,
        'priority_level': _calculate_priority(change_type, user_facing_changes)
    }


@tool
def write_documentation_file(file_path: str, content: str, action: str = "create") -> Dict[str, Any]:
    """
    Write or update documentation files in the coderipple directory.
    
    Args:
        file_path: Relative path within coderipple directory (e.g., "discovery.md")
        content: Content to write
        action: "create", "update", or "append"
        
    Returns:
        Dictionary with operation status and details
    """
    try:
        # Ensure coderipple directory exists
        coderipple_dir = "coderipple"
        if not os.path.exists(coderipple_dir):
            os.makedirs(coderipple_dir)
        
        full_path = os.path.join(coderipple_dir, file_path)
        
        # Ensure subdirectories exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        if action == "create":
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "created"
            
        elif action == "append":
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write("\n\n" + content)
            operation = "appended to"
            
        elif action == "update":
            # For update, we'll overwrite the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "updated"
        
        return {
            'status': 'success',
            'operation': operation,
            'file_path': full_path,
            'content_length': len(content)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file_path': file_path
        }


@tool
def generate_main_readme(repository_name: str, repository_url: str) -> Dict[str, Any]:
    """
    Generate main README.md that serves as documentation hub for all agent-generated docs.
    
    Args:
        repository_name: Repository name for context
        repository_url: Repository URL for links
        
    Returns:
        Dictionary with README content and metadata
    """
    try:
        # Discover all existing documentation
        existing_docs = _discover_all_documentation()
        
        # Generate comprehensive README content
        readme_content = _generate_hub_readme_content(repository_name, repository_url, existing_docs)
        
        return {
            'status': 'success',
            'content': readme_content,
            'docs_discovered': len(existing_docs),
            'sections': list(existing_docs.keys())
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'content': ''
        }


@tool
def update_readme_navigation(existing_readme: str, new_docs: List[str], repository_name: str) -> Dict[str, Any]:
    """
    Update README navigation when new documentation files are created.
    
    Args:
        existing_readme: Current README content
        new_docs: List of newly created documentation files
        repository_name: Repository name for context
        
    Returns:
        Dictionary with updated README content
    """
    try:
        # Re-discover all documentation to get latest state
        all_docs = _discover_all_documentation()
        
        # Check if we need to regenerate navigation section
        if _should_regenerate_navigation(existing_readme, all_docs):
            updated_content = _update_navigation_section(existing_readme, all_docs, repository_name)
        else:
            updated_content = existing_readme
        
        return {
            'status': 'success',
            'content': updated_content,
            'updated': len(new_docs),
            'total_docs': len([doc for section in all_docs.values() for doc in section])
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'content': existing_readme
        }


@tool  
def read_existing_documentation(file_path: str) -> Dict[str, Any]:
    """
    Read existing documentation file to check current content.
    
    Args:
        file_path: Relative path within coderipple directory
        
    Returns:
        Dictionary with file content or error
    """
    try:
        full_path = os.path.join("coderipple", file_path)
        
        if not os.path.exists(full_path):
            return {
                'status': 'not_found',
                'content': '',
                'file_path': full_path
            }
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return {
            'status': 'success',
            'content': content,
            'file_path': full_path,
            'length': len(content)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file_path': file_path
        }


def tourist_guide_agent(webhook_event: WebhookEvent, git_analysis: Dict[str, Any], context: Dict[str, Any]) -> TouristGuideResult:
    """
    Tourist Guide Agent that updates user-facing documentation based on code changes.
    
    Args:
        webhook_event: Parsed webhook event data
        git_analysis: Analysis from git analysis tool
        context: Additional context from orchestrator
        
    Returns:
        TouristGuideResult with documentation updates
    """
    
    change_type = git_analysis.get('change_type', 'unknown')
    affected_files = git_analysis.get('affected_components', [])
    commit_messages = [commit.message for commit in webhook_event.commits]
    
    # Use the workflow analysis tool
    workflow_analysis = analyze_user_workflow_impact(change_type, affected_files, commit_messages)
    
    # Generate documentation updates
    updates = _generate_documentation_updates(workflow_analysis, change_type, affected_files)
    
    # Write documentation files
    write_results = _write_documentation_files(updates, webhook_event.repository_name)
    
    # Generate or update main README.md hub
    readme_result = generate_main_readme(webhook_event.repository_name, webhook_event.repository_url or f"https://github.com/{webhook_event.repository_name}")
    if readme_result['status'] == 'success':
        readme_write_result = write_documentation_file("README.md", readme_result['content'], "create")
        write_results['README'] = readme_write_result
        if readme_write_result['status'] == 'success':
            print(f"✓ {readme_write_result['operation'].title()} {readme_write_result['file_path']}")
    
    # Create summary and user impact assessment
    summary = _generate_summary(updates, change_type, affected_files, write_results)
    user_impact = _assess_user_impact(workflow_analysis, change_type)
    
    return TouristGuideResult(
        updates=updates,
        summary=summary,
        user_impact=user_impact
    )


def _identify_user_facing_changes(change_type: str, affected_files: List[str], commit_messages: List[str]) -> Dict[str, Any]:
    """Identify which changes affect user workflows"""
    
    user_facing_indicators = {
        'cli_changes': ['cli.py', 'main.py', 'command', 'arg', 'option'],
        'api_changes': ['api/', 'endpoint', 'route', 'handler', 'controller'],
        'config_changes': ['config', 'settings', '.env', 'requirements'],
        'interface_changes': ['interface', 'ui/', 'frontend/', 'public/'],
        'documentation_files': ['readme', '.md', 'docs/', 'guide', 'tutorial'],
        'examples': ['example', 'sample', 'demo', 'tutorial']
    }
    
    identified_changes = {}
    
    for category, indicators in user_facing_indicators.items():
        matches = []
        
        # Check files
        for file in affected_files:
            if any(indicator in file.lower() for indicator in indicators):
                matches.append(f"File: {file}")
        
        # Check commit messages
        for msg in commit_messages:
            if any(indicator in msg.lower() for indicator in indicators):
                matches.append(f"Commit: {msg[:50]}...")
        
        if matches:
            identified_changes[category] = matches
    
    return identified_changes


def _assess_workflow_impact(change_type: str, user_facing_changes: Dict[str, Any]) -> Dict[str, str]:
    """Assess how changes impact user workflows"""
    
    impact_levels = {
        'discovery': 'none',
        'getting_started': 'none', 
        'patterns': 'none',
        'advanced': 'none',
        'troubleshooting': 'none'
    }
    
    # Feature changes typically affect multiple workflow areas
    if change_type == 'feature':
        if 'cli_changes' in user_facing_changes or 'api_changes' in user_facing_changes:
            impact_levels['getting_started'] = 'high'
            impact_levels['patterns'] = 'medium'
        if 'documentation_files' in user_facing_changes:
            impact_levels['discovery'] = 'medium'
    
    # Bug fixes often affect troubleshooting and getting started
    elif change_type == 'bugfix':
        impact_levels['troubleshooting'] = 'high'
        if 'cli_changes' in user_facing_changes:
            impact_levels['getting_started'] = 'medium'
    
    # Documentation changes directly affect discovery
    elif change_type == 'docs':
        impact_levels['discovery'] = 'high'
        if 'examples' in user_facing_changes:
            impact_levels['getting_started'] = 'high'
            impact_levels['patterns'] = 'medium'
    
    # Configuration changes affect setup and troubleshooting
    elif 'config_changes' in user_facing_changes:
        impact_levels['getting_started'] = 'medium'
        impact_levels['troubleshooting'] = 'medium'
    
    return impact_levels


def _recommend_documentation_updates(change_type: str, user_facing_changes: Dict[str, Any], workflow_impact: Dict[str, str]) -> List[str]:
    """Recommend specific documentation updates needed"""
    
    recommendations = []
    
    for section, impact_level in workflow_impact.items():
        if impact_level == 'none':
            continue
            
        if section == 'discovery':
            if change_type == 'feature':
                recommendations.append("Update project overview with new feature highlights")
                recommendations.append("Add feature to main README feature list")
            elif change_type == 'docs':
                recommendations.append("Refresh project description and value proposition")
        
        elif section == 'getting_started':
            if change_type == 'feature' and 'cli_changes' in user_facing_changes:
                recommendations.append("Update installation and setup instructions")
                recommendations.append("Add new feature to quick start guide")
            elif change_type == 'bugfix':
                recommendations.append("Update setup troubleshooting section")
        
        elif section == 'patterns':
            if change_type == 'feature':
                recommendations.append("Create usage examples for new feature")
                recommendations.append("Update common workflow patterns")
            elif change_type == 'docs' and 'examples' in user_facing_changes:
                recommendations.append("Review and update all usage examples")
        
        elif section == 'advanced':
            if change_type == 'feature' and impact_level in ['high', 'medium']:
                recommendations.append("Document advanced configuration options")
                recommendations.append("Add power user tips and tricks")
        
        elif section == 'troubleshooting':
            if change_type == 'bugfix':
                recommendations.append("Add resolved issue to troubleshooting guide")
                recommendations.append("Update error message documentation")
            elif 'config_changes' in user_facing_changes:
                recommendations.append("Update configuration troubleshooting section")
    
    return recommendations


def _generate_documentation_updates(workflow_analysis: Dict[str, Any], change_type: str, affected_files: List[str]) -> List[DocumentationUpdate]:
    """Generate specific documentation updates based on analysis"""
    
    updates = []
    doc_recommendations = workflow_analysis.get('documentation_updates', [])
    priority_level = workflow_analysis.get('priority_level', 3)
    
    # Group recommendations by section
    section_updates = {
        'discovery': [],
        'getting_started': [],
        'patterns': [],
        'advanced': [],
        'troubleshooting': []
    }
    
    for rec in doc_recommendations:
        if any(keyword in rec.lower() for keyword in ['overview', 'readme', 'feature list']):
            section_updates['discovery'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['installation', 'setup', 'quick start']):
            section_updates['getting_started'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['example', 'pattern', 'workflow']):
            section_updates['patterns'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['advanced', 'configuration', 'power user']):
            section_updates['advanced'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['troubleshooting', 'error', 'issue']):
            section_updates['troubleshooting'].append(rec)
    
    # Create DocumentationUpdate objects
    for section, recommendations in section_updates.items():
        if recommendations:
            content = _generate_content_for_section(section, change_type, affected_files, recommendations)
            updates.append(DocumentationUpdate(
                section=section,
                action='update' if change_type in ['feature', 'bugfix'] else 'append',
                content=content,
                reason=f"{change_type} changes affect {section}",
                priority=priority_level
            ))
    
    return updates


def _write_documentation_files(updates: List[DocumentationUpdate], repository_name: str) -> Dict[str, Any]:
    """Write documentation updates to files in coderipple directory"""
    write_results = {}
    
    for update in updates:
        file_name = f"{update.section}.md"
        
        # Check if file exists to determine action
        existing_doc = read_existing_documentation(file_name)
        
        if existing_doc['status'] == 'not_found':
            # Create new file with header
            content = _create_document_with_header(update, repository_name)
            action = "create"
        else:
            # Update existing file
            content = _update_existing_document(existing_doc['content'], update)
            action = "update"
        
        # Write the file
        result = write_documentation_file(file_name, content, action)
        write_results[update.section] = result
        
        if result['status'] == 'success':
            print(f"✓ {result['operation'].title()} {result['file_path']}")
        else:
            print(f"✗ Failed to write {file_name}: {result.get('error', 'Unknown error')}")
    
    return write_results


def _create_document_with_header(update: DocumentationUpdate, repository_name: str) -> str:
    """Create a new document with proper header and content"""
    section_titles = {
        'discovery': 'Project Discovery',
        'getting_started': 'Getting Started',
        'patterns': 'Usage Patterns',
        'advanced': 'Advanced Usage',
        'troubleshooting': 'Troubleshooting'
    }
    
    title = section_titles.get(update.section, update.section.replace('_', ' ').title())
    
    header = f"""# {title}

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: {repository_name}*  
*Last updated: {_get_current_timestamp()}*

---

"""
    
    return header + update.content


def _update_existing_document(existing_content: str, update: DocumentationUpdate) -> str:
    """Update existing document while preserving structure"""
    lines = existing_content.split('\n')
    
    # Update timestamp if it exists
    updated_lines = []
    for line in lines:
        if line.startswith('*Last updated:'):
            updated_lines.append(f"*Last updated: {_get_current_timestamp()}*")
        else:
            updated_lines.append(line)
    
    # Add new content at the end
    updated_content = '\n'.join(updated_lines)
    
    if update.action == "append":
        return updated_content + "\n\n---\n\n" + update.content
    else:
        # For "update" action, we'll append with a section header
        return updated_content + f"\n\n## Update: {_get_current_timestamp()}\n\n" + update.content


def _get_current_timestamp() -> str:
    """Get current timestamp for documentation headers"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _generate_content_for_section(section: str, change_type: str, affected_files: List[str], recommendations: List[str]) -> str:
    """Generate actual content for documentation sections"""
    
    if section == 'discovery':
        return f"""## Recent Updates

### {change_type.title()} Changes
- Modified files: {', '.join(affected_files[:3])}{'...' if len(affected_files) > 3 else ''}
- Impact: Enhanced user experience and functionality

### What's New
{chr(10).join(f"- {rec}" for rec in recommendations)}
"""
    
    elif section == 'getting_started':
        return f"""## Setup Notes

### Recent Changes ({change_type})
Due to recent {change_type} changes, please note:

{chr(10).join(f"- {rec}" for rec in recommendations)}

### Quick Start
1. Follow standard installation process
2. Review updated configuration options
3. Test new functionality
"""
    
    elif section == 'patterns':
        return f"""## Usage Patterns

### Updated Workflows
Recent {change_type} changes introduce new patterns:

{chr(10).join(f"- {rec}" for rec in recommendations)}

### Code Examples
```python
# Updated usage pattern
# TODO: Add specific examples based on changes
```
"""
    
    elif section == 'troubleshooting':
        if change_type == 'bugfix':
            return f"""## Resolved Issues

### Fixed in Latest Update
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Common Solutions
- Check updated configuration
- Verify file permissions
- Review error logs
"""
        else:
            return f"""## Configuration Issues

### Recent Changes
{chr(10).join(f"- {rec}" for rec in recommendations)}
"""
    
    return f"## {section.replace('_', ' ').title()}\n\nUpdated based on {change_type} changes."


def _calculate_priority(change_type: str, user_facing_changes: Dict[str, Any]) -> int:
    """Calculate priority level for documentation updates"""
    
    if change_type == 'feature' and ('cli_changes' in user_facing_changes or 'api_changes' in user_facing_changes):
        return 1  # High priority
    elif change_type in ['bugfix', 'docs'] and user_facing_changes:
        return 2  # Medium priority
    elif user_facing_changes:
        return 2  # Medium priority
    else:
        return 3  # Low priority


def _generate_summary(updates: List[DocumentationUpdate], change_type: str, affected_files: List[str], write_results: Dict[str, Any] = None) -> str:
    """Generate summary of Tourist Guide analysis"""
    
    if not updates:
        return f"No user-facing documentation updates needed for {change_type} changes."
    
    sections = list(set(update.section for update in updates))
    high_priority = sum(1 for update in updates if update.priority == 1)
    
    summary = f"Tourist Guide processed {len(updates)} documentation updates for {change_type} changes. "
    summary += f"Affected sections: {', '.join(sections)}. "
    
    if high_priority > 0:
        summary += f"{high_priority} high-priority updates identified. "
    else:
        summary += "All updates are medium/low priority. "
    
    # Add file writing results
    if write_results:
        successful_writes = sum(1 for result in write_results.values() if result.get('status') == 'success')
        total_writes = len(write_results)
        summary += f"Files written: {successful_writes}/{total_writes} successful."
    
    return summary


def _assess_user_impact(workflow_analysis: Dict[str, Any], change_type: str) -> str:
    """Assess overall impact on users"""
    
    priority_level = workflow_analysis.get('priority_level', 3)
    user_facing_changes = workflow_analysis.get('user_facing_changes', {})
    
    if priority_level == 1:
        return f"High impact: {change_type} changes significantly affect user workflows. Documentation updates required immediately."
    elif priority_level == 2:
        return f"Medium impact: {change_type} changes may affect some user workflows. Documentation should be updated soon."
    else:
        return f"Low impact: {change_type} changes have minimal effect on user workflows. Documentation updates can be deferred."


def _discover_all_documentation() -> Dict[str, List[Dict[str, Any]]]:
    """Discover all documentation files in coderipple directory"""
    import glob
    from datetime import datetime
    
    coderipple_dir = "coderipple"
    if not os.path.exists(coderipple_dir):
        return {}
    
    docs = {
        'user': [],
        'system': [],
        'decisions': []
    }
    
    # User documentation (Tourist Guide files)
    user_patterns = ['discovery.md', 'getting_started.md', 'patterns.md', 'troubleshooting.md', 'advanced.md']
    for pattern in user_patterns:
        files = glob.glob(os.path.join(coderipple_dir, pattern))
        for file_path in files:
            docs['user'].append(_get_file_info(file_path, 'user'))
    
    # System documentation (Building Inspector files)
    system_patterns = ['system/*.md', 'architecture.md', 'capabilities.md']
    for pattern in system_patterns:
        files = glob.glob(os.path.join(coderipple_dir, pattern))
        for file_path in files:
            docs['system'].append(_get_file_info(file_path, 'system'))
    
    # Decision documentation (Historian files)
    decision_patterns = ['decisions/*.md', 'adrs/*.md']
    for pattern in decision_patterns:
        files = glob.glob(os.path.join(coderipple_dir, pattern))
        for file_path in files:
            docs['decisions'].append(_get_file_info(file_path, 'decisions'))
    
    return docs


def _get_file_info(file_path: str, category: str) -> Dict[str, Any]:
    """Get file information including description and timestamp"""
    try:
        stat = os.stat(file_path)
        modified_time = datetime.fromtimestamp(stat.st_mtime)
        
        # Extract description from file
        description = _extract_description_from_file(file_path)
        
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'category': category,
            'description': description,
            'last_modified': modified_time.strftime("%Y-%m-%d %H:%M:%S"),
            'size': stat.st_size
        }
    except Exception as e:
        return {
            'path': file_path,
            'name': os.path.basename(file_path),
            'category': category,
            'description': 'Unable to read file description',
            'last_modified': 'Unknown',
            'size': 0,
            'error': str(e)
        }


def _extract_description_from_file(file_path: str) -> str:
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
            elif line.startswith('*This document') and 'Agent' in line:
                # Agent-maintained description
                continue
            elif line and not line.startswith('*') and not line.startswith('#') and len(line) > 20:
                # First substantial content line
                return line[:100] + '...' if len(line) > 100 else line
        
        return "Documentation file"
    except Exception:
        return "Unable to read description"


def _generate_hub_readme_content(repository_name: str, repository_url: str, existing_docs: Dict[str, List[Dict[str, Any]]]) -> str:
    """Generate content for the main README.md hub"""
    from datetime import datetime
    
    content = f"""# {repository_name} Documentation Hub

*Auto-generated documentation hub maintained by CodeRipple Tourist Guide Agent*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

Welcome to the {repository_name} documentation! This hub provides access to all automatically maintained documentation organized by a **layered documentation structure** - three layers that handle different depths of understanding.

## Documentation Layers

### 🎯 User Documentation (How to ENGAGE)
*Start here if you want to use or contribute to {repository_name}*

"""
    
    if existing_docs.get('user'):
        for doc in existing_docs['user']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
            content += f"  *Updated: {doc['last_modified']}*\n\n"
    else:
        content += "*No user documentation available yet*\n\n"
    
    content += """### 🏗️ System Documentation (What it IS)
*Current system architecture, capabilities, and technical specifications*

"""
    
    if existing_docs.get('system'):
        for doc in existing_docs['system']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
            content += f"  *Updated: {doc['last_modified']}*\n\n"
    else:
        content += "*No system documentation available yet*\n\n"
    
    content += """### 📚 Decision Documentation (Why it BECAME this way)
*Historical context, architectural decisions, and evolution story*

"""
    
    if existing_docs.get('decisions'):
        for doc in existing_docs['decisions']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
            content += f"  *Updated: {doc['last_modified']}*\n\n"
    else:
        content += "*No decision documentation available yet*\n\n"
    
    total_docs = sum(len(docs) for docs in existing_docs.values())
    
    content += f"""---

## Quick Navigation

- **[Repository]({repository_url})** - Source code and issues
- **Documentation Status**: {total_docs} files across {len([k for k, v in existing_docs.items() if v])} layers
- **Framework**: [Layered Documentation Structure](https://github.com/robertoallende/coderipple#documentation-layers)

## About This Documentation

This documentation is automatically maintained by **CodeRipple**, a multi-agent system that updates documentation based on code changes. Each layer serves a different purpose:

- **User docs** help you discover, learn, and use the system
- **System docs** explain what currently exists and how it works  
- **Decision docs** preserve why things were built this way

*Documentation automatically updates when code changes. If you notice gaps or issues, please [create an issue]({repository_url}/issues).*
"""
    
    return content


def _should_regenerate_navigation(existing_readme: str, all_docs: Dict[str, List[Dict[str, Any]]]) -> bool:
    """Check if README navigation section needs to be regenerated"""
    if not existing_readme:
        return True
    
    # Count current docs vs what's in README
    total_current_docs = sum(len(docs) for docs in all_docs.values())
    
    # Look for doc count in existing README
    import re
    doc_count_match = re.search(r'Documentation Status.*?(\d+) files', existing_readme)
    if doc_count_match:
        existing_count = int(doc_count_match.group(1))
        return existing_count != total_current_docs
    
    return True


def _update_navigation_section(existing_readme: str, all_docs: Dict[str, List[Dict[str, Any]]], repository_name: str) -> str:
    """Update the navigation section of existing README"""
    # For now, regenerate the entire README to ensure consistency
    # In a more sophisticated implementation, we could parse and update specific sections
    
    # Extract repository URL from existing content if available
    import re
    url_match = re.search(r'\[Repository\]\((.*?)\)', existing_readme)
    repository_url = url_match.group(1) if url_match else f"https://github.com/{repository_name}"
    
    return _generate_hub_readme_content(repository_name, repository_url, all_docs)


