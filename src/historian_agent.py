"""
Historian Agent for CodeRipple

This agent focuses on the inner layer of documentation - "Why it BECAME this way".
Preserves the reasoning behind how the system evolved through different versions.
Updates based on append-only pattern - new decisions added, old ones preserved with version context.

Core Elements:
- Architectural Decision Records (ADRs): Major design decisions and their reasoning
- Problem Evolution: How problems and requirements changed over time
- Major Refactors: Significant code restructuring and why it was necessary
- Technology Migrations: Technology changes and migration rationale
- Failed Experiments: What was tried but didn't work, and lessons learned
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from strands import tool
from config import get_config, get_documentation_path
from webhook_parser import WebhookEvent
from agent_context_flow import register_agent_state, get_agent_state, suggest_cross_references
from bedrock_integration_tools import (
    enhance_content_with_bedrock,
    check_documentation_consistency,
    generate_dynamic_examples,
    analyze_content_gaps
)
from content_validation_tools import (
    validate_documentation_quality,
    enforce_quality_standards,
    validate_and_improve_content
)


@dataclass
class DecisionDocumentationUpdate:
    """Represents a decision documentation update"""
    section: str  # 'architecture_decisions', 'problem_evolution', 'refactoring_history', 'technology_migrations', 'failed_experiments'
    action: str   # 'create', 'append'
    content: str
    reason: str
    priority: int  # 1=high, 2=medium, 3=low
    decision_id: str  # Unique identifier for this decision


@dataclass
class HistorianResult:
    """Result of Historian analysis"""
    updates: List[DecisionDocumentationUpdate]
    summary: str
    decision_impact: str  # Description of the significance of this decision


@tool
def analyze_decision_significance(change_type: str, affected_files: List[str], commit_messages: List[str]) -> Dict[str, Any]:
    """
    Analyze how code changes represent significant decisions or learnings that should be preserved.
    
    Args:
        change_type: Type of change (feature, bugfix, etc.)
        affected_files: List of files that were changed
        commit_messages: List of commit messages for context
        
    Returns:
        Dictionary with decision significance analysis and documentation recommendations
    """
    
    # Analyze decision-level significance
    decision_changes = _identify_decision_changes(change_type, affected_files, commit_messages)
    decision_significance = _assess_decision_significance(change_type, decision_changes)
    doc_updates = _recommend_decision_documentation_updates(change_type, decision_changes, decision_significance)
    
    return {
        'decision_changes': decision_changes,
        'decision_significance': decision_significance,
        'documentation_updates': doc_updates,
        'priority_level': _calculate_decision_priority(change_type, decision_changes)
    }


@tool
def write_decision_documentation_file(file_path: str, content: str, action: str = "append") -> Dict[str, Any]:
    """
    Write or append to decision documentation files using configurable output directory.
    
    Args:
        file_path: Relative path within decisions directory (e.g., "architecture_decisions.md")
        content: Content to write/append
        action: "create" or "append" (Historian preserves history)
        
    Returns:
        Dictionary with operation status and details
    """
    try:
        config = get_config()
        # Ensure decisions directory exists within configured output directory
        decisions_dir = get_documentation_path("decisions")
        if not os.path.exists(decisions_dir):
            os.makedirs(decisions_dir)
        
        full_path = os.path.join(decisions_dir, file_path)
        
        # Ensure subdirectories exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Validate content quality before writing
        validation_result = enforce_quality_standards(
            content=content,
            file_path=full_path,
            min_quality_score=65.0,  # Medium threshold for decision docs
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
                'error': f"Decision content validation failed (score: {validation_result['quality_score']:.1f})",
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
            
        elif action == "append":
            # Historian always appends to preserve history
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write("\n\n" + content)
            operation = "appended to"
        
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
def read_existing_decision_documentation(file_path: str) -> Dict[str, Any]:
    """
    Read existing decision documentation file to check current content.
    
    Args:
        file_path: Relative path within decisions directory
        
    Returns:
        Dictionary with file content or error
    """
    try:
        full_path = get_documentation_path(os.path.join("decisions", file_path))
        
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


def historian_agent(webhook_event: WebhookEvent, git_analysis: Dict[str, Any], context: Dict[str, Any]) -> HistorianResult:
    """
    Historian Agent that preserves decision context and system evolution based on code changes.
    
    Args:
        webhook_event: Parsed webhook event data
        git_analysis: Analysis from git analysis tool
        context: Additional context from orchestrator
        
    Returns:
        HistorianResult with decision documentation updates
    """
    
    change_type = git_analysis.get('change_type', 'unknown')
    affected_files = git_analysis.get('affected_components', [])
    commit_messages = [commit.message for commit in webhook_event.commits]
    
    # Use the decision analysis tool
    decision_analysis = analyze_decision_significance(change_type, affected_files, commit_messages)
    
    # Generate documentation updates
    updates = _generate_decision_documentation_updates(decision_analysis, change_type, affected_files, webhook_event)
    
    # Enhance content with Bedrock for decision documentation
    enhanced_updates = _enhance_decision_updates_with_bedrock(updates, decision_analysis, context)
    updates = enhanced_updates if enhanced_updates else updates
    
    # Write documentation files
    write_results = _write_decision_documentation_files(updates, webhook_event.repository_name)
    
    # Create summary and decision impact assessment
    summary = _generate_decision_summary(updates, change_type, affected_files, write_results)
    decision_impact = _assess_overall_decision_impact(decision_analysis, change_type)
    
    return HistorianResult(
        updates=updates,
        summary=summary,
        decision_impact=decision_impact
    )


def _identify_decision_changes(change_type: str, affected_files: List[str], commit_messages: List[str]) -> Dict[str, Any]:
    """Identify which changes represent significant decisions or learnings"""
    
    decision_indicators = {
        'architectural_decisions': ['architecture', 'design', 'pattern', 'structure', 'framework'],
        'technology_migrations': ['migrate', 'upgrade', 'replace', 'switch', 'dependency', 'version'],
        'refactoring_decisions': ['refactor', 'restructure', 'reorganize', 'cleanup', 'simplify'],
        'problem_evolution': ['requirement', 'spec', 'change', 'update', 'modify', 'enhance'],
        'failed_experiments': ['revert', 'rollback', 'remove', 'disable', 'deprecated']
    }
    
    identified_changes = {}
    
    for category, indicators in decision_indicators.items():
        matches = []
        
        # Check files for structural patterns
        for file in affected_files:
            if category == 'architectural_decisions' and any(pattern in file.lower() for pattern in ['src/', 'lib/', 'core/', 'main']):
                matches.append(f"File: {file}")
            elif category == 'technology_migrations' and any(pattern in file.lower() for pattern in ['requirements', 'package.json', 'dockerfile', 'config']):
                matches.append(f"File: {file}")
        
        # Check commit messages for decision keywords
        for msg in commit_messages:
            if any(indicator in msg.lower() for indicator in indicators):
                matches.append(f"Commit: {msg[:50]}...")
        
        if matches:
            identified_changes[category] = matches
    
    return identified_changes


def _assess_decision_significance(change_type: str, decision_changes: Dict[str, Any]) -> Dict[str, str]:
    """Assess the significance of decisions that should be preserved"""
    
    significance_levels = {
        'architecture_decisions': 'none',
        'problem_evolution': 'none',
        'refactoring_history': 'none',
        'technology_migrations': 'none',
        'failed_experiments': 'none'
    }
    
    # Refactoring represents significant architectural decisions
    if change_type == 'refactor':
        significance_levels['architecture_decisions'] = 'high'
        significance_levels['refactoring_history'] = 'high'
    
    # Feature changes may represent problem evolution
    elif change_type == 'feature':
        significance_levels['problem_evolution'] = 'medium'
        if 'architectural_decisions' in decision_changes:
            significance_levels['architecture_decisions'] = 'medium'
    
    # Technology changes in dependencies
    if 'technology_migrations' in decision_changes:
        significance_levels['technology_migrations'] = 'high'
    
    # Failed experiments (reverts, rollbacks)
    if 'failed_experiments' in decision_changes:
        significance_levels['failed_experiments'] = 'high'
    
    # Major refactoring decisions
    if 'refactoring_decisions' in decision_changes:
        significance_levels['refactoring_history'] = 'high'
        significance_levels['architecture_decisions'] = 'medium'
    
    return significance_levels


def _recommend_decision_documentation_updates(change_type: str, decision_changes: Dict[str, Any], decision_significance: Dict[str, str]) -> List[str]:
    """Recommend specific decision documentation updates needed"""
    
    recommendations = []
    
    for section, significance_level in decision_significance.items():
        if significance_level == 'none':
            continue
            
        if section == 'architecture_decisions':
            if change_type == 'refactor':
                recommendations.append("Document architectural refactoring decision and rationale")
                recommendations.append("Record design patterns and structure changes")
            elif change_type == 'feature' and significance_level in ['high', 'medium']:
                recommendations.append("Record architectural implications of new feature")
        
        elif section == 'problem_evolution':
            if change_type == 'feature':
                recommendations.append("Document how requirements evolved to drive this change")
                recommendations.append("Record problem context and solution approach")
        
        elif section == 'refactoring_history':
            if change_type == 'refactor':
                recommendations.append("Document refactoring scope and motivation")
                recommendations.append("Record before/after state and lessons learned")
        
        elif section == 'technology_migrations':
            if 'technology_migrations' in decision_changes:
                recommendations.append("Document technology migration decision and timeline")
                recommendations.append("Record migration challenges and solutions")
        
        elif section == 'failed_experiments':
            if 'failed_experiments' in decision_changes:
                recommendations.append("Document what was tried and why it failed")
                recommendations.append("Record lessons learned and alternative approaches")
    
    return recommendations


def _generate_decision_documentation_updates(decision_analysis: Dict[str, Any], change_type: str, affected_files: List[str], webhook_event: WebhookEvent) -> List[DecisionDocumentationUpdate]:
    """Generate specific decision documentation updates based on analysis"""
    
    updates = []
    doc_recommendations = decision_analysis.get('documentation_updates', [])
    priority_level = decision_analysis.get('priority_level', 3)
    
    # Group recommendations by section
    section_updates = {
        'architecture_decisions': [],
        'problem_evolution': [],
        'refactoring_history': [],
        'technology_migrations': [],
        'failed_experiments': []
    }
    
    for rec in doc_recommendations:
        if any(keyword in rec.lower() for keyword in ['architectural', 'design', 'pattern', 'structure']):
            section_updates['architecture_decisions'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['requirement', 'problem', 'evolution', 'context']):
            section_updates['problem_evolution'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['refactor', 'restructure', 'cleanup']):
            section_updates['refactoring_history'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['migration', 'technology', 'upgrade', 'dependency']):
            section_updates['technology_migrations'].append(rec)
        elif any(keyword in rec.lower() for keyword in ['failed', 'experiment', 'tried', 'lesson']):
            section_updates['failed_experiments'].append(rec)
    
    # Create DecisionDocumentationUpdate objects
    for section, recommendations in section_updates.items():
        if recommendations:
            # Generate unique decision ID
            from datetime import datetime
            decision_id = f"{change_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            content = _generate_decision_content_for_section(section, change_type, affected_files, recommendations, webhook_event, decision_id)
            
            # Historian always appends to preserve history
            updates.append(DecisionDocumentationUpdate(
                section=section,
                action='append',
                content=content,
                reason=f"{change_type} represents significant {section.replace('_', ' ')}",
                priority=priority_level,
                decision_id=decision_id
            ))
    
    return updates


def _write_decision_documentation_files(updates: List[DecisionDocumentationUpdate], repository_name: str) -> Dict[str, Any]:
    """Write decision documentation updates to files in coderipple/decisions directory"""
    write_results = {}
    
    for update in updates:
        file_name = f"{update.section}.md"
        
        # Check if file exists to determine action
        existing_doc = read_existing_decision_documentation(file_name)
        
        if existing_doc['status'] == 'not_found':
            # Create new file with header
            content = _create_decision_document_with_header(update, repository_name)
            action = "create"
        else:
            # Historian always appends to preserve history
            content = update.content
            action = "append"
        
        # Write the file
        result = write_decision_documentation_file(file_name, content, action)
        write_results[update.section] = result
        
        if result['status'] == 'success':
            print(f"✓ {result['operation'].title()} {result['file_path']}")
        else:
            print(f"✗ Failed to write {file_name}: {result.get('error', 'Unknown error')}")
    
    return write_results


def _create_decision_document_with_header(update: DecisionDocumentationUpdate, repository_name: str) -> str:
    """Create a new decision document with proper header and content"""
    section_titles = {
        'architecture_decisions': 'Architectural Decision Records (ADRs)',
        'problem_evolution': 'Problem Evolution',
        'refactoring_history': 'Major Refactoring History',
        'technology_migrations': 'Technology Migrations',
        'failed_experiments': 'Failed Experiments & Lessons Learned'
    }
    
    title = section_titles.get(update.section, update.section.replace('_', ' ').title())
    
    header = f"""# {title}

