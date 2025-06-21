"""
Tests for Orchestrator Agent

Tests the main orchestration logic that coordinates specialist agents
using the Layer Selection Decision Tree and manages cross-agent communication.
"""

import unittest
from unittest.mock import patch, MagicMock, Mock
import sys
import os
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator_agent import (
    orchestrator_agent,
    AgentDecision,
    OrchestrationResult,
    _apply_decision_tree,
    _execute_selected_agents,
    _should_invoke_tourist_guide,
    _should_invoke_building_inspector,
    _should_invoke_historian,
    _generate_orchestration_summary,
    _check_and_bootstrap_user_documentation
)


class TestOrchestrationDataClasses(unittest.TestCase):
    """Test data classes used in orchestration."""
    
    def test_agent_decision_dataclass(self):
        """Test AgentDecision dataclass."""
        decision = AgentDecision(
            agent_type='tourist_guide',
            reason='User interaction changes',
            priority=1,
            context={'change_type': 'feature'}
        )
        
        self.assertEqual(decision.agent_type, 'tourist_guide')
        self.assertEqual(decision.priority, 1)
        self.assertIn('change_type', decision.context)
    
    def test_orchestration_result_dataclass(self):
        """Test OrchestrationResult dataclass."""
        mock_webhook = MagicMock()
        mock_webhook.event_type = 'push'
        
        result = OrchestrationResult(
            webhook_event=mock_webhook,
            git_analysis={'change_type': 'feature'},
            agent_decisions=[],
            summary='Test summary'
        )
        
        self.assertEqual(result.webhook_event, mock_webhook)
        self.assertEqual(result.git_analysis['change_type'], 'feature')
        self.assertEqual(result.summary, 'Test summary')


