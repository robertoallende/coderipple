# Hello World Debugging Layer

This is a minimal Lambda function for debugging and CI/CD testing while the main CodeRipple system is being fixed. It tests Strands import functionality and platform targeting.

## Purpose

- **Debugging**: Verify CI/CD pipeline functionality
- **Platform Testing**: Validate Linux x86_64 compatibility from Unit 16
- **Dependency Verification**: Confirm Strands installation works
- **Infrastructure Baseline**: Known-good function for comparison

## Quick Start

### 1. Build and Deploy
```bash
# Make scripts executable
chmod +x *.sh

# Build layer with platform targeting
./build_helloworld_layer.sh

# Package function
./package_helloworld_function.sh

# Deploy layer
./deploy_helloworld_layer.sh

# Deploy function
./deploy_helloworld_function.sh
```

### 2. Test Function
```bash
# Test with AWS CLI
./test_helloworld.sh

# Or manually:
aws lambda invoke \
  --function-name helloworld-debug \
  --payload '{"test": "hello"}' \
  --cli-binary-format raw-in-base64-out \
  --region us-east-1 \
  response.json && cat response.json
```

## Testing with curl (API Gateway Required)

### Option 1: Function URL (Recommended)
```bash
# Function URL (already created):
FUNCTION_URL="https://4yyao74oguyvck256blqo5gpwa0kcyiw.lambda-url.us-east-1.on.aws/"

# Test with curl (wait a few minutes after deployment for URL to be active)
curl -X POST "$FUNCTION_URL" \
  -H "Content-Type: application/json" \
  -d '{"test": "curl_test"}' | jq '.'

# Alternative: Test with GET
curl -X GET "$FUNCTION_URL" | jq '.'
```

### Option 2: API Gateway (Manual Setup)
```bash
# Create REST API
aws apigateway create-rest-api \
  --name helloworld-debug-api \
  --description "Hello World debugging API"

# Manual configuration required in AWS Console
# Then test with:
curl -X GET https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/hello
```

## Expected Response

### Successful Response
```json
{
  "message": "Hello World from CodeRipple Debug Layer",
  "python_version": "3.12.x",
  "strands_import": "SUCCESS",
  "dependencies_status": {
    "boto3": "SUCCESS",
    "strands_agents": "SUCCESS", 
    "strands_agents_tools": "SUCCESS"
  },
  "platform_info": {
    "architecture": "x86_64",
    "system": "Linux"
  },
  "layer_info": {
    "opt_python_exists": true,
    "opt_python_contents": ["strands", "boto3", "..."]
  }
}
```

### Failed Response (Debugging Info)
```json
{
  "message": "Hello World from CodeRipple Debug Layer",
  "strands_import": "FAILED: No module named 'strands'",
  "dependencies_status": {
    "boto3": "SUCCESS",
    "strands_agents": "MISSING",
    "strands_agents_tools": "MISSING"
  }
}
```

## Troubleshooting

### Common Issues

#### 1. Platform Targeting Error
**Symptom**: `strands_import: "FAILED: No module named 'strands'"`
**Solution**: Rebuild layer with platform targeting
```bash
./build_helloworld_layer.sh
./deploy_helloworld_layer.sh
./deploy_helloworld_function.sh
```

#### 2. Layer Not Found
**Symptom**: Function deployment fails
**Solution**: Deploy layer first
```bash
./deploy_helloworld_layer.sh
./deploy_helloworld_function.sh
```

#### 3. Permission Errors
**Symptom**: AWS CLI errors
**Solution**: Check AWS credentials and IAM permissions
```bash
aws sts get-caller-identity
aws iam get-role --role-name coderipple-lambda-execution-role
```

### Debug Commands

```bash
# Check layer contents
unzip -l helloworld-dependencies.zip | head -20

# Check function logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/helloworld-debug"

# Get latest log events
aws logs get-log-events \
  --log-group-name "/aws/lambda/helloworld-debug" \
  --log-stream-name "$(aws logs describe-log-streams \
    --log-group-name "/aws/lambda/helloworld-debug" \
    --order-by LastEventTime \
    --descending \
    --limit 1 \
    --query 'logStreams[0].logStreamName' \
    --output text)"
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Test Hello World Debug Function
  run: |
    cd aws/helloworld
    ./build_helloworld_layer.sh
    ./deploy_helloworld_layer.sh
    ./deploy_helloworld_function.sh
    ./test_helloworld.sh
```

### Expected CI/CD Output
```
✅ Layer built successfully (31MB)
✅ Layer deployed (version X)
✅ Function deployed successfully
✅ Test passed: "Hello World from CodeRipple Debug Layer"
✅ Strands import: SUCCESS
✅ All dependencies: SUCCESS
```

## Files Structure

```
aws/helloworld/
├── README.md                      # This file
├── lambda_function.py             # Main function code
├── requirements_helloworld.txt    # Dependencies
├── build_helloworld_layer.sh      # Build layer script
├── package_helloworld_function.sh # Package function script
├── deploy_helloworld_layer.sh     # Deploy layer script
├── deploy_helloworld_function.sh  # Deploy function script
├── test_helloworld.sh             # Test function script
├── helloworld-dependencies.zip    # Generated layer package
├── helloworld-function.zip        # Generated function package
└── layer_arn.txt                  # Generated layer ARN
```

## Dependencies

Same minimal dependencies as Unit 16 platform fix:
- `strands-agents>=0.1.0`
- `strands-agents-tools>=0.1.0` 
- `boto3`

## Platform Targeting

Uses the same platform targeting solution from Unit 16:
```bash
pip install \
  --platform manylinux2014_x86_64 \
  --only-binary=:all: \
  --target helloworld_layer/python \
  --requirement requirements_helloworld.txt
```

This ensures Linux x86_64 binaries are installed for AWS Lambda compatibility.

## Support

This is a debugging tool created while CodeRipple is being fixed. For issues:

1. Check the troubleshooting section above
2. Verify platform targeting is working
3. Compare with Unit 16 platform resolution
4. Test with minimal payload: `{"test": "debug"}`

The function should always return "Hello World" message if basic infrastructure is working.
