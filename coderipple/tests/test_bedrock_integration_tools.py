"""
Tests for Bedrock Integration Tools (Step 4D)

Test the Amazon Bedrock integration tools for content enhancement,
consistency checking, and dynamic example generation.
"""

import unittest
from unittest.mock import patch, MagicMock
import sys
import os
from coderipple.bedrock_integration_tools import (
    enhance_content_with_bedrock,
    check_documentation_consistency,
    generate_dynamic_examples,
    analyze_content_gaps
)

class TestBedrockIntegrationTools(unittest.TestCase):
    """Test Bedrock integration tools functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_content = """# Test Documentation
        
This is a test documentation section that needs enhancement.
It contains basic information about the system.
        """
        
        self.test_context = {
            'section_type': 'user_guide',
            'target_audience': 'developers',
            'change_type': 'feature',
            'repository_context': 'test-repo'
        }
        
        self.mock_bedrock_response = {
            'body': MagicMock()
        }
        
        self.mock_response_content = {
            'content': [{
                'text': '{"enhanced_content": "Enhanced test content", "improvements_made": ["Better clarity", "Added examples"], "quality_score": 0.85}'
            }]
        }
    
    @patch('boto3.client')
    def test_enhance_content_with_bedrock_success(self, mock_boto3):
        """Test successful content enhancement with Bedrock"""
        # Setup mock
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        # Mock the response body
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = '{"content": [{"text": "{\\"enhanced_content\\": \\"Enhanced test content\\", \\"improvements_made\\": [\\"Better clarity\\"], \\"quality_score\\": 0.85}"}]}'
        
        mock_client.invoke_model.return_value = {
            'body': mock_response_body
        }
        
        # Call the function
        result = enhance_content_with_bedrock(
            content=self.test_content,
            context=self.test_context
        )
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        self.assertIn('content', result)
        self.assertIn('json', result['content'][0])
        
        enhanced_data = result['content'][0]['json']
        self.assertIn('enhanced_content', enhanced_data)
        self.assertIn('improvements_made', enhanced_data)
        self.assertIn('quality_score', enhanced_data)
        
        # Verify boto3 was called correctly
        mock_boto3.assert_called_once_with('bedrock-runtime', region_name='us-west-2')
        mock_client.invoke_model.assert_called_once()
    
    @patch('boto3.client')
    def test_enhance_content_with_bedrock_error(self, mock_boto3):
        """Test error handling in content enhancement"""
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        mock_client.invoke_model.side_effect = Exception("Bedrock API error")
        
        # Call the function
        result = enhance_content_with_bedrock(
            content=self.test_content,
            context=self.test_context
        )
        
        # Assertions
        self.assertEqual(result['status'], 'error')
        self.assertIn('Enhancement failed', result['content'][0]['text'])
        self.assertIn('fallback_content', result)
        self.assertEqual(result['fallback_content'], self.test_content)
    
    @patch('boto3.client')
    def test_check_documentation_consistency_success(self, mock_boto3):
        """Test successful consistency checking"""
        # Setup mock
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = '{"content": [{"text": "{\\"is_consistent\\": true, \\"conflicts\\": [], \\"recommendations\\": [\\"Good alignment\\"], \\"confidence_score\\": 0.9}"}]}'
        
        mock_client.invoke_model.return_value = {
            'body': mock_response_body
        }
        
        content_layers = {
            'tourist_guide': 'User documentation content',
            'building_inspector': 'System documentation content',
            'historian': 'Decision documentation content'
        }
        
        # Call the function
        result = check_documentation_consistency(
            content_layers=content_layers,
            focus_area='user_experience'
        )
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        self.assertIn('content', result)
        self.assertIn('json', result['content'][0])
        
        consistency_data = result['content'][0]['json']
        self.assertIn('is_consistent', consistency_data)
        self.assertIn('conflicts', consistency_data)
        self.assertIn('recommendations', consistency_data)
    
    @patch('boto3.client')
    def test_generate_dynamic_examples_success(self, mock_boto3):
        """Test successful dynamic example generation"""
        # Setup mock
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = '{"content": [{"text": "{\\"examples\\": [{\\"code\\": \\"print(\\\\\\"Hello World\\\\\\")\\", \\"language\\": \\"python\\", \\"description\\": \\"Basic example\\", \\"context\\": \\"Getting started\\", \\"complexity_level\\": \\"beginner\\"}], \\"usage_notes\\": [\\"Run in Python environment\\"], \\"prerequisites\\": [\\"Python installed\\"]}"}]}'
        
        mock_client.invoke_model.return_value = {
            'body': mock_response_body
        }
        
        code_context = {
            'file_changes': ['src/main.py', 'src/utils.py'],
            'system_capabilities': ['GitHub webhook processing'],
            'target_use_case': 'Basic system usage'
        }
        
        # Call the function
        result = generate_dynamic_examples(
            code_context=code_context,
            example_type='usage'
        )
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        self.assertIn('content', result)
        self.assertIn('json', result['content'][0])
        
        examples_data = result['content'][0]['json']
        self.assertIn('examples', examples_data)
        self.assertIn('usage_notes', examples_data)
        self.assertIn('prerequisites', examples_data)
        
        # Check example structure
        if examples_data['examples']:
            example = examples_data['examples'][0]
            self.assertIn('code', example)
            self.assertIn('language', example)
            self.assertIn('description', example)
    
    @patch('boto3.client')
    def test_analyze_content_gaps_success(self, mock_boto3):
        """Test successful content gap analysis"""
        # Setup mock
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = '{"content": [{"text": "{\\"coverage_score\\": 0.75, \\"missing_features\\": [\\"API documentation\\"], \\"outdated_content\\": [\\"Installation guide\\"], \\"detail_gaps\\": [\\"Error handling\\"], \\"priority_recommendations\\": [\\"Update API docs\\"], \\"user_scenario_gaps\\": [\\"Advanced usage\\"]}"}]}'
        
        mock_client.invoke_model.return_value = {
            'body': mock_response_body
        }
        
        existing_content = "Basic documentation about the system"
        system_analysis = {
            'capabilities': ['webhook processing', 'documentation generation'],
            'recent_changes': ['feature addition', 'bug fixes']
        }
        
        # Call the function
        result = analyze_content_gaps(
            existing_content=existing_content,
            system_analysis=system_analysis
        )
        
        # Assertions
        self.assertEqual(result['status'], 'success')
        self.assertIn('content', result)
        self.assertIn('json', result['content'][0])
        
        gaps_data = result['content'][0]['json']
        self.assertIn('coverage_score', gaps_data)
        self.assertIn('missing_features', gaps_data)
        self.assertIn('outdated_content', gaps_data)
        self.assertIn('priority_recommendations', gaps_data)
    
    def test_enhance_content_with_bedrock_empty_content(self):
        """Test enhancement with empty content"""
        result = enhance_content_with_bedrock(
            content="",
            context=self.test_context
        )
        
        # Should handle empty content gracefully
        self.assertIn('status', result)
    
    def test_check_documentation_consistency_insufficient_layers(self):
        """Test consistency check with insufficient content layers"""
        # Only one layer provided
        content_layers = {
            'tourist_guide': 'Only one layer of content'
        }
        
        # This should still work but might return different results
        result = check_documentation_consistency(
            content_layers=content_layers,
            focus_area='test'
        )
        
        self.assertIn('status', result)
    
    @patch('boto3.client')
    def test_bedrock_json_parsing_fallback(self, mock_boto3):
        """Test fallback when Bedrock returns invalid JSON"""
        # Setup mock with invalid JSON
        mock_client = MagicMock()
        mock_boto3.return_value = mock_client
        
        mock_response_body = MagicMock()
        mock_response_body.read.return_value = '{"content": [{"text": "Invalid JSON response"}]}'
        
        mock_client.invoke_model.return_value = {
            'body': mock_response_body
        }
        
        # Call the function
        result = enhance_content_with_bedrock(
            content=self.test_content,
            context=self.test_context
        )
        
        # Should handle invalid JSON gracefully
        self.assertEqual(result['status'], 'success')
        self.assertIn('content', result)

if __name__ == '__main__':
    unittest.main()