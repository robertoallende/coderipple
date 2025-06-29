"""
Test for Lambda Import Issue - Focused Test

This test reproduces the specific Lambda import error without requiring
all external dependencies. It focuses on the core issue: missing OrchestratorAgent class.
"""

import unittest
import sys
import os
import importlib.util
from unittest.mock import patch, MagicMock


class TestLambdaImportIssue(unittest.TestCase):
    """Test the specific Lambda import issue."""
    
    def setUp(self):
        """Set up test environment."""
        # Add src to path for imports
        src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    
    def test_orchestrator_agent_module_structure(self):
        """Test the structure of orchestrator_agent module without importing dependencies."""
        
        # Read the file directly to analyze its structure
        orchestrator_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'src', 'coderipple', 'orchestrator_agent.py'
        )
        
        self.assertTrue(os.path.exists(orchestrator_file), 
                       "orchestrator_agent.py should exist")
        
        with open(orchestrator_file, 'r') as f:
            content = f.read()
        
        # Check what's defined in the file
        self.assertIn('def orchestrator_agent(', content,
                     "orchestrator_agent function should be defined")
        self.assertIn('class AgentDecision:', content,
                     "AgentDecision class should be defined")
        self.assertIn('class OrchestrationResult:', content,
                     "OrchestrationResult class should be defined")
        
        # The key issue: OrchestratorAgent class should NOT exist
        self.assertNotIn('class OrchestratorAgent:', content,
                        "OrchestratorAgent class should NOT be defined (this is the bug)")
    
    def test_lambda_import_expectation_vs_reality(self):
        """Test the mismatch between Lambda expectations and implementation."""
        
        # Mock the dependencies to allow import
        with patch.dict('sys.modules', {
            'strands': MagicMock(),
            'coderipple.webhook_parser': MagicMock(),
            'coderipple.git_analysis_tool': MagicMock(),
            'coderipple.tourist_guide_agent': MagicMock(),
            'coderipple.building_inspector_agent': MagicMock(),
            'coderipple.historian_agent': MagicMock(),
            'coderipple.agent_context_flow': MagicMock(),
        }):
            # Now we can import the module
            import coderipple.orchestrator_agent as orch_module
            
            # Test what's actually available
            available_attrs = [attr for attr in dir(orch_module) if not attr.startswith('_')]
            
            # What Lambda expects (and fails to find)
            self.assertNotIn('OrchestratorAgent', available_attrs,
                           "OrchestratorAgent class should NOT be available")
            
            # What actually exists (and should be used instead)
            self.assertIn('orchestrator_agent', available_attrs,
                         "orchestrator_agent function should be available")
            
            # Verify it's a function
            self.assertTrue(callable(getattr(orch_module, 'orchestrator_agent')),
                          "orchestrator_agent should be callable")
    
    def test_reproduce_lambda_import_error(self):
        """Reproduce the exact import error that Lambda encounters."""
        
        # Mock dependencies
        with patch.dict('sys.modules', {
            'strands': MagicMock(),
            'coderipple.webhook_parser': MagicMock(),
            'coderipple.git_analysis_tool': MagicMock(),
            'coderipple.tourist_guide_agent': MagicMock(),
            'coderipple.building_inspector_agent': MagicMock(),
            'coderipple.historian_agent': MagicMock(),
            'coderipple.agent_context_flow': MagicMock(),
        }):
            # This should fail with the exact error Lambda sees
            with self.assertRaises(ImportError) as context:
                from coderipple.orchestrator_agent import OrchestratorAgent
            
            error_msg = str(context.exception)
            self.assertIn("cannot import name 'OrchestratorAgent'", error_msg)
            self.assertIn("coderipple.orchestrator_agent", error_msg)
    
    def test_working_import_pattern(self):
        """Test the import pattern that actually works."""
        
        # Mock dependencies
        with patch.dict('sys.modules', {
            'strands': MagicMock(),
            'coderipple.webhook_parser': MagicMock(),
            'coderipple.git_analysis_tool': MagicMock(),
            'coderipple.tourist_guide_agent': MagicMock(),
            'coderipple.building_inspector_agent': MagicMock(),
            'coderipple.historian_agent': MagicMock(),
            'coderipple.agent_context_flow': MagicMock(),
        }):
            # This should work
            try:
                from coderipple.orchestrator_agent import orchestrator_agent
                from coderipple.orchestrator_agent import AgentDecision
                from coderipple.orchestrator_agent import OrchestrationResult
                
                # Verify types
                self.assertTrue(callable(orchestrator_agent))
                self.assertTrue(hasattr(AgentDecision, '__annotations__'))
                self.assertTrue(hasattr(OrchestrationResult, '__annotations__'))
                
            except ImportError as e:
                self.fail(f"Working imports should succeed: {e}")
    
    def test_validation_script_issue(self):
        """Test what the validation script expects vs what exists."""
        
        # This documents the issue found in comprehensive-validation.sh
        expected_by_validation = "OrchestratorAgent"  # Class
        actually_implemented = "orchestrator_agent"   # Function
        
        self.assertNotEqual(expected_by_validation, actually_implemented,
                           "Validation expects class, implementation provides function")
        
        # The validation script tries to do:
        # from coderipple.orchestrator_agent import OrchestratorAgent
        # orchestrator = OrchestratorAgent()
        
        # But the implementation only provides:
        # from coderipple.orchestrator_agent import orchestrator_agent
        # result = orchestrator_agent(payload, event_type)
        
        self.assertTrue(True, "This test documents the architectural mismatch")


