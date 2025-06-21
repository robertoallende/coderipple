"""
Tests for agent_context_flow module

Tests the Step 4C Cross-Agent Context Flow functionality including
context sharing, agent state management, and cross-references.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from agent_context_flow import (
    initialize_shared_context,
    register_agent_state,
    get_agent_state,
    get_current_capabilities,
    get_cross_agent_references,
    suggest_cross_references,
    add_global_insight,
    get_documentation_status,
    _reset_shared_context
)


def test_context_initialization():
    """Test shared context initialization"""
    
    print("Testing context initialization...")
    
    # Reset context to start clean
    _reset_shared_context()
    
    # Initialize context
    result = initialize_shared_context(
        repository_name="test-repo",
        repository_url="https://github.com/test/repo",
        current_commit="abc123"
    )
    
    assert result['status'] == 'success', f"Expected success, got {result['status']}"
    assert result['repository_name'] == 'test-repo', f"Repository name mismatch: {result['repository_name']}"
    assert result['commit'] == 'abc123', f"Commit mismatch: {result['commit']}"
    assert result['agents_ready'] == 0, f"Expected 0 agents initially, got {result['agents_ready']}"
    
    print("   ✓ Context initialization working")


def test_agent_state_registration():
    """Test agent state registration and retrieval"""
    
    print("Testing agent state registration...")
    
    # Reset and initialize context
    _reset_shared_context()
    initialize_shared_context("test-repo", "https://github.com/test/repo", "abc123")
    
    # Register Building Inspector state
    register_result = register_agent_state(
        agent_name="Building Inspector",
        agent_role="building_inspector",
        repository_context={'change_type': 'feature', 'files': ['src/api.py']},
        current_capabilities=['GitHub webhook processing', 'Multi-agent documentation'],
        generated_files=['system/architecture.md'],
        key_insights=['System supports multi-agent workflows'],
        cross_references={'tourist_guide': 'References user documentation'}
    )
    
    assert register_result['status'] == 'success', f"Registration failed: {register_result}"
    assert register_result['agent_role'] == 'building_inspector', f"Agent role mismatch"
    assert register_result['files_registered'] == 1, f"Expected 1 file registered"
    assert register_result['total_agents'] == 1, f"Expected 1 total agent"
    
    # Retrieve agent state
    retrieve_result = get_agent_state('building_inspector')
    
    assert retrieve_result['status'] == 'success', f"Retrieval failed: {retrieve_result}"
    agent_state = retrieve_result['agent_state']
    assert agent_state['agent_name'] == 'Building Inspector', f"Agent name mismatch"
    assert len(agent_state['current_capabilities']) == 2, f"Expected 2 capabilities"
    assert len(agent_state['generated_files']) == 1, f"Expected 1 generated file"
    
    print("   ✓ Agent state registration and retrieval working")


def test_capability_consolidation():
    """Test consolidation of capabilities across agents"""
    
    print("Testing capability consolidation...")
    
    # Reset and initialize context
    _reset_shared_context()
    initialize_shared_context("test-repo", "https://github.com/test/repo", "abc123")
    
    # Register multiple agents with different capabilities
    register_agent_state(
        agent_name="Building Inspector",
        agent_role="building_inspector",
        repository_context={},
        current_capabilities=['System architecture', 'API documentation'],
        generated_files=['system/arch.md'],
        key_insights=['System uses multi-agent pattern']
    )
    
    register_agent_state(
        agent_name="Tourist Guide",
        agent_role="tourist_guide",
        repository_context={},
        current_capabilities=['User workflows', 'API documentation', 'Getting started guides'],
        generated_files=['getting_started.md'],
        key_insights=['Users need better onboarding']
    )
    
    # Get consolidated capabilities
    capabilities_result = get_current_capabilities()
    
    assert capabilities_result['status'] == 'success', f"Capabilities retrieval failed"
    assert capabilities_result['total_capabilities'] == 4, f"Expected 4 unique capabilities"
    
    consolidated = capabilities_result['consolidated_capabilities']
    expected_capabilities = ['API documentation', 'Getting started guides', 'System architecture', 'User workflows']
    for cap in expected_capabilities:
        assert cap in consolidated, f"Missing capability: {cap}"
    
    # Check agent contributions
    contributions = capabilities_result['agent_contributions']
    assert 'building_inspector' in contributions, "Missing building inspector contribution"
    assert 'tourist_guide' in contributions, "Missing tourist guide contribution"
    assert contributions['building_inspector']['capabilities_count'] == 2, "Wrong building inspector count"
    assert contributions['tourist_guide']['capabilities_count'] == 3, "Wrong tourist guide count"
    
    print("   ✓ Capability consolidation working")


def test_cross_references():
    """Test cross-reference functionality"""
    
    print("Testing cross-references...")
    
    # Reset and initialize context
    _reset_shared_context()
    initialize_shared_context("test-repo", "https://github.com/test/repo", "abc123")
    
    # Register agents with cross-references
    register_agent_state(
        agent_name="Building Inspector",
        agent_role="building_inspector",
        repository_context={},
        current_capabilities=['System architecture'],
        generated_files=['system/architecture.md'],
        key_insights=['Complex multi-agent system'],
        cross_references={'tourist_guide': 'See user guide for workflows'}
    )
    
    register_agent_state(
        agent_name="Tourist Guide",
        agent_role="tourist_guide",
        repository_context={},
        current_capabilities=['User workflows'],
        generated_files=['getting_started.md'],
        key_insights=['Users need system overview'],
        cross_references={'building_inspector': 'See system docs for architecture'}
    )
    
    # Get cross-references
    cross_refs = get_cross_agent_references()
    
    assert cross_refs['status'] == 'success', f"Cross-reference retrieval failed"
    
    # Check cross-references structure
    refs = cross_refs['cross_references']
    assert 'building_inspector' in refs, "Missing building inspector references"
    assert 'tourist_guide' in refs, "Missing tourist guide references"
    
    # Check reverse reference map
    ref_map = cross_refs['reference_map']
    assert 'tourist_guide' in ref_map, "Missing tourist guide in reference map"
    assert 'building_inspector' in ref_map, "Missing building inspector in reference map"
    
    print("   ✓ Cross-references working")


def test_suggestion_system():
    """Test cross-reference suggestion system"""
    
    print("Testing suggestion system...")
    
    # Reset and initialize context
    _reset_shared_context()
    initialize_shared_context("test-repo", "https://github.com/test/repo", "abc123")
    
    # Register Building Inspector with relevant capabilities
    register_agent_state(
        agent_name="Building Inspector",
        agent_role="building_inspector",
        repository_context={},
        current_capabilities=['API architecture', 'System design', 'Database schema'],
        generated_files=['system/api.md'],
        key_insights=['API follows REST principles', 'Database uses PostgreSQL']
    )
    
    # Test suggestions for API-related content
    suggestions = suggest_cross_references('tourist_guide', 'API documentation for user workflows')
    
    assert suggestions['status'] == 'success', f"Suggestions failed: {suggestions}"
    assert suggestions['requesting_agent'] == 'tourist_guide', "Wrong requesting agent"
    
    # Should suggest Building Inspector since it has API-related content
    suggestion_list = suggestions['suggestions']
    assert len(suggestion_list) > 0, "Expected at least one suggestion"
    
    # Find Building Inspector suggestion
    building_inspector_suggestion = None
    for suggestion in suggestion_list:
        if suggestion['agent_role'] == 'building_inspector':
            building_inspector_suggestion = suggestion
            break
    
    assert building_inspector_suggestion is not None, "Expected Building Inspector suggestion"
    assert len(building_inspector_suggestion['relevant_capabilities']) > 0, "Expected relevant capabilities"
    
    print("   ✓ Suggestion system working")


def test_global_insights():
    """Test global insight sharing"""
    
    print("Testing global insights...")
    
    # Reset and initialize context
    _reset_shared_context()
    initialize_shared_context("test-repo", "https://github.com/test/repo", "abc123")
    
    # Add insights from different agents
    insight1_result = add_global_insight(
        "System architecture is complex and requires multiple documentation layers",
        "building_inspector"
    )
    
    insight2_result = add_global_insight(
        "Users struggle with initial setup - need better onboarding",
        "tourist_guide"
    )
    
    assert insight1_result['status'] == 'success', "First insight addition failed"
    assert insight2_result['status'] == 'success', "Second insight addition failed"
    assert insight2_result['total_insights'] == 2, "Expected 2 total insights"
    
    # Get documentation status to see insights
    doc_status = get_documentation_status()
    
    assert doc_status['status'] == 'success', "Documentation status retrieval failed"
    
    global_insights = doc_status['global_insights']
    assert len(global_insights) == 2, f"Expected 2 insights, got {len(global_insights)}"
    
    # Check insight format (should have timestamp and source)
    for insight in global_insights:
        assert 'building_inspector' in insight or 'tourist_guide' in insight, f"Insight missing source: {insight}"
    
    print("   ✓ Global insights working")


def test_documentation_status():
    """Test comprehensive documentation status"""
    
    print("Testing documentation status...")
    
    # Reset and initialize context
    _reset_shared_context()
    initialize_shared_context("test-repo", "https://github.com/test/repo", "abc123")
    
    # Register multiple agents
    register_agent_state(
        agent_name="Building Inspector",
        agent_role="building_inspector",
        repository_context={},
        current_capabilities=['System docs'],
        generated_files=['system/architecture.md', 'system/api.md'],
        key_insights=['Complex system']
    )
    
    register_agent_state(
        agent_name="Tourist Guide",
        agent_role="tourist_guide",
        repository_context={},
        current_capabilities=['User docs'],
        generated_files=['getting_started.md', 'README.md'],
        key_insights=['Users need help']
    )
    
    # Get comprehensive status
    status = get_documentation_status()
    
    assert status['status'] == 'success', "Status retrieval failed"
    assert status['repository'] == 'test-repo', "Wrong repository"
    assert status['total_files_generated'] == 4, f"Expected 4 files, got {status['total_files_generated']}"
    assert status['active_agents'] == 2, f"Expected 2 agents, got {status['active_agents']}"
    
    # Check files by agent
    files_by_agent = status['files_by_agent']
    assert 'building_inspector' in files_by_agent, "Missing building inspector files"
    assert 'tourist_guide' in files_by_agent, "Missing tourist guide files"
    assert len(files_by_agent['building_inspector']) == 2, "Wrong building inspector file count"
    assert len(files_by_agent['tourist_guide']) == 2, "Wrong tourist guide file count"
    
    # Check agent summary
    agent_summary = status['agent_summary']
    assert 'building_inspector' in agent_summary, "Missing building inspector summary"
    assert 'tourist_guide' in agent_summary, "Missing tourist guide summary"
    
    print("   ✓ Documentation status working")


def run_all_tests():
    """Run all context flow tests"""
    
    print("🧪 Testing Agent Context Flow (Step 4C)")
    print("=" * 60)
    
    try:
        test_context_initialization()
        test_agent_state_registration()
        test_capability_consolidation()
        test_cross_references()
        test_suggestion_system()
        test_global_insights()
        test_documentation_status()
        
        print("\n✅ All agent context flow tests passed!")
        print("\n🎯 Step 4C: Cross-Agent Context Flow is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)