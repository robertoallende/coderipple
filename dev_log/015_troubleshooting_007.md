# Unit 015_troubleshooting_007: Lambda Alias Environment Mismatch and Import Logic Enhancement

## Objective

Resolve Lambda alias ResourceConflictException caused by environment variable mismatch in import logic and enhance import commands to be environment-aware rather than hardcoded, preventing future import gaps.

## Problem Analysis

### Critical Issue Identified
The deployment failed with a Lambda alias conflict after successfully creating other resources:

```
Error: creating Lambda Alias (prod): operation error Lambda: CreateAlias, 
https response error StatusCode: 409, RequestID: 32b32231-0680-4135-bad4-53891b529231, 
ResourceConflictException: Alias already exists: 
arn:aws:lambda:us-east-1:741448943849:function:coderipple-orchestrator:prod
```

### Root Cause Analysis

#### ❌ **Environment Variable Mismatch in Import Logic**:
1. **Terraform Environment**: `TF_VAR_environment: prod` (creates `:prod` alias)
2. **Import Logic**: Hardcoded `:dev` in import command
3. **Actual Alias**: Exists as `:prod` but import looks for `:dev`
4. **Result**: Import fails, Terraform tries to create existing `:prod` alias

#### ✅ **Positive Progress Indicators**:
- **API Gateway Method Settings**: Successfully created (`k60k38hrz7-prod-*/*`)
- **Most Resources**: Being processed correctly
- **Lambda Function**: Working and accessible
- **Units 15.1-15.6**: Successfully resolved previous import issues

#### 🔍 **Pattern Recognition**:
This reveals a **systematic issue** with hardcoded values in import logic:
- **Unit 15.3-15.4**: Fixed missing KMS and IAM resources
- **Unit 15.5**: Fixed missing Lambda function import
- **Unit 15.6**: Fixed OpenTelemetry runtime issues
- **Unit 15.7**: Environment-aware import logic needed

## Implementation

### Issue Classification: CRITICAL IMPORT LOGIC
This is a **critical import logic enhancement** that affects:
- ❌ Lambda alias deployment
- ❌ Environment-specific resource management
- ❌ Scalability to different environments (dev/staging/prod)
- ❌ Import logic reliability and maintainability

### Solution 1: Fix Lambda Alias Import Command ✅ PLANNED

#### Problem: Hardcoded Environment in Import
**Current Import Logic** (Wrong):
```yaml
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator:dev
```

**Should Be** (Environment-Aware):
```yaml
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator:${{ env.TF_VAR_environment }}
```

#### Implementation: Update Workflow Import Logic
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`
**Location**: Import Existing AWS Resources step

```yaml
# Import Lambda function and alias if they exist
echo "Importing Lambda function..."
terraform import aws_lambda_function.coderipple_orchestrator coderipple-orchestrator || echo "Lambda function import skipped (may not exist or already imported)"

# Fix: Use environment variable instead of hardcoded 'dev'
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator:${{ env.TF_VAR_environment }} || echo "Lambda alias import skipped (may not exist or already imported)"

