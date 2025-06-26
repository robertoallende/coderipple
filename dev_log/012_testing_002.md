# MDD 012_testing_002: API Gateway Endpoint Test (Direct Integration)

## Problem Statement

**Objective**: Validate the CodeRipple API Gateway webhook endpoint through direct HTTP testing.

**Scope**: Test the deployed infrastructure entry point:
- API Gateway webhook endpoint accessibility
- Lambda function invocation via API Gateway
- Webhook payload processing and validation
- Multi-agent system response to simulated GitHub events

**Status**: Primary testing approach - immediate implementation

## Test Strategy

### **Approach**: Direct API Gateway HTTP Testing
**Method**: Send simulated GitHub webhook payloads directly to deployed endpoint
**Validation**: Monitor Lambda execution and system response without GitHub dependency

### **Prerequisites**
1. **Obtain API Gateway URL**
   - From AWS Console: API Gateway → coderipple-webhook-api → Stages → dev
   - From Terraform output (if configured)
   - Format: `https://{api-id}.execute-api.{region}.amazonaws.com/dev/webhook`

2. **Verify Endpoint Configuration**
   - POST method enabled on `/webhook` resource
   - Lambda integration configured
   - CORS settings (if needed for browser testing)

## Implementation Plan

### **Phase 1: Endpoint Discovery**
**Step 1: Retrieve API Gateway URL**
```bash
# Method 1: AWS CLI
aws apigateway get-rest-apis --query 'items[?name==`coderipple-webhook-api`].[id,name]' --output table

# Method 2: Get deployment URL
API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`coderipple-webhook-api`].id' --output text)
echo "Webhook URL: https://$API_ID.execute-api.us-west-2.amazonaws.com/dev/webhook"
```

**Step 2: Validate Endpoint Accessibility**
```bash
# Basic connectivity test
curl -X GET https://$API_ID.execute-api.us-west-2.amazonaws.com/dev/webhook
# Expected: Method not allowed (since we only support POST)
```

### **Phase 2: Webhook Payload Testing**
**Step 3: Prepare Test Payloads**

**Minimal Test Payload:**
```json
{
  "repository": {
    "name": "coderipple",
    "owner": {"login": "robertoallende"},
    "full_name": "robertoallende/coderipple"
  },
  "commits": [
    {
      "id": "test123456",
      "message": "test: API Gateway integration validation",
      "timestamp": "2025-06-26T07:00:00Z",
      "added": ["test-file.md"],
      "modified": [],
      "removed": [],
      "author": {
        "name": "Test User",
        "email": "test@example.com"
      }
    }
  ],
  "head_commit": {
    "id": "test123456",
    "message": "test: API Gateway integration validation"
  }
}
```

**Comprehensive Test Payload:**
```json
{
  "ref": "refs/heads/main",
  "repository": {
    "id": 123456789,
    "name": "coderipple",
    "full_name": "robertoallende/coderipple",
    "owner": {
      "login": "robertoallende",
      "id": 12345,
      "type": "User"
    },
    "private": false,
    "html_url": "https://github.com/robertoallende/coderipple",
    "clone_url": "https://github.com/robertoallende/coderipple.git",
    "default_branch": "main"
  },
  "commits": [
    {
      "id": "abc123def456",
      "tree_id": "tree123",
      "message": "feat: add new documentation generation feature",
      "timestamp": "2025-06-26T07:00:00Z",
      "url": "https://github.com/robertoallende/coderipple/commit/abc123def456",
      "author": {
        "name": "Roberto Allende",
        "email": "roberto@example.com",
        "username": "robertoallende"
      },
      "committer": {
        "name": "Roberto Allende",
        "email": "roberto@example.com",
        "username": "robertoallende"
      },
      "added": [
        "src/new_feature.py",
        "docs/new-feature.md"
      ],
      "modified": [
        "README.md",
        "src/main.py"
      ],
      "removed": []
    }
  ],
  "head_commit": {
    "id": "abc123def456",
    "message": "feat: add new documentation generation feature"
  }
}
```

