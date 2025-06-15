#!/usr/bin/env python3

import os
import sys
import glob
sys.path.append('src')

def discover_all_documentation():
    """Debug version of _discover_all_documentation"""
    
    coderipple_dir = "coderipple"
    if not os.path.exists(coderipple_dir):
        print(f"Directory {coderipple_dir} does not exist")
        return {}
    
    print(f"Looking in {coderipple_dir}")
    
    docs = {
        'user': [],
        'system': [],
        'decisions': []
    }
    
    # User documentation (Tourist Guide files)
    user_patterns = ['discovery.md', 'getting_started.md', 'patterns.md', 'troubleshooting.md', 'advanced.md']
    print(f"Checking user patterns: {user_patterns}")
    for pattern in user_patterns:
        full_pattern = os.path.join(coderipple_dir, pattern)
        print(f"  Checking pattern: {full_pattern}")
        files = glob.glob(full_pattern)
        print(f"  Found files: {files}")
        for file_path in files:
            docs['user'].append({'path': file_path, 'name': os.path.basename(file_path)})
    
    # System documentation (Building Inspector files)
    system_patterns = ['system/*.md', 'architecture.md', 'capabilities.md']
    print(f"Checking system patterns: {system_patterns}")
    for pattern in system_patterns:
        full_pattern = os.path.join(coderipple_dir, pattern)
        print(f"  Checking pattern: {full_pattern}")
        files = glob.glob(full_pattern)
        print(f"  Found files: {files}")
        for file_path in files:
            docs['system'].append({'path': file_path, 'name': os.path.basename(file_path)})
    
    # Decision documentation (Historian files)
    decision_patterns = ['decisions/*.md', 'adrs/*.md']
    print(f"Checking decision patterns: {decision_patterns}")
    for pattern in decision_patterns:
        full_pattern = os.path.join(coderipple_dir, pattern)
        print(f"  Checking pattern: {full_pattern}")
        files = glob.glob(full_pattern)
        print(f"  Found files: {files}")
        for file_path in files:
            docs['decisions'].append({'path': file_path, 'name': os.path.basename(file_path)})
    
    return docs

def generate_hub_readme_content(repository_name, repository_url, existing_docs):
    """Debug version of _generate_hub_readme_content"""
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
            content += f"- **[{doc['name']}]({doc['path']})**: {doc.get('description', 'User documentation')}\n"
    else:
        content += "*No user documentation available yet*\n\n"
    
    content += """### 🏗️ System Documentation (What it IS)
*Current system architecture, capabilities, and technical specifications*

"""
    
    if existing_docs.get('system'):
        for doc in existing_docs['system']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc.get('description', 'System documentation')}\n"
    else:
        content += "*No system documentation available yet*\n\n"
    
    content += """### 📚 Decision Documentation (Why it BECAME this way)
*Historical context, architectural decisions, and evolution story*

"""
    
    if existing_docs.get('decisions'):
        for doc in existing_docs['decisions']:
            content += f"- **[{doc['name']}]({doc['path']})**: {doc.get('description', 'Decision documentation')}\n"
    else:
        content += "*No decision documentation available yet*\n\n"
    
    return content

def test_readme_debug():
    """Debug the README generation issue"""
    
    # Clean up any existing test directory
    if os.path.exists("coderipple"):
        import shutil
        shutil.rmtree("coderipple")
    
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
    
    print("=== Discovering documentation ===")
    existing_docs = discover_all_documentation()
    print(f"Discovered docs: {existing_docs}")
    
    print("\n=== Generating README content ===")
    readme_content = generate_hub_readme_content("test-repo", "https://github.com/user/test-repo", existing_docs)
    
    print("\n=== Generated README content ===")
    print(readme_content)
    
    print("\n=== Checking for 'discovery.md' in README ===")
    has_discovery = 'discovery.md' in readme_content
    print(f"README contains 'discovery.md': {has_discovery}")
    
    if not has_discovery:
        print("❌ Test would fail here - README doesn't contain 'discovery.md'")
    else:
        print("✅ Test would pass - README contains 'discovery.md'")
    
    # Clean up
    if os.path.exists("coderipple"):
        import shutil
        shutil.rmtree("coderipple")

if __name__ == "__main__":
    test_readme_debug()