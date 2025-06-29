# 11.2 Bootstrap Action Implementation Plan

## Overview
Add a `bootstrap` action to the existing GitHub Actions workflow to handle first-time infrastructure setup, specifically creating the S3 bucket for Terraform remote state storage.

## Current State Analysis
- Existing workflow supports `plan`, `apply`, `destroy` actions
- Environment selection: `dev`, `staging`, `prod` (staging and prod to be removed)
- Terraform backend configured for S3 remote state
- Bootstrap functionality currently missing, causing "bucket does not exist" errors
- Project scope indicates dev-only deployment is sufficient

## Requirements

### Functional Requirements
- **FR-11.2.1**: Add `bootstrap` option to workflow action choices
- **FR-11.2.2**: Create S3 bucket for Terraform state storage when bootstrap is selected
- **FR-11.2.3**: Configure bucket with versioning, encryption, and security settings
- **FR-11.2.4**: Migrate from local state to remote S3 state after bucket creation
- **FR-11.2.5**: Support single dev environment (remove staging/prod complexity)
- **FR-11.2.6**: Handle bootstrap as one-time operation for dev environment
- **FR-11.2.7**: Simplify workflow by removing unused environment options

### Non-Functional Requirements
- **NFR-11.2.1**: Bootstrap process must be idempotent (safe to run multiple times)
- **NFR-11.2.2**: Must work in GitHub Actions environment without local dependencies
- **NFR-11.2.3**: Should provide clear logging and error messages
- **NFR-11.2.4**: Must maintain security best practices for S3 bucket configuration

## Design Decisions

### Decision 1: Workflow Integration Approach
**Chosen**: Extend existing workflow with conditional logic
**Alternatives Considered**: Separate bootstrap workflow, Makefile approach
**Rationale**: Maintains single workflow interface, consistent with existing pattern

### Decision 2: Environment Strategy
**Chosen**: Single dev environment only
**Alternatives Considered**: Multi-environment setup (dev/staging/prod)
**Rationale**: Project scope is development/demo focused, staging and prod environments add unnecessary complexity without business value

### Decision 3: State Migration Approach
**Chosen**: Automatic migration from local to remote state during bootstrap
**Alternatives Considered**: Manual migration step, separate migration action
**Rationale**: Reduces manual steps, ensures consistent state management

## Implementation Plan

### Phase 1: Workflow Configuration Updates
1. **Update workflow inputs**
   - Add `bootstrap` to action choices
   - Remove staging and prod environment options
   - Set dev as default and only environment option

2. **Add conditional step logic**
   - Bootstrap-specific initialization
   - Non-bootstrap initialization
   - Shared execution steps

### Phase 2: Bootstrap Logic Implementation
1. **S3 Bucket Creation**
   - Target specific Terraform resources
   - Apply bucket, versioning, encryption, security configurations
   - Use simplified dev-only naming convention

2. **State Migration**
   - Initialize with remote backend configuration
   - Migrate existing local state
   - Validate successful migration

### Phase 3: Integration and Testing
1. **Workflow Testing**
   - Test bootstrap action in dev environment
   - Verify subsequent plan/apply operations work
   - Test idempotent behavior

2. **Environment Simplification**
   - Remove staging and prod environment options from workflow
   - Update documentation to reflect dev-only deployment
   - Simplify bucket naming without environment suffixes

3. **Documentation Updates**
   - Update deployment instructions
   - Document bootstrap process
   - Add troubleshooting guidance

## Technical Specifications

### Workflow Input Schema
```yaml
action:
  type: choice
  options: [bootstrap, plan, apply, destroy]
  default: plan

# Environment selection removed - dev only
# Simplified workflow with single target environment
```

### S3 Bucket Configuration
- **Naming**: `coderipple-terraform-state` (simplified, dev-only)
- **Region**: `us-west-2`
- **Versioning**: Enabled
- **Encryption**: AES256
- **Public Access**: Blocked
- **State Key**: `coderipple/terraform.tfstate`

### Terraform Targets for Bootstrap
- `aws_s3_bucket.terraform_state`
- `aws_s3_bucket_versioning.terraform_state`
- `aws_s3_bucket_server_side_encryption_configuration.terraform_state`
- `aws_s3_bucket_public_access_block.terraform_state`

## Success Criteria
- Bootstrap action successfully creates S3 bucket on first run
- Subsequent bootstrap runs are idempotent (no errors, no changes)
- Plan/apply actions work correctly after bootstrap
- Simplified workflow with dev-only environment reduces complexity
- Clear error messages for common failure scenarios

## Risk Mitigation
- **Risk**: Bootstrap fails mid-process leaving inconsistent state
  **Mitigation**: Use targeted applies for atomic operations
- **Risk**: Workflow complexity from unused environments
  **Mitigation**: Remove staging/prod options, focus on dev-only deployment
- **Risk**: State migration failures
  **Mitigation**: Validate state migration success, provide rollback guidance

This plan aligns with CodeRipple's multi-agent architecture by ensuring the AWS infrastructure foundation (S3 state storage) is properly established before deploying the Lambda functions and Strands orchestration components.
