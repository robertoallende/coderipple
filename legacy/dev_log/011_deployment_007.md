# 11.7 GitHub Actions Variable Name Alignment

## Overview
Fix the variable name mismatch between GitHub Actions workflow environment variables and Terraform variable definitions that is causing the bootstrap process to hang while prompting for manual input.

## Current State Analysis
- **Bootstrap status**: Stuck at variable input prompt for `var.github_repo_name`
- **Root cause**: GitHub Actions workflow uses `github_repository_*` naming
- **Terraform expects**: `github_repo_*` naming (shorter form)
- **Impact**: Bootstrap cannot proceed automatically, requires manual intervention
- **Duration stuck**: 6+ minutes waiting for variable input

## Requirements

### Functional Requirements
- **FR-11.7.1**: Align GitHub Actions environment variable names with Terraform variable names
- **FR-11.7.2**: Ensure bootstrap process runs without manual input prompts
- **FR-11.7.3**: Maintain consistency across all GitHub repository-related variables
- **FR-11.7.4**: Update any references to the old variable names in workflow outputs

### Non-Functional Requirements
- **NFR-11.7.1**: Changes must not break existing GitHub Secrets configuration
- **NFR-11.7.2**: Variable names must be clear and consistent
- **NFR-11.7.3**: Changes must be backward compatible with existing infrastructure

## Design Decisions

### Decision 1: Variable Naming Convention
**Chosen**: Use shorter `github_repo_*` naming to match Terraform variables
**Alternatives Considered**: Change Terraform variables to match workflow, use mapping
**Rationale**: Terraform variables are already defined and used throughout infrastructure code

### Decision 2: GitHub Secrets Update Strategy
**Chosen**: Update GitHub Secrets to match new variable names
**Alternatives Considered**: Keep existing secrets, use variable mapping
**Rationale**: Direct alignment is cleaner and reduces complexity

### Decision 3: Workflow Update Scope
**Chosen**: Update all references to GitHub repository variables in workflow
**Alternatives Considered**: Partial update, gradual migration
**Rationale**: Complete alignment prevents future confusion and issues

## Implementation Plan

### Phase 1: Identify Variable Mismatches
1. **Current GitHub Actions variables**:
   - `TF_VAR_github_repository_owner`
   - `TF_VAR_github_repository_name`

2. **Expected Terraform variables**:
   - `TF_VAR_github_repo_owner`
   - `TF_VAR_github_repo_name`

### Phase 2: Update GitHub Actions Workflow
1. **Update environment variable declarations**
   - Change `github_repository_owner` → `github_repo_owner`
   - Change `github_repository_name` → `github_repo_name`

2. **Update workflow output references**
   - Fix any summary outputs that reference the old variable names
   - Ensure consistency throughout the workflow file

### Phase 3: Update GitHub Secrets
1. **Create new secrets with correct names**:
   - `TF_VAR_github_repo_owner`
   - `TF_VAR_github_repo_name`

2. **Remove old secrets** (after testing):
   - `TF_VAR_github_repository_owner`
   - `TF_VAR_github_repository_name`

### Phase 4: Testing and Validation
1. **Test bootstrap process**
   - Cancel current stuck workflow
   - Re-run bootstrap with updated variables
   - Verify automatic progression without prompts

2. **Validate variable resolution**
   - Confirm Terraform receives all required variables
   - Check that no manual input prompts appear

## Technical Specifications

### GitHub Actions Environment Variables (Updated)
```yaml
env:
  # GitHub repository configuration
  TF_VAR_github_repo_owner: ${{ secrets.TF_VAR_github_repo_owner }}
  TF_VAR_github_repo_name: ${{ secrets.TF_VAR_github_repo_name }}
  TF_VAR_github_webhook_secret: ${{ secrets.TF_VAR_github_webhook_secret }}
```

### Required GitHub Secrets
```
TF_VAR_aws_region
TF_VAR_github_repo_owner          # Updated name
TF_VAR_github_repo_name           # Updated name  
TF_VAR_github_webhook_secret
TF_VAR_coderipple_min_quality_score
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

### Terraform Variables (No Changes Needed)
```hcl
variable "github_repo_owner" {
  description = "GitHub repository owner (username or organization)"
  type        = string
}

variable "github_repo_name" {
  description = "GitHub repository name"
  type        = string
}
```

## Files to Update
- `.github/workflows/deploy-infrastructure.yml` - Environment variable names
- GitHub repository secrets configuration
- Any documentation referencing the old variable names

## Success Criteria
- Bootstrap process completes without manual input prompts
- All Terraform variables receive values from GitHub Actions environment
- No variable name mismatches between workflow and Terraform
- Workflow runs successfully from start to finish
- S3 bucket creation and state migration complete automatically

## Risk Mitigation
- **Risk**: Updating secrets breaks existing workflows
  **Mitigation**: Update workflow first, then secrets, test immediately
- **Risk**: Missing variable references in workflow
  **Mitigation**: Search for all instances of old variable names before updating
- **Risk**: Bootstrap still fails after variable fix
  **Mitigation**: Have fallback plan to check other potential issues (permissions, regions)

This fix addresses the immediate blocking issue preventing the bootstrap process from completing automatically.
