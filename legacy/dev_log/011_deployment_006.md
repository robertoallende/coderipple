# 11.6 Advanced Security Hardening Implementation Plan

## Overview
Address the remaining 17 security vulnerabilities identified by Checkov security scan after implementing basic security hardening (11.4), focusing on advanced security configurations for production-ready deployment.

## Current State Analysis
- **Security scan results**: 17 failed checks remaining (down from 22)
- **Progress**: Basic security hardening (11.4) reduced failures by 22%
- **Remaining issues**: Advanced security configurations, compliance requirements
- **Risk level**: Medium - functional and secure, but missing enterprise-grade features
- **Impact**: Advanced security features needed for production compliance

## Requirements

### Functional Requirements
- **FR-11.6.1**: Add KMS key policy for proper access control
- **FR-11.6.2**: Enable CloudWatch Log Group KMS encryption
- **FR-11.6.3**: Enable API Gateway X-Ray tracing and caching
- **FR-11.6.4**: Add S3 bucket lifecycle configuration
- **FR-11.6.5**: Implement API Gateway request validation
- **FR-11.6.6**: Configure API Gateway method settings properly
- **FR-11.6.7**: Add S3 access logging configuration

### Non-Functional Requirements
- **NFR-11.6.1**: Security enhancements must not impact webhook functionality
- **NFR-11.6.2**: Performance impact must be minimal (< 10% latency increase)
- **NFR-11.6.3**: Cost increase must be reasonable (< $20/month additional)
- **NFR-11.6.4**: Configuration must follow AWS security best practices

### Optional Requirements (Enterprise Features)
- **OR-11.6.1**: Lambda VPC configuration (deferred - adds complexity)
- **OR-11.6.2**: Lambda code signing (deferred - requires signing infrastructure)
- **OR-11.6.3**: WAF protection for API Gateway (deferred - adds cost)
- **OR-11.6.4**: S3 cross-region replication (deferred - not needed for dev)
- **OR-11.6.5**: Client certificate authentication (deferred - GitHub webhooks incompatible)

## Design Decisions

### Decision 1: Security vs Functionality Balance
**Chosen**: Implement security features that don't break GitHub webhook functionality
**Alternatives Considered**: Full enterprise security, minimal security
**Rationale**: GitHub webhooks have specific requirements that conflict with some security features

### Decision 2: Cost vs Security Trade-offs
**Chosen**: Implement cost-effective security improvements, defer expensive features
**Alternatives Considered**: Full enterprise security regardless of cost
**Rationale**: Development project needs good security but not enterprise-grade costs

### Decision 3: Deferred Security Features
**Chosen**: Defer Lambda VPC, code signing, WAF, and S3 replication
**Alternatives Considered**: Implement all security features
**Rationale**: These features add significant complexity/cost without proportional security benefit for this use case

## Implementation Plan

### Phase 1: KMS and Encryption Enhancements
1. **Add KMS key policy**
   - Define explicit key usage policies
   - Grant access to necessary AWS services
   - Follow least privilege principles

2. **Enable CloudWatch Log Group encryption**
   - Add KMS encryption to Lambda log group
   - Add KMS encryption to API Gateway log group
   - Update IAM permissions for encrypted logs

### Phase 2: API Gateway Security Enhancements
1. **Enable X-Ray tracing**
   - Enable tracing at API Gateway stage level
   - Configure tracing sampling rules
   - Update IAM permissions

2. **Configure caching (with webhook considerations)**
   - Enable caching for appropriate methods
   - Disable caching for webhook endpoint (GitHub requires fresh responses)
   - Configure cache key parameters

3. **Add request validation**
   - Create request validator for webhook endpoint
   - Define request schema validation
   - Configure error responses

4. **Fix method settings**
   - Disable data trace (security requirement)
   - Enable metrics and appropriate logging
   - Configure throttling settings

### Phase 3: S3 Security Enhancements
1. **Add lifecycle configuration**
   - Configure versioning lifecycle rules
   - Set up intelligent tiering for cost optimization
   - Configure deletion policies

2. **Enable access logging**
   - Create separate S3 bucket for access logs
   - Configure access logging for state bucket
   - Set up log retention policies

