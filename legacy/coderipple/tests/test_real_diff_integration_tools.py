"""
Tests for Real Diff Integration Tools

This module tests the git diff parsing, code change extraction, 
and targeted documentation generation capabilities.
"""

import os
import unittest
import tempfile
import shutil
from pathlib import Path
# Import the modules to test
import sys
from coderipple.real_diff_integration_tools import (
    GitDiffParser,
    CodeChange,
    FunctionChange,
    ClassChange,
    ImportChange,
    DiffAnalysisResult,
    extract_specific_changes,
    generate_code_examples_from_diff,
    generate_file_specific_documentation
)

class TestGitDiffParser(unittest.TestCase):
    """Test the core GitDiffParser functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.parser = GitDiffParser()
        self.sample_diff = """diff --git a/src/webhook_parser.py b/src/webhook_parser.py
index 1234567..abcdefg 100644
--- a/src/webhook_parser.py
+++ b/src/webhook_parser.py
@@ -1,6 +1,15 @@
 import json
 from typing import Dict, Any, List, Optional
+from dataclasses import dataclass
+from strands import tool
 
-def parse_webhook(payload: str) -> Dict[str, Any]:
+@dataclass
+class WebhookEvent:
+    repository: str
+    commits: List[Dict[str, Any]]
+    action: str
+
+def parse_webhook(payload: str) -> WebhookEvent:
     \"\"\"Parse GitHub webhook payload.\"\"\"
     data = json.loads(payload)
-    return data
+    return WebhookEvent(
+        repository=data.get('repository', {}).get('name', ''),
+        commits=data.get('commits', []),
+        action=data.get('action', 'push')
+    )
"""
    
    def test_parse_basic_diff(self):
        """Test parsing of basic git diff."""
        result = self.parser.parse_diff(self.sample_diff)
        
        self.assertIsInstance(result, DiffAnalysisResult)
        self.assertEqual(len(result.files_modified), 1)
        self.assertIn('src/webhook_parser.py', result.files_modified)
        self.assertGreater(result.total_lines_added, 0)
        self.assertGreater(result.total_lines_removed, 0)
    
    def test_extract_function_changes(self):
        """Test extraction of function changes."""
        result = self.parser.parse_diff(self.sample_diff)
        
        # Should detect the modified parse_webhook function
        self.assertGreater(len(result.function_changes), 0)
        
        func_change = result.function_changes[0]
        self.assertEqual(func_change.name, 'parse_webhook')
        self.assertEqual(func_change.change_type, 'signature_changed')
        self.assertIn('WebhookEvent', func_change.new_signature)
    
    def test_extract_class_changes(self):
        """Test extraction of class changes."""
        result = self.parser.parse_diff(self.sample_diff)
        
        # Should detect the new WebhookEvent class
        class_changes = [c for c in result.class_changes if c.name == 'WebhookEvent']
        self.assertEqual(len(class_changes), 1)
        
        class_change = class_changes[0]
        self.assertEqual(class_change.change_type, 'added')
        self.assertIn('WebhookEvent', class_change.new_definition)
    
    def test_extract_import_changes(self):
        """Test extraction of import changes."""
        result = self.parser.parse_diff(self.sample_diff)
        
        # Should detect new imports
        import_changes = result.import_changes
        self.assertGreater(len(import_changes), 0)
        
        # Check for dataclass import
        dataclass_imports = [i for i in import_changes if 'dataclass' in i.imported_items]
        self.assertGreater(len(dataclass_imports), 0)

class TestCodeChangeExtraction(unittest.TestCase):
    """Test specific code change extraction functionality."""
    
    def test_extract_specific_changes_new_feature(self):
        """Test extraction for new feature changes."""
        git_diff = """diff --git a/src/new_feature.py b/src/new_feature.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/new_feature.py
