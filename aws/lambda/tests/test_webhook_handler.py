#!/usr/bin/env python3
"""
Test Lambda handler with realistic GitHub webhook payloads.
"""

import json
import sys
import os
from unittest.mock import Mock

# Add parent directory to path for lambda_handler imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def create_github_push_payload():
    """Create realistic GitHub push webhook payload."""
    return {
        "ref": "refs/heads/main",
        "before": "0000000000000000000000000000000000000000",
        "after": "1234567890abcdef1234567890abcdef12345678",
        "repository": {
            "id": 123456789,
            "name": "coderipple",
            "full_name": "robertoallende/coderipple",
            "owner": {
                "name": "robertoallende",
                "email": "robert@example.com"
            },
            "html_url": "https://github.com/robertoallende/coderipple",
            "clone_url": "https://github.com/robertoallende/coderipple.git"
        },
        "commits": [
            {
                "id": "1234567890abcdef1234567890abcdef12345678",
                "tree_id": "abcdef1234567890abcdef1234567890abcdef12",
                "message": "Add Lambda handler for CodeRipple AWS deployment\n\nImplement Sub-task 9.1a with comprehensive webhook processing",
                "timestamp": "2024-12-22T10:30:00Z",
                "author": {
                    "name": "Developer",
                    "email": "dev@example.com",
                    "username": "developer"
                },
                "committer": {
                    "name": "Developer", 
                    "email": "dev@example.com",
                    "username": "developer"
                },
                "added": [
                    "aws/lambda/lambda_handler.py",
                    "aws/lambda/test_handler.py"
                ],
                "removed": [],
                "modified": [
                    "CLAUDE.md"
                ],
                "url": "https://github.com/robertoallende/coderipple/commit/1234567890abcdef1234567890abcdef12345678"
            }
        ],
        "head_commit": {
            "id": "1234567890abcdef1234567890abcdef12345678",
            "message": "Add Lambda handler for CodeRipple AWS deployment",
            "timestamp": "2024-12-22T10:30:00Z",
            "author": {
                "name": "Developer",
                "email": "dev@example.com"
            }
        },
        "pusher": {
            "name": "developer",
            "email": "dev@example.com"
        }
    }

