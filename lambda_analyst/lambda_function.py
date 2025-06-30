import json
import os
import traceback
import zipfile
import tempfile
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
    Subunit 5.2: Mock Analysis Implementation
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
            'message': 'Mock analysis processing started'
        })
        
        # Process the mock analysis
        process_mock_analysis(event_detail, task_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Mock analysis completed successfully'})
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
                'message': 'Mock analysis processing failed - no content delivered'
            })
        except Exception as log_error:
            print(f"Failed to send task_failed event: {str(log_error)}")
        
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Mock analysis processing failed'})
        }

def process_mock_analysis(event_detail, task_id):
    """Process mock analysis - Subunit 5.2 implementation"""
    
    try:
        # Extract repository information
        repository = event_detail.get('repository', {})
        repo_owner = repository.get('owner')
        repo_name = repository.get('name')
        commit_sha = repository.get('commit_sha')
        s3_location = event_detail.get('s3_location')
        
        if not all([repo_owner, repo_name, commit_sha, s3_location]):
            raise ValueError("Missing required repository information")
        
        print(f"Processing mock analysis for repository: {repo_owner}/{repo_name} at {commit_sha}")
        print(f"S3 location: {s3_location}")
        
        # Download and extract workingcopy
        workingcopy_extracted = False
        try:
            workingcopy_key = f"{s3_location}/workingcopy.zip"
            workingcopy_extracted = download_and_extract_workingcopy(workingcopy_key)
        except Exception as e:
            print(f"Warning: Failed to extract workingcopy: {str(e)}")
            # Record error in EventBridge for Hermes logging
            send_error_event('workingcopy_extraction_failed', {
                'repository': {'owner': repo_owner, 'name': repo_name, 'commit_sha': commit_sha},
                'error': str(e),
                'message': 'Workingcopy extraction failed, proceeding with basic mock analysis'
            })
        
        # Generate mock analysis (always attempt, even if extraction failed)
        analysis_content = generate_mock_analysis(repo_owner, repo_name, workingcopy_extracted)
        
        # Upload analysis results to S3
        analysis_key = f"{s3_location}/analysis/README.md"
        upload_analysis_results(analysis_key, analysis_content)
        
        # Publish analysis_ready event for Deliverer
        send_analysis_ready_event(s3_location, repo_owner, repo_name)
        
        # Send task_completed event
        send_task_event('task_completed', task_id, {
            'repository': {
                'owner': repo_owner,
                'name': repo_name,
                'commit_sha': commit_sha
            },
            's3_location': s3_location,
            'analysis_location': f"{s3_location}/analysis/",
            'workingcopy_extracted': workingcopy_extracted,
            'message': 'Mock analysis completed successfully'
        })
        
        print(f"Mock analysis completed for repository: {repo_owner}/{repo_name}")
        
    except Exception as e:
        print(f"Error in process_mock_analysis: {str(e)}")
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
            'message': 'Mock analysis failed - no content could be delivered'
        })
        
        # Re-raise to be handled by main lambda_handler
        raise

def download_and_extract_workingcopy(workingcopy_key):
    """Download and extract workingcopy.zip - return True if successful"""
    
    try:
        print(f"Downloading workingcopy: {workingcopy_key}")
        
        # Download workingcopy.zip to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            s3_client.download_fileobj(DRAWER_BUCKET, workingcopy_key, temp_file)
            temp_zip_path = temp_file.name
        
        # Test ZIP file integrity and extract
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            # Test ZIP integrity
            zip_ref.testzip()
            
            # Extract to temporary directory (for inspection if needed)
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_ref.extractall(temp_dir)
                file_count = len([f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))])
                print(f"Successfully extracted workingcopy with {file_count} files")
        
        # Clean up temporary ZIP file
        os.unlink(temp_zip_path)
        
        return True
        
    except zipfile.BadZipFile:
        print("Error: Corrupted ZIP file detected")
        raise ValueError("Workingcopy ZIP file is corrupted")
    except Exception as e:
        print(f"Error extracting workingcopy: {str(e)}")
        raise

def generate_mock_analysis(repo_owner, repo_name, workingcopy_extracted):
    """Generate mock analysis content"""
    
    # Basic mock analysis content
    content = f"# Mock Analysis Report\n\n"
    content += f"This is a mock analysis for repository **{repo_owner}/{repo_name}**\n\n"
    
    if workingcopy_extracted:
        content += "✅ Repository workingcopy successfully processed\n"
        content += "📊 Mock analysis completed with full repository access\n\n"
    else:
        content += "⚠️ Repository workingcopy extraction failed\n"
        content += "📊 Mock analysis completed with limited information\n\n"
    
    content += "## Analysis Summary\n\n"
    content += "- **Status**: Mock Analysis Complete\n"
    content += "- **Type**: Foundation Testing\n"
    content += f"- **Repository**: {repo_owner}/{repo_name}\n"
    content += f"- **Generated**: {datetime.utcnow().isoformat()}Z\n\n"
    content += "## Next Steps\n\n"
    content += "This mock analysis will be replaced with real Strands analysis in Subunit 5.5.\n"
    
    return content

def upload_analysis_results(analysis_key, content):
    """Upload analysis results to S3"""
    
    try:
        print(f"Uploading analysis results to: {analysis_key}")
        
        s3_client.put_object(
            Bucket=DRAWER_BUCKET,
            Key=analysis_key,
            Body=content.encode('utf-8'),
            ContentType='text/markdown'
        )
        
        print(f"Successfully uploaded analysis results")
        
    except Exception as e:
        print(f"Error uploading analysis results: {str(e)}")
        raise ValueError(f"Failed to upload analysis results: {str(e)}")

def send_analysis_ready_event(s3_location, repo_owner, repo_name):
    """Send analysis_ready event for Deliverer"""
    
    event_detail = {
        's3_location': s3_location,
        'repository_name': f"{repo_owner}/{repo_name}",
        'analysis_location': f"{s3_location}/analysis/",
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'component': 'analyst',
        'message': 'Mock analysis ready for delivery'
    }
    
    eventbridge_client.put_events(
        Entries=[{
            'Source': 'coderipple.system',
            'DetailType': 'analysis_ready',
            'Detail': json.dumps(event_detail)
        }]
    )
    
    print(f"Sent analysis_ready event for {repo_owner}/{repo_name}")

def send_error_event(error_type, details):
    """Send error event to EventBridge for Hermes logging"""
    
    event_detail = {
        'error_type': error_type,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'component': 'analyst',
        **details
    }
    
    eventbridge_client.put_events(
        Entries=[{
            'Source': 'coderipple.analyst',
            'DetailType': 'processing_error',
            'Detail': json.dumps(event_detail)
        }]
    )
    
    print(f"Sent error event: {error_type}")

def send_task_event(event_type, task_id, details):
    """Send task logging events following Component Task Logging Standard"""
    
    event_detail = {
        'task_id': task_id,
        'component': 'analyst',
        'task_type': 'mock_analysis_processing',
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
