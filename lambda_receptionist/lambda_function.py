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
    
    try:
        # Always return 200 OK to GitHub immediately
        response = {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook received'})
        }
        
        # Process webhook asynchronously
        process_webhook(event)
        
        return response
        
    except Exception as e:
        # Log error but still return 200 to GitHub
        print(f"Error processing webhook: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        # Send error event to EventBridge for Hermes logging
        send_error_event(str(e), traceback.format_exc(), event)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Webhook received'})
        }

def process_webhook(event):
    """Process GitHub webhook event"""
    
    # Validate webhook signature
    if not validate_github_signature(event):
        raise ValueError("Invalid GitHub webhook signature")
    
    # Parse webhook payload
    body = json.loads(event.get('body', '{}'))
    
    # Extract repository information
    repository = body.get('repository', {})
    head_commit = body.get('head_commit', {})
    
    repo_owner = repository.get('owner', {}).get('login')
    repo_name = repository.get('name')
    default_branch = repository.get('default_branch', 'main')
    commit_sha = head_commit.get('id')
    
    if not all([repo_owner, repo_name, commit_sha]):
        raise ValueError("Missing required repository information")
    
    print(f"Processing repository: {repo_owner}/{repo_name} at {commit_sha}")
    
    # Clone repository with three-step process
    workingcopy_path, repohistory_path = clone_repository(repo_owner, repo_name, commit_sha)
    
    # Upload to Drawer S3 bucket
    s3_location = upload_to_drawer(repo_owner, repo_name, commit_sha, workingcopy_path, repohistory_path)
    
    # Send repo_ready event to EventBridge
    send_repo_ready_event(repo_owner, repo_name, default_branch, commit_sha, s3_location)
    
    print(f"Successfully processed repository: {repo_owner}/{repo_name}")

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

def send_error_event(error_message, error_traceback, original_event):
    """Send error event to EventBridge for Hermes logging"""
    
    # Extract what we can from the original event
    try:
        body = json.loads(original_event.get('body', '{}'))
        repository = body.get('repository', {})
        repo_owner = repository.get('owner', {}).get('login', 'unknown')
        repo_name = repository.get('name', 'unknown')
        commit_sha = body.get('head_commit', {}).get('id', 'unknown')
    except:
        repo_owner = repo_name = commit_sha = 'unknown'
    
    error_detail = {
        'component': 'Receptionist',
        'error_type': 'repository_processing_failed',
        'repository': {
            'owner': repo_owner,
            'name': repo_name
        },
        'commit_sha': commit_sha,
        'error_message': error_message,
        'error_details': error_traceback,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        eventbridge_client.put_events(
            Entries=[{
                'Source': 'coderipple.system',
                'DetailType': 'processing_error',
                'Detail': json.dumps(error_detail)
            }]
        )
        print("Sent error event to EventBridge")
    except Exception as e:
        print(f"Failed to send error event: {str(e)}")
