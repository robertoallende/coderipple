#!/usr/bin/env python3

"""
Cleanup script for Hermes README.md table.
Removes empty lines within the event log table while preserving the overall structure.
"""

import boto3
import sys

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
                # Skip empty lines in table
                print(f"Removing empty line: '{line}'")
                continue
            elif line.startswith('|') and line.endswith('|'):
                # Valid table row
                cleaned_lines.append(line)
            elif line.strip() == '':
                # Empty line after table - keep it and stop processing table
                in_table = False
                header_separator_found = False
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

def main():
    """Clean up the Cabinet README.md table"""
    
    bucket_name = "coderipple-cabinet"
    s3_key = "README.md"
    
    print(f"🧹 Cleaning up table in s3://{bucket_name}/{s3_key}")
    
    try:
        # Initialize S3 client
        s3_client = boto3.client('s3')
        
        # Download current README.md
        print("📥 Downloading current README.md...")
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_key)
        original_content = response['Body'].read().decode('utf-8')
        
        print(f"📊 Original content length: {len(original_content)} characters")
        
        # Clean up empty lines in table
        print("🔧 Cleaning empty lines from table...")
        cleaned_content = clean_table_empty_lines(original_content)
        
        print(f"📊 Cleaned content length: {len(cleaned_content)} characters")
        
        # Check if changes were made
        if original_content == cleaned_content:
            print("✅ No empty lines found - table is already clean!")
            return
        
        # Upload cleaned version
        print("📤 Uploading cleaned README.md...")
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=cleaned_content.encode('utf-8'),
            ContentType='text/markdown'
        )
        
        print("✅ Table cleanup complete!")
        print(f"🌐 View result: http://{bucket_name}.s3-website-us-east-1.amazonaws.com/README.md")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()