@@ -0,0 +1,20 @@
+from strands import tool
+
+@tool
+def analyze_code_quality(file_path: str, content: str) -> dict:
+    \"\"\"Analyze code quality metrics.\"\"\"
+    metrics = {
+        'complexity': calculate_complexity(content),
+        'maintainability': check_maintainability(content),
+        'test_coverage': estimate_coverage(file_path)
+    }
+    return metrics
+
+def calculate_complexity(code: str) -> int:
+    \"\"\"Calculate cyclomatic complexity.\"\"\"
+    return len(code.split('if ')) + len(code.split('for ')) + len(code.split('while '))
"""
        
        result = extract_specific_changes(git_diff, 'feature')
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(result['function_changes']), 0)
        
        # Check for the new tool function
        tool_functions = [f for f in result['function_changes'] if f.get('name') == 'analyze_code_quality']
        self.assertGreater(len(tool_functions), 0)
    
    def test_extract_specific_changes_bugfix(self):
        """Test extraction for bugfix changes."""
        git_diff = """diff --git a/src/parser.py b/src/parser.py
index abc123..def456 100644
--- a/src/parser.py
+++ b/src/parser.py
@@ -10,7 +10,10 @@ def parse_data(input_data):
         return {}
     
     try:
-        result = json.loads(input_data)
+        # Fix: Handle both string and dict inputs
+        if isinstance(input_data, str):
+            result = json.loads(input_data)
+        else:
+            result = input_data
         return result
     except json.JSONDecodeError:
         return {'error': 'Invalid JSON'}
"""
        
        result = extract_specific_changes(git_diff, 'bugfix')
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('modified', result['summary'].lower())
        # Bugfix may or may not detect function changes depending on diff pattern
        self.assertIsInstance(result['function_changes'], list)

class TestCodeExampleGeneration(unittest.TestCase):
    """Test code example generation from diffs."""
    
    def test_generate_code_examples_from_diff(self):
        """Test generation of code examples from git diff."""
        git_diff = """diff --git a/src/api.py b/src/api.py
index 1111111..2222222 100644
--- a/src/api.py
+++ b/src/api.py
@@ -1,4 +1,12 @@
 from flask import Flask
+from strands import tool
 
 app = Flask(__name__)
+
+@tool
+def create_endpoint(path: str, handler) -> dict:
+    \"\"\"Create a new API endpoint.\"\"\"
+    app.add_url_rule(path, endpoint=path, view_func=handler)
+    return {'status': 'created', 'path': path}
"""
        
        result = generate_code_examples_from_diff(git_diff, 'src/api.py', 'feature')
        
        self.assertEqual(result['status'], 'success')
        self.assertGreater(len(result['examples']), 0)
        
        # Check for function example
        examples = result['examples']
        function_examples = [ex for ex in examples if ex['type'] == 'new_function']
        self.assertGreater(len(function_examples), 0)
        
        func_example = function_examples[0]
        self.assertIn('create_endpoint', func_example['code'])
        self.assertIn('def create_endpoint', func_example['code'])
    
    def test_generate_usage_examples(self):
        """Test generation of usage examples."""
        git_diff = """diff --git a/src/client.py b/src/client.py
index aaaa111..bbbb222 100644
--- a/src/client.py
+++ b/src/client.py
@@ -5,6 +5,15 @@ class APIClient:
     def __init__(self, base_url: str):
         self.base_url = base_url
         self.session = requests.Session()
