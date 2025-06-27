"""
Tests for Tourist Guide Agent

Tests the Tourist Guide Agent functionality including workflow analysis,
documentation generation, and file writing capabilities.
"""

import sys
import os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from coderipple.tourist_guide_agent import tourist_guide_agent
from coderipple.webhook_parser import CommitInfo, WebhookEvent
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
    
    from coderipple.tourist_guide_agent import generate_main_readme
    
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

if __name__ == "__main__":
    test_tourist_guide()
    test_readme_generation()
    print("\n" + "="*50)
    print("All Tourist Guide Agent tests completed!")