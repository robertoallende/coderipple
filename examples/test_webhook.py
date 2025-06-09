#!/usr/bin/env python3
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from webhook_parser import process_webhook

def main():
    if len(sys.argv) != 3:
        print("Usage: python test_webhook.py <json_file> <event_type>")
        print("Example: python test_webhook.py webhook.json push")
        sys.exit(1)
    
    json_file = sys.argv[1]
    event_type = sys.argv[2]
    
    with open(json_file, 'r') as f:
        payload = f.read()
    
    process_webhook(payload, event_type)

if __name__ == "__main__":
    main()