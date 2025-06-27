#!/usr/bin/env python3
"""
CodeRipple Single Lambda Handler (Layer-based)

Same functionality as current local setup, but uses layers for dependencies.
All agents run in this single function as they do locally.
"""

import json
import logging
import traceback
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    CodeRipple Single Lambda Handler (Layer-based)
    
    Same functionality as current local setup, but uses layers for dependencies.
    All agents run in this single function as they do locally.
    """
    
    try:
        # Import from layers (same imports as current local setup)
        from coderipple.orchestrator_agent import process_webhook
        from coderipple.webhook_parser import WebhookEvent
        from coderipple.config import get_config
        
        logger.info("CodeRipple started (layer-based, single function)")
        logger.info(f"Event type: {event.get('httpMethod', 'unknown')}")
        
        # Parse webhook event (same as current)
        if 'body' in event:
            # API Gateway event
            webhook_data = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
        else:
            # Direct invocation
            webhook_data = event
        
        # Create webhook event object (same as current)
        webhook_event = WebhookEvent(webhook_data)
        logger.info(f"Processing webhook for repository: {webhook_event.repository_name}")
        
        # Process webhook through orchestrator (SAME LOGIC AS CURRENT LOCAL SETUP)
        result = process_webhook(webhook_event, context)
        
        # Return API Gateway compatible response (same as current)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Webhook processed successfully',
                'repository': webhook_event.repository_name,
                'agents_invoked': result.get('agents_invoked', []),
                'documentation_updated': result.get('documentation_updated', False),
                'processing_time': result.get('processing_time', 0),
                'ai_powered': True,
                'architecture': 'single-lambda-with-layers'
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Return error response (same as current)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Webhook processing failed',
                'error': str(e),
                'mode': 'error'
            })
        }

def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Health check endpoint for monitoring"""
    
    try:
        # Test layer imports (same packages as current local setup)
        from coderipple import __version__
        import boto3
        import strands_agents
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'status': 'healthy',
                'coderipple_version': __version__,
                'boto3_version': boto3.__version__,
                'strands_version': strands_agents.__version__,
                'layers_functional': True,
                'architecture': 'single-lambda-with-layers'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'layers_functional': False
            })
        }

if __name__ == "__main__":
    # Local testing
    test_event = {
        'repository': {'name': 'test-repo', 'full_name': 'user/test-repo'},
        'commits': [{'id': 'test123', 'message': 'test commit'}]
    }
    
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request-id'
            self.remaining_time_in_millis = lambda: 30000
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
