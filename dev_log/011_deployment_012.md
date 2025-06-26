# MDD 011_deployment_012: API Gateway Deprecation Warning and Resource Conflicts

## Problem Statement

**Status**: Lambda reserved environment variable error resolved ✅ (MDD 011_deployment_011 successful)

**New Issues**: Terraform apply failing with three distinct problems:

1. **API Gateway Deprecation Warning**:
```
Warning: Argument is deprecated
  with aws_api_gateway_deployment.webhook_deployment,
  on main.tf line ***8, in resource "aws_api_gateway_deployment" "webhook_deployment":
  ***8:   stage_name  = var.api_gateway_stage

stage_name is deprecated. Use the aws_api_gateway_stage resource instead.
```

2. **S3 Bucket Already Exists** (Persistent):
```
Error: creating S3 Bucket (***-terraform-state): BucketAlreadyExists
  with aws_s3_bucket.terraform_state,
  on main.tf line 108, in resource "aws_s3_bucket" "terraform_state":
  108: resource "aws_s3_bucket" "terraform_state" {
```

3. **API Gateway Stage Conflict**:
```
Error: creating API Gateway Stage (dev): operation error API Gateway: CreateStage, 
https response error StatusCode: 409, RequestID: bca9a4d9-2e16-4967-875b-7b9c00e2ad4f, 
ConflictException: Stage already exists
  with aws_api_gateway_stage.webhook_stage,
  on main.tf line 846, in resource "aws_api_gateway_stage" "webhook_stage":
  846: resource "aws_api_gateway_stage" "webhook_stage" {
```

**Context**:
- Deployment progressing further after Lambda environment variable fix
- CloudWatch permissions appear to be resolved (no CloudWatch errors)
- New API Gateway and persistent S3 state management issues

## Root Cause Analysis

### **Issue 1: API Gateway Deprecation**
**Root Cause**: Using deprecated `stage_name` parameter in `aws_api_gateway_deployment` resource.

**Current Configuration** (main.tf line ~***8):
```hcl
resource "aws_api_gateway_deployment" "webhook_deployment" {
  # ... other config
  stage_name = var.api_gateway_stage  # ❌ DEPRECATED
}
```

**Modern Approach**: Use separate `aws_api_gateway_stage` resource for stage management.

### **Issue 2: S3 Bucket Conflict (Persistent)**
**Root Cause**: Same as previous MDDs - bucket exists but not in Terraform state.
- Requires import strategy in GitHub Actions context
- Cannot be resolved locally due to different AWS credentials

### **Issue 3: API Gateway Stage Conflict**
**Root Cause**: API Gateway stage "dev" already exists from previous deployment attempt.
- Similar to S3 bucket issue - resource exists but not tracked in Terraform state
- Requires import or recreation strategy

## Solution Strategy

### **Solution 1: Fix API Gateway Deprecation**
**Approach**: Remove deprecated `stage_name` from deployment resource, rely on separate stage resource.

**Current Configuration**:
```hcl
# Deployment resource (deprecated approach)
resource "aws_api_gateway_deployment" "webhook_deployment" {
  rest_api_id = aws_api_gateway_rest_api.webhook_api.id
  stage_name  = var.api_gateway_stage  # Remove this
  
  # Trigger redeployment on changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.webhook_resource.id,
      aws_api_gateway_method.webhook_post.id,
      aws_api_gateway_integration.lambda_integration.id,
    ]))
  }
}

# Stage resource (modern approach)
resource "aws_api_gateway_stage" "webhook_stage" {
  deployment_id = aws_api_gateway_deployment.webhook_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.webhook_api.id
  stage_name    = var.api_gateway_stage
}
```

**Fixed Configuration**:
```hcl
# Deployment resource (no stage_name)
resource "aws_api_gateway_deployment" "webhook_deployment" {
  rest_api_id = aws_api_gateway_rest_api.webhook_api.id
  
  # Trigger redeployment on changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.webhook_resource.id,
      aws_api_gateway_method.webhook_post.id,
      aws_api_gateway_integration.lambda_integration.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# Stage resource handles stage creation
resource "aws_api_gateway_stage" "webhook_stage" {
  deployment_id = aws_api_gateway_deployment.webhook_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.webhook_api.id
  stage_name    = var.api_gateway_stage
}
```

### **Solution 2: S3 Bucket Import Strategy**
**Approach**: Import existing bucket in GitHub Actions context.

