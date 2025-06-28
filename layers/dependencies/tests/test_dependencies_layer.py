#!/usr/bin/env python3.12
"""
Comprehensive test suite for CodeRipple Dependencies Layer
Tests layer functionality, performance, and AWS Lambda compatibility
"""

import sys
import os
import unittest
import tempfile
import zipfile
import json
import time
import subprocess
from pathlib import Path

# Add layer path for testing
LAYER_DIR = Path(__file__).parent.parent
LAYER_ZIP = LAYER_DIR / "coderipple-dependencies-layer.zip"
BUILD_DIR = LAYER_DIR / "build" / "python"

class TestDependenciesLayer(unittest.TestCase):
    """Test suite for CodeRipple Dependencies Layer"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.temp_dir = tempfile.mkdtemp()
        cls.layer_extracted = False
        
        # Extract layer if ZIP exists
        if LAYER_ZIP.exists():
            with zipfile.ZipFile(LAYER_ZIP, 'r') as zip_ref:
                zip_ref.extractall(cls.temp_dir)
            cls.layer_extracted = True
            
            # Add layer to Python path
            layer_python_path = os.path.join(cls.temp_dir, 'python')
            if layer_python_path not in sys.path:
                sys.path.insert(0, layer_python_path)
    
    def test_layer_structure(self):
        """Test that layer has correct directory structure"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        python_dir = os.path.join(self.temp_dir, 'python')
        self.assertTrue(os.path.exists(python_dir), "python/ directory missing from layer")
        
        # Check for critical packages
        critical_packages = [
            'boto3', 'botocore', 'strands', 'requests', 
            'pydantic', 'urllib3', 'httpx'
        ]
        
        for package in critical_packages:
            package_path = os.path.join(python_dir, package)
            self.assertTrue(
                os.path.exists(package_path) or 
                os.path.exists(package_path + '.py') or
                any(f.startswith(package) for f in os.listdir(python_dir)),
                f"Package {package} not found in layer"
            )
    
    def test_critical_imports(self):
        """Test that all critical packages can be imported"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        critical_imports = {
            'boto3': 'AWS SDK',
            'botocore': 'AWS Core',
            'strands': 'Multi-agent framework',
            'requests': 'HTTP library',
            'pydantic': 'Data validation',
            'urllib3': 'HTTP client',
            'httpx': 'Async HTTP client'
        }
        
        for module_name, description in critical_imports.items():
            with self.subTest(module=module_name):
                try:
                    module = __import__(module_name)
                    self.assertIsNotNone(module, f"Failed to import {module_name} ({description})")
                except ImportError as e:
                    self.fail(f"Failed to import {module_name} ({description}): {e}")
    
    def test_package_versions(self):
        """Test that packages have expected versions"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        version_requirements = {
            'boto3': '1.38.32',
            'requests': '2.32.3',
            'pydantic': '2.11.5'
        }
        
        for package_name, expected_version in version_requirements.items():
            with self.subTest(package=package_name):
                try:
                    module = __import__(package_name)
                    actual_version = getattr(module, '__version__', 'unknown')
                    self.assertEqual(
                        actual_version, expected_version,
                        f"{package_name} version mismatch: expected {expected_version}, got {actual_version}"
                    )
                except ImportError:
                    self.fail(f"Could not import {package_name} to check version")
    
    def test_aws_functionality(self):
        """Test basic AWS SDK functionality"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        try:
            import boto3
            
            # Test session creation
            session = boto3.Session()
            self.assertIsNotNone(session, "Failed to create boto3 session")
            
            # Test client creation (without actual AWS calls)
            try:
                client = session.client('lambda', region_name='us-west-2')
                self.assertIsNotNone(client, "Failed to create Lambda client")
            except Exception as e:
                # This is expected without AWS credentials
                self.assertIn('credentials', str(e).lower(), f"Unexpected error: {e}")
                
        except ImportError as e:
            self.fail(f"Failed to import boto3: {e}")
    
    def test_http_functionality(self):
        """Test HTTP library functionality"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        try:
            import requests
            
            # Test basic requests functionality (no actual HTTP calls)
            session = requests.Session()
            self.assertIsNotNone(session, "Failed to create requests session")
            
            # Test URL building
            from urllib.parse import urljoin
            url = urljoin('https://api.example.com/', 'endpoint')
            self.assertEqual(url, 'https://api.example.com/endpoint')
            
        except ImportError as e:
            self.fail(f"Failed to import requests: {e}")
    
    def test_data_validation(self):
        """Test Pydantic data validation functionality"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        try:
            from pydantic import BaseModel, ValidationError
            
            class TestModel(BaseModel):
                name: str
                value: int
                
            # Test valid data
            valid_obj = TestModel(name="test", value=42)
            self.assertEqual(valid_obj.name, "test")
            self.assertEqual(valid_obj.value, 42)
            
            # Test validation error
            with self.assertRaises(ValidationError):
                TestModel(name="test", value="not_an_int")
                
        except ImportError as e:
            self.fail(f"Failed to import pydantic: {e}")
    
    def test_strands_framework(self):
        """Test Strands multi-agent framework"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        try:
            import strands
            
            # Basic import test - strands may not have full functionality without proper setup
            self.assertIsNotNone(strands, "Failed to import strands")
            
            # Test if we can access basic strands components
            try:
                from strands import Agent
                self.assertTrue(hasattr(strands, 'Agent') or Agent is not None)
            except (ImportError, AttributeError):
                # This might be expected depending on strands structure
                pass
                
        except ImportError as e:
            self.fail(f"Failed to import strands: {e}")
    
    def test_layer_size_limits(self):
        """Test that layer meets AWS Lambda size limits"""
        if not LAYER_ZIP.exists():
            self.skipTest("Layer ZIP not found")
        
        # AWS Lambda layer limits
        MAX_LAYER_SIZE = 250 * 1024 * 1024  # 250MB uncompressed
        MAX_ZIP_SIZE = 50 * 1024 * 1024     # 50MB compressed (typical limit)
        
        # Test compressed size
        zip_size = LAYER_ZIP.stat().st_size
        self.assertLess(
            zip_size, MAX_ZIP_SIZE,
            f"Layer ZIP size ({zip_size / 1024 / 1024:.1f}MB) exceeds typical limit ({MAX_ZIP_SIZE / 1024 / 1024}MB)"
        )
        
        # Test uncompressed size if build directory exists
        if BUILD_DIR.exists():
            uncompressed_size = sum(
                f.stat().st_size for f in BUILD_DIR.rglob('*') if f.is_file()
            )
            self.assertLess(
                uncompressed_size, MAX_LAYER_SIZE,
                f"Layer uncompressed size ({uncompressed_size / 1024 / 1024:.1f}MB) exceeds AWS limit ({MAX_LAYER_SIZE / 1024 / 1024}MB)"
            )
    
    def test_import_performance(self):
        """Test import performance for Lambda cold starts"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        # Test import times for critical packages
        import_tests = ['boto3', 'requests', 'pydantic', 'strands']
        
        for package in import_tests:
            with self.subTest(package=package):
                start_time = time.time()
                try:
                    __import__(package)
                    import_time = time.time() - start_time
                    
                    # Warn if import takes too long (impacts Lambda cold start)
                    if import_time > 1.0:
                        print(f"⚠️  {package} import time: {import_time:.3f}s (may impact cold start)")
                    
                    self.assertLess(
                        import_time, 5.0,
                        f"{package} import time ({import_time:.3f}s) too slow for Lambda"
                    )
                except ImportError:
                    self.fail(f"Could not import {package}")
    
    def test_lambda_simulation(self):
        """Simulate Lambda environment and test functionality"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        def mock_lambda_handler(event, context):
            """Mock Lambda handler using layer dependencies"""
            import boto3
            import requests
            import pydantic
            
            return {
                'statusCode': 200,
                'body': {
                    'boto3_version': boto3.__version__,
                    'requests_version': requests.__version__,
                    'pydantic_version': pydantic.__version__,
                    'message': 'Layer dependencies functional'
                }
            }
        
        # Test handler execution
        result = mock_lambda_handler({}, {})
        
        self.assertEqual(result['statusCode'], 200)
        self.assertIn('boto3_version', result['body'])
        self.assertIn('requests_version', result['body'])
        self.assertIn('pydantic_version', result['body'])
        self.assertEqual(result['body']['message'], 'Layer dependencies functional')
    
    def test_layer_metadata(self):
        """Test layer metadata file"""
        metadata_file = LAYER_DIR / "metadata" / "layer-metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Test required metadata fields
            required_fields = [
                'layer_name', 'description', 'compatible_runtimes',
                'compatible_architectures', 'created_date'
            ]
            
            for field in required_fields:
                self.assertIn(field, metadata, f"Missing metadata field: {field}")
            
            # Test specific values
            self.assertEqual(metadata['layer_name'], 'coderipple-dependencies')
            self.assertIn('python3.12', metadata['compatible_runtimes'])
            self.assertIn('x86_64', metadata['compatible_architectures'])
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)


