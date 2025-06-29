"""
Test Utilities - Standard patterns and utilities for robust testing
Part of Unit 14.3: Enhanced CI/CD Testing Framework
"""

import os
import sys
import importlib
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import patch, MagicMock


class TestUtils:
    """Utility class for consistent test patterns"""
    
    @staticmethod
    def get_module_path(module_name: str) -> str:
        """Get the correct module path for CodeRipple modules"""
        if not module_name.startswith('coderipple.'):
            return f'coderipple.{module_name}'
        return module_name
    
    @staticmethod
    def validate_mock_target(target: str) -> bool:
        """Validate that a mock patch target exists"""
        try:
            parts = target.split('.')
            if len(parts) < 2:
                return False
                
            module_name = '.'.join(parts[:-1])
            attr_name = parts[-1]
            
            module = importlib.import_module(module_name)
            return hasattr(module, attr_name)
            
        except ImportError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def get_file_path(relative_path: str) -> str:
        """Get correct file path for CodeRipple files"""
        if relative_path.startswith('src/') and not relative_path.startswith('src/coderipple/'):
            # Convert old pattern to new pattern
            filename = Path(relative_path).name
            return f'src/coderipple/{filename}'
        return relative_path
    
    @staticmethod
    def setup_test_environment() -> Dict[str, Any]:
        """Setup standard test environment and return environment info"""
        env_info = {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'python_path': sys.path.copy(),
            'coderipple_available': False
        }
        
        try:
            import coderipple
            env_info['coderipple_available'] = True
            env_info['coderipple_location'] = coderipple.__file__
            env_info['coderipple_version'] = getattr(coderipple, '__version__', 'unknown')
        except ImportError:
            pass
            
        return env_info
    
    @staticmethod
    def create_mock_patch(target: str, **kwargs):
        """Create a mock patch with validation"""
        # Ensure target uses correct module path
        if not target.startswith('coderipple.') and any(agent in target for agent in 
                                                       ['orchestrator_agent', 'tourist_guide_agent', 
                                                        'building_inspector_agent', 'historian_agent']):
            target = f'coderipple.{target}'
        
        # Validate target exists
        if not TestUtils.validate_mock_target(target):
            raise ValueError(f"Mock target does not exist: {target}")
            
        return patch(target, **kwargs)
    
    @staticmethod
    def import_coderipple_module(module_name: str):
        """Import a CodeRipple module with proper error handling"""
        full_module_name = TestUtils.get_module_path(module_name)
        
        try:
            return importlib.import_module(full_module_name)
        except ImportError as e:
            raise ImportError(f"Failed to import {full_module_name}: {e}")
    
    @staticmethod
    def create_test_context() -> Dict[str, Any]:
        """Create standard test context"""
        return {
            'repository_name': 'test-repo',
            'repository_url': 'https://github.com/user/test-repo',
            'branch': 'main',
            'commit_sha': 'abc123',
            'timestamp': '2025-06-27T12:00:00Z'
        }
    
    @staticmethod
    def create_mock_webhook_event() -> Dict[str, Any]:
        """Create a standard mock webhook event for testing"""
        return {
            'repository': {
                'name': 'test-repo',
                'full_name': 'user/test-repo',
                'html_url': 'https://github.com/user/test-repo'
            },
            'commits': [{
                'id': 'abc123',
                'message': 'Test commit',
                'author': {
                    'name': 'Test User',
                    'email': 'test@example.com'
                },
                'added': ['new_file.py'],
                'modified': ['existing_file.py'],
                'removed': []
            }],
            'head_commit': {
                'id': 'abc123',
                'message': 'Test commit'
            }
        }
    
    @staticmethod
    def create_mock_git_diff() -> str:
        """Create a standard mock git diff for testing"""
        return """diff --git a/test_file.py b/test_file.py
index abc123..def456 100644
--- a/test_file.py
+++ b/test_file.py
@@ -1,3 +1,6 @@
 def existing_function():
     return "existing"
 
+def new_function():
+    return "new"
+
"""

    @staticmethod
    def assert_import_works(module_name: str) -> bool:
        """Assert that a module can be imported successfully"""
        try:
            TestUtils.import_coderipple_module(module_name)
            return True
        except ImportError:
            return False
    
    @staticmethod
    def get_test_file_issues(test_file_path: str) -> Dict[str, Any]:
        """Analyze a test file for common issues"""
        issues = {
            'legacy_imports': [],
            'incorrect_patches': [],
            'wrong_file_paths': [],
            'syntax_errors': []
        }
        
        try:
            with open(test_file_path, 'r') as f:
                content = f.read()
            
            # Check for legacy import patterns
            import re
            legacy_patterns = re.findall(r'from\s+(orchestrator_agent|tourist_guide_agent|building_inspector_agent|historian_agent)\s+import', content)
            issues['legacy_imports'] = legacy_patterns
            
            # Check for incorrect patch targets
            patch_patterns = re.findall(r"@patch\('([^']+)'\)", content)
            for patch in patch_patterns:
                if not patch.startswith('coderipple.') and any(agent in patch for agent in 
                                                             ['orchestrator_agent', 'tourist_guide_agent', 
                                                              'building_inspector_agent', 'historian_agent']):
                    issues['incorrect_patches'].append(patch)
            
            # Check for wrong file paths
            file_refs = re.findall(r'"([^"]*\.py)"', content)
            for ref in file_refs:
                if ref.startswith('src/') and not ref.startswith('src/coderipple/'):
                    issues['wrong_file_paths'].append(ref)
                    
        except Exception as e:
            issues['syntax_errors'].append(str(e))
            
        return issues