+    
+    def authenticate(self, token: str) -> bool:
+        \"\"\"Authenticate with API token.\"\"\"
+        self.session.headers.update({'Authorization': f'Bearer {token}'})
+        response = self.session.get(f'{self.base_url}/auth/verify')
+        return response.status_code == 200
+    
+    def get_user_data(self, user_id: str) -> dict:
+        \"\"\"Retrieve user data by ID.\"\"\"
+        response = self.session.get(f'{self.base_url}/users/{user_id}')
+        return response.json()
"""
        
        result = generate_code_examples_from_diff(git_diff, 'src/client.py', 'feature')
        
        self.assertEqual(result['status'], 'success')
        examples = result['examples']
        
        # Should have usage examples for the new methods
        usage_examples = [ex for ex in examples if 'usage_example' in ex]
        self.assertGreater(len(usage_examples), 0)

class TestFileSpecificDocumentation(unittest.TestCase):
    """Test file-specific documentation generation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_generate_api_documentation(self):
        """Test API documentation generation."""
        git_diff = """diff --git a/src/webhook_api.py b/src/webhook_api.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/webhook_api.py
@@ -0,0 +1,25 @@
+from flask import Flask, request, jsonify
+from strands import tool
+
+app = Flask(__name__)
+
+@app.route('/webhook', methods=['POST'])
+def handle_webhook():
+    \"\"\"Handle incoming GitHub webhook.\"\"\"
+    payload = request.get_json()
+    result = process_webhook_payload(payload)
+    return jsonify(result)
+
+@tool
+def process_webhook_payload(payload: dict) -> dict:
+    \"\"\"Process webhook payload and trigger agents.\"\"\"
+    event_type = payload.get('action', 'unknown')
+    repository = payload.get('repository', {}).get('name', '')
+    
+    if event_type == 'push':
+        return trigger_documentation_update(repository, payload)
+    
+    return {'status': 'ignored', 'reason': f'Unsupported event: {event_type}'}
+
+def trigger_documentation_update(repo: str, payload: dict) -> dict:
+    \"\"\"Trigger documentation update process.\"\"\"
+    return {'status': 'processing', 'repository': repo}
"""
        
        result = generate_file_specific_documentation(
            git_diff=git_diff,
            file_path='src/webhook_api.py',
            existing_docs='',
            doc_type='api'
        )
        
        self.assertEqual(result['status'], 'success')
        self.assertIn('documentation', result)
        
        docs = result['documentation']
        self.assertIn('Documentation', docs)
        self.assertIn('handle_webhook', docs)
        self.assertIn('webhook', docs.lower())
    
    def test_generate_user_documentation(self):
        """Test user documentation generation."""
        git_diff = """diff --git a/src/cli.py b/src/cli.py
new file mode 100644
index 0000000..abcdefg
--- /dev/null
+++ b/src/cli.py
@@ -0,0 +1,30 @@
+import argparse
+import sys
+from webhook_parser import process_webhook_file
+
+def main():
+    \"\"\"Main CLI entry point.\"\"\"
+    parser = argparse.ArgumentParser(description='CodeRipple CLI')
+    parser.add_argument('--webhook', help='Process webhook file')
+    parser.add_argument('--repository', help='Repository to monitor')
+    parser.add_argument('--output', help='Output directory for docs')
+    
+    args = parser.parse_args()
+    
+    if args.webhook:
+        return process_webhook_command(args.webhook, args.output)
+    elif args.repository:
+        return monitor_repository_command(args.repository, args.output)
+    else:
+        parser.print_help()
+        return 1
+
+def process_webhook_command(webhook_file: str, output_dir: str) -> int:
+    \"\"\"Process a webhook file and generate documentation.\"\"\"
+    try:
+        result = process_webhook_file(webhook_file, output_dir)
+        print(f"Documentation generated: {result['files_created']} files")
+        return 0
+    except Exception as e:
+        print(f"Error: {e}", file=sys.stderr)
+        return 1
"""
        
        result = generate_file_specific_documentation(
            git_diff=git_diff,
            file_path='src/cli.py',
            existing_docs='',
            doc_type='user'
        )
        
        self.assertEqual(result['status'], 'success')
        docs = result['documentation']
        
        self.assertIn('documentation', docs.lower())
        self.assertIn('main', docs.lower())
        self.assertIn('entry point', docs.lower())

class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world integration scenarios."""
    
    def test_feature_addition_workflow(self):
        """Test complete workflow for feature addition."""
        # Simulate adding a new validation feature
        git_diff = """diff --git a/src/content_validator.py b/src/content_validator.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/content_validator.py
