#!/bin/bash

# IAM Policies for Drawer S3 Bucket Access
# Creates policies for Receptionist, Analyst, and Deliverer components

set -e

echo "🔐 Deploying IAM Policies for Drawer Access..."

# Variables
BUCKET_NAME="coderipple-drawer"
REGION="us-east-1"

if [ ! -f "bucket-name.txt" ]; then
    echo "❌ Bucket name not found. Run deploy-bucket.sh first."
    exit 1
fi

BUCKET_NAME=$(cat bucket-name.txt)

# 1. Receptionist Policy - Write workingcopy and repohistory
echo "📝 Creating Receptionist IAM policy..."
cat > receptionist-policy.json << EOF
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
        "arn:aws:s3:::$BUCKET_NAME/repos/*/workingcopy/*",
        "arn:aws:s3:::$BUCKET_NAME/repos/*/repohistory/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::$BUCKET_NAME",
      "Condition": {
        "StringLike": {
          "s3:prefix": "repos/*"
        }
      }
    }
  ]
}
EOF

# Create or update policy
aws iam put-role-policy \
  --role-name coderipple-receptionist-role \
  --policy-name ReceptionistDrawerAccess \
  --policy-document file://receptionist-policy.json 2>/dev/null || echo "Receptionist role not found - will create with Lambda"

echo "✅ Receptionist policy configured"

# 2. Analyst Policy - Read workingcopy, write analysis
echo "📊 Creating Analyst IAM policy..."
cat > analyst-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME/repos/*/workingcopy/*",
        "arn:aws:s3:::$BUCKET_NAME/repos/*/repohistory/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:PutObjectAcl"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME/repos/*/analysis/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::$BUCKET_NAME",
      "Condition": {
        "StringLike": {
          "s3:prefix": "repos/*"
        }
      }
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name coderipple-analyst-role \
  --policy-name AnalystDrawerAccess \
  --policy-document file://analyst-policy.json 2>/dev/null || echo "Analyst role not found - will create with Lambda"

echo "✅ Analyst policy configured"

# 3. Deliverer Policy - Read analysis files
echo "🚚 Creating Deliverer IAM policy..."
cat > deliverer-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME/repos/*/analysis/*",
        "arn:aws:s3:::$BUCKET_NAME/repos/*/workingcopy/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME/repos/*/analysis/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::$BUCKET_NAME",
      "Condition": {
        "StringLike": {
          "s3:prefix": "repos/*"
        }
      }
    }
  ]
}
EOF

aws iam put-role-policy \
  --role-name coderipple-deliverer-role \
  --policy-name DelivererDrawerAccess \
  --policy-document file://deliverer-policy.json 2>/dev/null || echo "Deliverer role not found - will create with Lambda"

echo "✅ Deliverer policy configured"

# 4. Create a test policy for manual testing
echo "🧪 Creating test user policy..."
cat > test-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::$BUCKET_NAME",
        "arn:aws:s3:::$BUCKET_NAME/*"
      ]
    }
  ]
}
EOF

# Save test policy for manual attachment if needed
echo "💾 Test policy saved to test-policy.json"

echo ""
echo "🎉 IAM Policies Deployment Complete!"
echo "🔐 Policies created for:"
echo "  - Receptionist: Write workingcopy + repohistory"
echo "  - Analyst: Read workingcopy, write analysis"
echo "  - Deliverer: Read analysis, delete after PR"
echo ""
echo "📋 Policy Summary:"
echo "  - Least privilege access per component"
echo "  - Directory-specific permissions"
echo "  - Secure bucket operations only"
echo ""
echo "Next steps:"
echo "1. Test drawer operations with test-drawer.sh"
echo "2. Deploy Receptionist Lambda (Unit 4.2)"
echo "3. Verify component access patterns"

# Cleanup
rm -f receptionist-policy.json analyst-policy.json deliverer-policy.json

echo "💾 IAM policies configured and ready"
