#!/bin/bash

# Showroom Deployment Script with Shared Assets
set -e

# Configuration
BUCKET_NAME="coderipple-showroom"
REGION="us-east-1"
BUILD_DIR="./build"
SHARED_ASSETS="../shared-assets"

echo "🚀 Deploying Showroom with shared assets..."

# 1. Clean and create build directory
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/assets/{css,images,fonts}

# 2. Copy shared assets
echo "📦 Copying shared assets..."
cp -r $SHARED_ASSETS/css/* $BUILD_DIR/assets/css/
cp -r $SHARED_ASSETS/images/* $BUILD_DIR/assets/images/
cp -r $SHARED_ASSETS/fonts/* $BUILD_DIR/assets/fonts/

# 3. Generate index.html from template
echo "🔧 Generating index.html from template..."
$SHARED_ASSETS/generate-html.sh showroom $BUILD_DIR/index.html

# 4. Copy showroom-specific content
echo "📄 Copying showroom content..."
cp content/*.md $BUILD_DIR/

# 5. Create S3 bucket if it doesn't exist
echo "🪣 Ensuring S3 bucket exists..."
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# 6. Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document index.html --error-document error.html --region $REGION

# 7. Set bucket policy for public read access
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

aws s3api put-public-access-block --bucket $BUCKET_NAME --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false --region $REGION
aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://bucket-policy.json --region $REGION

# 8. Deploy to S3
echo "☁️ Deploying to S3..."
aws s3 sync $BUILD_DIR/ s3://$BUCKET_NAME/ --region $REGION --delete

# 9. Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo $WEBSITE_URL > website-url.txt

# 10. Cleanup
rm -f bucket-policy.json

echo "✅ Showroom deployment complete!"
echo "🌐 Website URL: $WEBSITE_URL"
echo "📁 Bucket: s3://$BUCKET_NAME"
echo "🔗 Analysis delivery ready for Deliverer integration"
