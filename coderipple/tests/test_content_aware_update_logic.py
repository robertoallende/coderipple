"""
Tests for Content-Aware Update Logic

Tests the intelligent content update functionality that enables agents to
merge new information with existing documentation instead of wholesale replacement.
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

from content_aware_update_logic import apply_content_aware_updates, ContentAwareUpdater


class TestContentAwareUpdateLogic(unittest.TestCase):
    """Test the content-aware update logic functionality"""
    
    def setUp(self):
        """Set up test environment with sample data"""
        self.sample_source_analysis = {
            'project_name': 'TestProject',
            'main_purpose': 'Test documentation system',
            'key_technologies': ['Python', 'AWS Strands'],
            'main_modules': ['parser', 'analyzer', 'generator'],
            'public_api': [
                {'name': 'parse_content', 'type': 'function', 'file': 'parser.py', 'description': 'Parses input content'},
                {'name': 'ContentAnalyzer', 'type': 'class', 'file': 'analyzer.py', 'description': 'Analyzes content structure'},
                {'name': 'generate_docs', 'type': 'function', 'file': 'generator.py', 'description': 'Generates documentation'}
            ]
        }
        
        self.sample_existing_docs = {
            'documentation_files': [
                {
                    'file_name': 'user_guide.md',
                    'category': 'user',
                    'title': 'User Guide',
                    'sections': [
                        {'title': 'Getting Started', 'content': 'Basic setup instructions'},
                        {'title': 'API Reference', 'content': 'Available functions: parse_content()'}
                    ],
                    'topics_covered': ['setup', 'usage', 'api'],
                    'apis_mentioned': ['parse_content'],
                    'completeness_score': 0.7
                },
                {
                    'file_name': 'architecture.md',
                    'category': 'system',
                    'title': 'System Architecture',
                    'sections': [
                        {'title': 'Overview', 'content': 'System design overview'},
                        {'title': 'Components', 'content': 'Parser and analyzer modules'}
                    ],
                    'topics_covered': ['architecture', 'components'],
                    'apis_mentioned': [],
                    'completeness_score': 0.8
                }
            ]
        }
    
    def test_apply_content_aware_updates_success(self):
        """Test that the tool successfully determines update strategies"""
        result = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/parser.py'],
            git_diff='+def new_parse_function():\n+    return "parsed"',
            target_category='user',
            source_analysis=self.sample_source_analysis,
            existing_docs=self.sample_existing_docs
        )
        
        # Validate success
        self.assertEqual(result['status'], 'success')
        
        # Should have update decision
        self.assertIn('update_decision', result)
        decision = result['update_decision']
        self.assertIsInstance(decision['should_update'], bool)
        self.assertIn(decision['strategy'], ['create_new', 'update_existing', 'merge_content'])
        
        # Should have content updates
        self.assertIn('content_updates', result)
        self.assertIsInstance(result['content_updates'], list)
    
    def test_update_existing_strategy(self):
        """Test strategy when relevant existing documentation exists"""
        result = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/parser.py'],
            git_diff='+def enhanced_parse():\n+    """Enhanced parsing functionality"""\n+    pass',
            target_category='user',
            source_analysis=self.sample_source_analysis,
            existing_docs=self.sample_existing_docs
        )
        
        self.assertEqual(result['status'], 'success')
        decision = result['update_decision']
        
        # Should choose to update existing content
        self.assertEqual(decision['strategy'], 'update_existing')
        self.assertTrue(decision['should_update'])
        
        # Should target the relevant existing file
        self.assertEqual(decision['target_file'], 'user_guide.md')
        
        # Should have preservation notes
        self.assertGreater(len(decision['preservation_notes']), 0)
    
    def test_create_new_strategy(self):
        """Test strategy when no relevant existing documentation exists"""
        # Test with empty existing docs
        empty_docs = {'documentation_files': []}
        
        result = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/new_module.py'],
            git_diff='+def completely_new_function():\n+    pass',
            target_category='user',
            source_analysis=self.sample_source_analysis,
            existing_docs=empty_docs
        )
        
        self.assertEqual(result['status'], 'success')
        decision = result['update_decision']
        
        # Should choose to create new content
        self.assertEqual(decision['strategy'], 'create_new')
        self.assertTrue(decision['should_update'])
        
        # Should suggest appropriate filename
        self.assertTrue(decision['target_file'].endswith('.md'))
    
    def test_content_preservation(self):
        """Test that valuable existing content is preserved"""
        result = apply_content_aware_updates(
            change_type='enhancement',
            affected_files=['src/analyzer.py'],
            git_diff='+    # Enhanced analysis logic\n+    return improved_result',
            target_category='user',
            source_analysis=self.sample_source_analysis,
            existing_docs=self.sample_existing_docs
        )
        
        self.assertEqual(result['status'], 'success')
        decision = result['update_decision']
        
        # Should have preservation notes
        self.assertGreater(len(decision['preservation_notes']), 0)
        
        # Preservation notes should mention specific content being preserved
        preservation_text = ' '.join(decision['preservation_notes'])
        self.assertIn('preserving', preservation_text.lower())
    
    def test_different_change_types(self):
        """Test that different change types result in appropriate strategies"""
        change_types = ['feature', 'bugfix', 'refactor', 'enhancement']
        
        for change_type in change_types:
            with self.subTest(change_type=change_type):
                result = apply_content_aware_updates(
                    change_type=change_type,
                    affected_files=['src/parser.py'],
                    git_diff=f'+# {change_type} change',
                    target_category='user',
                    source_analysis=self.sample_source_analysis,
                    existing_docs=self.sample_existing_docs
                )
                
                self.assertEqual(result['status'], 'success')
                self.assertIn('update_decision', result)
                
                # All change types should result in some update decision
                decision = result['update_decision']
                self.assertIsInstance(decision['should_update'], bool)
    
    def test_different_categories(self):
        """Test that different documentation categories are handled appropriately"""
        categories = ['user', 'system', 'decisions']
        
        for category in categories:
            with self.subTest(category=category):
                result = apply_content_aware_updates(
                    change_type='feature',
                    affected_files=['src/parser.py'],
                    git_diff='+def new_function(): pass',
                    target_category=category,
                    source_analysis=self.sample_source_analysis,
                    existing_docs=self.sample_existing_docs
                )
                
                self.assertEqual(result['status'], 'success')
                
                # Should appropriately target files for each category
                decision = result['update_decision']
                if decision['should_update']:
                    target_file = decision['target_file']
                    self.assertTrue(target_file.endswith('.md'))
    
    def test_content_update_details(self):
        """Test that content updates include necessary details"""
        result = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/parser.py'],
            git_diff='+def advanced_parse():\n+    """Advanced parsing with new features"""\n+    return result',
            target_category='user',
            source_analysis=self.sample_source_analysis,
            existing_docs=self.sample_existing_docs
        )
        
        self.assertEqual(result['status'], 'success')
        updates = result['content_updates']
        
        if updates:
            update = updates[0]
            
            # Should have required fields
            required_fields = ['update_type', 'target_section', 'new_content', 'merge_strategy', 'confidence', 'rationale']
            for field in required_fields:
                self.assertIn(field, update)
            
            # Content should be meaningful
            self.assertGreater(len(update['new_content']), 10)
            self.assertGreater(len(update['rationale']), 10)
            
            # Confidence should be reasonable
            self.assertGreaterEqual(update['confidence'], 0.0)
            self.assertLessEqual(update['confidence'], 1.0)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        # Test with invalid change type
        result = apply_content_aware_updates(
            change_type='invalid_type',
            affected_files=[],
            git_diff='',
            target_category='user',
            source_analysis=None,
            existing_docs=None
        )
        
        # Should handle gracefully (though may not have updates)
        self.assertIn('status', result)
        
    def test_git_diff_parsing(self):
        """Test that git diff content is properly parsed for updates"""
        complex_diff = """