### Phase 4: Validation and Testing
1. **Security scan validation**
   - Re-run Checkov security scan
   - Verify critical issues resolved
   - Document acceptable remaining risks

2. **Functional testing**
   - Test GitHub webhook functionality
   - Validate API Gateway caching behavior
   - Confirm logging and monitoring

## Technical Specifications

### KMS Key Policy
```hcl
resource "aws_kms_key" "coderipple_key" {
  description             = "CodeRipple encryption key for S3, Lambda, and other resources"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
}
```

### CloudWatch Log Group Encryption
```hcl
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.coderipple_key.arn
}
```

### API Gateway Caching Configuration
```hcl
resource "aws_api_gateway_stage" "webhook_stage" {
  # ... existing configuration ...
  
  xray_tracing_enabled = true
  
  cache_cluster_enabled = true
  cache_cluster_size    = "0.5"  # Smallest size for cost efficiency
}

resource "aws_api_gateway_method_settings" "webhook_method_settings" {
  # ... existing configuration ...
  
  settings {
    metrics_enabled    = true
    data_trace_enabled = false  # Security requirement
    logging_level      = "INFO"
    
    # Caching settings - disabled for webhook endpoint
    caching_enabled = false  # GitHub webhooks need fresh responses
    
    throttling_rate_limit  = 100
    throttling_burst_limit = 50
  }
}
```

### S3 Lifecycle Configuration
```hcl
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    id     = "terraform_state_lifecycle"
    status = "Enabled"

    versioning {
      newer_noncurrent_versions = 5
    }

    noncurrent_version_expiration {
      noncurrent_days = 90
    }
  }
}
```

## Security Issues Addressed

### High Priority (Will Fix)
1. **CKV2_AWS_64**: KMS key policy definition ✅
2. **CKV_AWS_158**: CloudWatch Log Group KMS encryption ✅
3. **CKV_AWS_73**: API Gateway X-Ray tracing ✅
4. **CKV_AWS_120**: API Gateway caching (with webhook considerations) ✅
5. **CKV_AWS_225**: API Gateway method caching settings ✅
6. **CKV_AWS_276**: Disable API Gateway data tracing ✅
7. **CKV2_AWS_61**: S3 bucket lifecycle configuration ✅
8. **CKV_AWS_18**: S3 bucket access logging ✅
9. **CKV2_AWS_53**: API Gateway request validation ✅

### Deferred (Acceptable Risk for Development)
1. **CKV_AWS_272**: Lambda code signing (requires signing infrastructure)
2. **CKV_AWS_117**: Lambda VPC configuration (adds complexity, not needed for webhooks)
3. **CKV_AWS_59**: API Gateway authorization (conflicts with GitHub webhook requirements)
4. **CKV2_AWS_51**: Client certificate authentication (incompatible with GitHub webhooks)
5. **CKV2_AWS_29**: WAF protection (adds significant cost for development)
6. **CKV_AWS_144**: S3 cross-region replication (not needed for development)
7. **CKV2_AWS_62**: S3 event notifications (not needed for Terraform state)

## Success Criteria
- Checkov security scan shows ≤ 8 failed checks (50% reduction from current 17)
- All high-priority security issues resolved
- GitHub webhook functionality remains intact
- API Gateway caching works appropriately (disabled for webhooks)
- CloudWatch logs encrypted with KMS
- S3 bucket has proper lifecycle and logging
- Performance impact < 10% latency increase
- Cost increase < $20/month

## Risk Mitigation
- **Risk**: API Gateway caching breaks webhook functionality
  **Mitigation**: Disable caching specifically for webhook endpoint while enabling for stage
- **Risk**: Request validation rejects valid GitHub webhooks
  **Mitigation**: Create permissive validation schema that accepts GitHub webhook format
- **Risk**: KMS encryption increases costs significantly
  **Mitigation**: Use single KMS key for all resources, enable key rotation for cost efficiency
- **Risk**: S3 access logging creates recursive logging loop
  **Mitigation**: Use separate bucket for access logs with different configuration

This plan addresses the most critical remaining security issues while maintaining functionality and reasonable costs for the CodeRipple development environment.
