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
        from datetime import datetime
        from typing import Dict, Any, Optional
        print("✅ Standard library imports successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Standard library imports failed: {e}")
        failed_imports.append("standard_library")
    
    # Test 2: Strands framework imports
    try:
        from strands import Agent
        from strands.agent.conversation_manager import SlidingWindowConversationManager
        print("✅ Strands framework imports successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Strands framework imports failed: {e}")
        failed_imports.append("strands")
        traceback.print_exc()
    
    # Test 3: CodeRipple configuration
    try:
        from config import CodeRippleConfig
        config = CodeRippleConfig()
        print("✅ CodeRipple configuration imports successful")
        success_count += 1
    except Exception as e:
        print(f"❌ CodeRipple configuration imports failed: {e}")
        failed_imports.append("config")
        traceback.print_exc()
    
    # Test 4: Tourist Guide Agent
    try:
        from tourist_guide_agent import tourist_guide_agent
        print("✅ Tourist Guide Agent import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Tourist Guide Agent import failed: {e}")
        failed_imports.append("tourist_guide_agent")
        traceback.print_exc()
    
    # Test 5: Building Inspector Agent
    try:
        from building_inspector_agent import building_inspector_agent
        print("✅ Building Inspector Agent import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Building Inspector Agent import failed: {e}")
        failed_imports.append("building_inspector_agent")
        traceback.print_exc()
    
    # Test 6: Historian Agent
    try:
        from historian_agent import historian_agent
        print("✅ Historian Agent import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Historian Agent import failed: {e}")
        failed_imports.append("historian_agent")
        traceback.print_exc()
    
    # Test 7: Git Analysis Tool
    try:
        from git_analysis_tool import analyze_git_diff
        print("✅ Git Analysis Tool import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Git Analysis Tool import failed: {e}")
        failed_imports.append("git_analysis_tool")
        traceback.print_exc()
    
    # Test 8: Lambda handler imports
    try:
        import lambda_handler
        print("✅ Lambda handler import successful")
        success_count += 1
    except Exception as e:
        print(f"❌ Lambda handler import failed: {e}")
        failed_imports.append("lambda_handler")
        traceback.print_exc()
    
    # Summary
    total_tests = 8
    print(f"\n📊 Import Test Results: {success_count}/{total_tests} successful")
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
        return False
    else:
        print("🎉 All imports successful! Lambda package is ready.")
        return True

def test_strands_agent_creation():
    """Test that Strands agent can be created with all tools."""
    print("\n🔬 Testing Strands Agent Creation...")
    
    try:
        from strands import Agent
        from strands.agent.conversation_manager import SlidingWindowConversationManager
        from tourist_guide_agent import tourist_guide_agent
        from building_inspector_agent import building_inspector_agent
        from historian_agent import historian_agent
        from git_analysis_tool import analyze_git_diff
        
        # Create conversation manager
        conversation_manager = SlidingWindowConversationManager(window_size=10)
        
        # Create agent with all tools
        orchestrator = Agent(
            tools=[
                tourist_guide_agent,
                building_inspector_agent,
                historian_agent,
                analyze_git_diff
            ],
            system_prompt="Test orchestrator",
            conversation_manager=conversation_manager
        )
        
        print("✅ Strands Agent creation successful with all tools")
        return True
        
    except Exception as e:
        print(f"❌ Strands Agent creation failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import_success = test_imports()
    agent_success = test_strands_agent_creation() if import_success else False
    
    print("\n" + "="*50)
    if import_success and agent_success:
        print("🎉 All tests passed! Lambda package is ready for deployment.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Review errors above.")
        sys.exit(1)