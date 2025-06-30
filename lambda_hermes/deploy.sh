#!/bin/bash

# Hermes Lambda Deployment Script
# Creates Lambda function for event logging

set -e

echo "📋 Deploying Hermes The Bureaucrat Lambda..."

# Variables
FUNCTION_NAME="coderipple-hermes"
REGION="us-east-1"  # Change as needed
INVENTORY_BUCKET="coderipple-cabinet"

# 1. Create deployment package
echo "📦 Creating deployment package..."
rm -f hermes-lambda.zip

# Install dependencies with platform targeting for Lambda
pip3 install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target python \
  -r requirements.txt

# Create zip package
zip -r hermes-lambda.zip lambda_function.py python/

echo "✅ Deployment package created"

# 2. Create IAM role for Lambda
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
  --role-name coderipple-hermes-role \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=Project,Value=coderipple \
  --region $REGION || echo "Role may already exist"

# Attach basic Lambda execution policy
aws iam attach-role-policy \
  --role-name coderipple-hermes-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole \
  --region $REGION

# Create S3 access policy
cat > s3-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::$INVENTORY_BUCKET/*"
    }
  ]
}
EOF

# Create and attach S3 policy
aws iam put-role-policy \
  --role-name coderipple-hermes-role \
  --policy-name HermesS3Access \
  --policy-document file://s3-policy.json \
  --region $REGION

echo "✅ IAM role configured"

# Wait for role propagation
echo "⏳ Waiting for IAM role propagation..."
sleep 10

# 3. Get account ID for role ARN
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ROLE_ARN="arn:aws:iam::$ACCOUNT_ID:role/coderipple-hermes-role"

# 4. Create Lambda function
echo "🚀 Creating Lambda function..."
aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.12 \
  --role $ROLE_ARN \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://hermes-lambda.zip \
  --timeout 30 \
  --memory-size 256 \
  --environment Variables="{INVENTORY_BUCKET=$INVENTORY_BUCKET}" \
  --tags Project=coderipple \
  --region $REGION

echo "✅ Lambda function created"

# 5. Get Lambda function ARN
LAMBDA_ARN=$(aws lambda get-function \
  --function-name $FUNCTION_NAME \
  --region $REGION \
  --query 'Configuration.FunctionArn' \
  --output text)

echo ""
echo "🎉 Hermes Lambda Deployment Complete!"
echo "📋 Function Name: $FUNCTION_NAME"
echo "🔗 Function ARN: $LAMBDA_ARN"
echo "🗄️ Inventory Bucket: $INVENTORY_BUCKET"
echo ""
echo "Next steps:"
echo "1. Deploy Inventory S3 bucket (Subunit 3.2)"
echo "2. Configure EventBridge target (Subunit 3.3)"
echo "3. Test end-to-end event logging"

# Save function ARN for future reference
echo $LAMBDA_ARN > lambda-arn.txt
echo "💾 Lambda ARN saved to lambda-arn.txt"

# Cleanup
rm -f trust-policy.json s3-policy.json hermes-lambda.zip
rm -rf python/