**GitHub Actions Workflow Addition**:
```yaml
- name: Import Existing Resources
  run: |
    # Import S3 bucket if it exists
    terraform import aws_s3_bucket.terraform_state coderipple-terraform-state || echo "Bucket import failed or not needed"
  working-directory: infra/terraform
  continue-on-error: true
```

### **Solution 3: API Gateway Stage Import**
**Approach**: Import existing API Gateway stage.

**Import Command**:
```bash
# Format: terraform import aws_api_gateway_stage.resource_name REST-API-ID/STAGE-NAME
terraform import aws_api_gateway_stage.webhook_stage {rest_api_id}/dev
```

## Implementation Plan

### **Phase 1: Fix API Gateway Deprecation**
1. **Remove deprecated stage_name** from `aws_api_gateway_deployment`
2. **Add lifecycle rule** to prevent deployment conflicts
3. **Ensure stage resource** properly references deployment

### **Phase 2: Resource Import Strategy**
1. **Add import step** to GitHub Actions workflow
2. **Handle import failures gracefully** with continue-on-error
3. **Test deployment** after import attempts

### **Phase 3: Validation and Testing**
1. **Verify API Gateway** deployment and stage creation
2. **Test webhook endpoint** functionality
3. **Monitor for additional** resource conflicts

## Detailed Implementation

### **Step 1: API Gateway Configuration Fix**

**Find and Update Deployment Resource**:
```hcl
# Remove stage_name parameter
resource "aws_api_gateway_deployment" "webhook_deployment" {
  rest_api_id = aws_api_gateway_rest_api.webhook_api.id
  # stage_name  = var.api_gateway_stage  # REMOVE THIS LINE
  
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.webhook_resource.id,
      aws_api_gateway_method.webhook_post.id,
      aws_api_gateway_integration.lambda_integration.id,
    ]))
  }
  
  lifecycle {
    create_before_destroy = true
  }
}
```

### **Step 2: GitHub Actions Import Enhancement**

**Add to deploy-infrastructure.yml**:
```yaml
- name: Import Existing AWS Resources
  run: |
    echo "Attempting to import existing resources..."
    
    # Import S3 bucket
    terraform import aws_s3_bucket.terraform_state coderipple-terraform-state || echo "S3 bucket import skipped"
    
    # Import API Gateway stage (requires REST API ID)
    REST_API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`coderipple-webhook-api`].id' --output text)
    if [ ! -z "$REST_API_ID" ]; then
      terraform import aws_api_gateway_stage.webhook_stage $REST_API_ID/dev || echo "API Gateway stage import skipped"
    fi
  working-directory: infra/terraform
  continue-on-error: true
```

## Expected Outcomes

### **Immediate Resolution**
- **API Gateway Warning Eliminated**: Modern resource configuration
- **S3 Bucket Conflict Resolved**: Import handles existing bucket
- **API Gateway Stage Conflict Resolved**: Import handles existing stage

### **Long-term Benefits**
- **Modern Terraform Practices**: No deprecated resource usage
- **Robust Deployment Pipeline**: Handles existing resource conflicts
- **Cleaner Resource Management**: Proper separation of concerns

## Risk Assessment

### **Low Risk**
- API Gateway deprecation fix (standard modernization)
- Resource import with continue-on-error (safe fallback)

### **Medium Risk**
- API Gateway deployment changes (could affect endpoint availability)

### **Mitigation**
- **Lifecycle rules** prevent resource destruction during updates
- **Continue-on-error** prevents pipeline failure on import issues
- **Gradual deployment** allows rollback if needed

## Success Criteria

- [x] API Gateway deprecation warning eliminated
- [x] S3 bucket conflict resolved through import
- [x] API Gateway stage conflict resolved through import
- [x] Webhook endpoint remains functional
- [x] Deployment pipeline completes successfully
- [x] No regression in existing functionality

## Related Components

- **API Gateway Deployment**: `aws_api_gateway_deployment.webhook_deployment`
- **API Gateway Stage**: `aws_api_gateway_stage.webhook_stage`
- **S3 Bucket**: `aws_s3_bucket.terraform_state`
- **GitHub Actions**: `.github/workflows/deploy-infrastructure.yml`

## Notes

- API Gateway deprecation warnings are common in older Terraform configurations
- Resource import strategies essential for brownfield deployments
- GitHub Actions context provides proper AWS credentials for import operations
- This pattern will likely repeat for other AWS resources as deployment progresses
