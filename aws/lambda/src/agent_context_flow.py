"""
Agent Context Flow for Multi-Agent Communication and State Management

This module provides tools and mechanisms for agents to share their current state
and reference each other's outputs, enabling consistency across documentation layers.
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from strands import tool

@dataclass
class AgentState:
    """Represents the current state of an agent"""
    agent_name: str
    agent_role: str  # 'tourist_guide', 'building_inspector', 'historian'
    last_updated: str
    repository_context: Dict[str, Any]
    current_capabilities: List[str]
    generated_files: List[str]
    key_insights: List[str]
    cross_references: Dict[str, str]  # References to other agents' outputs

@dataclass
class SharedContext:
    """Shared context accessible to all agents"""
    repository_name: str
    repository_url: str
    current_commit: str
    agent_states: Dict[str, AgentState]
    global_insights: List[str]
    documentation_map: Dict[str, str]  # file_path -> agent_responsible

# Global context storage (in production, this would be in a database or shared storage)
_shared_context: Optional[SharedContext] = None

@tool
def initialize_shared_context(repository_name: str, repository_url: str, current_commit: str) -> Dict[str, Any]:
    """
    Initialize shared context for multi-agent collaboration.
    
    This tool sets up the global context that all agents can access and update.
    Should be called by the Orchestrator Agent at the beginning of processing.
    
    Args:
        repository_name: Name of the repository being processed
        repository_url: URL of the repository
        current_commit: Current commit SHA being processed
        
    Returns:
        Dictionary with initialization status and context summary
    """
    global _shared_context
    
    _shared_context = SharedContext(
        repository_name=repository_name,
        repository_url=repository_url,
        current_commit=current_commit,
        agent_states={},
        global_insights=[],
        documentation_map={}
    )
    
    return {
        'status': 'success',
        'message': f'Shared context initialized for {repository_name}',
        'repository_name': repository_name,
        'commit': current_commit,
        'agents_ready': 0
    }

@tool
def register_agent_state(agent_name: str, agent_role: str, repository_context: Dict[str, Any], 
                        current_capabilities: List[str], generated_files: List[str], 
                        key_insights: List[str], cross_references: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Register or update an agent's current state in the shared context.
    
    This allows agents to share their current understanding and outputs with other agents.
    Each agent should call this after completing their processing.
    
    Args:
        agent_name: Name of the agent (e.g., "Tourist Guide", "Building Inspector")
        agent_role: Role identifier ('tourist_guide', 'building_inspector', 'historian')
        repository_context: Agent's understanding of the repository state
        current_capabilities: List of current system capabilities the agent is aware of
        generated_files: List of files this agent has generated or updated
        key_insights: Important insights this agent has discovered
        cross_references: References to other agents' outputs (optional)
        
    Returns:
        Dictionary with registration status and context summary
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized. Call initialize_shared_context first.',
            'agent_name': agent_name
        }
    
    if cross_references is None:
        cross_references = {}
    
    agent_state = AgentState(
        agent_name=agent_name,
        agent_role=agent_role,
        last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        repository_context=repository_context,
        current_capabilities=current_capabilities,
        generated_files=generated_files,
        key_insights=key_insights,
        cross_references=cross_references
    )
    
    _shared_context.agent_states[agent_role] = agent_state
    
    # Update documentation map
    for file_path in generated_files:
        _shared_context.documentation_map[file_path] = agent_role
    
    return {
        'status': 'success',
        'message': f'{agent_name} state registered successfully',
        'agent_name': agent_name,
        'agent_role': agent_role,
        'files_registered': len(generated_files),
        'total_agents': len(_shared_context.agent_states)
    }

@tool
def get_agent_state(agent_role: str) -> Dict[str, Any]:
    """
    Retrieve the current state of a specific agent.
    
    This allows agents to reference each other's current understanding and outputs.
    
    Args:
        agent_role: Role identifier ('tourist_guide', 'building_inspector', 'historian')
        
    Returns:
        Dictionary with agent state information or error if not found
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized'
        }
    
    if agent_role not in _shared_context.agent_states:
        return {
            'status': 'not_found',
            'message': f'No state found for agent role: {agent_role}',
            'available_agents': list(_shared_context.agent_states.keys())
        }
    
    agent_state = _shared_context.agent_states[agent_role]
    
    return {
        'status': 'success',
        'agent_state': asdict(agent_state),
        'last_updated': agent_state.last_updated
    }

