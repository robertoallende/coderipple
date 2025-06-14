"""
Tests for Tourist Guide Agent

Tests the Tourist Guide Agent functionality including workflow analysis,
documentation generation, and file writing capabilities.
"""

import sys
import os
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


if __name__ == "__main__":
    test_tourist_guide()