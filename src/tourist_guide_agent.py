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
    
    # Create summary and user impact assessment
    summary = _generate_summary(updates, change_type, affected_files)
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


def _generate_summary(updates: List[DocumentationUpdate], change_type: str, affected_files: List[str]) -> str:
    """Generate summary of Tourist Guide analysis"""
    
    if not updates:
        return f"No user-facing documentation updates needed for {change_type} changes."
    
    sections = list(set(update.section for update in updates))
    high_priority = sum(1 for update in updates if update.priority == 1)
    
    summary = f"Tourist Guide recommends {len(updates)} documentation updates for {change_type} changes. "
    summary += f"Affected sections: {', '.join(sections)}. "
    
    if high_priority > 0:
        summary += f"{high_priority} high-priority updates identified."
    else:
        summary += "All updates are medium/low priority."
    
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


# Test function
def test_tourist_guide():
    """Test the Tourist Guide agent with sample data"""
    
    from webhook_parser import CommitInfo, WebhookEvent
    from datetime import datetime
    
    # Create sample webhook event
    sample_commit = CommitInfo(
        id="abc123",
        message="Add new CLI command for user authentication",
        author="Developer",
        timestamp=datetime.now(),
        added_files=["src/cli.py", "README.md"],
        modified_files=["src/main.py"],
        removed_files=[],
        url="https://github.com/user/repo/commit/abc123"
    )
    
    sample_event = WebhookEvent(
        event_type="push",
        repository_name="user/repo",
        repository_url="https://github.com/user/repo",
        branch="main",
        commits=[sample_commit],
        before_sha="before123",
        after_sha="abc123"
    )
    
    sample_git_analysis = {
        'change_type': 'feature',
        'affected_components': ['src/cli.py', 'README.md', 'src/main.py'],
        'confidence': 0.8,
        'summary': 'Detected feature changes in 3 files'
    }
    
    sample_context = {
        'change_type': 'feature',
        'affected_files': ['src/cli.py', 'README.md', 'src/main.py'],
        'focus': 'user_workflows'
    }
    
    print("Testing Tourist Guide Agent...")
    print("=" * 50)
    
    result = tourist_guide_agent(sample_event, sample_git_analysis, sample_context)
    
    print(f"Summary: {result.summary}")
    print(f"User Impact: {result.user_impact}")
    print(f"Documentation Updates ({len(result.updates)}):")
    
    for i, update in enumerate(result.updates, 1):
        print(f"\n{i}. {update.section} ({update.action}) - Priority {update.priority}")
        print(f"   Reason: {update.reason}")
        print(f"   Content Preview: {update.content[:100]}...")


if __name__ == "__main__":
    test_tourist_guide()