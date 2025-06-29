#!/usr/bin/env python3
"""
Demo script showing the Lambda import error

Run this to see the exact error that Lambda encounters.
"""

import sys
import os
from unittest.mock import patch, MagicMock

# Add src to path
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
sys.path.insert(0, src_path)

print("🔍 Lambda Import Error Demonstration")
print("=" * 50)

# Mock dependencies to allow import
mock_modules = {
    'strands': MagicMock(),
    'coderipple.webhook_parser': MagicMock(),
    'coderipple.git_analysis_tool': MagicMock(),
    'coderipple.tourist_guide_agent': MagicMock(),
    'coderipple.building_inspector_agent': MagicMock(),
    'coderipple.historian_agent': MagicMock(),
    'coderipple.agent_context_flow': MagicMock(),
}

with patch.dict('sys.modules', mock_modules):
    print("\n1. Testing what's actually available:")
    import coderipple.orchestrator_agent as orch_module
    available = [attr for attr in dir(orch_module) if not attr.startswith('_')]
    print(f"   Available exports: {available}")
    
    print("\n2. Testing working import (what should be used):")
    try:
        from coderipple.orchestrator_agent import orchestrator_agent
        print("   ✅ SUCCESS: orchestrator_agent function imported")
        print(f"   Type: {type(orchestrator_agent)}")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n3. Testing Lambda's expected import (this fails):")
    try:
        from coderipple.orchestrator_agent import OrchestratorAgent
        print("   ✅ SUCCESS: OrchestratorAgent class imported")
    except ImportError as e:
        print(f"   ❌ FAILED: {e}")
        print("   📍 This is the EXACT error Lambda encounters!")
    
    print("\n4. Demonstrating the fix options:")
    
    print("\n   Option 1 - Wrapper Class:")
    class OrchestratorAgent:
        def __init__(self):
            pass
        
        def process_webhook(self, webhook_payload, event_type, github_token=None):
            return orchestrator_agent(webhook_payload, event_type, github_token)
    
    try:
        agent = OrchestratorAgent()
        print("   ✅ SUCCESS: Wrapper class works")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
    
    print("\n   Option 2 - Direct Function Use:")
    try:
        # This is what Lambda should do instead
        result = orchestrator_agent('{"test": "payload"}', 'push')
        print("   ✅ SUCCESS: Direct function call works")
    except Exception as e:
        print(f"   ❌ FAILED: {e}")

print("\n" + "=" * 50)
print("🎯 CONCLUSION:")
print("The Lambda error is NOT an OpenTelemetry issue!")
print("It's a missing OrchestratorAgent CLASS that deployment expects.")
print("The implementation only provides orchestrator_agent FUNCTION.")
