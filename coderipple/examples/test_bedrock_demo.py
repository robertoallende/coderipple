#!/usr/bin/env python3
"""
Demo script to test Bedrock integration with real API calls.

This script demonstrates the Bedrock integration tools in action,
showing content enhancement, consistency checking, and example generation.

Prerequisites:
1. AWS credentials configured (aws configure or environment variables)
2. Access to Amazon Bedrock Claude 3.7 Sonnet model
3. Virtual environment activated

Run with: python test_bedrock_demo.py
"""

import sys
import os
import json
from datetime import datetime

from coderipple.bedrock_integration_tools import (
    enhance_content_with_bedrock,
    check_documentation_consistency,
    generate_dynamic_examples,
    analyze_content_gaps
)

def test_content_enhancement():
    """Test content enhancement with real Bedrock API call"""
    print("🚀 Testing Content Enhancement with Bedrock...")
    print("-" * 50)
    
    # Sample content to enhance
    test_content = """# Getting Started
    
This is basic documentation about our system. It does stuff and works with things.
You can use it to do various tasks.
"""
    
    # Context for enhancement
    context = {
        'section_type': 'getting_started',
        'target_audience': 'developers',
        'change_type': 'feature',
        'repository_context': 'CodeRipple'
    }
    
    print("Original Content:")
    print(test_content)
    print("\nEnhancing with Bedrock...")
    
    try:
        result = enhance_content_with_bedrock(content=test_content, context=context)
        
        if result.get('status') == 'success':
            enhanced_data = result.get('content', [{}])[0].get('json', {})
            
            print("\n✅ Enhancement successful!")
            print(f"Quality Score: {enhanced_data.get('quality_score', 'N/A')}")
            print(f"Improvements Made: {', '.join(enhanced_data.get('improvements_made', []))}")
            print("\nEnhanced Content:")
            print("-" * 30)
            print(enhanced_data.get('enhanced_content', 'No enhanced content'))
            
            if enhanced_data.get('suggestions'):
                print(f"\nSuggestions: {', '.join(enhanced_data.get('suggestions', []))}")
                
        else:
            print(f"❌ Enhancement failed: {result.get('content', [{}])[0].get('text', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error during enhancement: {str(e)}")
    
    print("\n" + "=" * 70 + "\n")

def test_consistency_checking():
    """Test documentation consistency checking"""
    print("🔍 Testing Documentation Consistency Checking...")
    print("-" * 50)
    
    # Sample content layers
    content_layers = {
        'tourist_guide': """# User Guide
Users can install the system with npm install and run it with npm start.
The system provides a web interface for easy interaction.""",
        
        'building_inspector': """# System Architecture  
The system is built with Node.js and Express, using a React frontend.
It connects to a PostgreSQL database for data persistence.""",
        
        'historian': """# Technical Decisions
We chose Node.js for its async capabilities and large ecosystem.
The React frontend was selected for component reusability."""
    }
    
    print("Checking consistency across layers...")
    print(f"Tourist Guide: {len(content_layers['tourist_guide'])} chars")
    print(f"Building Inspector: {len(content_layers['building_inspector'])} chars") 
    print(f"Historian: {len(content_layers['historian'])} chars")
    
    try:
        result = check_documentation_consistency(
            content_layers=content_layers,
            focus_area="technology_stack"
        )
        
        if result.get('status') == 'success':
            consistency_data = result.get('content', [{}])[0].get('json', {})
            
            print(f"\n✅ Consistency check completed!")
            print(f"Is Consistent: {consistency_data.get('is_consistent', 'Unknown')}")
            print(f"Confidence Score: {consistency_data.get('confidence_score', 'N/A')}")
            
            conflicts = consistency_data.get('conflicts', [])
            if conflicts:
                print(f"Conflicts Found: {len(conflicts)}")
                for i, conflict in enumerate(conflicts[:3], 1):
                    print(f"  {i}. {conflict}")
            else:
                print("No conflicts found")
                
            recommendations = consistency_data.get('recommendations', [])
            if recommendations:
                print(f"Recommendations: {len(recommendations)}")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {rec}")
                    
        else:
            print(f"❌ Consistency check failed: {result}")
            
    except Exception as e:
        print(f"❌ Error during consistency check: {str(e)}")
    
    print("\n" + "=" * 70 + "\n")