@@ -0,0 +1,35 @@
+from typing import List, Dict, Any
+from strands import tool
+import re
+
+@tool
+def validate_content_quality(content: str, rules: List[str]) -> dict:
+    \"\"\"Validate content against quality rules.\"\"\"
+    results = {
+        'score': 0,
+        'issues': [],
+        'suggestions': []
+    }
+    
+    for rule in rules:
+        rule_result = apply_validation_rule(content, rule)
+        results['score'] += rule_result['score']
+        results['issues'].extend(rule_result['issues'])
+    
+    return results
+
+def apply_validation_rule(content: str, rule: str) -> dict:
+    \"\"\"Apply a specific validation rule.\"\"\"
+    if rule == 'min_length':
+        return validate_min_length(content, 100)
+    elif rule == 'heading_structure':
+        return validate_heading_structure(content)
+    else:
+        return {'score': 0, 'issues': [f'Unknown rule: {rule}']}
+
+def validate_min_length(content: str, min_chars: int) -> dict:
+    \"\"\"Validate minimum content length.\"\"\"
+    if len(content) >= min_chars:
+        return {'score': 10, 'issues': []}
+    return {'score': 0, 'issues': [f'Content too short: {len(content)} < {min_chars}']}
"""
        
        # Test change extraction
        changes_result = extract_specific_changes(git_diff, 'feature')
        self.assertEqual(changes_result['status'], 'success')
        self.assertGreater(len(changes_result['function_changes']), 0)
        
        # Test code example generation
        examples_result = generate_code_examples_from_diff(git_diff, 'src/content_validator.py', 'feature')
        self.assertEqual(examples_result['status'], 'success')
        self.assertGreater(len(examples_result['examples']), 0)
        
        # Test documentation generation
        docs_result = generate_file_specific_documentation(
            git_diff=git_diff,
            file_path='src/content_validator.py',
            existing_docs='',
            doc_type='api'
        )
        self.assertEqual(docs_result['status'], 'success')
        self.assertIn('validate_content_quality', docs_result['documentation'])
    
    def test_bugfix_workflow(self):
        """Test workflow for bug fix documentation."""
        git_diff = """diff --git a/src/parser.py b/src/parser.py
index 1111111..2222222 100644
--- a/src/parser.py
+++ b/src/parser.py
@@ -15,8 +15,12 @@ def parse_commit_data(commit_info):
     
     files_changed = []
     for file_info in commit_info.get('files', []):
-        # Bug: Was not handling renamed files properly
-        files_changed.append(file_info['filename'])
+        # Fix: Handle renamed files properly
+        if 'previous_filename' in file_info:
+            # File was renamed
+            files_changed.append(f"{file_info['previous_filename']} -> {file_info['filename']}")
+        else:
+            files_changed.append(file_info['filename'])
     
     return {
         'message': commit_info.get('message', ''),
"""
        
        changes_result = extract_specific_changes(git_diff, 'bugfix')
        self.assertEqual(changes_result['status'], 'success')
        self.assertIn('modified', changes_result['summary'].lower())
        
        # Generate targeted documentation for the fix
        docs_result = generate_file_specific_documentation(
            git_diff=git_diff,
            file_path='src/parser.py',
            existing_docs='# Parser Documentation\n\nHandles commit parsing.',
            doc_type='system'
        )
        
        self.assertEqual(docs_result['status'], 'success')
        self.assertIn('Parser Documentation', docs_result['documentation'])

class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def test_invalid_git_diff(self):
        """Test handling of invalid git diff."""
        invalid_diff = "This is not a valid git diff format"
        
        result = extract_specific_changes(invalid_diff, 'feature')
        
        # Should handle gracefully but indicate no changes found
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['function_changes']), 0)
        self.assertEqual(len(result['class_changes']), 0)
    
    def test_empty_diff(self):
        """Test handling of empty diff."""
        result = extract_specific_changes('', 'feature')
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(len(result['function_changes']), 0)
    
    def test_unsupported_file_type(self):
        """Test handling of unsupported file types."""
        git_diff = """diff --git a/data/config.xml b/data/config.xml
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/data/config.xml
@@ -0,0 +1,10 @@
+<?xml version="1.0"?>
+<configuration>
+    <setting name="debug">true</setting>
+    <setting name="log_level">info</setting>
+</configuration>
"""
        
        result = generate_code_examples_from_diff(git_diff, 'data/config.xml', 'config')
        
        # Should handle gracefully
        self.assertEqual(result['status'], 'success')
        # May have limited examples for non-code files

if __name__ == '__main__':
    unittest.main()