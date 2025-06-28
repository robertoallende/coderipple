#!/usr/bin/env python3.13
"""
Comprehensive test suite for CodeRipple Lambda Function (Layer-based)
Tests function functionality, layer integration, and AWS Lambda compatibility
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
    """Test suite for CodeRipple Lambda Function"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.function_extracted = False
        
        # Mock environment variables for layer-based architecture
        os.environ['CODERIPPLE_LAYER_BASED'] = 'true'
        os.environ['CODERIPPLE_ARCHITECTURE'] = 'single-lambda-with-layers'
        os.environ['CODERIPPLE_DEPENDENCIES_LAYER'] = 'arn:aws:lambda:us-west-2:123456789012:layer:coderipple-dependencies:1'
        os.environ['CODERIPPLE_PACKAGE_LAYER'] = 'arn:aws:lambda:us-west-2:123456789012:layer:coderipple-package:1'
        
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
            
            # Check required functions exist
            self.assertTrue(hasattr(lambda_function, 'lambda_handler'))
            self.assertTrue(hasattr(lambda_function, 'health_check_handler'))
            self.assertTrue(hasattr(lambda_function, 'layer_info_handler'))
            
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
    
    @patch('lambda_function.validate_layer_imports')
    def test_layer_validation_success(self, mock_validate):
        """Test successful layer validation"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock successful layer validation
        mock_validate.return_value = {
            'dependencies_layer': True,
            'package_layer': True,
            'errors': []
        }
        
        import lambda_function
        
        result = lambda_function.validate_layer_imports()
        
        self.assertTrue(result['dependencies_layer'])
        self.assertTrue(result['package_layer'])
        self.assertEqual(len(result['errors']), 0)
    
    @patch('lambda_function.validate_layer_imports')
    @patch('lambda_function.OrchestratorAgent')
    @patch('lambda_function.parse_github_webhook')
    @patch('lambda_function.CodeRippleConfig')
    def test_lambda_handler_success(self, mock_config, mock_parser, mock_orchestrator, mock_validate):
        """Test successful webhook processing"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock successful layer validation
        mock_validate.return_value = {
            'dependencies_layer': True,
            'package_layer': True,
            'errors': []
        }
        
        # Mock webhook parsing
        mock_parser.return_value = {
            'repository': {'name': 'test-repo'},
            'commits': [{'id': 'abc123', 'message': 'test commit'}]
        }
        
        # Mock orchestrator
        mock_orchestrator_instance = Mock()
        mock_orchestrator_instance.process_webhook.return_value = {
            'agents_invoked': ['tourist_guide', 'building_inspector'],
            'documentation_updated': True
        }
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Mock config
        mock_config_instance = Mock()
        mock_config_instance.doc_strategy = 'github_direct'
        mock_config.return_value = mock_config_instance
        
        import lambda_function
        
        # Test event
        test_event = {
            'body': json.dumps({
                'repository': {'name': 'test-repo'},
                'commits': [{'id': 'abc123', 'message': 'test commit'}]
            })
        }
        
        result = lambda_function.lambda_handler(test_event, self.mock_context)
        
        # Verify response structure
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('body', result)
        
        body = json.loads(result['body'])
        self.assertEqual(body['message'], 'Webhook processed successfully')
        self.assertEqual(body['repository'], 'test-repo')
        self.assertTrue(body['layer_based'])
        self.assertEqual(body['architecture'], 'single-lambda-with-layers')
    
    @patch('lambda_function.validate_layer_imports')
    def test_lambda_handler_layer_failure(self, mock_validate):
        """Test lambda_handler with layer validation failure"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock layer validation failure
        mock_validate.return_value = {
            'dependencies_layer': False,
            'package_layer': True,
            'errors': ['Dependencies layer import failed: No module named boto3']
        }
        
        import lambda_function
        
        test_event = {'repository': {'name': 'test-repo'}}
        
        result = lambda_function.lambda_handler(test_event, self.mock_context)
        
        # Should return error response
        self.assertEqual(result['statusCode'], 500)
        
        body = json.loads(result['body'])
        self.assertEqual(body['message'], 'Webhook processing failed')
        self.assertIn('error', body)
    
    @patch('lambda_function.validate_layer_imports')
    def test_health_check_handler_healthy(self, mock_validate):
        """Test health check with healthy layers"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock successful layer validation
        mock_validate.return_value = {
            'dependencies_layer': True,
            'package_layer': True,
            'errors': []
        }
        
        import lambda_function
        
        result = lambda_function.health_check_handler({}, self.mock_context)
        
        self.assertEqual(result['statusCode'], 200)
        
        body = json.loads(result['body'])
        self.assertEqual(body['status'], 'healthy')
        self.assertTrue(body['layer_based'])
        self.assertTrue(body['layers']['dependencies']['functional'])
        self.assertTrue(body['layers']['package']['functional'])
    
    @patch('lambda_function.validate_layer_imports')
    def test_health_check_handler_unhealthy(self, mock_validate):
        """Test health check with unhealthy layers"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock layer validation failure
        mock_validate.return_value = {
            'dependencies_layer': False,
            'package_layer': True,
            'errors': ['Dependencies layer failed']
        }
        
        import lambda_function
        
        result = lambda_function.health_check_handler({}, self.mock_context)
        
        self.assertEqual(result['statusCode'], 503)
        
        body = json.loads(result['body'])
        self.assertEqual(body['status'], 'unhealthy')
        self.assertFalse(body['layers']['dependencies']['functional'])
    
    @patch('lambda_function.validate_layer_imports')
    def test_layer_info_handler(self, mock_validate):
        """Test layer info handler"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        # Mock layer validation
        mock_validate.return_value = {
            'dependencies_layer': True,
            'package_layer': True,
            'errors': []
        }
        
        import lambda_function
        
        result = lambda_function.layer_info_handler({}, self.mock_context)
        
        self.assertEqual(result['statusCode'], 200)
        
        body = json.loads(result['body'])
        self.assertEqual(body['architecture']['type'], 'single-lambda-with-layers')
        self.assertTrue(body['architecture']['layer_based'])
        self.assertIn('dependencies', body['layers'])
        self.assertIn('package', body['layers'])
    
    def test_environment_variables(self):
        """Test environment variable handling"""
        if not self.function_extracted:
            self.skipTest("Function code not available")
        
        import lambda_function
        
        # Test that environment variables are properly read
        self.assertTrue(lambda_function.LAYER_BASED)
        self.assertEqual(lambda_function.ARCHITECTURE, 'single-lambda-with-layers')
        self.assertIn('coderipple-dependencies', lambda_function.DEPENDENCIES_LAYER)
        self.assertIn('coderipple-package', lambda_function.PACKAGE_LAYER)
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)


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
    
    def test_function_package_size(self):
        """Test that function package meets size requirements"""
        if FUNCTION_ZIP.exists():
            # Function package should be small (layer-based)
            size_bytes = FUNCTION_ZIP.stat().st_size
            size_mb = size_bytes / (1024 * 1024)
            
            # Should be much smaller than 50MB (typical Lambda limit)
            self.assertLess(size_mb, 10, f"Function package too large: {size_mb:.1f}MB")
            
            # Should be significantly smaller than monolithic approach
            self.assertLess(size_mb, 1, f"Function package should be <1MB with layers: {size_mb:.1f}MB")


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
    
    print("🧪 Running CodeRipple Lambda Function Test Suite")
    print("=" * 60)
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
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