class TestOrchestratorAgent(unittest.TestCase):
    """Test main orchestrator agent function."""
    
    @patch('orchestrator_agent.GitHubWebhookParser')
    @patch('orchestrator_agent.analyze_git_diff')
    @patch('orchestrator_agent.initialize_shared_context')
    @patch('orchestrator_agent._check_and_bootstrap_user_documentation')
    @patch('orchestrator_agent._apply_decision_tree')
    @patch('orchestrator_agent._execute_selected_agents')
    @patch('orchestrator_agent.get_documentation_status')
    def test_orchestrator_agent_success(self, mock_doc_status, mock_execute, mock_decision_tree,
                                       mock_bootstrap, mock_init_context, mock_git_analysis,
                                       mock_parser_class):
        """Test successful orchestrator agent execution."""
        # Mock webhook parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        mock_webhook_event = MagicMock()
        mock_webhook_event.repository_name = 'test-repo'
        mock_webhook_event.repository_url = 'https://github.com/test/repo'
        mock_webhook_event.after_sha = 'abc123'
        mock_webhook_event.event_type = 'push'
        mock_webhook_event.commits = [MagicMock()]
        mock_webhook_event.commits[0].diff_data = 'sample diff'
        mock_webhook_event.commits[0].message = 'Add new feature'
        
        mock_parser.parse_webhook_payload.return_value = mock_webhook_event
        
        # Mock git analysis
        mock_git_analysis.return_value = {
            'change_type': 'feature',
            'affected_components': ['src/api.py'],
            'confidence': 0.8,
            'summary': 'Feature addition'
        }
        
        # Mock other components
        mock_init_context.return_value = {'status': 'success'}
        mock_bootstrap.return_value = {'status': 'success'}
        mock_decision_tree.return_value = [
            AgentDecision('tourist_guide', 'User changes', 1, {})
        ]
        mock_execute.return_value = {'tourist_guide': {'status': 'success'}}
        mock_doc_status.return_value = {'status': 'success', 'total_files_generated': 5}
        
        # Execute
        result = orchestrator_agent('{"test": "payload"}', 'push', 'token123')
        
        # Assertions
        self.assertIsInstance(result, OrchestrationResult)
        self.assertEqual(result.webhook_event, mock_webhook_event)
        self.assertEqual(result.git_analysis['change_type'], 'feature')
        self.assertEqual(len(result.agent_decisions), 1)
        # The summary should contain the change type and feature info
        self.assertIn('feature changes', result.summary.lower())
        
        # Verify calls
        mock_parser.parse_webhook_payload.assert_called_once_with('{"test": "payload"}', 'push')
        mock_parser.enrich_commits_with_diff_data.assert_called_once()
        mock_git_analysis.assert_called_once_with('sample diff')
    
    @patch('orchestrator_agent.GitHubWebhookParser')
    def test_orchestrator_agent_webhook_parse_failure(self, mock_parser_class):
        """Test orchestrator agent with webhook parsing failure."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_webhook_payload.return_value = None
        
        result = orchestrator_agent('invalid payload', 'push')
        
        self.assertIsInstance(result, OrchestrationResult)
        self.assertIsNone(result.webhook_event)
        self.assertEqual(result.git_analysis, {})
        self.assertEqual(result.agent_decisions, [])
        self.assertIn('Failed to parse', result.summary)
    
    @patch('orchestrator_agent.GitHubWebhookParser')
    @patch('orchestrator_agent.analyze_git_diff')
    @patch('orchestrator_agent.initialize_shared_context')
    @patch('orchestrator_agent._check_and_bootstrap_user_documentation')
    @patch('orchestrator_agent._apply_decision_tree')
    @patch('orchestrator_agent._execute_selected_agents')
    @patch('orchestrator_agent.get_documentation_status')
    def test_orchestrator_agent_no_diff_data(self, mock_doc_status, mock_execute, mock_decision_tree,
                                            mock_bootstrap, mock_init_context, mock_git_analysis,
                                            mock_parser_class):
        """Test orchestrator agent with no diff data (fallback analysis)."""
        # Mock webhook parser
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        mock_webhook_event = MagicMock()
        mock_webhook_event.repository_name = 'test-repo'
        mock_webhook_event.repository_url = 'https://github.com/test/repo'
        mock_webhook_event.after_sha = 'abc123'
        mock_webhook_event.event_type = 'push'
        mock_webhook_event.commits = [MagicMock()]
        mock_webhook_event.commits[0].diff_data = None  # No diff data
        mock_webhook_event.commits[0].message = 'Add new feature'
        mock_webhook_event.commits[0].added_files = ['src/new_feature.py']
        mock_webhook_event.commits[0].modified_files = ['src/api.py']
        mock_webhook_event.commits[0].removed_files = []
        
        mock_parser.parse_webhook_payload.return_value = mock_webhook_event
        
        # Mock other components
        mock_init_context.return_value = {'status': 'success'}
        mock_bootstrap.return_value = {'status': 'success'}
        mock_decision_tree.return_value = []
        mock_execute.return_value = {}
        mock_doc_status.return_value = {'status': 'success'}
        
        # Execute
        result = orchestrator_agent('{"test": "payload"}', 'push')
        
        # Should use fallback analysis
        self.assertEqual(result.git_analysis['change_type'], 'feature')  # Inferred from "Add"
        self.assertIn('src/new_feature.py', result.git_analysis['affected_components'])
        self.assertIn('src/api.py', result.git_analysis['affected_components'])
        self.assertIn('Inferred', result.git_analysis['summary'])
        
        # Git analysis tool should not be called
        mock_git_analysis.assert_not_called()


class TestDecisionTree(unittest.TestCase):
    """Test the Layer Selection Decision Tree logic."""
    
    def test_apply_decision_tree_feature_change(self):
        """Test decision tree for feature changes."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Add new API endpoint'
        
        git_analysis = {
            'change_type': 'feature',
            'affected_components': ['src/api.py', 'src/models.py']
        }
        
        decisions = _apply_decision_tree(mock_webhook, git_analysis)
        
        # Should invoke tourist guide and building inspector
        agent_types = [d.agent_type for d in decisions]
        self.assertIn('tourist_guide', agent_types)
        self.assertIn('building_inspector', agent_types)
        
        # Tourist guide should have higher priority for features
        tourist_guide_decision = next(d for d in decisions if d.agent_type == 'tourist_guide')
        self.assertEqual(tourist_guide_decision.priority, 1)
    
    def test_apply_decision_tree_refactor_change(self):
        """Test decision tree for refactor changes."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Refactor authentication system'
        
        git_analysis = {
            'change_type': 'refactor',
            'affected_components': ['src/auth.py', 'src/middleware.py']
        }
        
        decisions = _apply_decision_tree(mock_webhook, git_analysis)
        
        # Should invoke all three agents for refactoring
        agent_types = [d.agent_type for d in decisions]
        self.assertIn('building_inspector', agent_types)
        self.assertIn('historian', agent_types)
        
        # Historian should have high priority for refactoring
        historian_decision = next(d for d in decisions if d.agent_type == 'historian')
        self.assertEqual(historian_decision.priority, 2)
    
    def test_apply_decision_tree_docs_change(self):
        """Test decision tree for documentation changes."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Update README'
        
        git_analysis = {
            'change_type': 'docs',
            'affected_components': ['README.md']
        }
        
        decisions = _apply_decision_tree(mock_webhook, git_analysis)
        
        # Should primarily invoke tourist guide for docs
        agent_types = [d.agent_type for d in decisions]
        self.assertIn('tourist_guide', agent_types)
        
        # Decisions should be sorted by priority
        priorities = [d.priority for d in decisions]
        self.assertEqual(priorities, sorted(priorities))


