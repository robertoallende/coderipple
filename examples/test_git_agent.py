#!/usr/bin/env python3
"""
Test script for git analysis tool using Strands Agent

This script demonstrates how to properly use the @tool decorated function
with a Strands Agent for analyzing git diffs.
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strands import Agent
from git_analysis_tool import analyze_git_diff


def test_with_agent():
    """Test the git analysis tool with a Strands Agent"""
    
    # Create an agent with the git analysis tool
    # Note: You may need to configure AWS credentials for Bedrock
    agent = Agent(
        tools=[analyze_git_diff],
        # Uncomment and configure if using specific model
        # model_provider='bedrock',
        # model_name='anthropic.claude-3-haiku-20240307-v1:0'
    )
    
    sample_diff = """diff --git a/src/new_feature.py b/src/new_feature.py
new file mode 100644
index 0000000..1234567
--- /dev/null
+++ b/src/new_feature.py
@@ -0,0 +1,15 @@
+def calculate_metrics(data):
+    \"\"\"Calculate performance metrics from data\"\"\"
+    if not data:
+        return {}
+    
+    total = sum(data)
+    avg = total / len(data)
+    
+    return {
+        'total': total,
+        'average': avg,
+        'count': len(data)
+    }
+
diff --git a/tests/test_new_feature.py b/tests/test_new_feature.py
new file mode 100644
index 0000000..abcdef9
--- /dev/null
+++ b/tests/test_new_feature.py
@@ -0,0 +1,10 @@
+import unittest
+from src.new_feature import calculate_metrics
+
+class TestMetrics(unittest.TestCase):
+    def test_calculate_metrics(self):
+        result = calculate_metrics([1, 2, 3, 4, 5])
+        self.assertEqual(result['total'], 15)
+        self.assertEqual(result['average'], 3.0)
+        self.assertEqual(result['count'], 5)
"""

    print("Testing git analysis with Strands Agent...")
    print(f"Sample diff:\n{sample_diff}\n")
    
    # Ask the agent to analyze the git diff
    prompt = f"""
    Please use the analyze_git_diff tool to analyze the following git diff:
    
    {sample_diff}
    
    After analyzing, please explain what type of changes were made and provide insights about the code changes.
    """
    
    try:
        response = agent(prompt)
        print("Agent Response:")
        print(response)
    except Exception as e:
        print(f"Error using agent: {e}")
        print("This might be due to missing AWS credentials or model configuration.")
        print("Falling back to direct tool test...")
        
        # Fallback to direct tool usage
        result = analyze_git_diff(sample_diff)
        print("\nDirect Tool Result:")
        print(f"Change Type: {result['change_type']}")
        print(f"Affected Components: {result['affected_components']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Summary: {result['summary']}")


def test_multiple_scenarios():
    """Test various git diff scenarios"""
    
    scenarios = [
        ("Bug Fix", """diff --git a/src/parser.py b/src/parser.py
index 1234567..abcdefg 100644
--- a/src/parser.py
+++ b/src/parser.py
@@ -10,7 +10,7 @@ def parse_data(data):
     if not data:
-        return None  # Bug: this causes issues downstream
+        return []    # Fix: return empty list instead
     return process_data(data)
"""),
        
        ("Documentation", """diff --git a/README.md b/README.md
index 1234567..abcdefg 100644
--- a/README.md
+++ b/README.md
@@ -5,6 +5,12 @@
 
 ## Installation
 
+### Prerequisites
+
+- Python 3.8 or higher
+- AWS CLI configured
+
+### Install
 pip install coderipple
"""),
        
        ("Test Addition", """diff --git a/tests/test_webhook_parser.py b/tests/test_webhook_parser.py
index 1234567..abcdefg 100644
--- a/tests/test_webhook_parser.py
+++ b/tests/test_webhook_parser.py
@@ -100,6 +100,15 @@ class TestWebhookParser(unittest.TestCase):
         self.assertEqual(result.branch, "main")
     
+    def test_empty_commits(self):
+        \"\"\"Test handling of webhook with no commits\"\"\"
+        payload = {"ref": "refs/heads/main", "commits": []}
+        result = self.parser.parse_webhook_payload(json.dumps(payload), "push")
+        
+        self.assertIsNotNone(result)
+        self.assertEqual(len(result.commits), 0)
+
     def test_invalid_payload(self):
""")
    ]
    
    print("\\nTesting multiple scenarios directly...")
    for scenario_name, diff in scenarios:
        print(f"\\n--- {scenario_name} ---")
        result = analyze_git_diff(diff)
        print(f"Type: {result['change_type']}, Confidence: {result['confidence']:.1f}")
        print(f"Summary: {result['summary']}")


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--agent':
        test_with_agent()
    else:
        print("Running direct tool tests...")
        test_multiple_scenarios()
        print("\\n" + "="*50)
        print("To test with Strands Agent (requires AWS setup):")
        print("python test_git_agent.py --agent")


if __name__ == "__main__":
    main()