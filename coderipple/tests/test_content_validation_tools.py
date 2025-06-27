"""
Tests for Content Validation Tools

This module tests the comprehensive validation pipeline for documentation content,
including markdown syntax, code examples, cross-references, and quality standards.
"""

import os
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
# Import the modules to test
import sys
from coderipple.content_validation_tools import (
    ContentValidator,
    ValidationResult,
    CodeExample,
    CrossReference,
    validate_documentation_quality,
    enforce_quality_standards,
    validate_and_improve_content
)

class TestContentValidator(unittest.TestCase):
    """Test the core ContentValidator class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = ContentValidator(self.temp_dir)
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_markdown_syntax_valid(self):
        """Test markdown syntax validation with valid content."""
        content = """# Test Document

This is a valid markdown document with:

- Lists
- **Bold text**
- [Links](https://example.com)

## Code Examples

```python
def hello():
    return "world"
```

![Image with alt text](image.png)
"""
        result = self.validator.validate_markdown_syntax(content)
        
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_validate_markdown_syntax_invalid(self):
        """Test markdown syntax validation with invalid content."""
        content = """#Missing space after hash

This has issues:
- Unmatched [brackets
- ![](missing-alt-text.png)
```
Empty code block
```

###   Extra spaces
"""
        result = self.validator.validate_markdown_syntax(content)
        
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertGreater(len(result.warnings), 0)
    
    def test_extract_code_examples(self):
        """Test extraction of code examples from markdown."""
        content = """# Documentation

Here's a Python example:

```python
import os
from coderipple.webhook_parser import WebhookEvent
def process_webhook(payload):
    return WebhookEvent.parse(payload)
```

And a shell command:

```bash
python src/webhook_parser.py
pip install requirements.txt
```
"""
        examples = self.validator.extract_code_examples(content)
        
        self.assertEqual(len(examples), 2)
        
        python_example = examples[0]
        self.assertEqual(python_example.language, 'python')
        self.assertIn('import os', python_example.content)
        self.assertIn('webhook_parser', python_example.content)
        
        bash_example = examples[1]
        self.assertEqual(bash_example.language, 'bash')
        self.assertIn('python src/', bash_example.content)
    
    def test_validate_code_examples(self):
        """Test validation of code examples against system capabilities."""
        examples = [
            CodeExample(
                content="from coderipple.webhook_parser import WebhookEvent\nfrom strands import tool",
                language="python",
                line_number=5,
                context="Python imports"
            ),
            CodeExample(
                content="import nonexistent_module\nfrom fake_lib import something",
                language="python", 
                line_number=10,
                context="Bad imports"
            ),
            CodeExample(
                content="python src/webhook_parser.py\npython run_coderipple.py",
                language="bash",
                line_number=15,
                context="Shell commands"
            )
        ]
        
        result = self.validator.validate_code_examples(examples, self.temp_dir)
        
        # Should have warnings about missing imports but valid syntax
        self.assertTrue(result.is_valid)  # Syntax is valid even if imports don't exist
        self.assertGreater(len(result.warnings), 0)
    
    def test_extract_cross_references(self):
        """Test extraction of cross-reference links."""
        content = """# Documentation

See [system documentation](system/architecture.md) for details.

For user guides, check [getting started](getting_started.md).

External link: [GitHub](https://github.com/example/repo)

Internal anchor: [Configuration](#configuration-section)
"""
        references = self.validator.extract_cross_references(content)
        
        self.assertEqual(len(references), 4)
        
        # Check different link types
        link_types = [ref.link_type for ref in references]
        self.assertIn('file', link_types)
        self.assertIn('external', link_types)
        self.assertIn('section', link_types)
    
    def test_validate_cross_references(self):
        """Test validation of cross-reference links."""
        # Create test files
        (Path(self.temp_dir) / 'system').mkdir()
        (Path(self.temp_dir) / 'system' / 'architecture.md').write_text('# Architecture\n\n## Overview\n')
        (Path(self.temp_dir) / 'getting_started.md').write_text('# Getting Started\n')
        
        references = [
            CrossReference(
                text="architecture docs",
                target="system/architecture.md",
                line_number=5,
                link_type="file"
            ),
            CrossReference(
                text="getting started",
                target="getting_started.md",
                line_number=7,
                link_type="file"
            ),
            CrossReference(
                text="missing file",
                target="nonexistent.md",
                line_number=9,
                link_type="file"
            ),
            CrossReference(
                text="architecture overview",
                target="system/architecture.md#overview",
                line_number=11,
                link_type="section"
            )
        ]
        
        result = self.validator.validate_cross_references(references, self.temp_dir)
        
        # Should have errors for missing files
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
    
    def test_calculate_quality_score(self):
        """Test quality score calculation."""
        good_content = """# Comprehensive Documentation

This is a well-structured document with multiple sections.

## Features

- Feature 1: Important functionality
- Feature 2: Additional capabilities
- Feature 3: Advanced options

## Code Examples

```python
def example_function():
    \"\"\"Example function with documentation.\"\"\"
    return "Hello, World!"
```

## Architecture

The system follows these principles:

1. Modularity
2. Scalability  
3. Maintainability

### Components

- **Parser**: Handles input processing
- **Validator**: Ensures content quality
- **Generator**: Creates output files

"""
        
        validation_results = [
            ValidationResult(is_valid=True, errors=[], warnings=['Minor formatting issue'])
        ]
        
        score = self.validator.calculate_quality_score(good_content, validation_results)
        
        # Good content should score well
        self.assertGreaterEqual(score, 90.0)
        
        # Test with poor content
        poor_content = "# Bad\n\nVery short."
        poor_results = [
            ValidationResult(is_valid=False, errors=['Major error', 'Another error'], warnings=['Warning 1', 'Warning 2', 'Warning 3'])
        ]
        
        poor_score = self.validator.calculate_quality_score(poor_content, poor_results)
        self.assertLess(poor_score, 30.0)  # With more errors/warnings, score should be very low

class TestValidationTools(unittest.TestCase):
    """Test the validation tool functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_documentation_quality(self):
        """Test the validate_documentation_quality tool function."""
        content = """# Test Documentation

This is a test document with:

## Features

- Good structure
- Code examples
- Cross-references

```python
# Example code
def test():
    return True
```

See [related docs](other.md) for more information.
"""
        
        result = validate_documentation_quality(
            file_path="test.md",
            content=content,
            project_root=self.temp_dir
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('is_valid', result)
        self.assertIn('quality_score', result)
        self.assertIn('errors', result)
        self.assertIn('warnings', result)
        self.assertIn('code_examples_count', result)
        self.assertIn('cross_references_count', result)
    
    def test_enforce_quality_standards(self):
        """Test quality standards enforcement."""
        # Create a test file to make the cross-reference valid
        (Path(self.temp_dir) / 'system').mkdir(exist_ok=True)
        (Path(self.temp_dir) / 'system' / 'architecture.md').write_text('# Architecture\n\nSystem architecture details.')
        
        high_quality_content = """# Comprehensive Guide

This is a detailed guide with excellent structure and content.

## Overview

The system provides multiple capabilities:

1. **Primary Feature**: Core functionality
2. **Secondary Feature**: Additional capabilities
3. **Advanced Feature**: Power user options

## Implementation

```python
class DocumentationSystem:
    \"\"\"Main system class.\"\"\"
    
    def __init__(self):
        self.validator = ContentValidator()
    
    def process(self, content):
        \"\"\"Process documentation content.\"\"\"
        return self.validator.validate(content)
```

## Architecture

The system follows a modular architecture:

- **Input Layer**: Content processing
- **Validation Layer**: Quality assurance
- **Output Layer**: File generation

See [architecture docs](system/architecture.md) for details.

## Usage Examples

Multiple usage patterns are supported:

### Basic Usage

```python
validator = ContentValidator()
result = validator.validate_markdown_syntax(content)
```

### Advanced Usage

```python
validator = ContentValidator(project_root="/path/to/project")
quality_result = validator.calculate_quality_score(content, results)
```
"""
        
        result = enforce_quality_standards(
            content=high_quality_content,
            file_path="test.md",
            min_quality_score=70.0,
            project_root=self.temp_dir
        )
        
        self.assertTrue(result['write_approved'])
        self.assertGreaterEqual(result['quality_score'], 70.0)
        
        # Test with low quality content
        low_quality_content = "# Bad\n\nShort."
        
        poor_result = enforce_quality_standards(
            content=low_quality_content,
            file_path="bad.md",
            min_quality_score=70.0,
            project_root=self.temp_dir
        )
        
        self.assertFalse(poor_result['write_approved'])
        self.assertLess(poor_result['quality_score'], 70.0)
    
    def test_validate_and_improve_content(self):
        """Test content validation with improvement suggestions."""
        content = """# Documentation

Some content here.

```python
# Code without proper documentation
def func():
    return True
```
"""
        
        result = validate_and_improve_content(
            content=content,
            file_path="test.md",
            project_root=self.temp_dir
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('improvement_suggestions', result)
        self.assertIn('priority_level', result)
        self.assertIn('quality_score', result)

class TestSystemCapabilities(unittest.TestCase):
    """Test system capability detection."""
    
    def setUp(self):
        """Set up test project structure."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        
        # Create mock project structure
        (self.project_dir / 'src').mkdir()
        (self.project_dir / 'src' / 'webhook_parser.py').write_text('''
def parse_webhook(payload):
    """Parse webhook payload."""
    return WebhookEvent(payload)

class WebhookEvent:
    def __init__(self, data):
        self.data = data
''')
        
        (self.project_dir / 'src' / 'content_validation_tools.py').write_text('''
from strands import tool
@tool
def validate_documentation_quality(content):
    """Validate documentation quality."""
    pass

class ContentValidator:
    def validate_markdown_syntax(self, content):
        return ValidationResult()
''')
        
        (self.project_dir / 'requirements.txt').write_text('''
strands-agents==0.1.6
boto3==1.38.32
markdown-it-py==3.0.0
''')
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_get_system_capabilities(self):
        """Test extraction of system capabilities from project structure."""
        validator = ContentValidator(str(self.project_dir))
        capabilities = validator._get_system_capabilities(str(self.project_dir))
        
        self.assertIn('modules', capabilities)
        self.assertIn('functions', capabilities)
        self.assertIn('classes', capabilities)
        self.assertIn('files', capabilities)
        
        # Check if functions and classes were detected
        self.assertIn('parse_webhook', capabilities['functions'])
        self.assertIn('validate_documentation_quality', capabilities['functions'])
        self.assertIn('WebhookEvent', capabilities['classes'])
        self.assertIn('ContentValidator', capabilities['classes'])

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def test_empty_content(self):
        """Test validation with empty content."""
        result = validate_documentation_quality(
            file_path="empty.md",
            content="",
            project_root="/tmp"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertEqual(result['quality_score'], 0.0)
        self.assertGreater(len(result['errors']), 0)  # Should have "Content is empty" error
    
    def test_malformed_markdown(self):
        """Test validation with severely malformed markdown."""
        content = """
#######Too many hashes and no space
[[[[[[[Severely broken links]]]]]]]
```
Unclosed code block - missing closing backticks

((((((Severely nested parentheses))))))
****Bold without closing
"""
        
        result = validate_documentation_quality(
            file_path="malformed.md",
            content=content,
            project_root="/tmp"
        )
        
        self.assertFalse(result['is_valid'])
        self.assertGreater(len(result['errors']), 0)
    
    def test_nonexistent_project_root(self):
        """Test validation with nonexistent project root."""
        content = "# Test\n\nBasic content."
        
        result = validate_documentation_quality(
            file_path="test.md",
            content=content,
            project_root="/nonexistent/path"
        )
        
        # Should still work but with warnings about missing project context
        self.assertIsInstance(result, dict)
        self.assertIn('quality_score', result)

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete validation pipeline."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)
        
        # Create comprehensive project structure
        (self.project_dir / 'src').mkdir()
        (self.project_dir / 'docs').mkdir()
        (self.project_dir / 'tests').mkdir()
        
        # Create source files
        (self.project_dir / 'src' / 'main.py').write_text('''
from strands import Agent
from coderipple.webhook_parser import parse_webhook
def main():
    """Main application entry point."""
    agent = Agent()
    return agent.process()
''')
        
        # Create documentation
        (self.project_dir / 'docs' / 'api.md').write_text('''
# API Documentation

## Functions

### parse_webhook(payload)

Parse webhook payload and return structured data.
''')
        
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_complete_validation_pipeline(self):
        """Test the complete validation pipeline with a realistic document."""
        content = f"""# CodeRipple Documentation

CodeRipple is a multi-agent documentation system that automatically maintains software documentation.

## Features

- **Automatic Updates**: Documentation updates based on code changes
- **Multi-Agent System**: Specialized agents for different documentation layers
- **Quality Validation**: Comprehensive content validation pipeline

## Architecture

```python
from coderipple.webhook_parser import parse_webhook
from strands import Agent
# Main processing flow
def process_changes(webhook_payload):
    event = parse_webhook(webhook_payload)
    agent = Agent()
    return agent.process(event)
```

## System Components

- [Webhook Parser](src/webhook_parser.py): Processes GitHub webhooks
- [Content Validator](src/content_validation_tools.py): Validates documentation quality
- [API Documentation](docs/api.md): Detailed API reference

## Quality Standards

The system enforces quality standards including:

1. Markdown syntax validation
2. Code example verification
3. Cross-reference link checking
4. Content quality scoring

### Example Usage

```bash
python src/webhook_parser.py --input webhook.json
python run_coderipple.py --repository myproject
```

## Configuration

System configuration is handled through environment variables and configuration files.

See [configuration guide](docs/configuration.md) for details.
"""
        
        # Test the complete pipeline
        result = validate_documentation_quality(
            file_path="README.md",
            content=content,
            project_root=str(self.project_dir)
        )
        
        # Verify comprehensive results
        self.assertIsInstance(result, dict)
        self.assertIn('is_valid', result)
        self.assertIn('quality_score', result)
        self.assertIn('code_examples_count', result)
        self.assertIn('cross_references_count', result)
        
        # Should have code examples and cross-references
        self.assertGreater(result['code_examples_count'], 0)
        self.assertGreater(result['cross_references_count'], 0)
        
        # Test enforcement with high standards
        enforcement_result = enforce_quality_standards(
            content=content,
            file_path="README.md",
            min_quality_score=60.0,
            project_root=str(self.project_dir)
        )
        
        self.assertIn('write_approved', enforcement_result)
        self.assertIn('meets_standards', enforcement_result)

if __name__ == '__main__':
    unittest.main()