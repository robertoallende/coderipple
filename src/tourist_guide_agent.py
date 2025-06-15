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
from content_generation_tools import (
    analyze_change_patterns,
    extract_code_examples_from_diff,
    generate_context_aware_content,
    enhance_generic_content_with_context,
    CodeExample,
    DocumentationFocus
)
from agent_context_flow import (
    register_agent_state, 
    get_agent_state, 
    get_current_capabilities,
    suggest_cross_references,
    add_global_insight
)
from bedrock_integration_tools import (
    enhance_content_with_bedrock,
    check_documentation_consistency,
    generate_dynamic_examples,
    analyze_content_gaps
)


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
    Uses intelligent content generation from Step 4B and context flow from Step 4C.
    
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
    
    # Step 4C: Get current system capabilities from Building Inspector if available
    building_inspector_state = get_agent_state('building_inspector')
    current_system_capabilities = []
    if building_inspector_state.get('status') == 'success':
        agent_data = building_inspector_state.get('agent_state', {})
        current_system_capabilities = agent_data.get('current_capabilities', [])
        
        # Add insight about referencing system capabilities
        add_global_insight(
            f"Tourist Guide referencing {len(current_system_capabilities)} capabilities from Building Inspector", 
            'tourist_guide'
        )
    
    # Step 4C: Get cross-reference suggestions for user documentation
    cross_ref_suggestions = suggest_cross_references('tourist_guide', f"User documentation for {change_type} changes")
    
    # Step 4B: Analyze change patterns to determine documentation focus
    doc_focus = analyze_change_patterns(affected_files, commit_messages)
    
    # Step 4B: Extract code examples from git diff (if available)
    code_examples = []
    git_diff = context.get('git_diff', '')
    if git_diff:
        for file_path in affected_files:
            examples = extract_code_examples_from_diff(git_diff, file_path)
            code_examples.extend(examples)
    
    # Use the workflow analysis tool (existing)
    workflow_analysis = analyze_user_workflow_impact(change_type, affected_files, commit_messages)
    
    # Step 4C: Enhance workflow analysis with system capabilities
    workflow_analysis = _enhance_workflow_with_system_capabilities(
        workflow_analysis, current_system_capabilities, change_type
    )
    
    # Step 4B: Generate intelligent documentation updates
    updates = _generate_intelligent_documentation_updates(
        workflow_analysis, git_analysis, doc_focus, code_examples, affected_files
    )
    
    # Step 4D: Enhance content with Bedrock
    enhanced_updates = _enhance_updates_with_bedrock(updates, git_analysis, context)
    updates = enhanced_updates if enhanced_updates else updates
    
    # Write documentation files
    write_results = _write_documentation_files(updates, webhook_event.repository_name)
    
    # Generate or update main README.md hub
    readme_result = generate_main_readme(webhook_event.repository_name, webhook_event.repository_url or f"https://github.com/{webhook_event.repository_name}")
    if readme_result['status'] == 'success':
        readme_write_result = write_documentation_file("README.md", readme_result['content'], "create")
        write_results['README'] = readme_write_result
        if readme_write_result['status'] == 'success':
            print(f"✓ {readme_write_result['operation'].title()} {readme_write_result['file_path']}")
    
    # Step 4C: Extract user-facing capabilities and insights
    user_capabilities = _extract_user_facing_capabilities(affected_files, change_type, current_system_capabilities)
    user_insights = _extract_user_insights(doc_focus, change_type, code_examples)
    
    # Step 4C: Build cross-references to other agents
    cross_references = _build_user_cross_references(cross_ref_suggestions, building_inspector_state)
    
    # Step 4C: Register our state in shared context
    generated_files = [update.section + '.md' for update in updates]
    if readme_result.get('status') == 'success':
        generated_files.append('README.md')
        
    register_result = register_agent_state(
        agent_name="Tourist Guide",
        agent_role="tourist_guide",
        repository_context={
            'change_type': change_type,
            'affected_files': affected_files,
            'doc_focus': doc_focus.__dict__ if hasattr(doc_focus, '__dict__') else str(doc_focus)
        },
        current_capabilities=user_capabilities,
        generated_files=generated_files,
        key_insights=user_insights,
        cross_references=cross_references
    )
    
    # Create summary and user impact assessment
    summary = _generate_summary(updates, change_type, affected_files, write_results)
    user_impact = _assess_user_impact_intelligent(doc_focus, change_type, code_examples)
    
    # Add context flow information to summary
    if register_result.get('status') == 'success':
        summary += f" Context shared: {register_result.get('files_registered', 0)} files registered with {register_result.get('total_agents', 0)} agents."
    
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


