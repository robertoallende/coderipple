"""
Tests for Orchestrator Agent

Tests the Orchestrator Agent functionality including webhook processing,
decision tree logic, and agent coordination.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator_agent import orchestrator_agent


def test_orchestrator():
    """Test the orchestrator with sample webhook data"""
    sample_payload = """{
        "ref": "refs/heads/main",
        "before": "abc123",
        "after": "def456",
        "repository": {
            "full_name": "user/repo",
            "html_url": "https://github.com/user/repo"
        },
        "commits": [{
            "id": "def456",
            "message": "Add new CLI command for user authentication",
            "author": {"name": "Developer"},
            "timestamp": "2024-01-01T12:00:00Z",
            "url": "https://github.com/user/repo/commit/def456",
            "added": ["src/cli.py", "README.md"],
            "modified": ["src/main.py"],
            "removed": []
        }]
    }"""
    
    print("Testing Orchestrator Agent...")
    print("=" * 50)
    
    result = orchestrator_agent(sample_payload, "push")
    
    print(f"Summary: {result.summary}")
    print(f"Change Analysis: {result.git_analysis}")
    print(f"Agent Decisions ({len(result.agent_decisions)}):")
    
    for i, decision in enumerate(result.agent_decisions, 1):
        print(f"  {i}. {decision.agent_type} (Priority {decision.priority})")
        print(f"     Reason: {decision.reason}")
        print(f"     Context: {decision.context}")


if __name__ == "__main__":
    test_orchestrator()