#!/bin/bash

# Test script for Inventory S3 Bucket website

set -e

# Check if website URL exists
if [ ! -f "website-url.txt" ]; then
    echo "❌ Website URL not found. Run deploy-bucket.sh first."
    exit 1
fi

WEBSITE_URL=$(cat website-url.txt)
BUCKET_NAME="coderipple-cabinet"
REGION="us-east-1"

echo "🧪 Testing CodeRipple Cabinet S3 Website..."
echo "🌐 Website URL: $WEBSITE_URL"
echo ""

# Test 1: Check bucket exists and is accessible
echo "Test 1: Verify S3 bucket exists"
aws s3api head-bucket --bucket $BUCKET_NAME --region $REGION
echo "✅ S3 bucket accessible"
echo ""

# Test 2: Check website hosting is enabled
echo "Test 2: Verify website hosting configuration"
aws s3api get-bucket-website --bucket $BUCKET_NAME --region $REGION
echo "✅ Website hosting enabled"
echo ""

# Test 3: Check public access policy
echo "Test 3: Verify public read access policy"
aws s3api get-bucket-policy --bucket $BUCKET_NAME --region $REGION --query 'Policy' --output text | jq .
echo "✅ Public read access configured"
echo ""

# Test 4: Check files are uploaded
echo "Test 4: Verify initial files exist"
aws s3 ls s3://$BUCKET_NAME/ --region $REGION
echo "✅ Initial files present"
echo ""

# Test 5: Test website accessibility
echo "Test 5: Test website HTTP access"
echo "Fetching index.html..."
curl -s -o index-test.html $WEBSITE_URL
if [ -s index-test.html ]; then
    echo "✅ Website accessible via HTTP"
    echo "Content preview:"
    head -5 index-test.html
else
    echo "❌ Website not accessible"
fi
echo ""

# Test 6: Test README.md accessibility
echo "Test 6: Test README.md access"
README_URL="$WEBSITE_URL/README.md"
echo "Fetching README.md from: $README_URL"
curl -s -o readme-test.md $README_URL
if [ -s readme-test.md ]; then
    echo "✅ README.md accessible"
    echo "Content:"
    cat readme-test.md
else
    echo "❌ README.md not accessible"
fi
echo ""

# Test 7: Test Docsify rendering
echo "Test 7: Check Docsify integration"
if grep -q "docsify" index-test.html; then
    echo "✅ Docsify integration detected"
    if grep -q "CodeRipple Event Log" index-test.html; then
        echo "✅ Correct title found"
    else
        echo "⚠️ Title may need verification"
    fi
else
    echo "❌ Docsify integration not found"
fi

echo ""
echo "🎉 Testing complete!"
echo ""
echo "Website Access:"
echo "🌐 Main Site: $WEBSITE_URL"
echo "📄 Event Log: $WEBSITE_URL/#/"
echo ""
echo "Expected results:"
echo "- All tests should pass ✅"
echo "- Website should be accessible via HTTP"
echo "- Docsify should render the event log table"
echo "- README.md should show empty event table ready for Hermes"

# Cleanup
rm -f index-test.html readme-test.md
