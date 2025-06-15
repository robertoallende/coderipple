"""
Tests for Source Code Analysis Tool

Tests the source code analysis functionality that enables agents to understand
what the project actually does, rather than relying solely on git diffs.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock strands to avoid dependency issues
mock_strands = MagicMock()
mock_strands.tool = lambda func: func
sys.modules['strands'] = mock_strands

from source_code_analysis_tool import analyze_source_code, SourceCodeAnalyzer


class TestSourceCodeAnalysisTool(unittest.TestCase):
    """Test the source code analysis tool functionality"""
    
    def test_analyze_source_code_tool_success(self):
        """Test that the analyze_source_code tool returns meaningful results"""
        # Test on current project
        result = analyze_source_code(".")
        
        # Validate success
        self.assertEqual(result['status'], 'success')
        
        # Validate project identification
        self.assertIsInstance(result['project_name'], str)
        self.assertTrue(len(result['project_name']) > 0)
        self.assertNotEqual(result['project_name'], 'unknown')
        
        # Validate purpose identification
        self.assertIsInstance(result['main_purpose'], str)
        self.assertTrue(len(result['main_purpose']) > 10)  # Should be meaningful
        
        # Validate technology detection
        self.assertIsInstance(result['key_technologies'], list)
        self.assertGreater(len(result['key_technologies']), 0)
        
        # Validate module identification
        self.assertIsInstance(result['main_modules'], list)
        self.assertGreater(len(result['main_modules']), 0)
        
        # Validate API discovery
        self.assertIsInstance(result['public_api'], list)
        self.assertGreater(len(result['public_api']), 0)
        
        # Validate statistics
        self.assertIsInstance(result['statistics'], dict)
        self.assertGreater(result['statistics']['total_files'], 0)
        self.assertGreater(result['statistics']['total_lines'], 0)
        
        # Validate summary
        self.assertIsInstance(result['summary'], str)
        self.assertTrue(len(result['summary']) > 20)  # Should be comprehensive
    
    def test_project_understanding_quality(self):
        """Test that the tool produces accurate understanding of the project"""
        result = analyze_source_code(".")
        
        # Should correctly identify this as a documentation/agent system
        purpose_lower = result['main_purpose'].lower()
        self.assertTrue(
            any(keyword in purpose_lower for keyword in ['documentation', 'agent', 'webhook']),
            f"Purpose should mention documentation/agent/webhook: {result['main_purpose']}"
        )
        
        # Should detect key technologies we know are in use
        tech_names = [tech.lower() for tech in result['key_technologies']]
        self.assertTrue(
            any('strands' in tech for tech in tech_names),
            f"Should detect AWS Strands: {result['key_technologies']}"
        )
        
        # Should identify main agent modules
        modules = result['main_modules']
        agent_modules = [m for m in modules if 'agent' in m.lower()]
        self.assertGreater(len(agent_modules), 0, "Should identify agent modules")
        
        # Should find meaningful public APIs
        public_apis = result['public_api']
        self.assertTrue(
            any(api['type'] == 'function' for api in public_apis),
            "Should find public functions"
        )
    
    def test_meaningful_content_generation_basis(self):
        """Test that the analysis provides sufficient context for meaningful content generation"""
        result = analyze_source_code(".")
        
        # The result should provide enough information for an agent to understand:
        # 1. What the project does
        self.assertIn('agent', result['main_purpose'].lower())
        
        # 2. How it's structured
        self.assertGreater(len(result['main_modules']), 3)
        
        # 3. What technologies it uses
        self.assertGreater(len(result['key_technologies']), 2)
        
        # 4. What APIs are available
        self.assertGreater(len(result['public_api']), 5)
        
        # 5. How to use it (entry points)
        self.assertIsInstance(result['entry_points'], list)
        
        # This should be sufficient for generating meaningful documentation
        # rather than generic "we added some functionality" content
    
    def test_error_handling(self):
        """Test error handling for invalid project paths"""
        result = analyze_source_code("/nonexistent/path")
        
        # Should handle errors gracefully
        self.assertEqual(result['status'], 'error')
        self.assertIn('error', result)
        self.assertIsInstance(result['error'], str)
        
        # Should still provide fallback values
        self.assertEqual(result['project_name'], 'unknown')
        self.assertIn('Unable to analyze', result['main_purpose'])


class TestSourceCodeAnalyzer(unittest.TestCase):
    """Test the SourceCodeAnalyzer class directly"""
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        analyzer = SourceCodeAnalyzer(".")
        self.assertTrue(analyzer.project_root.exists())
    
    def test_project_name_inference(self):
        """Test project name is correctly inferred"""
        analyzer = SourceCodeAnalyzer(".")
        project_name = analyzer._infer_project_name()
        
        self.assertIsInstance(project_name, str)
        self.assertTrue(len(project_name) > 0)
        self.assertNotIn('__pycache__', project_name)
    
    def test_technology_detection(self):
        """Test technology detection works"""
        analyzer = SourceCodeAnalyzer(".")
        source_dir = analyzer._find_source_directory()
        files = analyzer._find_python_files(source_dir)
        technologies = analyzer._detect_technologies(files)
        
        self.assertIsInstance(technologies, list)
        self.assertGreater(len(technologies), 0)
        
        # Should detect AWS Strands since it's used throughout
        tech_names = [tech.lower() for tech in technologies]
        self.assertTrue(any('strands' in tech for tech in tech_names))
    
    def test_main_modules_identification(self):
        """Test main modules are correctly identified"""
        analyzer = SourceCodeAnalyzer(".")
        source_dir = analyzer._find_source_directory()
        files = analyzer._find_python_files(source_dir)
        modules = analyzer._identify_main_modules(files)
        
        self.assertIsInstance(modules, list)
        self.assertGreater(len(modules), 0)
        
        # Should prioritize agent modules
        agent_modules = [m for m in modules if 'agent' in m]
        self.assertGreater(len(agent_modules), 0)


class TestStepOneSuccessCriteria(unittest.TestCase):
    """Validate that Step 1 success criteria are met"""
    
    def test_step1_outcome_agents_understand_project(self):
        """
        Step 1 Success Criteria: Agents can understand what the project actually does
        
        Validation: Tool can generate a meaningful project summary from codebase alone
        """
        result = analyze_source_code(".")
        
        # Tool should work
        self.assertEqual(result['status'], 'success')
        
        # Should produce accurate description of what project does
        self.assertEqual(result['project_name'], 'coderipple')
        self.assertIn('documentation', result['main_purpose'].lower())
        
        # Should identify key characteristics that enable meaningful content generation
        self.assertGreater(len(result['key_technologies']), 3)
        self.assertGreater(len(result['main_modules']), 5)
        self.assertGreater(len(result['public_api']), 10)
        
        # Summary should be comprehensive and accurate
        summary = result['summary']
        self.assertIn('coderipple', summary)
        self.assertTrue(len(summary) > 50)  # Should be detailed
        
        print(f"\n✅ Step 1 Success: Tool correctly identified:")
        print(f"   Project: {result['project_name']}")
        print(f"   Purpose: {result['main_purpose']}")
        print(f"   Technologies: {len(result['key_technologies'])} detected")
        print(f"   Public APIs: {len(result['public_api'])} functions/classes")
        print(f"   Summary: {result['summary']}")
        
        # This level of understanding should enable agents to generate
        # meaningful documentation instead of generic content


if __name__ == "__main__":
    unittest.main(verbosity=2)