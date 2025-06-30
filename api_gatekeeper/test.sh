#!/bin/bash

# Test script for CodeRipple API Gatekeeper

set -e

# Check if API ID exists
if [ ! -f "api-id.txt" ]; then
    echo "❌ API ID not found. Run deploy.sh first."
    exit 1
fi

API_ID=$(cat api-id.txt)
REGION="us-east-1"  # Change as needed
STAGE_NAME="prod"
WEBHOOK_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE_NAME/webhook"

echo "🧪 Testing CodeRipple API Gatekeeper..."
echo "📍 URL: $WEBHOOK_URL"
echo ""

# Test 1: Basic POST request
echo "Test 1: Basic POST request"
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}' \
  $WEBHOOK_URL

echo -e "\n"

# Test 2: GitHub-like webhook payload
echo "Test 2: GitHub-like webhook payload"
curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -d '{
    "repository": {
      "name": "test-repo",
      "owner": {"login": "test-user"},
      "default_branch": "main"
    },
    "head_commit": {
      "id": "abc123def456"
    }
  }' \
  $WEBHOOK_URL

echo -e "\n"

# Test 3: GET request (should fail)
echo "Test 3: GET request (should return 403)"
curl -X GET $WEBHOOK_URL || echo " (Expected failure)"

echo -e "\n✅ Testing complete!"
echo ""
echo "Expected results:"
echo "- Tests 1 & 2: Should return 200 with success message"
echo "- Test 3: Should return 403 (Method Not Allowed)"
