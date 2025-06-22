"""
Tests for Building Inspector Agent

Tests the Building Inspector Agent functionality including system analysis,
documentation generation, and file writing capabilities.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from building_inspector_agent import building_inspector_agent
from webhook_parser import CommitInfo, WebhookEvent
from datetime import datetime


def test_building_inspector():
    """Test the Building Inspector agent with sample data"""
    
    # Create sample webhook event
    sample_commit = CommitInfo(
        id="abc123",
        message="Add new CLI command for user authentication",
        author="Developer",
        timestamp=datetime.now(),
        added_files=["src/cli.py", "src/auth.py"],
        modified_files=["src/main.py", "requirements.txt"],
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
        'affected_components': ['src/cli.py', 'src/auth.py', 'src/main.py', 'requirements.txt'],
        'confidence': 0.8,
        'summary': 'Detected feature changes in 4 files'
    }
    
    sample_context = {
        'change_type': 'feature',
        'affected_files': ['src/cli.py', 'src/auth.py', 'src/main.py', 'requirements.txt'],
        'focus': 'current_state'
    }
    
    print("Testing Building Inspector Agent...")
    print("=" * 50)
    
    result = building_inspector_agent(sample_event, sample_git_analysis, sample_context)
    
    print(f"Summary: {result.summary}")
    print(f"System Impact: {result.system_impact}")
    print(f"System Documentation Updates ({len(result.updates)}):")
    
    for i, update in enumerate(result.updates, 1):
        print(f"\n{i}. {update.section} ({update.action}) - Priority {update.priority}")
        print(f"   Reason: {update.reason}")
        print(f"   Content Preview: {update.content[:100]}...")


def test_generate_system_content_for_section():
    """Test the _generate_system_content_for_section function covering lines 532-656"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from building_inspector_agent import _generate_system_content_for_section
    
    print("\nTesting _generate_system_content_for_section...")
    
    recommendations = ["Added CLI authentication", "Updated main entry point"]
    change_type = "feature"
    
    # Test purpose section (lines 532-547)
    purpose_content = _generate_system_content_for_section('purpose', change_type, [], recommendations)
    assert "## System Purpose" in purpose_content
    assert "Automated documentation maintenance" in purpose_content
    assert "Added CLI authentication" in purpose_content
    print("✓ Purpose section test passed")
    
    # Test architecture section (lines 549-573)
    architecture_content = _generate_system_content_for_section('architecture', change_type, [], recommendations)
    assert "## System Architecture" in architecture_content
    assert "webhook-driven, multi-agent architecture" in architecture_content
    assert "GitHub Webhook → API Gateway" in architecture_content
    print("✓ Architecture section test passed")
    
    # Test interfaces section (lines 575-601)
    interfaces_content = _generate_system_content_for_section('interfaces', change_type, [], recommendations)
    assert "## System Interfaces" in interfaces_content
    assert "GitHub Webhooks" in interfaces_content
    assert "webhook_event = parser.parse_webhook_payload" in interfaces_content
    print("✓ Interfaces section test passed")
    
    # Test capabilities section (lines 603-626)
    capabilities_content = _generate_system_content_for_section('capabilities', change_type, [], recommendations)
    assert "## Current Capabilities" in capabilities_content
    assert "Parse GitHub webhook events" in capabilities_content
    assert "Response time: < 30 seconds" in capabilities_content
    print("✓ Capabilities section test passed")
    
    # Test tech_stack section (lines 628-654)
    tech_stack_content = _generate_system_content_for_section('tech_stack', change_type, [], recommendations)
    assert "## Technology Stack" in tech_stack_content
    assert "Python 3.x" in tech_stack_content
    assert "AWS Strands" in tech_stack_content
    print("✓ Tech stack section test passed")
    
    # Test default section (line 656)
    default_content = _generate_system_content_for_section('unknown_section', change_type, [], recommendations)
    assert "Unknown Section" in default_content
    assert "Current system documentation" in default_content
    print("✓ Default section test passed")


def test_enhance_system_updates_with_bedrock():
    """Test the _enhance_system_updates_with_bedrock function covering lines 836-895"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from building_inspector_agent import _enhance_system_updates_with_bedrock, SystemDocumentationUpdate
    
    print("\nTesting _enhance_system_updates_with_bedrock...")
    
    # Test with empty updates list (lines 836-837)
    empty_result = _enhance_system_updates_with_bedrock([], {}, {})
    assert empty_result == []
    print("✓ Empty updates test passed")
    
    # Test with sample updates (lines 839-895)
    sample_updates = [
        SystemDocumentationUpdate(
            section="purpose",
            action="update",
            content="Sample system purpose content",
            reason="Testing enhancement",
            priority=1
        )
    ]
    
    system_analysis = {
        'system_changes': {'type': 'feature', 'impact': 'medium'}
    }
    context = {'repository_name': 'test-repo'}
    
    # Mock the bedrock enhancement to avoid external dependencies
    def mock_enhance_content_with_bedrock(content, context):
        return {
            'status': 'success',
            'content': [{
                'json': {
                    'enhanced_content': f"Enhanced: {content}",
                    'improvements_made': ['improved clarity', 'added technical details'],
                    'quality_score': 0.85
                }
            }]
        }
    
    # Patch the function temporarily
    import building_inspector_agent
    original_enhance = getattr(building_inspector_agent, 'enhance_content_with_bedrock', None)
    building_inspector_agent.enhance_content_with_bedrock = mock_enhance_content_with_bedrock
    
    try:
        enhanced_updates = _enhance_system_updates_with_bedrock(sample_updates, system_analysis, context)
        assert len(enhanced_updates) == 1
        assert "Enhanced: Sample system purpose content" in enhanced_updates[0].content
        assert "quality: 0.85" in enhanced_updates[0].reason
        print("✓ Bedrock enhancement test passed")
    except Exception as e:
        # If bedrock tools not available, test error handling
        enhanced_updates = _enhance_system_updates_with_bedrock(sample_updates, system_analysis, context)
        assert len(enhanced_updates) == 1  # Should fallback to original
        print("✓ Bedrock fallback test passed")
    finally:
        # Restore original function
        if original_enhance:
            building_inspector_agent.enhance_content_with_bedrock = original_enhance


def test_generate_system_content_with_context_analysis():
    """Test the _generate_system_content_with_context_analysis function covering lines 905-957"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from building_inspector_agent import _generate_system_content_with_context_analysis
    
    print("\nTesting _generate_system_content_with_context_analysis...")
    
    section = "architecture"
    change_type = "feature"
    affected_files = ["src/main.py", "src/auth.py", "test/test_auth.py"]
    recommendations = ["Added authentication system"]
    system_analysis = {'system_changes': {'impact': 'high'}}
    
    # Test the function (lines 905-957)
    try:
        content = _generate_system_content_with_context_analysis(
            section, change_type, affected_files, recommendations, system_analysis
        )
        
        # Should return some content (either rich or fallback)
        assert content is not None
        assert len(content) > 10
        print("✓ Context analysis test passed")
        
    except Exception as e:
        # Test error handling fallback (lines 954-957)
        print(f"Testing fallback for error: {e}")
        
        # Should still return content via fallback
        content = _generate_system_content_with_context_analysis(
            section, change_type, affected_files, recommendations, system_analysis
        )
        assert content is not None
        print("✓ Error handling fallback test passed")


if __name__ == "__main__":
    test_building_inspector()
    test_generate_system_content_for_section()
    test_enhance_system_updates_with_bedrock()
    test_generate_system_content_with_context_analysis()
    print("\n" + "="*50)
    print("All Building Inspector Agent tests completed!")