def _generate_intelligent_documentation_updates(workflow_analysis: Dict[str, Any], git_analysis: Dict[str, Any], 
                                               doc_focus: DocumentationFocus, code_examples: List[CodeExample], 
                                               affected_files: List[str]) -> List[DocumentationUpdate]:
    """
    Generate intelligent documentation updates using Step 4B content generation.
    
    Args:
        workflow_analysis: Traditional workflow analysis
        git_analysis: Git analysis results
        doc_focus: Documentation focus from change pattern analysis
        code_examples: Extracted code examples
        affected_files: List of affected files
        
    Returns:
        List of intelligent DocumentationUpdate objects
    """
    
    updates = []
    change_type = git_analysis.get('change_type', 'unknown')
    
    # Determine which sections need updates based on documentation focus
    sections_to_update = _determine_sections_from_focus(doc_focus, workflow_analysis)
    
    for section in sections_to_update:
        # Use intelligent content generation instead of generic templates
        intelligent_content = generate_context_aware_content(
            section=section,
            git_analysis=git_analysis,
            file_changes=affected_files,
            code_examples=code_examples,
            doc_focus=doc_focus
        )
        
        # Determine action based on change type and impact
        action = _determine_update_action(section, doc_focus, change_type)
        
        # Calculate priority based on user impact level
        priority = _calculate_intelligent_priority(doc_focus, section, change_type)
        
        # Create intelligent reason
        reason = _generate_intelligent_reason(section, doc_focus, change_type, code_examples)
        
        updates.append(DocumentationUpdate(
            section=section,
            action=action,
            content=intelligent_content,
            reason=reason,
            priority=priority
        ))
    
    return updates


def _determine_sections_from_focus(doc_focus: DocumentationFocus, workflow_analysis: Dict[str, Any]) -> List[str]:
    """Determine which documentation sections to update based on focus analysis"""
    
    sections = []
    
    # Use documentation focus to prioritize sections
    if doc_focus.primary_focus == 'api':
        sections.extend(['getting_started', 'patterns'])
        if doc_focus.user_impact_level == 'high':
            sections.append('discovery')
    
    elif doc_focus.primary_focus == 'cli':
        sections.extend(['getting_started', 'patterns'])
        if 'CLI' in doc_focus.affected_areas:
            sections.append('discovery')
    
    elif doc_focus.primary_focus == 'config':
        sections.extend(['getting_started', 'troubleshooting'])
    
    elif doc_focus.primary_focus == 'architecture':
        # Architecture changes are more for Building Inspector, but may affect patterns
        sections.append('patterns')
        if doc_focus.user_impact_level == 'high':
            sections.append('advanced')
    
    elif doc_focus.primary_focus == 'usage':
        sections.extend(['patterns', 'getting_started'])
    
    elif doc_focus.primary_focus == 'documentation':
        sections.append('discovery')
    
    # Fall back to workflow analysis if no specific focus
    if not sections:
        workflow_impact = workflow_analysis.get('workflow_impact', {})
        sections = [section for section, impact in workflow_impact.items() 
                   if impact != 'none']
    
    # Always include discovery for high-impact changes
    if doc_focus.user_impact_level == 'high' and 'discovery' not in sections:
        sections.append('discovery')
    
    return list(set(sections))


def _determine_update_action(section: str, doc_focus: DocumentationFocus, change_type: str) -> str:
    """Determine whether to create, update, or append based on intelligent analysis"""
    
    # High impact changes often require complete rewrites
    if doc_focus.user_impact_level == 'high' and change_type == 'feature':
        return 'update'
    
    # Breaking changes require updates to existing content
    elif 'breaking' in doc_focus.affected_areas or change_type == 'breaking':
        return 'update'
    
    # Bug fixes and documentation updates can be appended
    elif change_type in ['bugfix', 'docs']:
        return 'append'
    
    # Default to update for feature changes
    else:
        return 'update'


def _calculate_intelligent_priority(doc_focus: DocumentationFocus, section: str, change_type: str) -> int:
    """Calculate priority using intelligent analysis"""
    
    # High user impact = high priority
    if doc_focus.user_impact_level == 'high':
        return 1
    
    # API/CLI changes to getting_started are high priority
    if section == 'getting_started' and doc_focus.primary_focus in ['api', 'cli']:
        return 1
    
    # Medium impact or important sections = medium priority  
    if doc_focus.user_impact_level == 'medium' or section in ['discovery', 'patterns']:
        return 2
    
    # Everything else = low priority
    return 3


