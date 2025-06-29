#!/bin/bash
# test_helloworld.sh

set -e

FUNCTION_NAME="helloworld-debug"
REGION="us-east-1"

echo "Testing Hello World Lambda function..."

# Test function with proper parameter order
aws lambda invoke \
  --function-name "$FUNCTION_NAME" \
  --region "$REGION" \
  --payload '{"test": "hello", "source": "manual_test"}' \
  --cli-binary-format raw-in-base64-out \
  /tmp/helloworld_response.json

echo "Response received:"
if command -v jq &> /dev/null; then
    cat /tmp/helloworld_response.json | jq '.'
else
    echo "jq not available, showing raw response:"
    cat /tmp/helloworld_response.json
fi

echo ""
echo "Testing complete!"
echo "Function is working if you see 'Hello World from CodeRipple Debug Layer' above."
