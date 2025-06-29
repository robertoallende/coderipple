# Unit 15: Infrastructure Troubleshooting and Resolution - Subunit: Lambda Refactor Using Official Strands Pattern

## Objective

Refactor the CodeRipple Lambda function to follow the official AWS Strands deployment pattern, eliminating OpenTelemetry compatibility issues by simplifying the architecture and removing complex layer validation and initialization procedures that cause runtime failures.

## Implementation

### Problem Analysis

**Current Architecture Issues:**
- Complex layer validation causing OpenTelemetry `StopIteration` exceptions
- Over-engineered initialization with conversation managers and multi-step validation
- Divergence from official Strands Lambda deployment patterns
- Unnecessary complexity for Lambda environment constraints

**Official Strands Pattern Analysis:**
Based on `strands/deploy_to_lambda/lambda/agent_handler.py`, the official approach is:
```python
from strands import Agent
from strands_tools import http_request

def handler(event: Dict[str, Any], _context) -> str:
    weather_agent = Agent(
        system_prompt=WEATHER_SYSTEM_PROMPT,
        tools=[http_request],
    )
    response = weather_agent(event.get('prompt'))
    return str(response)
```

**Key Characteristics:**
- **Minimal imports**: Only `strands.Agent` and tools
- **Direct instantiation**: No complex initialization or validation
- **Simple dependencies**: `strands-agents` and `strands-agents-tools` only
- **Streamlined execution**: Direct agent call with response return

### Technical Approach

Refactor the Lambda function to match the official Strands pattern:

1. **Eliminate layer validation** - Remove `validate_layer_imports()` entirely
2. **Simplify agent creation** - Direct `Agent()` instantiation like official example
3. **Streamline imports** - Minimal imports following Strands pattern
4. **Reduce complexity** - Remove conversation managers and multi-step initialization
5. **Focus on core functionality** - Process webhook through simplified agent pattern

### Code Changes

**New Simplified Lambda Function:**

```python
#!/usr/bin/env python3
"""
CodeRipple Lambda Handler (Simplified Strands Pattern)

Follows official AWS Strands deployment pattern for reliability and simplicity.
Based on strands/deploy_to_lambda/lambda/agent_handler.py
"""

import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CodeRipple system prompt for multi-agent documentation
CODERIPPLE_SYSTEM_PROMPT = """You are the CodeRipple Orchestrator Agent.

Your role is to process GitHub webhook events and coordinate documentation updates through the Three Mirror Documentation Framework:

1. **Tourist Guide Layer** (How to ENGAGE): User workflows, getting started, troubleshooting
2. **Building Inspector Layer** (What it IS): Current architecture, capabilities, interfaces  
3. **Historian Layer** (Why it BECAME): ADRs, decisions, evolution context

For each webhook:
1. Analyze the code changes using git diff analysis
2. Apply Layer Selection Decision Tree:
   - Does this change how users interact? → Tourist Guide updates
   - Does this change what the system is/does? → Building Inspector updates
   - Does this represent a significant decision? → Historian updates
3. Generate appropriate documentation updates
4. Return structured results

Process webhooks systematically and ensure comprehensive documentation coverage."""

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    CodeRipple Lambda Handler (Simplified Strands Pattern)
    
    Processes GitHub webhooks using direct Strands Agent instantiation.
    Follows official Strands deployment pattern for maximum reliability.
    """
    
    request_id = getattr(context, 'aws_request_id', 'unknown')
    logger.info(f"🚀 CodeRipple Lambda started (Request ID: {request_id})")
    
    try:
        # SIMPLIFIED PATTERN - Direct agent creation (like official Strands example)
        from strands import Agent
        from coderipple.git_analysis_tool import analyze_git_diff
        from coderipple.content_generation_tools import generate_documentation
        from coderipple.webhook_parser import parse_github_webhook
        
        logger.info("📦 Creating CodeRipple agent using Strands pattern")
        
        # Create agent directly (following official Strands pattern)
        coderipple_agent = Agent(
            system_prompt=CODERIPPLE_SYSTEM_PROMPT,
            tools=[
                analyze_git_diff,
                generate_documentation,
                parse_github_webhook
            ]
        )
        
        logger.info("📥 Processing webhook event")
        
        # Parse webhook payload
        if 'body' in event:
            # API Gateway event
            webhook_data = event['body']
            if isinstance(webhook_data, str):
                webhook_data = json.loads(webhook_data)
        else:
            # Direct invocation
            webhook_data = event
        
        # Extract key information for agent processing
        repository = webhook_data.get('repository', {}).get('full_name', 'unknown')
        commits = webhook_data.get('commits', [])
        
        # Create agent prompt from webhook data
        agent_prompt = f"""
GitHub webhook received for repository: {repository}

Webhook data:
{json.dumps(webhook_data, indent=2)}

Please process this webhook and coordinate appropriate documentation updates according to the Three Mirror Documentation Framework.
"""
        
        logger.info(f"📂 Repository: {repository}")
        logger.info(f"📝 Commits: {len(commits)}")
        
        # Process through agent (following official Strands pattern)
        logger.info("🤖 Processing webhook through CodeRipple agent")
        response = coderipple_agent(agent_prompt)
        
        logger.info("✅ Webhook processed successfully")
        
        # Return API Gateway compatible response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-CodeRipple-Pattern': 'simplified-strands',
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'repository': repository,
                'commits_processed': len(commits),
                'agent_response': str(response),
                'request_id': request_id,
                'pattern': 'simplified-strands'
            })
        }
        
    except Exception as e:
        logger.error(f"💥 Error processing webhook: {e}")
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-CodeRipple-Pattern': 'simplified-strands',
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'message': 'Webhook processing failed',
                'error': str(e),
                'request_id': request_id,
                'pattern': 'simplified-strands'
            })
        }

def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Simple health check following Strands pattern"""
    
    try:
        # Test basic Strands import
        from strands import Agent
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'pattern': 'simplified-strands',
                'strands_available': True
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'pattern': 'simplified-strands'
            })
        }

if __name__ == "__main__":
    # Local testing (following Strands example pattern)
    print("🧪 Testing CodeRipple Lambda (Simplified Strands Pattern)")
    
    test_event = {
        'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'},
        'commits': [{'id': 'test123', 'message': 'test commit', 'modified': ['README.md']}],
        'ref': 'refs/heads/main'
    }
    
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id-12345'
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
```

