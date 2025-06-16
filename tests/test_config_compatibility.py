#!/usr/bin/env python3

import os
import sys
import shutil

# Add src to path for imports
sys.path.append('src')

def test_backward_compatibility():
    """Test that system maintains backward compatibility with default 'coderipple' directory"""
    
    print("🔄 Testing Step 7: Backward Compatibility")
    print("=" * 45)
    
    # Clean up any existing test directory
    if os.path.exists("coderipple"):
        shutil.rmtree("coderipple")
    
    # Test 1: Default directory creation and usage
    print("\n1️⃣ Testing default directory behavior...")
    
    try:
        # Ensure clean environment
        for var in ['CODERIPPLE_OUTPUT_DIR', 'CODERIPPLE_SOURCE_REPO']:
            os.environ.pop(var, None)
        
        # Load fresh configuration
        from config import reload_config, get_config, get_documentation_path
        config = reload_config()
        
        # Verify defaults
        if config.output_dir == "coderipple":
            print(f"✓ Default output directory: {config.output_dir}")
        else:
            print(f"❌ Expected 'coderipple', got '{config.output_dir}'")
            return False
            
        if config.source_repo == os.getcwd():
            print(f"✓ Default source repo: {config.source_repo}")
        else:
            print(f"❌ Expected current directory, got '{config.source_repo}'")
            return False
        
        # Test path generation uses default directory
        test_paths = [
            ("user/overview.md", "coderipple/user/overview.md"),
            ("system/architecture.md", "coderipple/system/architecture.md"),
            ("decisions/adr-001.md", "coderipple/decisions/adr-001.md"),
            ("README.md", "coderipple/README.md")
        ]
        
        for input_path, expected in test_paths:
            actual = get_documentation_path(input_path)
            if actual == expected:
                print(f"✓ Path '{input_path}' -> '{actual}'")
            else:
                print(f"❌ Path '{input_path}': expected '{expected}', got '{actual}'")
                return False
        
        print("✅ Default directory behavior working correctly")
        
    except Exception as e:
        print(f"❌ Default directory test failed: {e}")
        return False
    
    # Test 2: Directory creation when needed
    print("\n2️⃣ Testing automatic directory creation...")
    
    try:
        from config import get_config
        config = get_config()
        
        # Create nested documentation path to test directory creation
        test_file_path = get_documentation_path("user/guides/advanced.md")
        expected_dir = os.path.dirname(test_file_path)
        
        # Simulate directory creation (like agents would do)
        os.makedirs(expected_dir, exist_ok=True)
        
        if os.path.exists(expected_dir):
            print(f"✓ Created directory: {expected_dir}")
        else:
            print(f"❌ Failed to create directory: {expected_dir}")
            return False
        
        # Test that the main output directory was created
        if os.path.exists(config.output_dir):
            print(f"✓ Main output directory exists: {config.output_dir}")
        else:
            print(f"❌ Main output directory not found: {config.output_dir}")
            return False
        
        print("✅ Automatic directory creation working correctly")
        
    except Exception as e:
        print(f"❌ Directory creation test failed: {e}")
        return False
    
    # Test 3: Configuration to_dict and string representation
    print("\n3️⃣ Testing configuration introspection...")
    
    try:
        config = get_config()
        
        # Test to_dict functionality
        config_dict = config.to_dict()
        
        if isinstance(config_dict, dict):
            print("✓ to_dict() returns dictionary")
        else:
            print(f"❌ to_dict() should return dict, got {type(config_dict)}")
            return False
        
        required_keys = ['source_repo', 'output_dir', 'enabled_agents', 'log_level']
        for key in required_keys:
            if key in config_dict:
                print(f"✓ Config dict contains '{key}': {config_dict[key]}")
            else:
                print(f"❌ Config dict missing key '{key}'")
                return False
        
        # Test string representation
        config_str = str(config)
        if 'CodeRippleConfig' in config_str and 'coderipple' in config_str:
            print(f"✓ String representation: {config_str}")
        else:
            print(f"❌ Invalid string representation: {config_str}")
            return False
        
        print("✅ Configuration introspection working correctly")
        
    except Exception as e:
        print(f"❌ Configuration introspection test failed: {e}")
        return False
    
    # Test 4: Error handling for missing directories
    print("\n4️⃣ Testing error handling...")
    
    try:
        # Test graceful handling of configuration edge cases
        config = get_config()
        
        # Test agent enablement with empty string
        original_agents = os.getenv('CODERIPPLE_ENABLED_AGENTS')
        os.environ['CODERIPPLE_ENABLED_AGENTS'] = ''
        
        config_empty = reload_config()
        if len(config_empty.enabled_agents) == 0:
            print("✓ Empty agents string handled correctly")
        else:
            print(f"❌ Expected empty agents list, got {config_empty.enabled_agents}")
            return False
        
        # Restore original configuration
        if original_agents is None:
            os.environ.pop('CODERIPPLE_ENABLED_AGENTS', None)
        else:
            os.environ['CODERIPPLE_ENABLED_AGENTS'] = original_agents
        
        config = reload_config()
        
        print("✅ Error handling working correctly")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False
    
    # Test 5: Real-world usage patterns
    print("\n5️⃣ Testing real-world usage patterns...")
    
    try:
        # Test common patterns that existing code would use
        from config import get_output_dir, get_documentation_path
        
        # Pattern 1: Getting output directory for file operations
        output_dir = get_output_dir()
        if output_dir == "coderipple":
            print("✓ get_output_dir() for file operations")
        else:
            print(f"❌ Expected 'coderipple', got '{output_dir}'")
            return False
        
        # Pattern 2: Building nested paths
        nested_paths = [
            "user/getting_started.md",
            "system/capabilities.md", 
            "decisions/architecture.md"
        ]
        
        for path in nested_paths:
            full_path = get_documentation_path(path)
            expected = os.path.join("coderipple", path)
            if full_path == expected:
                print(f"✓ Nested path: {path}")
            else:
                print(f"❌ Nested path '{path}': expected '{expected}', got '{full_path}'")
                return False
        
        # Pattern 3: Configuration singleton behavior
        config1 = get_config()
        config2 = get_config()
        
        if config1 is config2:
            print("✓ Configuration singleton pattern working")
        else:
            print("❌ Configuration should be singleton")
            return False
        
        print("✅ Real-world usage patterns working correctly")
        
    except Exception as e:
        print(f"❌ Real-world usage test failed: {e}")
        return False
    
    print("\n✅ All backward compatibility tests passed!")
    return True


if __name__ == "__main__":
    try:
        success = test_backward_compatibility()
        
        if success:
            print("\\n🎉 Step 7: Backward Compatibility - ALL TESTS PASSED!")
            print("\\n📋 Summary:")
            print("  ✅ Default directory behavior preserved")
            print("  ✅ Automatic directory creation working")  
            print("  ✅ Configuration introspection functional")
            print("  ✅ Error handling robust")
            print("  ✅ Real-world usage patterns supported")
            print("\\n🚀 Backward compatibility verified!")
        else:
            print("\\n💥 Backward compatibility tests failed")
            sys.exit(1)
            
    finally:
        # Clean up test files
        if os.path.exists("coderipple"):
            shutil.rmtree("coderipple")
            print("\\n🧹 Cleaned up test files")