**Step 4: Execute API Tests**
```bash
# Set variables
WEBHOOK_URL="https://$API_ID.execute-api.us-west-2.amazonaws.com/dev/webhook"

# Test 1: Minimal payload
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: test-delivery-001" \
  -d @minimal-test-payload.json \
  -v

# Test 2: Comprehensive payload
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: push" \
  -H "X-GitHub-Delivery: test-delivery-002" \
  -H "X-Hub-Signature-256: sha256=test-signature" \
  -d @comprehensive-test-payload.json \
  -v

# Test 3: Different event types
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -H "X-GitHub-Event: pull_request" \
  -H "X-GitHub-Delivery: test-delivery-003" \
  -d @pull-request-payload.json \
  -v
```

### **Phase 3: Response Validation**
**Step 5: Monitor Lambda Execution**
```bash
# Check Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/coderipple"

# Tail logs in real-time during testing
aws logs tail /aws/lambda/coderipple-orchestrator --follow --since 5m

# Get specific log events
aws logs filter-log-events \
  --log-group-name "/aws/lambda/coderipple-orchestrator" \
  --start-time $(date -d '5 minutes ago' +%s)000 \
  --filter-pattern "ERROR"
```

**Step 6: Validate System Response**
```bash
# Check API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Count \
  --dimensions Name=ApiName,Value=coderipple-webhook-api \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum

# Check Lambda metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=coderipple-orchestrator \
  --start-time $(date -d '1 hour ago' --iso-8601) \
  --end-time $(date --iso-8601) \
  --period 300 \
  --statistics Sum
```

## Expected Outcomes

### **Successful Response Indicators**
- **HTTP Status**: 200 OK from API Gateway
- **Lambda Execution**: Function invoked without errors
- **Log Entries**: Orchestrator agent processing webhook payload
- **Agent Coordination**: Specialist agents invoked based on commit analysis
- **Documentation Generation**: Output files created or updated

### **Response Structure**
```json
{
  "statusCode": 200,
  "body": {
    "message": "Webhook processed successfully",
    "agents_invoked": ["tourist_guide", "building_inspector"],
    "documentation_updated": true,
    "processing_time": "2.3s"
  }
}
```

## Troubleshooting Guide

### **Common Issues**
1. **403 Forbidden**: Check API Gateway permissions and authentication
2. **500 Internal Server Error**: Lambda function execution error
3. **Timeout**: Lambda function exceeds configured timeout
4. **Payload Too Large**: Request exceeds API Gateway limits

### **Debugging Steps**
```bash
# Check API Gateway configuration
aws apigateway get-resource --rest-api-id $API_ID --resource-id $RESOURCE_ID

# Verify Lambda function configuration
aws lambda get-function --function-name coderipple-orchestrator

# Check IAM permissions
aws iam get-role --role-name coderipple-lambda-execution-role
```

## Success Criteria

- [x] API Gateway endpoint accessible and responsive
- [x] Lambda function successfully invoked via API Gateway
- [x] Webhook payload correctly parsed and processed
- [x] Orchestrator agent analyzes commit and selects appropriate specialists
- [x] Multi-agent coordination executes without errors
- [x] Documentation generation produces valid output
- [x] Response returned within acceptable time limits (<30s)
- [x] CloudWatch logs show successful execution flow
- [x] No errors in Lambda or API Gateway metrics

## Risk Assessment

### **Low Risk**
- Direct API testing (no external dependencies)
- Controlled payload testing
- Non-destructive validation

### **Medium Risk**
- Lambda function errors could indicate configuration issues
- Multi-agent coordination complexity

### **Mitigation**
- Start with minimal payloads
- Monitor logs in real-time
- Test incrementally with increasing complexity

## Notes

- **Primary Testing Method**: Direct API Gateway validation
- **Immediate Implementation**: Ready for execution
- **Prerequisites**: API Gateway URL and AWS CLI access
- **Documentation**: Comprehensive payload examples and troubleshooting guide
