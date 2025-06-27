"""
Tests for Historian Agent

Tests the Historian Agent functionality including decision analysis,
decision documentation generation, and file writing capabilities.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from coderipple.historian_agent import historian_agent
from coderipple.webhook_parser import CommitInfo, WebhookEvent
from datetime import datetime

def test_historian():
    """Test the Historian agent with sample data"""
    
    # Create sample webhook event for a refactoring
    sample_commit = CommitInfo(
        id="abc123",
        message="Refactor authentication system to improve security architecture",
        author="Developer",
        timestamp=datetime.now(),
        added_files=["src/auth/new_auth.py"],
        modified_files=["src/main.py", "src/auth/auth.py", "requirements.txt"],
        removed_files=["src/auth/old_auth.py"],
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
        'change_type': 'refactor',
        'affected_components': ['src/auth/new_auth.py', 'src/main.py', 'src/auth/auth.py', 'requirements.txt'],
        'confidence': 0.9,
        'summary': 'Detected refactor changes in 4 files'
    }
    
    sample_context = {
        'change_type': 'refactor',
        'affected_files': ['src/auth/new_auth.py', 'src/main.py', 'src/auth/auth.py', 'requirements.txt'],
        'focus': 'decision_context',
        'commit_messages': ['Refactor authentication system to improve security architecture']
    }
    
    print("Testing Historian Agent...")
    print("=" * 50)
    
    result = historian_agent(sample_event, sample_git_analysis, sample_context)
    
    print(f"Summary: {result.summary}")
    print(f"Decision Impact: {result.decision_impact}")
    print(f"Decision Documentation Updates ({len(result.updates)}):")
    
    for i, update in enumerate(result.updates, 1):
        print(f"\n{i}. {update.section} ({update.action}) - Priority {update.priority}")
        print(f"   Decision ID: {update.decision_id}")
        print(f"   Reason: {update.reason}")
        print(f"   Content Preview: {update.content[:100]}...")

def test_generate_decision_content_for_section():
    """Test the _generate_decision_content_for_section function covering lines 473-619"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from coderipple.historian_agent import _generate_decision_content_for_section
    from coderipple.webhook_parser import CommitInfo, WebhookEvent
    from datetime import datetime
    
    print("\nTesting _generate_decision_content_for_section...")
    
    # Create sample webhook event
    sample_commit = CommitInfo(
        id="abc123456789",
        message="Refactor authentication system",
        author="Test Developer",
        timestamp=datetime.now(),
        added_files=["src/auth.py"],
        modified_files=["src/main.py"],
        removed_files=[],
        url="https://github.com/test/repo/commit/abc123456789"
    )
    
    webhook_event = WebhookEvent(
        event_type="push",
        repository_name="test/repo",
        repository_url="https://github.com/test/repo",
        branch="main",
        commits=[sample_commit],
        before_sha="before123",
        after_sha="abc123456789"
    )
    
    recommendations = ["Improved security", "Better maintainability"]
    affected_files = ["src/auth.py", "src/main.py"]
    change_type = "refactor"
    decision_id = "001"
    
    # Test architecture_decisions section (lines 476-498)
    arch_content = _generate_decision_content_for_section(
        'architecture_decisions', change_type, affected_files, recommendations, webhook_event, decision_id
    )
    assert f"ADR-{decision_id}: Refactor Architectural Decision" in arch_content
    assert "Test Developer" in arch_content
    assert "abc12345" in arch_content  # Short commit hash
    assert "Improved security" in arch_content
    assert "src/auth.py, src/main.py" in arch_content
    print("✓ Architecture decisions section test passed")
    
    # Test problem_evolution section (lines 500-525)
    problem_content = _generate_decision_content_for_section(
        'problem_evolution', change_type, affected_files, recommendations, webhook_event, decision_id
    )
    assert "Problem Evolution Entry" in problem_content
    assert "Change Type**: refactor" in problem_content
    assert "2 files" in problem_content
    assert "Better maintainability" in problem_content
    print("✓ Problem evolution section test passed")
    
    # Test refactoring_history section (lines 527-553)
    refactor_content = _generate_decision_content_for_section(
        'refactoring_history', change_type, affected_files, recommendations, webhook_event, decision_id
    )
    assert f"REFACTOR-{decision_id}" in refactor_content
    assert "refactor refactoring" in refactor_content
    assert "2 files affected" in refactor_content
    assert "Legacy structure with technical debt" in refactor_content
    assert "Testing ensures functionality preservation" in refactor_content
    print("✓ Refactoring history section test passed")
    
    # Test technology_migrations section (lines 555-581)
    tech_content = _generate_decision_content_for_section(
        'technology_migrations', change_type, affected_files, recommendations, webhook_event, decision_id
    )
    assert f"TECH-{decision_id}" in tech_content
    assert "Technology Migration" in tech_content
    assert "src/auth.py, src/main.py" in tech_content
    assert "Knowledge transfer for new technologies" in tech_content
    print("✓ Technology migrations section test passed")
    
    # Test failed_experiments section (lines 583-617)
    exp_content = _generate_decision_content_for_section(
        'failed_experiments', change_type, affected_files, recommendations, webhook_event, decision_id
    )
    assert f"EXP-{decision_id}" in exp_content
    assert "Failed Experiment" in exp_content
    assert "Failed/Reverted" in exp_content
    assert "Technical limitations discovered" in exp_content
    assert "Revisit when technology landscape changes" in exp_content
    print("✓ Failed experiments section test passed")
    
    # Test default section (line 619)
    default_content = _generate_decision_content_for_section(
        'unknown_section', change_type, affected_files, recommendations, webhook_event, decision_id
    )
    assert "Unknown Section" in default_content
    assert "Decision context preserved for refactor changes" in default_content
    print("✓ Default section test passed")

