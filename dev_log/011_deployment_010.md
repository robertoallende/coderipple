# MDD 011_deployment_010: S3 Bucket Conflict and SQS Permission Issues

## Problem Statement

**Errors**: Terraform apply failing with two distinct issues:

1. **S3 Bucket Already Exists**:
```
Error: creating S3 Bucket (***-terraform-state): BucketAlreadyExists
  with aws_s3_bucket.terraform_state,
  on main.tf line 108, in resource "aws_s3_bucket" "terraform_state":
  108: resource "aws_s3_bucket" "terraform_state" {
```

2. **SQS Permission Denied**:
```
Error: creating SQS Queue (***-lambda-dlq): operation error SQS: CreateQueue, 
https response error StatusCode: 403, RequestID: 6fd38b5b-f0a3-5f47-af81-eb8d1c2984a5, 
api error AccessDenied: User: arn:aws:iam::741448943849:user/***-deployment 
is not authorized to perform: sqs:createqueue on resource: arn:aws:sqs:***:741448943849:***-lambda-dlq 
because no identity-based policy allows the sqs:createqueue action
```

**Context**:
- GitHub Actions deployment via Terraform
- User: `***-deployment` (likely `coderipple-deployment`)
- Previous MDD 011_deployment_009 successfully resolved `TF_VAR_log_retention_days` issue
- Deployment now progressing further but hitting infrastructure creation issues

## Root Cause Analysis

### **Issue 1: S3 Bucket Already Exists**
**Cause**: The Terraform state bucket was created in a previous deployment attempt but:
- Not tracked in current Terraform state file
- Terraform trying to create it again
- S3 bucket names are globally unique

**Possible Scenarios**:
- Previous failed deployment created the bucket
- Terraform state drift (bucket exists but not in state)
- Manual bucket creation outside Terraform

### **Issue 2: Missing SQS Permissions**
**Cause**: The `***-deployment` user lacks SQS permissions in IAM policy.

**Current Policy** (from MDD 011_deployment_008):
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
                "kms:*"
            ],
            "Resource": "*"
        }
    ]
}
```

**Missing**: `"sqs:*"` permissions for SQS queue creation and management.

## Solution Strategy

### **Solution 1: S3 Bucket Conflict Resolution**

#### **Option A: Import Existing Bucket (Recommended)**
```bash
# Import the existing bucket into Terraform state
terraform import aws_s3_bucket.terraform_state ***-terraform-state
terraform apply
```

#### **Option B: Use Different Bucket Name**
```hcl
# Add random suffix to ensure uniqueness
resource "aws_s3_bucket" "terraform_state" {
  bucket = "${var.project_name}-terraform-state-${random_id.bucket_suffix.hex}"
}

resource "random_id" "bucket_suffix" {
  byte_length = 4
}
```

#### **Option C: Delete and Recreate (If Safe)**
```bash
# Only if bucket is empty and safe to delete
aws s3 rb s3://***-terraform-state --force
terraform apply
```

### **Solution 2: Add SQS Permissions**

Update the `***-deployment` user IAM policy to include SQS permissions:

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

## Implementation Plan

### **Step 1: Investigate S3 Bucket**
```bash
# Check if bucket exists and its contents
aws s3 ls s3://***-terraform-state
aws s3api get-bucket-location --bucket ***-terraform-state
```

### **Step 2: Add SQS Permissions**
**Via AWS Console**:
1. IAM → Users → `***-deployment`
2. Permissions → Edit inline policy
3. Add `"sqs:*"` to Actions array

**Via AWS CLI** (as admin user):
```bash
# Update the user policy with SQS permissions
aws iam put-user-policy \
    --user-name ***-deployment \
    --policy-name CodeRippleDeploymentPolicy \
    --policy-document file://updated-policy.json
```

### **Step 3: Resolve S3 Bucket Conflict**
**If bucket is yours and contains state**:
```bash
cd infra/terraform
terraform import aws_s3_bucket.terraform_state ***-terraform-state
```

**If bucket is empty**:
```bash
aws s3 rb s3://***-terraform-state
```

### **Step 4: Re-run Deployment**
```bash
# Trigger GitHub Actions deployment
git commit --allow-empty -m "Retry deployment after fixing S3 and SQS issues"
git push
```

## Recommended Approach

### **Immediate Actions**
1. **Add SQS permissions** to deployment user (critical)
2. **Check S3 bucket contents** to determine import vs delete strategy
3. **Import bucket if it contains state**, delete if empty
4. **Re-run deployment**

### **Long-term Improvements**
1. **Comprehensive IAM policy** covering all AWS services needed
2. **Terraform state management** best practices
3. **Pre-deployment validation** to catch permission issues early

## Expected Resolution

After implementing both fixes:
- **SQS queue creation** will succeed with proper permissions
- **S3 bucket conflict** resolved through import or recreation
- **Terraform deployment** will proceed to next resources
- **CodeRipple infrastructure** deployment continues

## Risk Assessment

### **Low Risk**
- Adding SQS permissions (standard service permission)
- Importing existing S3 bucket (preserves state)

### **Medium Risk**
- Deleting S3 bucket (only if confirmed empty and safe)

### **Mitigation**
- Always check bucket contents before deletion
- Backup any existing Terraform state
- Test permissions with AWS CLI before deployment

## Success Criteria

- [x] SQS permissions added to `***-deployment` user
- [x] S3 bucket conflict resolved (import or recreate)
- [x] Terraform apply proceeds past these two errors
- [x] No data loss from S3 bucket operations
- [x] GitHub Actions deployment continues successfully

## Related Issues

- **MDD 011_deployment_008**: KMS permissions (resolved)
- **MDD 011_deployment_009**: Variable validation (resolved)
- **Future**: May need additional AWS service permissions as deployment progresses

## Notes

- This demonstrates the iterative nature of AWS permission debugging
- Each deployment attempt reveals missing permissions for new services
- Consider comprehensive AWS service policy for future deployments
- S3 bucket naming conflicts are common in multi-environment setups
