#!/bin/bash

# Deliverer Lambda Deployment Script
# Unit 7: Analysis results packaging and Showroom delivery

set -e

# Configuration
FUNCTION_NAME="coderipple-deliverer"
REGION="us-east-1"
ROLE_NAME="coderipple-deliverer-role"

echo "🚀 Deploying Deliverer Lambda for analysis packaging and delivery..."

# 1. Create IAM role for Deliverer
echo "👤 Creating IAM role..."
cat > deliverer-trust-policy.json << EOF
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

aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://deliverer-trust-policy.json \
  --region $REGION 2>/dev/null || echo "Role already exists"

# 2. Create IAM policy for Deliverer permissions
echo "🔐 Creating IAM policy..."
cat > deliverer-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::coderipple-drawer",
        "arn:aws:s3:::coderipple-drawer/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl",
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::coderipple-showroom",
        "arn:aws:s3:::coderipple-showroom/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "arn:aws:events:*:*:event-bus/coderipple-events"
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name "DelivererPolicy" \
  --policy-document file://deliverer-policy.json \
  --region $REGION

# 3. Package Lambda function
echo "📦 Packaging Lambda function..."
rm -rf python/
mkdir -p python/

# Install dependencies
python3 -m pip install -r requirements.txt -t python/

# Create deployment package
zip -r deliverer-lambda.zip lambda_function.py python/

# 4. Create or update Lambda function
echo "⚡ Creating Lambda function..."

ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text --region $REGION)

# Wait for role to be ready
echo "⏳ Waiting for IAM role to be ready..."
sleep 10

aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.12 \
  --role $ROLE_ARN \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://deliverer-lambda.zip \
  --timeout 300 \
  --memory-size 1024 \
  --ephemeral-storage Size=2048 \
  --region $REGION 2>/dev/null || {
    echo "Function exists, updating..."
    aws lambda update-function-code \
      --function-name $FUNCTION_NAME \
      --zip-file fileb://deliverer-lambda.zip \
      --region $REGION
  }

# 5. Set environment variables
echo "🔧 Setting environment variables..."
aws lambda update-function-configuration \
  --function-name $FUNCTION_NAME \
  --environment Variables='{
    "DRAWER_BUCKET": "coderipple-drawer",
    "SHOWROOM_BUCKET": "coderipple-showroom",
    "EVENT_BUS_NAME": "coderipple-events"
  }' \
  --region $REGION

# 6. Create EventBridge rule for analysis_ready events
echo "📡 Creating EventBridge rule..."
aws events put-rule \
  --name "coderipple-deliverer-trigger" \
  --event-pattern '{
    "source": ["coderipple.analyst"],
    "detail-type": ["Analysis Complete"]
  }' \
  --event-bus-name "coderipple-events" \
  --region $REGION

# 7. Add Lambda permission for EventBridge
echo "🔗 Adding EventBridge permission..."
aws lambda add-permission \
  --function-name $FUNCTION_NAME \
  --statement-id "allow-eventbridge" \
  --action "lambda:InvokeFunction" \
  --principal events.amazonaws.com \
  --source-arn "arn:aws:events:$REGION:$(aws sts get-caller-identity --query Account --output text):rule/coderipple-events/coderipple-deliverer-trigger" \
  --region $REGION 2>/dev/null || echo "Permission already exists"

# 8. Add EventBridge target
echo "🎯 Adding EventBridge target..."
LAMBDA_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --query 'Configuration.FunctionArn' --output text --region $REGION)

aws events put-targets \
  --rule "coderipple-deliverer-trigger" \
  --event-bus-name "coderipple-events" \
  --targets "Id"="1","Arn"="$LAMBDA_ARN" \
  --region $REGION

# 9. Save Lambda ARN
echo $LAMBDA_ARN > lambda-arn.txt

# 10. Cleanup
rm -f deliverer-trust-policy.json deliverer-policy.json

echo "✅ Deliverer Lambda deployment complete!"
echo "📋 Function: $FUNCTION_NAME"
echo "🔗 ARN: $LAMBDA_ARN"
echo "📡 EventBridge: Listening for analysis_ready events"
echo "📦 Ready to package and deliver analysis results to Showroom!"