@tool
def get_current_capabilities() -> Dict[str, Any]:
    """
    Get a consolidated view of current system capabilities from all agents.
    
    This combines capabilities reported by all agents to provide a comprehensive
    view of what the system currently supports.
    
    Returns:
        Dictionary with consolidated capabilities from all agents
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized'
        }
    
    all_capabilities = set()
    agent_contributions = {}
    
    for agent_role, agent_state in _shared_context.agent_states.items():
        agent_capabilities = set(agent_state.current_capabilities)
        all_capabilities.update(agent_capabilities)
        agent_contributions[agent_role] = {
            'agent_name': agent_state.agent_name,
            'capabilities_count': len(agent_capabilities),
            'capabilities': list(agent_capabilities),
            'last_updated': agent_state.last_updated
        }
    
    return {
        'status': 'success',
        'total_capabilities': len(all_capabilities),
        'consolidated_capabilities': sorted(list(all_capabilities)),
        'agent_contributions': agent_contributions,
        'repository': _shared_context.repository_name
    }

@tool
def get_cross_agent_references() -> Dict[str, Any]:
    """
    Get cross-references between agents for consistency checking.
    
    This helps identify where agents reference each other's work and ensures
    consistency across documentation layers.
    
    Returns:
        Dictionary with cross-reference information between agents
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized'
        }
    
    cross_references = {}
    reference_map = {}
    
    for agent_role, agent_state in _shared_context.agent_states.items():
        cross_references[agent_role] = {
            'agent_name': agent_state.agent_name,
            'references_to_others': agent_state.cross_references,
            'generated_files': agent_state.generated_files
        }
        
        # Build reverse reference map
        for ref_target, ref_description in agent_state.cross_references.items():
            if ref_target not in reference_map:
                reference_map[ref_target] = []
            reference_map[ref_target].append({
                'from_agent': agent_role,
                'reference_description': ref_description
            })
    
    return {
        'status': 'success',
        'cross_references': cross_references,
        'reference_map': reference_map,
        'documentation_map': _shared_context.documentation_map
    }

@tool
def add_global_insight(insight: str, source_agent: str) -> Dict[str, Any]:
    """
    Add a global insight that may be relevant to multiple agents.
    
    This allows agents to share important discoveries that might affect
    other agents' documentation strategies.
    
    Args:
        insight: The insight or discovery to share
        source_agent: The agent role that discovered this insight
        
    Returns:
        Dictionary with success status and insight summary
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized'
        }
    
    timestamped_insight = f"[{datetime.now().strftime('%H:%M:%S')}] {source_agent}: {insight}"
    _shared_context.global_insights.append(timestamped_insight)
    
    return {
        'status': 'success',
        'message': 'Global insight added successfully',
        'insight': timestamped_insight,
        'total_insights': len(_shared_context.global_insights)
    }

@tool
def get_documentation_status() -> Dict[str, Any]:
    """
    Get comprehensive status of all documentation generated by agents.
    
    This provides a bird's-eye view of what documentation has been created,
    by which agents, and how agents are referencing each other's work.
    
    Returns:
        Dictionary with comprehensive documentation status
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized'
        }
    
    total_files = len(_shared_context.documentation_map)
    files_by_agent = {}
    
    for file_path, agent_role in _shared_context.documentation_map.items():
        if agent_role not in files_by_agent:
            files_by_agent[agent_role] = []
        files_by_agent[agent_role].append(file_path)
    
    agent_summary = {}
    for agent_role, agent_state in _shared_context.agent_states.items():
        agent_summary[agent_role] = {
            'agent_name': agent_state.agent_name,
            'files_generated': len(agent_state.generated_files),
            'capabilities_documented': len(agent_state.current_capabilities),
            'insights_shared': len(agent_state.key_insights),
            'cross_references': len(agent_state.cross_references),
            'last_updated': agent_state.last_updated
        }
    
    return {
        'status': 'success',
        'repository': _shared_context.repository_name,
        'commit': _shared_context.current_commit,
        'total_files_generated': total_files,
        'files_by_agent': files_by_agent,
        'agent_summary': agent_summary,
        'global_insights': _shared_context.global_insights,
        'active_agents': len(_shared_context.agent_states)
    }

@tool
def suggest_cross_references(requesting_agent: str, target_content: str) -> Dict[str, Any]:
    """
    Suggest cross-references to other agents' content based on target content.
    
    This helps agents identify relevant content from other agents that they
    should reference to maintain consistency and avoid duplication.
    
    Args:
        requesting_agent: The agent role requesting suggestions
        target_content: Description of content being created (for context matching)
        
    Returns:
        Dictionary with suggested cross-references to other agents' work
    """
    global _shared_context
    
    if not _shared_context:
        return {
            'status': 'error',
            'message': 'Shared context not initialized'
        }
    
    suggestions = []
    target_lower = target_content.lower()
    
    for agent_role, agent_state in _shared_context.agent_states.items():
        if agent_role == requesting_agent:
            continue
            
        # Check capabilities for matches
        relevant_capabilities = []
        for capability in agent_state.current_capabilities:
            if any(keyword in capability.lower() for keyword in target_lower.split()):
                relevant_capabilities.append(capability)
        
        # Check insights for matches
        relevant_insights = []
        for insight in agent_state.key_insights:
            if any(keyword in insight.lower() for keyword in target_lower.split()):
                relevant_insights.append(insight)
        
        # Check files for relevance
        relevant_files = []
        for file_path in agent_state.generated_files:
            if any(keyword in file_path.lower() for keyword in target_lower.split()):
                relevant_files.append(file_path)
        
        if relevant_capabilities or relevant_insights or relevant_files:
            suggestions.append({
                'agent_role': agent_role,
                'agent_name': agent_state.agent_name,
                'relevant_capabilities': relevant_capabilities,
                'relevant_insights': relevant_insights,
                'relevant_files': relevant_files,
                'last_updated': agent_state.last_updated
            })
    
    return {
        'status': 'success',
        'requesting_agent': requesting_agent,
        'target_content': target_content,
        'suggestions': suggestions,
        'suggestion_count': len(suggestions)
    }

def _get_shared_context() -> Optional[SharedContext]:
    """Internal function to get shared context (for testing)"""
    return _shared_context

def _reset_shared_context():
    """Internal function to reset shared context (for testing)"""
    global _shared_context
    _shared_context = None