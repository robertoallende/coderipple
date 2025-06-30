#!/bin/bash

# Test script for EventBridge integration with Hermes
# Sends test events through EventBridge to verify end-to-end logging

set -e

REGION="us-east-1"
CABINET_URL="http://coderipple-cabinet.s3-website-us-east-1.amazonaws.com"

echo "🧪 Testing EventBridge Integration with Hermes..."
echo "🌐 Cabinet URL: $CABINET_URL"
echo ""

# Test 1: Receptionist repo_ready event
echo "Test 1: Sending Receptionist repo_ready event via EventBridge"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "repo_ready",
      "Detail": "{\"component\":\"Receptionist\",\"repository\":{\"owner\":\"test-org\",\"name\":\"sample-repo\",\"commit_sha\":\"def456\",\"default_branch\":\"main\"},\"s3_location\":\"bucket/repos/test-org/sample-repo/def456/\",\"timestamp\":\"2025-06-30T18:00:00Z\"}"
    }
  ]' \
  --region $REGION

echo "✅ Event sent via EventBridge"
echo "⏳ Waiting 5 seconds for processing..."
sleep 5

# Test 2: Analyst analysis_complete event
echo ""
echo "Test 2: Sending Analyst analysis_complete event via EventBridge"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "analysis_complete",
      "Detail": "{\"component\":\"Analyst\",\"repository\":{\"owner\":\"test-org\",\"name\":\"sample-repo\",\"commit_sha\":\"def456\",\"default_branch\":\"main\"},\"s3_files\":[\"analysis/report.md\",\"analysis/metrics.json\",\"analysis/summary.txt\"],\"timestamp\":\"2025-06-30T18:01:00Z\"}"
    }
  ]' \
  --region $REGION

echo "✅ Event sent via EventBridge"
echo "⏳ Waiting 5 seconds for processing..."
sleep 5

# Test 3: Deliverer pr_created event
echo ""
echo "Test 3: Sending Deliverer pr_created event via EventBridge"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "pr_created",
      "Detail": "{\"component\":\"Deliverer\",\"repository\":{\"owner\":\"test-org\",\"name\":\"sample-repo\",\"commit_sha\":\"def456\",\"default_branch\":\"main\"},\"pr_number\":42,\"pr_url\":\"https://github.com/test-org/sample-repo/pull/42\",\"timestamp\":\"2025-06-30T18:02:00Z\"}"
    }
  ]' \
  --region $REGION

echo "✅ Event sent via EventBridge"
echo "⏳ Waiting 5 seconds for processing..."
sleep 5

# Test 4: Error event (malformed)
echo ""
echo "Test 4: Sending malformed event to test error handling"
aws events put-events \
  --entries '[
    {
      "Source": "coderipple.system",
      "DetailType": "unknown_event",
      "Detail": "{\"malformed\":\"data\",\"missing\":\"component field\",\"timestamp\":\"2025-06-30T18:03:00Z\"}"
    }
  ]' \
  --region $REGION

echo "✅ Malformed event sent via EventBridge"
echo "⏳ Waiting 5 seconds for processing..."
sleep 5

# Verify results
echo ""
echo "📊 Checking Cabinet for logged events..."
echo "Fetching current README.md content:"
echo "----------------------------------------"
curl -s "$CABINET_URL/README.md"
echo ""
echo "----------------------------------------"

echo ""
echo "🎉 EventBridge Integration Testing Complete!"
echo ""
echo "Expected results:"
echo "- 4 new events should appear in the Cabinet table"
echo "- Events should show: Receptionist, Analyst, Deliverer, and Error entries"
echo "- All events should have proper timestamps and details"
echo ""
echo "🌐 View live results: $CABINET_URL"
echo ""
echo "If events don't appear:"
echo "1. Check CloudWatch logs: /aws/lambda/coderipple-hermes"
echo "2. Verify EventBridge rule is enabled"
echo "3. Confirm Lambda permissions are correct"
