"""
Orchestrator Agent for CodeRipple

This agent receives GitHub webhook events, analyzes the changes using the git analysis tool,
and determines which specialist agents should be invoked based on the Layer Selection Decision Tree.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from strands import Agent
from webhook_parser import GitHubWebhookParser, WebhookEvent
from git_analysis_tool import analyze_git_diff
from tourist_guide_agent import tourist_guide_agent


@dataclass
class AgentDecision:
    """Represents a decision to invoke a specialist agent"""
    agent_type: str  # 'tourist_guide', 'building_inspector', 'historian'
    reason: str
    priority: int  # 1=high, 2=medium, 3=low
    context: Dict[str, Any]


@dataclass
class OrchestrationResult:
    """Result of orchestrator analysis"""
    webhook_event: WebhookEvent
    git_analysis: Dict[str, Any]
    agent_decisions: List[AgentDecision]
    summary: str


def orchestrator_agent(webhook_payload: str, event_type: str, github_token: Optional[str] = None) -> OrchestrationResult:
    """
    Orchestrator Agent that analyzes webhook events and determines which specialist agents to invoke.
    
    Args:
        webhook_payload: Raw JSON string from GitHub webhook
        event_type: GitHub event type from X-GitHub-Event header
        github_token: Optional GitHub token for fetching commit diffs
        
    Returns:
        OrchestrationResult with decisions on which agents to invoke
    """
    
    # Step 1: Parse the webhook payload
    parser = GitHubWebhookParser()
    webhook_event = parser.parse_webhook_payload(webhook_payload, event_type)
    
    if not webhook_event:
        return OrchestrationResult(
            webhook_event=None,
            git_analysis={},
            agent_decisions=[],
            summary="Failed to parse webhook payload"
        )
    
    # Step 2: Enrich with git diff data
    if github_token:
        parser.enrich_commits_with_diff_data(webhook_event, github_token)
    
    # Step 3: Analyze changes using git analysis tool
    git_analysis = {}
    if webhook_event.commits and webhook_event.commits[0].diff_data:
        git_analysis = analyze_git_diff(webhook_event.commits[0].diff_data)
    else:
        # For testing without real diff data, infer from file changes
        affected_components = []
        for commit in webhook_event.commits:
            affected_components.extend(commit.added_files)
            affected_components.extend(commit.modified_files)
            affected_components.extend(commit.removed_files)
        
        # Simple change type inference for testing
        change_type = 'unknown'
        commit_msg = webhook_event.commits[0].message if webhook_event.commits else ''
        
        if 'Add' in commit_msg or 'new' in commit_msg.lower():
            change_type = 'feature'
        elif 'fix' in commit_msg.lower():
            change_type = 'bugfix'
        elif any('readme' in f.lower() for f in affected_components) and change_type == 'unknown':
            change_type = 'docs'
        
        git_analysis = {
            'change_type': change_type,
            'affected_components': list(set(affected_components)),
            'confidence': 0.6,
            'summary': f'Inferred {change_type} changes from file modifications'
        }
    
    # Step 4: Apply Layer Selection Decision Tree
    agent_decisions = _apply_decision_tree(webhook_event, git_analysis)
    
    # Step 5: Execute selected agents
    agent_results = _execute_selected_agents(webhook_event, git_analysis, agent_decisions)
    
    # Step 6: Generate summary
    summary = _generate_orchestration_summary(webhook_event, git_analysis, agent_decisions)
    
    return OrchestrationResult(
        webhook_event=webhook_event,
        git_analysis=git_analysis,
        agent_decisions=agent_decisions,
        summary=summary
    )


def _apply_decision_tree(webhook_event: WebhookEvent, git_analysis: Dict[str, Any]) -> List[AgentDecision]:
    """
    Apply the Layer Selection Decision Tree to determine which agents to invoke:
    
    1. Does this change how users interact with the system? → Tourist Guide Agent
    2. Does this change what the system currently is or does? → Building Inspector Agent  
    3. Does this represent a significant decision or learning? → Historian Agent
    """
    decisions = []
    change_type = git_analysis.get('change_type', 'unknown')
    affected_files = git_analysis.get('affected_components', [])
    
    # Decision 1: Tourist Guide Agent (How to ENGAGE)
    if _should_invoke_tourist_guide(change_type, affected_files):
        decisions.append(AgentDecision(
            agent_type='tourist_guide',
            reason=f"User interaction changes detected: {change_type} affecting {len(affected_files)} files",
            priority=1 if change_type == 'feature' else 2,
            context={
                'change_type': change_type,
                'affected_files': affected_files,
                'focus': 'user_workflows'
            }
        ))
    
    # Decision 2: Building Inspector Agent (What it IS)
    if _should_invoke_building_inspector(change_type, affected_files):
        decisions.append(AgentDecision(
            agent_type='building_inspector',
            reason=f"System changes detected: {change_type} modifications to current capabilities",
            priority=1 if change_type in ['feature', 'bugfix'] else 2,
            context={
                'change_type': change_type,
                'affected_files': affected_files,
                'focus': 'current_state'
            }
        ))
    
    # Decision 3: Historian Agent (Why it BECAME this way)
    if _should_invoke_historian(change_type, affected_files, webhook_event):
        decisions.append(AgentDecision(
            agent_type='historian',
            reason=f"Significant decision/learning detected: {change_type} with architectural implications",
            priority=2 if change_type == 'refactor' else 3,
            context={
                'change_type': change_type,
                'affected_files': affected_files,
                'focus': 'decision_context',
                'commit_messages': [commit.message for commit in webhook_event.commits]
            }
        ))
    
    return sorted(decisions, key=lambda x: x.priority)


def _execute_selected_agents(webhook_event: WebhookEvent, git_analysis: Dict[str, Any], agent_decisions: List[AgentDecision]) -> Dict[str, Any]:
    """Execute the selected specialist agents and return their results"""
    agent_results = {}
    
    for decision in agent_decisions:
        try:
            if decision.agent_type == 'tourist_guide':
                result = tourist_guide_agent(webhook_event, git_analysis, decision.context)
                agent_results['tourist_guide'] = result
                print(f"Tourist Guide Agent executed: {result.summary}")
                
            elif decision.agent_type == 'building_inspector':
                # Placeholder for Building Inspector Agent
                print(f"Building Inspector Agent would be executed (not implemented yet)")
                agent_results['building_inspector'] = {"status": "placeholder"}
                
            elif decision.agent_type == 'historian':
                # Placeholder for Historian Agent  
                print(f"Historian Agent would be executed (not implemented yet)")
                agent_results['historian'] = {"status": "placeholder"}
                
        except Exception as e:
            print(f"Error executing {decision.agent_type} agent: {e}")
            agent_results[decision.agent_type] = {"error": str(e)}
    
    return agent_results


def _should_invoke_tourist_guide(change_type: str, affected_files: List[str]) -> bool:
    """Determine if Tourist Guide Agent should be invoked"""
    # Invoke for changes that affect user workflows
    user_facing_indicators = [
        'readme', 'getting-started', 'tutorial', 'guide', 'example',
        'cli', 'api', 'interface', 'ui', 'frontend'
    ]
    
    # Feature changes likely affect user interaction
    if change_type == 'feature':
        return True
    
    # Documentation changes affect user guidance
    if change_type == 'docs':
        return True
    
    # Check if any affected files are user-facing
    for file in affected_files:
        if any(indicator in file.lower() for indicator in user_facing_indicators):
            return True
    
    return False


def _should_invoke_building_inspector(change_type: str, affected_files: List[str]) -> bool:
    """Determine if Building Inspector Agent should be invoked"""
    # Always invoke for functional changes to the current system
    functional_changes = ['feature', 'bugfix', 'performance', 'refactor']
    
    if change_type in functional_changes:
        return True
    
    # Invoke for core system file changes
    core_indicators = ['src/', 'lib/', 'core/', 'main', 'index']
    for file in affected_files:
        if any(indicator in file.lower() for indicator in core_indicators):
            return True
    
    return False


def _should_invoke_historian(change_type: str, affected_files: List[str], webhook_event: WebhookEvent) -> bool:
    """Determine if Historian Agent should be invoked"""
    # Invoke for significant architectural decisions
    if change_type == 'refactor':
        return True
    
    # Invoke for major feature additions (multiple files)
    if change_type == 'feature' and len(affected_files) > 3:
        return True
    
    # Invoke for configuration/infrastructure changes
    config_indicators = ['config', 'dockerfile', 'requirements', 'package.json', '.yml', '.yaml', 'terraform']
    for file in affected_files:
        if any(indicator in file.lower() for indicator in config_indicators):
            return True
    
    # Invoke for commits with decision-oriented messages
    decision_keywords = ['architecture', 'design', 'decision', 'refactor', 'migrate', 'upgrade']
    for commit in webhook_event.commits:
        if any(keyword in commit.message.lower() for keyword in decision_keywords):
            return True
    
    return False


def _generate_orchestration_summary(webhook_event: WebhookEvent, git_analysis: Dict[str, Any], agent_decisions: List[AgentDecision]) -> str:
    """Generate a summary of the orchestration results"""
    if not webhook_event:
        return "No valid webhook event to process"
    
    change_type = git_analysis.get('change_type', 'unknown')
    file_count = len(git_analysis.get('affected_components', []))
    agent_count = len(agent_decisions)
    
    summary = f"Processed {webhook_event.event_type} event: {change_type} changes to {file_count} files. "
    
    if agent_count == 0:
        summary += "No specialist agents required."
    elif agent_count == 1:
        summary += f"Invoking {agent_decisions[0].agent_type} agent."
    else:
        agent_types = [d.agent_type for d in agent_decisions]
        summary += f"Invoking {agent_count} agents: {', '.join(agent_types)}."
    
    return summary


