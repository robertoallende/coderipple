#!/usr/bin/env python3

import os
import sys
import shutil

sys.path.append('src')

def test_readme_generation_fixed():
    """Test README generation with skip_validation flag"""
    
    # Mock the imports to avoid dependency issues
    import types
    
    # Create mock modules
    mock_strands = types.ModuleType('strands')
    mock_strands.tool = lambda func: func
    
    mock_content_generation_tools = types.ModuleType('content_generation_tools')
    mock_agent_context_flow = types.ModuleType('agent_context_flow') 
    mock_bedrock_integration_tools = types.ModuleType('bedrock_integration_tools')
    mock_content_validation_tools = types.ModuleType('content_validation_tools')
    
    # Add to sys.modules
    sys.modules['strands'] = mock_strands
    sys.modules['content_generation_tools'] = mock_content_generation_tools
    sys.modules['agent_context_flow'] = mock_agent_context_flow
    sys.modules['bedrock_integration_tools'] = mock_bedrock_integration_tools
    sys.modules['content_validation_tools'] = mock_content_validation_tools
    
    # Now import the functions
    try:
        from tourist_guide_agent import generate_main_readme, write_documentation_file
    except Exception as e:
        print(f"Import failed: {e}")
        return False
    
    print("Testing README generation with fixed skip_validation...")
    
    # Clean up any existing test directory
    if os.path.exists("coderipple"):
        shutil.rmtree("coderipple")
    
    try:
        # Create some sample documentation first
        os.makedirs("coderipple/decisions", exist_ok=True)
        
        # Write sample discovery.md
        sample_discovery = """# Project Discovery

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: test-repo*  
*Last updated: 2025-06-14 12:00:00*

---

Welcome to our project! This is a sample discovery document.
"""
        result1 = write_documentation_file("discovery.md", sample_discovery, "create", skip_validation=True)
        print(f"Discovery write result: {result1}")
        
        # Write sample decision document
        sample_decision = """# Architecture Decisions

*This document is automatically maintained by CodeRipple Historian Agent*  
*Repository: test-repo*  
*Last updated: 2025-06-14 12:00:00*

---

This document contains our architectural decisions.
"""
        result2 = write_documentation_file("decisions/architecture.md", sample_decision, "create", skip_validation=True)
        print(f"Architecture write result: {result2}")
        
        # Check if files were created
        discovery_exists = os.path.exists("coderipple/discovery.md")
        architecture_exists = os.path.exists("coderipple/decisions/architecture.md")
        print(f"discovery.md exists: {discovery_exists}")
        print(f"architecture.md exists: {architecture_exists}")
        
        if not discovery_exists or not architecture_exists:
            print("❌ Files were not created properly")
            return False
        
        # Generate README
        readme_result = generate_main_readme("test-repo", "https://github.com/user/test-repo")
        print(f"README generation result: {readme_result['status']}")
        
        if readme_result['status'] != 'success':
            print(f"❌ README generation failed: {readme_result.get('error', 'Unknown error')}")
            return False
        
        # Check the key assertion
        readme_content = readme_result['content']
        has_discovery = 'discovery.md' in readme_content
        has_architecture = 'architecture.md' in readme_content
        has_hub_title = 'test-repo Documentation Hub' in readme_content
        has_layered = 'layered documentation structure' in readme_content
        
        print(f"README contains 'discovery.md': {has_discovery}")
        print(f"README contains 'architecture.md': {has_architecture}")
        print(f"README contains hub title: {has_hub_title}")
        print(f"README contains layered structure: {has_layered}")
        
        if has_discovery and has_architecture and has_hub_title and has_layered:
            print("✅ All assertions would pass!")
            return True
        else:
            print("❌ Some assertions would fail!")
            print("README content preview:")
            print(readme_content[:500] + "...")
            return False
        
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
        
    finally:
        # Clean up
        if os.path.exists("coderipple"):
            shutil.rmtree("coderipple")

if __name__ == "__main__":
    success = test_readme_generation_fixed()
    if success:
        print("\n🎉 Test would now pass!")
    else:
        print("\n💥 Test still fails")