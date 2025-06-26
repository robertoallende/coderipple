"""
AWS Lambda handler for CodeRipple multi-agent documentation system.

This handler processes GitHub webhook events and orchestrates the multi-agent
documentation generation system using AWS Strands framework.
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

# Initialize configuration from environment variables
try:
    from coderipple.config import CodeRippleConfig
    config = CodeRippleConfig()
    logger.info("CodeRipple configuration loaded successfully")
except ImportError as e:
    logger.warning(f"Could not load CodeRipple config: {e}, using environment variables directly")
    config = None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda entry point for GitHub webhook processing.
    
    Args:
        event: Lambda event containing GitHub webhook payload
        context: Lambda context object with runtime information
        
    Returns:
        Dict containing HTTP response for API Gateway

    """
    start_time = time.time()
    request_id = context.aws_request_id
    
    # Structured logging for webhook event
    logger.info(json.dumps({
        'event': 'webhook_received',
        'timestamp': datetime.utcnow().isoformat(),
        'request_id': request_id,
        'memory_limit': context.memory_limit_in_mb,
        'remaining_time': context.get_remaining_time_in_millis()
    }))
    
    try:
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
        
        # Initialize Strands orchestrator
        orchestrator = initialize_strands_orchestrator()
        
        if orchestrator is None:
            # Fallback mode if Strands is not available (for testing/development)
            logger.warning("Strands orchestrator unavailable, using fallback mode")
            processing_time = time.time() - start_time
            
            return create_success_response({
                'message': 'Webhook processed in fallback mode (no agents available)',
                'request_id': request_id,
                'processing_time': processing_time,
                'mode': 'fallback'
            })
        
        # Process webhook through multi-agent system
        agent_result = process_webhook_with_agents(orchestrator, webhook_payload)
        processing_time = time.time() - start_time
        
        # Add timing information to result
        agent_result['processing_time'] = processing_time
        agent_result['request_id'] = request_id
        
        # Success logging with agent details
        logger.info(json.dumps({
            'event': 'webhook_processed_success',
            'processing_time': processing_time,
            'request_id': request_id,
            'repository': agent_result.get('repository'),
            'commits_processed': agent_result.get('commits_processed', 0),
            'agent_status': agent_result.get('status'),
            'timestamp': datetime.utcnow().isoformat()
        }))
        
        return create_success_response(agent_result)
        
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
            'X-CodeRipple-Version': '1.0.0'
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
            'X-CodeRipple-Version': '1.0.0'
        },
        'body': json.dumps({
            'error': message,
            'request_id': request_id,
            'timestamp': datetime.utcnow().isoformat()
        })
    }


