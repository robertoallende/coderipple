"""
Tests for content_generation_tools module

Tests the intelligent content generation capabilities including change pattern analysis, 
code example extraction, and context-aware content generation.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

, '..', 'src'))

from coderipple.content_generation_tools import (
    analyze_change_patterns,
    extract_code_examples_from_diff,
    generate_context_aware_content,
    generate_targeted_content_from_diff,
    generate_api_documentation_from_diff,
    generate_migration_guide_from_diff,
    generate_context_rich_content,
    enhance_generic_content_with_context,
    DocumentationFocus,
    CodeExample
)

class TestDocumentationFocus(unittest.TestCase):
    """Test documentation focus analysis."""

    def test_analyze_change_patterns_api_focus(self):
        """Test API-focused change detection."""
        file_paths = ['src/api/users.py', 'src/endpoints/auth.py']
        commit_messages = ['Add new user authentication endpoint']
        
        focus = analyze_change_patterns(file_paths, commit_messages)
        
        self.assertEqual(focus.primary_focus, 'api')
        self.assertIn('API', focus.affected_areas)
        self.assertIn('API Reference', focus.suggested_sections)

    def test_analyze_change_patterns_cli_focus(self):
        """Test CLI-focused change detection."""
        file_paths = ['src/cli.py', 'bin/deploy.sh']
        commit_messages = ['Add new deploy command', 'implement cli interface']
        
        focus = analyze_change_patterns(file_paths, commit_messages)
        
        self.assertEqual(focus.primary_focus, 'cli')
        self.assertIn('CLI', focus.affected_areas)
        self.assertIn('Command Reference', focus.suggested_sections)

    def test_analyze_change_patterns_config_focus(self):
        """Test configuration-focused change detection."""
        file_paths = ['config/settings.yaml', 'src/config.py']
        commit_messages = ['Update configuration options']
        
        focus = analyze_change_patterns(file_paths, commit_messages)
        
        self.assertEqual(focus.primary_focus, 'config')
        self.assertIn('Configuration', focus.affected_areas)
        self.assertIn('Configuration', focus.suggested_sections)

    def test_analyze_change_patterns_architecture_focus(self):
        """Test architecture-focused change detection."""
        file_paths = ['src/core/engine.py', 'lib/utils.py']
        commit_messages = ['Refactor core architecture']
        
        focus = analyze_change_patterns(file_paths, commit_messages)
        
        self.assertEqual(focus.primary_focus, 'architecture')
        self.assertIn('Architecture', focus.affected_areas)
        self.assertIn('System Architecture', focus.suggested_sections)

    def test_analyze_change_patterns_breaking_changes(self):
        """Test detection of breaking changes."""
        file_paths = ['src/api/v2.py']
        commit_messages = ['breaking: remove deprecated API', 'change api signature']
        
        focus = analyze_change_patterns(file_paths, commit_messages)
        
        self.assertEqual(focus.user_impact_level, 'high')

    def test_analyze_change_patterns_empty_input(self):
        """Test with empty input."""
        focus = analyze_change_patterns([], [])
        
        # Should return valid focus even with empty input
        self.assertIsInstance(focus.primary_focus, str)
        self.assertIsInstance(focus.affected_areas, list)
        self.assertIsInstance(focus.suggested_sections, list)

class TestCodeExamples(unittest.TestCase):
    """Test code example extraction."""

    def test_extract_code_examples_python(self):
        """Test extracting Python code examples."""
        git_diff = """
@@ -1,3 +1,8 @@
 import os
+
+def new_function():
+    '''New function added'''
+    return "example"
+
 def existing_function():
     pass
"""
        
        examples = extract_code_examples_from_diff(git_diff, 'src/example.py')
        
        self.assertTrue(len(examples) >= 1)
        
        # Should have detected the new function
        function_examples = [ex for ex in examples if 'function' in ex.description.lower()]
        self.assertTrue(len(function_examples) > 0)
        
        if function_examples:
            example = function_examples[0]
            self.assertEqual(example.language, 'python')
            self.assertEqual(example.change_type, 'added')
            self.assertIn('new_function', example.code)

    def test_extract_code_examples_javascript(self):
        """Test extracting JavaScript code examples."""
        git_diff = """
