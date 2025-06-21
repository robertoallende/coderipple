"""
Tests for content_generation_tools module

Tests the intelligent content generation capabilities including change pattern analysis, 
code example extraction, and context-aware content generation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from content_generation_tools import (
    analyze_change_patterns,
    extract_code_examples_from_diff,
    generate_context_aware_content,
    DocumentationFocus,
    CodeExample
)


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