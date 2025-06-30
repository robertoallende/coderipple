#!/bin/bash

# Analyst Lambda Deployment Script with Layer Support
# Updated for Unit 5.7: Lambda Layers Implementation

set -e

# Configuration
FUNCTION_NAME="coderipple-analyst"
ROLE_NAME="coderipple-analyst-role"
REGION="us-east-1"
DRAWER_BUCKET="coderipple-drawer"

echo "🚀 Deploying Analyst Lambda with Strands Layer..."

# 1. Verify layer exists
if [ ! -f "layer-arn.txt" ]; then
    echo "❌ Layer not found. Run ./deploy-layer-s3.sh first"
    exit 1
fi

LAYER_ARN=$(cat layer-arn.txt)
echo "📦 Using layer: $LAYER_ARN"

# 2. Create IAM role for Lambda
echo "📋 Creating IAM role..."

# Trust policy for Lambda
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create role (ignore if exists)
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=Project,Value=coderipple \
  --region $REGION 2>/dev/null || echo "Role already exists"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --region $REGION

echo "✅ IAM role configured"

# 3. Create Lambda-specific policies
echo "📋 Creating Lambda policies..."

# S3 Drawer access policy
cat > drawer-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:HeadObject"
      ],
      "Resource": "arn:aws:s3:::$DRAWER_BUCKET/repos/*/workingcopy.zip"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::$DRAWER_BUCKET/repos/*/analysis/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::$DRAWER_BUCKET",
      "Condition": {
        "StringLike": {
          "s3:prefix": "repos/*"
        }
      }
    }
  ]
}
EOF

# EventBridge policy
cat > eventbridge-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "*"
    }
  ]
}
EOF

# Bedrock policy for Strands analysis
cat > bedrock-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
      ]
    }
  ]
}
EOF

# Create and attach policies
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name DrawerAccess \
  --policy-document file://drawer-policy.json \
  --region $REGION

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name EventBridgeAccess \
  --policy-document file://eventbridge-policy.json \
  --region $REGION

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name BedrockAccess \
  --policy-document file://bedrock-policy.json \
  --region $REGION

echo "✅ Lambda policies attached"

# 4. Create lightweight deployment package (code only, no dependencies)
echo "📦 Creating lightweight deployment package..."

# Remove any existing python dependencies directory
rm -rf python/

# Create deployment package with only code files
zip -r analyst-lambda.zip \
  lambda_function.py \
  magic_mirror.py \
  config.py \
  git_tools.py \
  file_system_tools.py \
  generic_tools.py \
  prompts.py \
  better_prompts.py \
  context.txt

# Check package size
PACKAGE_SIZE=$(du -sh analyst-lambda.zip | cut -f1)
echo "✅ Lightweight deployment package created: $PACKAGE_SIZE"

# 5. Create/Update Lambda function with layer
echo "🚀 Creating Lambda function with layer..."

# Wait for IAM role to be ready
echo "⏳ Waiting for IAM role to be ready..."
sleep 10

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text --region $REGION)

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION >/dev/null 2>&1; then
  echo "Function exists, updating code and configuration..."
  
  # Update function code
  aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --zip-file fileb://analyst-lambda.zip \
    --region $REGION
  
  # Update configuration with layer
  aws lambda update-function-configuration \
    --function-name $FUNCTION_NAME \
    --layers $LAYER_ARN \
    --timeout 900 \
    --memory-size 1024 \
    --ephemeral-storage Size=5120 \
    --environment Variables="{DRAWER_BUCKET=$DRAWER_BUCKET,MODEL_STRING=us.anthropic.claude-3-5-sonnet-20241022-v2:0,AWS_REGION=us-east-1,LOG_LEVEL=INFO}" \
    --region $REGION
else
  echo "Creating new function with layer..."
  aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.12 \
    --role $ROLE_ARN \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://analyst-lambda.zip \
    --timeout 900 \
    --memory-size 1024 \
    --ephemeral-storage Size=5120 \
    --layers $LAYER_ARN \
    --environment Variables="{DRAWER_BUCKET=$DRAWER_BUCKET,MODEL_STRING=us.anthropic.claude-3-5-sonnet-20241022-v2:0,AWS_REGION=us-east-1,LOG_LEVEL=INFO}" \
    --tags Project=coderipple \
    --region $REGION
fi

echo "✅ Lambda function deployed with layer"

# 6. Create EventBridge rule for repo_ready events
echo "📡 Creating EventBridge rule..."

# Create event pattern for repo_ready events
cat > event-pattern.json << EOF
{
  "source": ["coderipple.system"],
  "detail-type": ["repo_ready"]
}
EOF

# Create EventBridge rule
aws events put-rule \
  --name "coderipple-analyst-trigger" \
  --event-pattern file://event-pattern.json \
  --state ENABLED \
  --description "Trigger Analyst Lambda on repo_ready events" \
  --tags Key=Project,Value=coderipple \
  --region $REGION

# Add Lambda as target
LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text --region $REGION)

aws events put-targets \
  --rule "coderipple-analyst-trigger" \
  --targets "Id"="1","Arn"="$LAMBDA_ARN" \
  --region $REGION

# Add permission for EventBridge to invoke Lambda
aws lambda add-permission \
  --function-name $FUNCTION_NAME \
  --statement-id "allow-eventbridge" \
  --action "lambda:InvokeFunction" \
  --principal "events.amazonaws.com" \
  --source-arn "arn:aws:events:$REGION:$(aws sts get-caller-identity --query Account --output text):rule/coderipple-analyst-trigger" \
  --region $REGION 2>/dev/null || echo "Permission already exists"

echo "✅ EventBridge rule configured"

# Save Lambda ARN for reference
echo $LAMBDA_ARN > lambda-arn.txt

echo "🎉 Analyst Lambda with Strands Layer deployment complete!"
echo "📦 Function: $LAMBDA_ARN"
echo "🔗 Layer: $LAYER_ARN"
echo "📡 EventBridge Rule: coderipple-analyst-trigger"
echo "✅ Ready for real AI-powered code analysis!"

# Display deployment summary
echo ""
echo "📊 Deployment Summary:"
echo "  • Function Package: $PACKAGE_SIZE (lightweight, code only)"
echo "  • Dependencies: 58MB (via Lambda Layer)"
echo "  • Total Capability: Full Strands + Claude 3.5 Sonnet"
echo "  • Memory: 1GB"
echo "  • Timeout: 15 minutes"
echo "  • Storage: 5GB ephemeral"
