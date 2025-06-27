"""
Tests for Git Analysis Tool

Tests the git diff analysis functionality that categorizes changes
and identifies affected components for intelligent documentation updates.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from coderipple.git_analysis_tool import (
    analyze_git_diff,
    _extract_affected_files,
    _determine_change_type,
    _calculate_confidence,
    _generate_summary,
    test_tool_directly
)

class TestGitAnalysisTool(unittest.TestCase):
    """Test the main git analysis tool function."""

    def test_analyze_git_diff_feature_change(self):
        """Test analysis of feature addition changes."""
        feature_diff = """diff --git a/src/new_feature.py b/src/new_feature.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/new_feature.py
@@ -0,0 +1,15 @@
+def new_function():
+    '''Implement new feature functionality'''
+    return "new feature"
+
+class NewFeatureHandler:
+    def __init__(self):
+        pass
"""
        
        result = analyze_git_diff(feature_diff)
        
        self.assertEqual(result['change_type'], 'feature')
        self.assertIn('src/new_feature.py', result['affected_components'])
        self.assertGreater(result['confidence'], 0.5)
        self.assertIn('feature', result['summary'])

    def test_analyze_git_diff_bugfix_change(self):
        """Test analysis of bug fix changes."""
        bugfix_diff = """diff --git a/src/api.py b/src/api.py
index 1234567..abcdefg 100644
--- a/src/api.py
+++ b/src/api.py
@@ -10,7 +10,7 @@ def process_request(data):
     if not data:
-        return None  # This was causing issues
+        return {'error': 'No data provided'}  # Fix: proper error handling
     
     return process_data(data)
"""
        
        result = analyze_git_diff(bugfix_diff)
        
        self.assertEqual(result['change_type'], 'bugfix')
        self.assertIn('src/api.py', result['affected_components'])
        self.assertGreater(result['confidence'], 0.5)
        self.assertIn('bugfix', result['summary'])

    def test_analyze_git_diff_test_change(self):
        """Test analysis of test file changes."""
        test_diff = """diff --git a/tests/test_api.py b/tests/test_api.py
index 1234567..abcdefg 100644
--- a/tests/test_api.py
+++ b/tests/test_api.py
@@ -20,6 +20,12 @@ class TestAPI(unittest.TestCase):
         result = api.process_request(data)
         self.assertEqual(result['status'], 'success')
 
+    def test_error_handling(self):
+        '''Test error handling for invalid input'''
+        result = api.process_request(None)
+        self.assertIn('error', result)
+
 if __name__ == '__main__':
     unittest.main()
"""
        
        result = analyze_git_diff(test_diff)
        
        self.assertEqual(result['change_type'], 'test')
        self.assertIn('tests/test_api.py', result['affected_components'])
        self.assertGreater(result['confidence'], 0.7)  # High confidence for test files

    def test_analyze_git_diff_docs_change(self):
        """Test analysis of documentation changes."""
        docs_diff = """diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -1,6 +1,6 @@
 # Project Name
 
-Brief description of the project.
+Comprehensive description of the project with new features.
 
 ## Installation
 
@@ -10,6 +10,10 @@ pip install -r requirements.txt
 
 ## Usage
 
