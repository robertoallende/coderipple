"""
Tests for Existing Content Discovery Tool

Tests the enhanced content discovery functionality that enables agents to read
and understand existing documentation content, not just discover file names.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import tempfile
import shutil

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock strands to avoid dependency issues
mock_strands = MagicMock()
mock_strands.tool = lambda func: func
sys.modules['strands'] = mock_strands

from coderipple.existing_content_discovery_tool import analyze_existing_content, ExistingContentAnalyzer

class TestExistingContentDiscoveryTool(unittest.TestCase):
    """Test the existing content discovery tool functionality"""
    
    def setUp(self):
        """Set up test environment with sample documentation"""
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.test_dir, "test_docs")
        os.makedirs(self.docs_dir)
        
        # Create sample documentation files
        self._create_sample_docs()
        
        # Sample source analysis
        self.source_analysis = {
            'public_api': [
                {'name': 'analyze_code', 'type': 'function'},
                {'name': 'DocumentParser', 'type': 'class'},
                {'name': 'generate_report', 'type': 'function'}
            ],
            'key_technologies': ['Python', 'AWS Strands', 'Markdown'],
            'main_modules': ['parser', 'analyzer', 'generator']
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_sample_docs(self):
        """Create sample documentation files for testing"""
        
        # User documentation
        user_doc = """# Getting Started
        
This is a comprehensive guide to getting started with our project.

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Basic Usage

Use the `analyze_code()` function to analyze your code:

```python
result = analyze_code("path/to/code")
```

## Advanced Features

The system supports advanced configuration and customization.
"""
        with open(os.path.join(self.docs_dir, "getting_started.md"), 'w') as f:
            f.write(user_doc)
        
        # System documentation
        system_doc = """# System Architecture

## Overview

Our system follows a modular architecture with three main components.

## Components

### Parser Module
Handles code parsing and analysis.

### Analyzer Module  
Performs deep analysis of code structure.

### Generator Module
Generates documentation from analysis results.

## Technologies

- Python for core functionality
- AWS Strands for coordination
- Markdown for documentation

## APIs

The `DocumentParser` class provides the main interface.
"""
        os.makedirs(os.path.join(self.docs_dir, "system"), exist_ok=True)
        with open(os.path.join(self.docs_dir, "system", "architecture.md"), 'w') as f:
            f.write(system_doc)
        
        # Decision documentation
        decision_doc = """# Architectural Decisions

## ADR-001: Technology Choice

We chose Python for its simplicity and ecosystem.

### Context
Need a flexible language for rapid development.

### Decision
Use Python 3.8+ with modern tooling.

### Consequences
- Pros: Fast development, great libraries
- Cons: Performance limitations for heavy workloads
"""
        os.makedirs(os.path.join(self.docs_dir, "decisions"), exist_ok=True)
        with open(os.path.join(self.docs_dir, "decisions", "tech_choices.md"), 'w') as f:
            f.write(decision_doc)
    
    def test_analyze_existing_content_success(self):
        """Test that the tool successfully analyzes existing content"""
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        # Validate success
        self.assertEqual(result['status'], 'success')
        
        # Should find all documentation files
        self.assertEqual(len(result['documentation_files']), 3)
        
        # Should categorize files correctly
        categories = {f['category'] for f in result['documentation_files']}
        self.assertIn('user', categories)
        self.assertIn('system', categories)
        self.assertIn('decisions', categories)
        
        # Should parse content structure
        for file in result['documentation_files']:
            self.assertIsInstance(file['sections'], list)
            self.assertGreater(len(file['sections']), 0)
            self.assertIsInstance(file['word_count'], int)
            self.assertGreater(file['word_count'], 0)
    
    def test_content_parsing_quality(self):
        """Test that content parsing extracts meaningful information"""
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        # Find the getting started doc
        getting_started = next(f for f in result['documentation_files'] if 'getting_started' in f['file_name'])
        
        # Should extract title correctly
        self.assertEqual(getting_started['title'], 'Getting Started')
        
        # Should identify sections
        section_titles = [s['title'] for s in getting_started['sections']]
        self.assertIn('Installation', section_titles)
        self.assertIn('Basic Usage', section_titles)
        
        # Should extract API mentions
        self.assertIn('analyze_code', getting_started['apis_mentioned'])
        
        # Should identify topics
        self.assertTrue(len(getting_started['topics_covered']) > 0)
    
    def test_gap_identification(self):
        """Test that the tool identifies gaps between docs and code"""
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        # Should identify gaps
        self.assertGreater(len(result['content_gaps']), 0)
        
        # Should find missing API documentation
        gap_descriptions = [gap['description'] for gap in result['content_gaps']]
        missing_api_gaps = [desc for desc in gap_descriptions if 'generate_report' in desc]
        self.assertGreater(len(missing_api_gaps), 0)
        
        # Should categorize gap severity
        severities = {gap['severity'] for gap in result['content_gaps']}
        self.assertTrue(len(severities) > 0)
    
    def test_coverage_analysis(self):
        """Test that coverage analysis works correctly"""
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        coverage = result['coverage_analysis']
        
        # Should analyze coverage by category
        self.assertIn('by_category', coverage)
        self.assertIn('user', coverage['by_category'])
        self.assertIn('system', coverage['by_category'])
        self.assertIn('decisions', coverage['by_category'])
        
        # Coverage should be between 0 and 1
        for cat_coverage in coverage['by_category'].values():
            self.assertGreaterEqual(cat_coverage, 0.0)
            self.assertLessEqual(cat_coverage, 1.0)
        
        # Should have overall completeness
        self.assertIn('overall_completeness', coverage)
        self.assertGreaterEqual(coverage['overall_completeness'], 0.0)
        self.assertLessEqual(coverage['overall_completeness'], 1.0)
    
    def test_cross_reference_analysis(self):
        """Test cross-reference integrity checking"""
        # Add a doc with cross-references
        cross_ref_doc = """# Cross Reference Test
        