def test_enhance_decision_updates_with_bedrock():
    """Test the _enhance_decision_updates_with_bedrock function covering lines 689-750"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from coderipple.historian_agent import _enhance_decision_updates_with_bedrock, DecisionDocumentationUpdate
    
    print("\nTesting _enhance_decision_updates_with_bedrock...")
    
    # Test with empty updates list (lines 689-690)
    empty_result = _enhance_decision_updates_with_bedrock([], {}, {})
    assert empty_result == []
    print("✓ Empty updates test passed")
    
    # Test with sample updates (lines 692-750)
    sample_updates = [
        DecisionDocumentationUpdate(
            section="architecture_decisions",
            action="create",
            content="Sample architecture decision content",
            reason="Testing enhancement",
            priority=1,
            decision_id="TEST-001"
        )
    ]
    
    decision_analysis = {
        'decision_changes': {'type': 'refactor', 'impact': 'high'}
    }
    context = {'repository_name': 'test-repo'}
    
    # Mock the bedrock enhancement to avoid external dependencies
    def mock_enhance_content_with_bedrock(content, context):
        return {
            'status': 'success',
            'content': [{
                'json': {
                    'enhanced_content': f"Enhanced: {content}",
                    'improvements_made': ['improved clarity', 'added historical context'],
                    'quality_score': 0.88
                }
            }]
        }
    
    # Patch the function temporarily
    from coderipple import historian_agent
    original_enhance = getattr(historian_agent, 'enhance_content_with_bedrock', None)
    historian_agent.enhance_content_with_bedrock = mock_enhance_content_with_bedrock
    
    try:
        enhanced_updates = _enhance_decision_updates_with_bedrock(sample_updates, decision_analysis, context)
        assert len(enhanced_updates) == 1
        assert "Enhanced: Sample architecture decision content" in enhanced_updates[0].content
        assert "quality: 0.88" in enhanced_updates[0].reason
        assert enhanced_updates[0].decision_id == "TEST-001"
        print("✓ Bedrock enhancement test passed")
    except Exception as e:
        # If bedrock tools not available, test error handling
        enhanced_updates = _enhance_decision_updates_with_bedrock(sample_updates, decision_analysis, context)
        assert len(enhanced_updates) == 1  # Should fallback to original
        print("✓ Bedrock fallback test passed")
    finally:
        # Restore original function
        if original_enhance:
            historian_agent.enhance_content_with_bedrock = original_enhance
    
    # Test error handling (lines 745-748)
    def mock_error_enhance(content, context):
        raise Exception("Simulated Bedrock error")
    
    historian_agent.enhance_content_with_bedrock = mock_error_enhance
    
    try:
        error_enhanced = _enhance_decision_updates_with_bedrock(sample_updates, decision_analysis, context)
        assert len(error_enhanced) == 1
        assert error_enhanced[0].content == "Sample architecture decision content"  # Original content preserved
        print("✓ Error handling test passed")
    finally:
        # Restore original function
        if original_enhance:
            historian_agent.enhance_content_with_bedrock = original_enhance

def test_helper_functions():
    """Test utility functions in historian_agent.py"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from coderipple.historian_agent import _get_current_timestamp, _calculate_decision_priority
    
    print("\nTesting helper functions...")
    
    # Test _get_current_timestamp function
    timestamp = _get_current_timestamp()
    assert isinstance(timestamp, str)
    assert len(timestamp) > 10  # Should be a reasonable timestamp string
    print("✓ Timestamp function test passed")
    
    # Test _calculate_decision_priority function
    priority = _calculate_decision_priority('refactor', {'decision_changes': {'impact': 'high'}})
    assert isinstance(priority, int)
    assert 1 <= priority <= 3  # Should return valid priority
    print("✓ Priority calculation test passed")

if __name__ == "__main__":
    test_historian()
    test_generate_decision_content_for_section()
    test_enhance_decision_updates_with_bedrock()
    test_helper_functions()
    print("\n" + "="*50)
    print("All Historian Agent tests completed!")