#!/bin/bash
set -e

LAYER_NAME="coderipple-strands-layer"
REGION="us-east-1"
S3_BUCKET="coderipple-lambda-layers-1751191178"
S3_KEY="strands-layer-$(date +%Y%m%d-%H%M%S).zip"

echo "🚀 Deploying Strands Layer via S3..."

# Clean and create layer directory
rm -rf layer strands-layer.zip
mkdir -p layer/python

# Install dependencies with platform targeting for Lambda
echo "📦 Installing dependencies for Lambda x86_64..."
python3 -m pip install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target layer/python \
  strands-agents>=0.1.0 \
  strands-agents-tools>=0.1.0 \
  boto3>=1.26.0 \
  botocore>=1.29.0

# Package layer
echo "📦 Creating layer package..."
cd layer && zip -r ../strands-layer.zip python/
cd ..

# Check layer size
LAYER_SIZE=$(du -sh strands-layer.zip | cut -f1)
echo "📏 Layer package size: $LAYER_SIZE"

# Upload to S3
echo "☁️ Uploading layer to S3..."
aws s3 cp strands-layer.zip s3://$S3_BUCKET/$S3_KEY --region $REGION

# Publish layer from S3
echo "🔗 Publishing layer from S3..."
LAYER_ARN=$(aws lambda publish-layer-version \
  --layer-name $LAYER_NAME \
  --content S3Bucket=$S3_BUCKET,S3Key=$S3_KEY \
  --compatible-runtimes python3.12 \
  --region $REGION \
  --description "Strands dependencies for CodeRipple analysis (deployed via S3)" \
  --query 'LayerVersionArn' \
  --output text)

echo $LAYER_ARN > layer-arn.txt
echo "✅ Layer deployed: $LAYER_ARN"

# Cleanup local files
rm -rf layer strands-layer.zip

# Optional: Clean up S3 file after successful deployment
echo "🧹 Cleaning up S3 temporary file..."
aws s3 rm s3://$S3_BUCKET/$S3_KEY --region $REGION

echo "🎉 Layer deployment complete!"
echo "📝 Layer ARN saved to layer-arn.txt"
echo "📦 S3 temporary file cleaned up"
