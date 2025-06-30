#!/bin/bash

# Showroom S3 Bucket Deployment Script
# Unit 6: Public analysis delivery with Docsify website

set -e

# Configuration
BUCKET_NAME="coderipple-showroom"
REGION="us-east-1"

echo "🚀 Deploying Showroom S3 bucket for public analysis delivery..."

# 1. Create S3 bucket
echo "📦 Creating S3 bucket..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# 2. Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html --region $REGION

# 3. Set bucket policy for public read access
echo "🔓 Setting public read access policy..."
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

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json --region $REGION

# 4. Upload Docsify website files
echo "📄 Uploading Docsify website..."
aws s3 sync ./website/ s3://$BUCKET_NAME/ --region $REGION --delete

# 5. Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo $WEBSITE_URL > website-url.txt

echo "✅ Showroom deployment complete!"
echo "🌐 Website URL: $WEBSITE_URL"
echo "📁 Bucket: s3://$BUCKET_NAME"
echo "🔗 Analysis delivery ready for Deliverer integration"
