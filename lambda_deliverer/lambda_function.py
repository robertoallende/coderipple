import json
import boto3
import os
import zipfile
import tempfile
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# AWS clients
s3_client = boto3.client('s3')
events_client = boto3.client('events')

# Environment variables
DRAWER_BUCKET = os.environ.get('DRAWER_BUCKET', 'coderipple-drawer')
SHOWROOM_BUCKET = os.environ.get('SHOWROOM_BUCKET', 'coderipple-showroom')
EVENT_BUS_NAME = os.environ.get('EVENT_BUS_NAME', 'coderipple-events')

def lambda_handler(event, context):
    """
    Deliverer Lambda - Packages analysis results and delivers to Showroom
    
    Triggered by: analysis_ready events from Analyst
    Outputs: Packaged results in Showroom + updated website
    """
    
    logger.info(f"Deliverer received event: {json.dumps(event)}")
    
    try:
        # Parse EventBridge event
        detail = event.get('detail', {})
        repo_owner = detail.get('repository', {}).get('owner')
        repo_name = detail.get('repository', {}).get('name')
        commit_sha = detail.get('commit_sha')
        
        if not all([repo_owner, repo_name, commit_sha]):
            raise ValueError("Missing required repository information in event")
        
        logger.info(f"Processing delivery for {repo_owner}/{repo_name} @ {commit_sha}")
        
        # Step 1: Retrieve analysis results from Drawer
        analysis_data = retrieve_analysis_results(repo_owner, repo_name, commit_sha)
        
        # Step 2: Package analysis results
        package_path = package_analysis_results(repo_owner, repo_name, commit_sha, analysis_data)
        
        # Step 3: Upload to Showroom
        analysis_url = upload_to_showroom(repo_owner, repo_name, commit_sha, package_path, analysis_data)
        
        # Step 4: Update Showroom website
        try:
            update_showroom_website(repo_owner, repo_name, commit_sha, analysis_url)
            website_updated = True
        except Exception as e:
            logger.error(f"Failed to update Showroom website: {e}")
            website_updated = False
            # Send error event to Telephonist for Hermes logging
            send_error_event(repo_owner, repo_name, commit_sha, f"Website update failed: {e}")
        
        # Step 5: Publish delivery_complete event
        send_delivery_complete_event(repo_owner, repo_name, commit_sha, analysis_url, website_updated)
        
        logger.info(f"✅ Delivery complete for {repo_owner}/{repo_name} @ {commit_sha}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Delivery completed successfully',
                'repository': f"{repo_owner}/{repo_name}",
                'commit': commit_sha,
                'analysis_url': analysis_url,
                'website_updated': website_updated
            })
        }
        
    except Exception as e:
        logger.error(f"❌ Delivery failed: {e}")
        
        # Send error event to Telephonist
        try:
            repo_info = f"{repo_owner}/{repo_name}" if 'repo_owner' in locals() else "unknown"
            send_error_event(repo_info, "unknown", "unknown", f"Delivery failed: {e}")
        except:
            pass
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Delivery failed'
            })
        }

def retrieve_analysis_results(repo_owner: str, repo_name: str, commit_sha: str) -> Dict[str, Any]:
    """
    Retrieve analysis results from Drawer S3 bucket
    """
    
    drawer_prefix = f"repos/{repo_owner}/{repo_name}/{commit_sha}/analysis/"
    
    logger.info(f"Retrieving analysis results from s3://{DRAWER_BUCKET}/{drawer_prefix}")
    
    try:
        # List analysis files
        response = s3_client.list_objects_v2(
            Bucket=DRAWER_BUCKET,
            Prefix=drawer_prefix
        )
        
        if 'Contents' not in response:
            raise ValueError(f"No analysis results found at {drawer_prefix}")
        
        analysis_files = {}
        
        # Download analysis files
        for obj in response['Contents']:
            key = obj['Key']
            filename = key.split('/')[-1]
            
            logger.info(f"Downloading {key}")
            
            file_response = s3_client.get_object(Bucket=DRAWER_BUCKET, Key=key)
            content = file_response['Body'].read()
            
            if filename.endswith('.md'):
                analysis_files[filename] = content.decode('utf-8')
            else:
                analysis_files[filename] = content
        
        logger.info(f"Retrieved {len(analysis_files)} analysis files")
        return analysis_files
        
    except Exception as e:
        logger.error(f"Failed to retrieve analysis results: {e}")
        raise