**Simplified Requirements (matching Strands pattern):**
```
strands-agents
strands-agents-tools
```

### Key Simplifications

#### **Removed Complex Components:**
1. **Layer validation** - Eliminated `validate_layer_imports()` completely
2. **Conversation managers** - No `SlidingWindowConversationManager`
3. **Complex initialization** - No multi-step agent setup
4. **Specialist agent imports** - Simplified to core tools only
5. **Environment variable complexity** - Minimal configuration

#### **Adopted Strands Patterns:**
1. **Direct Agent instantiation** - `Agent(system_prompt, tools)`
2. **Simple tool imports** - Only essential CodeRipple tools
3. **Minimal dependencies** - Follow official Strands requirements
4. **Streamlined execution** - Direct agent call with response
5. **Standard error handling** - Simple try/catch pattern

#### **Preserved Core Functionality:**
1. **GitHub webhook processing** - Parse and process webhook data
2. **Documentation coordination** - Multi-agent logic via system prompt
3. **API Gateway compatibility** - Standard HTTP response format
4. **Logging and monitoring** - Essential logging for debugging
5. **Error handling** - Robust error responses

## AI Interactions

**Context:** Analysis of official Strands Lambda deployment example revealed significant architectural differences from our complex implementation.

**Key Discovery:** Official Strands pattern uses direct `Agent()` instantiation with minimal dependencies, avoiding complex initialization that triggers OpenTelemetry issues.

**Strategic Decision:** Refactor to match proven Strands pattern rather than working around complex initialization issues with exception handling.

**Benefits of Simplified Approach:**
- Eliminates OpenTelemetry compatibility issues at source
- Follows officially supported deployment pattern
- Reduces Lambda cold start time and memory usage
- Simplifies debugging and maintenance
- Aligns with Strands best practices

## Files Modified

- `functions/orchestrator/lambda_function.py` - Complete refactor to simplified pattern
- `functions/orchestrator/requirements.txt` - Simplified dependencies

## Status: Ready for Implementation

**Implementation Steps:**
1. **Backup current complex implementation**
2. **Replace with simplified Strands pattern code**
3. **Update requirements.txt to match Strands example**
4. **Test locally with simplified pattern**
5. **Deploy and validate webhook functionality**
6. **Monitor for OpenTelemetry issues (should be eliminated)**

**Success Criteria:**
- Lambda function initializes without OpenTelemetry errors
- Webhook processing completes successfully
- Agent responses provide documentation coordination
- No layer validation or complex initialization errors
- Performance improved with simplified architecture

**Migration Strategy:**
- **Phase 1**: Deploy simplified version alongside current version
- **Phase 2**: A/B test both implementations
- **Phase 3**: Switch traffic to simplified version if successful
- **Phase 4**: Remove complex implementation after validation

**Long-term Benefits:**
- **Maintainability**: Simpler codebase following official patterns
- **Reliability**: Fewer failure points and dependencies
- **Performance**: Faster cold starts and reduced memory usage
- **Supportability**: Alignment with official Strands examples