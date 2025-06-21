"""
Tests for Historian Agent

Tests the Historian Agent functionality including decision analysis,
decision documentation generation, and file writing capabilities.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from historian_agent import historian_agent
from webhook_parser import CommitInfo, WebhookEvent
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


if __name__ == "__main__":
    test_historian()