import json
import boto3
import logging
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3_client = boto3.client('s3')

# Environment variables
INVENTORY_BUCKET = os.environ.get('INVENTORY_BUCKET', 'coderipple-cabinet')

def lambda_handler(event, context):
    """
    Hermes - The Bureaucrat
    Processes EventBridge events and logs them to S3 Inventory bucket
    """
    
    try:
        # Process the event and create log entry
        log_entry = process_event(event)
        
        # Write to S3
        write_to_inventory(log_entry)
        
        logger.info(f"Successfully logged event: {log_entry}")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Event logged successfully')
        }
        
    except Exception as e:
        # Create error log entry
        error_entry = create_error_log(event, str(e))
        
        # Try to write error to S3
        try:
            write_to_inventory(error_entry)
        except Exception as s3_error:
            logger.error(f"Failed to write error log to S3: {s3_error}")
        
        logger.error(f"Error processing event: {e}")
        
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error processing event: {str(e)}')
        }

def process_event(event):
    """
    Extract component, timestamp, event type and details from EventBridge event
    Format: Timestamp | Component | Event | Details
    """
    
    # Extract event details
    detail = event.get('detail', {})
    component = detail.get('component', 'Unknown')
    timestamp = detail.get('timestamp', datetime.utcnow().isoformat() + 'Z')
    event_type = event.get('detail-type', 'unknown_event')
    
    # Extract meaningful details based on event type
    details = extract_event_details(event_type, detail)
    
    # Format log entry
    log_entry = f"{timestamp} | {component} | {event_type} | {details}"
    
    return log_entry

def extract_event_details(event_type, detail):
    """
    Extract relevant details based on event type
    """
    
    repository = detail.get('repository', {})
    repo_name = f"{repository.get('owner', 'unknown')}/{repository.get('name', 'unknown')}"
    
    if event_type == 'repo_ready':
        return f"{repo_name}"
    elif event_type == 'analysis_complete':
        files = detail.get('s3_files', [])
        return f"{repo_name} ({len(files)} files)"
    elif event_type == 'pr_created':
        pr_number = detail.get('pr_number', 'unknown')
        return f"{repo_name}#{pr_number}"
    else:
        return f"{repo_name}"

def create_error_log(event, error_message):
    """
    Create error log entry when event processing fails
    """
    timestamp = datetime.utcnow().isoformat() + 'Z'
    raw_event = json.dumps(event, separators=(',', ':'))[:500]  # Truncate if too long
    
    return f"{timestamp} | Error | processing_failed | {error_message} | {raw_event}"

def clean_table_empty_lines(content):
    """
    Remove empty lines within the table after the header separator.
    Preserves the original table structure but removes any blank table rows.
    """
    lines = content.split('\n')
    cleaned_lines = []
    in_table = False
    header_separator_found = False
    
    for line in lines:
        # Detect if we're in the table section
        if '| Timestamp | Component | Event | Repository |' in line:
            in_table = True
            cleaned_lines.append(line)
        elif '|-----------|-----------|-------|------------|' in line:
            header_separator_found = True
            cleaned_lines.append(line)
        elif in_table and header_separator_found:
            # We're in the table data section
            if line.strip() == '' or line.strip() == '|':
                # Skip empty lines in table completely
                continue
            elif line.startswith('|') and line.endswith('|'):
                # Valid table row
                cleaned_lines.append(line)
            else:
                # Non-table content - stop processing table
                in_table = False
                header_separator_found = False
                cleaned_lines.append(line)
        else:
            # Not in table or before table
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def write_to_inventory(log_entry):
    """
    Write log entry to README.md in the existing table format
    """
    
    s3_key = "README.md"
    
    try:
        # Try to get existing README.md
        try:
            response = s3_client.get_object(Bucket=INVENTORY_BUCKET, Key=s3_key)
            existing_content = response['Body'].read().decode('utf-8')
        except s3_client.exceptions.NoSuchKey:
            logger.error("README.md doesn't exist - it should be pre-created")
            return
        
        # Parse log entry and format as table row
        parts = log_entry.split(' | ')
        if len(parts) >= 4:
            timestamp, component, event, details = parts[0], parts[1], parts[2], ' | '.join(parts[3:])
            table_row = f"| {timestamp} | {component} | {event} | {details} |"
        else:
            # Fallback for malformed entries
            table_row = f"| {log_entry} | | | |"
        
        # Add the new table row to the content
        new_content = existing_content + '\n' + table_row
        
        # Clean up any empty lines in the table
        cleaned_content = clean_table_empty_lines(new_content)
        
        # Write updated README back to S3
        s3_client.put_object(
            Bucket=INVENTORY_BUCKET,
            Key=s3_key,
            Body=cleaned_content.encode('utf-8'),
            ContentType='text/markdown'
        )
        
        logger.info(f"Appended to README.md: {table_row}")
        
    except Exception as e:
        logger.error(f"Failed to write to README.md: {e}")
        raise