@@ -1,2 +1,6 @@
 const util = require('util');
+
+function newFeature() {
+    return 'example';
+}
"""
        
        examples = extract_code_examples_from_diff(git_diff, 'src/example.js')
        
        if examples:
            self.assertEqual(examples[0].language, 'javascript')

    def test_extract_code_examples_empty_diff(self):
        """Test with empty diff."""
        examples = extract_code_examples_from_diff('', 'test.py')
        self.assertEqual(examples, [])

    def test_extract_code_examples_no_file_path(self):
        """Test with no file path."""
        examples = extract_code_examples_from_diff('some diff', '')
        self.assertEqual(examples, [])

    def test_extract_code_examples_unknown_language(self):
        """Test with unknown file extension."""
        git_diff = """
@@ -1,1 +1,3 @@
 existing line
+new line 1
+new line 2
"""
        
        examples = extract_code_examples_from_diff(git_diff, 'unknown.xyz')
        
        if examples:
            self.assertEqual(examples[0].language, 'text')

class TestContentGeneration(unittest.TestCase):
    """Test content generation functions."""

    def setUp(self):
        """Set up test data."""
        self.git_analysis = {
            'change_type': 'feature',
            'affected_components': ['API', 'Database'],
            'summary': 'Added new user management functionality'
        }
        
        self.file_changes = ['src/api/users.py', 'src/models/user.py']
        
        self.code_examples = [
            CodeExample(
                language='python',
                code='def create_user(name): return User(name)',
                description='Create new user',
                file_path='src/api/users.py',
                change_type='added'
            )
        ]
        
        self.doc_focus = DocumentationFocus(
            primary_focus='api',
            affected_areas=['API'],
            user_impact_level='medium',
            suggested_sections=['API Reference']
        )

    def test_generate_context_aware_content_discovery(self):
        """Test discovery section content generation."""
        content = generate_context_aware_content(
            'discovery', self.git_analysis, self.file_changes, 
            self.code_examples, self.doc_focus
        )
        
        self.assertIn('Recent Changes', content)
        self.assertIn('Feature', content)
        self.assertIn('user management', content)

    def test_generate_context_aware_content_getting_started_cli(self):
        """Test getting started content for CLI focus."""
        cli_focus = DocumentationFocus(
            primary_focus='cli',
            affected_areas=['CLI'],
            user_impact_level='medium',
            suggested_sections=['Command Reference']
        )
        
        content = generate_context_aware_content(
            'getting_started', self.git_analysis, self.file_changes,
            self.code_examples, cli_focus
        )
        
        self.assertIn('Command Line Interface', content)

    def test_generate_context_aware_content_getting_started_api(self):
        """Test getting started content for API focus."""
        content = generate_context_aware_content(
            'getting_started', self.git_analysis, self.file_changes,
            self.code_examples, self.doc_focus
        )
        
        self.assertIn('API Usage', content)
        self.assertIn('endpoints', content)

    def test_generate_context_aware_content_architecture(self):
        """Test architecture section content generation."""
        content = generate_context_aware_content(
            'architecture', self.git_analysis, self.file_changes,
            self.code_examples, self.doc_focus
        )
        
        self.assertIn('System Changes', content)
        self.assertIn('Affected Components', content)
        self.assertIn('API', content)
        self.assertIn('Database', content)

    def test_generate_context_aware_content_high_impact(self):
        """Test content generation for high impact changes."""
        high_impact_focus = DocumentationFocus(
            primary_focus='api',
            affected_areas=['API'],
            user_impact_level='high',
            suggested_sections=['API Reference']
        )
        
        content = generate_context_aware_content(
            'discovery', self.git_analysis, self.file_changes,
            self.code_examples, high_impact_focus
        )
        
        self.assertIn('Important', content)
        self.assertIn('breaking changes', content)

class TestStrandsTools(unittest.TestCase):
    """Test Strands @tool decorated functions."""

    def test_generate_targeted_content_from_diff_basic(self):
        """Test basic targeted content generation."""
        result = generate_targeted_content_from_diff('sample diff', 'discovery', 'feature', 'user')
        
        self.assertIn('status', result)
        # Function should handle the request

    def test_generate_api_documentation_from_diff_basic(self):
        """Test basic API documentation generation."""
        result = generate_api_documentation_from_diff('sample diff', 'api.py')
        
        self.assertIn('status', result)
        # Function should handle the request

    def test_generate_migration_guide_from_diff_basic(self):
        """Test migration guide generation."""
        result = generate_migration_guide_from_diff('sample diff', 'breaking_changes')
        
        self.assertIn('status', result)
        # Function should handle the request

    def test_generate_context_rich_content_basic(self):
        """Test context-rich content generation."""
        git_analysis = {'change_type': 'feature', 'summary': 'Test changes'}
        file_changes = ['test.py']
        code_examples = []
        doc_focus = DocumentationFocus('api', [], 'medium', [])
        
        result = generate_context_rich_content('discovery', git_analysis, file_changes, code_examples, doc_focus, 'feature')
        
        self.assertIsInstance(result, str)
        # Should return enhanced content string

    def test_enhance_generic_content_with_context_basic(self):
        """Test content enhancement with context."""
        generic_content = "# Basic README\n\nThis is a project."
        git_analysis = {'summary': 'Added new features'}
        
        result = enhance_generic_content_with_context(generic_content, git_analysis, [])
        
        self.assertIsInstance(result, str)
        # Should return enhanced content

class TestDataClasses(unittest.TestCase):
    """Test data class functionality."""

    def test_code_example_dataclass(self):
        """Test CodeExample dataclass."""
        example = CodeExample(
            language='python',
            code='def test(): pass',
            description='Test function',
            file_path='test.py',
            change_type='added'
        )
        
        self.assertEqual(example.language, 'python')
        self.assertEqual(example.change_type, 'added')

    def test_documentation_focus_dataclass(self):
        """Test DocumentationFocus dataclass."""
        focus = DocumentationFocus(
            primary_focus='api',
            affected_areas=['API', 'Database'],
            user_impact_level='high',
            suggested_sections=['API Reference', 'Migration Guide']
        )
        
        self.assertEqual(focus.primary_focus, 'api')
        self.assertEqual(focus.user_impact_level, 'high')
        self.assertEqual(len(focus.affected_areas), 2)

class TestUtilityFunctions(unittest.TestCase):
    """Test utility and helper functions."""

    def test_analyze_change_patterns_scoring(self):
        """Test the scoring mechanism in change pattern analysis."""
        # Test that scoring works correctly
        file_paths = ['src/api/test.py', 'src/api/another.py']  # Should score API higher
        commit_messages = ['api changes']
        
        focus = analyze_change_patterns(file_paths, commit_messages)
        
        # With 2 API files, should definitely be API focused
        self.assertEqual(focus.primary_focus, 'api')

    def test_extract_code_examples_edge_cases(self):
        """Test edge cases in code example extraction."""
        # Test with malformed diff
        malformed_diff = "not a real diff format"
        examples = extract_code_examples_from_diff(malformed_diff, 'test.py')
        
        # Should handle gracefully
        self.assertIsInstance(examples, list)

    def test_generate_context_aware_content_unknown_section(self):
        """Test content generation with unknown section."""
        git_analysis = {'change_type': 'unknown', 'summary': 'Changes'}
        
        content = generate_context_aware_content(
            'unknown_section', git_analysis, [], [], 
            DocumentationFocus('api', [], 'low', [])
        )
        
        # Should return string even for unknown sections
        self.assertIsInstance(content, str)

# Keep the original test functions for backwards compatibility
def test_change_pattern_analysis():
    """Test analysis of change patterns to determine documentation focus"""
    
    print("Testing change pattern analysis...")
    
    # Test API change detection
    api_files = ['src/api/handlers.py', 'src/routes.py', 'api/endpoints/user.py']
    api_commits = ['Add new user authentication endpoint', 'Update API response format']
    
    api_focus = analyze_change_patterns(api_files, api_commits)
    
    assert api_focus.primary_focus == 'api', f"Expected 'api', got '{api_focus.primary_focus}'"
    assert 'API' in api_focus.affected_areas, f"Expected 'API' in affected areas: {api_focus.affected_areas}"
    assert api_focus.user_impact_level in ['medium', 'high'], f"Expected medium/high impact, got '{api_focus.user_impact_level}'"
    
    print("   ✓ API change pattern detection working")
    
    # Test CLI change detection
    cli_files = ['src/cli.py', 'src/commands/deploy.py']
    cli_commits = ['Add new deploy command', 'Update CLI argument parsing']
    
    cli_focus = analyze_change_patterns(cli_files, cli_commits)
    
    assert cli_focus.primary_focus == 'cli', f"Expected 'cli', got '{cli_focus.primary_focus}'"
    assert 'CLI' in cli_focus.affected_areas, f"Expected 'CLI' in affected areas: {cli_focus.affected_areas}"
    
    print("   ✓ CLI change pattern detection working")

def test_code_example_extraction():
    """Test extraction of code examples from git diff"""
    
    print("Testing code example extraction...")
    
    # Sample git diff with Python code
    python_diff = """diff --git a/src/api.py b/src/api.py
