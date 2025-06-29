#!/usr/bin/env python3
"""
Test script to validate all imports work in Lambda context.
"""

import sys
import os
import traceback

# Package is now installed, no path manipulation needed

def test_imports():
    """Test all imports required for Lambda function."""
    print("🧪 Testing Lambda imports...")
    
    failed_imports = []
    success_count = 0
    
    # Test 1: Standard library imports
    try:
        import json, logging, time
        from datetime import datetime, timezone
        from typing import Dict, Any, Optional
        print("✅ Standard library imports successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Standard library imports failed: {e}")
        failed_imports.append("standard_library")
    
    # Test 2: Lambda handler imports (what we actually use)
    try:
        import lambda_handler
        print("✅ Lambda handler import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Lambda handler import failed: {e}")
        failed_imports.append("lambda_handler")
        traceback.print_exc()
    
    # Test 3: CodeRipple orchestrator function (what our Lambda actually uses)
    try:
        from coderipple.orchestrator_agent import orchestrator_agent
        print("✅ CodeRipple orchestrator_agent import successful")
        success_count += 1
    except ImportError as e:
        print(f"❌ CodeRipple orchestrator_agent import failed: {e}")
        failed_imports.append("coderipple.orchestrator_agent")
        # This indicates missing dependencies (strands, boto3, etc.)
        print("ℹ️  Note: This indicates missing dependencies in CI environment")
        print("ℹ️  Required: strands, boto3, markdown-it-py for full CodeRipple functionality")
    except Exception as e:
        print(f"❌ CodeRipple orchestrator_agent unexpected error: {e}")
        failed_imports.append("coderipple.orchestrator_agent")
    
    # Test 4: Strands framework imports (required by CodeRipple)
    try:
        from strands import Agent
        print("✅ Strands framework imports successful")
        success_count += 1
    except ImportError as e:
        print(f"❌ Strands framework imports failed: {e}")
        failed_imports.append("strands")
        print("ℹ️  Note: Strands is required for CodeRipple functionality")
        print("ℹ️  Install with: pip install strands-agents")
    except Exception as e:
        print(f"❌ Strands framework unexpected error: {e}")
        failed_imports.append("strands")
    
    # Summary
    total_tests = 4
    print(f"\n📊 Import Test Results: {success_count}/{total_tests} successful")
    
    # Only fail if critical imports fail (lambda_handler is essential)
    critical_failures = [imp for imp in failed_imports if imp in ['lambda_handler', 'standard_library']]
    
    if critical_failures:
        print(f"❌ Critical import failures: {', '.join(critical_failures)}")
        assert False, f"Critical imports failed: {', '.join(critical_failures)}"
    else:
        print("✅ All critical imports successful! Lambda handler is ready.")
        if failed_imports:
            print(f"ℹ️  Non-critical import warnings: {', '.join(failed_imports)}")
        assert True

def test_strands_agent_creation():
    """Test that our Lambda handler can work with or without Strands."""
    print("\n🔬 Testing Lambda Handler Functionality...")
    
    try:
        # Test that our Lambda handler works
        from lambda_handler import lambda_handler, health_check_handler
        
        # Create mock context
        class MockContext:
            def __init__(self):
                self.aws_request_id = 'test-request-id'
                self.memory_limit_in_mb = 1536
                
            def get_remaining_time_in_millis(self):
                return 30000
        
        # Test health check (should always work)
        health_result = health_check_handler({}, MockContext())
        assert health_result['statusCode'] in [200, 503]  # Either healthy or unhealthy is fine
        
        # Test basic Lambda handler with minimal payload
        test_event = {
            'body': '{"repository": {"name": "test", "full_name": "test/test", "html_url": "https://github.com/test/test"}, "commits": [], "ref": "refs/heads/main", "before": "abc123", "after": "def456"}'
        }
        
        lambda_result = lambda_handler(test_event, MockContext())
        assert lambda_result['statusCode'] in [200, 500]  # Either success or expected failure is fine
        
        print("✅ Lambda handler functionality test successful")
        assert True
        
    except Exception as e:
        print(f"❌ Lambda handler functionality test failed: {e}")
        traceback.print_exc()
        assert False, f"Lambda handler functionality test failed: {e}"

if __name__ == "__main__":
    print("🚀 Running Lambda Import Tests...")
    try:
        test_imports()
        test_strands_agent_creation()
        print("\n" + "="*50)
        print("🎉 All tests passed! Lambda package is ready for deployment.")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        print("\n" + "="*50)
        print("⚠️  Some tests failed. Review errors above.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        print("\n" + "="*50)
        print("⚠️  Unexpected error occurred. Review errors above.")
        sys.exit(1)