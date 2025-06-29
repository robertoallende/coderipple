#!/bin/bash
# deploy_helloworld_layer.sh

set -e

LAYER_NAME="helloworld-dependencies"
REGION="us-east-1"

echo "Deploying Hello World dependencies layer..."

# Upload layer
LAYER_VERSION=$(aws lambda publish-layer-version \
  --layer-name "$LAYER_NAME" \
  --description "Hello World debugging layer with Strands dependencies (platform-targeted)" \
  --zip-file fileb://helloworld-dependencies.zip \
  --compatible-runtimes python3.12 \
  --compatible-architectures x86_64 \
  --region "$REGION" \
  --query 'Version' \
  --output text)

echo "Hello World dependencies layer deployed successfully!"
echo "Layer ARN: arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):layer:$LAYER_NAME:$LAYER_VERSION"
echo "Layer Version: $LAYER_VERSION"

# Save layer ARN for function deployment
echo "arn:aws:lambda:$REGION:$(aws sts get-caller-identity --query Account --output text):layer:$LAYER_NAME:$LAYER_VERSION" > layer_arn.txt
