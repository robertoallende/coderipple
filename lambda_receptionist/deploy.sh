#!/bin/bash

# Receptionist Lambda Deployment
# Creates Lambda function for GitHub webhook processing and repository cloning

set -e

echo "👋 Deploying Receptionist Lambda..."

# Variables
FUNCTION_NAME="coderipple-receptionist"
ROLE_NAME="coderipple-receptionist-role"
REGION="us-east-1"
DRAWER_BUCKET="coderipple-drawer"

# 1. Create IAM role for Lambda
echo "🔐 Creating IAM role..."

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

# Create role
aws iam create-role \
  --role-name $ROLE_NAME \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=Project,Value=coderipple Key=Component,Value=receptionist 2>/dev/null || echo "Role already exists"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name $ROLE_NAME \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo "✅ IAM role configured"

# 2. Create Lambda-specific policies
echo "📋 Creating Lambda policies..."

# Drawer S3 access policy
cat > drawer-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::$DRAWER_BUCKET/repos/*/workingcopy/*",
        "arn:aws:s3:::$DRAWER_BUCKET/repos/*/repohistory/*"
      ]
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

# EventBridge publish policy
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

# Attach policies to role
aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name ReceptionistDrawerAccess \
  --policy-document file://drawer-policy.json

aws iam put-role-policy \
  --role-name $ROLE_NAME \
  --policy-name ReceptionistEventBridgeAccess \
  --policy-document file://eventbridge-policy.json

echo "✅ Lambda policies attached"

# 3. Install dependencies
echo "📦 Installing dependencies..."
rm -rf python/
pip3 install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target python \
  -r requirements.txt

echo "✅ Dependencies installed"

# 4. Create deployment package
echo "📦 Creating deployment package..."
rm -f receptionist-lambda.zip
zip -r receptionist-lambda.zip lambda_function.py python/

echo "✅ Deployment package created"

# 5. Create Lambda function
echo "🚀 Creating Lambda function..."

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

# Wait for role to be ready
echo "⏳ Waiting for IAM role to be ready..."
sleep 10

# Create Lambda function
aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.12 \
  --role $ROLE_ARN \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://receptionist-lambda.zip \
  --timeout 300 \
  --memory-size 1024 \
  --ephemeral-storage Size=5120 \
  --environment Variables='{"DRAWER_BUCKET":"'$DRAWER_BUCKET'","GITHUB_WEBHOOK_SECRET":""}' \
  --tags Project=coderipple,Component=receptionist \
  --region $REGION 2>/dev/null || echo "Function already exists, updating..."

# Update function if it already exists
aws lambda update-function-code \
  --function-name $FUNCTION_NAME \
  --zip-file fileb://receptionist-lambda.zip \
  --region $REGION 2>/dev/null || echo "Function created successfully"

# Update configuration
aws lambda update-function-configuration \
  --function-name $FUNCTION_NAME \
  --timeout 300 \
  --memory-size 1024 \
  --ephemeral-storage Size=5120 \
  --environment file://env-vars.json \
  --region $REGION

echo "✅ Lambda function deployed"

# 6. Get function details
echo "📋 Getting function details..."
FUNCTION_ARN=$(aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --query 'Configuration.FunctionArn' --output text)

echo "✅ Function ARN: $FUNCTION_ARN"

# 7. Test function
echo "🧪 Testing Lambda function..."
echo '{"body": "{\"repository\":{\"owner\":{\"login\":\"test-user\"},\"name\":\"test-repo\",\"default_branch\":\"main\"},\"head_commit\":{\"id\":\"abc123\"}}"}' > test-payload.json

aws lambda invoke \
  --function-name $FUNCTION_NAME \
  --payload file://test-payload.json \
  --region $REGION \
  response.json

echo "Test response:"
cat response.json
echo ""

echo ""
echo "🎉 Receptionist Lambda Deployment Complete!"
echo "🚀 Function Name: $FUNCTION_NAME"
echo "📍 Region: $REGION"
echo "💾 Memory: 1GB"
echo "💿 Storage: 5GB ephemeral"
echo "⏱️ Timeout: 5 minutes"
echo "🗄️ Drawer Bucket: $DRAWER_BUCKET"
echo ""
echo "Next steps:"
echo "1. Connect to API Gateway webhook endpoint"
echo "2. Test with real GitHub webhook"
echo "3. Verify EventBridge events reach Hermes"
echo "4. Check repository files in Drawer S3 bucket"

# Save function ARN for integration
echo $FUNCTION_ARN > lambda-arn.txt
echo "💾 Function ARN saved to lambda-arn.txt"

# Cleanup
rm -f trust-policy.json drawer-policy.json eventbridge-policy.json test-payload.json