# Import Lambda permissions if they exist
terraform import aws_lambda_permission.api_gateway_invoke coderipple-orchestrator/AllowExecutionFromAPIGateway || echo "Lambda permission import skipped (may not exist or already imported)"
```

### Solution 2: Environment-Aware Import Logic Enhancement ✅ PLANNED

#### Make All Import Commands Environment-Aware
**Objective**: Replace hardcoded values with environment variables throughout import logic

**Enhanced Import Logic**:
```yaml
- name: Import Existing AWS Resources
  run: |
    echo "🔄 Attempting to import existing AWS resources..."
    echo "🔍 Import process debugging enabled..."
    echo "Environment: ${{ env.TF_VAR_environment }}"
    echo "Project: ${{ env.TF_VAR_project_name }}"
    echo "Region: ${{ env.AWS_DEFAULT_REGION }}"
    
    # Environment-aware resource naming
    PROJECT_NAME="${{ env.TF_VAR_project_name }}"
    ENVIRONMENT="${{ env.TF_VAR_environment }}"
    REGION="${{ env.AWS_DEFAULT_REGION }}"
    
    # Import S3 buckets with project-aware naming
    echo "Importing S3 buckets..."
    terraform import aws_s3_bucket.terraform_state ${PROJECT_NAME}-terraform-state || echo "S3 terraform state bucket import skipped"
    terraform import aws_s3_bucket.terraform_state_access_logs ${PROJECT_NAME}-terraform-state-access-logs || echo "S3 access logs bucket import skipped"
    
    # Import IAM roles with project-aware naming
    echo "Importing IAM roles..."
    terraform import aws_iam_role.lambda_execution_role ${PROJECT_NAME}-lambda-execution-role || echo "Lambda execution role import skipped"
    terraform import aws_iam_role.api_gateway_cloudwatch_role ${PROJECT_NAME}-api-gateway-cloudwatch-role || echo "API Gateway CloudWatch role import skipped"
    
    # Import IAM policies with dynamic account ID and project naming
    echo "Importing IAM policies..."
    ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    terraform import aws_iam_policy.bedrock_access_policy arn:aws:iam::${ACCOUNT_ID}:policy/${PROJECT_NAME}-bedrock-access || echo "Bedrock access policy import skipped"
    terraform import aws_iam_policy.cloudwatch_enhanced_policy arn:aws:iam::${ACCOUNT_ID}:policy/${PROJECT_NAME}-cloudwatch-enhanced || echo "CloudWatch enhanced policy import skipped"
    terraform import aws_iam_policy.parameter_store_policy arn:aws:iam::${ACCOUNT_ID}:policy/${PROJECT_NAME}-parameter-store-access || echo "Parameter store policy import skipped"
    terraform import aws_iam_policy.lambda_kms_policy arn:aws:iam::${ACCOUNT_ID}:policy/${PROJECT_NAME}-lambda-kms-policy || echo "Lambda KMS policy import skipped"
    terraform import aws_iam_policy.lambda_xray_policy arn:aws:iam::${ACCOUNT_ID}:policy/${PROJECT_NAME}-lambda-xray-policy || echo "Lambda X-Ray policy import skipped"
    terraform import aws_iam_policy.lambda_sqs_policy arn:aws:iam::${ACCOUNT_ID}:policy/${PROJECT_NAME}-lambda-sqs-policy || echo "Lambda SQS policy import skipped"
    
    # Import SQS queue with environment-aware naming
    echo "Importing SQS queue..."
    terraform import aws_sqs_queue.lambda_dlq https://sqs.${REGION}.amazonaws.com/${ACCOUNT_ID}/${PROJECT_NAME}-lambda-dlq || echo "SQS DLQ import skipped"
    
    # Import CloudWatch log groups with project-aware naming
    echo "Importing CloudWatch log groups..."
    terraform import aws_cloudwatch_log_group.lambda_logs /aws/lambda/${PROJECT_NAME}-orchestrator || echo "Lambda log group import skipped"
    terraform import aws_cloudwatch_log_group.api_gateway_logs /aws/apigateway/${PROJECT_NAME}-webhook-api || echo "API Gateway log group import skipped"
    
    # Import API Gateway resources with project-aware discovery
    echo "Checking for existing API Gateway..."
    REST_API_ID=$(aws apigateway get-rest-apis --query "items[?name==\`${PROJECT_NAME}-webhook-api\`] | sort_by(@, &createdDate) | [0].id" --output text 2>/dev/null || echo "")
    if [ ! -z "$REST_API_ID" ] && [ "$REST_API_ID" != "None" ]; then
      echo "Found API Gateway with ID: $REST_API_ID"
      terraform import aws_api_gateway_rest_api.webhook_api $REST_API_ID || echo "API Gateway REST API import skipped"
      terraform import aws_api_gateway_stage.webhook_stage $REST_API_ID/$ENVIRONMENT || echo "API Gateway stage import skipped"
      
      # Import API Gateway resources and methods
      ROOT_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $REST_API_ID --query 'items[?path==`/`].id' --output text 2>/dev/null || echo "")
      if [ ! -z "$ROOT_RESOURCE_ID" ] && [ "$ROOT_RESOURCE_ID" != "None" ]; then
        WEBHOOK_RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $REST_API_ID --query 'items[?pathPart==`webhook`].id' --output text 2>/dev/null || echo "")
        if [ ! -z "$WEBHOOK_RESOURCE_ID" ] && [ "$WEBHOOK_RESOURCE_ID" != "None" ]; then
          terraform import aws_api_gateway_resource.webhook_resource $REST_API_ID/$WEBHOOK_RESOURCE_ID || echo "API Gateway webhook resource import skipped"
          terraform import aws_api_gateway_method.webhook_post $REST_API_ID/$WEBHOOK_RESOURCE_ID/POST || echo "API Gateway POST method import skipped"
          terraform import aws_api_gateway_integration.webhook_integration $REST_API_ID/$WEBHOOK_RESOURCE_ID/POST || echo "API Gateway integration import skipped"
        fi
      fi
    else
      echo "No existing API Gateway found"
    fi
    
    # Import Lambda function and alias with environment-aware naming
    echo "Importing Lambda function..."
    terraform import aws_lambda_function.coderipple_orchestrator ${PROJECT_NAME}-orchestrator || echo "Lambda function import skipped"
    terraform import aws_lambda_alias.coderipple_orchestrator_alias ${PROJECT_NAME}-orchestrator:${ENVIRONMENT} || echo "Lambda alias import skipped"
    
    # Import Lambda permissions with environment-aware naming
    terraform import aws_lambda_permission.api_gateway_invoke ${PROJECT_NAME}-orchestrator/AllowExecutionFromAPIGateway || echo "Lambda permission import skipped"
    
    # Import KMS key and alias with project-aware naming
    echo "Importing KMS resources..."
    KMS_KEY_ID=$(aws kms list-aliases --query "Aliases[?AliasName==\`alias/${PROJECT_NAME}-encryption-key\`].TargetKeyId" --output text 2>/dev/null || echo "")
    if [ ! -z "$KMS_KEY_ID" ] && [ "$KMS_KEY_ID" != "None" ]; then
      terraform import aws_kms_key.coderipple_key $KMS_KEY_ID || echo "KMS key import skipped"
      terraform import aws_kms_alias.coderipple_key_alias alias/${PROJECT_NAME}-encryption-key || echo "KMS alias import skipped"
    fi
    
    # Import CloudWatch alarms with project-aware naming
    echo "Importing CloudWatch alarms..."
    terraform import aws_cloudwatch_metric_alarm.dlq_messages ${PROJECT_NAME}-dlq-messages || echo "DLQ messages alarm import skipped"
    terraform import aws_cloudwatch_metric_alarm.lambda_throttles ${PROJECT_NAME}-lambda-throttles || echo "Lambda throttles alarm import skipped"
    
    echo "✅ Environment-aware resource import attempt completed"
