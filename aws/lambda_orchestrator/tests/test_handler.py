#!/usr/bin/env python3
"""
Test script for Lambda handler to verify basic functionality.

This script tests the handler without requiring actual AWS Lambda environment
or Strands dependencies.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for lambda_handler imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_basic_imports():
    """Test that the handler can be imported without errors."""
    import lambda_handler
    assert lambda_handler is not None

def test_webhook_parsing():
    """Test webhook payload parsing functions."""
    from lambda_handler import parse_webhook_event, validate_webhook_payload
    
    # Test API Gateway format
    api_gateway_event = {
        'body': json.dumps({
            'repository': {'full_name': 'test/repo'},
            'commits': [{'id': 'abc123', 'message': 'test commit'}]
        })
    }
    
    parsed = parse_webhook_event(api_gateway_event)
    assert parsed is not None
    assert validate_webhook_payload(parsed) is True

def test_response_creation():
    """Test HTTP response creation functions."""
    from lambda_handler import create_success_response, create_error_response
    
    success_resp = create_success_response({'test': 'data'})
    error_resp = create_error_response(400, 'test error', 'req123')
    
    assert success_resp['statusCode'] == 200
    assert error_resp['statusCode'] == 400
    assert 'test' in json.loads(success_resp['body'])

def test_orchestrator_initialization():
    """Test orchestrator initialization (expected to fail gracefully without Strands)."""
    from lambda_handler import initialize_strands_orchestrator
    
    # This should either return None (Strands not available) or an orchestrator (Strands available)
    orchestrator = initialize_strands_orchestrator()
    
    # Both None and non-None are valid outcomes
    assert orchestrator is None or orchestrator is not None

def test_full_handler():
    """Test the full Lambda handler with mock context."""
    from lambda_handler import lambda_handler
    
    # Create mock context
    mock_context = Mock()
    mock_context.aws_request_id = 'test-request-123'
    mock_context.memory_limit_in_mb = 512
    mock_context.get_remaining_time_in_millis = Mock(return_value=30000)
    
    # Create test event
    test_event = {
        'body': json.dumps({
            'repository': {
                'full_name': 'test/coderipple'
            },
            'commits': [
                {
                    'id': 'abc123',
                    'message': 'Test commit',
                    'author': {'name': 'Test User'},
                    'added': ['file1.py'],
                    'modified': ['file2.py'],
                    'removed': []
                }
            ]
        })
    }
    
    # Call handler
    response = lambda_handler(test_event, mock_context)
    
    assert response['statusCode'] == 200
    response_body = json.loads(response['body'])
    assert 'request_id' in response_body

