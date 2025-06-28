#!/usr/bin/env python3.13
"""
Comprehensive test suite for CodeRipple Package Layer
Tests layer functionality, agent imports, and AWS Lambda compatibility
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
LAYER_ZIP = LAYER_DIR / "coderipple-package-layer.zip"
BUILD_DIR = LAYER_DIR / "build" / "python"
CODERIPPLE_SOURCE = LAYER_DIR / ".." / ".." / "coderipple"

class TestCodeRipplePackageLayer(unittest.TestCase):
    """Test suite for CodeRipple Package Layer"""
    
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
        
        # Check for CodeRipple package
        coderipple_dir = os.path.join(python_dir, 'coderipple')
        self.assertTrue(os.path.exists(coderipple_dir), "coderipple package missing from layer")
        
        # Check for critical agent files
        critical_agents = [
            'tourist_guide_agent.py',
            'building_inspector_agent.py', 
            'historian_agent.py',
            'orchestrator_agent.py'
        ]
        
        for agent in critical_agents:
            agent_path = os.path.join(coderipple_dir, agent)
            self.assertTrue(
                os.path.exists(agent_path),
                f"Agent {agent} not found in layer"
            )
    
    def test_coderipple_package_import(self):
        """Test that CodeRipple package can be imported"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        try:
            import coderipple
            self.assertIsNotNone(coderipple, "Failed to import coderipple package")
            
        except ImportError as e:
            self.fail(f"Failed to import coderipple package: {e}")
    
    def test_agent_imports(self):
        """Test that all agents can be imported"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        agents = [
            'coderipple.tourist_guide_agent',
            'coderipple.building_inspector_agent',
            'coderipple.historian_agent', 
            'coderipple.orchestrator_agent'
        ]
        
        for agent_module in agents:
            with self.subTest(agent=agent_module):
                try:
                    module = __import__(agent_module, fromlist=[''])
                    self.assertIsNotNone(module, f"Failed to import {agent_module}")
                except ImportError as e:
                    self.fail(f"Failed to import {agent_module}: {e}")
    
    def test_tool_imports(self):
        """Test that supporting tools can be imported"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        tools = [
            'coderipple.config',
            'coderipple.webhook_parser',
            'coderipple.git_analysis_tool',
            'coderipple.content_generation_tools'
        ]
        
        for tool_module in tools:
            with self.subTest(tool=tool_module):
                try:
                    module = __import__(tool_module, fromlist=[''])
                    self.assertIsNotNone(module, f"Failed to import {tool_module}")
                except ImportError as e:
                    self.fail(f"Failed to import {tool_module}: {e}")
    
    def test_layer_size_limits(self):
        """Test that layer meets AWS Lambda size limits"""
        if not LAYER_ZIP.exists():
            self.skipTest("Layer ZIP not found")
        
        # AWS Lambda layer limits
        MAX_LAYER_SIZE = 250 * 1024 * 1024  # 250MB uncompressed
        MAX_ZIP_SIZE = 50 * 1024 * 1024     # 50MB compressed
        
        # Test compressed size
        zip_size = LAYER_ZIP.stat().st_size
        self.assertLess(
            zip_size, MAX_ZIP_SIZE,
            f"Layer ZIP size ({zip_size / 1024 / 1024:.1f}MB) exceeds limit"
        )
    
    def test_import_performance(self):
        """Test import performance for Lambda cold starts"""
        if not self.layer_extracted:
            self.skipTest("Layer ZIP not found")
        
        # Test import times for critical modules
        import_tests = [
            'coderipple',
            'coderipple.orchestrator_agent',
            'coderipple.config'
        ]
        
        for module in import_tests:
            with self.subTest(module=module):
                start_time = time.time()
                try:
                    __import__(module)
                    import_time = time.time() - start_time
                    
                    self.assertLess(
                        import_time, 2.0,
                        f"{module} import time ({import_time:.3f}s) too slow for Lambda"
                    )
                except ImportError:
                    self.fail(f"Could not import {module}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test environment"""
        import shutil
        if hasattr(cls, 'temp_dir') and os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)


class TestPackageLayerBuildProcess(unittest.TestCase):
    """Test the package layer build process"""
    
    def test_build_scripts_exist(self):
        """Test that all build scripts exist and are executable"""
        build_scripts = [
            LAYER_DIR / "1-install.sh",
            LAYER_DIR / "2-package.sh", 
            LAYER_DIR / "3-validate.sh"
        ]
        
        for script in build_scripts:
            self.assertTrue(script.exists(), f"Build script missing: {script}")
            self.assertTrue(os.access(script, os.X_OK), f"Build script not executable: {script}")


def run_comprehensive_tests():
    """Run comprehensive test suite with detailed reporting"""
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCodeRipplePackageLayer))
    suite.addTests(loader.loadTestsFromTestCase(TestPackageLayerBuildProcess))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(
        verbosity=2,
        stream=sys.stdout,
        descriptions=True,
        failfast=False
    )
    
    print("🧪 Running CodeRipple Package Layer Test Suite")
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
    
    if not result.failures and not result.errors:
        print("\n✅ All tests passed!")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)
