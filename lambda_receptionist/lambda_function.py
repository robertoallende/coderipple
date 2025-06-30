import json
import os
import subprocess
import zipfile
import tempfile
import traceback
from datetime import datetime
import boto3
import hashlib
import hmac

# AWS clients
s3_client = boto3.client('s3')
eventbridge_client = boto3.client('events')

# Configuration
DRAWER_BUCKET = 'coderipple-drawer'
GITHUB_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', '')

def lambda_handler(event, context):
    """
    Receptionist Lambda - Processes GitHub webhook events
    Clones repositories and stores in Drawer S3 bucket
    """
    
    print(f"Received event: {json.dumps(event, indent=2)}")
    
    # Generate task ID for tracking
    task_id = f"webhook_processing_{int(datetime.utcnow().timestamp())}"
    
    try:
        # Parse webhook payload first to get repository info for logging
        body = json.loads(event.get('body', '{}'))
        repository = body.get('repository', {})
        repo_owner = repository.get('owner', {}).get('login', 'unknown')
        repo_name = repository.get('name', 'unknown')
        webhook_event = event.get('headers', {}).get('X-GitHub-Event', 'unknown')
        
        # Send task_started event
        send_task_event('task_started', task_id, {
            'repository': {'owner': repo_owner, 'name': repo_name},
            'webhook_event': webhook_event,
            'message': 'Receptionist acknowledged webhook processing task'
        })
        
        # Always return 200 OK to GitHub immediately
        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook received'})
        }
        
        # Process webhook asynchronously
        process_webhook(event, task_id)
        
        return response
        
    except Exception as e:
        # Log error but still return 200 to GitHub
        print(f"Error processing webhook: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Send task_failed event
        send_task_event('task_failed', task_id, {
            'repository': {'owner': repo_owner, 'name': repo_name},
            'webhook_event': webhook_event,
            'error': {
                'type': 'WebhookProcessingError',
                'message': str(e),
                'stack_trace': traceback.format_exc()
            },
            'message': 'Webhook processing failed'
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook received'})
        }

def process_webhook(event, task_id):
    """Process GitHub webhook event with filtering and validation"""
    
    try:
        # Validate webhook signature
        if not validate_github_signature(event):
            raise ValueError("Invalid GitHub webhook signature")
        
        # Parse webhook payload
        body = json.loads(event.get('body', '{}'))
        webhook_event = event.get('headers', {}).get('X-GitHub-Event', '')
        
        print(f"Processing GitHub event: {webhook_event}")
        
        # Filter GitHub events - only process push and pull_request events
        if not should_process_event(webhook_event, body):
            print(f"Skipping event type: {webhook_event}")
            # Send task_completed for filtered events
            repository = body.get('repository', {})
            send_task_event('task_completed', task_id, {
                'repository': {
                    'owner': repository.get('owner', {}).get('login', 'unknown'),
                    'name': repository.get('name', 'unknown')
                },
                'webhook_event': webhook_event,
                'message': f'Event type {webhook_event} filtered - no processing required'
            })
            return
        
        # Extract repository information
        repository = body.get('repository', {})
        repo_owner = repository.get('owner', {}).get('login')
        repo_name = repository.get('name')
        default_branch = repository.get('default_branch', 'main')
        
        # Get commit SHA based on event type
        commit_sha = get_commit_sha(webhook_event, body)
        
        if not all([repo_owner, repo_name, commit_sha]):
            raise ValueError("Missing required repository information")
        
        print(f"Processing repository: {repo_owner}/{repo_name} at {commit_sha}")
        
        # Clone repository with three-step process
        workingcopy_path, repohistory_path = clone_repository(repo_owner, repo_name, commit_sha)
        
        # Upload to Drawer S3 bucket
        s3_location = upload_to_drawer(repo_owner, repo_name, commit_sha, workingcopy_path, repohistory_path)
        
        # Send repo_ready event to EventBridge
        send_repo_ready_event(repo_owner, repo_name, default_branch, commit_sha, s3_location)
        
        # Send task_completed event
        send_task_event('task_completed', task_id, {
            'repository': {
                'owner': repo_owner,
                'name': repo_name,
                'commit_sha': commit_sha
            },
            's3_location': s3_location,
            'webhook_event': webhook_event,
            'message': 'Repository successfully processed and stored in S3'
        })
        
        print(f"Successfully processed repository: {repo_owner}/{repo_name}")
        
    except Exception as e:
        print(f"Error in process_webhook: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Extract repository info for error logging
        try:
            body = json.loads(event.get('body', '{}'))
            repository = body.get('repository', {})
            repo_owner = repository.get('owner', {}).get('login', 'unknown')
            repo_name = repository.get('name', 'unknown')
            webhook_event = event.get('headers', {}).get('X-GitHub-Event', 'unknown')
        except:
            repo_owner = repo_name = webhook_event = 'unknown'
        
        # Send task_failed event
        send_task_event('task_failed', task_id, {
            'repository': {'owner': repo_owner, 'name': repo_name},
            'webhook_event': webhook_event,
            'error': {
                'type': type(e).__name__,
                'message': str(e),
                'stack_trace': traceback.format_exc()
            },
            'message': 'Repository processing failed'
        })
        
        # Re-raise to be handled by main lambda_handler
        raise

def should_process_event(webhook_event, body):
    """Filter GitHub webhook events - only process relevant events"""
    
    # Process push events to main/master branches
    if webhook_event == 'push':
        ref = body.get('ref', '')
        # Only process pushes to main/master branches
        return ref in ['refs/heads/main', 'refs/heads/master']
    
    # Process pull request events (opened, synchronize, reopened)
    if webhook_event == 'pull_request':
        action = body.get('action', '')
        return action in ['opened', 'synchronize', 'reopened']
    
    # Skip all other events
    return False

def get_commit_sha(webhook_event, body):
    """Extract commit SHA based on webhook event type"""
    
    if webhook_event == 'push':
        return body.get('head_commit', {}).get('id')
    
    if webhook_event == 'pull_request':
        return body.get('pull_request', {}).get('head', {}).get('sha')
    
    return None

def validate_github_signature(event):
    """Validate GitHub webhook signature"""
    
    if not GITHUB_SECRET:
        print("Warning: No GitHub webhook secret configured")
        return True  # Skip validation if no secret set
    
    signature = event.get('headers', {}).get('X-Hub-Signature-256', '')
    body = event.get('body', '')
    
    if not signature.startswith('sha256='):
        return False
    
    expected_signature = 'sha256=' + hmac.new(
        GITHUB_SECRET.encode('utf-8'),
        body.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

def clone_repository(repo_owner, repo_name, commit_sha):
    """
    Clone repository using three-step process:
    1. Full clone with history
    2. Checkout specific commit
    3. Create clean working copy
    """
    
    repo_url = f"https://github.com/{repo_owner}/{repo_name}.git"
    
    # Create temporary directories
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_full_path = os.path.join(temp_dir, 'repo_full')
        workingcopy_path = os.path.join(temp_dir, 'workingcopy')
        repohistory_path = os.path.join(temp_dir, 'repohistory')
        
        print(f"Cloning repository: {repo_url}")
        
        # Step 1: Clone full repository with history
        subprocess.run([
            'git', 'clone',
            repo_url,
            repo_full_path
        ], check=True, capture_output=True, text=True)
        
        print(f"Checking out commit: {commit_sha}")
        
        # Step 2: Checkout specific commit
        subprocess.run([
            'git', 'checkout', commit_sha
        ], cwd=repo_full_path, check=True, capture_output=True, text=True)
        
        print("Creating clean working copy")
        
        # Step 3: Create clean working copy (no .git)
        os.makedirs(workingcopy_path)
        subprocess.run([
            'git', 'archive', commit_sha,
            '--format=tar'
        ], cwd=repo_full_path, stdout=open(os.path.join(temp_dir, 'workingcopy.tar'), 'wb'), check=True)
        
        # Extract working copy
        subprocess.run([
            'tar', '-xf', os.path.join(temp_dir, 'workingcopy.tar'),
            '-C', workingcopy_path
        ], check=True)
        
        # Copy full repository for history
        subprocess.run([
            'cp', '-r', repo_full_path, repohistory_path
        ], check=True)
        
        # Create ZIP files for upload
        workingcopy_zip = os.path.join(temp_dir, 'workingcopy.zip')
        repohistory_zip = os.path.join(temp_dir, 'repohistory.zip')
        
        create_zip_archive(workingcopy_path, workingcopy_zip)
        create_zip_archive(repohistory_path, repohistory_zip)
        
        return workingcopy_zip, repohistory_zip

def create_zip_archive(source_dir, zip_path):
    """Create ZIP archive from directory"""
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arc_name)

def upload_to_drawer(repo_owner, repo_name, commit_sha, workingcopy_path, repohistory_path):
    """Upload repository files to Drawer S3 bucket"""
    
    s3_prefix = f"repos/{repo_owner}/{repo_name}/{commit_sha}"
    
    print(f"Uploading to S3: {s3_prefix}")
    
    # Upload workingcopy
    workingcopy_key = f"{s3_prefix}/workingcopy.zip"
    s3_client.upload_file(workingcopy_path, DRAWER_BUCKET, workingcopy_key)
    print(f"Uploaded workingcopy: {workingcopy_key}")
    
    # Upload repohistory
    repohistory_key = f"{s3_prefix}/repohistory.zip"
    s3_client.upload_file(repohistory_path, DRAWER_BUCKET, repohistory_key)
    print(f"Uploaded repohistory: {repohistory_key}")
    
    return s3_prefix

def send_task_event(event_type, task_id, details):
    """Send task logging events following Component Task Logging Standard"""
    
    event_detail = {
        'task_id': task_id,
        'component': 'receptionist',
        'task_type': 'webhook_processing',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        **details
    }
    
    eventbridge_client.put_events(
        Entries=[{
            'Source': 'coderipple.receptionist',
            'DetailType': event_type,
            'Detail': json.dumps(event_detail)
        }]
    )
    
    print(f"Sent {event_type} event for task {task_id}")

def send_repo_ready_event(repo_owner, repo_name, default_branch, commit_sha, s3_location):
    """Send repo_ready event to EventBridge"""
    
    event_detail = {
        'component': 'Receptionist',
        'repository': {
            'owner': repo_owner,
            'name': repo_name,
            'default_branch': default_branch,
            'commit_sha': commit_sha
        },
        's3_location': s3_location,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    eventbridge_client.put_events(
        Entries=[{
            'Source': 'coderipple.system',
            'DetailType': 'repo_ready',
            'Detail': json.dumps(event_detail)
        }]
    )
    
    print(f"Sent repo_ready event for {repo_owner}/{repo_name}")