class TestAgentInvocationLogic(unittest.TestCase):
    """Test individual agent invocation decision logic."""
    
    def test_should_invoke_tourist_guide_feature(self):
        """Test tourist guide invocation for feature changes."""
        self.assertTrue(_should_invoke_tourist_guide('feature', ['src/api.py']))
    
    def test_should_invoke_tourist_guide_docs(self):
        """Test tourist guide invocation for documentation changes."""
        self.assertTrue(_should_invoke_tourist_guide('docs', ['README.md']))
    
    def test_should_invoke_tourist_guide_user_facing_files(self):
        """Test tourist guide invocation for user-facing files."""
        user_facing_files = [
            'src/cli.py',
            'src/api/handlers.py',
            'docs/getting-started.md',
            'examples/tutorial.py'
        ]
        
        for file in user_facing_files:
            with self.subTest(file=file):
                self.assertTrue(_should_invoke_tourist_guide('unknown', [file]))
    
    def test_should_invoke_tourist_guide_false_cases(self):
        """Test cases where tourist guide should not be invoked."""
        self.assertFalse(_should_invoke_tourist_guide('test', ['tests/test_utils.py']))
        self.assertFalse(_should_invoke_tourist_guide('chore', ['package.json']))  # Changed from requirements.txt
    
    def test_should_invoke_building_inspector_functional_changes(self):
        """Test building inspector invocation for functional changes."""
        functional_changes = ['feature', 'bugfix', 'performance', 'refactor']
        
        for change_type in functional_changes:
            with self.subTest(change_type=change_type):
                self.assertTrue(_should_invoke_building_inspector(change_type, ['src/utils.py']))
    
    def test_should_invoke_building_inspector_core_files(self):
        """Test building inspector invocation for core system files."""
        core_files = [
            'src/main.py',
            'lib/core/engine.py',
            'core/processor.py',
            'index.js'
        ]
        
        for file in core_files:
            with self.subTest(file=file):
                self.assertTrue(_should_invoke_building_inspector('unknown', [file]))
    
    def test_should_invoke_building_inspector_false_cases(self):
        """Test cases where building inspector should not be invoked."""
        self.assertFalse(_should_invoke_building_inspector('docs', ['README.md']))
        self.assertFalse(_should_invoke_building_inspector('test', ['tests/']))
    
    def test_should_invoke_historian_refactor(self):
        """Test historian invocation for refactoring."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Refactor database layer'
        
        self.assertTrue(_should_invoke_historian('refactor', ['src/db.py'], mock_webhook))
    
    def test_should_invoke_historian_major_feature(self):
        """Test historian invocation for major features (multiple files)."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Add user management system'
        
        many_files = ['src/api.py', 'src/models.py', 'src/auth.py', 'src/middleware.py']
        self.assertTrue(_should_invoke_historian('feature', many_files, mock_webhook))
    
    def test_should_invoke_historian_config_changes(self):
        """Test historian invocation for configuration changes."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Update deployment configuration'
        
        config_files = [
            'config/production.yml',
            'Dockerfile',
            'requirements.txt',
            'package.json',
            'terraform/main.tf'
        ]
        
        for file in config_files:
            with self.subTest(file=file):
                self.assertTrue(_should_invoke_historian('unknown', [file], mock_webhook))
    
    def test_should_invoke_historian_decision_keywords(self):
        """Test historian invocation for decision-oriented commit messages."""
        mock_webhook = MagicMock()
        
        decision_messages = [
            'Architecture decision: switch to microservices',
            'Design change: implement event sourcing',
            'Refactor user authentication',
            'Migrate to new database schema',
            'Upgrade to Python 3.9'
        ]
        
        for message in decision_messages:
            with self.subTest(message=message):
                mock_webhook.commits = [MagicMock()]
                mock_webhook.commits[0].message = message
                self.assertTrue(_should_invoke_historian('unknown', ['src/file.py'], mock_webhook))
    
    def test_should_invoke_historian_false_cases(self):
        """Test cases where historian should not be invoked."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Fix typo in README'
        
        self.assertFalse(_should_invoke_historian('docs', ['README.md'], mock_webhook))
        self.assertFalse(_should_invoke_historian('test', ['tests/test_api.py'], mock_webhook))


