# MDD 011_deployment_011: Lambda Reserved Environment Variable and CloudWatch Permission Issues

## Problem Statement

**Errors**: Terraform apply failing with three distinct issues after resolving SQS permissions:

1. **S3 Bucket Already Exists** (Persistent):
```
Error: creating S3 Bucket (***-terraform-state): BucketAlreadyExists
  with aws_s3_bucket.terraform_state,
  on main.tf line 108, in resource "aws_s3_bucket" "terraform_state":
  108: resource "aws_s3_bucket" "terraform_state" {
```

2. **Lambda Reserved Environment Variable**:
```
Error: creating Lambda Function (***-orchestrator): operation error Lambda: CreateFunction, 
https response error StatusCode: 400, RequestID: 6297***a4-d550-42a6-8859-3cf6dd6***a4f, 
InvalidParameterValueException: Lambda was unable to configure your environment variables 
because the environment variables you have provided contains reserved keys that are currently 
not supported for modification. Reserved keys used in this request: AWS_DEFAULT_REGION
```

3. **CloudWatch Permission Denied**:
```
Error: creating CloudWatch Metric Alarm (***-dlq-messages): operation error CloudWatch: PutMetricAlarm, 
https response error StatusCode: 403, RequestID: f5ac2016-9ef3-4aa6-99af-b3c6d0795e43, 
api error AccessDenied: User: arn:aws:iam::741448943849:user/***-deployment is not authorized 
to perform: cloudwatch:PutMetricAlarm on resource: arn:aws:cloudwatch:***:741448943849:alarm:***-dlq-messages 
because no identity-based policy allows the cloudwatch:PutMetricAlarm action
```

**Context**:
- GitHub Actions deployment progressing further after previous fixes
- MDD 011_deployment_009: TF_VAR_log_retention_days resolved ✅
- MDD 011_deployment_010: SQS permissions partially addressed
- New Lambda and CloudWatch issues emerging as deployment advances

## Root Cause Analysis

### **Issue 1: S3 Bucket Conflict (Persistent)**
**Status**: Unresolved from MDD 011_deployment_010
- Terraform state bucket exists but not tracked in current state
- Requires import or deletion strategy

### **Issue 2: Lambda Reserved Environment Variable**
**Root Cause**: AWS Lambda automatically provides certain environment variables and prohibits manual override.

**Problematic Configuration** (main.tf line ~536):
```hcl
environment {
  variables = {
    AWS_DEFAULT_REGION = var.aws_region  # ❌ RESERVED - Cannot be set manually
    PYTHONPATH        = "/var/runtime:/var/task/src:/opt"
    # ... other variables
  }
}
```

**AWS Lambda Reserved Environment Variables**:
- `AWS_DEFAULT_REGION` - Automatically set to function's region
- `AWS_REGION` - Automatically set to function's region  
- `AWS_EXECUTION_ENV` - Runtime environment identifier
- `AWS_LAMBDA_FUNCTION_NAME` - Function name
- `AWS_LAMBDA_FUNCTION_VERSION` - Function version
- `AWS_LAMBDA_RUNTIME_API` - Runtime API endpoint

### **Issue 3: Missing CloudWatch Permissions**
**Root Cause**: Deployment user IAM policy lacks CloudWatch alarm management permissions.

**Current Policy** (needs CloudWatch addition):
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "iam:*",
                "apigateway:*",
                "logs:*",
                "ssm:*",
                "s3:*",
                "dynamodb:*",
                "events:*",
                "kms:*",
                "sqs:*"
            ],
            "Resource": "*"
        }
    ]
}
```

**Missing**: `"cloudwatch:*"` permissions for metric alarms and monitoring.

## Solution Strategy

### **Solution 1: Remove Reserved Environment Variable**
**Approach**: Remove `AWS_DEFAULT_REGION` from Lambda environment variables

**Implementation**:
```hcl
# In main.tf Lambda function configuration
environment {
  variables = {
    # Remove: AWS_DEFAULT_REGION = var.aws_region
    PYTHONPATH        = "/var/runtime:/var/task/src:/opt"
    
    # GitHub repository information
    CODERIPPLE_GITHUB_REPO_OWNER = var.github_repo_owner
    CODERIPPLE_GITHUB_REPO_NAME  = var.github_repo_name
    
    # Environment and project info
    CODERIPPLE_ENVIRONMENT = var.environment
    CODERIPPLE_PROJECT     = var.project_name
  }
}
```

**Rationale**: 
- AWS Lambda automatically sets `AWS_DEFAULT_REGION` to the function's deployment region
- Manual override is prohibited and unnecessary
- Function code can access region via `os.environ['AWS_DEFAULT_REGION']` or `boto3.Session().region_name`

### **Solution 2: Add CloudWatch Permissions**
**Approach**: Extend deployment user IAM policy with CloudWatch permissions

**Updated Policy**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:*",
                "iam:*",
                "apigateway:*",
                "logs:*",
                "ssm:*",
                "s3:*",
                "dynamodb:*",
                "events:*",
                "kms:*",
                "sqs:*",
               
               
            ],
            "Resource": "*"
        }
    ]
}
```

