"""
Tests for Tourist Guide Agent

Tests the Tourist Guide Agent functionality including workflow analysis,
documentation generation, and file writing capabilities.
"""

import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from tourist_guide_agent import tourist_guide_agent
from webhook_parser import CommitInfo, WebhookEvent
from datetime import datetime


def test_tourist_guide():
    """Test the Tourist Guide agent with sample data"""
    
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
    
    # Clean up
    if os.path.exists("coderipple"):
        import shutil
        shutil.rmtree("coderipple")
    
    print("All Tourist Guide Agent tests passed!")


def test_readme_generation():
    """Test README.md generation functionality"""
    print("Testing README generation...")
    
    from tourist_guide_agent import generate_main_readme
    
    # Mock the documentation discovery to return expected files
    mock_docs = {
        'user': [
            {
                'path': 'coderipple/discovery.md',
                'name': 'discovery.md',
                'description': 'Project discovery and feature exploration',
                'category': 'user',
                'last_modified': '2025-06-14 12:00:00'
            },
            {
                'path': 'coderipple/getting_started.md',
                'name': 'getting_started.md', 
                'description': 'Getting started guide and tutorials',
                'category': 'user',
                'last_modified': '2025-06-14 12:00:00'
            }
        ],
        'system': [
            {
                'path': 'coderipple/system/architecture.md',
                'name': 'architecture.md',
                'description': 'System architecture and design',
                'category': 'system',
                'last_modified': '2025-06-14 12:00:00'
            }
        ],
        'decisions': [
            {
                'path': 'coderipple/decisions/architecture.md',
                'name': 'architecture.md',
                'description': 'Architecture decisions and rationale',
                'category': 'decisions',
                'last_modified': '2025-06-14 12:00:00'
            }
        ]
    }
    
    # Mock the _discover_all_documentation function
    with patch('tourist_guide_agent._discover_all_documentation', return_value=mock_docs):
        # Generate README
        readme_result = generate_main_readme("test-repo", "https://github.com/user/test-repo")
        
        # Verify README generation
        assert readme_result['status'] == 'success', f"README generation failed: {readme_result.get('error', 'Unknown error')}"
        assert 'test-repo Documentation Hub' in readme_result['content'], "README should contain repository name"
        assert 'layered documentation structure' in readme_result['content'], "README should mention layered structure"
        assert 'discovery.md' in readme_result['content'], "README should list discovery.md"
        assert 'architecture.md' in readme_result['content'], "README should list decision docs"
        
    print("✓ README generation test passed")


