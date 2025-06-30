#!/bin/bash

# Test script for CodeRipple Telephonist EventBridge

set -e

# Check if event bus exists
if [ ! -f "event-bus-name.txt" ]; then
    echo "❌ Event bus name not found. Run deploy.sh first."
    exit 1
fi

BUS_NAME=$(cat event-bus-name.txt)
REGION="us-east-1"  # Change as needed

echo "🧪 Testing CodeRipple Telephonist..."
echo "📞 Event Bus: $BUS_NAME"
echo ""

# Test 1: Send repo_ready event
echo "Test 1: Sending repo_ready event"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "repo_ready",
      "Detail": "{\"repository\":{\"owner\":\"test-user\",\"name\":\"test-repo\",\"commit_sha\":\"abc123\",\"default_branch\":\"main\"},\"s3_location\":\"bucket/test/\",\"timestamp\":\"2025-06-30T12:30:00Z\"}",
      "EventBusName": "'$BUS_NAME'"
    }
  ]' \
  --region $REGION

echo "✅ repo_ready event sent"
echo ""

# Test 2: Send analysis_complete event  
echo "Test 2: Sending analysis_complete event"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "analysis_complete", 
      "Detail": "{\"repository\":{\"owner\":\"test-user\",\"name\":\"test-repo\",\"commit_sha\":\"abc123\",\"default_branch\":\"main\"},\"s3_files\":[\"report.md\"],\"timestamp\":\"2025-06-30T12:31:00Z\"}",
      "EventBusName": "'$BUS_NAME'"
    }
  ]' \
  --region $REGION

echo "✅ analysis_complete event sent"
echo ""

# Test 3: Send pr_created event
echo "Test 3: Sending pr_created event"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "pr_created",
      "Detail": "{\"repository\":{\"owner\":\"test-user\",\"name\":\"test-repo\",\"commit_sha\":\"abc123\",\"default_branch\":\"main\"},\"pr_number\":123,\"pr_url\":\"https://github.com/test-user/test-repo/pull/123\",\"timestamp\":\"2025-06-30T12:32:00Z\"}",
      "EventBusName": "'$BUS_NAME'"
    }
  ]' \
  --region $REGION

echo "✅ pr_created event sent"
echo ""

# Test 4: List rules to verify setup
echo "Test 4: Verifying EventBridge rules"
aws events list-rules \
  --event-bus-name $BUS_NAME \
  --region $REGION \
  --query 'Rules[].{Name:Name,State:State,Description:Description}' \
  --output table

echo ""
echo "✅ Testing complete!"
echo ""
echo "Expected results:"
echo "- All events should be accepted (no errors)"
echo "- Rules should be listed and ENABLED"
echo "- Events are queued for routing (targets needed for delivery)"
echo ""
echo "Next: Deploy Hermes Lambda to see event logging in action!"
