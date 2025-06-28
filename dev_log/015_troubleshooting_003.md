# Unit 015_troubleshooting_003: Terraform Variable Validation Failures

## Objective

Resolve critical Terraform deployment failures caused by invalid variable values that prevent infrastructure deployment, despite GitHub Actions marking the job as "successful" due to inadequate error handling.

## Problem Analysis

### Critical Issue Identified
The Terraform deployment is **failing during the plan stage** with variable validation errors:

```
Error: Invalid value for variable
  on variables.tf line 95:
  95: variable "log_retention_days" {
Log retention days must be a valid CloudWatch retention period.

Error: Invalid value for variable
  on variables.tf line 112:
 112: variable "environment" {
Environment must be one of: dev, staging, prod.

Error: Terraform exited with code 1.
```

### Root Cause Analysis
The deployment appears successful in GitHub Actions but actually fails because:

#### ❌ **Variable Validation Failures**:
1. **log_retention_days**: Invalid CloudWatch retention period value
2. **environment**: Value not in allowed list (dev, staging, prod)

#### ❌ **GitHub Actions Error Handling Issue**:
- Terraform plan fails with exit code 1
- GitHub Actions job still shows as "succeeded" 
- No terraform-outputs-production artifact created
- Validation job fails due to missing infrastructure

### Pipeline Flow Issue
```
✅ Build Layers → ❌ Terraform Plan Fails → ✅ Job Marked Success → ❌ Validation Fails
```

## Implementation

### Issue Classification: CRITICAL
This is a **critical configuration error** that prevents:
- ❌ Terraform plan execution
- ❌ Infrastructure deployment
- ❌ Lambda function creation
- ❌ terraform-outputs-production artifact generation

### Variable Configuration Fixes

#### 1. Fix log_retention_days Variable
**Problem**: Current value not a valid CloudWatch retention period
**Valid CloudWatch retention periods**: 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653

**Current workflow sets**: `TF_VAR_log_retention_days: 14`
**Status**: Should be valid - need to check variable definition

#### 2. Fix environment Variable  
**Problem**: Current value not in allowed list
**Allowed values**: dev, staging, prod
**Current workflow sets**: `TF_VAR_environment: production`
**Issue**: Workflow uses "production" but validation expects "prod"

### Solution Implementation

#### 1. Update GitHub Actions Workflow Variables
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`

```yaml
env:
  # Fix environment variable - change from 'production' to 'prod'
  TF_VAR_environment: prod  # Changed from 'production'
  
  # Ensure log retention is valid CloudWatch period
  TF_VAR_log_retention_days: 14  # Should be valid, check variable definition
```

#### 2. Verify Terraform Variable Definitions
**File**: `infra/terraform/variables.tf`

Check variable validation rules:
```hcl
variable "log_retention_days" {
  # Verify validation rule allows 14
}

variable "environment" {
  # Verify validation rule includes "prod"
}
```

#### 3. Fix GitHub Actions Error Handling
The workflow should fail when Terraform plan fails:
```yaml
- name: Terraform Plan
  id: plan
  run: |
    terraform plan -out=tfplan
    # Ensure step fails if terraform plan fails
  continue-on-error: false
```

## AI Interactions

### Problem Identification Strategy
- **Log Analysis**: Identified Terraform variable validation failures from build logs
- **GitHub Actions Behavior**: Recognized job success despite Terraform failure
- **Variable Mapping**: Traced workflow environment variables to Terraform variables
- **Validation Rule Analysis**: Identified specific validation constraints causing failures

### Solution Approach
- **Variable Value Correction**: Fix environment variable from "production" to "prod"
- **Validation Rule Review**: Verify log_retention_days validation logic
- **Error Handling**: Ensure proper failure propagation in GitHub Actions
- **Testing Strategy**: Validate fixes before deployment

## Files to Modify

### 1. GitHub Actions Workflow (PRIMARY FIX)
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`
**Change**:
```yaml
# Line ~32: Fix environment variable
TF_VAR_environment: prod  # Changed from 'production'
```

### 2. Terraform Variables (VERIFICATION)
**File**: `infra/terraform/variables.tf`
**Check**: Verify validation rules for both variables

### 3. Workflow Error Handling (IMPROVEMENT)
**File**: `.github/workflows/deploy-layer-based-infrastructure.yml`
**Add**: Proper error handling for Terraform plan failures

## Status: In Progress - Critical Configuration Errors Identified

### Immediate Priority
**CRITICAL**: Fix environment variable value in GitHub Actions workflow

### Required Changes
1. **Environment Variable**: Change `TF_VAR_environment: production` to `TF_VAR_environment: prod`
2. **Validation Check**: Verify log_retention_days validation rule
3. **Error Handling**: Ensure Terraform failures properly fail the GitHub Actions job

### Expected Resolution
Once variable values are corrected:
- ✅ Terraform plan will succeed
- ✅ Terraform apply will execute
- ✅ Lambda function will be deployed with layer-based architecture
- ✅ terraform-outputs-production artifact will be created
- ✅ End-to-end validation will succeed

### Next Steps
1. **Fix environment variable** in GitHub Actions workflow
2. **Verify Terraform variable validation rules**
3. **Re-run deployment workflow**
4. **Confirm successful infrastructure deployment**

**Unit 15.3 Status: 🔍 IN PROGRESS - Critical variable validation failures identified, fix ready for implementation**