+### New Feature
+
+Use the new feature like this:
+
 ```python
 import project
 project.run()
"""
        
        result = analyze_git_diff(docs_diff)
        
        self.assertEqual(result['change_type'], 'docs')
        self.assertIn('README.md', result['affected_components'])
        self.assertGreater(result['confidence'], 0.7)  # High confidence for docs

    def test_analyze_git_diff_refactor_change(self):
        """Test analysis of refactoring changes."""
        refactor_diff = """diff --git a/src/utils.py b/src/utils.py
index 1234567..abcdefg 100644
--- a/src/utils.py
+++ b/src/utils.py
@@ -5,15 +5,10 @@ def process_data(data):
     # Refactor: simplify complex logic
-    if data is not None:
-        if isinstance(data, dict):
-            if 'items' in data:
-                return [item for item in data['items'] if item]
-            else:
-                return []
-        else:
-            return []
-    else:
-        return []
+    if not data or not isinstance(data, dict):
+        return []
+    
+    return [item for item in data.get('items', []) if item]
"""
        
        result = analyze_git_diff(refactor_diff)
        
        self.assertEqual(result['change_type'], 'refactor')
        self.assertIn('src/utils.py', result['affected_components'])

    def test_analyze_git_diff_empty_input(self):
        """Test analysis with empty or invalid input."""
        result = analyze_git_diff('')
        
        self.assertEqual(result['change_type'], 'unknown')
        self.assertEqual(result['affected_components'], [])
        self.assertEqual(result['confidence'], 0.0)
        self.assertIn('Empty', result['summary'])

    def test_analyze_git_diff_none_input(self):
        """Test analysis with None input."""
        result = analyze_git_diff(None)
        
        self.assertEqual(result['change_type'], 'unknown')
        self.assertEqual(result['affected_components'], [])
        self.assertEqual(result['confidence'], 0.0)

    def test_analyze_git_diff_multiple_files(self):
        """Test analysis with multiple files changed."""
        multi_file_diff = """diff --git a/src/api.py b/src/api.py
index 1234567..abcdefg 100644
--- a/src/api.py
+++ b/src/api.py
@@ -10,6 +10,9 @@ def get_user(id):
     user = database.find_user(id)
     return user

+def create_user(data):
+    '''Add new user creation functionality'''
+    return database.create_user(data)

diff --git a/src/models.py b/src/models.py
index 2345678..bcdefgh 100644
--- a/src/models.py
+++ b/src/models.py
@@ -5,6 +5,12 @@ class User:
     def __init__(self, name, email):
         self.name = name
         self.email = email
+
+    def to_dict(self):
+        '''Convert user to dictionary representation'''
+        return {
+            'name': self.name,
+            'email': self.email
+        }
"""
        
        result = analyze_git_diff(multi_file_diff)
        
        self.assertEqual(result['change_type'], 'feature')
        self.assertIn('src/api.py', result['affected_components'])
        self.assertIn('src/models.py', result['affected_components'])
        self.assertGreater(len(result['affected_components']), 1)

class TestExtractAffectedFiles(unittest.TestCase):
    """Test file extraction from git diffs."""

    def test_extract_affected_files_standard_diff(self):
        """Test extraction from standard git diff format."""
        diff = """diff --git a/src/file1.py b/src/file1.py
index 1234567..abcdefg 100644
--- a/src/file1.py
+++ b/src/file1.py
@@ -1,3 +1,4 @@
 line 1
 line 2
+new line
 line 3
"""
        
        files = _extract_affected_files(diff)
        
        self.assertIn('src/file1.py', files)

    def test_extract_affected_files_new_file(self):
        """Test extraction for new file creation."""
        diff = """diff --git a/src/new_file.py b/src/new_file.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/new_file.py
@@ -0,0 +1,5 @@
+def new_function():
+    pass
"""
        
        files = _extract_affected_files(diff)
        
        self.assertIn('src/new_file.py', files)

    def test_extract_affected_files_deleted_file(self):
        """Test extraction for file deletion."""
        diff = """diff --git a/src/old_file.py b/src/old_file.py
deleted file mode 100644
index 1234567..0000000
--- a/src/old_file.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def old_function():
-    pass
"""
        
        files = _extract_affected_files(diff)
        
        self.assertIn('src/old_file.py', files)

    def test_extract_affected_files_multiple_files(self):
        """Test extraction from diff with multiple files."""
        diff = """diff --git a/src/file1.py b/src/file1.py
index 1234567..abcdefg 100644
--- a/src/file1.py
+++ b/src/file1.py
@@ -1,2 +1,3 @@
 line 1
+new line
 line 2

diff --git a/src/file2.py b/src/file2.py
index 2345678..bcdefgh 100644
--- a/src/file2.py
+++ b/src/file2.py
@@ -1,2 +1,3 @@
 line A
+new line
 line B
"""
        
        files = _extract_affected_files(diff)
        
        self.assertIn('src/file1.py', files)
        self.assertIn('src/file2.py', files)
        self.assertEqual(len(files), 2)

    def test_extract_affected_files_empty_diff(self):
        """Test extraction from empty diff."""
        files = _extract_affected_files('')
        
        self.assertEqual(files, [])

    def test_extract_affected_files_no_duplicates(self):
        """Test that duplicate files are not included."""
        diff = """diff --git a/src/file.py b/src/file.py
index 1234567..abcdefg 100644
--- a/src/file.py
+++ b/src/file.py
@@ -1,2 +1,3 @@
 line 1
+new line
--- a/src/file.py
+++ b/src/file.py
"""
        
        files = _extract_affected_files(diff)
        
        # Should only appear once despite multiple references
        self.assertEqual(files.count('src/file.py'), 1)

class TestDetermineChangeType(unittest.TestCase):
    """Test change type determination logic."""

    def test_determine_change_type_feature_new_file(self):
        """Test feature detection for new files."""
        diff = "new file mode 100644\n+def new_function():\n+    pass"
        files = ['src/new_feature.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'feature')

    def test_determine_change_type_bugfix_keywords(self):
        """Test bugfix detection with keywords."""
        diff = "fix the critical bug in authentication\n-broken_code\n+fixed_code"
        files = ['src/auth.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'bugfix')

    def test_determine_change_type_test_files(self):
        """Test test detection for test files."""
        diff = "+def test_new_functionality():\n+    assert True"
        files = ['tests/test_feature.py', 'src/test_utils.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'test')

    def test_determine_change_type_docs_files(self):
        """Test docs detection for documentation files."""
        diff = "+## New Section\n+This explains the feature"
        files = ['README.md', 'docs/guide.rst']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'docs')

    def test_determine_change_type_refactor_keywords(self):
        """Test refactor detection with keywords."""
        diff = "refactor the module structure\n-old_code\n+simplified_code"
        files = ['src/module.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'refactor')

    def test_determine_change_type_performance_keywords(self):
        """Test performance detection with keywords."""
        diff = "optimize the database queries for better performance\n+cache_result"
        files = ['src/database.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'performance')

    def test_determine_change_type_mixed_changes(self):
        """Test change type for mixed changes (should pick highest score)."""
        diff = "add new feature and fix bug\n+def new_feature():\n+fix error handling"
        files = ['src/feature.py']
        
        change_type = _determine_change_type(diff, files)
        
        # Should pick either feature or bugfix based on scoring
        self.assertIn(change_type, ['feature', 'bugfix'])

    def test_determine_change_type_unknown(self):
        """Test unknown change type for unclear diffs."""
        diff = "some random changes\nmodified file"
        files = ['src/unclear.py']
        
        change_type = _determine_change_type(diff, files)
        
        # Could be unknown or have low confidence in any type
        self.assertIsInstance(change_type, str)

    def test_determine_change_type_deleted_files(self):
        """Test change type for deleted files."""
        diff = "deleted file mode 100644\n-old_content"
        files = ['src/old_file.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'chore')

    def test_determine_change_type_style_changes(self):
        """Test style change detection."""
        diff = "format code and fix indentation\n-  spaced_wrong\n+    spaced_right"
        files = ['src/formatted.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'style')

    def test_determine_change_type_rename_files(self):
        """Test refactor detection for file renames."""
        diff = """diff --git a/src/old_name.py b/src/new_name.py
similarity index 90%
rename from src/old_name.py
rename to src/new_name.py
index 1234567..abcdefg 100644
--- a/src/old_name.py
+++ b/src/new_name.py
@@ -1,3 +1,3 @@
 def function():
-    return "old"
+    return "new"
"""
        files = ['src/new_name.py']
        
        change_type = _determine_change_type(diff, files)
        
        self.assertEqual(change_type, 'refactor')

class TestCalculateConfidence(unittest.TestCase):
    """Test confidence score calculation."""

    def test_calculate_confidence_high_for_clear_indicators(self):
        """Test high confidence for clear change indicators."""
        diff = "new file mode 100644\n+def feature():\n+    pass"
        confidence = _calculate_confidence(diff, 'feature', ['src/feature.py'])
        
        self.assertGreaterEqual(confidence, 0.6)

    def test_calculate_confidence_high_for_test_files(self):
        """Test high confidence for test file changes."""
        diff = "+def test_something():\n+    assert True"
        confidence = _calculate_confidence(diff, 'test', ['tests/test_file.py'])
        
        self.assertGreater(confidence, 0.7)

    def test_calculate_confidence_high_for_docs(self):
        """Test high confidence for documentation changes."""
        diff = "+## New Section\n+Documentation update"
        confidence = _calculate_confidence(diff, 'docs', ['README.md'])
        
        self.assertGreater(confidence, 0.7)

    def test_calculate_confidence_bugfix_indicators(self):
        """Test confidence for clear bug fix indicators."""
        diff = "fix critical bug in authentication\n-broken\n+fixed"
        confidence = _calculate_confidence(diff, 'bugfix', ['src/auth.py'])
        
        self.assertGreaterEqual(confidence, 0.6)

    def test_calculate_confidence_large_diff_penalty(self):
        """Test confidence penalty for very large diffs."""
        large_diff = '\n'.join([f"line {i}" for i in range(150)])  # 150 lines
        confidence = _calculate_confidence(large_diff, 'feature', ['src/file.py'])
        
        # Should have penalty for large size
        self.assertLess(confidence, 0.7)

    def test_calculate_confidence_small_diff_penalty(self):
        """Test confidence penalty for very small diffs."""
        small_diff = "line 1\nline 2"  # Very small
        confidence = _calculate_confidence(small_diff, 'feature', ['src/file.py'])
        
        # Should have penalty for small size
        self.assertLess(confidence, 0.7)

    def test_calculate_confidence_bounds(self):
        """Test that confidence is always between 0 and 1."""
        # Test with extreme inputs
        confidence_high = _calculate_confidence("perfect indicators", 'test', ['test.py'])
        confidence_low = _calculate_confidence("", 'unknown', [])
        
        self.assertGreaterEqual(confidence_high, 0.0)
        self.assertLessEqual(confidence_high, 1.0)
        self.assertGreaterEqual(confidence_low, 0.0)
        self.assertLessEqual(confidence_low, 1.0)

class TestGenerateSummary(unittest.TestCase):
    """Test summary generation."""

    def test_generate_summary_no_files(self):
        """Test summary with no affected files."""
        summary = _generate_summary("diff content", "feature", [])
        
        self.assertIn("no clear file modifications", summary)
        self.assertIn("feature", summary)

    def test_generate_summary_single_file(self):
        """Test summary with single affected file."""
        summary = _generate_summary("diff content", "bugfix", ["src/api.py"])
        
        self.assertIn("bugfix", summary)
        self.assertIn("src/api.py", summary)

    def test_generate_summary_multiple_files(self):
        """Test summary with multiple affected files."""
        files = ["src/api.py", "src/models.py", "src/utils.py"]
        summary = _generate_summary("diff content", "feature", files)
        
        self.assertIn("feature", summary)
        self.assertIn("3 files", summary)
        self.assertIn("src/api.py", summary)

    def test_generate_summary_many_files_truncated(self):
        """Test summary with many files (should truncate)."""
        files = ["file1.py", "file2.py", "file3.py", "file4.py", "file5.py"]
        summary = _generate_summary("diff content", "refactor", files)
        
        self.assertIn("refactor", summary)
        self.assertIn("5 files", summary)
        self.assertIn("...", summary)  # Should truncate

    def test_generate_summary_different_change_types(self):
        """Test summary generation for different change types."""
        files = ["src/test.py"]
        
        for change_type in ['feature', 'bugfix', 'refactor', 'test', 'docs']:
            summary = _generate_summary("diff", change_type, files)
            self.assertIn(change_type, summary)

class TestDirectTesting(unittest.TestCase):
    """Test the direct testing functionality."""

    def test_test_tool_directly_function_exists(self):
        """Test that the direct testing function exists and is callable."""
        self.assertTrue(callable(test_tool_directly))

    @patch('builtins.print')
    def test_test_tool_directly_runs(self, mock_print):
        """Test that the direct testing function runs without errors."""
        # Should not raise any exceptions
        test_tool_directly()
        
        # Should have printed some output
        self.assertTrue(mock_print.called)

    def test_test_tool_directly_integration(self):
        """Test integration between direct test and analyze_git_diff."""
        # This is an integration test to ensure the tool works end-to-end
        sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 line 1
+new line
 line 2
"""
        
        result = analyze_git_diff(sample_diff)
        
        # Should return valid analysis
        self.assertIn('change_type', result)
        self.assertIn('affected_components', result)
        self.assertIn('confidence', result)
        self.assertIn('summary', result)

    @patch('builtins.print')  # Mock print to suppress output
    def test_main_execution_block(self, mock_print):
        """Test the if __name__ == '__main__' execution block."""
        # Direct execution to ensure line 200 is covered
        # This imports and explicitly runs the main code path
        
        import importlib.util
        import sys
        
        # Load the module as a script to trigger __main__
        spec = importlib.util.spec_from_file_location("__main__", "src/git_analysis_tool.py")
        module = importlib.util.module_from_spec(spec)
        
        # Set up the environment as if it's the main module
        old_name = getattr(module, '__name__', None)
        module.__name__ = '__main__'
        
        try:
            # Execute the module - this should trigger the if __name__ == '__main__' block
            spec.loader.exec_module(module)
        finally:
            # Restore original name if it existed
            if old_name is not None:
                module.__name__ = old_name
        
        # The print mock should have been called (indicating test_tool_directly ran)
        self.assertTrue(mock_print.called)

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def test_malformed_diff_handling(self):
        """Test handling of malformed diff content."""
        malformed_diff = "not a real diff format\nrandom content"
        
        result = analyze_git_diff(malformed_diff)
        
        # Should handle gracefully
        self.assertIsInstance(result, dict)
        self.assertIn('change_type', result)

    def test_unicode_content(self):
        """Test handling of unicode content in diffs."""
        unicode_diff = """diff --git a/src/test.py b/src/test.py
index 1234567..abcdefg 100644
--- a/src/test.py
+++ b/src/test.py
@@ -1,2 +1,3 @@
 # Test with unicode: ñáéíóú
+def new_function():  # Added new function with unicode: 中文测试
 def function():
"""
        
        result = analyze_git_diff(unicode_diff)
        
        # Should handle unicode gracefully
        self.assertIsInstance(result, dict)
        # Should detect as feature due to new function
        self.assertEqual(result['change_type'], 'feature')

    def test_very_long_file_names(self):
        """Test handling of very long file names."""
        long_name = "src/" + "very_long_name_" * 10 + ".py"
        diff = f"""diff --git a/{long_name} b/{long_name}
index 1234567..abcdefg 100644
--- a/{long_name}
+++ b/{long_name}
@@ -1,2 +1,3 @@
 line 1
+new line
 line 2
"""
        
        result = analyze_git_diff(diff)
        
        # Should handle long names gracefully
        self.assertIsInstance(result, dict)
        self.assertIn(long_name, result['affected_components'])

    def test_binary_file_indicators(self):
        """Test handling of binary file changes."""
        binary_diff = """diff --git a/image.png b/image.png
index 1234567..abcdefg 100644
Binary files a/image.png and b/image.png differ
"""
        
        result = analyze_git_diff(binary_diff)
        
        # Should handle binary files
        self.assertIsInstance(result, dict)
        self.assertIn('image.png', result['affected_components'])

if __name__ == '__main__':
    unittest.main()