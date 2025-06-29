#!/usr/bin/env python3
"""
Simple test for README generation functionality without complex dependencies
"""

import os
import sys
import shutil
import glob
from datetime import datetime

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
    
    # System documentation (Building Inspector files)
    system_patterns = ['system/*.md', 'architecture.md', 'capabilities.md']
    for pattern in system_patterns:
        files = glob.glob(os.path.join(coderipple_dir, pattern))
        for file_path in files:
            docs['system'].append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'description': 'System documentation'
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

def generate_main_readme_simple(repository_name, repository_url):
    """Simple version of generate_main_readme without validation"""
    try:
        # Discover all existing documentation
        existing_docs = discover_all_documentation()
        
        # Generate comprehensive README content
        readme_content = generate_hub_readme_content(repository_name, repository_url, existing_docs)
        
        return {
            'status': 'success',
            'content': readme_content,
            'docs_discovered': sum(len(docs) for docs in existing_docs.values()),
            'sections': list(existing_docs.keys())
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e),
            'content': ''
        }

def test_readme_generation():
    """Test README.md generation functionality"""
    print("Testing README generation (simple version)...")
    
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
        with open("coderipple/discovery.md", 'w') as f:
            f.write(sample_discovery)
        
        # Write sample decision document
        sample_decision = """# Architecture Decisions

*This document is automatically maintained by CodeRipple Historian Agent*  
*Repository: test-repo*  
*Last updated: 2025-06-14 12:00:00*

---

This document contains our architectural decisions.
"""
        with open("coderipple/decisions/architecture.md", 'w') as f:
            f.write(sample_decision)
        
        # Generate README
        readme_result = generate_main_readme_simple("test-repo", "https://github.com/user/test-repo")
        
        # Verify README generation
        assert readme_result['status'] == 'success', f"README generation failed: {readme_result.get('error', 'Unknown error')}"
        assert 'test-repo Documentation Hub' in readme_result['content'], "README should contain repository name"
        assert 'layered documentation structure' in readme_result['content'], "README should mention layered structure"
        assert 'discovery.md' in readme_result['content'], "README should list discovery.md"
        assert 'architecture.md' in readme_result['content'], "README should list decision docs"
        
        # Write README and verify it exists
        with open("coderipple/README.md", 'w') as f:
            f.write(readme_result['content'])
        
        assert os.path.exists("coderipple/README.md"), "README.md should be created"
        
        # Verify README content on disk
        with open("coderipple/README.md", 'r') as f:
            readme_content = f.read()
        
        assert 'test-repo Documentation Hub' in readme_content, "Written README should contain repository name"
        assert 'discovery.md' in readme_content, "Written README should list existing docs"
        
        print("✅ README generation test passed")
        
    finally:
        # Clean up
        if os.path.exists("coderipple"):
            shutil.rmtree("coderipple")

if __name__ == "__main__":
    test_readme_generation()