class TestAgentExecution(unittest.TestCase):
    """Test agent execution logic."""
    
    @patch('orchestrator_agent.tourist_guide_agent')
    @patch('orchestrator_agent.building_inspector_agent')
    @patch('orchestrator_agent.historian_agent')
    def test_execute_selected_agents_success(self, mock_historian, mock_inspector, mock_tourist):
        """Test successful execution of selected agents."""
        # Mock agent responses
        mock_tourist.return_value = MagicMock(summary='Tourist guide completed')
        mock_inspector.return_value = MagicMock(summary='Building inspector completed')
        mock_historian.return_value = MagicMock(summary='Historian completed')
        
        # Mock webhook and analysis
        mock_webhook = MagicMock()
        git_analysis = {'change_type': 'feature'}
        
        # Create agent decisions
        decisions = [
            AgentDecision('tourist_guide', 'User changes', 1, {'test': 'context'}),
            AgentDecision('building_inspector', 'System changes', 1, {'test': 'context'}),
            AgentDecision('historian', 'Decision context', 2, {'test': 'context'})
        ]
        
        # Execute
        with patch('builtins.print'):  # Suppress print statements
            results = _execute_selected_agents(mock_webhook, git_analysis, decisions)
        
        # Verify all agents were called
        mock_tourist.assert_called_once_with(mock_webhook, git_analysis, {'test': 'context'})
        mock_inspector.assert_called_once_with(mock_webhook, git_analysis, {'test': 'context'})
        mock_historian.assert_called_once_with(mock_webhook, git_analysis, {'test': 'context'})
        
        # Verify results
        self.assertIn('tourist_guide', results)
        self.assertIn('building_inspector', results)
        self.assertIn('historian', results)
    
    @patch('orchestrator_agent.tourist_guide_agent')
    def test_execute_selected_agents_error_handling(self, mock_tourist):
        """Test error handling in agent execution."""
        # Mock agent to raise exception
        mock_tourist.side_effect = Exception('Agent failed')
        
        mock_webhook = MagicMock()
        git_analysis = {'change_type': 'feature'}
        decisions = [AgentDecision('tourist_guide', 'User changes', 1, {})]
        
        # Execute
        with patch('builtins.print'):  # Suppress print statements
            results = _execute_selected_agents(mock_webhook, git_analysis, decisions)
        
        # Should handle error gracefully
        self.assertIn('tourist_guide', results)
        self.assertIn('error', results['tourist_guide'])
        self.assertEqual(results['tourist_guide']['error'], 'Agent failed')
    
    def test_execute_selected_agents_unknown_agent(self):
        """Test execution with unknown agent type."""
        mock_webhook = MagicMock()
        git_analysis = {'change_type': 'feature'}
        decisions = [AgentDecision('unknown_agent', 'Unknown', 1, {})]
        
        # Execute
        with patch('builtins.print'):  # Suppress print statements
            results = _execute_selected_agents(mock_webhook, git_analysis, decisions)
        
        # Should not crash, but also not add anything to results
        self.assertEqual(results, {})