def _generate_intelligent_reason(section: str, doc_focus: DocumentationFocus, 
                                change_type: str, code_examples: List[CodeExample]) -> str:
    """Generate intelligent reason for documentation update"""
    
    base_reason = f"{change_type.title()} changes with {doc_focus.primary_focus} focus"
    
    if code_examples:
        example_count = len(code_examples)
        base_reason += f" ({example_count} code example{'s' if example_count != 1 else ''} extracted)"
    
    if doc_focus.user_impact_level == 'high':
        base_reason += " - High user impact detected"
    
    if doc_focus.affected_areas:
        areas = ', '.join(doc_focus.affected_areas[:2])
        base_reason += f" affecting {areas}"
    
    return base_reason


def _assess_user_impact_intelligent(doc_focus: DocumentationFocus, change_type: str, 
                                   code_examples: List[CodeExample]) -> str:
    """Assess user impact using intelligent analysis from Step 4B"""
    
    impact_description = f"{doc_focus.user_impact_level.title()} impact: "
    
    if doc_focus.user_impact_level == 'high':
        impact_description += f"{change_type.title()} changes with {doc_focus.primary_focus} focus "
        impact_description += "significantly affect user workflows. "
        
        if code_examples:
            new_examples = [ex for ex in code_examples if ex.change_type == 'added']
            if new_examples:
                impact_description += f"New functionality introduced ({len(new_examples)} new code patterns). "
        
        impact_description += "Documentation updates required immediately."
    
    elif doc_focus.user_impact_level == 'medium':
        impact_description += f"{change_type.title()} changes may affect user workflows in {doc_focus.primary_focus} area. "
        
        if doc_focus.affected_areas:
            areas = ', '.join(doc_focus.affected_areas)
            impact_description += f"Areas affected: {areas}. "
        
        impact_description += "Documentation should be updated soon."
    
    else:
        impact_description += f"{change_type.title()} changes have minimal direct user impact. "
        impact_description += "Documentation updates can be deferred unless user feedback indicates otherwise."
    
    return impact_description


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


def _enhance_workflow_with_system_capabilities(workflow_analysis: Dict[str, Any], 
                                             system_capabilities: List[str], 
                                             change_type: str) -> Dict[str, Any]:
    """Enhance workflow analysis with current system capabilities (Step 4C)"""
    
    enhanced_analysis = workflow_analysis.copy()
    
    # Add system capabilities context to recommendations
    if system_capabilities:
        enhanced_analysis['system_capabilities'] = system_capabilities
        
        # Add capability-aware recommendations
        capability_recommendations = []
        
        if change_type == 'feature':
            capability_recommendations.append(f"Document how new feature integrates with existing capabilities: {', '.join(system_capabilities[:3])}")
            
        if 'Multi-agent documentation generation' in system_capabilities:
            capability_recommendations.append("Update user workflow to reflect multi-agent documentation system")
            
        if 'GitHub webhook processing' in system_capabilities:
            capability_recommendations.append("Ensure user understands webhook-driven documentation updates")
        
        # Merge with existing recommendations
        existing_recs = enhanced_analysis.get('documentation_updates', [])
        enhanced_analysis['documentation_updates'] = existing_recs + capability_recommendations
    
    return enhanced_analysis


def _extract_user_facing_capabilities(affected_files: List[str], change_type: str, 
                                    system_capabilities: List[str]) -> List[str]:
    """Extract user-facing capabilities (Step 4C)"""
    
    user_capabilities = []
    
    # Base user capabilities
    user_capabilities.extend([
        "Automatic documentation generation",
        "GitHub webhook integration",
        "Multi-layered documentation structure"
    ])
    
    # Add capabilities based on change type
    if change_type == 'feature':
        user_capabilities.extend(["New feature availability", "Enhanced user workflows"])
    elif change_type == 'bugfix':
        user_capabilities.extend(["Improved system reliability", "Resolved user issues"])
    elif change_type == 'refactor':
        user_capabilities.append("Improved system performance")
    
    # Add capabilities based on affected files
    if any('cli' in f.lower() for f in affected_files):
        user_capabilities.append("Command-line interface")
        
    if any('api' in f.lower() for f in affected_files):
        user_capabilities.append("API integration capabilities")
        
    if any('test' in f.lower() for f in affected_files):
        user_capabilities.append("Automated testing and validation")
    
    # Reference system capabilities if available
    if system_capabilities:
        # Map system capabilities to user-facing ones
        system_to_user_mapping = {
            'GitHub webhook processing': 'Real-time documentation updates',
            'Multi-agent documentation generation': 'Comprehensive documentation coverage',
            'Git analysis and change detection': 'Smart change-based documentation',
            'Markdown documentation output': 'Readable documentation format'
        }
        
        for sys_cap in system_capabilities:
            if sys_cap in system_to_user_mapping:
                user_capabilities.append(system_to_user_mapping[sys_cap])
    
    return list(set(user_capabilities))  # Remove duplicates


