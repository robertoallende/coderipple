#!/usr/bin/env python3
"""
CodeRipple Lambda Handler (Function-Based Pattern)

Uses the working orchestrator_agent function instead of trying to create
an OrchestratorAgent class that doesn't exist.
"""

import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    CodeRipple Lambda Handler using the working orchestrator_agent function
    """
    
    request_id = getattr(context, 'aws_request_id', 'unknown')
    logger.info(f"🚀 CodeRipple Lambda started (Request ID: {request_id})")
    
    try:
        # Import the working orchestrator_agent function
        from coderipple.orchestrator_agent import orchestrator_agent
        
        logger.info("📦 orchestrator_agent function imported successfully")
        
        # Parse webhook payload
        if 'body' in event:
            # API Gateway event
            webhook_payload = event['body']
            if isinstance(webhook_payload, str):
                # Already a JSON string, use as-is
                pass
            else:
                # Convert dict to JSON string
                webhook_payload = json.dumps(webhook_payload)
        else:
            # Direct invocation - convert to JSON string
            webhook_payload = json.dumps(event)
        
        # Extract event type from headers
        event_type = 'push'  # Default
        if 'headers' in event:
            event_type = event.get('headers', {}).get('X-GitHub-Event', 'push')
        
        logger.info(f"📥 Processing webhook event type: {event_type}")
        logger.info(f"📦 Payload size: {len(webhook_payload)} bytes")
        
        # Process through orchestrator_agent function
        logger.info("🤖 Processing webhook through orchestrator_agent function")
        result = orchestrator_agent(webhook_payload, event_type)
        
        logger.info("✅ Webhook processed successfully")
        logger.info(f"📊 Result type: {type(result).__name__}")
        logger.info(f"🎯 Agent decisions: {len(result.agent_decisions)} decisions made")
        
        # Extract repository info for response
        try:
            webhook_data = json.loads(webhook_payload)
            repository = webhook_data.get('repository', {}).get('full_name', 'unknown')
            commits = webhook_data.get('commits', [])
        except:
            repository = 'unknown'
            commits = []
        
        # Return API Gateway compatible response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-CodeRipple-Pattern': 'function-based',
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'repository': repository,
                'commits_processed': len(commits),
                'agent_decisions': len(result.agent_decisions),
                'orchestration_summary': result.summary,
                'request_id': request_id,
                'pattern': 'function-based'
            })
        }
        
    except Exception as e:
        logger.error(f"💥 Error processing webhook: {e}")
        logger.error(f"📍 Traceback: {str(e)}")
        
        # Return error response
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'X-CodeRipple-Pattern': 'function-based',
                'X-Request-ID': request_id
            },
            'body': json.dumps({
                'message': 'Webhook processing failed',
                'error': str(e),
                'request_id': request_id,
                'pattern': 'function-based'
            })
        }

def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Health check using function-based pattern"""
    
    try:
        # Test orchestrator_agent import
        from coderipple.orchestrator_agent import orchestrator_agent
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'pattern': 'function-based',
                'orchestrator_agent_available': True
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'pattern': 'function-based'
            })
        }

if __name__ == "__main__":
    # Local testing
    print("🧪 Testing CodeRipple Lambda (Function-Based Pattern)")
    
    test_event = {
        'body': json.dumps({
            'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'},
            'commits': [{'id': 'test123', 'message': 'test commit', 'modified': ['README.md']}],
            'ref': 'refs/heads/main'
        }),
        'headers': {'X-GitHub-Event': 'push'}
    }
    
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id-12345'
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
