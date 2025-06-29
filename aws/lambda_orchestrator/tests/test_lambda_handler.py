#!/usr/bin/env python3
"""
Test script for Lambda handler with mock webhook payload
"""

import json
import sys
from lambda_handler import lambda_handler

# Mock Lambda context
class MockContext:
    def __init__(self):
        self.aws_request_id = "test-request-123"
        self.memory_limit_in_mb = 1024
        self.remaining_time_in_millis = lambda: 300000
        
    def get_remaining_time_in_millis(self):
        return 300000

# Mock GitHub webhook payload
mock_webhook = {
    "body": json.dumps({
        "repository": {
            "full_name": "test/repo",
            "name": "repo",
            "owner": {"login": "test"}
        },
        "commits": [{
            "id": "abc123def456",
            "message": "Add new feature",
            "author": {"name": "Test User"},
            "added": ["src/new_feature.py"],
            "modified": ["README.md"],
            "removed": []
        }],
        "action": "push"
    })
}

def test_lambda_handler():
    """Test the Lambda handler with mock data"""
    print("🧪 Testing Lambda Handler...")
    
    try:
        context = MockContext()
        result = lambda_handler(mock_webhook, context)
        
        print(f"✅ Lambda handler executed successfully")
        print(f"📊 Status Code: {result['statusCode']}")
        
        body = json.loads(result['body'])
        print(f"📝 Response: {body}")
        
        if result['statusCode'] == 200:
            print("🎉 Lambda handler test PASSED!")
            assert True
        else:
            print("❌ Lambda handler test FAILED!")
            assert False, f"Lambda handler returned status {result['statusCode']}"
            
    except Exception as e:
        print(f"❌ Lambda handler test ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_lambda_handler()
    sys.exit(0 if success else 1)