def _extract_user_insights(doc_focus: DocumentationFocus, change_type: str, 
                         code_examples: List[CodeExample]) -> List[str]:
    """Extract insights relevant to users (Step 4C)"""
    
    insights = []
    
    # Focus-based insights
    if doc_focus.primary_focus == 'api':
        insights.append("API changes may require updates to user integrations")
    elif doc_focus.primary_focus == 'cli':
        insights.append("Command-line interface changes affect user workflows")
    elif doc_focus.primary_focus == 'config':
        insights.append("Configuration changes may require user environment updates")
    
    # Impact level insights
    if doc_focus.user_impact_level == 'high':
        insights.append("High-impact changes require immediate user attention")
        if code_examples:
            insights.append(f"Users should review {len(code_examples)} new code examples")
    elif doc_focus.user_impact_level == 'medium':
        insights.append("Moderate impact - users should review changes when convenient")
    
    # Change type insights
    if change_type == 'feature':
        insights.append("New functionality expands user capabilities")
    elif change_type == 'bugfix':
        insights.append("Bug fixes improve user experience and reliability")
    elif change_type == 'refactor':
        insights.append("Internal improvements with minimal user-facing changes")
    
    # Code example insights
    if code_examples:
        added_examples = [ex for ex in code_examples if ex.change_type == 'added']
        if added_examples:
            insights.append(f"New code patterns introduced: {len(added_examples)} examples for users to follow")
    
    return insights


def _build_user_cross_references(cross_ref_suggestions: Dict[str, Any], 
                                building_inspector_state: Dict[str, Any]) -> Dict[str, str]:
    """Build cross-references to other agents' work for users (Step 4C)"""
    
    cross_references = {}
    
    # Reference Building Inspector system documentation
    if building_inspector_state.get('status') == 'success':
        agent_data = building_inspector_state.get('agent_state', {})
        system_files = agent_data.get('generated_files', [])
        
        if system_files:
            cross_references['system_documentation'] = f"See technical system documentation for architecture details"
            cross_references['system_files'] = f"System docs: {', '.join(system_files[:2])}"
    
    # Process cross-reference suggestions
    if cross_ref_suggestions.get('status') == 'success':
        suggestions = cross_ref_suggestions.get('suggestions', [])
        
        for suggestion in suggestions:
            agent_role = suggestion.get('agent_role')
            agent_name = suggestion.get('agent_name')
            
            if agent_role == 'building_inspector':
                cross_references['technical_details'] = f"For technical implementation details, see {agent_name} documentation"
                
            elif agent_role == 'historian':
                cross_references['evolution_context'] = f"For background and decision context, see {agent_name} documentation"
                
            # Include relevant capabilities
            relevant_capabilities = suggestion.get('relevant_capabilities', [])
            if relevant_capabilities:
                cross_references[f'{agent_role}_capabilities'] = f"Related capabilities: {', '.join(relevant_capabilities[:2])}"
    
    return cross_references