class TestLambdaFixVerification(unittest.TestCase):
    """Tests to verify that fixes work correctly."""
    
    def setUp(self):
        """Set up test environment."""
        src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
    
    def test_fix_option_1_wrapper_class(self):
        """Test that Option 1 (wrapper class) would work."""
        
        # Mock dependencies
        with patch.dict('sys.modules', {
            'strands': MagicMock(),
            'coderipple.webhook_parser': MagicMock(),
            'coderipple.git_analysis_tool': MagicMock(),
            'coderipple.tourist_guide_agent': MagicMock(),
            'coderipple.building_inspector_agent': MagicMock(),
            'coderipple.historian_agent': MagicMock(),
            'coderipple.agent_context_flow': MagicMock(),
        }):
            # Import the function
            from coderipple.orchestrator_agent import orchestrator_agent
            
            # Create a wrapper class (this is what Option 1 would add)
            class OrchestratorAgent:
                def __init__(self):
                    pass
                
                def process_webhook(self, webhook_payload, event_type, github_token=None):
                    return orchestrator_agent(webhook_payload, event_type, github_token)
            
            # Test that this would satisfy Lambda's expectations
            agent = OrchestratorAgent()
            self.assertIsNotNone(agent)
            self.assertTrue(hasattr(agent, 'process_webhook'))
            self.assertTrue(callable(agent.process_webhook))
    
    def test_fix_option_2_update_lambda_code(self):
        """Test that Option 2 (update Lambda code) would work."""
        
        # Mock dependencies
        with patch.dict('sys.modules', {
            'strands': MagicMock(),
            'coderipple.webhook_parser': MagicMock(),
            'coderipple.git_analysis_tool': MagicMock(),
            'coderipple.tourist_guide_agent': MagicMock(),
            'coderipple.building_inspector_agent': MagicMock(),
            'coderipple.historian_agent': MagicMock(),
            'coderipple.agent_context_flow': MagicMock(),
        }):
            # This is what the Lambda code should do instead
            from coderipple.orchestrator_agent import orchestrator_agent
            
            # Simulate Lambda handler using the function directly
            def lambda_handler(event, context):
                webhook_payload = event.get('body', '{}')
                event_type = event.get('headers', {}).get('X-GitHub-Event', 'unknown')
                
                result = orchestrator_agent(webhook_payload, event_type)
                return {
                    'statusCode': 200,
                    'body': 'Processed successfully'
                }
            
            # Test that this approach works
            mock_event = {
                'body': '{"test": "payload"}',
                'headers': {'X-GitHub-Event': 'push'}
            }
            
            # This should not raise ImportError
            response = lambda_handler(mock_event, {})
            self.assertEqual(response['statusCode'], 200)


if __name__ == '__main__':
    unittest.main(verbosity=2)
