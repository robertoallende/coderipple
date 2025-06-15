"""
Bedrock Integration Tools for Step 4D: Amazon Bedrock Integration

This module provides Strands @tool decorated functions that use Amazon Bedrock
for content enhancement, consistency checking, and dynamic example generation.
"""

import json
import boto3
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from strands import tool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ContentEnhancement:
    """Result of Bedrock content enhancement"""
    enhanced_content: str
    improvements_made: List[str]
    quality_score: float
    suggestions: List[str]


@dataclass
class ConsistencyCheck:
    """Result of cross-agent consistency checking"""
    is_consistent: bool
    conflicts: List[str]
    recommendations: List[str]
    confidence_score: float


@dataclass
class DynamicExample:
    """Dynamically generated code example"""
    code: str
    language: str
    description: str
    context: str
    complexity_level: str


@tool
def enhance_content_with_bedrock(content: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Use Amazon Bedrock to improve documentation content quality.
    
    Args:
        content: The documentation content to enhance
        context: Additional context about the content (section type, target audience, etc.)
    
    Returns:
        Dictionary with enhanced content and improvement details
    """
    try:
        # Initialize Bedrock client
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Prepare context information
        context_info = context or {}
        section_type = context_info.get('section_type', 'general')
        target_audience = context_info.get('target_audience', 'developers')
        
        # Create enhancement prompt
        prompt = f"""You are a technical documentation expert. Please enhance the following documentation content to make it more clear, engaging, and useful for {target_audience}.

Section Type: {section_type}
Target Audience: {target_audience}

Original Content:
```
{content}
```

Please:
1. Improve clarity and readability
2. Add helpful details where appropriate
3. Ensure technical accuracy
4. Make it more engaging
5. Fix any grammar or formatting issues

Respond with JSON in this format:
{{
    "enhanced_content": "improved content here",
    "improvements_made": ["list of specific improvements"],
    "quality_score": 0.85,
    "suggestions": ["additional suggestions for further improvement"]
}}"""

        # Prepare request body for Claude 3.7 Sonnet
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.3,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        content_text = response_body['content'][0]['text']
        
        # Try to parse as JSON, fallback to structured text
        try:
            result = json.loads(content_text)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            result = {
                "enhanced_content": content_text,
                "improvements_made": ["Content enhanced by Bedrock"],
                "quality_score": 0.8,
                "suggestions": ["Review enhanced content for accuracy"]
            }
        
        logger.info(f"Content enhancement completed. Quality score: {result.get('quality_score', 'N/A')}")
        return {
            "status": "success",
            "content": [{"json": result}]
        }
        
    except Exception as e:
        logger.error(f"Bedrock content enhancement failed: {str(e)}")
        return {
            "status": "error",
            "content": [{"text": f"Enhancement failed: {str(e)}. Using original content."}],
            "fallback_content": content
        }


@tool
def check_documentation_consistency(content_layers: Dict[str, str], focus_area: str = "all") -> Dict[str, Any]:
    """
    Check consistency across documentation layers using Bedrock analysis.
    
    Args:
        content_layers: Dictionary with layer names as keys and content as values
                       e.g., {"tourist_guide": "...", "building_inspector": "...", "historian": "..."}
        focus_area: Specific area to focus consistency check on ("architecture", "features", "usage", "all")
    
    Returns:
        Dictionary with consistency analysis results
    """
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Prepare layers summary for analysis
        layers_summary = ""
        for layer_name, layer_content in content_layers.items():
            layers_summary += f"\n=== {layer_name.upper()} LAYER ===\n{layer_content[:1000]}...\n"
        
        prompt = f"""You are a documentation consistency expert. Analyze the following documentation layers for consistency issues, conflicts, and opportunities for better alignment.

Focus Area: {focus_area}

Documentation Layers:
{layers_summary}

Please analyze for:
1. Conflicting information between layers
2. Missing cross-references
3. Inconsistent terminology
4. Gaps in coverage
5. Alignment with stated focus area

Respond with JSON in this format:
{{
    "is_consistent": true/false,
    "conflicts": ["list of specific conflicts found"],
    "recommendations": ["specific recommendations to improve consistency"],
    "confidence_score": 0.85,
    "layer_alignment": {{
        "tourist_guide": "assessment of this layer",
        "building_inspector": "assessment of this layer", 
        "historian": "assessment of this layer"
    }}
}}"""

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 3000,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content_text = response_body['content'][0]['text']
        
        try:
            result = json.loads(content_text)
        except json.JSONDecodeError:
            result = {
                "is_consistent": True,
                "conflicts": [],
                "recommendations": ["Review documentation manually for consistency"],
                "confidence_score": 0.5,
                "layer_alignment": {}
            }
        
        logger.info(f"Consistency check completed. Consistent: {result.get('is_consistent', 'Unknown')}")
        return {
            "status": "success",
            "content": [{"json": result}]
        }
        
    except Exception as e:
        logger.error(f"Consistency check failed: {str(e)}")
        return {
            "status": "error",
            "content": [{"text": f"Consistency check failed: {str(e)}"}]
        }


@tool
def generate_dynamic_examples(code_context: Dict[str, Any], example_type: str = "usage") -> Dict[str, Any]:
    """
    Generate dynamic code examples based on actual system capabilities using Bedrock.
    
    Args:
        code_context: Context about the code/system including:
                     - file_changes: recent file changes
                     - system_capabilities: current system features
                     - target_use_case: specific use case to demonstrate
        example_type: Type of example to generate ("usage", "integration", "api", "cli")
    
    Returns:
        Dictionary with generated examples and metadata
    """
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        # Extract context information
        file_changes = code_context.get('file_changes', [])
        capabilities = code_context.get('system_capabilities', [])
        use_case = code_context.get('target_use_case', 'general usage')
        
        # Build context summary
        context_summary = f"""
File Changes: {', '.join(file_changes[:5])}
System Capabilities: {', '.join(capabilities[:5])}
Target Use Case: {use_case}
Example Type: {example_type}
"""
        
        prompt = f"""You are a technical documentation expert specializing in code examples. Generate practical, executable code examples based on the provided system context.

Context:
{context_summary}

Please generate 2-3 code examples that:
1. Demonstrate real system capabilities
2. Are practical and executable
3. Show {example_type} patterns
4. Include helpful comments
5. Are appropriate for the target use case

Respond with JSON in this format:
{{
    "examples": [
        {{
            "code": "# Complete code example here",
            "language": "python",
            "description": "What this example demonstrates",
            "context": "When to use this pattern", 
            "complexity_level": "beginner/intermediate/advanced"
        }}
    ],
    "usage_notes": ["important notes about using these examples"],
    "prerequisites": ["what users need before running these examples"]
}}"""

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "temperature": 0.4,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content_text = response_body['content'][0]['text']
        
        try:
            result = json.loads(content_text)
        except json.JSONDecodeError:
            result = {
                "examples": [],
                "usage_notes": ["Generated examples may need review"],
                "prerequisites": ["System setup required"]
            }
        
        logger.info(f"Generated {len(result.get('examples', []))} dynamic examples")
        return {
            "status": "success", 
            "content": [{"json": result}]
        }
        
    except Exception as e:
        logger.error(f"Dynamic example generation failed: {str(e)}")
        return {
            "status": "error",
            "content": [{"text": f"Example generation failed: {str(e)}"}]
        }


@tool
def analyze_content_gaps(existing_content: str, system_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Use Bedrock to identify gaps in documentation coverage.
    
    Args:
        existing_content: Current documentation content
        system_analysis: Analysis of the actual system capabilities and changes
    
    Returns:
        Dictionary with identified gaps and recommendations
    """
    try:
        bedrock = boto3.client('bedrock-runtime', region_name='us-west-2')
        
        system_summary = json.dumps(system_analysis, indent=2)[:2000]  # Truncate for prompt size
        
        prompt = f"""You are a documentation completeness expert. Analyze the existing documentation against the actual system capabilities to identify coverage gaps.

Existing Documentation:
```
{existing_content[:2000]}
```

System Analysis:
```
{system_summary}
```

Please identify:
1. Features mentioned in system analysis but missing from docs
2. Outdated information in the documentation
3. Areas that need more detail or examples
4. User scenarios that aren't covered

Respond with JSON:
{{
    "coverage_score": 0.75,
    "missing_features": ["list of undocumented features"],
    "outdated_content": ["list of content that needs updating"],
    "detail_gaps": ["areas needing more detail"],
    "priority_recommendations": ["highest priority improvements"],
    "user_scenario_gaps": ["missing user scenarios"]
}}"""

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2500,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        response = bedrock.invoke_model(
            modelId="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
            body=json.dumps(request_body),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        content_text = response_body['content'][0]['text']
        
        try:
            result = json.loads(content_text)
        except json.JSONDecodeError:
            result = {
                "coverage_score": 0.5,
                "missing_features": [],
                "outdated_content": [],
                "detail_gaps": [],
                "priority_recommendations": ["Manual review recommended"],
                "user_scenario_gaps": []
            }
        
        logger.info(f"Content gap analysis completed. Coverage score: {result.get('coverage_score', 'N/A')}")
        return {
            "status": "success",
            "content": [{"json": result}]
        }
        
    except Exception as e:
        logger.error(f"Content gap analysis failed: {str(e)}")
        return {
            "status": "error",
            "content": [{"text": f"Gap analysis failed: {str(e)}"}]
        }