class MockHelper:
    """Helper class for creating consistent mocks"""
    
    @staticmethod
    def create_bedrock_response(content: str, quality_score: float = 0.85) -> Dict[str, Any]:
        """Create a standard mock Bedrock response"""
        return {
            'status': 'success',
            'content': [{
                'json': {
                    'enhanced_content': f"Enhanced: {content}",
                    'improvements_made': ['improved clarity', 'added technical details'],
                    'quality_score': quality_score
                }
            }]
        }
    
    @staticmethod
    def create_git_analysis_result() -> Dict[str, Any]:
        """Create a standard mock git analysis result"""
        return {
            'files_changed': ['test_file.py'],
            'lines_added': 3,
            'lines_removed': 0,
            'change_type': 'feature',
            'impact_level': 'medium',
            'summary': 'Added new function'
        }
    
    @staticmethod
    def create_documentation_update(section: str = "test_section", 
                                  action: str = "update", 
                                  content: str = "Test content") -> Dict[str, Any]:
        """Create a standard documentation update object"""
        return {
            'section': section,
            'action': action,
            'content': content,
            'reason': 'Test update',
            'priority': 1
        }


# Test pattern examples and templates
TEST_PATTERNS = {
    'standard_import': """
# ✅ Correct import pattern
from coderipple.module_name import function_name
""",
    
    'mock_patch': """
# ✅ Correct mock patch pattern
@patch('coderipple.module_name.function_name')
def test_function(self, mock_function):
    pass
""",
    
    'file_path': """
# ✅ Correct file path pattern
spec = importlib.util.spec_from_file_location("__main__", "src/coderipple/module_name.py")
""",
    
    'test_setup': """
# ✅ Standard test setup pattern
def setUp(self):
    self.test_utils = TestUtils()
    self.env_info = self.test_utils.setup_test_environment()
    self.context = self.test_utils.create_test_context()
"""
}


def validate_test_patterns():
    """Validate that test patterns are being followed"""
    print("🔍 Validating test patterns across codebase...")
    
    test_files = list(Path('tests').glob('test_*.py'))
    issues_found = 0
    
    for test_file in test_files:
        issues = TestUtils.get_test_file_issues(str(test_file))
        
        total_issues = sum(len(v) for v in issues.values())
        if total_issues > 0:
            print(f"❌ {test_file}: {total_issues} issues found")
            issues_found += total_issues
        else:
            print(f"✅ {test_file}: No issues")
    
    if issues_found == 0:
        print("✅ All test files follow standard patterns")
    else:
        print(f"❌ Found {issues_found} pattern issues across test files")
    
    return issues_found == 0


if __name__ == "__main__":
    validate_test_patterns()
