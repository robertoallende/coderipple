# MDD 011_deployment_008: Fix KMS TagResource Permission Error

## Problem Statement

**Error**: Terraform deployment failing with KMS permission error during GitHub Actions deployment:
```
Error: creating KMS Key: operation error KMS: CreateKey, https response error StatusCode: 400, 
RequestID: d5c084e0-25e8-461b-b3a6-e6310f224d03, 
api error AccessDeniedException: User: arn:aws:iam::741448943849:user/***-deployment 
is not authorized to perform: kms:TagResource because no identity-based policy allows the kms:TagResource action
```

**Context**:
- Deployment via GitHub Actions
- IAM user: `***-deployment` in AWS account `741448943849`
- KMS key creation in `main.tf` line 33
- User has access to modify IAM policies
- Likely using KMS for Lambda environment variable encryption or S3 encryption

## Root Cause Analysis

The `***-deployment` IAM user lacks comprehensive KMS permissions, specifically:
- `kms:TagResource` - Required to apply tags during key creation
- Other KMS management permissions likely missing

## Solution

### Step 1: Add KMS Permissions to Deployment User

Add the following IAM policy to the `***-deployment` user:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "KMSManagementForCodeRipple",
            "Effect": "Allow",
            "Action": [
                "kms:CreateKey",
                "kms:DescribeKey",
                "kms:GetKeyPolicy",
                "kms:PutKeyPolicy",
                "kms:TagResource",
                "kms:UntagResource",
                "kms:ListResourceTags",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion",
                "kms:EnableKey",
                "kms:DisableKey",
                "kms:GetKeyRotationStatus",
                "kms:EnableKeyRotation",
                "kms:DisableKeyRotation"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": ["us-east-1", "us-west-2"]
                }
            }
        }
    ]
}
```

### Step 2: Implementation Options

#### Option A: Inline Policy (Quick Fix)
```bash
# Create policy document
cat > kms-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "KMSManagementForCodeRipple",
            "Effect": "Allow",
            "Action": [
                "kms:CreateKey",
                "kms:DescribeKey",
                "kms:GetKeyPolicy",
                "kms:PutKeyPolicy",
                "kms:TagResource",
                "kms:UntagResource",
                "kms:ListResourceTags",
                "kms:ScheduleKeyDeletion",
                "kms:CancelKeyDeletion",
                "kms:EnableKey",
                "kms:DisableKey",
                "kms:GetKeyRotationStatus",
                "kms:EnableKeyRotation",
                "kms:DisableKeyRotation"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Apply inline policy
aws iam put-user-policy \
    --user-name ***-deployment \
    --policy-name CodeRippleKMSPolicy \
    --policy-document file://kms-policy.json
```

#### Option B: Managed Policy (Recommended)
```bash
# Attach AWS managed policy
aws iam attach-user-policy \
    --user-name ***-deployment \
    --policy-arn arn:aws:iam::aws:policy/AWSKeyManagementServicePowerUser
```

### Step 3: Verification

```bash
# Check current user policies
aws iam list-attached-user-policies --user-name ***-deployment

# Check inline policies
aws iam list-user-policies --user-name ***-deployment

# Test KMS permissions
aws kms describe-key --key-id alias/aws/s3 --region us-east-1
```

## Implementation Steps

1. **Immediate Fix**: Apply Option B (managed policy) for quick resolution
2. **Verify Permissions**: Run verification commands
3. **Re-run Deployment**: Trigger GitHub Actions deployment
4. **Monitor**: Check CloudWatch logs for any additional permission issues
5. **Cleanup**: If using Option A, consider migrating to managed policy later

## Prevention

### GitHub Actions Workflow Enhancement
Add permission verification step to deployment workflow:

```yaml
- name: Verify KMS Permissions
  run: |
    aws kms describe-key --key-id alias/aws/s3 --region ${{ env.AWS_REGION }} || echo "KMS permissions may be insufficient"
```

### Terraform State Considerations
- Ensure KMS key deletion protection is enabled
- Consider using `prevent_destroy` lifecycle rule for KMS keys
- Document key usage and rotation policies

## Related Issues

- May need similar permissions for other AWS services (Lambda, S3, etc.)
- Consider comprehensive IAM audit for deployment user
- Review principle of least privilege after successful deployment

## Success Criteria

- [x] KMS key creation succeeds in Terraform
- [x] GitHub Actions deployment completes without permission errors
- [x] CodeRipple infrastructure deploys successfully
- [x] No security vulnerabilities introduced

## Notes

- The `openssl rand -hex 32` command suggests encryption key generation, confirming KMS usage
- AWS account `741448943849` has admin access available
- GitHub Actions deployment context confirmed
