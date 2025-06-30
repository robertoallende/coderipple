#!/bin/bash

# Drawer S3 Bucket Deployment
# Creates private S3 bucket for repository storage with three-directory structure

set -e

echo "🗄️ Deploying CodeRipple Drawer S3 Bucket..."

# Variables
BUCKET_NAME="coderipple-drawer"
REGION="us-east-1"

# 1. Create S3 bucket
echo "📦 Creating S3 bucket..."
aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region $REGION 2>/dev/null || echo "Bucket already exists"

echo "✅ S3 bucket created/verified"

# 2. Configure bucket settings - Private bucket (no public access)
echo "🔒 Configuring private bucket settings..."

# Block all public access
aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo "✅ Public access blocked"

# 3. Enable versioning (optional but recommended)
echo "📝 Enabling versioning..."
aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

echo "✅ Versioning enabled"

# 4. Add bucket tags
echo "🏷️ Adding bucket tags..."
aws s3api put-bucket-tagging \
  --bucket $BUCKET_NAME \
  --tagging 'TagSet=[
    {Key=Project,Value=coderipple},
    {Key=Component,Value=drawer},
    {Key=Purpose,Value=repository-storage}
  ]'

echo "✅ Bucket tagged"

# 5. Create initial directory structure documentation
echo "📁 Creating directory structure documentation..."
cat > directory-structure.md << EOF
# CodeRipple Drawer Directory Structure

## S3 Bucket: $BUCKET_NAME

### Directory Pattern:
\`\`\`
repos/{owner}/{repo}/{commit_sha}/
├── workingcopy/          # Clean source code at specific commit
│   ├── src/
│   ├── README.md
│   └── ... (all source files)
├── repohistory/          # Full git repository with history
│   ├── .git/            # Complete git metadata
│   ├── src/
│   └── ... (full repository)
└── analysis/             # Generated analysis files (created by Analyst)
    ├── report.md
    ├── metrics.json
    ├── summary.txt
    └── ... (analysis outputs)
\`\`\`

### Component Access:
- **Receptionist**: Writes workingcopy/ and repohistory/
- **Analyst**: Reads workingcopy/, writes analysis/
- **Deliverer**: Reads analysis/ for PR creation

### Storage Classes:
- **Standard**: For active analysis (first 30 days)
- **IA**: For completed analysis (after 30 days)
- **Glacier**: For long-term archival (after 90 days)
EOF

# Upload documentation to bucket
aws s3 cp directory-structure.md s3://$BUCKET_NAME/README.md

echo "✅ Directory structure documented"

# 6. Set up lifecycle policy for cost optimization
echo "💰 Configuring lifecycle policy..."
cat > lifecycle-policy.json << EOF
{
  "Rules": [
    {
      "ID": "RepositoryStorageLifecycle",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "repos/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        }
      ]
    }
  ]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
  --bucket $BUCKET_NAME \
  --lifecycle-configuration file://lifecycle-policy.json

echo "✅ Lifecycle policy configured"

# 7. Test bucket access
echo "🧪 Testing bucket access..."
echo "Test file for drawer bucket" > test-file.txt
aws s3 cp test-file.txt s3://$BUCKET_NAME/test/test-file.txt
aws s3 rm s3://$BUCKET_NAME/test/test-file.txt
rm test-file.txt

echo "✅ Bucket access verified"

echo ""
echo "🎉 Drawer S3 Bucket Deployment Complete!"
echo "🗄️ Bucket Name: $BUCKET_NAME"
echo "📍 Region: $REGION"
echo "🔒 Access: Private (IAM roles only)"
echo "📁 Structure: Three-directory pattern ready"
echo ""
echo "Next steps:"
echo "1. Deploy IAM policies with deploy-iam.sh"
echo "2. Test bucket operations with test-drawer.sh"
echo "3. Integrate with Receptionist Lambda (Unit 4.2)"

# Save bucket info for other scripts
echo $BUCKET_NAME > bucket-name.txt
echo "💾 Bucket name saved to bucket-name.txt"

# Cleanup
rm -f lifecycle-policy.json directory-structure.md
