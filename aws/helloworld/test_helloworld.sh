#!/bin/bash
# test_helloworld.sh

set -e

FUNCTION_NAME="helloworld-debug"
REGION="us-east-1"

echo "Testing Hello World Lambda function..."

# Test function
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --payload '{"test": "hello", "source": "manual_test"}' \
  --cli-binary-format raw-in-base64-out \
  --region "$REGION" \
  /tmp/helloworld_response.json

echo "Response received:"
cat /tmp/helloworld_response.json | jq '.'

echo ""
echo "Testing complete!"
echo "Function is working if you see 'Hello World from CodeRipple Debug Layer' above."