class TestLayerBuildProcess(unittest.TestCase):
    """Test the layer build process"""
    
    def test_build_scripts_exist(self):
        """Test that all build scripts exist and are executable"""
        build_scripts = [
            LAYER_DIR / "1-install.sh",
            LAYER_DIR / "2-package.sh", 
            LAYER_DIR / "3-validate.sh",
            LAYER_DIR / "build-automation.sh"
        ]
        
        for script in build_scripts:
            self.assertTrue(script.exists(), f"Build script missing: {script}")
            self.assertTrue(os.access(script, os.X_OK), f"Build script not executable: {script}")
    
    def test_requirements_file(self):
        """Test requirements.txt file"""
        requirements_file = LAYER_DIR / "requirements.txt"
        self.assertTrue(requirements_file.exists(), "requirements.txt missing")
        
        with open(requirements_file, 'r') as f:
            content = f.read()
        
        # Test for critical packages
        critical_packages = [
            'boto3==', 'botocore==', 'strands-agents==',
            'requests==', 'pydantic==', 'urllib3=='
        ]
        
        for package in critical_packages:
            self.assertIn(package, content, f"Missing package in requirements.txt: {package}")
    
    def test_build_automation_functionality(self):
        """Test build automation script functionality"""
        automation_script = LAYER_DIR / "build-automation.sh"
        
        if automation_script.exists():
            # Test script syntax
            result = subprocess.run(
                ['bash', '-n', str(automation_script)],
                capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0, f"Syntax error in build automation script: {result.stderr}")


def run_comprehensive_tests():
    """Run comprehensive test suite with detailed reporting"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDependenciesLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestLayerBuildProcess))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("🧪 Running CodeRipple Dependencies Layer Test Suite")
    print("=" * 60)
    
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"🧪 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
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