class TestSummaryGeneration(unittest.TestCase):
    """Test orchestration summary generation."""
    
    def test_generate_orchestration_summary_no_webhook(self):
        """Test summary generation with no webhook event."""
        summary = _generate_orchestration_summary(None, {}, [], None)
        self.assertEqual(summary, "No valid webhook event to process")
    
    def test_generate_orchestration_summary_no_agents(self):
        """Test summary generation with no agents invoked."""
        mock_webhook = MagicMock()
        mock_webhook.event_type = 'push'
        
        git_analysis = {
            'change_type': 'test',
            'affected_components': ['tests/test_api.py']
        }
        
        summary = _generate_orchestration_summary(mock_webhook, git_analysis, [], None)
        
        self.assertIn('push event', summary)
        self.assertIn('test changes', summary)
        self.assertIn('1 files', summary)
        self.assertIn('No specialist agents required', summary)
    
    def test_generate_orchestration_summary_single_agent(self):
        """Test summary generation with single agent."""
        mock_webhook = MagicMock()
        mock_webhook.event_type = 'push'
        
        git_analysis = {
            'change_type': 'feature',
            'affected_components': ['src/api.py', 'src/models.py']
        }
        
        decisions = [AgentDecision('tourist_guide', 'User changes', 1, {})]
        
        summary = _generate_orchestration_summary(mock_webhook, git_analysis, decisions, None)
        
        self.assertIn('feature changes', summary)
        self.assertIn('2 files', summary)
        self.assertIn('Invoking tourist_guide agent', summary)
    
    def test_generate_orchestration_summary_multiple_agents(self):
        """Test summary generation with multiple agents."""
        mock_webhook = MagicMock()
        mock_webhook.event_type = 'push'
        
        git_analysis = {
            'change_type': 'refactor',
            'affected_components': ['src/core.py']
        }
        
        decisions = [
            AgentDecision('tourist_guide', 'User changes', 1, {}),
            AgentDecision('building_inspector', 'System changes', 1, {}),
            AgentDecision('historian', 'Decision context', 2, {})
        ]
        
        summary = _generate_orchestration_summary(mock_webhook, git_analysis, decisions, None)
        
        self.assertIn('refactor changes', summary)
        self.assertIn('Invoking 3 agents', summary)
        self.assertIn('tourist_guide, building_inspector, historian', summary)
    
    def test_generate_orchestration_summary_with_doc_status(self):
        """Test summary generation with documentation status."""
        mock_webhook = MagicMock()
        mock_webhook.event_type = 'push'
        
        git_analysis = {
            'change_type': 'feature',
            'affected_components': ['src/api.py']
        }
        
        decisions = [AgentDecision('tourist_guide', 'User changes', 1, {})]
        
        doc_status = {
            'status': 'success',
            'total_files_generated': 5,
            'active_agents': 2
        }
        
        summary = _generate_orchestration_summary(mock_webhook, git_analysis, decisions, doc_status)
        
        self.assertIn('Context shared', summary)
        self.assertIn('5 files generated', summary)
        self.assertIn('2 agents', summary)


