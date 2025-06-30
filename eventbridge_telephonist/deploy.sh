#!/bin/bash

# CodeRipple Telephonist Deployment Script
# Creates EventBridge custom bus and routing rules

set -e

echo "📞 Deploying CodeRipple Telephonist..."

# Variables
BUS_NAME="coderipple-events"
REGION="us-east-1"  # Change as needed

# 1. Create custom event bus
echo "🚌 Creating custom event bus..."
aws events create-event-bus \
  --name $BUS_NAME \
  --region $REGION \
  --tags Key=Project,Value=coderipple

echo "✅ Event bus '$BUS_NAME' created"

# 2. Create rule for Hermes (all events)
echo "📝 Creating Hermes logging rule..."
aws events put-rule \
  --name "coderipple-hermes-all-events" \
  --event-pattern '{"source":["coderipple.system"]}' \
  --state ENABLED \
  --description "Route all CodeRipple events to Hermes for logging" \
  --event-bus-name $BUS_NAME \
  --region $REGION \
  --tags Key=Project,Value=coderipple

echo "✅ Hermes logging rule created"

# 3. Create rule for Analyst (repo_ready events)
echo "🔬 Creating Analyst trigger rule..."
aws events put-rule \
  --name "coderipple-analyst-repo-ready" \
  --event-pattern '{"source":["coderipple.system"],"detail-type":["repo_ready"]}' \
  --state ENABLED \
  --description "Route repo_ready events to Analyst" \
  --event-bus-name $BUS_NAME \
  --region $REGION \
  --tags Key=Project,Value=coderipple

echo "✅ Analyst trigger rule created"

# 4. Create rule for Deliverer (analysis_complete events)
echo "🚚 Creating Deliverer trigger rule..."
aws events put-rule \
  --name "coderipple-deliverer-analysis-complete" \
  --event-pattern '{"source":["coderipple.system"],"detail-type":["analysis_complete"]}' \
  --state ENABLED \
  --description "Route analysis_complete events to Deliverer" \
  --event-bus-name $BUS_NAME \
  --region $REGION \
  --tags Key=Project,Value=coderipple

echo "✅ Deliverer trigger rule created"

echo ""
echo "🎉 Telephonist Deployment Complete!"
echo "📞 Event Bus: $BUS_NAME"
echo "🌍 Region: $REGION"
echo ""
echo "Next steps:"
echo "1. Deploy Hermes Lambda and add as target to hermes rule"
echo "2. Deploy other services and configure as targets"
echo "3. Test event routing with sample events"

# Save bus name for future reference
echo $BUS_NAME > event-bus-name.txt
echo "💾 Event bus name saved to event-bus-name.txt"