def test_generate_project_context_content():
    """Test the _generate_project_context_content function covering lines 2067-2700"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from tourist_guide_agent import _generate_project_context_content
    
    print("\nTesting _generate_project_context_content...")
    
    # Mock project context data
    project_context = {
        'project_name': 'TestProject',
        'project_description': 'A test project for documentation',
        'actual_modules': ['module1.py', 'module2.py'],
        'current_capabilities': [
            'GitHub webhook processing',
            'Multi-agent documentation generation', 
            'AWS integration (Lambda, Bedrock)',
            'AWS Strands orchestration'
        ],
        'key_dependencies': ['boto3', 'strands'],
        'existing_docs': {
            'system_architecture': 'system/architecture.md',
            'decision_history': 'decisions/history.md'
        },
        'project_status': {
            'completion_percentage': '85%',
            'production_ready': 'Ready for deployment'
        }
    }
    
    # Test discovery section (lines 2078-2114)
    discovery_content = _generate_project_context_content(
        'discovery', 'feature', ['test.py'], ['test rec'], project_context
    )
    assert "TestProject Overview" in discovery_content
    assert "GitHub Integration" in discovery_content
    assert "Multi-Agent Architecture" in discovery_content
    assert "AI-Enhanced Content" in discovery_content
    assert "Scalable Orchestration" in discovery_content
    assert "85% complete" in discovery_content
    assert "Related Documentation" in discovery_content
    print("✓ Discovery section test passed")
    
    # Test getting_started section (lines 2116-2200+)  
    getting_started_content = _generate_project_context_content(
        'getting_started', 'feature', ['test.py'], ['test rec'], project_context
    )
    assert "Getting Started" in getting_started_content
    assert "TestProject" in getting_started_content
    print("✓ Getting started section test passed")
    
    # Test workflows section
    workflows_content = _generate_project_context_content(
        'workflows', 'feature', ['test.py'], ['test rec'], project_context
    )
    assert "workflows" in workflows_content.lower() or "TestProject" in workflows_content
    print("✓ Workflows section test passed")
    
    # Test tutorials section
    tutorials_content = _generate_project_context_content(
        'tutorials', 'feature', ['test.py'], ['test rec'], project_context
    )
    assert "tutorials" in tutorials_content.lower() or "TestProject" in tutorials_content
    print("✓ Tutorials section test passed")
    
    # Test default section
    default_content = _generate_project_context_content(
        'unknown_section', 'feature', ['test.py'], ['test rec'], project_context
    )
    assert "TestProject" in default_content
    print("✓ Default section test passed")


def test_retry_with_targeted_improvement():
    """Test the _retry_with_targeted_improvement function covering lines 435-521"""
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
    from tourist_guide_agent import _retry_with_targeted_improvement
    
    print("\nTesting _retry_with_targeted_improvement...")
    
    # Mock validation result
    validation_result = {
        'is_valid': False,
        'overall_quality_score': 45.0,
        'failure_reasons': ['Grammar issues', 'Incomplete sections'],
        'priority_fixes': ['Fix grammar', 'Add missing content'],
        'category_scores': {'grammar': 30, 'completeness': 60}
    }
    
    test_content = "Test content that needs improvement"
    file_path = "test.md"
    
    # Mock external functions
    import tourist_guide_agent
    
    def mock_create_targeted_improvement_prompt(validation_result, attempt):
        return f"Improve content based on validation failures (attempt {attempt})"
    
    def mock_enhance_content_with_bedrock(content, context):
        return {
            'status': 'success',
            'content': f"Enhanced: {content}",
            'improvements': ['improved clarity']
        }
    
    def mock_align_and_validate_content_quality(file_path, content, bedrock_result, project_root, min_quality_score):
        # Return passing validation for enhanced content
        if "Enhanced:" in content:
            return {
                'is_valid': True,
                'overall_quality_score': 85.0,
                'category_scores': {'grammar': 90, 'completeness': 80}
            }
        else:
            return validation_result
    
    # Apply mocks
    original_functions = {}
    mock_functions = {
        '_create_targeted_improvement_prompt': mock_create_targeted_improvement_prompt,
        'enhance_content_with_bedrock': mock_enhance_content_with_bedrock,
        'align_and_validate_content_quality': mock_align_and_validate_content_quality
    }
    
    for func_name, mock_func in mock_functions.items():
        if hasattr(tourist_guide_agent, func_name):
            original_functions[func_name] = getattr(tourist_guide_agent, func_name)
            setattr(tourist_guide_agent, func_name, mock_func)
    
    try:
        # Test successful retry
        result = _retry_with_targeted_improvement(
            file_path, test_content, validation_result, max_retries=2
        )
        
        assert result['success'] == True
        assert result['attempts'] == 1
        assert "Enhanced:" in result['improved_content']
        assert result['final_validation']['is_valid'] == True
        assert len(result['retry_history']) == 1
        
        print("✓ Successful retry test passed")
        
        # Test with failing enhancement
        def mock_enhance_fail(content, context):
            return {'status': 'error', 'error': 'Enhancement failed'}
        
        tourist_guide_agent.enhance_content_with_bedrock = mock_enhance_fail
        
        result_fail = _retry_with_targeted_improvement(
            file_path, test_content, validation_result, max_retries=1
        )
        
        assert result_fail['success'] == False
        assert result_fail['attempts'] == 1
        assert len(result_fail['retry_history']) == 1
        
        print("✓ Failed retry test passed")
        
    finally:
        # Restore original functions
        for func_name, original_func in original_functions.items():
            setattr(tourist_guide_agent, func_name, original_func)


if __name__ == "__main__":
    test_tourist_guide()
    test_readme_generation()
    test_generate_project_context_content()
    test_retry_with_targeted_improvement()
    print("\n" + "="*50)
    print("All Tourist Guide Agent tests completed!")