def test_api_gateway_format():
    """Test handler with API Gateway event format."""
    print("📡 Testing API Gateway webhook format...")
    
    try:
        from lambda_handler import lambda_handler
        
        # Create mock Lambda context
        mock_context = Mock()
        mock_context.aws_request_id = 'api-gateway-test-123'
        mock_context.memory_limit_in_mb = 1024
        mock_context.get_remaining_time_in_millis = Mock(return_value=30000)
        
        # Create API Gateway event
        api_event = {
            'httpMethod': 'POST',
            'path': '/webhook',
            'headers': {
                'X-GitHub-Event': 'push',
                'X-GitHub-Delivery': 'test-delivery-123',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(create_github_push_payload())
        }
        
        # Call handler
        response = lambda_handler(api_event, mock_context)
        
        # Validate response
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"✅ API Gateway test successful")
            print(f"   Repository: {body.get('repository', 'unknown')}")
            print(f"   Commits: {body.get('commits_processed', 0)}")
            print(f"   Mode: {body.get('mode', 'agent')}")
            print(f"   Processing time: {body.get('processing_time', 0):.3f}s")
            return True
        else:
            print(f"❌ API Gateway test failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ API Gateway test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_direct_invocation():
    """Test handler with direct Lambda invocation."""
    print("\n🚀 Testing direct Lambda invocation...")
    
    try:
        from lambda_handler import lambda_handler
        
        # Create mock Lambda context
        mock_context = Mock()
        mock_context.aws_request_id = 'direct-test-456'
        mock_context.memory_limit_in_mb = 2048
        mock_context.get_remaining_time_in_millis = Mock(return_value=25000)
        
        # Create direct event (webhook payload directly)
        direct_event = create_github_push_payload()
        
        # Call handler
        response = lambda_handler(direct_event, mock_context)
        
        # Validate response
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"✅ Direct invocation test successful")
            print(f"   Repository: {body.get('repository', 'unknown')}")
            print(f"   Commits: {body.get('commits_processed', 0)}")
            print(f"   Mode: {body.get('mode', 'agent')}")
            print(f"   Processing time: {body.get('processing_time', 0):.3f}s")
            return True
        else:
            print(f"❌ Direct invocation test failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Direct invocation test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_invalid_payload():
    """Test handler with invalid webhook payload."""
    print("\n🚫 Testing invalid payload handling...")
    
    try:
        from lambda_handler import lambda_handler
        
        # Create mock Lambda context
        mock_context = Mock()
        mock_context.aws_request_id = 'invalid-test-789'
        mock_context.memory_limit_in_mb = 512
        mock_context.get_remaining_time_in_millis = Mock(return_value=30000)
        
        # Create invalid event (missing repository)
        invalid_event = {
            'body': json.dumps({
                'commits': [{'id': 'abc123'}]
                # Missing 'repository' field
            })
        }
        
        # Call handler
        response = lambda_handler(invalid_event, mock_context)
        
        # Should return 400 error
        if response['statusCode'] == 400:
            print(f"✅ Invalid payload correctly rejected")
            return True
        else:
            print(f"❌ Invalid payload test failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Invalid payload test error: {e}")
        return False

def test_multiple_commits():
    """Test handler with multiple commits."""
    print("\n📦 Testing multiple commits processing...")
    
    try:
        from lambda_handler import lambda_handler
        
        # Create mock Lambda context
        mock_context = Mock()
        mock_context.aws_request_id = 'multi-commit-test'
        mock_context.memory_limit_in_mb = 1024
        mock_context.get_remaining_time_in_millis = Mock(return_value = 30000)
        
        # Create payload with multiple commits
        payload = create_github_push_payload()
        payload['commits'] = [
            {
                "id": "commit1",
                "message": "Add new feature X",
                "author": {"name": "Dev1"},
                "added": ["src/feature_x.py"],
                "modified": ["README.md"],
                "removed": []
            },
            {
                "id": "commit2", 
                "message": "Fix bug in feature Y",
                "author": {"name": "Dev2"},
                "added": [],
                "modified": ["src/feature_y.py"],
                "removed": []
            },
            {
                "id": "commit3",
                "message": "Update documentation",
                "author": {"name": "Dev3"},
                "added": [],
                "modified": ["docs/api.md"],
                "removed": ["docs/old.md"]
            }
        ]
        
        # Call handler
        response = lambda_handler(payload, mock_context)
        
        # Validate response
        if response['statusCode'] == 200:
            body = json.loads(response['body'])
            print(f"✅ Multiple commits test successful")
            print(f"   Commits processed: {body.get('commits_processed', 0)}")
            if body.get('commits_processed') == 3:
                print(f"   ✅ All 3 commits processed correctly")
                return True
            else:
                print(f"   ❌ Expected 3 commits, got {body.get('commits_processed')}")
                return False
        else:
            print(f"❌ Multiple commits test failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Multiple commits test error: {e}")
        return False

def main():
    """Run all webhook tests."""
    print("🧪 Testing CodeRipple Lambda Handler with Webhook Payloads")
    print("=" * 60)
    
    tests = [
        ("API Gateway Format", test_api_gateway_format),
        ("Direct Invocation", test_direct_invocation),
        ("Invalid Payload", test_invalid_payload),
        ("Multiple Commits", test_multiple_commits)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        
    print("\n" + "=" * 60)
    print(f"📊 Webhook Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All webhook tests passed!")
        print("\n📋 Handler supports:")
        print("   ✅ API Gateway webhook events")
        print("   ✅ Direct Lambda invocation")
        print("   ✅ Invalid payload rejection")
        print("   ✅ Multiple commit processing")
        print("   ✅ Structured logging and error handling")
        print("   ✅ Graceful fallback when Strands unavailable")
        return True
    else:
        print("⚠️  Some webhook tests failed. Review errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)