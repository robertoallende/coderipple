#!/bin/bash

# Cabinet Deployment Script with Shared Assets
# Preserves existing Hermes functionality while adding CodeRipple styling
set -e

# Configuration
BUCKET_NAME="coderipple-cabinet"
REGION="us-east-1"
BUILD_DIR="./build"
SHARED_ASSETS="../shared-assets"

echo "🚀 Deploying Cabinet with shared assets (preserving Hermes functionality)..."

# 1. Clean and create build directory
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR/assets/{css,images,fonts}

# 2. Copy shared assets
echo "📦 Copying shared assets..."
cp -r $SHARED_ASSETS/css/* $BUILD_DIR/assets/css/
cp -r $SHARED_ASSETS/images/* $BUILD_DIR/assets/images/
cp -r $SHARED_ASSETS/fonts/* $BUILD_DIR/assets/fonts/

# 3. Generate index.html from template (Cabinet configuration)
echo "🔧 Generating index.html from template..."
$SHARED_ASSETS/generate-html.sh cabinet $BUILD_DIR/index.html

# 4. Copy cabinet-specific content (preserve existing README.md)
echo "📄 Copying cabinet content..."
cp content/*.md $BUILD_DIR/

# 5. Ensure bucket exists (don't recreate if exists)
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

# 8. Deploy to S3 (preserve existing logs and content)
echo "☁️ Deploying to S3..."
aws s3 sync $BUILD_DIR/ s3://$BUCKET_NAME/ --region $REGION --exclude "logs/*"

# 9. Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"
echo $WEBSITE_URL > website-url.txt

# 10. Cleanup
rm -f bucket-policy.json

echo "✅ Cabinet deployment complete!"
echo "🌐 Website URL: $WEBSITE_URL"
echo "📁 Bucket: s3://$BUCKET_NAME"
echo "📝 Hermes integration preserved - README.md can still be updated"
echo "🎨 Now styled with CodeRipple branding!"
