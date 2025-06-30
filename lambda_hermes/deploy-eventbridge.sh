#!/bin/bash

# EventBridge Integration for Hermes Lambda
# Creates EventBridge rule to route CodeRipple system events to Hermes

set -e

echo "📡 Deploying EventBridge Integration for Hermes..."

# Variables
RULE_NAME="coderipple-hermes-logging"
REGION="us-east-1"
LAMBDA_FUNCTION="coderipple-hermes"

# Check if Lambda ARN exists
if [ ! -f "lambda-arn.txt" ]; then
    echo "❌ Lambda ARN not found. Run deploy.sh first."
    exit 1
fi

LAMBDA_ARN=$(cat lambda-arn.txt)

# 1. Create EventBridge rule
echo "📋 Creating EventBridge rule..."

# Event pattern to match all CodeRipple system events
cat > event-pattern.json << EOF
{
  "source": ["coderipple.system"]
}
EOF

# Create the rule
aws events put-rule \
  --name $RULE_NAME \
  --event-pattern file://event-pattern.json \
  --description "Routes all CodeRipple system events to Hermes for logging" \
  --state ENABLED \
  --region $REGION

echo "✅ EventBridge rule created"

# 2. Add Lambda target to the rule
echo "🎯 Adding Hermes Lambda as target..."

aws events put-targets \
  --rule $RULE_NAME \
  --targets "Id"="1","Arn"="$LAMBDA_ARN" \
  --region $REGION

echo "✅ Lambda target added"

# 3. Grant EventBridge permission to invoke Lambda
echo "🔐 Granting EventBridge permission to invoke Lambda..."

# Create unique statement ID
STATEMENT_ID="AllowEventBridgeInvoke-$(date +%s)"

aws lambda add-permission \
  --function-name $LAMBDA_FUNCTION \
  --statement-id $STATEMENT_ID \
  --action lambda:InvokeFunction \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$(aws sts get-caller-identity --query Account --output text):rule/$RULE_NAME" \
  --region $REGION

echo "✅ EventBridge permissions granted"

# 4. Verify the setup
echo "🔍 Verifying EventBridge integration..."

# Check rule status
RULE_STATUS=$(aws events describe-rule --name $RULE_NAME --region $REGION --query 'State' --output text)
echo "Rule Status: $RULE_STATUS"

# Check targets
TARGET_COUNT=$(aws events list-targets-by-rule --rule $RULE_NAME --region $REGION --query 'length(Targets)' --output text)
echo "Target Count: $TARGET_COUNT"

echo ""
echo "🎉 EventBridge Integration Complete!"
echo "📋 Rule Name: $RULE_NAME"
echo "🎯 Target: $LAMBDA_FUNCTION"
echo "📡 Event Pattern: source = 'coderipple.system'"
echo ""
echo "Next steps:"
echo "1. Test event routing with test-eventbridge.sh"
echo "2. Verify events appear in Cabinet website"
echo "3. Complete end-to-end integration testing"

# Save rule ARN for testing
RULE_ARN="arn:aws:events:$REGION:$(aws sts get-caller-identity --query Account --output text):rule/$RULE_NAME"
echo $RULE_ARN > eventbridge-rule-arn.txt
echo "💾 Rule ARN saved to eventbridge-rule-arn.txt"

# Cleanup
rm -f event-pattern.json
