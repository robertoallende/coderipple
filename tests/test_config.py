#!/usr/bin/env python3

import os
import sys
import tempfile

# Add src to path for imports
sys.path.append('src')

def test_core_configuration():
    """Test core Step 7 configuration functionality without agent dependencies"""
    
    print("🔧 Testing Step 7: Core Configuration Management")
    print("=" * 50)
    
    # Test 1: Basic configuration loading
    print("\n1️⃣ Testing basic configuration loading...")
    
    try:
        from config import get_config, get_documentation_path, get_output_dir
        
        # Test default configuration
        config = get_config()
        print(f"✓ Source repo: {config.source_repo}")
        print(f"✓ Output dir: {config.output_dir}")
        print(f"✓ Enabled agents: {config.enabled_agents}")
        print(f"✓ Min quality score: {config.min_quality_score}")
        
        # Verify default values
        if config.output_dir == "coderipple":
            print("✅ Default output directory correct")
        else:
            print(f"❌ Expected 'coderipple', got '{config.output_dir}'")
            return False
            
        if 'tourist_guide' in config.enabled_agents:
            print("✅ Default agents enabled correctly")
        else:
            print(f"❌ Expected tourist_guide in agents, got {config.enabled_agents}")
            return False
            
    except Exception as e:
        print(f"❌ Basic configuration test failed: {e}")
        return False
    
    # Test 2: Environment variable override
    print("\n2️⃣ Testing environment variable configuration...")
    
    try:
        # Set test environment variables
        test_values = {
            'CODERIPPLE_OUTPUT_DIR': 'test_docs_output',
            'CODERIPPLE_ENABLED_AGENTS': 'tourist_guide,building_inspector',
            'CODERIPPLE_MIN_QUALITY_SCORE': '75.0',
            'CODERIPPLE_LOG_LEVEL': 'DEBUG'
        }
        
        # Store original values
        original_values = {}
        for key in test_values:
            original_values[key] = os.getenv(key)
            os.environ[key] = test_values[key]
        
        # Reload configuration
        from config import reload_config
        config = reload_config()
        
        # Verify environment variables are used
        if config.output_dir == 'test_docs_output':
            print("✓ Output directory from environment")
        else:
            print(f"❌ Expected 'test_docs_output', got '{config.output_dir}'")
            return False
            
        if config.enabled_agents == ['tourist_guide', 'building_inspector']:
            print("✓ Enabled agents from environment")
        else:
            print(f"❌ Expected ['tourist_guide', 'building_inspector'], got {config.enabled_agents}")
            return False
            
        if config.min_quality_score == 75.0:
            print("✓ Quality score from environment")
        else:
            print(f"❌ Expected 75.0, got {config.min_quality_score}")
            return False
            
        if config.log_level == 'DEBUG':
            print("✓ Log level from environment")
        else:
            print(f"❌ Expected 'DEBUG', got '{config.log_level}'")
            return False
        
        print("✅ Environment variable configuration working")
        
        # Restore original values
        for key, value in original_values.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        
    except Exception as e:
        print(f"❌ Environment configuration test failed: {e}")
        return False
    
    # Test 3: Path generation functions
    print("\n3️⃣ Testing path generation functions...")
    
    try:
        # Reset to defaults
        reload_config()
        
        # Test convenience functions
        output_dir = get_output_dir()
        doc_path = get_documentation_path("user/overview.md")
        system_path = get_documentation_path("system/architecture.md")
        decision_path = get_documentation_path("decisions/adr-001.md")
        
        print(f"✓ get_output_dir(): {output_dir}")
        print(f"✓ user doc path: {doc_path}")
        print(f"✓ system doc path: {system_path}")
        print(f"✓ decision doc path: {decision_path}")
        
        # Verify paths are correctly constructed
        expected_user = os.path.join("coderipple", "user", "overview.md")
        expected_system = os.path.join("coderipple", "system", "architecture.md")
        expected_decision = os.path.join("coderipple", "decisions", "adr-001.md")
        
        if doc_path == expected_user:
            print("✓ User documentation path correct")
        else:
            print(f"❌ Expected '{expected_user}', got '{doc_path}'")
            return False
            
        if system_path == expected_system:
            print("✓ System documentation path correct")
        else:
            print(f"❌ Expected '{expected_system}', got '{system_path}'")
            return False
            
        if decision_path == expected_decision:
            print("✓ Decision documentation path correct")
        else:
            print(f"❌ Expected '{expected_decision}', got '{decision_path}'")
            return False
        
        print("✅ Path generation functions working correctly")
        
    except Exception as e:
        print(f"❌ Path generation test failed: {e}")
        return False
    
    # Test 4: Configuration validation
    print("\n4️⃣ Testing configuration validation...")
    
    try:
        # Test with invalid quality score
        os.environ['CODERIPPLE_MIN_QUALITY_SCORE'] = '150.0'  # Invalid: > 100
        
        try:
            config = reload_config()
            print("❌ Expected validation error for quality score > 100")
            return False
        except ValueError as e:
            if "Min quality score must be between 0-100" in str(e):
                print("✓ Quality score validation working")
            else:
                print(f"❌ Unexpected validation error: {e}")
                return False
        
        # Clean up invalid environment
        os.environ.pop('CODERIPPLE_MIN_QUALITY_SCORE', None)
        
        # Test with invalid source repo
        with tempfile.TemporaryDirectory() as temp_dir:
            nonexistent_path = os.path.join(temp_dir, "nonexistent")
            os.environ['CODERIPPLE_SOURCE_REPO'] = nonexistent_path
            
            try:
                config = reload_config()
                print("❌ Expected validation error for nonexistent source repo")
                return False
            except ValueError as e:
                if "Source repository path does not exist" in str(e):
                    print("✓ Source repository validation working")
                else:
                    print(f"❌ Unexpected validation error: {e}")
                    return False
            
            # Clean up invalid environment
            os.environ.pop('CODERIPPLE_SOURCE_REPO', None)
        
        # Test valid configuration again
        config = reload_config()
        print("✓ Valid configuration loads successfully after cleanup")
        
        print("✅ Configuration validation working correctly")
        
    except Exception as e:
        print(f"❌ Configuration validation test failed: {e}")
        return False
    
    # Test 5: Agent enablement check
    print("\n5️⃣ Testing agent enablement functionality...")
    
    try:
        config = get_config()
        
        # Test agent checking
        if config.is_agent_enabled('tourist_guide'):
            print("✓ Tourist guide agent enabled by default")
        else:
            print("❌ Tourist guide agent should be enabled by default")
            return False
            
        if config.is_agent_enabled('nonexistent_agent'):
            print("❌ Nonexistent agent should not be enabled")
            return False
        else:
            print("✓ Nonexistent agent correctly disabled")
        
        # Test custom agent configuration
        os.environ['CODERIPPLE_ENABLED_AGENTS'] = 'building_inspector'
        config = reload_config()
        
        if config.is_agent_enabled('building_inspector'):
            print("✓ Custom agent enablement working")
        else:
            print("❌ Custom agent enablement failed")
            return False
            
        if not config.is_agent_enabled('tourist_guide'):
            print("✓ Disabled agents correctly excluded")
        else:
            print("❌ Disabled agents should be excluded")
            return False
        
        # Clean up
        os.environ.pop('CODERIPPLE_ENABLED_AGENTS', None)
        reload_config()
        
        print("✅ Agent enablement functionality working correctly")
        
    except Exception as e:
        print(f"❌ Agent enablement test failed: {e}")
        return False
    
    print("\n✅ All Step 7 core configuration tests passed!")
    return True


if __name__ == "__main__":
    success = test_core_configuration()
    
    if success:
        print("\\n🎉 Step 7: Core Configuration Management - ALL TESTS PASSED!")
        print("\\n📋 Summary:")
        print("  ✅ Basic configuration loading")
        print("  ✅ Environment variable override")  
        print("  ✅ Path generation functions")
        print("  ✅ Configuration validation")
        print("  ✅ Agent enablement functionality")
        print("\\n🚀 Step 7 core implementation verified!")
    else:
        print("\\n💥 Step 7 core tests failed")
        sys.exit(1)