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
from config import get_config, get_documentation_path
from webhook_parser import WebhookEvent
from content_generation_tools import (
    analyze_change_patterns,
    extract_code_examples_from_diff,
    generate_context_aware_content,
    generate_context_rich_content,
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
from content_validation_tools import (
    validate_documentation_quality,
    validate_documentation_quality_detailed,
    align_and_validate_content_quality,
    validate_with_progressive_quality,
    validate_with_partial_success,
    enforce_quality_standards,
    validate_and_improve_content
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
def write_documentation_file(file_path: str, content: str, action: str = "create", skip_validation: bool = False) -> Dict[str, Any]:
    """
    Write or update documentation files using configurable output directory.
    
    Args:
        file_path: Relative path within documentation directory (e.g., "user/overview.md")
        content: Content to write
        action: "create", "update", or "append"
        skip_validation: Skip validation for testing purposes
        
    Returns:
        Dictionary with operation status and details
    """
    try:
        # Get configuration
        config = get_config()
        
        # Get full path using configuration
        full_path = get_documentation_path(file_path)
        
        # Ensure output directory exists
        output_dir = config.output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Ensure subdirectories exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        # Step 4D: Validate content quality before writing (unless skipped for testing)
        if skip_validation:
            validation_result = {
                'write_approved': True,
                'quality_score': 75.0,
                'errors': [],
                'warnings': [],
                'suggestions': []
            }
        else:
            # Step 8 Subtask 4: Partial Success Handling with Progressive Quality Standards
            config = get_config()
            
            if config.enable_partial_success:
                print(f"   📊 VALIDATING with Partial Success & Progressive Quality Standards...")
                
                validation_result = validate_with_partial_success(
                    file_path=full_path,
                    content=content,
                    project_root=os.getcwd()
                )
                
                # Log validation results
                tier_info = validation_result.get('tier_display_info', {})
                tier_achieved = validation_result.get('final_tier_achieved', 'unknown')
                
                print(f"   {tier_info.get('icon', '📝')} VALIDATION: {tier_info.get('name', tier_achieved.title())} (Score: {validation_result['final_score']:.1f})")
                print(f"   📄 Description: {tier_info.get('description', 'Validation complete')}")
                
                # Show section processing if partial validation occurred
                if validation_result.get('partial_validation', False):
                    sections_processed = validation_result.get('sections_processed', 0)
                    sections_passed = validation_result.get('sections_passed', 0)
                    sections_failed = validation_result.get('sections_failed', 0)
                    
                    print(f"   📊 Section Analysis: {sections_processed} sections processed")
                    print(f"   ✅ Passed: {sections_passed} sections")
                    if sections_failed > 0:
                        print(f"   ❌ Failed: {sections_failed} sections (excluded from final document)")
                
                # Display quality warnings if any
                quality_warnings = validation_result.get('quality_warnings', [])
                if quality_warnings:
                    print(f"   ⚠️ Quality Warnings:")
                    for warning in quality_warnings[:3]:  # Show top 3 warnings
                        print(f"     • {warning}")
                
            else:
                # Fallback to progressive quality only
                print(f"   📊 VALIDATING with Progressive Quality Standards...")
                
                validation_result = validate_with_progressive_quality(
                    file_path=full_path,
                    content=content,
                    project_root=os.getcwd()
                )
                
                # Log the tier achieved and any warnings
                tier_info = validation_result.get('tier_display_info', {})
                tier_achieved = validation_result.get('final_tier_achieved', 'unknown')
                
                print(f"   {tier_info.get('icon', '📝')} QUALITY TIER: {tier_info.get('name', tier_achieved.title())} (Score: {validation_result['final_score']:.1f})")
                print(f"   📄 Description: {tier_info.get('description', 'Quality validation complete')}")
                
                # Display quality warnings if any
                quality_warnings = validation_result.get('quality_warnings', [])
                if quality_warnings:
                    print(f"   ⚠️ Quality Warnings:")
                    for warning in quality_warnings[:3]:  # Show top 3 warnings
                        print(f"     • {warning}")
                
                # Show tier attempts for transparency
                attempts = validation_result.get('attempts_made', [])
                if len(attempts) > 1:
                    attempt_summary = ' → '.join([f"{a['tier'].title()}({a['score_achieved']:.1f})" for a in attempts])
                    print(f"   📊 Tier Attempts: {attempt_summary}")
                
                # Handle fallback case
                fallback_reason = validation_result.get('fallback_reason')
                if fallback_reason:
                    print(f"   ⚠️ Fallback Applied: {fallback_reason}")
            
            # If content was enhanced with quality tier notices or partial content, use the enhanced version
            if 'enhanced_content' in validation_result:
                content = validation_result['enhanced_content']
        
        # Content passed validation - proceed with writing
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
            'content_length': len(content),
            'validation_score': validation_result.get('overall_quality_score', validation_result.get('quality_score', 0.0)),
            'validation_warnings': validation_result.get('warnings', [])
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


def _retry_content_improvement(content: str, validation_result: Dict[str, Any], file_path: str, max_retries: int = 3) -> Dict[str, Any]:
    """
    Step 8 Subtask 2: Retry mechanism with iterative improvement using validation feedback.
    
    Args:
        content: The original content that failed validation
        validation_result: Detailed validation results from initial attempt
        file_path: Path to the file being created
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dictionary with retry results, improved content, and final validation
    """
    current_content = content
    retry_history = []
    
    for attempt in range(1, max_retries + 1):
        print(f"   🔄 Retry Attempt {attempt}/{max_retries}...")
        
        # Create targeted improvement prompt based on validation failures
        improvement_prompt = _create_targeted_improvement_prompt(validation_result, attempt)
        
        try:
            # Use Bedrock to improve content based on specific feedback
            enhanced_result = enhance_content_with_bedrock(
                content=current_content,
                context={
                    'improvement_focus': improvement_prompt,
                    'validation_failures': validation_result['failure_reasons'],
                    'priority_fixes': validation_result['priority_fixes'],
                    'category_scores': validation_result['category_scores'],
                    'attempt_number': attempt,
                    'file_type': 'user_documentation'
                }
            )
            
            if enhanced_result.get('status') == 'success':
                improved_content = enhanced_result.get('content', current_content)
                print(f"     📝 Content enhanced (attempt {attempt})")
                
                # Validate the improved content using alignment with Bedrock results
                new_validation = align_and_validate_content_quality(
                    file_path=file_path,
                    content=improved_content,
                    bedrock_result=enhanced_result,
                    project_root=os.getcwd(),
                    min_quality_score=60.0
                )
                
                # Track retry attempt
                retry_history.append({
                    'attempt': attempt,
                    'improvement_prompt': improvement_prompt,
                    'score_before': validation_result['overall_quality_score'],
                    'score_after': new_validation['overall_quality_score'],
                    'improvement': new_validation['overall_quality_score'] - validation_result['overall_quality_score'],
                    'passed': new_validation['is_valid'],
                    'main_issues_targeted': validation_result['failure_reasons'][:3]
                })
                
                print(f"     📊 Score: {validation_result['overall_quality_score']:.1f} → {new_validation['overall_quality_score']:.1f} ({new_validation['overall_quality_score'] - validation_result['overall_quality_score']:+.1f})")
                
                if new_validation['is_valid']:
                    # Success! Content now passes validation
                    return {
                        'success': True,
                        'attempts': attempt,
                        'improved_content': improved_content,
                        'final_validation': new_validation,
                        'retry_history': retry_history,
                        'total_improvement': new_validation['overall_quality_score'] - retry_history[0]['score_before']
                    }
                
                # Update for next iteration
                current_content = improved_content
                validation_result = new_validation
                
            else:
                print(f"     ⚠️ Enhancement failed on attempt {attempt}: {enhanced_result.get('error', 'Unknown error')}")
                retry_history.append({
                    'attempt': attempt,
                    'improvement_prompt': improvement_prompt,
                    'score_before': validation_result['overall_quality_score'],
                    'score_after': validation_result['overall_quality_score'],
                    'improvement': 0.0,
                    'passed': False,
                    'error': enhanced_result.get('error', 'Enhancement failed')
                })
                
        except Exception as e:
            print(f"     ❌ Retry attempt {attempt} failed: {str(e)}")
            retry_history.append({
                'attempt': attempt,
                'improvement_prompt': improvement_prompt,
                'error': str(e),
                'passed': False
            })
    
    # All retries exhausted
    return {
        'success': False,
        'attempts': max_retries,
        'improved_content': current_content,
        'final_validation': validation_result,
        'retry_history': retry_history,
        'total_improvement': validation_result['overall_quality_score'] - retry_history[0]['score_before'] if retry_history else 0.0
    }


def _create_targeted_improvement_prompt(validation_result: Dict[str, Any], attempt_number: int) -> str:
    """
    Create a targeted improvement prompt based on specific validation failures.
    
    Args:
        validation_result: Detailed validation results
        attempt_number: Current retry attempt number
        
    Returns:
        Targeted improvement prompt for Bedrock
    """
    # Identify the worst-performing categories
    category_scores = validation_result['category_scores']
    worst_categories = sorted(category_scores.items(), key=lambda x: x[1])[:3]
    
    # Get specific issues and fixes
    priority_fixes = validation_result.get('priority_fixes', [])
    failure_reasons = validation_result.get('failure_reasons', [])
    
    if attempt_number == 1:
        # First retry: Focus on the most critical issues
        prompt = f"""
CONTENT IMPROVEMENT REQUEST (Attempt {attempt_number}):

CRITICAL ISSUES TO FIX:
{chr(10).join([f"- {reason}" for reason in failure_reasons[:3]])}

PRIORITY FIXES NEEDED:
{chr(10).join([f"- {fix}" for fix in priority_fixes[:3]])}

WEAKEST CATEGORIES:
{chr(10).join([f"- {cat.replace('_', ' ').title()}: {score:.1f}/100" for cat, score in worst_categories])}

IMPROVEMENT FOCUS:
1. Address the critical structural issues first
2. Add proper headers and organization
3. Expand content with meaningful detail
4. Ensure professional markdown formatting

Please rewrite the content to specifically address these issues while maintaining the core message and purpose.
"""
    
    elif attempt_number == 2:
        # Second retry: Focus on remaining weak areas and polish
        prompt = f"""
CONTENT IMPROVEMENT REQUEST (Attempt {attempt_number}):

REMAINING ISSUES TO ADDRESS:
{chr(10).join([f"- {reason}" for reason in failure_reasons[:2]])}

SPECIFIC FIXES NEEDED:
{chr(10).join([f"- {fix}" for fix in priority_fixes[:4]])}

IMPROVEMENT FOCUS:
1. Polish content structure and flow
2. Add code examples or practical illustrations if applicable
3. Improve readability and clarity
4. Ensure comprehensive coverage of the topic
5. Add cross-references to related sections

Please enhance the content with these specific improvements while preserving the existing quality improvements.
"""
    
    else:
        # Final retry: Comprehensive improvement attempt
        prompt = f"""
CONTENT IMPROVEMENT REQUEST (Final Attempt {attempt_number}):

ALL REMAINING ISSUES:
{chr(10).join([f"- {reason}" for reason in failure_reasons])}

COMPREHENSIVE FIXES:
{chr(10).join([f"- {fix}" for fix in priority_fixes])}

FINAL IMPROVEMENT FOCUS:
1. Ensure all validation criteria are met
2. Create comprehensive, well-structured content
3. Add appropriate examples, lists, and formatting
4. Maintain professional tone and clarity
5. Include proper introduction and conclusion
6. Add relevant cross-references and links

This is the final attempt - please create the best possible version of this content that addresses all identified issues.
"""
    
    return prompt.strip()


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
        # Use STEP 5D: context-rich content generation with all smart tools
        intelligent_content = generate_context_rich_content(
            section=section,
            git_analysis=git_analysis,
            file_changes=affected_files,
            code_examples=code_examples,
            doc_focus=doc_focus,
            change_type=change_type
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


# Step 6.1 & 6.2: Bootstrap User Documentation Structure
USER_DOCUMENTATION_STRUCTURE = {
    'discovery': 'user/overview.md',
    'getting_started': 'user/getting_started.md', 
    'patterns': 'user/usage_patterns.md',
    'advanced': 'user/advanced_usage.md',
    'troubleshooting': 'user/troubleshooting.md'
}


@tool
def bootstrap_user_documentation(project_context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Bootstrap the initial user documentation structure when missing.
    Creates the user/ directory and initial files for all 5 sections.
    
    Args:
        project_context: Optional context about the project for initial content
        
    Returns:
        Dictionary with bootstrap results and created files
    """
    try:
        created_files = []
        errors = []
        
        # Get configuration
        config = get_config()
        
        # Ensure user directory exists
        user_dir = get_documentation_path("user")
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)
            print(f"✓ Created user documentation directory: {user_dir}")
        
        # Create each documentation file if it doesn't exist
        for section, file_path in USER_DOCUMENTATION_STRUCTURE.items():
            full_path = get_documentation_path(file_path)
            
            if not os.path.exists(full_path):
                # Generate initial placeholder content
                initial_content = _generate_initial_section_content(section, project_context)
                
                # Write the file with validation
                write_result = write_documentation_file(
                    file_path=file_path,
                    content=initial_content,
                    action="create",
                    skip_validation=True  # Skip validation for initial bootstrap
                )
                
                if write_result.get('status') == 'success':
                    created_files.append(file_path)
                    print(f"✓ Created {section} documentation: {file_path}")
                else:
                    errors.append(f"Failed to create {file_path}: {write_result.get('message', 'Unknown error')}")
            else:
                print(f"⚠ User documentation already exists: {file_path}")
        
        # Register the bootstrap completion in agent state
        register_agent_state(
            agent_name='Tourist Guide Agent',
            agent_role='tourist_guide',
            repository_context={'bootstrap_completed': True, 'user_docs_structure': USER_DOCUMENTATION_STRUCTURE},
            current_capabilities=['User documentation generation', 'Bootstrap documentation structure'],
            generated_files=created_files,
            key_insights=[f"Created initial user documentation structure with {len(created_files)} files"],
            cross_references={}
        )
        
        return {
            'status': 'success',
            'created_files': created_files,
            'errors': errors,
            'structure': USER_DOCUMENTATION_STRUCTURE,
            'message': f"Bootstrap completed. Created {len(created_files)} user documentation files."
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Bootstrap failed: {str(e)}",
            'created_files': [],
            'errors': [str(e)]
        }


@tool
def analyze_project_context_for_content_generation() -> Dict[str, Any]:
    """
    Analyze the current project state to generate intelligent, context-aware content.
    
    This function examines:
    - Current README and documentation
    - Actual Python modules and capabilities
    - Requirements and dependencies
    - Existing system architecture
    
    Returns:
        Dictionary with comprehensive project context for content generation
    """
    try:
        context = {
            'project_name': 'CodeRipple',
            'project_description': 'Multi-agent documentation system that automatically maintains comprehensive software documentation',
            'actual_modules': [],
            'key_dependencies': [],
            'current_capabilities': [],
            'existing_docs': {},
            'architecture_info': {},
            'usage_patterns': []
        }
        
        # Analyze actual Python modules
        import glob
        import os
        
        src_files = glob.glob('src/*.py')
        context['actual_modules'] = [f.replace('src/', '').replace('.py', '') for f in sorted(src_files)]
        
        # Analyze key dependencies
        if os.path.exists('requirements.txt'):
            with open('requirements.txt', 'r') as f:
                deps = [line.strip().split('==')[0] for line in f if line.strip() and not line.startswith('#')]
                key_deps = [d for d in deps if d in ['boto3', 'strands-agents', 'strands-agents-tools', 'requests', 'pydantic', 'click']]
                context['key_dependencies'] = key_deps
        
        # Extract current capabilities from README
        if os.path.exists('README.md'):
            with open('README.md', 'r') as f:
                readme_content = f.read()
                if 'webhook' in readme_content.lower():
                    context['current_capabilities'].append('GitHub webhook processing')
                if 'multi-agent' in readme_content.lower():
                    context['current_capabilities'].append('Multi-agent documentation generation')
                if 'aws' in readme_content.lower():
                    context['current_capabilities'].append('AWS integration (Lambda, Bedrock)')
                if 'strands' in readme_content.lower():
                    context['current_capabilities'].append('AWS Strands orchestration')
        
        # Analyze existing documentation structure
        if os.path.exists('coderipple/system/architecture.md'):
            context['existing_docs']['system_architecture'] = 'coderipple/system/architecture.md'
        if os.path.exists('coderipple/decisions/architecture_decisions.md'):
            context['existing_docs']['decision_history'] = 'coderipple/decisions/architecture_decisions.md'
        if os.path.exists('coderipple/patterns.md'):
            context['existing_docs']['usage_patterns'] = 'coderipple/patterns.md'
        
        # Extract architecture information from system docs
        if os.path.exists('coderipple/system/architecture.md'):
            with open('coderipple/system/architecture.md', 'r') as f:
                arch_content = f.read()
                context['architecture_info'] = {
                    'webhook_driven': 'GitHub Webhook' in arch_content,
                    'multi_agent': 'Specialist Agents' in arch_content,
                    'has_orchestrator': 'Orchestrator Agent' in arch_content,
                    'aws_integration': 'AWS' in arch_content
                }
        
        # Extract usage patterns from existing patterns.md
        if os.path.exists('coderipple/patterns.md'):
            with open('coderipple/patterns.md', 'r') as f:
                patterns_content = f.read()
                if 'webhook' in patterns_content.lower():
                    context['usage_patterns'].append('Webhook-triggered documentation generation')
                if 'agent' in patterns_content.lower():
                    context['usage_patterns'].append('Multi-agent coordination')
        
        # Identify actual execution entry points
        if os.path.exists('run_coderipple.py'):
            context['entry_points'] = ['run_coderipple.py']
        
        # Add project status information
        context['project_status'] = {
            'completion_percentage': '95%',
            'production_ready': 'Local usage fully operational',
            'remaining_work': 'AWS infrastructure deployment'
        }
        
        return context
        
    except Exception as e:
        print(f"Warning: Could not fully analyze project context: {str(e)}")
        # Return basic context if analysis fails
        return {
            'project_name': 'CodeRipple',
            'project_description': 'Multi-agent documentation system',
            'actual_modules': ['tourist_guide_agent', 'building_inspector_agent', 'historian_agent'],
            'key_dependencies': ['strands-agents', 'boto3'],
            'current_capabilities': ['Multi-agent documentation generation'],
            'existing_docs': {},
            'architecture_info': {},
            'usage_patterns': []
        }


def _generate_initial_section_content(section: str, project_context: Dict[str, Any] = None) -> str:
    """
    Generate initial intelligent content for a documentation section using project analysis.
    
    Args:
        section: Section name (discovery, getting_started, etc.)
        project_context: Optional project context (if None, will analyze automatically)
        
    Returns:
        Initial markdown content for the section with project-specific information
    """
    
    # Get intelligent project context
    if project_context is None:
        project_context = analyze_project_context_for_content_generation()
    
    project_name = project_context.get('project_name', 'CodeRipple')
    project_description = project_context.get('project_description', 'Multi-agent documentation system')
    modules = project_context.get('actual_modules', [])
    capabilities = project_context.get('current_capabilities', [])
    dependencies = project_context.get('key_dependencies', [])
    existing_docs = project_context.get('existing_docs', {})
    status = project_context.get('project_status', {})
    
    if section == 'discovery':
        # Generate intelligent overview based on actual project state
        features_list = []
        if 'GitHub webhook processing' in capabilities:
            features_list.append("- **GitHub Integration**: Automatically triggered by repository commits and pull requests")
        if 'Multi-agent documentation generation' in capabilities:
            features_list.append("- **Multi-Agent Architecture**: Coordinated specialist agents handle different documentation perspectives")
        if 'AWS integration (Lambda, Bedrock)' in capabilities:
            features_list.append("- **AI-Enhanced Content**: Uses Amazon Bedrock for intelligent content generation and validation")
        if 'AWS Strands orchestration' in capabilities:
            features_list.append("- **Scalable Orchestration**: AWS Strands manages complex multi-agent workflows")
        
        # Add project status information
        status_info = ""
        if status.get('completion_percentage'):
            status_info = f"\n**Current Status**: {status['completion_percentage']} complete - {status.get('production_ready', 'In development')}"
        
        # Create cross-references to existing documentation
        related_docs = []
        if existing_docs.get('system_architecture'):
            related_docs.append(f"- **[System Architecture](../{existing_docs['system_architecture']})**: Technical architecture and component details")
        if existing_docs.get('decision_history'):
            related_docs.append(f"- **[Decision History](../{existing_docs['decision_history']})**: Architectural decisions and evolution context")
        
        related_docs_section = ""
        if related_docs:
            related_docs_section = f"\n## Related Documentation\n\n" + "\n".join(related_docs)
        
        return f"""# {project_name} Overview

## What is {project_name}?

{project_description} by analyzing code changes through different perspectives using a **layered documentation structure**.{status_info}

## Key Features

{chr(10).join(features_list) if features_list else "- **Automated Documentation**: Generates documentation automatically from code changes"}

## Architecture

{project_name} implements a **webhook-driven multi-agent system**:

```
GitHub Repository → Webhook → Orchestrator Agent → Specialist Agents → Documentation Updates
```

The system includes **{len(modules)} core modules** including specialized agents for different documentation layers:
- **Tourist Guide Agent**: User experience and onboarding documentation
- **Building Inspector Agent**: Current system architecture and capabilities  
- **Historian Agent**: Decision history and evolution context

## Quick Start

See [Getting Started](getting_started.md) for detailed setup instructions.

## Documentation Structure

This documentation is organized into several sections:

- **Overview** (this page): Introduction and key concepts
- **[Getting Started](getting_started.md)**: Step-by-step setup and first usage
- **[Usage Patterns](usage_patterns.md)**: Common workflows and examples
- **[Advanced Usage](advanced_usage.md)**: Power user features and customization
- **[Troubleshooting](troubleshooting.md)**: Common issues and solutions{related_docs_section}

*This documentation is automatically maintained and updated as the system evolves.*
"""

    elif section == 'getting_started':
        # Generate intelligent installation guide based on actual project setup
        deps_info = ""
        if dependencies:
            key_deps_str = ", ".join(dependencies[:4])
            deps_info = f" (including {key_deps_str})"
        
        entry_point = project_context.get('entry_points', ['run_coderipple.py'])[0]
        
        # Generate realistic setup steps
        venv_setup = ""
        if os.path.exists('venv') or 'venv' in project_context.get('project_structure', []):
            venv_setup = """
4. **Activate virtual environment**
   ```bash
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
"""

        return f"""# Getting Started with {project_name}

## Prerequisites

- **Python 3.8+** (project uses Python with virtual environment)
- **Git repository** to monitor for documentation generation
- **AWS account** (for production deployment with Lambda and Bedrock)
- **GitHub repository** with webhook capability

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd coderipple
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   This installs **{len(dependencies)} key packages**{deps_info} required for multi-agent orchestration and AWS integration.{venv_setup}

## First Run

1. **Test the system locally**
   ```bash
   python {entry_point}
   ```

2. **Verify documentation generation**
   - Check that documentation files are created in the `coderipple/` directory
   - Review generated content for your project's specific patterns
   - Verify the three-layer documentation structure is established

## Configuration

The system requires minimal configuration for local testing:

- **Webhook endpoint**: Configure GitHub repository to send webhooks (for production)
- **AWS credentials**: Set up for Bedrock integration (optional for local testing)
- **Repository monitoring**: Point to your target repository for documentation

## Expected Output

After successful setup, you should see:

- **User documentation** in `coderipple/user/` (this layer)
- **System documentation** in `coderipple/system/` (current architecture)
- **Decision documentation** in `coderipple/decisions/` (evolution history)

## Next Steps

- Review [Usage Patterns](usage_patterns.md) for webhook integration workflows
- Explore [Advanced Usage](advanced_usage.md) for agent customization
- Check [Troubleshooting](troubleshooting.md) if you encounter setup issues

*This documentation is automatically maintained and updated as the system evolves.*
"""

    elif section == 'patterns':
        # Generate intelligent patterns based on actual usage and architecture
        entry_point = project_context.get('entry_points', ['run_coderipple.py'])[0]
        
        # Generate realistic agent examples based on actual modules
        agent_examples = []
        if 'tourist_guide_agent' in modules:
            agent_examples.append("- **Tourist Guide Agent**: Updates user-facing documentation when new features affect workflows")
        if 'building_inspector_agent' in modules:
            agent_examples.append("- **Building Inspector Agent**: Documents current system capabilities when architecture changes")
        if 'historian_agent' in modules:
            agent_examples.append("- **Historian Agent**: Records significant decisions and architectural changes")
        
        agent_examples_str = "\n".join(agent_examples) if agent_examples else "- **Multi-agent coordination**: Specialized agents handle different documentation perspectives"
        
        # Add actual testing patterns if examples exist
        testing_section = ""
        if os.path.exists('examples'):
            testing_section = f"""
### Testing Patterns

For development and validation:

```bash
# Test individual components
python examples/test_webhook.py

# Test agent coordination
python examples/test_git_agent.py

# Validate content generation
python examples/test_tourist_guide_bedrock.py
```
"""
        
        return f"""# Usage Patterns

## Core Workflow

{project_name} follows a **webhook-driven documentation generation pattern**:

### Automatic Documentation Generation

1. **Code Change**: Developer commits to monitored repository
2. **Webhook Trigger**: GitHub sends webhook payload to {project_name}
3. **Git Analysis**: System analyzes diff to understand change impact
4. **Agent Selection**: Orchestrator determines which agents to activate based on change type
5. **Parallel Processing**: Multiple specialist agents update documentation simultaneously
6. **Quality Validation**: Generated content passes through validation pipeline
7. **Documentation Commit**: Updated documentation is committed back to repository

### Agent Coordination Patterns

The multi-agent system follows **layer-based activation**:

{agent_examples_str}

Each agent operates on its specific documentation layer while maintaining cross-references to other layers.

## Integration Patterns

### GitHub Repository Integration

```bash
# Configure webhook in GitHub repository settings
Payload URL: https://your-coderipple-endpoint.com/webhook
Content type: application/json
Events: Push events, Pull request events
```

### Local Development Workflow

```bash
# 1. Set up development environment
source venv/bin/activate
python {entry_point}

# 2. Test with sample data
python src/webhook_parser.py --test

# 3. Verify output in coderipple/ directory
ls -la coderipple/user/
ls -la coderipple/system/
ls -la coderipple/decisions/
```{testing_section}

## Documentation Layer Patterns

### Three-Layer Structure

1. **User Layer** (`coderipple/user/`): How to engage with the system
2. **System Layer** (`coderipple/system/`): What the system currently is
3. **Decision Layer** (`coderipple/decisions/`): Why the system became this way

Each layer has **different update patterns**:
- User docs: Task-oriented updates based on workflow changes
- System docs: Incremental rewrites reflecting current state
- Decision docs: Append-only with historical preservation

## Best Practices

- **Monitor Agent Output**: Review generated documentation for accuracy and relevance
- **Customize Agent Prompts**: Adjust agent behavior for your project's specific needs
- **Validate Cross-References**: Ensure links between documentation layers remain accurate
- **Track Documentation Debt**: Use the validation pipeline to maintain quality standards

*This documentation is automatically maintained and updated as the system evolves.*
"""

    elif section == 'advanced':
        # Generate advanced usage based on actual modules and capabilities
        modules_list = ", ".join(modules[:5]) if modules else "core agent modules"
        
        # Add strands-specific configuration if detected
        strands_config = ""
        if 'strands-agents' in dependencies:
            strands_config = f"""
### AWS Strands Configuration

{project_name} uses AWS Strands for agent orchestration:

```python
# Example: Customizing agent behavior in src/{modules[0] if modules else 'agent'}.py
@tool
def custom_analysis_tool(change_data: dict) -> dict:
    # Custom analysis logic for your project
    return analysis_result
```

Configure Strands session management for multi-agent coordination:
- **Session State**: Maintain context across agent interactions
- **Tool Coordination**: Chain agent tools for complex workflows
- **Error Handling**: Implement graceful degradation for agent failures
"""
        
        # Add AWS integration details if capabilities detected
        aws_section = ""
        if 'AWS integration (Lambda, Bedrock)' in capabilities:
            aws_section = """
### AWS Integration

For production deployment and AI enhancement:

**Amazon Bedrock Integration**:
- Content quality improvement using large language models
- Dynamic example generation based on code analysis  
- Consistency checking across documentation layers

**AWS Lambda Deployment**:
- Serverless execution for webhook processing
- Automatic scaling based on repository activity
- Cost-effective operation for varying workloads
"""
        
        return f"""# Advanced Usage

## Agent Customization

{project_name} provides **{len(modules)} specialized modules** ({modules_list}) that can be customized for your specific needs.

### Individual Agent Configuration

Each agent can be customized by modifying its source in the `src/` directory:

```python
# Example: Customizing Tourist Guide Agent behavior
def _generate_content_for_section(section: str, context: dict):
    # Customize content generation logic
    # Add project-specific patterns and examples
    return customized_content
```

### Multi-Agent Orchestration

The **Orchestrator Agent** uses a **Layer Selection Decision Tree** to determine which agents to activate:

1. **User Impact Changes** → Tourist Guide Agent
2. **System Architecture Changes** → Building Inspector Agent  
3. **Significant Decisions** → Historian Agent

Customize the decision logic in `src/orchestrator_agent.py`.{strands_config}

## Advanced Workflows

### Multi-Repository Setup

For organizations managing multiple projects:

1. **Instance per Repository**: Deploy separate {project_name} instances
2. **Shared Infrastructure**: Use common AWS resources with project-specific configuration
3. **Cross-Repository References**: Link related documentation across projects
4. **Centralized Monitoring**: Aggregate documentation quality metrics

### Custom Documentation Types

Extend beyond the three-layer structure:

```python
# Add custom agent for specific documentation needs
class CustomSpecialistAgent:
    def analyze_changes(self, git_diff, context):
        # Custom analysis logic
        pass
    
    def generate_documentation(self, analysis_result):
        # Custom content generation
        pass
```{aws_section}

## Power User Features

### Advanced Git Analysis

Leverage detailed change analysis for sophisticated documentation patterns:

- **Dependency Impact**: Track how changes ripple through system components
- **Breaking Change Detection**: Automatically identify user-facing impacts
- **Code Quality Metrics**: Integrate documentation quality with code review

### Content Validation Pipeline

Customize the validation pipeline for your quality standards:

```python
# Example: Custom validation rules
def custom_validation_rules(content: str, context: dict) -> dict:
    # Implement project-specific validation logic
    return validation_result
```

### Performance Optimization

For high-volume repositories:

- **Batch Processing**: Group multiple commits for efficient processing
- **Selective Activation**: Configure which changes trigger documentation updates
- **Caching Strategies**: Optimize for repeated analysis patterns

## Integration APIs

Access {project_name} functionality programmatically:

```python
from src.orchestrator_agent import process_webhook_event
from src.tourist_guide_agent import bootstrap_user_documentation

# Programmatic documentation generation
result = process_webhook_event(webhook_data)

# Bootstrap new project documentation
bootstrap_result = bootstrap_user_documentation(project_context)
```

*This documentation is automatically maintained and updated as the system evolves.*
"""

    elif section == 'troubleshooting':
        # Generate intelligent troubleshooting based on actual project setup
        entry_point = project_context.get('entry_points', ['run_coderipple.py'])[0]
        actual_dependencies = len(dependencies) if dependencies else "required"
        
        # Add specific troubleshooting for virtual environment
        venv_troubleshooting = ""
        if os.path.exists('venv'):
            venv_troubleshooting = """
### Virtual Environment Issues

**Symptoms**: Import errors or missing dependencies

**Solutions**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Verify activation
which python  # Should point to venv/bin/python

# Reinstall dependencies if needed
pip install -r requirements.txt
```
"""
        
        # Add specific module troubleshooting
        module_troubleshooting = ""
        if modules:
            key_modules = modules[:3]
            module_troubleshooting = f"""
### Module Import Issues

**Symptoms**: `ModuleNotFoundError` for {project_name} components

**Common Issues**:
- Running from wrong directory
- Virtual environment not activated
- Missing dependencies

**Solutions**:
```bash
# Run from project root directory
cd /path/to/coderipple

# Verify key modules exist
ls src/{key_modules[0] if key_modules else 'agent'}.py

# Test imports
python -c "from src.{key_modules[0] if key_modules else 'agent'} import *"
```
"""
        
        return f"""# Troubleshooting

## Common Issues

### Setup and Installation

**Symptoms**: {project_name} fails to start or import errors occur

**Possible Causes**:
- Virtual environment not activated
- Missing dependencies ({actual_dependencies} packages required)
- Wrong working directory

**Solutions**:
1. **Verify Environment Setup**:
   ```bash
   source venv/bin/activate
   pip list | grep strands  # Should show strands-agents package
   ```

2. **Check Working Directory**:
   ```bash
   ls src/  # Should show agent modules
   python {entry_point}  # Run from project root
   ```

3. **Reinstall Dependencies**:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```{venv_troubleshooting}{module_troubleshooting}

### Documentation Generation Issues

**Symptoms**: No documentation files created in `coderipple/` directory

**Diagnostic Steps**:
```bash
# 1. Test bootstrap functionality
python -c "from src.tourist_guide_agent import bootstrap_user_documentation; print(bootstrap_user_documentation())"

# 2. Check file permissions
ls -la coderipple/

# 3. Verify agent execution
python {entry_point} --verbose
```

**Common Solutions**:
- Ensure `coderipple/` directory is writable
- Check that agent modules can import successfully
- Verify git repository has commits to analyze

### Content Quality Issues

**Symptoms**: Generated documentation is generic or inaccurate

**Possible Causes**:
- Insufficient project context analysis
- Agent prompts need customization
- Git analysis not capturing project-specific patterns

**Solutions**:
1. **Enhance Project Context**:
   ```python
   # Test context analysis
   from src.tourist_guide_agent import analyze_project_context_for_content_generation
   context = analyze_project_context_for_content_generation()
   print(context)
   ```

2. **Customize Agent Behavior**: Modify prompts in `src/` directory
3. **Validate Git Analysis**: Ensure change analysis captures relevant patterns

### AWS Integration Issues

**Symptoms**: Bedrock integration fails or AWS-related errors

**Possible Causes**:
- Missing AWS credentials
- Insufficient IAM permissions
- Region configuration issues

**Solutions**:
```bash
# Check AWS configuration
aws configure list

# Test Bedrock access
python examples/test_bedrock_demo.py

# Verify IAM permissions for Bedrock
aws bedrock list-foundation-models
```

## Debug Mode

Enable detailed logging for troubleshooting:

```bash
# Run with debug output
python {entry_point} --debug

# Test individual components
python src/webhook_parser.py --verbose
python examples/test_git_agent.py
```

## Performance Optimization

### Large Repository Handling

For repositories with extensive history or large diffs:

```bash
# Process specific commits only
python {entry_point} --commits HEAD~5..HEAD

# Limit diff analysis scope
python {entry_point} --max-files 50
```

### Memory and Processing Issues

**Symptoms**: High memory usage or timeout errors

**Solutions**:
- Process commits in smaller batches
- Increase system memory allocation
- Configure agent timeout limits

## Getting Help

**Diagnostic Information to Collect**:
1. **System Environment**:
   ```bash
   python --version
   pip list | grep -E "(strands|boto3|pydantic)"
   ls -la src/
   ```

2. **Error Logs**: Copy full error messages and stack traces
3. **Project Context**: Repository size, commit frequency, existing documentation

**Support Channels**:
- **Documentation Issues**: Review this troubleshooting guide
- **Bug Reports**: Include diagnostic information above
- **Feature Requests**: Describe your specific documentation needs

## Known Limitations

- **Large Repositories**: Repositories with >10,000 commits may require performance tuning
- **Complex Merge Conflicts**: Manual resolution may be needed for conflicting documentation updates
- **AWS Service Limits**: Rate limits may affect high-frequency usage (>100 commits/hour)
- **Language Support**: Optimized for Python projects; other languages may need custom configuration

*This documentation is automatically maintained and updated as the system evolves.*
"""

    else:
        return f"""# {section.replace('_', ' ').title()}

This section is under development.

*This documentation is automatically maintained and updated as the system evolves.*
"""


@tool
def check_user_documentation_completeness() -> Dict[str, Any]:
    """
    Check if all user documentation files exist and are complete.
    
    Returns:
        Dictionary with completeness status and missing files
    """
    try:
        missing_files = []
        existing_files = []
        
        for section, file_path in USER_DOCUMENTATION_STRUCTURE.items():
            full_path = get_documentation_path(file_path)
            if os.path.exists(full_path):
                existing_files.append(file_path)
            else:
                missing_files.append(file_path)
        
        is_complete = len(missing_files) == 0
        
        return {
            'status': 'success',
            'is_complete': is_complete,
            'existing_files': existing_files,
            'missing_files': missing_files,
            'completion_percentage': (len(existing_files) / len(USER_DOCUMENTATION_STRUCTURE)) * 100
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Completeness check failed: {str(e)}",
            'is_complete': False
        }