*This document is automatically maintained by CodeRipple Historian Agent*  
*Repository: {repository_name}*  
*Last updated: {_get_current_timestamp()}*  
*All decisions preserved with historical context*

---

"""
    
    return header + update.content


def _get_current_timestamp() -> str:
    """Get current timestamp for documentation headers"""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _generate_decision_content_for_section(section: str, change_type: str, affected_files: List[str], recommendations: List[str], webhook_event: WebhookEvent, decision_id: str) -> str:
    """Generate actual content for decision documentation sections"""
    
    timestamp = _get_current_timestamp()
    commit_hash = webhook_event.commits[0].id[:8] if webhook_event.commits else "unknown"
    
    if section == 'architecture_decisions':
        return f"""## ADR-{decision_id}: {change_type.title()} Architectural Decision

**Date**: {timestamp}  
**Status**: Accepted  
**Commit**: {commit_hash}  
**Author**: {webhook_event.commits[0].author if webhook_event.commits else 'Unknown'}

### Context
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Decision
Implemented {change_type} changes affecting the following components:
- Files modified: {', '.join(affected_files[:5])}{'...' if len(affected_files) > 5 else ''}

### Consequences
- **Positive**: Enhanced system architecture and maintainability
- **Negative**: Requires documentation and potential learning curve
- **Neutral**: Standard evolution of system architecture

