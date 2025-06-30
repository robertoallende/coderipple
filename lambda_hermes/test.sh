#!/bin/bash

# Test script for Hermes Lambda function

set -e

# Check if Lambda ARN exists
if [ ! -f "lambda-arn.txt" ]; then
    echo "❌ Lambda ARN not found. Run deploy.sh first."
    exit 1
fi

LAMBDA_ARN=$(cat lambda-arn.txt)
FUNCTION_NAME="coderipple-hermes"
REGION="us-east-1"

echo "🧪 Testing Hermes Lambda Function..."
echo "📋 Function: $FUNCTION_NAME"
echo ""

# Test 1: repo_ready event
echo "Test 1: Sending repo_ready event"
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{"source":"coderipple.system","detail-type":"repo_ready","detail":{"component":"Receptionist","repository":{"owner":"test-user","name":"test-repo","commit_sha":"abc123def456","default_branch":"main"},"s3_location":"bucket/repos/test-user/test-repo/abc123def456/","timestamp":"2025-06-30T12:30:00Z"}}' \
  --region $REGION \
  response-1.json

echo "Response:"
cat response-1.json
echo -e "\n"

# Test 2: analysis_complete event
echo "Test 2: Sending analysis_complete event"
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{"source":"coderipple.system","detail-type":"analysis_complete","detail":{"component":"Analyst","repository":{"owner":"test-user","name":"test-repo","commit_sha":"abc123def456","default_branch":"main"},"s3_files":["analysis/report.md","analysis/metrics.json"],"timestamp":"2025-06-30T12:31:00Z"}}' \
  --region $REGION \
  response-2.json

echo "Response:"
cat response-2.json
echo -e "\n"

# Test 3: Malformed event (should create error log)
echo "Test 3: Sending malformed event"
aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload '{"source":"coderipple.system","detail-type":"unknown_event","detail":{"malformed":"data","missing":"component field"}}' \
  --region $REGION \
  response-3.json

echo "Response:"
cat response-3.json
echo -e "\n"

# Check CloudWatch logs
echo "📊 Recent CloudWatch logs:"
aws logs describe-log-streams \
  --log-group-name "/aws/lambda/$FUNCTION_NAME" \
  --region $REGION \
  --order-by LastEventTime \
  --descending \
  --max-items 1 \
  --query 'logStreams[0].logStreamName' \
  --output text > latest-log-stream.txt

if [ -s latest-log-stream.txt ]; then
    LATEST_STREAM=$(cat latest-log-stream.txt)
    echo "Latest log stream: $LATEST_STREAM"
    
    aws logs get-log-events \
      --log-group-name "/aws/lambda/$FUNCTION_NAME" \
      --log-stream-name "$LATEST_STREAM" \
      --region $REGION \
      --query 'events[*].message' \
      --output text
else
    echo "No log streams found yet"
fi

echo ""
echo "✅ Testing complete!"
echo ""
echo "Expected results:"
echo "- Tests 1 & 2: Should show S3 bucket errors (bucket doesn't exist yet)"
echo "- Test 3: Should handle malformed event gracefully"
echo "- CloudWatch logs should show detailed error information"

# Cleanup
rm -f response-*.json latest-log-stream.txt
