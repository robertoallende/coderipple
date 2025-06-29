#!/bin/bash
# deploy_helloworld_function.sh

set -e

FUNCTION_NAME="helloworld-debug"
REGION="us-east-1"
ROLE_ARN="arn:aws:iam::741448943849:role/coderipple-lambda-execution-role"

echo "Deploying Hello World Lambda function..."

# Get layer ARN from previous deployment
if [ -f layer_arn.txt ]; then
    LAYER_ARN=$(cat layer_arn.txt)
    echo "Using layer ARN: $LAYER_ARN"
else
    echo "Error: layer_arn.txt not found. Please run deploy_helloworld_layer.sh first."
    exit 1
fi

# Create or update function
echo "Creating/updating Lambda function..."
aws lambda create-function \
  --function-name "$FUNCTION_NAME" \
  --runtime python3.12 \
  --role "$ROLE_ARN" \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://helloworld-function.zip \
  --layers "$LAYER_ARN" \
  --timeout 30 \
  --memory-size 512 \
  --architectures x86_64 \
  --region "$REGION" \
  --description "Hello World debugging function for CI/CD testing" \
  2>/dev/null || \
{
    echo "Function exists, updating code..."
    aws lambda update-function-code \
      --function-name "$FUNCTION_NAME" \
      --zip-file fileb://helloworld-function.zip \
      --region "$REGION"
    
    echo "Waiting for function update to complete..."
    aws lambda wait function-updated \
      --function-name "$FUNCTION_NAME" \
      --region "$REGION"
    
    echo "Updating function configuration..."
    aws lambda update-function-configuration \
      --function-name "$FUNCTION_NAME" \
      --layers "$LAYER_ARN" \
      --region "$REGION"
}

echo "Hello World Lambda function deployed successfully!"
echo "Function ARN: arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):function:$FUNCTION_NAME"