index 1234567..abcdefg 100644
--- a/src/api.py
+++ b/src/api.py
@@ -10,6 +10,15 @@ from flask import Flask, request
 
 app = Flask(__name__)
 
+@app.route('/api/users', methods=['POST'])
+def create_user():
+    \"\"\"Create a new user account\"\"\"
+    data = request.get_json()
+    user = User(name=data['name'], email=data['email'])
+    db.session.add(user)
+    db.session.commit()
+    return {'id': user.id, 'status': 'created'}
+
 @app.route('/health')
 def health_check():
     return {'status': 'ok'}
"""
    
    examples = extract_code_examples_from_diff(python_diff, 'src/api.py')
    
    assert len(examples) > 0, "Should extract at least one code example"
    
    # Check the extracted example
    example = examples[0]
    assert example.language == 'python', f"Expected 'python', got '{example.language}'"
    assert example.change_type == 'added', f"Expected 'added', got '{example.change_type}'"
    assert 'create_user' in example.code, "Should contain the function name"
    assert example.file_path == 'src/api.py', f"Expected 'src/api.py', got '{example.file_path}'"
    
    print("   ✓ Code example extraction working")
    print(f"   📝 Extracted: {example.description}")

def test_context_aware_content_generation():
    """Test intelligent content generation based on context"""
    
    print("Testing context-aware content generation...")
    
    # Mock git analysis
    git_analysis = {
        'change_type': 'feature',
        'affected_components': ['src/api.py', 'src/models.py'],
        'summary': 'Added user management API endpoints'
    }
    
    # Mock documentation focus
    doc_focus = DocumentationFocus(
        primary_focus='api',
        affected_areas=['API', 'Database'],
        user_impact_level='high',
        suggested_sections=['API Reference', 'Getting Started']
    )
    
    # Mock code examples
    code_examples = [
        CodeExample(
            language='python',
            code='@app.route(\'/api/users\', methods=[\'POST\'])\ndef create_user():\n    pass',
            description='New user creation endpoint',
            file_path='src/api.py',
            change_type='added'
        )
    ]
    
    # Test discovery section generation
    discovery_content = generate_context_aware_content(
        section='discovery',
        git_analysis=git_analysis,
        file_changes=['src/api.py', 'src/models.py'],
        code_examples=code_examples,
        doc_focus=doc_focus
    )
    
    # Verify content contains relevant information
    assert 'feature' in discovery_content.lower(), "Should mention feature changes"
    assert 'high' in discovery_content.lower() or 'important' in discovery_content.lower(), "Should indicate high impact"
    assert 'api' in discovery_content.lower(), "Should mention API focus"
    
    print("   ✓ Discovery content generation working")
    
    # Test getting_started section generation
    getting_started_content = generate_context_aware_content(
        section='getting_started',
        git_analysis=git_analysis,
        file_changes=['src/api.py'],
        code_examples=code_examples,
        doc_focus=doc_focus
    )
    
    # Verify content contains API-specific information
    assert 'api' in getting_started_content.lower(), "Should mention API"
    assert 'endpoint' in getting_started_content.lower() or 'route' in getting_started_content.lower(), "Should mention endpoints"
    
    print("   ✓ Getting started content generation working")
    print(f"   📄 Sample content: {discovery_content[:100]}...")

def test_intelligent_vs_generic_content():
    """Test that intelligent content is more specific than generic content"""
    
    print("Testing intelligent vs generic content...")
    
    # Mock data for comparison
    git_analysis = {
        'change_type': 'feature',
        'affected_components': ['src/tourist_guide_agent.py'],
        'summary': 'Added README generation capability'
    }
    
    doc_focus = DocumentationFocus(
        primary_focus='architecture',
        affected_areas=['Documentation', 'Agent System'],
        user_impact_level='medium',
        suggested_sections=['Getting Started', 'Architecture']
    )
    
    code_examples = [
        CodeExample(
            language='python',
            code='def generate_main_readme(repository_name: str) -> str:\n    return f"# {repository_name} Documentation"',
            description='README generation function',
            file_path='src/tourist_guide_agent.py',
            change_type='added'
        )
    ]
    
    # Generate intelligent content
    intelligent_content = generate_context_aware_content(
        section='discovery',
        git_analysis=git_analysis,
        file_changes=['src/tourist_guide_agent.py'],
        code_examples=code_examples,
        doc_focus=doc_focus
    )
    
    # Generic content (what we had before)
    generic_content = """## Recent Updates
    