```

### Solution 3: Immediate Manual Fix ✅ READY

#### Quick Resolution for Current Deployment
**Objective**: Fix the immediate Lambda alias conflict

**Manual Import Command**:
```bash
cd infra/terraform
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator:prod
terraform plan
terraform apply
```

### Solution 4: Import Logic Validation ✅ PLANNED

#### Add Import Validation and Debugging
**Objective**: Better visibility into import success/failure

```yaml
# Add validation after imports
echo "🔍 Validating import results..."
echo "Terraform state after imports:"
terraform state list | grep -E "(lambda|api_gateway|kms)" || echo "No matching resources in state"

echo "AWS resources that should be imported:"
aws lambda list-functions --query 'Functions[?starts_with(FunctionName, `'${PROJECT_NAME}'`)].FunctionName' --output table
aws lambda list-aliases --function-name ${PROJECT_NAME}-orchestrator --query 'Aliases[].Name' --output table
```

## AI Interactions

### Problem Identification Strategy
- **Error Pattern Analysis**: Recognized ResourceConflictException pattern from previous units
- **Environment Variable Analysis**: Identified mismatch between deployment and import environments
- **Import Logic Review**: Found hardcoded values throughout import commands
- **Systematic Issue Recognition**: Connected this to broader import logic enhancement needs

### Solution Development Approach
- **Environment-Aware Design**: Replace hardcoded values with dynamic environment variables
- **Comprehensive Enhancement**: Update all import commands for consistency
- **Immediate Fix Strategy**: Provide quick manual resolution for current deployment
- **Future-Proofing**: Design import logic to work across different environments

### Technical Decision Points
- **Variable Usage**: Use GitHub Actions environment variables for dynamic naming
- **Error Handling**: Maintain continue-on-error pattern for resilient imports
- **Validation Enhancement**: Add post-import validation for better debugging
- **Backward Compatibility**: Ensure changes work with existing infrastructure

## Files to Modify

### 1. Workflow Import Logic Enhancement (PRIMARY FIX)
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`
**Changes**:
- **Replace hardcoded values** with environment variables
- **Fix Lambda alias import** to use correct environment
- **Add import validation** and debugging output
- **Enhance error handling** for better troubleshooting

### 2. Documentation Update (TRACKING)
**File**: `dev_log/000_main.md`
**Add**: Unit 15.7 entry

## Status: Ready for Implementation

### Implementation Plan Summary

#### ✅ **Phase 1: Immediate Fix** (URGENT):
- **Manual import** of Lambda alias with correct environment
- **Continue current deployment** to completion
- **Verify deployment success** with curl tests

#### ✅ **Phase 2: Import Logic Enhancement** (SYSTEMATIC FIX):
- **Update workflow import logic** to be environment-aware
- **Replace all hardcoded values** with dynamic variables
- **Add import validation** and debugging
- **Test with different environments** (dev/staging/prod)

#### ✅ **Phase 3: Validation** (TESTING):
- **Test import logic** with fresh deployment
- **Verify environment flexibility** works correctly
- **Confirm no more ResourceConflictExceptions**

### Expected Results
With Unit 15.7 implementation:
- ✅ **Lambda alias import succeeds** with correct environment
- ✅ **Environment-aware import logic** works for dev/staging/prod
- ✅ **No more hardcoded values** in import commands
- ✅ **Scalable import process** for different project configurations
- ✅ **Complete deployment pipeline success**

### Integration with Previous Units
**Unit 15.7 completes the import logic enhancement series**:
- **Units 15.1-15.2**: Resolved Terraform configuration conflicts
- **Units 15.3-15.5**: Fixed state management and resource import gaps
- **Unit 15.6**: Resolved runtime compatibility issues
- **Unit 15.7**: Enhanced import logic to be environment-aware and maintainable

### Next Steps
1. **Run immediate manual fix** for Lambda alias import
2. **Complete current deployment** and verify success
3. **Implement enhanced import logic** for future deployments
4. **Test environment flexibility** with different configurations

**Unit 15.7 Status: ✅ READY - Lambda alias import fix and comprehensive import logic enhancement prepared**
