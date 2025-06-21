#!/usr/bin/env python3

import os
import sys
import glob
import shutil

def write_simple_file(file_path, content):
    """Simple file writer without validation"""
    # Ensure coderipple directory exists
    coderipple_dir = "coderipple"
    if not os.path.exists(coderipple_dir):
        os.makedirs(coderipple_dir)
    
    full_path = os.path.join(coderipple_dir, file_path)
    
    # Ensure subdirectories exist
    dir_path = os.path.dirname(full_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path)
    
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return {'status': 'success', 'file_path': full_path}

def discover_all_documentation():
    """Discover all documentation files in coderipple directory"""
    
    coderipple_dir = "coderipple"
    if not os.path.exists(coderipple_dir):
        return {}
    
    docs = {
        'user': [],
        'system': [],
        'decisions': []
    }
    
    # User documentation (Tourist Guide files)
    user_patterns = ['discovery.md', 'getting_started.md', 'patterns.md', 'troubleshooting.md', 'advanced.md']
    for pattern in user_patterns:
        files = glob.glob(os.path.join(coderipple_dir, pattern))
        for file_path in files:
            docs['user'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'description': 'User documentation'
            })
    
    # Decision documentation (Historian files)
    decision_patterns = ['decisions/*.md', 'adrs/*.md']
    for pattern in decision_patterns:
        files = glob.glob(os.path.join(coderipple_dir, pattern))
        for file_path in files:
            docs['decisions'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'description': 'Decision documentation'
            })
    
    return docs

def generate_hub_readme_content(repository_name, repository_url, existing_docs):
    """Generate content for the main README.md hub"""
    from datetime import datetime
    
    content = f"""# {repository_name} Documentation Hub

*Auto-generated documentation hub maintained by CodeRipple Tourist Guide Agent*  
*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

---

Welcome to the {repository_name} documentation! This hub provides access to all automatically maintained documentation organized by a **layered documentation structure** - three layers that handle different depths of understanding.

## Documentation Layers

### 🎯 User Documentation (How to ENGAGE)
*Start here if you want to use or contribute to {repository_name}*

"""
    
    if existing_docs.get('user'):
        for doc in existing_docs['user']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
    else:
        content += "*No user documentation available yet*\n\n"
    
    content += """### 🏗️ System Documentation (What it IS)
*Current system architecture, capabilities, and technical specifications*

"""
    
    if existing_docs.get('system'):
        for doc in existing_docs['system']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
    else:
        content += "*No system documentation available yet*\n\n"
    
    content += """### 📚 Decision Documentation (Why it BECAME this way)
*Historical context, architectural decisions, and evolution story*

"""
    
    if existing_docs.get('decisions'):
        for doc in existing_docs['decisions']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc['description']}\n"
    else:
        content += "*No decision documentation available yet*\n\n"
    
    return content

def test_readme_generation_debug():
    """Debug the README generation functionality exactly like the test"""
    print("Testing README generation (debug version)...")
    
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
        result1 = write_simple_file("discovery.md", sample_discovery)
        print(f"✓ Wrote discovery.md: {result1}")
        
        # Write sample decision document
        sample_decision = """# Architecture Decisions

*This document is automatically maintained by CodeRipple Historian Agent*  
*Repository: test-repo*  
*Last updated: 2025-06-14 12:00:00*

---

This document contains our architectural decisions.
"""
        result2 = write_simple_file("decisions/architecture.md", sample_decision)
        print(f"✓ Wrote architecture.md: {result2}")
        
        # Verify files actually exist
        print(f"discovery.md exists: {os.path.exists('coderipple/discovery.md')}")
        print(f"architecture.md exists: {os.path.exists('coderipple/decisions/architecture.md')}")
        
        # Discover documentation (this is what generate_main_readme does internally)
        existing_docs = discover_all_documentation()
        print(f"Discovered docs: {existing_docs}")
        
        # Generate README content
        readme_content = generate_hub_readme_content("test-repo", "https://github.com/user/test-repo", existing_docs)
        
        print("=== README CONTENT ===")
        print(readme_content)
        print("=== END README CONTENT ===")
        
        # Test the assertions
        print("\n=== Testing assertions ===")
        
        test1 = 'test-repo Documentation Hub' in readme_content
        print(f"Contains 'test-repo Documentation Hub': {test1}")
        
        test2 = 'layered documentation structure' in readme_content
        print(f"Contains 'layered documentation structure': {test2}")
        
        test3 = 'discovery.md' in readme_content
        print(f"Contains 'discovery.md': {test3}")
        
        test4 = 'architecture.md' in readme_content
        print(f"Contains 'architecture.md': {test4}")
        
        if test1 and test2 and test3 and test4:
            print("✅ All assertions would pass!")
        else:
            print("❌ Some assertions would fail!")
            
        print("✓ README generation test completed")
        
    finally:
        # Clean up
        if os.path.exists("coderipple"):
            shutil.rmtree("coderipple")

if __name__ == "__main__":
    test_readme_generation_debug()