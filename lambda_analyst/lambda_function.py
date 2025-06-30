import json
import os
import traceback
from datetime import datetime
import boto3

# AWS clients
s3_client = boto3.client('s3')
eventbridge_client = boto3.client('events')

# Configuration
DRAWER_BUCKET = os.environ.get('DRAWER_BUCKET', 'coderipple-drawer')

def lambda_handler(event, context):
    """
    Analyst Lambda - Processes repo_ready events and performs code analysis
    Foundation implementation with EventBridge integration and task logging
    """
    
    print(f"Received event: {json.dumps(event, indent=2)}")
    
    # Generate task ID for tracking
    task_id = f"analysis_processing_{int(datetime.utcnow().timestamp())}"
    
    try:
        # Parse EventBridge event
        event_detail = event.get('detail', {})
        repository = event_detail.get('repository', {})
        repo_owner = repository.get('owner', 'unknown')
        repo_name = repository.get('name', 'unknown')
        commit_sha = repository.get('commit_sha', 'unknown')
        s3_location = event_detail.get('s3_location', '')
        
        # Send task_started event
        send_task_event('task_started', task_id, {
            'repository': {
                'owner': repo_owner,
                'name': repo_name,
                'commit_sha': commit_sha
            },
            's3_location': s3_location,
            'message': 'Analyst acknowledged analysis processing task'
        })
        
        # Process the analysis request
        process_analysis(event_detail, task_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Analysis processing initiated'})
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Send task_failed event
        try:
            event_detail = event.get('detail', {})
            repository = event_detail.get('repository', {})
            send_task_event('task_failed', task_id, {
                'repository': {
                    'owner': repository.get('owner', 'unknown'),
                    'name': repository.get('name', 'unknown'),
                    'commit_sha': repository.get('commit_sha', 'unknown')
                },
                'error': {
                    'type': type(e).__name__,
                    'message': str(e),
                    'stack_trace': traceback.format_exc()
                },
                'message': 'Analysis processing failed'
            })
        except Exception as log_error:
            print(f"Failed to send task_failed event: {str(log_error)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Analysis processing failed'})
        }

def process_analysis(event_detail, task_id):
    """Process analysis request - foundation implementation"""
    
    try:
        # Extract repository information
        repository = event_detail.get('repository', {})
        repo_owner = repository.get('owner')
        repo_name = repository.get('name')
        commit_sha = repository.get('commit_sha')
        s3_location = event_detail.get('s3_location')
        
        if not all([repo_owner, repo_name, commit_sha, s3_location]):
            raise ValueError("Missing required repository information")
        
        print(f"Processing analysis for repository: {repo_owner}/{repo_name} at {commit_sha}")
        print(f"S3 location: {s3_location}")
        
        # Test S3 connectivity - verify workingcopy exists
        workingcopy_key = f"{s3_location}/workingcopy.zip"
        test_s3_connectivity(workingcopy_key)
        
        # Foundation testing complete - send task_completed
        send_task_event('task_completed', task_id, {
            'repository': {
                'owner': repo_owner,
                'name': repo_name,
                'commit_sha': commit_sha
            },
            's3_location': s3_location,
            'message': 'Analyst foundation testing completed successfully'
        })
        
        print(f"Foundation testing completed for repository: {repo_owner}/{repo_name}")
        
    except Exception as e:
        print(f"Error in process_analysis: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Send task_failed event
        repository = event_detail.get('repository', {})
        send_task_event('task_failed', task_id, {
            'repository': {
                'owner': repository.get('owner', 'unknown'),
                'name': repository.get('name', 'unknown'),
                'commit_sha': repository.get('commit_sha', 'unknown')
            },
            'error': {
                'type': type(e).__name__,
                'message': str(e),
                'stack_trace': traceback.format_exc()
            },
            'message': 'Analysis processing failed during foundation testing'
        })
        
        # Re-raise to be handled by main lambda_handler
        raise

def test_s3_connectivity(workingcopy_key):
    """Test S3 connectivity to verify Drawer bucket access"""
    
    try:
        # Check if workingcopy exists
        response = s3_client.head_object(Bucket=DRAWER_BUCKET, Key=workingcopy_key)
        print(f"S3 connectivity verified - workingcopy found: {workingcopy_key}")
        print(f"Object size: {response.get('ContentLength', 0)} bytes")
        
    except s3_client.exceptions.NoSuchKey:
        raise ValueError(f"Workingcopy not found in S3: {workingcopy_key}")
    except Exception as e:
        raise ValueError(f"S3 connectivity test failed: {str(e)}")

def send_task_event(event_type, task_id, details):
    """Send task logging events following Component Task Logging Standard"""
    
    event_detail = {
        'task_id': task_id,
        'component': 'analyst',
        'task_type': 'analysis_processing',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        **details
    }
    
    eventbridge_client.put_events(
        Entries=[{
            'Source': 'coderipple.analyst',
            'DetailType': event_type,
            'Detail': json.dumps(event_detail)
        }]
    )
    
    print(f"Sent {event_type} event for task {task_id}")
