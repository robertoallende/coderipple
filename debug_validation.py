#!/usr/bin/env python3

import os
import sys
import shutil

def mock_validation_function(content, file_path, min_quality_score, project_root):
    """Mock validation that always passes"""
    return {
        'write_approved': True,
        'quality_score': 75.0,
        'errors': [],
        'warnings': [],
        'suggestions': []
    }

def write_documentation_file_debug(file_path: str, content: str, action: str = "create"):
    """
    Debug version of write_documentation_file function to see where it fails
    """
    try:
        # Ensure coderipple directory exists
        coderipple_dir = "coderipple"
        if not os.path.exists(coderipple_dir):
            os.makedirs(coderipple_dir)
        
        full_path = os.path.join(coderipple_dir, file_path)
        
        # Ensure subdirectories exist
        dir_path = os.path.dirname(full_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        
        print(f"About to validate content for {file_path}")
        
        # Mock validation (since we can't import the real validation functions)
        validation_result = mock_validation_function(
            content=content,
            file_path=full_path,
            min_quality_score=60.0,
            project_root=os.getcwd()
        )
        
        print(f"Validation result: {validation_result}")
        
        # Check if content meets quality standards
        if not validation_result['write_approved']:
            print(f"❌ Validation failed for {file_path}")
            return {
                'status': 'validation_failed',
                'error': f"Content validation failed (score: {validation_result['quality_score']:.1f})",
                'validation_errors': validation_result['errors'],
                'validation_warnings': validation_result['warnings'],
                'suggestions': validation_result['suggestions'],
                'file_path': file_path,
                'content_length': len(content)
            }
        
        print(f"✅ Content passed validation for {file_path}")
        
        # Content passed validation - proceed with writing
        if action == "create":
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "created"
            
        elif action == "append":
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write("\n\n" + content)
            operation = "appended to"
            
        elif action == "update":
            # For update, we'll overwrite the file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            operation = "updated"
        
        print(f"✅ Successfully wrote {file_path}")
        
        return {
            'status': 'success',
            'operation': operation,
            'file_path': full_path,
            'content_length': len(content),
            'validation_score': validation_result['quality_score'],
            'validation_warnings': validation_result.get('warnings', [])
        }
        
    except Exception as e:
        print(f"❌ Exception writing {file_path}: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'file_path': file_path
        }

def test_validation_issue():
    """Test if validation is causing the issue"""
    print("Testing validation issue...")
    
    # Clean up any existing test directory
    if os.path.exists("coderipple"):
        shutil.rmtree("coderipple")
    
    try:
        # Write sample discovery.md with validation
        sample_discovery = """# Project Discovery

*This document is automatically maintained by CodeRipple Tourist Guide Agent*  
*Repository: test-repo*  
*Last updated: 2025-06-14 12:00:00*

---

Welcome to our project! This is a sample discovery document.
"""
        result1 = write_documentation_file_debug("discovery.md", sample_discovery, "create")
        print(f"Discovery.md write result: {result1}")
        
        # Check if file was actually created
        discovery_exists = os.path.exists("coderipple/discovery.md")
        print(f"discovery.md actually exists: {discovery_exists}")
        
        if discovery_exists:
            with open("coderipple/discovery.md", 'r') as f:
                content = f.read()
            print(f"discovery.md content length: {len(content)}")
        
    finally:
        # Clean up
        if os.path.exists("coderipple"):
            shutil.rmtree("coderipple")

if __name__ == "__main__":
    test_validation_issue()