def test_dynamic_examples():
    """Test dynamic code example generation"""
    print("💡 Testing Dynamic Example Generation...")
    print("-" * 50)
    
    # Context for example generation
    code_context = {
        'file_changes': ['src/webhook_parser.py', 'src/tourist_guide_agent.py'],
        'system_capabilities': [
            'GitHub webhook processing',
            'Multi-agent documentation generation',
            'Automated content creation'
        ],
        'target_use_case': 'Setting up webhook integration for documentation automation'
    }
    
    print("Generating examples for context:")
    print(f"File Changes: {', '.join(code_context['file_changes'])}")
    print(f"Use Case: {code_context['target_use_case']}")
    
    try:
        result = generate_dynamic_examples(
            code_context=code_context,
            example_type="integration"
        )
        
        if result.get('status') == 'success':
            examples_data = result.get('content', [{}])[0].get('json', {})
            examples = examples_data.get('examples', [])
            
            print(f"\n✅ Generated {len(examples)} examples!")
            
            for i, example in enumerate(examples[:2], 1):  # Show first 2
                print(f"\nExample {i}: {example.get('description', 'No description')}")
                print(f"Language: {example.get('language', 'Unknown')}")
                print(f"Complexity: {example.get('complexity_level', 'Unknown')}")
                print("Code:")
                print("```" + example.get('language', ''))
                print(example.get('code', 'No code'))
                print("```")
                
            usage_notes = examples_data.get('usage_notes', [])
            if usage_notes:
                print(f"\nUsage Notes:")
                for note in usage_notes[:3]:
                    print(f"  • {note}")
                    
        else:
            print(f"❌ Example generation failed: {result}")
            
    except Exception as e:
        print(f"❌ Error during example generation: {str(e)}")
    
    print("\n" + "=" * 70 + "\n")

def test_content_gaps():
    """Test content gap analysis"""
    print("📊 Testing Content Gap Analysis...")
    print("-" * 50)
    
    existing_content = """# CodeRipple Documentation

CodeRipple is a documentation system. It uses agents to update docs.

## Features
- Webhook processing
- Documentation generation

## Installation
Run the system with Python.
"""
    
    system_analysis = {
        'capabilities': [
            'GitHub webhook processing',
            'Multi-agent documentation generation',
            'Git analysis and change detection',
            'Markdown documentation output',
            'Amazon Bedrock integration'
        ],
        'recent_changes': [
            'Added Bedrock integration',
            'Enhanced content generation',
            'Cross-agent context flow'
        ]
    }
    
    print("Analyzing content gaps...")
    print(f"Existing content: {len(existing_content)} characters")
    print(f"System capabilities: {len(system_analysis['capabilities'])} items")
    
    try:
        result = analyze_content_gaps(
            existing_content=existing_content,
            system_analysis=system_analysis
        )
        
        if result.get('status') == 'success':
            gaps_data = result.get('content', [{}])[0].get('json', {})
            
            print(f"\n✅ Gap analysis completed!")
            print(f"Coverage Score: {gaps_data.get('coverage_score', 'N/A')}")
            
            missing_features = gaps_data.get('missing_features', [])
            if missing_features:
                print(f"Missing Features ({len(missing_features)}):")
                for feature in missing_features[:5]:
                    print(f"  • {feature}")
                    
            priority_recs = gaps_data.get('priority_recommendations', [])
            if priority_recs:
                print(f"Priority Recommendations ({len(priority_recs)}):")
                for rec in priority_recs[:3]:
                    print(f"  • {rec}")
                    
        else:
            print(f"❌ Gap analysis failed: {result}")
            
    except Exception as e:
        print(f"❌ Error during gap analysis: {str(e)}")
    
    print("\n" + "=" * 70 + "\n")

def main():
    """Run all Bedrock integration tests"""
    print("🤖 CodeRipple Bedrock Integration Demo")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    # Check if AWS credentials are available
    try:
        import boto3
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        print("✅ AWS credentials found and Bedrock client initialized")
        print()
    except Exception as e:
        print(f"⚠️  Warning: AWS credentials issue: {str(e)}")
        print("   Make sure you have AWS credentials configured")
        print("   Run: aws configure")
        print()
    
    # Run all tests
    test_content_enhancement()
    test_consistency_checking()  
    test_dynamic_examples()
    test_content_gaps()
    
    print("🎉 Demo completed!")
    print("\nNext steps:")
    print("1. Review the enhanced content quality")
    print("2. Check consistency recommendations") 
    print("3. Use generated examples in your documentation")
    print("4. Address identified content gaps")

if __name__ == "__main__":
    main()