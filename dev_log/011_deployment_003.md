# 11.3 AWS Region Unification Plan

## Overview
Unify all AWS region references across the CodeRipple project to use `us-west-2` consistently, eliminating region inconsistencies that could cause deployment failures.

## Current State Analysis
- **Terraform configuration**: Uses `ap-southeast-2` (Sydney) as default
- **GitHub Actions workflow**: Expects `us-west-2` (Oregon)
- **Documentation**: Mixed references to both regions
- **Bootstrap implementation**: Will fail due to region mismatch
- **Impact**: S3 bucket creation and state management will fail

## Requirements

### Functional Requirements
- **FR-11.3.1**: Update Terraform variables to use `us-west-2` as default region
- **FR-11.3.2**: Ensure GitHub Actions workflow uses `us-west-2` consistently
- **FR-11.3.3**: Update all documentation references to reflect `us-west-2`
- **FR-11.3.4**: Validate all AWS resource ARNs use correct region
- **FR-11.3.5**: Update backend configuration examples to use `us-west-2`

### Non-Functional Requirements
- **NFR-11.3.1**: Changes must not break existing Terraform state (if any)
- **NFR-11.3.2**: All region references must be parameterized, not hardcoded
- **NFR-11.3.3**: Documentation must be consistent across all files
- **NFR-11.3.4**: Changes must be backward compatible with existing AWS resources

## Design Decisions

### Decision 1: Target Region Selection
**Chosen**: `us-west-2` (Oregon, USA)
**Alternatives Considered**: `ap-southeast-2` (Sydney), `us-east-1` (Virginia)
**Rationale**: 
- Lower latency for North American users
- GitHub Actions workflow already expects this region
- Well-established AWS region with full service availability
- Cost-effective for development workloads

### Decision 2: Update Strategy
**Chosen**: Comprehensive update across all configuration files
**Alternatives Considered**: Gradual migration, environment-specific regions
**Rationale**: Eliminates confusion, ensures consistency, prevents deployment failures

### Decision 3: Parameterization Approach
**Chosen**: Use Terraform variables and GitHub Secrets for region configuration
**Alternatives Considered**: Hardcoded values, environment-specific configs
**Rationale**: Maintains flexibility while ensuring consistency

## Implementation Plan

### Phase 1: Terraform Configuration Updates
1. **Update variables.tf**
   - Change default region from `ap-southeast-2` to `us-west-2`
   - Ensure all region references use the variable

2. **Update backend configuration**
   - Update backend.tf comments and examples
   - Ensure S3 backend uses correct region

3. **Validate resource ARNs**
   - Check all ARN constructions use `var.aws_region`
   - Ensure no hardcoded region references

### Phase 2: GitHub Actions Workflow Updates
1. **Verify workflow configuration**
   - Confirm GitHub Actions uses `us-west-2`
   - Update any hardcoded region references
   - Ensure secrets configuration matches

2. **Update bootstrap logic**
   - Verify S3 bucket creation uses correct region
   - Update backend migration commands

### Phase 3: Documentation Updates
1. **Update development logs**
   - Fix region references in existing dev_log files
   - Update deployment documentation
   - Correct README and setup instructions

2. **Update configuration examples**
   - Fix terraform.tfvars.example
   - Update deployment guides
   - Correct troubleshooting documentation

### Phase 4: Validation and Testing
1. **Configuration validation**
   - Run terraform validate
   - Check for any remaining region inconsistencies
   - Verify all ARNs are correctly constructed

2. **Documentation review**
   - Ensure all files reference `us-west-2`
   - Check for any missed references
   - Validate examples and commands

## Technical Specifications

### Target Region Configuration
- **Primary Region**: `us-west-2` (Oregon)
- **Availability Zones**: `us-west-2a`, `us-west-2b`, `us-west-2c`
- **S3 Bucket Region**: `us-west-2`
- **Lambda Region**: `us-west-2`
- **API Gateway Region**: `us-west-2`

### Files to Update
- `infra/terraform/variables.tf` - Default region value
- `infra/terraform/backend.tf` - Example configurations
- `dev_log/009_aws_02.md` - Infrastructure documentation
- `dev_log/011_deployment_002.md` - Bootstrap documentation
- Any other files with region references

### Validation Checklist
- [ ] All Terraform variables use `us-west-2`
- [ ] GitHub Actions workflow uses `us-west-2`
- [ ] Documentation consistently references `us-west-2`
- [ ] No hardcoded region references remain
- [ ] ARN constructions use variables
- [ ] Backend examples use correct region

## Success Criteria
- All AWS region references consistently use `us-west-2`
- Bootstrap action works without region-related errors
- Terraform validation passes without warnings
- Documentation provides consistent guidance
- No hardcoded region references remain in codebase

## Risk Mitigation
- **Risk**: Breaking existing AWS resources in different regions
  **Mitigation**: This is a new deployment, no existing resources to conflict
- **Risk**: Missing region references during update
  **Mitigation**: Comprehensive search and systematic file-by-file review
- **Risk**: GitHub Secrets misconfiguration
  **Mitigation**: Validate secrets match expected region configuration

This plan ensures CodeRipple's AWS infrastructure deploys consistently to `us-west-2`, eliminating the region mismatch that would prevent successful bootstrap and deployment operations.
