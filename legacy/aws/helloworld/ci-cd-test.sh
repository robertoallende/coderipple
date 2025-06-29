#!/bin/bash
# ci-cd-test.sh - CI/CD integration test for Hello World debugging function

set -e

echo "🚀 Starting Hello World CI/CD Test..."

# Build, deploy, and test Hello World function
echo "📦 Building Hello World layer..."
./build_helloworld_layer.sh

echo "📦 Packaging Hello World function..."
./package_helloworld_function.sh

echo "🚀 Deploying Hello World layer..."
./deploy_helloworld_layer.sh

echo "🚀 Deploying Hello World function..."
./deploy_helloworld_function.sh

echo "🧪 Testing Hello World function..."
./test_helloworld.sh

echo "✅ Hello World CI/CD Test Complete!"
echo ""
echo "Function URL for curl testing:"
echo "https://4yyao74oguyvck256blqo5gpwa0kcyiw.lambda-url.us-east-1.on.aws/"
echo ""
echo "Test with curl:"
echo 'curl -X POST "https://4yyao74oguyvck256blqo5gpwa0kcyiw.lambda-url.us-east-1.on.aws/" -H "Content-Type: application/json" -d '"'"'{"test": "ci-cd"}'"'"' | jq '"'"'.'"'"''
