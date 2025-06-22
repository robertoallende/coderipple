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
    try:
        import lambda_handler
        print("✅ Lambda handler imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_webhook_parsing():
    """Test webhook payload parsing functions."""
    try:
        from lambda_handler import parse_webhook_event, validate_webhook_payload
        
        # Test API Gateway format
        api_gateway_event = {
            'body': json.dumps({
                'repository': {'full_name': 'test/repo'},
                'commits': [{'id': 'abc123', 'message': 'test commit'}]
            })
        }
        
        parsed = parse_webhook_event(api_gateway_event)
        if parsed and validate_webhook_payload(parsed):
            print("✅ Webhook parsing works correctly")
            return True
        else:
            print("❌ Webhook parsing failed")
            return False
            
    except Exception as e:
        print(f"❌ Webhook parsing error: {e}")
        return False

def test_response_creation():
    """Test HTTP response creation functions."""
    try:
        from lambda_handler import create_success_response, create_error_response
        
        success_resp = create_success_response({'test': 'data'})
        error_resp = create_error_response(400, 'test error', 'req123')
        
        if (success_resp['statusCode'] == 200 and 
            error_resp['statusCode'] == 400 and
            'test' in json.loads(success_resp['body'])):
            print("✅ Response creation works correctly")
            return True
        else:
            print("❌ Response creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Response creation error: {e}")
        return False

def test_orchestrator_initialization():
    """Test orchestrator initialization (expected to fail gracefully without Strands)."""
    try:
        from lambda_handler import initialize_strands_orchestrator
        
        # This should return None because Strands is not installed
        orchestrator = initialize_strands_orchestrator()
        
        if orchestrator is None:
            print("✅ Orchestrator initialization fails gracefully (Strands not available)")
            return True
        else:
            print("✅ Orchestrator initialization successful (Strands available)")
            return True
            
    except Exception as e:
        print(f"❌ Orchestrator initialization error: {e}")
        return False

def test_full_handler():
    """Test the full Lambda handler with mock context."""
    try:
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
        
        if (response['statusCode'] == 200 and 
            'request_id' in json.loads(response['body'])):
            print("✅ Full Lambda handler test successful")
            return True
        else:
            print(f"❌ Handler returned unexpected response: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Full handler test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🧪 Testing CodeRipple Lambda Handler")
    print("=" * 50)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("Webhook Parsing", test_webhook_parsing),
        ("Response Creation", test_response_creation),
        ("Orchestrator Init", test_orchestrator_initialization),
        ("Full Handler", test_full_handler)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Lambda handler is ready for Sub-task 9.1b")
        return True
    else:
        print("⚠️  Some tests failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)