def package_analysis_results(repo_owner: str, repo_name: str, commit_sha: str, analysis_data: Dict[str, Any]) -> str:
    """
    Package analysis results into ZIP file
    """
    
    logger.info(f"Packaging analysis results for {repo_owner}/{repo_name}")
    
    # Create temporary ZIP file
    temp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(temp_dir, f"analysis-{repo_owner}-{repo_name}-{commit_sha[:8]}.zip")
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            # Add README for the package
            package_readme = generate_package_readme(repo_owner, repo_name, commit_sha)
            zipf.writestr("README.md", package_readme)
            
            # Add analysis files
            for filename, content in analysis_data.items():
                if isinstance(content, str):
                    zipf.writestr(f"analysis/{filename}", content)
                else:
                    zipf.writestr(f"analysis/{filename}", content)
            
            # Add metadata
            metadata = {
                "repository": f"{repo_owner}/{repo_name}",
                "commit_sha": commit_sha,
                "generated_at": datetime.utcnow().isoformat() + "Z",
                "coderipple_version": "1.0.0",
                "package_type": "analysis_results"
            }
            zipf.writestr("coderipple/metadata.json", json.dumps(metadata, indent=2))
        
        logger.info(f"✅ Package created: {zip_path}")
        return zip_path
        
    except Exception as e:
        logger.error(f"Failed to package analysis results: {e}")
        raise

def generate_package_readme(repo_owner: str, repo_name: str, commit_sha: str) -> str:
    """
    Generate README.md for the analysis package
    """
    
    return f"""# CodeRipple Analysis Results

## Repository Information
- **Repository**: {repo_owner}/{repo_name}
- **Commit**: {commit_sha}
- **Generated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

## Package Contents

### analysis/
Contains the analysis results and reports generated by CodeRipple:
- Analysis reports in Markdown format
- Code quality metrics and insights
- Generated documentation and findings

### coderipple/
Contains metadata about this analysis package:
- Generation timestamp and version information
- Repository and commit details
- Package type and structure information

## About CodeRipple

CodeRipple is a serverless code analysis platform that automatically analyzes your repositories and generates comprehensive insights, documentation, and quality reports.

**Website**: [CodeRipple Showroom](http://{SHOWROOM_BUCKET}.s3-website-us-east-1.amazonaws.com)

---

*Generated by CodeRipple - documentation that evolves with your code, automatically*
"""

def upload_to_showroom(repo_owner: str, repo_name: str, commit_sha: str, package_path: str, analysis_data: Dict[str, Any]) -> str:
    """
    Upload packaged results to Showroom S3 bucket
    """
    
    showroom_prefix = f"analyses/{repo_owner}/{repo_name}/{commit_sha}"
    
    logger.info(f"Uploading to Showroom: s3://{SHOWROOM_BUCKET}/{showroom_prefix}")
    
    try:
        # Upload ZIP package
        zip_key = f"{showroom_prefix}/analysis.zip"
        with open(package_path, 'rb') as f:
            s3_client.put_object(
                Bucket=SHOWROOM_BUCKET,
                Key=zip_key,
                Body=f,
                ContentType='application/zip',
                ACL='public-read'
            )
        
        # Generate and upload analysis page
        analysis_html = generate_analysis_page(repo_owner, repo_name, commit_sha, analysis_data)
        s3_client.put_object(
            Bucket=SHOWROOM_BUCKET,
            Key=f"{showroom_prefix}/index.html",
            Body=analysis_html,
            ContentType='text/html',
            ACL='public-read'
        )
        
        # Upload individual analysis files for web viewing
        for filename, content in analysis_data.items():
            if filename.endswith('.md'):
                s3_client.put_object(
                    Bucket=SHOWROOM_BUCKET,
                    Key=f"{showroom_prefix}/{filename}",
                    Body=content if isinstance(content, str) else content.decode('utf-8'),
                    ContentType='text/markdown',
                    ACL='public-read'
                )
        
        analysis_url = f"http://{SHOWROOM_BUCKET}.s3-website-us-east-1.amazonaws.com/analyses/{repo_owner}/{repo_name}/{commit_sha}/"
        
        logger.info(f"✅ Uploaded to Showroom: {analysis_url}")
        return analysis_url
        
    except Exception as e:
        logger.error(f"Failed to upload to Showroom: {e}")
        raise

