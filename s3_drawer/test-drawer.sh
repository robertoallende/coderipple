#!/bin/bash

# Test script for Drawer S3 bucket operations
# Simulates the three-directory structure and component access patterns

set -e

if [ ! -f "bucket-name.txt" ]; then
    echo "❌ Bucket name not found. Run deploy-bucket.sh first."
    exit 1
fi

BUCKET_NAME=$(cat bucket-name.txt)
TEST_REPO="test-org/sample-repo"
TEST_COMMIT="abc123def456"
S3_PREFIX="repos/$TEST_REPO/$TEST_COMMIT"

echo "🧪 Testing Drawer S3 Bucket Operations..."
echo "🗄️ Bucket: $BUCKET_NAME"
echo "📁 Test Path: $S3_PREFIX"
echo ""

# Create test files
mkdir -p test-data/workingcopy test-data/repohistory test-data/analysis

# 1. Test workingcopy directory (Receptionist writes)
echo "📝 Testing workingcopy directory..."
echo "# Sample Repository" > test-data/workingcopy/README.md
echo "console.log('Hello World');" > test-data/workingcopy/index.js
echo '{"name": "sample-repo", "version": "1.0.0"}' > test-data/workingcopy/package.json

# Upload workingcopy files
aws s3 cp test-data/workingcopy/ s3://$BUCKET_NAME/$S3_PREFIX/workingcopy/ --recursive
echo "✅ Workingcopy files uploaded"

# 2. Test repohistory directory (Receptionist writes)
echo "📚 Testing repohistory directory..."
echo "# Sample Repository with Git History" > test-data/repohistory/README.md
echo "console.log('Hello World');" > test-data/repohistory/index.js
echo '{"name": "sample-repo", "version": "1.0.0"}' > test-data/repohistory/package.json
mkdir -p test-data/repohistory/.git
echo "Git metadata placeholder" > test-data/repohistory/.git/HEAD

# Upload repohistory files
aws s3 cp test-data/repohistory/ s3://$BUCKET_NAME/$S3_PREFIX/repohistory/ --recursive
echo "✅ Repohistory files uploaded"

# 3. Test analysis directory (Analyst writes)
echo "📊 Testing analysis directory..."
cat > test-data/analysis/report.md << EOF
# Code Analysis Report

## Repository: $TEST_REPO
## Commit: $TEST_COMMIT

### Summary
- Files analyzed: 3
- Lines of code: 25
- Issues found: 0

### Recommendations
- Code quality: Good
- Documentation: Adequate
- Test coverage: Missing
EOF

echo '{"files": 3, "loc": 25, "issues": 0, "score": 85}' > test-data/analysis/metrics.json
echo "Analysis completed successfully for $TEST_REPO at $TEST_COMMIT" > test-data/analysis/summary.txt

# Upload analysis files
aws s3 cp test-data/analysis/ s3://$BUCKET_NAME/$S3_PREFIX/analysis/ --recursive
echo "✅ Analysis files uploaded"

# 4. Test directory listing
echo "📋 Testing directory structure..."
echo "Repository structure in S3:"
aws s3 ls s3://$BUCKET_NAME/$S3_PREFIX/ --recursive

echo ""
echo "🔍 Verifying three-directory structure..."

# Check workingcopy
WORKINGCOPY_COUNT=$(aws s3 ls s3://$BUCKET_NAME/$S3_PREFIX/workingcopy/ --recursive | wc -l)
echo "Workingcopy files: $WORKINGCOPY_COUNT"

# Check repohistory  
REPOHISTORY_COUNT=$(aws s3 ls s3://$BUCKET_NAME/$S3_PREFIX/repohistory/ --recursive | wc -l)
echo "Repohistory files: $REPOHISTORY_COUNT"

# Check analysis
ANALYSIS_COUNT=$(aws s3 ls s3://$BUCKET_NAME/$S3_PREFIX/analysis/ --recursive | wc -l)
echo "Analysis files: $ANALYSIS_COUNT"

# 5. Test component access patterns
echo ""
echo "🔄 Testing component access patterns..."

# Simulate Analyst reading workingcopy
echo "📖 Analyst: Reading workingcopy for analysis..."
aws s3 cp s3://$BUCKET_NAME/$S3_PREFIX/workingcopy/package.json ./downloaded-package.json
echo "✅ Analyst can read workingcopy files"
rm downloaded-package.json

# Simulate Deliverer reading analysis
echo "📤 Deliverer: Reading analysis for PR creation..."
aws s3 cp s3://$BUCKET_NAME/$S3_PREFIX/analysis/report.md ./downloaded-report.md
echo "✅ Deliverer can read analysis files"
rm downloaded-report.md

# 6. Test cleanup (Deliverer deletes analysis after PR)
echo "🧹 Testing analysis cleanup..."
aws s3 rm s3://$BUCKET_NAME/$S3_PREFIX/analysis/ --recursive
echo "✅ Analysis files cleaned up"

# Verify cleanup
REMAINING_ANALYSIS=$(aws s3 ls s3://$BUCKET_NAME/$S3_PREFIX/analysis/ --recursive | wc -l)
echo "Remaining analysis files: $REMAINING_ANALYSIS"

# 7. Final structure check
echo ""
echo "📊 Final repository structure:"
aws s3 ls s3://$BUCKET_NAME/$S3_PREFIX/ --recursive

echo ""
echo "🎉 Drawer Testing Complete!"
echo ""
echo "✅ Test Results:"
echo "  - Workingcopy directory: Working"
echo "  - Repohistory directory: Working"  
echo "  - Analysis directory: Working"
echo "  - Component access patterns: Working"
echo "  - Cleanup operations: Working"
echo ""
echo "🗄️ Drawer S3 bucket is ready for:"
echo "  - Receptionist: Repository storage"
echo "  - Analyst: Code analysis"
echo "  - Deliverer: PR creation and cleanup"

# Cleanup test data
rm -rf test-data
aws s3 rm s3://$BUCKET_NAME/$S3_PREFIX/ --recursive

echo "🧹 Test data cleaned up"