def initialize_strands_orchestrator():
    """
    Initialize AWS Strands orchestrator with all agents.
    
    Creates a Strands Agent with specialist agents as tools for Lambda environment.
    """
    try:
        logger.info("🚀 Starting Strands orchestrator initialization")
        
        # Step 1: Test Strands SDK imports
        logger.info("📦 Attempting Strands SDK imports...")
        from strands.agent.agent import Agent
        from strands.agent.conversation_manager.sliding_window_conversation_manager import SlidingWindowConversationManager
        logger.info("✅ Strands SDK imports successful")
        
        # Step 2: Test CodeRipple agent imports
        logger.info("🔧 Attempting CodeRipple agent imports...")
        
        logger.info("  - Importing Tourist Guide agent...")
        from coderipple.tourist_guide_agent import (
            analyze_user_workflow_impact,
            generate_main_readme,
            bootstrap_user_documentation
        )
        logger.info("  ✅ Tourist Guide agent imports successful")
        
        logger.info("  - Importing Building Inspector agent...")
        from coderipple.building_inspector_agent import (
            analyze_system_changes,
            write_system_documentation_file,
            read_existing_system_documentation
        )
        logger.info("  ✅ Building Inspector agent imports successful")
        
        logger.info("  - Importing Historian agent...")
        from coderipple.historian_agent import (
            analyze_decision_significance,
            write_decision_documentation_file,
            read_existing_decision_documentation
        )
        logger.info("  ✅ Historian agent imports successful")
        
        logger.info("  - Importing Git analysis tool...")
        from coderipple.git_analysis_tool import analyze_git_diff
        logger.info("  ✅ Git analysis tool import successful")
        
        # Step 3: Test conversation manager creation
        logger.info("💬 Creating conversation manager...")
        conversation_manager = SlidingWindowConversationManager(
            window_size=10  # Keep recent context within Lambda memory limits
        )
        logger.info("✅ Conversation manager created successfully")
        
        # Step 4: Test agent creation
        logger.info("🤖 Creating orchestrator agent with tools...")
        orchestrator = Agent(
            tools=[
                analyze_user_workflow_impact,
                generate_main_readme,
                bootstrap_user_documentation,
                analyze_system_changes,
                write_system_documentation_file,
                read_existing_system_documentation,
                analyze_decision_significance,
                write_decision_documentation_file,
                read_existing_decision_documentation,
                analyze_git_diff
            ],
            system_prompt="""You are the CodeRipple Orchestrator Agent running in AWS Lambda.

Your role is to:
1. Process GitHub webhook events and analyze code changes
2. Apply the Layer Selection Decision Tree to determine which specialist agents to invoke:
   - Does this change how users interact? → Tourist Guide Agent
   - Does this change what the system is/does? → Building Inspector Agent  
   - Does this represent a significant decision? → Historian Agent
3. Coordinate the specialist agents using their @tool functions
4. Generate comprehensive documentation updates based on agent outputs

You have access to these specialist agents:
- tourist_guide_agent: Creates user-facing documentation (discovery, getting started, patterns)
- building_inspector_agent: Documents current system state (architecture, capabilities, interfaces)
- historian_agent: Preserves decision context (ADRs, evolution history, refactors)
- analyze_git_diff: Analyzes git changes to understand what changed and why

Process each webhook systematically and ensure all relevant agents contribute to the documentation update.""",
            conversation_manager=conversation_manager
        )
        logger.info("✅ Orchestrator agent created successfully")
        
        logger.info("🎉 Strands orchestrator initialized successfully")
        return orchestrator
        
    except ImportError as e:
        logger.error(f"❌ Import failure: {e}")
        logger.error(f"Import error type: {type(e).__name__}")
        logger.error(f"Import error args: {e.args}")
        # Add sys.path debugging
        import sys
        logger.error(f"Python sys.path: {sys.path}")
        # Try to list available packages
        try:
            import os
            lambda_packages = os.listdir('/var/task')
            logger.error(f"Available packages in /var/task: {lambda_packages}")
        except Exception as list_error:
            logger.error(f"Could not list /var/task contents: {list_error}")
        return None
    except Exception as e:
        logger.error(f"❌ Orchestrator initialization failure: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error args: {e.args}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None


def process_webhook_with_agents(orchestrator, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process webhook payload through multi-agent system using Strands orchestration.
    
    Args:
        orchestrator: Initialized Strands Agent with specialist agents
        payload: GitHub webhook payload
        
    Returns:
        Dict containing agent results and documentation updates
    """
    try:
        # Extract key information from webhook
        repo_name = payload.get('repository', {}).get('full_name', 'unknown')
        commits = payload.get('commits', [])
        
        # Format webhook data for agent processing
        webhook_summary = f"""
GitHub webhook received for repository: {repo_name}

Commits ({len(commits)}):
"""
        
        for i, commit in enumerate(commits[:3]):  # Limit to first 3 commits
            webhook_summary += f"""
Commit {i+1}:
- ID: {commit.get('id', 'unknown')[:8]}
- Message: {commit.get('message', 'No message')}
- Author: {commit.get('author', {}).get('name', 'Unknown')}
- Added: {len(commit.get('added', []))} files
- Modified: {len(commit.get('modified', []))} files  
- Removed: {len(commit.get('removed', []))} files
"""
        
        if len(commits) > 3:
            webhook_summary += f"\n... and {len(commits) - 3} more commits"
        
        webhook_summary += f"""

Please analyze these changes and coordinate the appropriate specialist agents to update documentation.
Apply the Layer Selection Decision Tree to determine which agents should be involved.
"""
        
        # Process through Strands orchestrator
        logger.info("Processing webhook through Strands orchestrator")
        result = orchestrator(webhook_summary)
        
        # Extract results from orchestrator response
        response_data = {
            'status': 'success',
            'repository': repo_name,
            'commits_processed': len(commits),
            'orchestrator_response': result.message if hasattr(result, 'message') else str(result),
            'documentation_updates': []  # Will be populated by agents
        }
        
        logger.info(f"Orchestrator processed {len(commits)} commits for {repo_name}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error processing webhook with agents: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'repository': payload.get('repository', {}).get('full_name', 'unknown')
        }