def generate_analysis_page(repo_owner: str, repo_name: str, commit_sha: str, analysis_data: Dict[str, Any]) -> str:
    """
    Generate HTML page for analysis results using Showroom template style
    """
    
    # Find the main analysis report
    main_report = None
    for filename, content in analysis_data.items():
        if filename.endswith('.md') and isinstance(content, str):
            main_report = content
            break
    
    if not main_report:
        main_report = "# Analysis Results\n\nAnalysis completed successfully. Download the full results package for detailed information."
    
    # Convert markdown to HTML-friendly format (basic conversion)
    html_content = main_report.replace('\n', '<br>\n').replace('# ', '<h1>').replace('## ', '<h2>').replace('### ', '<h3>')
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>CodeRipple Analysis - {repo_owner}/{repo_name}</title>
  <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
  <meta name="description" content="CodeRipple analysis results for {repo_owner}/{repo_name}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=1.0">
  <link rel="stylesheet" href="//cdn.jsdelivr.net/npm/docsify@4/lib/themes/vue.css">
  <link rel="stylesheet" href="../../../assets/css/coderipple.css">
  <link rel="icon" type="image/png" href="../../../assets/images/coderipple-logo.png">
</head>
<body>
  <div id="app">
    <div style="text-align: center; padding: 50px; color: #021A2D;">
      <h2>Loading Analysis Results...</h2>
      <p>CodeRipple analysis for {repo_owner}/{repo_name}</p>
    </div>
  </div>
  <script>
    window.$docsify = {{
      name: 'CodeRipple Analysis',
      repo: '',
      loadSidebar: false,
      loadNavbar: false,
      maxLevel: 4,
      subMaxLevel: 3,
      auto2top: true,
      plugins: [
        function(hook, vm) {{
          hook.mounted(function() {{
            // Create custom header
            const header = document.createElement('div');
            header.className = 'app-name';
            header.innerHTML = '<a href="../../../#/" class="app-name-link">' +
              '<img src="../../../assets/images/coderipple-logo.png" alt="CodeRipple">' +
              '<div class="app-name-text">' +
                '<div class="app-name-title">CodeRipple Analysis</div>' +
                '<div class="app-name-tagline">{repo_owner}/{repo_name} @ {commit_sha[:8]}</div>' +
              '</div>' +
            '</a>';
            document.body.insertBefore(header, document.body.firstChild);
            
            // Create fixed footer
            const footer = document.createElement('div');
            footer.className = 'footer-content';
            footer.innerHTML = '<p style="font-size: 1.1em; margin-bottom: 8px;"><strong>CodeRipple Analysis</strong></p>' +
              '<p style="font-family: \\'JetBrains Mono\\', monospace; font-size: 0.9em; opacity: 0.8; margin-bottom: 12px;">documentation that evolves with your code, automatically</p>' +
              '<p style="font-size: 0.8em; opacity: 0.7;"><em>Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC</em></p>';
            document.body.appendChild(footer);
            
            // Add download button
            const downloadBtn = document.createElement('div');
            downloadBtn.style.cssText = 'position: fixed; top: 100px; right: 20px; z-index: 1000;';
            downloadBtn.innerHTML = '<a href="./analysis.zip" class="coderipple-btn" style="background-color: #1EA3B7; color: white; padding: 10px 15px; text-decoration: none; border-radius: 4px;">Download Results</a>';
            document.body.appendChild(downloadBtn);
          }});
        }}
      ]
    }}
  </script>
  <!-- Docsify v4 -->
  <script src="//cdn.jsdelivr.net/npm/docsify@4"></script>
