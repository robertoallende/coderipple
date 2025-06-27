#!/usr/bin/env python3
"""
Test Tourist Guide Agent with Bedrock Integration

This script tests the Tourist Guide agent with real Bedrock enhancement,
showing how content gets improved through the AI integration.
"""

import sys
import os
from datetime import datetime

from coderipple.tourist_guide_agent import _enhance_updates_with_bedrock, DocumentationUpdate
from coderipple.webhook_parser import WebhookEvent, CommitInfo

def create_sample_webhook_event():
    """Create a sample webhook event for testing"""
    commit = CommitInfo(
        id="abc123def456",
        message="Add Bedrock integration for content enhancement",
        author="developer@example.com",
        timestamp="2024-01-15T10:30:00Z",
        added_files=["src/bedrock_integration_tools.py"],
        modified_files=["src/tourist_guide_agent.py", "requirements.txt"],
        removed_files=[]
    )
    
    return WebhookEvent(
        event_type="push",
        repository_name="coderipple",
        repository_url="https://github.com/user/coderipple",
        branch="main",
        commits=[commit]
    )

def test_tourist_guide_bedrock_enhancement():
    """Test the Tourist Guide agent with Bedrock enhancement"""
    
    print("🎯 Testing Tourist Guide Agent with Bedrock Integration")
    print("=" * 60)
    print()
    
    # Create sample documentation updates (before Bedrock enhancement)
    original_updates = [
        DocumentationUpdate(
            section="getting_started",
            action="update",
            content="""## Getting Started

This system helps with documentation. You can use it to make docs better.

### Setup
1. Install dependencies
2. Run the system
3. Check the output

It works with webhooks and uses AI.""",
            reason="Feature changes affect getting started",
            priority=1
        ),
        
        DocumentationUpdate(
            section="patterns",
            action="update", 
            content="""## Usage Patterns

Here are some ways to use the system:

- Set up webhooks
- Process changes
- Generate docs

The system has agents that do different things.""",
            reason="Feature changes affect usage patterns",
            priority=2
        )
    ]
    
    # Sample git analysis results
    git_analysis = {
        'change_type': 'feature',
        'affected_components': ['src/bedrock_integration_tools.py', 'src/tourist_guide_agent.py'],
        'summary': 'Added Amazon Bedrock integration for AI-powered content enhancement'
    }
    
    # Sample context
    context = {
        'repository_name': 'coderipple',
        'event_type': 'push'
    }
    
    print("Original Documentation Updates:")
    print("-" * 40)
    for i, update in enumerate(original_updates, 1):
        print(f"{i}. Section: {update.section}")
        print(f"   Priority: {update.priority}")
        print(f"   Content length: {len(update.content)} characters")
        print(f"   Preview: {update.content[:100]}...")
        print()
    
    print("🤖 Enhancing content with Bedrock...")
    print("-" * 40)
    
    try:
        # Call the Bedrock enhancement function
        enhanced_updates = _enhance_updates_with_bedrock(
            updates=original_updates,
            git_analysis=git_analysis,
            context=context
        )
        
        if enhanced_updates:
            print("✅ Enhancement completed!")
            print()
            
            print("Enhanced Documentation Updates:")
            print("-" * 40)
            
            for i, (original, enhanced) in enumerate(zip(original_updates, enhanced_updates), 1):
                print(f"{i}. Section: {enhanced.section}")
                print(f"   Original length: {len(original.content)} characters")
                print(f"   Enhanced length: {len(enhanced.content)} characters")
                
                # Check if content actually changed
                if enhanced.content != original.content:
                    print("   ✨ Content was enhanced by Bedrock!")
                    
                    # Show reason if it includes quality score
                    if "Bedrock enhanced" in enhanced.reason:
                        print(f"   Reason: {enhanced.reason}")
                        
                    # Show a preview of enhanced content
                    print(f"   Enhanced preview: {enhanced.content[:150]}...")
                    
                else:
                    print("   ℹ️  Content unchanged (may have used fallback)")
                    
                print()
        else:
            print("❌ No enhanced updates returned")
            
    except Exception as e:
        print(f"❌ Error during enhancement: {str(e)}")
        print("This might be due to:")
        print("  - AWS credentials not configured")
        print("  - No access to Bedrock model")
        print("  - Network connectivity issues")
    
    print("=" * 60)
    print("🔍 To see Bedrock in action:")
    print("1. Configure AWS credentials: aws configure")
    print("2. Request Bedrock model access in AWS Console")
    print("3. Re-run this test script")
    print()
    print("The enhancement improves:")
    print("  • Content clarity and readability")
    print("  • Technical accuracy")
    print("  • User engagement")
    print("  • Code examples and structure")

def test_bedrock_tool_directly():
    """Test the Bedrock tools directly"""
    print("\n🔧 Direct Bedrock Tool Test")
    print("-" * 30)
    
    try:
        from bedrock_integration_tools import enhance_content_with_bedrock
        
        simple_content = "This is basic documentation that needs improvement."
        context = {
            'section_type': 'user_guide',
            'target_audience': 'developers'
        }
        
        print("Testing direct Bedrock call...")
        result = enhance_content_with_bedrock(simple_content, context)
        
        if result.get('status') == 'success':
            print("✅ Direct Bedrock call successful!")
            enhanced_data = result.get('content', [{}])[0].get('json', {})
            if enhanced_data:
                print(f"Quality score: {enhanced_data.get('quality_score', 'N/A')}")
                print(f"Improvements: {enhanced_data.get('improvements_made', [])}")
        else:
            print(f"❌ Direct call failed: {result.get('content', [{}])[0].get('text', 'Unknown')}")
            
    except Exception as e:
        print(f"❌ Direct tool test error: {str(e)}")

if __name__ == "__main__":
    test_tourist_guide_bedrock_enhancement()
    test_bedrock_tool_directly()