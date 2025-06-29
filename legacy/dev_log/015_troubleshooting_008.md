# Unit 015_troubleshooting_008: Import Syntax Errors and Duplicate Resource Handling

## Objective

Fix critical import syntax errors for Lambda alias and API Gateway duplicate handling that prevent successful resource imports, causing continued ResourceConflictException errors during deployment.

## Problem Analysis

### Critical Issues Identified from Import Log

#### ❌ **Lambda Alias Import Syntax Error**:
```
Error: Unexpected format of ID ("coderipple-orchestrator:prod"), expected FUNCTION_NAME/ALIAS
```
**Problem**: Lambda alias import uses wrong syntax format
- **Current**: `coderipple-orchestrator:prod` 
- **Expected**: `coderipple-orchestrator/prod`

#### ❌ **API Gateway Duplicate Handling Error**:
```
Found API Gateway with ID: 8v94cdsv9d	k60k38hrz7
The import command expects two arguments.
```
**Problem**: Query returns multiple API Gateway IDs on one line, breaking import command

#### ✅ **Successful Imports Confirmed**:
- **S3 Buckets**: ✅ Successfully imported
- **IAM Roles & Policies**: ✅ Successfully imported  
- **SQS Queue**: ✅ Successfully imported
- **CloudWatch Log Groups**: ✅ Successfully imported
- **Lambda Function**: ✅ Successfully imported
- **Lambda Permission**: ✅ Successfully imported
- **KMS Key & Alias**: ✅ Successfully imported
- **CloudWatch Alarms**: ✅ Successfully imported

## Implementation

### Issue Classification: CRITICAL IMPORT SYNTAX
This is a **critical import syntax and logic issue** that prevents:
- ❌ Lambda alias import completion
- ❌ API Gateway resource import
- ❌ Complete state synchronization
- ❌ Successful deployment without conflicts

### Solution 1: Fix Lambda Alias Import Syntax ✅ IMMEDIATE

#### Problem: Wrong Import ID Format
**Current (Wrong)**:
```yaml
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator:${{ env.TF_VAR_environment }}
```

**Correct Syntax**:
```yaml
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator/${{ env.TF_VAR_environment }}
```

**Change**: Replace `:` with `/` in Lambda alias import ID

### Solution 2: Fix API Gateway Duplicate Handling ✅ IMMEDIATE

#### Problem: Multiple API IDs Returned on One Line
**Current Query** (Returns multiple IDs):
```bash
REST_API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`coderipple-webhook-api`].id' --output text)
# Result: "8v94cdsv9d	k60k38hrz7" (tab-separated)
```

**Fixed Query** (Returns oldest/first ID only):
```bash
REST_API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`coderipple-webhook-api`] | sort_by(@, &createdDate) | [0].id' --output text)
# Result: "8v94cdsv9d" (single ID)
```

### Solution 3: Manual Import Commands for Immediate Fix ✅ READY

#### Immediate Resolution Commands
```bash
cd infra/terraform

# Fix Lambda alias import with correct syntax
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator/prod

# Import the working API Gateway (8v94cdsv9d - the one we've been testing)
terraform import aws_api_gateway_rest_api.webhook_api 8v94cdsv9d
terraform import aws_api_gateway_stage.webhook_stage 8v94cdsv9d/prod

# Continue deployment
terraform plan
terraform apply
```

### Solution 4: Enhanced Import Logic ✅ SYSTEMATIC FIX

#### Update Workflow Import Logic
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`

**Lambda Alias Import Fix**:
```yaml
# Fix Lambda alias import syntax (: to /)
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator/${{ env.TF_VAR_environment }} || echo "Lambda alias import skipped (may not exist or already imported)"
```

**API Gateway Duplicate Handling Fix**:
```yaml
# Import API Gateway resources with duplicate handling
echo "Checking for existing API Gateway..."
REST_API_ID=$(aws apigateway get-rest-apis --query 'items[?name==`coderipple-webhook-api`] | sort_by(@, &createdDate) | [0].id' --output text 2>/dev/null || echo "")
if [ ! -z "$REST_API_ID" ] && [ "$REST_API_ID" != "None" ] && [ "$REST_API_ID" != "null" ]; then
  echo "Found API Gateway with ID: $REST_API_ID"
  terraform import aws_api_gateway_rest_api.webhook_api $REST_API_ID || echo "API Gateway REST API import skipped (may not exist or already imported)"
  terraform import aws_api_gateway_stage.webhook_stage $REST_API_ID/${{ env.TF_VAR_environment }} || echo "API Gateway stage import skipped (may not exist or already imported)"
  
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
  echo "No existing API Gateway found or multiple duplicates detected"
fi
```

## Files to Modify

### 1. Immediate Manual Fix (URGENT)
**Commands**: Run manual import commands above to fix current deployment

### 2. Workflow Import Logic Fix (SYSTEMATIC)
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`
**Changes**:
- **Fix Lambda alias import syntax**: Change `:` to `/`
- **Fix API Gateway duplicate handling**: Use sorted query to get single ID
- **Add validation**: Check for null/empty values

### 3. Documentation Update
**File**: `dev_log/000_main.md`
**Add**: Unit 15.8 entry

## Status: Ready for Immediate Implementation

### Implementation Priority

#### ✅ **Phase 1: Immediate Manual Fix** (NOW):
```bash
cd infra/terraform
terraform import aws_lambda_alias.coderipple_orchestrator_alias coderipple-orchestrator/prod
terraform import aws_api_gateway_rest_api.webhook_api 8v94cdsv9d
terraform import aws_api_gateway_stage.webhook_stage 8v94cdsv9d/prod
terraform apply
```

#### ✅ **Phase 2: Workflow Logic Fix** (SYSTEMATIC):
- **Update import syntax** in workflow file
- **Fix duplicate handling** logic
- **Test with future deployments**

### Expected Results
With Unit 15.8 implementation:
- ✅ **Lambda alias import succeeds** with correct `/` syntax
- ✅ **API Gateway import succeeds** with single ID handling
- ✅ **Complete deployment success** without ResourceConflictException
- ✅ **All import gaps resolved** from Units 15.3-15.8

### Integration with Previous Units
**Unit 15.8 completes the import syntax fixes**:
- **Units 15.3-15.5**: Fixed missing resource imports
- **Unit 15.6**: Fixed runtime compatibility
- **Unit 15.7**: Fixed environment variable mismatches
- **Unit 15.8**: Fixed import syntax and duplicate handling

**Unit 15.8 Status: ✅ READY - Critical import syntax fixes prepared for immediate implementation**
