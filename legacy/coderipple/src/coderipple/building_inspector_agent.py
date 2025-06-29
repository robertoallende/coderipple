"""
Building Inspector Agent for CodeRipple

This agent focuses on the middle layer of documentation - "What it IS".
Documents what's actually there right now, how systems work, current specifications.
Updates based on incremental rewrites as sections change.

Core Elements:
- Purpose & Problem Solved: Why this system exists
- Architecture & Design: How it's structured and organized  
- Interfaces & Usage: How to interact with the system
- Current Capabilities & Constraints: What it can/cannot do
- Technology Stack: What technologies are used
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from strands import tool
from coderipple.config import get_config, get_documentation_path
from coderipple.webhook_parser import WebhookEvent
from coderipple.agent_context_flow import register_agent_state, get_agent_state, suggest_cross_references
from coderipple.bedrock_integration_tools import (
    enhance_content_with_bedrock,
    check_documentation_consistency,
    generate_dynamic_examples,
    analyze_content_gaps
)
from coderipple.content_generation_tools import generate_context_rich_content
from coderipple.content_validation_tools import (
    validate_documentation_quality,
    enforce_quality_standards,
    validate_and_improve_content
)


@dataclass
class SystemDocumentationUpdate:
    """Represents a system documentation update decision"""
    section: str  # 'purpose', 'architecture', 'interfaces', 'capabilities', 'tech_stack'
    action: str   # 'create', 'update', 'rewrite'
    content: str
    reason: str
    priority: int  # 1=high, 2=medium, 3=low


@dataclass
class BuildingInspectorResult:
    """Result of Building Inspector analysis"""
    updates: List[SystemDocumentationUpdate]
    summary: str
    system_impact: str  # Description of how this affects the current system


@tool
def analyze_system_changes(change_type: str, affected_files: List[str], commit_messages: List[str]) -> Dict[str, Any]:
    """
    Analyze how code changes impact the current system and determine documentation updates needed.
    
    Args:
        change_type: Type of change (feature, bugfix, etc.)
        affected_files: List of files that were changed
        commit_messages: List of commit messages for context
        
    Returns:
        Dictionary with system impact analysis and documentation recommendations
    """
    
    # Analyze system-level impact
    system_changes = _identify_system_changes(change_type, affected_files, commit_messages)
    system_impact = _assess_system_impact(change_type, system_changes)
    doc_updates = _recommend_system_documentation_updates(change_type, system_changes, system_impact)
    
    return {
        'system_changes': system_changes,
        'system_impact': system_impact,
        'documentation_updates': doc_updates,
        'priority_level': _calculate_system_priority(change_type, system_changes)
    }


@tool
def write_system_documentation_file(file_path: str, content: str, action: str = "create") -> Dict[str, Any]:
    """
    Write or update system documentation files using configurable output directory.
    
    Args:
        file_path: Relative path within system directory (e.g., "architecture.md")
        content: Content to write
        action: "create", "update", or "rewrite"
        
    Returns:
        Dictionary with operation status and details
    """
    try:
        config = get_config()
        # Ensure system directory exists within configured output directory
        system_dir = get_documentation_path("system")
        if not os.path.exists(system_dir):
            os.makedirs(system_dir)
        
        full_path = os.path.join(system_dir, file_path)
        
        # Ensure subdirectories exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Validate content quality before writing
        validation_result = enforce_quality_standards(
            content=content,
            file_path=full_path,
            min_quality_score=70.0,  # Higher threshold for system docs
            project_root=os.getcwd()
        )
        
        # Check if content meets quality standards
        if not validation_result['write_approved']:
            # Try to get improved content if validation suggests improvements
            improvement_result = validate_and_improve_content(
                content=content,
                file_path=full_path,
                project_root=os.getcwd()
            )
            
            return {
                'status': 'validation_failed',
                'error': f"System content validation failed (score: {validation_result['quality_score']:.1f})",
                'validation_errors': validation_result['errors'],
                'validation_warnings': validation_result['warnings'],
                'suggestions': validation_result['suggestions'],
                'improvement_suggestions': improvement_result.get('improvement_suggestions', []),
                'file_path': file_path,
                'content_length': len(content)
            }
        
        # Content passed validation - proceed with writing
        if action == "create":
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "created"
            
        elif action == "rewrite":
            # For rewrite, we completely replace the content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "rewritten"
            
        elif action == "update":
            # For update, we'll overwrite the file (Building Inspector doesn't preserve history)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "updated"
        
        return {
            'status': 'success',
            'operation': operation,
            'file_path': full_path,
            'content_length': len(content),
            'validation_score': validation_result['quality_score'],
            'validation_warnings': validation_result.get('warnings', [])
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'file_path': file_path
        }


@tool  
def read_existing_system_documentation(file_path: str) -> Dict[str, Any]:
    """
    Read existing system documentation file to check current content.
    
    Args:
        file_path: Relative path within system directory
        
    Returns:
        Dictionary with file content or error
    """
    try:
        full_path = get_documentation_path(os.path.join("system", file_path))
        
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


def building_inspector_agent(webhook_event: WebhookEvent, git_analysis: Dict[str, Any], context: Dict[str, Any]) -> BuildingInspectorResult:
    """
    Building Inspector Agent that updates system documentation based on code changes.
    Uses context flow to share system state and reference other agents.
    
    Args:
        webhook_event: Parsed webhook event data
        git_analysis: Analysis from git analysis tool
        context: Additional context from orchestrator
        
    Returns:
        BuildingInspectorResult with system documentation updates
    """
    
    change_type = git_analysis.get('change_type', 'unknown')
    affected_files = git_analysis.get('affected_components', [])
    commit_messages = [commit.message for commit in webhook_event.commits]
    
    # Check if other agents have relevant context
    cross_ref_suggestions = suggest_cross_references('building_inspector', f"System architecture changes for {change_type}")
    
    # Use the system analysis tool
    system_analysis = analyze_system_changes(change_type, affected_files, commit_messages)
    
    # Generate documentation updates
    updates = _generate_system_documentation_updates(system_analysis, change_type, affected_files)
    
    # Enhance content with Bedrock for system documentation
    enhanced_updates = _enhance_system_updates_with_bedrock(updates, system_analysis, context)
    updates = enhanced_updates if enhanced_updates else updates
    
    # Write documentation files
    write_results = _write_system_documentation_files(updates, webhook_event.repository_name)
    
    # Extract current capabilities from our analysis
    current_capabilities = _extract_system_capabilities(system_analysis, affected_files, change_type)
    
    # Identify key insights about the system
    key_insights = _extract_system_insights(system_analysis, change_type, affected_files)
    
    # Create cross-references to other agents if they exist
    cross_references = _build_cross_references(cross_ref_suggestions)
    
    # Register our state in shared context
    generated_files = [update.section + '.md' for update in updates]
    register_result = register_agent_state(
        agent_name="Building Inspector",
        agent_role="building_inspector", 
        repository_context={
            'change_type': change_type,
            'affected_files': affected_files,
            'system_analysis': system_analysis
        },
        current_capabilities=current_capabilities,
        generated_files=[f"system/{f}" for f in generated_files],
        key_insights=key_insights,
        cross_references=cross_references
    )
    
    # Create summary and system impact assessment
    summary = _generate_system_summary(updates, change_type, affected_files, write_results)
    system_impact = _assess_overall_system_impact(system_analysis, change_type)
    
    # Add context flow information to summary
    if register_result.get('status') == 'success':
        summary += f" Context shared: {register_result.get('files_registered', 0)} files registered with {register_result.get('total_agents', 0)} agents."
    
    return BuildingInspectorResult(
        updates=updates,
        summary=summary,
        system_impact=system_impact
    )


def _identify_system_changes(change_type: str, affected_files: List[str], commit_messages: List[str]) -> Dict[str, Any]:
    """Identify which changes affect the current system"""
    
    system_indicators = {
        'core_functionality': ['src/', 'lib/', 'core/', 'main.py', 'app.py', '__init__.py'],
        'architecture_changes': ['migrations/', 'models/', 'schema', 'database/', 'db/'],
        'api_interfaces': ['api/', 'routes/', 'endpoints/', 'controllers/', 'handlers/'],
        'configuration': ['config/', 'settings', '.env', 'dockerfile', 'docker-compose'],
        'dependencies': ['requirements.txt', 'package.json', 'Cargo.toml', 'pom.xml', 'setup.py'],
        'infrastructure': ['terraform/', 'cloudformation/', '.github/', 'deploy/', 'k8s/']
    }
    
    identified_changes = {}
    
    for category, indicators in system_indicators.items():
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


def _assess_system_impact(change_type: str, system_changes: Dict[str, Any]) -> Dict[str, str]:
    """Assess how changes impact different aspects of the current system"""
    
    impact_levels = {
        'purpose': 'none',
        'architecture': 'none',
        'interfaces': 'none',
        'capabilities': 'none',
        'tech_stack': 'none'
    }
    
    # Feature changes typically affect capabilities and interfaces
    if change_type == 'feature':
        impact_levels['capabilities'] = 'high'
        if 'api_interfaces' in system_changes:
            impact_levels['interfaces'] = 'high'
        if 'core_functionality' in system_changes:
            impact_levels['architecture'] = 'medium'
    
    # Bug fixes affect current capabilities
    elif change_type == 'bugfix':
        impact_levels['capabilities'] = 'medium'
        if 'core_functionality' in system_changes:
            impact_levels['architecture'] = 'low'
    
    # Refactoring affects architecture significantly
    elif change_type == 'refactor':
        impact_levels['architecture'] = 'high'
        if 'core_functionality' in system_changes:
            impact_levels['capabilities'] = 'medium'
    
    # Dependencies affect tech stack
    if 'dependencies' in system_changes:
        impact_levels['tech_stack'] = 'high'
    
    # Infrastructure changes affect architecture
    if 'infrastructure' in system_changes:
        impact_levels['architecture'] = 'medium'
        impact_levels['tech_stack'] = 'medium'
    
    # Configuration changes affect current setup
    if 'configuration' in system_changes:
        impact_levels['capabilities'] = 'medium'
        impact_levels['tech_stack'] = 'low'
    
    return impact_levels


def _recommend_system_documentation_updates(change_type: str, system_changes: Dict[str, Any], system_impact: Dict[str, str]) -> List[str]:
    """Recommend specific system documentation updates needed"""
    
    recommendations = []
    
    for section, impact_level in system_impact.items():
        if impact_level == 'none':
            continue
            
        if section == 'purpose':
            if change_type == 'feature' and impact_level == 'high':
                recommendations.append("Update system purpose with new capabilities")
                recommendations.append("Refresh problem statement and solution approach")
        
        elif section == 'architecture':
            if change_type == 'feature':
                recommendations.append("Update architectural diagrams with new components")
                recommendations.append("Document new system interactions and data flows")
            elif change_type == 'refactor':
                recommendations.append("Rewrite architectural documentation to reflect changes")
                recommendations.append("Update component relationships and boundaries")
        
        elif section == 'interfaces':
            if 'api_interfaces' in system_changes:
                recommendations.append("Update API documentation with new endpoints")
                recommendations.append("Document interface changes and compatibility")
            if change_type == 'feature':
                recommendations.append("Add new interface usage examples")
        
        elif section == 'capabilities':
            if change_type == 'feature':
                recommendations.append("Document new system capabilities and features")
                recommendations.append("Update capability matrix and limitations")
            elif change_type == 'bugfix':
                recommendations.append("Update known limitations and resolved issues")
        
        elif section == 'tech_stack':
            if 'dependencies' in system_changes:
                recommendations.append("Update technology stack documentation")
                recommendations.append("Document new dependencies and versions")
            if 'infrastructure' in system_changes:
                recommendations.append("Update deployment and infrastructure documentation")
    
    return recommendations


def _generate_system_documentation_updates(system_analysis: Dict[str, Any], change_type: str, affected_files: List[str]) -> List[SystemDocumentationUpdate]:
    """Generate specific system documentation updates based on analysis"""
    
    updates = []
    doc_recommendations = system_analysis.get('documentation_updates', [])
    priority_level = system_analysis.get('priority_level', 3)
    
    # Group recommendations by section
    section_updates = {
        'purpose': [],
        'architecture': [],
        'interfaces': [],
        'capabilities': [],
        'tech_stack': []
    }
    
    for rec in doc_recommendations:
        if any(keyword in rec.lower() for keyword in ['purpose', 'problem', 'solution']):
            section_updates['purpose'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['architecture', 'component', 'diagram', 'structure']):
            section_updates['architecture'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['api', 'interface', 'endpoint', 'usage']):
            section_updates['interfaces'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['capabilities', 'feature', 'limitation', 'constraint']):
            section_updates['capabilities'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['technology', 'dependencies', 'stack', 'infrastructure']):
            section_updates['tech_stack'].append(rec)
    
    # Create SystemDocumentationUpdate objects
    for section, recommendations in section_updates.items():
        if recommendations:
            # Use context-rich content generation with system focus
            content = _generate_system_content_with_context_analysis(section, change_type, affected_files, recommendations, system_analysis)
            
            # Building Inspector uses rewrite pattern for major changes
            action = 'rewrite' if change_type == 'refactor' else 'update'
            
            updates.append(SystemDocumentationUpdate(
                section=section,
                action=action,
                content=content,
                reason=f"{change_type} changes affect current {section}",
                priority=priority_level
            ))
    
    return updates


def _write_system_documentation_files(updates: List[SystemDocumentationUpdate], repository_name: str) -> Dict[str, Any]:
    """Write system documentation updates to files in coderipple/system directory"""
    write_results = {}
    
    for update in updates:
        file_name = f"{update.section}.md"
        
        # Check if file exists to determine action
        existing_doc = read_existing_system_documentation(file_name)
        
        if existing_doc['status'] == 'not_found':
            # Create new file with header
            content = _create_system_document_with_header(update, repository_name)
            action = "create"
        else:
            # Building Inspector rewrites sections (no history preservation)
            content = _rewrite_system_document(update, repository_name)
            action = update.action
        
        # Write the file
        result = write_system_documentation_file(file_name, content, action)
        write_results[update.section] = result
        
        if result['status'] == 'success':
            print(f"✓ {result['operation'].title()} {result['file_path']}")
        else:
            print(f"✗ Failed to write {file_name}: {result.get('error', 'Unknown error')}")
    
    return write_results


def _create_system_document_with_header(update: SystemDocumentationUpdate, repository_name: str) -> str:
    """Create a new system document with proper header and content"""
    section_titles = {
        'purpose': 'System Purpose & Problem Solved',
        'architecture': 'Architecture & Design',
        'interfaces': 'Interfaces & Usage',
        'capabilities': 'Current Capabilities & Constraints',
        'tech_stack': 'Technology Stack'
    }
    
    title = section_titles.get(update.section, update.section.replace('_', ' ').title())
    
    header = f"""# {title}

