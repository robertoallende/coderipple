#!/usr/bin/env python3
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from webhook_parser import process_webhook

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python test_webhook.py <json_file> <event_type> [--fetch-diff]")
        print("Example: python test_webhook.py webhook.json push")
        print("Example: python test_webhook.py webhook.json push --fetch-diff")
        sys.exit(1)
    
    json_file = sys.argv[1]
    event_type = sys.argv[2]
    fetch_diff = len(sys.argv) == 4 and sys.argv[3] == '--fetch-diff'
    
    with open(json_file, 'r') as f:
        payload = f.read()
    
    # Note: For private repos, you would need to set GITHUB_TOKEN environment variable
    github_token = os.environ.get('GITHUB_TOKEN')
    
    process_webhook(payload, event_type, fetch_diff, github_token)

if __name__ == "__main__":
    main()