class TestBootstrapFunctionality(unittest.TestCase):
    """Test bootstrap functionality."""
    
    @patch('orchestrator_agent.check_user_documentation_completeness')
    def test_check_and_bootstrap_complete_documentation(self, mock_check):
        """Test bootstrap when documentation is already complete."""
        mock_check.return_value = {
            'status': 'success',
            'is_complete': True,
            'completion_percentage': 100,
            'existing_files': ['README.md', 'GETTING_STARTED.md']
        }
        
        with patch('builtins.print'):  # Suppress print statements
            result = _check_and_bootstrap_user_documentation()
        
        self.assertEqual(result['status'], 'success')
        self.assertFalse(result['bootstrap_triggered'])
        self.assertEqual(result['action_taken'], 'No action needed')
        self.assertIn('complete', result['message'])
    
    @patch('orchestrator_agent.check_user_documentation_completeness')
    @patch('orchestrator_agent.bootstrap_user_documentation')
    def test_check_and_bootstrap_incomplete_documentation(self, mock_bootstrap, mock_check):
        """Test bootstrap when documentation is incomplete."""
        mock_check.return_value = {
            'status': 'success',
            'is_complete': False,
            'completion_percentage': 60,
            'missing_files': ['GETTING_STARTED.md', 'API_REFERENCE.md']
        }
        
        mock_bootstrap.return_value = {
            'status': 'success',
            'created_files': ['GETTING_STARTED.md', 'API_REFERENCE.md']
        }
        
        with patch('builtins.print'):  # Suppress print statements
            result = _check_and_bootstrap_user_documentation()
        
        self.assertEqual(result['status'], 'success')
        self.assertTrue(result['bootstrap_triggered'])
        self.assertEqual(result['action_taken'], 'Bootstrap user documentation')
        self.assertEqual(len(result['created_files']), 2)
        self.assertIn('Created 2 missing', result['message'])
        
        # Verify bootstrap was called
        mock_bootstrap.assert_called_once()
    
    @patch('orchestrator_agent.check_user_documentation_completeness')
    def test_check_and_bootstrap_check_failure(self, mock_check):
        """Test bootstrap when completeness check fails."""
        mock_check.return_value = {
            'status': 'error',
            'message': 'Failed to check completeness'
        }
        
        result = _check_and_bootstrap_user_documentation()
        
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['bootstrap_triggered'])
        self.assertIn('Failed to check user documentation completeness', result['message'])
    
    @patch('orchestrator_agent.check_user_documentation_completeness')
    @patch('orchestrator_agent.bootstrap_user_documentation')
    def test_check_and_bootstrap_bootstrap_failure(self, mock_bootstrap, mock_check):
        """Test bootstrap when bootstrap process fails."""
        mock_check.return_value = {
            'status': 'success',
            'is_complete': False,
            'completion_percentage': 40,
            'missing_files': ['README.md']
        }
        
        mock_bootstrap.return_value = {
            'status': 'error',
            'message': 'Bootstrap failed',
            'errors': ['Permission denied']
        }
        
        with patch('builtins.print'):  # Suppress print statements
            result = _check_and_bootstrap_user_documentation()
        
        self.assertEqual(result['status'], 'error')
        self.assertTrue(result['bootstrap_triggered'])
        self.assertIn('Bootstrap failed', result['message'])
        self.assertIn('errors', result)
    
    @patch('orchestrator_agent.check_user_documentation_completeness')
    def test_check_and_bootstrap_exception_handling(self, mock_check):
        """Test bootstrap exception handling."""
        mock_check.side_effect = Exception('Unexpected error')
        
        result = _check_and_bootstrap_user_documentation()
        
        self.assertEqual(result['status'], 'error')
        self.assertFalse(result['bootstrap_triggered'])
        self.assertIn('Bootstrap check failed', result['message'])
        self.assertIn('Unexpected error', result['message'])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_decision_tree_empty_analysis(self):
        """Test decision tree with empty git analysis."""
        mock_webhook = MagicMock()
        mock_webhook.commits = []
        
        decisions = _apply_decision_tree(mock_webhook, {})
        
        # Should handle gracefully and return empty decisions
        self.assertEqual(decisions, [])
    
    def test_decision_tree_unknown_change_type(self):
        """Test decision tree with unknown change type."""
        mock_webhook = MagicMock()
        mock_webhook.commits = [MagicMock()]
        mock_webhook.commits[0].message = 'Random change'
        
        git_analysis = {
            'change_type': 'unknown',
            'affected_components': ['some/file.py']
        }
        
        decisions = _apply_decision_tree(mock_webhook, git_analysis)
        
        # Should make decisions based on file patterns even with unknown type
        self.assertIsInstance(decisions, list)
    
    def test_summary_generation_edge_cases(self):
        """Test summary generation with edge cases."""
        mock_webhook = MagicMock()
        mock_webhook.event_type = 'push'
        
        # Empty git analysis
        summary = _generate_orchestration_summary(mock_webhook, {}, [], None)
        self.assertIn('unknown changes', summary)
        self.assertIn('0 files', summary)
        
        # No affected components
        git_analysis = {'change_type': 'feature', 'affected_components': []}
        summary = _generate_orchestration_summary(mock_webhook, git_analysis, [], None)
        self.assertIn('0 files', summary)


# Legacy test function for backward compatibility
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
    unittest.main()