See [Getting Started](getting_started.md) for basic usage.
Also check [Architecture](system/architecture.md) for details.
This [broken link](nonexistent.md) should be detected.
"""
        with open(os.path.join(self.docs_dir, "cross_ref_test.md"), 'w') as f:
            f.write(cross_ref_doc)
        
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        # Should analyze cross-reference integrity
        self.assertIn('cross_reference_integrity', result['coverage_analysis'])
        integrity = result['coverage_analysis']['cross_reference_integrity']
        self.assertGreaterEqual(integrity, 0.0)
        self.assertLessEqual(integrity, 1.0)
    
    def test_topics_analysis(self):
        """Test topic extraction and gap identification"""
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        topics = result['topics_analysis']
        
        # Should extract documented topics
        self.assertIn('documented', topics)
        self.assertIsInstance(topics['documented'], list)
        self.assertGreater(len(topics['documented']), 0)
        
        # Should identify missing topics
        self.assertIn('missing', topics)
        self.assertIsInstance(topics['missing'], list)
        
        # Should identify technology-related topics
        documented_topics = set(topics['documented'])
        self.assertTrue(any('python' in topic.lower() for topic in documented_topics))

class TestContentDiscoverySuccessCriteria(unittest.TestCase):
    """Validate that content discovery functionality meets requirements"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        self.docs_dir = os.path.join(self.test_dir, "test_docs")
        os.makedirs(self.docs_dir)
        
        # Create sample docs with varying quality
        self._create_comprehensive_test_docs()
        
        self.source_analysis = {
            'public_api': [
                {'name': 'documented_function', 'type': 'function'},
                {'name': 'undocumented_function', 'type': 'function'},
                {'name': 'DocumentedClass', 'type': 'class'},
                {'name': 'UndocumentedClass', 'type': 'class'}
            ],
            'key_technologies': ['Python', 'AWS', 'Strands'],
            'main_modules': ['documented_module', 'undocumented_module']
        }
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def _create_comprehensive_test_docs(self):
        """Create comprehensive test documentation"""
        
        # Well-documented API
        api_doc = """# API Documentation

## Functions

### documented_function()

This function performs important analysis.

```python
result = documented_function(input_data)
```

## Classes

### DocumentedClass

Well-documented class with examples.
"""
        with open(os.path.join(self.docs_dir, "api.md"), 'w') as f:
            f.write(api_doc)
        
        # Incomplete user guide
        user_doc = """# User Guide

Basic information only.
"""
        with open(os.path.join(self.docs_dir, "user_guide.md"), 'w') as f:
            f.write(user_doc)
    
    def test_agents_read_existing_content(self):
        """
        Content Discovery: Agents know what documentation already exists and can read it
        
        Validation: Agent can summarize what's already documented vs what's missing
        """
        result = analyze_existing_content(self.docs_dir, self.source_analysis)
        
        # Tool should work
        self.assertEqual(result['status'], 'success')
        
        # Should read and parse existing content
        self.assertGreater(len(result['documentation_files']), 0)
        
        # Should extract content details (not just file names)
        for file in result['documentation_files']:
            self.assertIn('sections', file)
            self.assertIn('topics_covered', file)
            self.assertIn('apis_mentioned', file)
            self.assertIn('summary', file)
            self.assertTrue(len(file['summary']) > 10)  # Should have meaningful summary
        
        # Should identify what's documented vs missing
        self.assertIn('content_gaps', result)
        self.assertIn('topics_analysis', result)
        
        # Should identify specific gaps
        gaps = result['content_gaps']
        gap_types = {gap['type'] for gap in gaps}
        self.assertIn('missing_api', gap_types)  # Should find undocumented APIs
        
        # Should provide actionable insights
        self.assertIn('insights', result)
        self.assertGreater(len(result['insights']), 0)
        
        print(f"\n✅ Content Discovery: Tool correctly analyzed existing content:")
        print(f"   Files analyzed: {len(result['documentation_files'])}")
        print(f"   Content gaps identified: {len(result['content_gaps'])}")
        print(f"   Topics documented: {len(result['topics_analysis']['documented'])}")
        print(f"   Topics missing: {len(result['topics_analysis']['missing'])}")
        print(f"   Summary: {result['summary']}")
        
        # Should correctly identify documented vs undocumented items
        documented_apis = set()
        for file in result['documentation_files']:
            documented_apis.update(file['apis_mentioned'])
        
        self.assertIn('documented_function', documented_apis)
        
        # Should suggest what's missing
        missing_api_gaps = [gap for gap in gaps if gap['type'] == 'missing_api']
        missing_api_names = {gap['description'] for gap in missing_api_gaps}
        self.assertTrue(any('undocumented_function' in desc for desc in missing_api_names))
        
        # This level of content understanding enables intelligent updates
        # rather than wholesale replacement

if __name__ == "__main__":
    unittest.main(verbosity=2)