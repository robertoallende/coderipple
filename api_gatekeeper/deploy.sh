#!/bin/bash

# CodeRipple API Gatekeeper Deployment Script
# Creates API Gateway REST API for GitHub webhook handling

set -e

echo "🚀 Deploying CodeRipple API Gatekeeper..."

# Variables
API_NAME="coderipple-gatekeeper"
REGION="us-east-1"  # Change as needed
STAGE_NAME="prod"

# 1. Create REST API
echo "📡 Creating REST API..."
API_ID=$(aws apigateway create-rest-api \
  --cli-input-json file://api-config.json \
  --region $REGION \
  --query 'id' \
  --output text)

echo "✅ API created with ID: $API_ID"

# 2. Get root resource ID
echo "🔍 Getting root resource..."
ROOT_RESOURCE_ID=$(aws apigateway get-resources \
  --rest-api-id $API_ID \
  --region $REGION \
  --query 'items[0].id' \
  --output text)

echo "✅ Root resource ID: $ROOT_RESOURCE_ID"

# 3. Create /webhook resource
echo "📝 Creating /webhook resource..."
WEBHOOK_RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_RESOURCE_ID \
  --path-part "webhook" \
  --region $REGION \
  --query 'id' \
  --output text)

echo "✅ Webhook resource created: $WEBHOOK_RESOURCE_ID"

# 4. Create POST method
echo "🔧 Creating POST method..."
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $WEBHOOK_RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE \
  --region $REGION

echo "✅ POST method created"

# 5. Create method response
echo "📤 Creating method response..."
aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $WEBHOOK_RESOURCE_ID \
  --http-method POST \
  --status-code 200 \
  --region $REGION

echo "✅ Method response created"

# 6. Create integration (placeholder - will be updated when Lambda is ready)
echo "🔗 Creating mock integration (temporary)..."
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $WEBHOOK_RESOURCE_ID \
  --http-method POST \
  --type MOCK \
  --integration-http-method POST \
  --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
  --region $REGION

echo "✅ Mock integration created"

# 7. Create integration response
echo "📥 Creating integration response..."
aws apigateway put-integration-response \
  --rest-api-id $API_ID \
  --resource-id $WEBHOOK_RESOURCE_ID \
  --http-method POST \
  --status-code 200 \
  --response-templates '{"application/json": "{\"message\": \"Webhook received - CodeRipple Gatekeeper\"}"}' \
  --region $REGION

echo "✅ Integration response created"

# 8. Deploy API
echo "🚀 Deploying to $STAGE_NAME stage..."
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name $STAGE_NAME \
  --stage-description "Production stage for CodeRipple webhook" \
  --description "Initial deployment" \
  --region $REGION

echo "✅ API deployed successfully!"

# 9. Output webhook URL
WEBHOOK_URL="https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE_NAME/webhook"
echo ""
echo "🎉 Deployment Complete!"
echo "📍 Webhook URL: $WEBHOOK_URL"
echo ""
echo "Next steps:"
echo "1. Test the endpoint: curl -X POST $WEBHOOK_URL"
echo "2. Configure GitHub webhook with this URL"
echo "3. Update integration to point to Receptionist Lambda when ready"

# Save API ID for future reference
echo $API_ID > api-id.txt
echo "💾 API ID saved to api-id.txt"
