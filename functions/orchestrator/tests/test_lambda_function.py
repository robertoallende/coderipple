#!/usr/bin/env python3.12
"""
Comprehensive test suite for CodeRipple Lambda Function (Simplified Strands Pattern)
Tests function functionality and AWS Lambda compatibility
"""

import sys
import os
import unittest
import json
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add function path for testing
FUNCTION_DIR = Path(__file__).parent.parent
FUNCTION_ZIP = FUNCTION_DIR / "function.zip"
BUILD_DIR = FUNCTION_DIR / "build"

class TestLambdaFunction(unittest.TestCase):
    """Test suite for CodeRipple Lambda Function (Simplified Strands Pattern)"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.function_extracted = False
        
        # Extract function if ZIP exists
        if FUNCTION_ZIP.exists():
            with zipfile.ZipFile(FUNCTION_ZIP, 'r') as zip_ref:
                zip_ref.extractall(cls.temp_dir)
            cls.function_extracted = True
            
            # Add function to Python path
            if cls.temp_dir not in sys.path:
                sys.path.insert(0, cls.temp_dir)
        elif BUILD_DIR.exists():
            # Use build directory if ZIP doesn't exist
            sys.path.insert(0, str(BUILD_DIR))
            cls.function_extracted = True
        else:
            # Use function directory directly
            sys.path.insert(0, str(FUNCTION_DIR))
            cls.function_extracted = True
    
    def setUp(self):
        """Set up each test"""
        self.mock_context = Mock()
        self.mock_context.aws_request_id = 'test-request-id-12345'
        self.mock_context.remaining_time_in_millis = Mock(return_value=30000)
        self.mock_context.function_name = 'coderipple-orchestrator'
        self.mock_context.function_version = '1'
    
    def test_function_import(self):
        """Test that Lambda function can be imported"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        try:
            import lambda_function
            self.assertIsNotNone(lambda_function, "Failed to import lambda_function")
            
            # Check required functions exist (simplified pattern)
            self.assertTrue(hasattr(lambda_function, 'lambda_handler'))
            self.assertTrue(hasattr(lambda_function, 'health_check_handler'))
            
            # Check system prompt is defined
            self.assertTrue(hasattr(lambda_function, 'CODERIPPLE_SYSTEM_PROMPT'))
            
        except ImportError as e:
            self.fail(f"Failed to import lambda_function: {e}")
    
    def test_lambda_handler_signature(self):
        """Test lambda_handler has correct signature"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        import inspect
        
        # Check lambda_handler signature
        sig = inspect.signature(lambda_function.lambda_handler)
        params = list(sig.parameters.keys())
        
        self.assertEqual(len(params), 2, "lambda_handler should have 2 parameters")
        self.assertIn('event', params, "lambda_handler should have 'event' parameter")
        self.assertIn('context', params, "lambda_handler should have 'context' parameter")
    
    @patch('strands.Agent')
    def test_lambda_handler_success_mock_strands(self, mock_agent_class):
        """Test successful webhook processing with mocked Strands"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock Strands Agent
        mock_agent_instance = Mock()
        mock_agent_instance.return_value = "Documentation updated successfully"
        mock_agent_class.return_value = mock_agent_instance
        
        import lambda_function
        
        # Test event
        test_event = {
            'body': json.dumps({
                'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'},
                'commits': [{'id': 'abc123', 'message': 'test commit'}]
            })
        }
        
        result = lambda_function.lambda_handler(test_event, self.mock_context)
        
        # Verify response structure
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('body', result)
        self.assertIn('X-CodeRipple-Pattern', result['headers'])
        self.assertEqual(result['headers']['X-CodeRipple-Pattern'], 'simplified-strands')
        
        body = json.loads(result['body'])
        self.assertEqual(body['message'], 'Webhook processed successfully')
        self.assertEqual(body['repository'], 'user/test-repo')
        self.assertEqual(body['pattern'], 'simplified-strands')
        self.assertIn('agent_response', body)
    
    def test_lambda_handler_direct_invocation(self):
        """Test lambda_handler with direct invocation (no body wrapper)"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        # Test direct invocation (no API Gateway wrapper)
        test_event = {
            'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'},
            'commits': [{'id': 'abc123', 'message': 'test commit'}]
        }
        
        # This will fail due to missing Strands, but should handle gracefully
        result = lambda_function.lambda_handler(test_event, self.mock_context)
        
        # Should return error response for missing dependencies
        self.assertEqual(result['statusCode'], 500)
        
        body = json.loads(result['body'])
        self.assertEqual(body['message'], 'Webhook processing failed')
        self.assertIn('error', body)
        self.assertEqual(body['pattern'], 'simplified-strands')
    
    def test_lambda_handler_invalid_json(self):
        """Test lambda_handler with invalid JSON in body"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        # Test event with invalid JSON
        test_event = {
            'body': '{"invalid": json}'  # Invalid JSON
        }
        
        result = lambda_function.lambda_handler(test_event, self.mock_context)
        
        # Should return error response
        self.assertEqual(result['statusCode'], 500)
        
        body = json.loads(result['body'])
        self.assertEqual(body['message'], 'Webhook processing failed')
        self.assertIn('error', body)
    
    @patch('strands.Agent')
    def test_health_check_handler_success(self, mock_agent_class):
        """Test health check with successful Strands import"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        result = lambda_function.health_check_handler({}, self.mock_context)
        
        self.assertEqual(result['statusCode'], 200)
        
        body = json.loads(result['body'])
        self.assertEqual(body['status'], 'healthy')
        self.assertEqual(body['pattern'], 'simplified-strands')
        self.assertTrue(body['strands_available'])
    
    def test_health_check_handler_strands_unavailable(self):
        """Test health check when Strands is not available"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        # This will fail due to missing Strands in test environment
        result = lambda_function.health_check_handler({}, self.mock_context)
        
        self.assertEqual(result['statusCode'], 503)
        
        body = json.loads(result['body'])
        self.assertEqual(body['status'], 'unhealthy')
        self.assertEqual(body['pattern'], 'simplified-strands')
        self.assertIn('error', body)
    
    def test_system_prompt_defined(self):
        """Test that system prompt is properly defined"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        self.assertIsInstance(lambda_function.CODERIPPLE_SYSTEM_PROMPT, str)
        self.assertGreater(len(lambda_function.CODERIPPLE_SYSTEM_PROMPT), 100)
        
        # Check key concepts are mentioned
        prompt = lambda_function.CODERIPPLE_SYSTEM_PROMPT
        self.assertIn('Three Mirror Documentation Framework', prompt)
        self.assertIn('Tourist Guide', prompt)
        self.assertIn('Building Inspector', prompt)
        self.assertIn('Historian', prompt)
        self.assertIn('Layer Selection Decision Tree', prompt)
    
    def test_response_headers(self):
        """Test that response includes correct headers"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        test_event = {'repository': {'name': 'test'}}
        result = lambda_function.lambda_handler(test_event, self.mock_context)
        
        headers = result['headers']
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['Access-Control-Allow-Origin'], '*')
        self.assertEqual(headers['X-CodeRipple-Pattern'], 'simplified-strands')
        self.assertIn('X-Request-ID', headers)


