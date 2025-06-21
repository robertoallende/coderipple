#!/usr/bin/env python3
"""
Test edge cases for git analysis tool

This script tests various edge cases to ensure robust handling.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from git_analysis_tool import analyze_git_diff


def test_empty_diff():
    """Test with empty diff"""
    print("=== Testing Empty Diff ===")
    
    result = analyze_git_diff("")
    print(f"Empty string - Type: {result['change_type']}, Confidence: {result['confidence']}")
    
    result = analyze_git_diff("   \n  \n  ")
    print(f"Whitespace only - Type: {result['change_type']}, Confidence: {result['confidence']}")
    
    result = analyze_git_diff(None)
    print(f"None input - Type: {result['change_type']}, Confidence: {result['confidence']}")


def test_large_diff():
    """Test with very large diff"""
    print("\n=== Testing Large Diff ===")
    
    # Generate a large diff with many lines
    large_diff_lines = [
        "diff --git a/src/large_file.py b/src/large_file.py",
        "index 1234567..abcdefg 100644",
        "--- a/src/large_file.py",
        "+++ b/src/large_file.py",
        "@@ -1,10 +1,110 @@"
    ]
    
    # Add 200 lines of changes
    for i in range(200):
        large_diff_lines.append(f"+def function_{i}():")
        large_diff_lines.append(f"+    \"\"\"Generated function {i}\"\"\"")
        large_diff_lines.append(f"+    return {i}")
        large_diff_lines.append("+")
    
    large_diff = "\n".join(large_diff_lines)
    
    result = analyze_git_diff(large_diff)
    print(f"Large diff ({len(large_diff)} chars) - Type: {result['change_type']}, Confidence: {result['confidence']}")
    print(f"Summary: {result['summary']}")


def test_mixed_changes():
    """Test with mixed change types in one diff"""
    print("\n=== Testing Mixed Changes ===")
    
    mixed_diff = """diff --git a/src/parser.py b/src/parser.py
index 1234567..abcdefg 100644
--- a/src/parser.py
+++ b/src/parser.py
@@ -10,7 +10,7 @@ def parse_data(data):
     # Bug fix: handle None case properly
     if not data:
-        return None  # This was causing downstream issues
+        return []    # Fixed: return empty list instead
     
     # Performance improvement: add caching
+    @lru_cache(maxsize=128)
     def process_item(item):
         return transform(item)

diff --git a/tests/test_parser.py b/tests/test_parser.py
index 7890abc..defghij 100644
--- a/tests/test_parser.py
+++ b/tests/test_parser.py
@@ -20,6 +20,12 @@ class TestParser(unittest.TestCase):
         result = self.parser.parse([1, 2, 3])
         self.assertEqual(len(result), 3)
     
+    def test_empty_input_fix(self):
+        \"\"\"Test the None input bug fix\"\"\"
+        result = self.parser.parse(None)
+        self.assertEqual(result, [])
+        self.assertIsInstance(result, list)

diff --git a/README.md b/README.md
index abc1234..def5678 100644
--- a/README.md
+++ b/README.md
@@ -15,6 +15,10 @@ Parser utility for processing data.
 
 ## Recent Changes
 
+### v1.2.0
+- Fixed bug with None input handling
+- Added performance optimizations with caching
+- Improved test coverage
"""
    
    result = analyze_git_diff(mixed_diff)
    print(f"Mixed changes - Type: {result['change_type']}, Confidence: {result['confidence']}")
    print(f"Affected: {result['affected_components']}")
    print(f"Summary: {result['summary']}")


def test_binary_files():
    """Test with binary file changes"""
    print("\n=== Testing Binary Files ===")
    
    binary_diff = """diff --git a/assets/logo.png b/assets/logo.png
index 1234567..abcdefg 100644
Binary files a/assets/logo.png and b/assets/logo.png differ

diff --git a/docs/diagram.pdf b/docs/diagram.pdf
index abcdefg..1234567 100644
Binary files a/docs/diagram.pdf and b/docs/diagram.pdf differ
"""
    
    result = analyze_git_diff(binary_diff)
    print(f"Binary files - Type: {result['change_type']}, Confidence: {result['confidence']}")
    print(f"Affected: {result['affected_components']}")


def test_file_operations():
    """Test file additions, deletions, and renames"""
    print("\n=== Testing File Operations ===")
    
    # File addition
    addition_diff = """diff --git a/src/new_module.py b/src/new_module.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/new_module.py
@@ -0,0 +1,10 @@
+\"\"\"New module for advanced features\"\"\"
+
+def new_feature():
+    return "Hello World"
"""
    
    result = analyze_git_diff(addition_diff)
    print(f"New file - Type: {result['change_type']}, Confidence: {result['confidence']}")
    
    # File deletion
    deletion_diff = """diff --git a/src/deprecated.py b/src/deprecated.py
deleted file mode 100644
index 1234567..0000000
--- a/src/deprecated.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def old_function():
-    \"\"\"This function is no longer needed\"\"\"
-    pass
"""
    
    result = analyze_git_diff(deletion_diff)
    print(f"Deleted file - Type: {result['change_type']}, Confidence: {result['confidence']}")
    
    # File rename
    rename_diff = """diff --git a/src/old_name.py b/src/new_name.py
similarity index 85%
rename from src/old_name.py
rename to src/new_name.py
index 1234567..abcdefg 100644
--- a/src/old_name.py
+++ b/src/new_name.py
@@ -1,5 +1,5 @@
-\"\"\"Old module name\"\"\"
+\"\"\"Renamed module for clarity\"\"\"
 
 def main_function():
     return "refactored"
"""
    
    result = analyze_git_diff(rename_diff)
    print(f"Renamed file - Type: {result['change_type']}, Confidence: {result['confidence']}")


def test_malformed_diffs():
    """Test with malformed or unusual diff formats"""
    print("\n=== Testing Malformed Diffs ===")
    
    # Missing headers
    malformed1 = """@@ -10,7 +10,8 @@
 def function():
-    old_code()
+    new_code()
+    additional_line()
"""
    
    result = analyze_git_diff(malformed1)
    print(f"Missing headers - Type: {result['change_type']}, Confidence: {result['confidence']}")
    
    # Only file headers, no content
    malformed2 = """diff --git a/src/empty.py b/src/empty.py
index 1234567..abcdefg 100644
--- a/src/empty.py
+++ b/src/empty.py
"""
    
    result = analyze_git_diff(malformed2)
    print(f"Headers only - Type: {result['change_type']}, Confidence: {result['confidence']}")


def main():
    """Run all edge case tests"""
    try:
        test_empty_diff()
        test_large_diff()
        test_mixed_changes()
        test_binary_files()
        test_file_operations()
        test_malformed_diffs()
        
        print("\n" + "="*50)
        print("All edge case tests completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()