### Related Decisions
- Links to related ADRs will be added as system evolves
"""
    
    elif section == 'problem_evolution':
        return f"""## Problem Evolution Entry - {timestamp}

**Change Type**: {change_type}  
**Commit**: {commit_hash}  
**Affected Files**: {len(affected_files)} files

### Problem Context
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Solution Approach
The {change_type} addresses evolving requirements by:
- Modifying core functionality in: {', '.join(affected_files[:3])}
- Implementing new patterns and approaches
- Adapting to changing user needs and technical constraints

### Requirements Evolution
- **Previous State**: System met baseline requirements
- **New Requirements**: Enhanced functionality and capabilities
- **Future Considerations**: Continued evolution expected based on feedback

### Impact Assessment
- User experience improvements
- Technical debt reduction
- System capability expansion
"""
    
    elif section == 'refactoring_history':
        return f"""## Major Refactoring - {timestamp}

**Refactoring ID**: REFACTOR-{decision_id}  
**Scope**: {change_type} refactoring  
**Commit**: {commit_hash}  
**Files Affected**: {len(affected_files)}

### Motivation
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Changes Made
- **Modified Components**: {', '.join(affected_files[:5])}
- **Refactoring Type**: {change_type} improvements
- **Complexity**: {len(affected_files)} files affected