def _enhance_updates_with_bedrock(updates: List[DocumentationUpdate], git_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[DocumentationUpdate]:
    """
    Enhance documentation updates using Bedrock AI integration (Step 4D).
    
    Args:
        updates: List of documentation updates to enhance
        git_analysis: Git analysis results for context
        context: Additional context from orchestrator
        
    Returns:
        List of enhanced DocumentationUpdate objects
    """
    if not updates:
        return updates
    
    enhanced_updates = []
    
    for update in updates:
        try:
            # Prepare context for Bedrock enhancement
            enhancement_context = {
                'section_type': update.section,
                'target_audience': 'developers',
                'change_type': git_analysis.get('change_type', 'unknown'),
                'user_impact': update.priority,
                'repository_context': context.get('repository_name', 'Unknown')
            }
            
            # Call Bedrock enhancement tool
            enhancement_result = enhance_content_with_bedrock(
                content=update.content,
                context=enhancement_context
            )
            
            if enhancement_result.get('status') == 'success':
                # Extract enhanced content from Bedrock response
                bedrock_data = enhancement_result.get('content', [{}])[0]
                
                if 'json' in bedrock_data:
                    enhanced_data = bedrock_data['json']
                    enhanced_content = enhanced_data.get('enhanced_content', update.content)
                    improvements = enhanced_data.get('improvements_made', [])
                    quality_score = enhanced_data.get('quality_score', 0.0)
                    
                    # Update the documentation update with enhanced content
                    enhanced_update = DocumentationUpdate(
                        section=update.section,
                        action=update.action,
                        content=enhanced_content,
                        reason=f"{update.reason} | Bedrock enhanced (quality: {quality_score:.2f})",
                        priority=update.priority
                    )
                    
                    enhanced_updates.append(enhanced_update)
                    
                    # Log improvements made
                    if improvements:
                        print(f"✓ Bedrock enhanced {update.section}: {', '.join(improvements[:2])}")
                else:
                    # Fallback if JSON parsing failed
                    enhanced_updates.append(update)
            else:
                # Fallback to original content if Bedrock fails
                enhanced_updates.append(update)
                print(f"⚠ Bedrock enhancement failed for {update.section}, using original content")
                
        except Exception as e:
            # Fallback to original content on any error
            enhanced_updates.append(update)
            print(f"⚠ Bedrock enhancement error for {update.section}: {str(e)}")
    
    return enhanced_updates


def _check_cross_agent_consistency(agent_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check consistency across documentation layers using Bedrock (Step 4D).
    
    Args:
        agent_state: Current agent state including generated content
        
    Returns:
        Dictionary with consistency check results
    """
    try:
        # Get content from all agents if available
        content_layers = {}
        
        # Tourist Guide content (this agent)
        tourist_files = agent_state.get('generated_files', [])
        if tourist_files:
            content_layers['tourist_guide'] = f"Generated files: {', '.join(tourist_files)}"
        
        # Try to get Building Inspector content
        building_inspector_state = get_agent_state('building_inspector')
        if building_inspector_state.get('status') == 'success':
            inspector_data = building_inspector_state.get('agent_state', {})
            inspector_files = inspector_data.get('generated_files', [])
            if inspector_files:
                content_layers['building_inspector'] = f"System files: {', '.join(inspector_files)}"
        
        # Try to get Historian content
        historian_state = get_agent_state('historian')
        if historian_state.get('status') == 'success':
            historian_data = historian_state.get('agent_state', {})
            historian_files = historian_data.get('generated_files', [])
            if historian_files:
                content_layers['historian'] = f"Decision files: {', '.join(historian_files)}"
        
        if len(content_layers) < 2:
            return {
                'status': 'insufficient_data',
                'message': 'Need at least 2 agents to check consistency'
            }
        
        # Call Bedrock consistency check
        consistency_result = check_documentation_consistency(
            content_layers=content_layers,
            focus_area="user_experience"
        )
        
        if consistency_result.get('status') == 'success':
            consistency_data = consistency_result.get('content', [{}])[0]
            if 'json' in consistency_data:
                return {
                    'status': 'success',
                    'consistency_check': consistency_data['json']
                }
        
        return {
            'status': 'error',
            'message': 'Consistency check failed'
        }
        
    except Exception as e:
        return {
            'status': 'error', 
            'message': f"Consistency check error: {str(e)}"
        }


def _generate_dynamic_examples_for_users(code_context: Dict[str, Any], git_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate dynamic code examples for user documentation using Bedrock (Step 4D).
    
    Args:
        code_context: Context about recent code changes
        git_analysis: Git analysis results
        
    Returns:
        List of generated examples
    """
    try:
        # Prepare context for dynamic example generation
        example_context = {
            'file_changes': git_analysis.get('affected_components', []),
            'system_capabilities': [
                'GitHub webhook processing',
                'Multi-agent documentation generation', 
                'Automated content creation'
            ],
            'target_use_case': f"Using the system after {git_analysis.get('change_type', 'recent')} changes"
        }
        
        # Generate examples for common user scenarios
        example_types = ['usage', 'integration', 'cli']
        all_examples = []
        
        for example_type in example_types:
            example_result = generate_dynamic_examples(
                code_context=example_context,
                example_type=example_type
            )
            
            if example_result.get('status') == 'success':
                example_data = example_result.get('content', [{}])[0]
                if 'json' in example_data:
                    examples = example_data['json'].get('examples', [])
                    for example in examples:
                        example['type'] = example_type
                        all_examples.append(example)
        
        return all_examples
        
    except Exception as e:
        print(f"⚠ Dynamic example generation failed: {str(e)}")
        return []


