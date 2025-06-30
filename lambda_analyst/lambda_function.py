import json
import os
import traceback
import zipfile
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
import boto3

# Import Magic Mirror for Strands analysis
from magic_mirror import analyze_repository

# AWS clients
s3_client = boto3.client('s3')
eventbridge_client = boto3.client('events')

# Configuration
DRAWER_BUCKET = os.environ.get('DRAWER_BUCKET', 'coderipple-drawer')

def lambda_handler(event, context):
    """
    Analyst Lambda - Processes repo_ready events and performs real Strands code analysis
    Subunit 5.5: Real Strands Integration Implementation
    """
    
    print(f"Received event: {json.dumps(event, indent=2)}")
    
    # Generate task ID for tracking
    task_id = f"strands_analysis_{int(datetime.utcnow().timestamp())}"
    
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
            'message': 'Strands analysis processing started'
        })
        
        # Process the Strands analysis
        process_strands_analysis(event_detail, task_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Strands analysis completed successfully'})
        }
        
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Send task_failed event and stop (no fallback)
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
                'message': 'Strands analysis failed - pipeline stopped'
            })
        except Exception as log_error:
            print(f"Failed to send task_failed event: {str(log_error)}")
        
        # Return error and stop pipeline
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Strands analysis failed - pipeline stopped'})
        }

def process_strands_analysis(event_detail, task_id):
    """Process real Strands analysis - Subunit 5.5 implementation"""
    
    try:
        # Extract repository information
        repository = event_detail.get('repository', {})
        repo_owner = repository.get('owner')
        repo_name = repository.get('name')
        commit_sha = repository.get('commit_sha')
        s3_location = event_detail.get('s3_location')
        
        if not all([repo_owner, repo_name, commit_sha, s3_location]):
            raise ValueError("Missing required repository information")
        
        print(f"Processing Strands analysis for repository: {repo_owner}/{repo_name} at {commit_sha}")
        print(f"S3 location: {s3_location}")
        
        # Download and extract workingcopy to temporary directory
        repo_path = download_and_extract_workingcopy(s3_location)
        
        try:
            # Run Magic Mirror Strands analysis
            print("🪞 Starting Magic Mirror analysis...")
            analysis_result = analyze_repository(repo_path, quiet=False)
            print("✅ Magic Mirror analysis completed")
            
            # Upload analysis results to S3 (rename to README.md)
            analysis_key = f"{s3_location}/analysis/README.md"
            upload_analysis_results(analysis_key, analysis_result)
            
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
                'analysis_type': 'strands_magic_mirror',
                'message': 'Strands analysis completed successfully'
            })
            
            print(f"✅ Strands analysis completed for repository: {repo_owner}/{repo_name}")
            
        finally:
            # Clean up temporary directory
            cleanup_temp_directory(repo_path)
        
    except Exception as e:
        print(f"Error in process_strands_analysis: {str(e)}")
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
            'message': 'Strands analysis failed - no fallback available'
        })
        
        # Re-raise to be handled by main lambda_handler
        raise

def download_and_extract_workingcopy(s3_location):
    """Download and extract workingcopy.zip to temporary directory for analysis"""
    
    try:
        workingcopy_key = f"{s3_location}/workingcopy.zip"
        print(f"Downloading workingcopy: {workingcopy_key}")
        
        # Create temporary directory for extraction
        temp_dir = tempfile.mkdtemp(prefix='coderipple_analysis_')
        
        # Download workingcopy.zip to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            s3_client.download_fileobj(DRAWER_BUCKET, workingcopy_key, temp_file)
            temp_zip_path = temp_file.name
        
        # Extract ZIP to temporary directory
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            # Test ZIP integrity
            zip_ref.testzip()
            
            # Extract all files
            zip_ref.extractall(temp_dir)
            
            # Count extracted files
            file_count = sum(1 for _ in Path(temp_dir).rglob('*') if _.is_file())
            print(f"Successfully extracted workingcopy with {file_count} files to {temp_dir}")
        
        # Clean up temporary ZIP file
        os.unlink(temp_zip_path)
        
        return temp_dir
        
    except zipfile.BadZipFile:
        print("Error: Corrupted ZIP file detected")
        raise ValueError("Workingcopy ZIP file is corrupted")
    except Exception as e:
        print(f"Error extracting workingcopy: {str(e)}")
        raise ValueError(f"Failed to extract workingcopy: {str(e)}")

def cleanup_temp_directory(temp_dir):
    """Clean up temporary directory after analysis"""
    
    try:
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"Cleaned up temporary directory: {temp_dir}")
    except Exception as e:
        print(f"Warning: Failed to cleanup temporary directory {temp_dir}: {str(e)}")

def upload_analysis_results(analysis_key, content):
    """Upload Strands analysis results to S3"""
    
    try:
        print(f"Uploading analysis results to: {analysis_key}")
        
        s3_client.put_object(
            Bucket=DRAWER_BUCKET,
            Key=analysis_key,
            Body=content.encode('utf-8'),
            ContentType='text/markdown'
        )
        
        print(f"Successfully uploaded analysis results ({len(content)} characters)")
        
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
        'analysis_type': 'strands_magic_mirror',
        'message': 'Strands analysis ready for delivery'
    }
    
    eventbridge_client.put_events(
        Entries=[{
            'Source': 'coderipple.system',
            'DetailType': 'analysis_ready',
            'Detail': json.dumps(event_detail)
        }]
    )
    
    print(f"Sent analysis_ready event for {repo_owner}/{repo_name}")

def send_task_event(event_type, task_id, details):
    """Send task logging events following Component Task Logging Standard"""
    
    event_detail = {
        'task_id': task_id,
        'component': 'analyst',
        'task_type': 'strands_analysis_processing',
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