*This document is automatically maintained by CodeRipple Building Inspector Agent*  
*Repository: {repository_name}*  
*Last updated: {_get_current_timestamp()}*  
*Documentation reflects current system state only*

---

"""
    
    return header + update.content


def _rewrite_system_document(update: SystemDocumentationUpdate, repository_name: str) -> str:
    """Rewrite system document (Building Inspector doesn't preserve history)"""
    # Building Inspector always rewrites to reflect current state
    return _create_system_document_with_header(update, repository_name)


def _get_current_timestamp() -> str:
    """Get current timestamp for documentation headers"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _generate_system_content_for_section(section: str, change_type: str, affected_files: List[str], recommendations: List[str]) -> str:
    """Generate actual content for system documentation sections"""
    
    if section == 'purpose':
        return f"""## System Purpose

This system addresses the following problem:
- Automated documentation maintenance through multi-agent analysis
- Reduction of documentation debt and manual updating overhead

### Current Solution Approach
The system uses role-based agents to analyze code changes and update documentation at different layers:
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Key Value Propositions
- Real-time documentation updates
- Multi-perspective documentation coverage
- Autonomous operation without human intervention
"""
    
    elif section == 'architecture':
        return f"""## System Architecture

### Current Architecture Overview
The system follows a webhook-driven, multi-agent architecture:

```
GitHub Webhook → API Gateway → Orchestrator Agent → Specialist Agents → Documentation Output
```

### Recent Changes ({change_type})
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Core Components
- **Orchestrator Agent**: Coordinates agent invocation based on change analysis
- **Tourist Guide Agent**: Maintains user-facing documentation
- **Building Inspector Agent**: Documents current system state
- **Historian Agent**: Preserves architectural decisions and evolution

### Data Flow
1. Webhook event received from GitHub
2. Git analysis tool categorizes changes
3. Decision tree determines which agents to invoke
4. Agents update their respective documentation layers
"""
    
    elif section == 'interfaces':
        return f"""## System Interfaces

### Primary Interfaces
- **GitHub Webhooks**: Incoming change notifications
- **Strands Tools**: Agent coordination and communication
- **File System**: Documentation output (`coderipple/` directory)

### Recent Interface Changes ({change_type})
{chr(10).join(f"- {rec}" for rec in recommendations)}

### API Usage Patterns
```python
# Webhook processing
webhook_event = parser.parse_webhook_payload(payload, event_type)

# Agent invocation
result = orchestrator_agent(webhook_payload, event_type)

# Documentation writing
write_result = write_documentation_file(file_path, content, action)
```

### Input/Output Specifications
- **Input**: GitHub webhook JSON payloads
- **Output**: Markdown documentation files organized by agent type
"""
    
    elif section == 'capabilities':
        return f"""## Current Capabilities

### What the System Can Do
- Parse GitHub webhook events (push, pull_request)
- Analyze git diffs to categorize change types
- Coordinate multiple specialist agents based on change analysis
- Generate and update documentation files automatically
- Maintain separate documentation layers (user-facing, system, decisions)

### Recent Capability Changes ({change_type})
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Current Constraints
- Limited to GitHub webhooks as trigger mechanism
- Requires manual setup and configuration
- Not yet deployed to production infrastructure
- Agent coordination limited to implemented agents

### Performance Characteristics
- Response time: < 30 seconds for typical changes
- Supported file types: All text-based files
- Concurrent processing: Single-threaded currently
"""
    
    elif section == 'tech_stack':
        return f"""## Technology Stack

### Core Technologies
- **Python 3.x**: Primary development language
- **AWS Strands**: Agent orchestration framework
- **AWS Lambda**: Planned serverless execution environment
- **GitHub API**: Source code change detection

### Recent Technology Changes ({change_type})
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Dependencies
- strands-agents: Agent framework and tools
- Standard Python libraries: json, urllib, datetime, typing

### Infrastructure Components (Planned)
- AWS API Gateway: Webhook endpoint
- AWS Lambda: Agent execution
- Amazon Bedrock: AI analysis
- Terraform: Infrastructure as Code

### Development Tools
- Virtual environment: Python venv
- Testing: Python unittest framework
- Version control: Git with GitHub
"""
    
    return f"## {section.replace('_', ' ').title()}\n\nCurrent system documentation for {section} based on {change_type} changes."


def _calculate_system_priority(change_type: str, system_changes: Dict[str, Any]) -> int:
    """Calculate priority level for system documentation updates"""
    
    if change_type == 'feature' and ('core_functionality' in system_changes or 'api_interfaces' in system_changes):
        return 1  # High priority
    elif change_type == 'refactor' and 'architecture_changes' in system_changes:
        return 1  # High priority for architectural changes
    elif change_type in ['feature', 'bugfix'] and system_changes:
        return 2  # Medium priority
    elif system_changes:
        return 2  # Medium priority
    else:
        return 3  # Low priority


def _generate_system_summary(updates: List[SystemDocumentationUpdate], change_type: str, affected_files: List[str], write_results: Dict[str, Any] = None) -> str:
    """Generate summary of Building Inspector analysis"""
    
    if not updates:
        return f"No system documentation updates needed for {change_type} changes."
    
    sections = list(set(update.section for update in updates))
    high_priority = sum(1 for update in updates if update.priority == 1)
    
    summary = f"Building Inspector processed {len(updates)} system documentation updates for {change_type} changes. "
    summary += f"Affected sections: {', '.join(sections)}. "
    
    if high_priority > 0:
        summary += f"{high_priority} high-priority updates identified. "
    else:
        summary += "All updates are medium/low priority. "
    
    # Add file writing results
    if write_results:
        successful_writes = sum(1 for result in write_results.values() if result.get('status') == 'success')
        total_writes = len(write_results)
        summary += f"System docs written: {successful_writes}/{total_writes} successful."
    
    return summary


def _assess_overall_system_impact(system_analysis: Dict[str, Any], change_type: str) -> str:
    """Assess overall impact on the current system"""
    
    priority_level = system_analysis.get('priority_level', 3)
    system_changes = system_analysis.get('system_changes', {})
    
    if priority_level == 1:
        return f"High impact: {change_type} changes significantly modify current system architecture or capabilities."
    elif priority_level == 2:
        return f"Medium impact: {change_type} changes affect some aspects of the current system."
    else:
        return f"Low impact: {change_type} changes have minimal effect on current system documentation."


def _extract_system_capabilities(system_analysis: Dict[str, Any], affected_files: List[str], change_type: str) -> List[str]:
    """Extract current system capabilities from analysis"""
    
    capabilities = []
    system_changes = system_analysis.get('system_changes', {})
    
    # Base capabilities
    capabilities.extend([
        "GitHub webhook processing",
        "Multi-agent documentation generation", 
        "Git analysis and change detection",
        "Markdown documentation output"
    ])
    
    # Add capabilities based on detected changes
    if 'core_functionality' in system_changes:
        capabilities.append("Core system functionality")
        
    if 'api_interfaces' in system_changes:
        capabilities.extend(["API endpoint management", "Interface documentation"])
        
    if 'architecture_changes' in system_changes:
        capabilities.extend(["Architecture modification", "System restructuring"])
        
    if 'dependencies' in system_changes:
        capabilities.append("Dependency management")
        
    if 'infrastructure' in system_changes:
        capabilities.extend(["Infrastructure as code", "Deployment automation"])
        
    if 'configuration' in system_changes:
        capabilities.append("Configuration management")
    
    # Add change-type specific capabilities
    if change_type == 'feature':
        capabilities.append("Feature integration and documentation")
    elif change_type == 'bugfix':
        capabilities.append("Issue resolution and system repair")
    elif change_type == 'refactor':
        capabilities.append("Code refactoring and optimization")
    
    return list(set(capabilities))  # Remove duplicates


def _extract_system_insights(system_analysis: Dict[str, Any], change_type: str, affected_files: List[str]) -> List[str]:
    """Extract key insights about the system"""
    
    insights = []
    system_changes = system_analysis.get('system_changes', {})
    
    # Insights based on change patterns
    if len(system_changes) > 3:
        insights.append(f"Broad system impact: {change_type} affects multiple system areas")
        
    if 'core_functionality' in system_changes and 'api_interfaces' in system_changes:
        insights.append("Changes affect both core functionality and external interfaces")
        
    if 'dependencies' in system_changes:
        insights.append("Dependency changes may require environment updates")
        
    if 'infrastructure' in system_changes:
        insights.append("Infrastructure changes detected - deployment may be affected")
        
    # File-based insights
    py_files = [f for f in affected_files if f.endswith('.py')]
    if len(py_files) > 5:
        insights.append(f"Extensive Python code changes: {len(py_files)} files modified")
        
    agent_files = [f for f in affected_files if 'agent' in f.lower()]
    if agent_files:
        insights.append(f"Agent system modifications: {len(agent_files)} agent-related files changed")
    
    # Change type insights
    if change_type == 'feature':
        insights.append("New feature implementation - system capabilities expanded")
    elif change_type == 'refactor':
        insights.append("Code refactoring - internal structure improved without external changes")
    elif change_type == 'bugfix':
        insights.append("Bug resolution - system reliability improved")
        
    return insights


def _build_cross_references(cross_ref_suggestions: Dict[str, Any]) -> Dict[str, str]:
    """Build cross-references to other agents' work"""
    
    cross_references = {}
    
    if cross_ref_suggestions.get('status') == 'success':
        suggestions = cross_ref_suggestions.get('suggestions', [])
        
        for suggestion in suggestions:
            agent_role = suggestion.get('agent_role')
            agent_name = suggestion.get('agent_name')
            
            # Create reference based on agent type
            if agent_role == 'tourist_guide':
                cross_references['user_documentation'] = f"See user-facing documentation maintained by {agent_name}"
                
            elif agent_role == 'historian':
                cross_references['decision_history'] = f"See architectural decisions and evolution context by {agent_name}"
                
            # Include relevant files if any
            relevant_files = suggestion.get('relevant_files', [])
            if relevant_files:
                cross_references[f'{agent_role}_files'] = f"Related files: {', '.join(relevant_files[:3])}"
    
    return cross_references


def _enhance_system_updates_with_bedrock(updates: List[SystemDocumentationUpdate], system_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[SystemDocumentationUpdate]:
    """
    Enhance system documentation updates using Bedrock AI integration.
    
    Args:
        updates: List of system documentation updates to enhance
        system_analysis: System analysis results for context
        context: Additional context from orchestrator
        
    Returns:
        List of enhanced SystemDocumentationUpdate objects
    """
    if not updates:
        return updates
    
    enhanced_updates = []
    
    for update in updates:
        try:
            # Prepare context for Bedrock enhancement  
            enhancement_context = {
                'section_type': f'system_{update.section}',
                'target_audience': 'technical_architects',
                'change_type': system_analysis.get('system_changes', {}),
                'system_impact': update.priority,
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
                    
                    # Update the system documentation update with enhanced content
                    enhanced_update = SystemDocumentationUpdate(
                        section=update.section,
                        action=update.action,
                        content=enhanced_content,
                        reason=f"{update.reason} | Bedrock enhanced (quality: {quality_score:.2f})",
                        priority=update.priority
                    )
                    
                    enhanced_updates.append(enhanced_update)
                    
                    # Log improvements made
                    if improvements:
                        print(f"✓ Bedrock enhanced system {update.section}: {', '.join(improvements[:2])}")
                else:
                    # Fallback if JSON parsing failed
                    enhanced_updates.append(update)
            else:
                # Fallback to original content if Bedrock fails
                enhanced_updates.append(update)
                print(f"⚠ Bedrock system enhancement failed for {update.section}, using original content")
                
        except Exception as e:
            # Fallback to original content on any error
            enhanced_updates.append(update)
            print(f"⚠ Bedrock system enhancement error for {update.section}: {str(e)}")
    
    return enhanced_updates


def _generate_system_content_with_context_analysis(section: str, change_type: str, affected_files: List[str], 
                                        recommendations: List[str], system_analysis: Dict[str, Any]) -> str:
    """
    Generate system content using comprehensive analysis tools for meaningful documentation.
    
    This function integrates analysis tools for Building Inspector system documentation.
    """
    try:
        # Use the general content generation function with system-specific parameters
        from content_generation_tools import DocumentationFocus, CodeExample
        
        # Create a system-focused DocumentationFocus
        doc_focus = DocumentationFocus(
            primary_focus='architecture',
            affected_areas=['System', 'Architecture'],
            user_impact_level='medium',
            suggested_sections=[section]
        )
        
        # Create simple code examples from affected files
        code_examples = []
        for file in affected_files[:3]:  # Limit to 3 files
            if file.endswith('.py'):
                code_examples.append(CodeExample(
                    language='python',
                    code=f'# Changes in {file}',
                    description=f'System changes in {file}',
                    file_path=file,
                    change_type='modified'
                ))
        
        # Create a mock git analysis for system focus
        git_analysis = {
            'change_type': change_type,
            'affected_components': affected_files,
            'summary': f'System {change_type} changes',
            'diff': ''
        }
        
        # Use the context-rich content generation
        rich_content = generate_context_rich_content(
            section=section,
            git_analysis=git_analysis,
            file_changes=affected_files,
            code_examples=code_examples,
            doc_focus=doc_focus,
            change_type=change_type
        )
        
        # If rich content generation succeeds, return it
        if rich_content and len(rich_content) > 50:  # Ensure meaningful content
            return rich_content
        else:
            # Fallback to original system content generation
            return _generate_system_content_for_section(section, change_type, affected_files, recommendations)
            
    except Exception as e:
        # Fallback to original method on any error
        print(f"⚠ System content generation failed for {section}: {str(e)}")
        return _generate_system_content_for_section(section, change_type, affected_files, recommendations)