</body>
</html>"""

def update_showroom_website(repo_owner: str, repo_name: str, commit_sha: str, analysis_url: str):
    """
    Update Showroom README.md with new analysis entry (prepend method)
    """
    
    logger.info(f"Updating Showroom website with new analysis entry")
    
    try:
        # Download current README.md
        response = s3_client.get_object(Bucket=SHOWROOM_BUCKET, Key='README.md')
        current_readme = response['Body'].read().decode('utf-8')
        
        # Generate new analysis entry
        timestamp = datetime.utcnow().strftime('%Y-%m-%d at %H:%M UTC')
        new_entry = f"""
<div class="analysis-item">
  <div class="repo-name">
    <a href="/analyses/{repo_owner}/{repo_name}/{commit_sha}/">{repo_owner}/{repo_name}</a>
  </div>
  <div class="analysis-time">Analyzed: {timestamp}</div>
  <div class="analysis-links">
    <a href="/analyses/{repo_owner}/{repo_name}/{commit_sha}/">View Analysis</a>
    <a href="/analyses/{repo_owner}/{repo_name}/{commit_sha}/analysis.zip">Download Results</a>
  </div>
</div>
"""
        
        # Find "Recent Analyses" section and prepend new entry
        lines = current_readme.split('\n')
        header_index = -1
        
        for i, line in enumerate(lines):
            if line.strip() == '# Recent Analyses':
                header_index = i
                break
        
        if header_index == -1:
            raise ValueError("Could not find 'Recent Analyses' section in README.md")
        
        # Insert new entry after the header (and any empty line)
        insert_index = header_index + 1
        if insert_index < len(lines) and lines[insert_index].strip() == '':
            insert_index += 1
        
        lines.insert(insert_index, new_entry)
        
        # Upload updated README.md
        updated_readme = '\n'.join(lines)
        s3_client.put_object(
            Bucket=SHOWROOM_BUCKET,
            Key='README.md',
            Body=updated_readme,
            ContentType='text/markdown',
            ACL='public-read'
        )
        
        logger.info(f"✅ Showroom website updated with new analysis entry")
        
    except Exception as e:
        logger.error(f"Failed to update Showroom website: {e}")
        raise

def send_delivery_complete_event(repo_owner: str, repo_name: str, commit_sha: str, analysis_url: str, website_updated: bool):
    """
    Send delivery_complete event to EventBridge
    """
    
    event_detail = {
        'event_type': 'delivery_complete',
        'component': 'Deliverer',
        'repository': {
            'owner': repo_owner,
            'name': repo_name
        },
        'commit_sha': commit_sha,
        'analysis_url': analysis_url,
        'website_updated': website_updated,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        events_client.put_events(
            Entries=[
                {
                    'Source': 'coderipple.deliverer',
                    'DetailType': 'Delivery Complete',
                    'Detail': json.dumps(event_detail),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )
        
        logger.info(f"✅ Sent delivery_complete event for {repo_owner}/{repo_name}")
        
    except Exception as e:
        logger.error(f"Failed to send delivery_complete event: {e}")
        # Don't raise - delivery was successful even if event failed

def send_error_event(repo_owner: str, repo_name: str, commit_sha: str, error_message: str):
    """
    Send error event to EventBridge for Hermes logging
    """
    
    event_detail = {
        'event_type': 'delivery_error',
        'component': 'Deliverer',
        'repository': {
            'owner': repo_owner,
            'name': repo_name
        },
        'commit_sha': commit_sha,
        'error': error_message,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    try:
        events_client.put_events(
            Entries=[
                {
                    'Source': 'coderipple.deliverer',
                    'DetailType': 'Delivery Error',
                    'Detail': json.dumps(event_detail),
                    'EventBusName': EVENT_BUS_NAME
                }
            ]
        )
        
        logger.info(f"✅ Sent error event to Telephonist for Hermes logging")
        
    except Exception as e:
        logger.error(f"Failed to send error event: {e}")
        # Don't raise - this is just for logging