+def new_feature():
+    '''New feature for enhanced functionality'''
+    return True
+
+class NewClass:
+    '''New class for better organization'''
+    pass
+
-def old_function():
-    return False
        """
        
        result = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/features.py'],
            git_diff=complex_diff,
            target_category='user',
            source_analysis=self.sample_source_analysis,
            existing_docs={'documentation_files': []}
        )
        
        self.assertEqual(result['status'], 'success')
        
        # Should extract meaningful information from diff
        if result['content_updates']:
            content = result['content_updates'][0]['new_content']
            self.assertIn('new_feature', content.lower())


class TestContentAwareUpdater(unittest.TestCase):
    """Test the ContentAwareUpdater class directly"""
    
    def setUp(self):
        """Set up test environment"""
        self.source_analysis = {
            'public_api': [
                {'name': 'test_function', 'file': 'test.py'}
            ]
        }
        
        self.existing_docs = {
            'documentation_files': [
                {
                    'file_name': 'test.md',
                    'category': 'user',
                    'sections': [{'title': 'Test Section', 'content': 'Test content'}],
                    'apis_mentioned': ['test_function'],
                    'topics_covered': ['testing'],
                    'completeness_score': 0.8
                }
            ]
        }
        
        self.updater = ContentAwareUpdater(self.source_analysis, self.existing_docs)
    
    def test_find_relevant_existing_docs(self):
        """Test finding relevant documentation for changed files"""
        relevant_docs = self.updater._find_relevant_existing_docs(['src/test.py'], 'user')
        
        self.assertGreater(len(relevant_docs), 0)
        self.assertEqual(relevant_docs[0]['file_name'], 'test.md')
    
    def test_api_relates_to_file(self):
        """Test API-to-file relationship detection"""
        self.assertTrue(self.updater._api_relates_to_file('test_function', 'src/test.py'))
        self.assertFalse(self.updater._api_relates_to_file('other_function', 'src/test.py'))
    
    def test_topic_relates_to_file(self):
        """Test topic-to-file relationship detection"""
        self.assertTrue(self.updater._topic_relates_to_file('test', 'src/test.py'))
        self.assertFalse(self.updater._topic_relates_to_file('unrelated', 'src/test.py'))
    
    def test_determine_target_filename(self):
        """Test target filename determination"""
        filename = self.updater._determine_target_filename('feature', ['src/api.py'], 'user')
        self.assertTrue(filename.endswith('.md'))
        
        filename = self.updater._determine_target_filename('refactor', ['src/arch.py'], 'system')
        self.assertTrue(filename.endswith('.md'))


class TestContentAwareUpdateCriteria(unittest.TestCase):
    """Validate that content-aware update functionality meets requirements"""
    
    def setUp(self):
        """Set up comprehensive test environment"""
        self.source_analysis = {
            'project_name': 'TestProject',
            'main_purpose': 'Multi-agent documentation system',
            'public_api': [
                {'name': 'existing_function', 'type': 'function', 'file': 'module.py'},
                {'name': 'new_function', 'type': 'function', 'file': 'module.py'}
            ],
            'key_technologies': ['Python', 'AWS']
        }
        
        self.existing_docs = {
            'documentation_files': [
                {
                    'file_name': 'user_guide.md',
                    'category': 'user',
                    'sections': [
                        {'title': 'Functions', 'content': 'Available functions:\n- existing_function(): Does important work'},
                        {'title': 'Examples', 'content': 'Usage examples here'}
                    ],
                    'apis_mentioned': ['existing_function'],
                    'topics_covered': ['functions', 'examples'],
                    'completeness_score': 0.8
                }
            ]
        }
    
    def test_intelligent_content_updates(self):
        """
        Content-Aware Updates: Agents update existing content instead of replacing it
        
        Validation: Update existing doc section, verify preservation + enhancement
        """
        # Test updating existing content
        result = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/module.py'],
            git_diff='+def new_function():\n+    """New functionality added"""\n+    return "new"',
            target_category='user',
            source_analysis=self.source_analysis,
            existing_docs=self.existing_docs
        )
        
        # Tool should work
        self.assertEqual(result['status'], 'success')
        
        # Should choose to update existing content, not replace
        decision = result['update_decision']
        self.assertEqual(decision['strategy'], 'update_existing')
        self.assertTrue(decision['should_update'])
        
        # Should preserve existing valuable content
        self.assertGreater(len(decision['preservation_notes']), 0)
        preservation_text = ' '.join(decision['preservation_notes']).lower()
        self.assertIn('preserving', preservation_text)
        
        # Should have specific content updates
        updates = result['content_updates']
        self.assertGreater(len(updates), 0)
        
        # Updates should be intelligent, not wholesale replacement
        for update in updates:
            self.assertIn(update['update_type'], ['section_update', 'section_add', 'content_merge'])
            self.assertIn(update['merge_strategy'], ['append', 'merge', 'enhance'])
            
            # Should have rationale for updates
            self.assertGreater(len(update['rationale']), 10)
            self.assertGreater(update['confidence'], 0.0)
        
        print(f"\n✅ Content-Aware Updates: Intelligent content merging working correctly:")
        print(f"   Strategy: {decision['strategy']} (preserves existing content)")
        print(f"   Updates planned: {len(updates)} intelligent updates")
        print(f"   Content preserved: {len(decision['preservation_notes'])} items")
        print(f"   Target file: {decision['target_file']}")
        
        # Test the IF/ELSE logic requirements
        
        # Test: IF existing content EXISTS, merge new info with existing
        self.assertEqual(decision['strategy'], 'update_existing')
        merge_updates = [u for u in updates if u['merge_strategy'] in ['merge', 'append', 'enhance']]
        self.assertGreater(len(merge_updates), 0, "Should merge with existing content")
        
        # Test with no existing content - should use source analysis foundation
        empty_docs = {'documentation_files': []}
        result_new = apply_content_aware_updates(
            change_type='feature',
            affected_files=['src/new_module.py'],
            git_diff='+def brand_new_function(): pass',
            target_category='user',
            source_analysis=self.source_analysis,
            existing_docs=empty_docs
        )
        
        # Should create new content based on source analysis
        decision_new = result_new['update_decision']
        self.assertEqual(decision_new['strategy'], 'create_new')
        
        # Content should include source analysis information
        if result_new['content_updates']:
            new_content = result_new['content_updates'][0]['new_content']
            self.assertIn('TestProject', new_content)  # Should use project name from source analysis
        
        print(f"   ✓ WHEN existing content EXISTS: merge strategy used")
        print(f"   ✓ WHEN no existing content: source analysis foundation used")
        
        # This level of intelligence enables agents to enhance rather than replace


if __name__ == "__main__":
    unittest.main(verbosity=2)