### Feature Changes
- Modified files and enhanced functionality
- Impact: Enhanced user experience

### What's New
- System improvements and updates
"""
    
    # Intelligent content should be more specific (content quality over length)
    # Check for expected content based on what's actually generated
    assert 'feature' in intelligent_content.lower(), "Should mention feature changes"
    assert 'readme' in intelligent_content.lower(), "Should mention specific functionality (README)"
    assert 'new features' in intelligent_content.lower(), "Should have structured sections"
    
    # Check that intelligent content has more specific information
    specific_terms = ['readme', 'generation', 'function', 'feature']
    intelligent_specific_count = sum(1 for term in specific_terms if term in intelligent_content.lower())
    generic_specific_count = sum(1 for term in specific_terms if term in generic_content.lower())
    
    assert intelligent_specific_count >= 3, f"Intelligent content should have specific terms: found {intelligent_specific_count}"
    assert intelligent_specific_count > generic_specific_count, f"Intelligent content should be more specific: {intelligent_specific_count} vs {generic_specific_count} specific terms"
    
    print("   ✓ Intelligent content is more specific than generic content")
    print(f"   📊 Intelligent: {len(intelligent_content)} chars ({intelligent_specific_count} specific terms)")
    print(f"   📊 Generic: {len(generic_content)} chars ({generic_specific_count} specific terms)")

def run_all_tests():
    """Run all content generation tools tests"""
    
    print("🧪 Testing Content Generation Tools")
    print("=" * 60)
    
    try:
        test_change_pattern_analysis()
        test_code_example_extraction()
        test_context_aware_content_generation()
        test_intelligent_vs_generic_content()
        
        print("\n✅ All content generation tools tests passed!")
        print("\n🎯 Content Generation Tools: Intelligent Content Generation is working correctly")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)