class TestLambdaFunctionBuild(unittest.TestCase):
    """Test the Lambda function build process"""
    
    def test_build_scripts_exist(self):
        """Test that build scripts exist and are executable"""
        build_scripts = [
            FUNCTION_DIR / "1-build.sh",
            FUNCTION_DIR / "build-automation.sh"
        ]
        
        for script in build_scripts:
            self.assertTrue(script.exists(), f"Build script missing: {script}")
            self.assertTrue(os.access(script, os.X_OK), f"Build script not executable: {script}")
    
    def test_lambda_function_exists(self):
        """Test that lambda_function.py exists"""
        lambda_file = FUNCTION_DIR / "lambda_function.py"
        self.assertTrue(lambda_file.exists(), "lambda_function.py missing")
        
        # Test basic Python syntax
        with open(lambda_file, 'r') as f:
            content = f.read()
        
        try:
            compile(content, str(lambda_file), 'exec')
        except SyntaxError as e:
            self.fail(f"Syntax error in lambda_function.py: {e}")
    
    def test_requirements_exist(self):
        """Test that requirements.txt exists and contains Strands dependencies"""
        requirements_file = FUNCTION_DIR / "requirements.txt"
        self.assertTrue(requirements_file.exists(), "requirements.txt missing")
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Should contain simplified Strands dependencies
        self.assertIn('strands-agents', content)
        self.assertIn('strands-agents-tools', content)
    
    def test_function_package_size(self):
        """Test that function package meets size requirements"""
        if FUNCTION_ZIP.exists():
            # Function package should be small (simplified pattern)
            size_bytes = FUNCTION_ZIP.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # Should be much smaller than 50MB (typical Lambda limit)
            self.assertLess(size_mb, 10, f"Function package too large: {size_mb:.1f}MB")
            
            # Should be very small with simplified pattern
            self.assertLess(size_mb, 1, f"Function package should be <1MB with simplified pattern: {size_mb:.1f}MB")


def run_comprehensive_tests():
    """Run comprehensive test suite with detailed reporting"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestLambdaFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestLambdaFunctionBuild))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("🧪 Running CodeRipple Lambda Function Test Suite (Simplified Strands Pattern)")
    print("=" * 70)
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print(f"🧪 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    if result.testsRun > 0:
        print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   • {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"   • {test}: {traceback.split('\\n')[-2]}")
    
    if not result.failures and not result.errors:
        print("\n✅ All tests passed!")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)