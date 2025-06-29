"""
Tests for Tourist Guide Agent - Fixed Version

Tests the Tourist Guide Agent functionality with proper mocking of dependencies.
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock the dependencies before importing
mock_strands = MagicMock()
mock_strands.tool = lambda func: func

mock_content_generation_tools = MagicMock()
mock_agent_context_flow = MagicMock() 
mock_bedrock_integration_tools = MagicMock()
mock_content_validation_tools = MagicMock()

# Mock the validation functions to always pass
mock_content_validation_tools.enforce_quality_standards.return_value = {
    'write_approved': True,
    'quality_score': 75.0,
    'errors': [],
    'warnings': [],
    'suggestions': []
}

mock_content_validation_tools.validate_and_improve_content.return_value = {
    'improvement_suggestions': []
}

sys.modules['strands'] = mock_strands
sys.modules['content_generation_tools'] = mock_content_generation_tools
sys.modules['agent_context_flow'] = mock_agent_context_flow
sys.modules['bedrock_integration_tools'] = mock_bedrock_integration_tools
sys.modules['content_validation_tools'] = mock_content_validation_tools

# Now import the actual modules
from coderipple.webhook_parser import CommitInfo, WebhookEvent
from coderipple.tourist_guide_agent import generate_main_readme, write_documentation_file

class TestTouristGuideAgentFixed(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment"""
        # Clean up any existing test directory
        if os.path.exists("coderipple"):
            import shutil
            shutil.rmtree("coderipple")

    def tearDown(self):
        """Clean up after tests"""
        if os.path.exists("coderipple"):
            import shutil
            shutil.rmtree("coderipple")

    def test_readme_generation_with_mocked_validation(self):
        """Test README.md generation functionality with mocked validation"""
        print("Testing README generation with mocked validation...")
        
        # Create some sample documentation first
        os.makedirs("coderipple/decisions", exist_ok=True)
        
        # Write sample discovery.md
        sample_discovery = """# Project Discovery

*This document is automatically maintained by CodeRipple Tourist Guide Agent*
*Repository: test-repo*
*Last updated: 2025-06-14 12:00:00*

---

## Overview

Welcome to our test project! This comprehensive discovery document provides detailed information about the project's features, capabilities, and usage patterns.

## Key Features

- **Feature 1**: Advanced CLI functionality for user interaction
- **Feature 2**: Comprehensive documentation generation system
- **Feature 3**: Multi-agent coordination and workflow management

## Getting Started

To begin using this project:

1. Install the required dependencies
2. Configure your environment settings
3. Run the initialization commands
4. Explore the available CLI options

## Code Examples

```bash
# Basic usage example
python run_coderipple.py --help

# Advanced configuration
python run_coderipple.py --config custom.json --verbose
```

## Common Use Cases

This project is designed for developers who need:
- Automated documentation generation
- Multi-agent system coordination
- CLI-based workflow management

For more detailed information, explore the documentation sections above.
"""
        result1 = write_documentation_file("discovery.md", sample_discovery, "create")
        self.assertEqual(result1['status'], 'success', f"Failed to create discovery.md: {result1}")
        
        # Write sample decision document
        sample_decision = """# Architecture Decisions

*This document is automatically maintained by CodeRipple Historian Agent*
*Repository: test-repo*
*Last updated: 2025-06-14 12:00:00*

---

## Overview

This document captures the key architectural decisions made during the development of our multi-agent documentation system. Each decision includes context, options considered, and rationale.

## Decision Record Format

Each architectural decision follows this structure:
- **Context**: The situation requiring a decision
- **Decision**: What was decided
- **Status**: Current status (proposed, accepted, deprecated)
- **Consequences**: Expected outcomes and trade-offs

## Active Decisions

### ADR-001: Multi-Agent Architecture Pattern

**Context**: Need to coordinate multiple specialized agents for documentation generation.

**Decision**: Implement layered agent architecture with Tourist Guide, Building Inspector, and Historian agents.

**Status**: Accepted

**Consequences**:
- **Positive**: Clear separation of concerns, specialized expertise per documentation layer
- **Negative**: Increased coordination complexity, potential for agent conflicts

### ADR-002: AWS Strands for Agent Orchestration

**Context**: Required robust framework for multi-agent communication and state management.

**Decision**: Use AWS Strands for agent coordination and conversation state management.

**Status**: Accepted

**Consequences**:
- **Positive**: Built-in state management, model-driven orchestration
- **Negative**: AWS vendor lock-in, learning curve for team

### ADR-003: Amazon Bedrock for Content Enhancement

**Context**: Need AI-powered content quality improvement and consistency checking.

**Decision**: Integrate Amazon Bedrock for content enhancement and validation.

**Status**: Accepted

**Consequences**:
- **Positive**: High-quality content generation, automated consistency checking
- **Negative**: Additional API costs, dependency on external AI service

## Deprecated Decisions

### ADR-000: Manual Documentation Updates

**Context**: Initial approach used manual documentation maintenance.

**Decision**: Team members manually update documentation after code changes.

**Status**: Deprecated (replaced by ADR-001)

**Consequences**: Led to inconsistent and outdated documentation, motivating the automated approach.

## Decision Criteria

Our architectural decisions are evaluated based on:
1. **Maintainability**: Long-term sustainability and evolution
2. **Scalability**: Ability to handle growing documentation needs
3. **Quality**: Accuracy and usefulness of generated content
4. **Developer Experience**: Ease of use and integration
5. **Cost**: Infrastructure and operational expenses

For questions about these decisions, please review the rationale or open a discussion in the repository.
"""
        result2 = write_documentation_file("decisions/architecture.md", sample_decision, "create")
        self.assertEqual(result2['status'], 'success', f"Failed to create architecture.md: {result2}")
        
        # Verify files exist
        self.assertTrue(os.path.exists("coderipple/discovery.md"), "discovery.md should exist")
        self.assertTrue(os.path.exists("coderipple/decisions/architecture.md"), "architecture.md should exist")
        
        # Generate README
        readme_result = generate_main_readme("test-repo", "https://github.com/user/test-repo")
        
        # Verify README generation
        self.assertEqual(readme_result['status'], 'success', f"README generation failed: {readme_result.get('error', 'Unknown error')}")
        
        # Test content assertions
        readme_content = readme_result['content']
        
        self.assertIn('test-repo Documentation Hub', readme_content, "README should contain repository name")
        self.assertIn('layered documentation structure', readme_content, "README should mention layered structure")
        self.assertIn('discovery.md', readme_content, "README should list discovery.md")
        self.assertIn('architecture.md', readme_content, "README should list decision docs")
        
        # Write README and verify it exists
        readme_write_result = write_documentation_file("README.md", readme_content, "create")
        self.assertEqual(readme_write_result['status'], 'success', f"README writing failed: {readme_write_result.get('error', 'Unknown error')}")
        self.assertTrue(os.path.exists("coderipple/README.md"), "README.md should be created")
        
        # Verify README content on disk
        with open("coderipple/README.md", 'r') as f:
            disk_readme_content = f.read()
        
        self.assertIn('test-repo Documentation Hub', disk_readme_content, "Written README should contain repository name")
        self.assertIn('discovery.md', disk_readme_content, "Written README should list existing docs")
        
        print("✓ README generation test passed with mocked validation")

    def test_simple_readme_generation_without_dependencies(self):
        """Test README generation using simple file operations"""
        print("Testing simple README generation...")
        
        # Create documentation files directly
        os.makedirs("coderipple/decisions", exist_ok=True)
        
        # Write discovery.md directly
        with open("coderipple/discovery.md", 'w') as f:
            f.write("# Project Discovery\n\nSample discovery content")
        
        # Write architecture.md directly  
        with open("coderipple/decisions/architecture.md", 'w') as f:
            f.write("# Architecture Decisions\n\nSample decision content")
        
        # Generate README
        readme_result = generate_main_readme("test-repo", "https://github.com/user/test-repo")
        
        # Verify README generation
        self.assertEqual(readme_result['status'], 'success')
        
        readme_content = readme_result['content']
        
        # Test the specific assertion that was failing
        self.assertIn('discovery.md', readme_content, "README should list discovery.md")
        self.assertIn('architecture.md', readme_content, "README should list architecture.md")
        
        print("✓ Simple README generation test passed")

if __name__ == "__main__":
    unittest.main()