### Before/After
- **Before**: Legacy structure with technical debt
- **After**: Improved structure with better maintainability
- **Migration**: Gradual transition with backward compatibility

### Lessons Learned
- Systematic refactoring reduces complexity
- Incremental changes minimize risk
- Documentation crucial for team understanding
- Testing ensures functionality preservation
"""
    
    elif section == 'technology_migrations':
        return f"""## Technology Migration - {timestamp}

**Migration ID**: TECH-{decision_id}  
**Technology**: Dependency and stack updates  
**Commit**: {commit_hash}

### Migration Details
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Technology Changes
- **Components Updated**: {', '.join(affected_files)}
- **Migration Type**: {change_type} technology update
- **Compatibility**: Maintained backward compatibility where possible

### Migration Timeline
- **Planning**: Analysis of dependencies and impact
- **Implementation**: Gradual rollout with testing
- **Validation**: Comprehensive testing and monitoring
- **Completion**: Full migration with documentation update

### Challenges & Solutions
- **Dependencies**: Updated to compatible versions
- **Testing**: Comprehensive test suite execution
- **Documentation**: Updated to reflect new technologies
- **Team Training**: Knowledge transfer for new technologies
"""
    
    elif section == 'failed_experiments':
        return f"""## Failed Experiment - {timestamp}

**Experiment ID**: EXP-{decision_id}  
**Type**: {change_type} experiment  
**Commit**: {commit_hash}  
**Status**: Failed/Reverted

### What Was Tried
{chr(10).join(f"- {rec}" for rec in recommendations)}

### Why It Failed
- Technical limitations discovered during implementation
- Performance impact exceeded acceptable thresholds
- Complexity introduced without proportional benefits
- User experience degradation identified

### Lessons Learned
- **Technical**: Implementation approach needs refinement
- **Process**: Earlier validation could prevent similar issues
- **Architecture**: Current design patterns more suitable
- **Team**: Knowledge gained for future experiments

### Alternative Approaches
- Consider incremental implementation
- Evaluate different technical approaches
- Gather more user feedback before major changes
- Prototype in isolated environment first