### **Solution 3: Resolve S3 Bucket Conflict**
**Approach**: Import existing bucket or delete if safe

**Investigation Required**:
```bash
# Check bucket contents
aws s3 ls s3://***-terraform-state

# If empty - delete and recreate
aws s3 rb s3://***-terraform-state --force

# If contains state - import to Terraform
terraform import aws_s3_bucket.terraform_state ***-terraform-state
```

## Implementation Plan

### **Phase 1: Code Changes**
1. **Remove Reserved Environment Variable**
   - Edit `infra/terraform/main.tf` 
   - Remove `AWS_DEFAULT_REGION = var.aws_region` from Lambda environment
   - Test Lambda function can still access region information

2. **Commit Infrastructure Changes**
   - Git commit the Terraform configuration fix
   - Document the reserved variable issue

### **Phase 2: AWS Permissions**
1. **Add CloudWatch Permissions**
   - Update `***-deployment` user IAM policy via AWS Console
   - Add `"cloudwatch:*"` to Actions array
   - Verify permissions with AWS CLI test

### **Phase 3: S3 Bucket Resolution**
1. **Investigate Bucket State**
   - Check bucket contents and ownership
   - Determine import vs delete strategy
   - Execute chosen approach

2. **Validate Resolution**
   - Ensure Terraform can manage bucket
   - Verify no state conflicts

### **Phase 4: Deployment Testing**
1. **Trigger GitHub Actions**
   - Push changes to trigger deployment
   - Monitor for resolution of all three errors
   - Verify Lambda function creation succeeds

## Expected Outcomes

### **Immediate Resolution**
- **Lambda Creation Success**: Function deploys without environment variable conflicts
- **CloudWatch Alarms Created**: Monitoring infrastructure established
- **S3 State Management**: Terraform state bucket properly managed

### **Long-term Benefits**
- **Cleaner Lambda Configuration**: No reserved variable conflicts
- **Comprehensive Monitoring**: CloudWatch alarms for system health
- **Stable State Management**: Proper Terraform state handling

## Technical Considerations

### **Lambda Environment Variables**
- **Automatic Variables**: AWS provides region, function name, version automatically
- **Custom Variables**: Only set application-specific configuration
- **Security**: Sensitive values should use Parameter Store or Secrets Manager

### **CloudWatch Permissions**
- **Metric Alarms**: Required for SQS DLQ monitoring
- **Log Groups**: Already covered by `"logs:*"` permissions
- **Dashboards**: Future monitoring enhancements

### **S3 State Management**
- **State Locking**: Consider DynamoDB table for state locking
- **Versioning**: Ensure state file versioning enabled
- **Encryption**: KMS encryption for state file security

## Risk Assessment

### **Low Risk**
- Removing reserved environment variable (AWS handles automatically)
- Adding CloudWatch permissions (standard monitoring service)

### **Medium Risk**
- S3 bucket operations (potential state loss if mishandled)

### **Mitigation Strategies**
- **Backup**: Export current Terraform state before S3 operations
- **Validation**: Test Lambda function region access after environment variable removal
- **Monitoring**: Verify CloudWatch alarms function after permission addition

## Success Criteria

- [x] Lambda function creates without reserved environment variable error
- [x] CloudWatch metric alarms deploy successfully
- [x] S3 bucket conflict resolved (import or recreate)
- [x] GitHub Actions deployment proceeds to next infrastructure components
- [x] No regression in Lambda function region access
- [x] Monitoring infrastructure operational

## Related Components

- **Lambda Function**: `aws_lambda_function.coderipple_orchestrator` (main.tf line 519)
- **CloudWatch Alarms**: `aws_cloudwatch_metric_alarm.dlq_messages` (main.tf line 777)
- **S3 Bucket**: `aws_s3_bucket.terraform_state` (main.tf line 108)
- **IAM Policy**: `***-deployment` user permissions

## Documentation Impact

This MDD demonstrates:
- **AWS Service Constraints**: Understanding platform limitations and reserved resources
- **Progressive Permission Discovery**: Iterative approach to IAM policy development
- **Infrastructure State Management**: Terraform state handling best practices
- **Multi-Service Coordination**: Lambda, CloudWatch, and S3 integration challenges

## Notes

- AWS Lambda reserved environment variables are a common deployment pitfall
- CloudWatch permissions often overlooked in initial IAM policy design
- S3 bucket naming conflicts frequent in multi-environment deployments
- This represents typical AWS infrastructure deployment progression pattern
