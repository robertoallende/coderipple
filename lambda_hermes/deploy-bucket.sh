#!/bin/bash

# Inventory S3 Bucket Deployment Script
# Creates S3 bucket with public website hosting for Docsify

set -e

echo "🗄️ Deploying CodeRipple Inventory S3 Bucket..."

# Variables
BUCKET_NAME="coderipple-cabinet"
REGION="us-east-1"

# 1. Create S3 bucket
echo "📦 Creating S3 bucket..."
if [ "$REGION" = "us-east-1" ]; then
    # us-east-1 doesn't need LocationConstraint
    aws s3api create-bucket \
      --bucket $BUCKET_NAME \
      --region $REGION 2>/dev/null || echo "Bucket may already exist"
else
    # Other regions need LocationConstraint
    aws s3api create-bucket \
      --bucket $BUCKET_NAME \
      --region $REGION \
      --create-bucket-configuration LocationConstraint=$REGION 2>/dev/null || echo "Bucket may already exist"
fi

echo "✅ S3 bucket created/verified"

# 2. Enable static website hosting
echo "🌐 Configuring static website hosting..."
aws s3api put-bucket-website \
  --bucket $BUCKET_NAME \
  --website-configuration '{
    "IndexDocument": {"Suffix": "index.html"},
    "ErrorDocument": {"Key": "index.html"}
  }' \
  --region $REGION

echo "✅ Static website hosting enabled"

# 3. Configure public read access
echo "🔓 Configuring public read access..."

# Remove public access block
aws s3api delete-public-access-block \
  --bucket $BUCKET_NAME \
  --region $REGION

# Create bucket policy for public read access
cat > bucket-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
  --bucket $BUCKET_NAME \
  --policy file://bucket-policy.json \
  --region $REGION

echo "✅ Public read access configured"

# 4. Add bucket tagging
echo "🏷️ Adding bucket tags..."
aws s3api put-bucket-tagging \
  --bucket $BUCKET_NAME \
  --tagging 'TagSet=[{Key=Project,Value=coderipple}]' \
  --region $REGION

echo "✅ Bucket tagged"

# 5. Upload initial files
echo "📄 Uploading initial files..."

# Upload index.html
aws s3 cp index.html s3://$BUCKET_NAME/index.html \
  --content-type "text/html" \
  --region $REGION

# Upload initial README.md
aws s3 cp initial-readme.md s3://$BUCKET_NAME/README.md \
  --content-type "text/markdown" \
  --region $REGION

echo "✅ Initial files uploaded"

echo ""
echo "🎉 Cabinet S3 Bucket Deployment Complete!"
echo "🗄️ Bucket Name: $BUCKET_NAME"
echo "🌐 Website URL: $WEBSITE_URL"
echo "📍 Region: $REGION"
echo ""
echo "Next steps:"
echo "1. Test website access with test-bucket.sh"
echo "2. Re-run Hermes Lambda test to verify S3 writes work"
echo "3. Configure EventBridge integration (Subunit 3.3)"

# Save website URL for testing
echo $WEBSITE_URL > website-url.txt
echo "💾 Website URL saved to website-url.txt"

# Cleanup
rm -f bucket-policy.json