### Future Considerations
- Revisit when technology landscape changes
- Consider user feedback and requirements evolution
- Evaluate with improved technical capabilities
- Document for future reference and learning
"""
    
    return f"## {section.replace('_', ' ').title()} - {timestamp}\n\nDecision context preserved for {change_type} changes."


def _calculate_decision_priority(change_type: str, decision_changes: Dict[str, Any]) -> int:
    """Calculate priority level for decision documentation updates"""
    
    if change_type == 'refactor' and ('architectural_decisions' in decision_changes or 'refactoring_decisions' in decision_changes):
        return 1  # High priority for architectural decisions
    elif 'technology_migrations' in decision_changes:
        return 1  # High priority for technology changes
    elif 'failed_experiments' in decision_changes:
        return 2  # Medium priority for learning from failures
    elif change_type == 'feature' and decision_changes:
        return 2  # Medium priority for feature decisions
    else:
        return 3  # Low priority


def _generate_decision_summary(updates: List[DecisionDocumentationUpdate], change_type: str, affected_files: List[str], write_results: Dict[str, Any] = None) -> str:
    """Generate summary of Historian analysis"""
    
    if not updates:
        return f"No significant decisions to preserve for {change_type} changes."
    
    sections = list(set(update.section for update in updates))
    high_priority = sum(1 for update in updates if update.priority == 1)
    
    summary = f"Historian preserved {len(updates)} significant decisions for {change_type} changes. "
    summary += f"Decision types: {', '.join(sections)}. "
    
    if high_priority > 0:
        summary += f"{high_priority} high-priority decisions recorded. "
    else:
        summary += "All decisions are medium/low priority. "
    
    # Add file writing results
    if write_results:
        successful_writes = sum(1 for result in write_results.values() if result.get('status') == 'success')
        total_writes = len(write_results)
        summary += f"Decision docs written: {successful_writes}/{total_writes} successful."
    
    return summary


def _assess_overall_decision_impact(decision_analysis: Dict[str, Any], change_type: str) -> str:
    """Assess overall significance of decisions being preserved"""
    
    priority_level = decision_analysis.get('priority_level', 3)
    decision_changes = decision_analysis.get('decision_changes', {})
    
    if priority_level == 1:
        return f"High significance: {change_type} represents major architectural or technological decisions that will impact future development."
    elif priority_level == 2:
        return f"Medium significance: {change_type} contains decisions worth preserving for future reference and learning."
    else:
        return f"Low significance: {change_type} decisions documented for completeness but minimal long-term impact expected."


def _enhance_decision_updates_with_bedrock(updates: List[DecisionDocumentationUpdate], decision_analysis: Dict[str, Any], context: Dict[str, Any]) -> List[DecisionDocumentationUpdate]:
    """
    Enhance decision documentation updates using Bedrock AI integration.
    
    Args:
        updates: List of decision documentation updates to enhance
        decision_analysis: Decision analysis results for context
        context: Additional context from orchestrator
        
    Returns:
        List of enhanced DecisionDocumentationUpdate objects
    """
    if not updates:
        return updates
    
    enhanced_updates = []
    
    for update in updates:
        try:
            # Prepare context for Bedrock enhancement
            enhancement_context = {
                'section_type': f'decision_{update.section}',
                'target_audience': 'future_developers',
                'decision_context': decision_analysis.get('decision_changes', {}),
                'historical_importance': update.priority,
                'repository_context': context.get('repository_name', 'Unknown'),
                'decision_id': update.decision_id
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
                    
                    # Update the decision documentation update with enhanced content
                    enhanced_update = DecisionDocumentationUpdate(
                        section=update.section,
                        action=update.action,
                        content=enhanced_content,
                        reason=f"{update.reason} | Bedrock enhanced (quality: {quality_score:.2f})",
                        priority=update.priority,
                        decision_id=update.decision_id
                    )
                    
                    enhanced_updates.append(enhanced_update)
                    
                    # Log improvements made
                    if improvements:
                        print(f"✓ Bedrock enhanced decision {update.section}: {', '.join(improvements[:2])}")
                else:
                    # Fallback if JSON parsing failed
                    enhanced_updates.append(update)
            else:
                # Fallback to original content if Bedrock fails
                enhanced_updates.append(update)
                print(f"⚠ Bedrock decision enhancement failed for {update.section}, using original content")
                
        except Exception as e:
            # Fallback to original content on any error
            enhanced_updates.append(update)
            print(f"⚠ Bedrock decision enhancement error for {update.section}: {str(e)}")
    
    return enhanced_updates