"""
AWS Lambda handler for CodeRipple multi-agent documentation system.

This handler processes GitHub webhook events using the working orchestrator_agent function
instead of trying to create an OrchestratorAgent class that doesn't exist.
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Configure structured logging for Lambda
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda entry point for GitHub webhook processing using orchestrator_agent function.
    
    Args:
        event: Lambda event containing GitHub webhook payload
        context: Lambda context object with runtime information
        
    Returns:
        Dict containing HTTP response for API Gateway
    """
    start_time = time.time()
    request_id = getattr(context, 'aws_request_id', 'unknown')
    
    # Structured logging for webhook event
    logger.info(json.dumps({
        'event': 'webhook_received',
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': request_id,
        'memory_limit': getattr(context, 'memory_limit_in_mb', 'unknown'),
        'remaining_time': getattr(context, 'get_remaining_time_in_millis', lambda: 'unknown')()
    }))
    
    try:
        # Import the working orchestrator_agent function
        from coderipple.orchestrator_agent import orchestrator_agent
        logger.info("✅ orchestrator_agent function imported successfully")
        
        # Parse webhook payload from API Gateway
        webhook_payload = parse_webhook_event(event)
        
        # Validate webhook payload
        if not validate_webhook_payload(webhook_payload):
            return create_error_response(400, "Invalid webhook payload", request_id)
        
        # Log webhook details
        logger.info(json.dumps({
            'event': 'webhook_parsed',
            'repository': webhook_payload.get('repository', {}).get('full_name'),
            'action': webhook_payload.get('action'),
            'commits_count': len(webhook_payload.get('commits', [])),
            'request_id': request_id
        }))
        
        # Convert webhook payload to JSON string for orchestrator_agent function
        webhook_payload_str = json.dumps(webhook_payload)
        
        # Extract event type (default to 'push' if not available)
        event_type = 'push'
        if 'headers' in event:
            event_type = event.get('headers', {}).get('X-GitHub-Event', 'push')
        
        logger.info(f"🤖 Processing webhook through orchestrator_agent function (event_type: {event_type})")
        
        # Process webhook through orchestrator_agent function
        orchestration_result = orchestrator_agent(webhook_payload_str, event_type)
        
        processing_time = time.time() - start_time
        
        # Extract results from OrchestrationResult
        agent_result = {
            'status': 'success',
            'repository': webhook_payload.get('repository', {}).get('full_name'),
            'commits_processed': len(webhook_payload.get('commits', [])),
            'agent_decisions': len(orchestration_result.agent_decisions),
            'orchestration_summary': orchestration_result.summary,
            'processing_time': processing_time,
            'request_id': request_id,
            'pattern': 'function-based'
        }
        
        # Add agent decision details
        if orchestration_result.agent_decisions:
            agent_result['decisions'] = [
                {
                    'agent_type': decision.agent_type,
                    'reason': decision.reason,
                    'priority': decision.priority
                }
                for decision in orchestration_result.agent_decisions
            ]
        
        # Success logging with agent details
        logger.info(json.dumps({
            'event': 'webhook_processed_success',
            'processing_time': processing_time,
            'request_id': request_id,
            'repository': agent_result.get('repository'),
            'commits_processed': agent_result.get('commits_processed', 0),
            'agent_decisions': agent_result.get('agent_decisions', 0),
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        return create_success_response(agent_result)
        
    except ImportError as e:
        processing_time = time.time() - start_time
        
        # Import error logging (this was the original problem)
        logger.error(json.dumps({
            'event': 'import_error',
            'error': str(e),
            'error_type': type(e).__name__,
            'processing_time': processing_time,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        return create_error_response(500, f"Import error: {str(e)}", request_id)
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Error logging
        logger.error(json.dumps({
            'event': 'webhook_processing_error',
            'error': str(e),
            'error_type': type(e).__name__,
            'processing_time': processing_time,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        return create_error_response(500, f"Internal processing error: {str(e)}", request_id)


def parse_webhook_event(event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse GitHub webhook payload from API Gateway event.
    
    Args:
        event: Lambda event from API Gateway
        
    Returns:
        Parsed webhook payload or None if parsing fails
    """
    try:
        # Handle different event sources (API Gateway, direct invocation)
        if 'body' in event:
            # From API Gateway
            body = event['body']
            if isinstance(body, str):
                return json.loads(body)
            return body
        elif 'payload' in event:
            # Direct Lambda invocation for testing
            return event['payload']
        else:
            # Direct webhook payload
            return event
            
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Failed to parse webhook event: {e}")
        return None


def validate_webhook_payload(payload: Optional[Dict[str, Any]]) -> bool:
    """
    Validate that webhook payload contains required GitHub fields.
    
    Args:
        payload: Parsed webhook payload
        
    Returns:
        True if payload is valid, False otherwise
    """
    if not payload:
        return False
    
    # Check for required GitHub webhook fields
    required_fields = ['repository']
    for field in required_fields:
        if field not in payload:
            logger.warning(f"Missing required field in webhook: {field}")
            return False
    
    # Validate repository information
    repo = payload.get('repository', {})
    if not repo.get('full_name'):
        logger.warning("Missing repository full_name in webhook")
        return False
    
    return True


def create_success_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create successful HTTP response for API Gateway.
    
    Args:
        data: Response data to include in body
        
    Returns:
        API Gateway response format
    """
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'X-CodeRipple-Version': '1.0.0',
            'X-CodeRipple-Pattern': 'function-based'
        },
        'body': json.dumps(data)
    }


def create_error_response(status_code: int, message: str, request_id: str) -> Dict[str, Any]:
    """
    Create error HTTP response for API Gateway.
    
    Args:
        status_code: HTTP status code
        message: Error message
        request_id: Lambda request ID for tracking
        
    Returns:
        API Gateway error response format
    """
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'X-CodeRipple-Version': '1.0.0',
            'X-CodeRipple-Pattern': 'function-based'
        },
        'body': json.dumps({
            'error': message,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    }


def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Health check handler using function-based pattern.
    """
    try:
        # Test orchestrator_agent import
        from coderipple.orchestrator_agent import orchestrator_agent
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'healthy',
                'pattern': 'function-based',
                'orchestrator_agent_available': True,
                'timestamp': datetime.utcnow().isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 503,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'unhealthy',
                'error': str(e),
                'pattern': 'function-based',
                'timestamp': datetime.utcnow().isoformat()
            })
        }


if __name__ == "__main__":
    # Local testing
    print("🧪 Testing CodeRipple Lambda Handler (Function-Based Pattern)")
    
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
            self.memory_limit_in_mb = 1536
            
        def get_remaining_time_in_millis(self):
            return 30000
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2))
