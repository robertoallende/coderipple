# MDD 011_deployment_009: GitHub Actions Variable Management via MCP Servers

## Problem Statement

**Error**: Terraform plan failing with variable validation error:
```
Error: Invalid value for variable
  on variables.tf line 95:
  95: variable "log_retention_days" {

Log retention days must be a valid CloudWatch retention period.
This was checked by the validation rule at variables.tf:100,3-13.
```

**Context**:
- GitHub Actions deployment pipeline failing at Terraform plan stage
- `TF_VAR_log_retention_days` environment variable not being properly recognized
- Variable validation expects CloudWatch retention periods: `[1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653]`
- Current workflow sets `TF_VAR_log_retention_days: 14` in environment variables
- No conflicting repository secrets or variables found in GitHub console

## Root Cause Analysis

**Variable Precedence Issue**: The hardcoded environment variable in the GitHub Actions workflow may be experiencing:
1. **Type conversion problems** - String vs number handling
2. **Environment variable precedence conflicts**
3. **Terraform variable resolution issues** during GitHub Actions execution

**Current Configuration**:
```yaml
# .github/workflows/deploy-infrastructure.yml
env:
  TF_VAR_log_retention_days: 14  # Hardcoded in workflow
```

## Solution Strategy: MCP Server-Based Resolution

### **Approach**: Leverage GitHub and Terraform MCP Servers

**Available MCP Servers**:
- `github` - GitHub API integration for repository management
- `terraform` - Infrastructure as Code validation and management
- `git` - Repository operations

### **Step 1: GitHub MCP Server Diagnosis**
Use `github___` tools to:
- Check repository secrets and variables for conflicts
- Verify current GitHub Actions workflow configuration
- Review recent workflow run logs for variable handling

### **Step 2: GitHub MCP Server Implementation**
Use `github___` tools to:
- Add `TF_VAR_log_retention_days` as a repository secret with value `14`
- Remove hardcoded environment variable from workflow file
- Ensure proper variable precedence in GitHub Actions

### **Step 3: Terraform MCP Server Validation**
Use `terraform___` tools to:
- Validate variable configuration in `variables.tf`
- Test variable validation logic accepts value `14`
- Verify Terraform configuration syntax

### **Step 4: GitHub MCP Server Testing**
Use `github___` tools to:
- Trigger new workflow run
- Monitor deployment progress
- Verify Terraform plan succeeds

## Implementation Plan

### **Phase 1: Diagnosis via MCP**
```bash
# Use Q CLI with GitHub MCP server
q chat
# "Use github tools to check my repository secrets and variables for TF_VAR_log_retention_days"
# "Use terraform tools to validate my log_retention_days variable configuration"
```

### **Phase 2: Repository Secret Management**
```bash
# Use Q CLI with GitHub MCP server
q chat
# "Use github tools to add TF_VAR_log_retention_days as a repository secret with value 14"
```

### **Phase 3: Workflow Cleanup**
```yaml
# Remove from .github/workflows/deploy-infrastructure.yml
env:
  # TF_VAR_log_retention_days: 14  # Remove this line
  TF_VAR_api_gateway_name: coderipple-webhook-api
  TF_VAR_api_gateway_stage: dev
```

### **Phase 4: Validation and Testing**
```bash
# Use Q CLI with GitHub and Terraform MCP servers
q chat
# "Use terraform tools to validate my variables.tf configuration"
# "Use github tools to trigger a new deployment workflow"
```

## Expected Benefits

### **Immediate Resolution**
- **Proper Variable Handling**: GitHub secrets ensure correct type and precedence
- **Terraform Validation Success**: Value `14` is valid CloudWatch retention period
- **Deployment Pipeline Continuation**: Workflow proceeds past variable validation

### **Long-term Improvements**
- **Better Secret Management**: Sensitive/configurable values in GitHub secrets
- **Cleaner Workflow Files**: Reduced hardcoded values
- **MCP Server Integration**: Demonstrates programmatic GitHub/Terraform management

## Technical Advantages of MCP Approach

### **GitHub MCP Server Benefits**
- **Direct API Access**: No manual console navigation required
- **Programmatic Management**: Scriptable repository configuration
- **Workflow Integration**: Can trigger and monitor deployments

### **Terraform MCP Server Benefits**
- **Local Validation**: Test configurations before deployment
- **Syntax Checking**: Verify Terraform code correctness
- **Variable Analysis**: Debug variable resolution issues

### **Combined Workflow**
- **End-to-End Automation**: From diagnosis to resolution via Q CLI
- **Integrated Toolchain**: GitHub + Terraform operations in single interface
- **Reproducible Process**: Documented MCP server usage patterns

## Success Criteria

- [x] GitHub repository secret `TF_VAR_log_retention_days` created with value `14`
- [x] Hardcoded environment variable removed from workflow
- [x] Terraform variable validation passes
- [x] GitHub Actions deployment proceeds without variable errors
- [x] MCP server integration demonstrates programmatic DevOps management

## Risk Mitigation

### **Backup Strategy**
- Keep original workflow file backed up
- Test with Terraform plan before apply
- Monitor first deployment run closely

### **Rollback Plan**
- Restore hardcoded environment variable if needed
- Remove repository secret if conflicts arise
- Use manual GitHub console as fallback

## Related Components

- **GitHub Actions Workflow**: `.github/workflows/deploy-infrastructure.yml`
- **Terraform Variables**: `infra/terraform/variables.tf`
- **MCP Configuration**: Global MCP servers (github, terraform, git)
- **Repository Settings**: GitHub secrets and variables

## Documentation Impact

This approach demonstrates:
- **MCP Server Integration** for DevOps workflows
- **Programmatic GitHub Management** via Q CLI
- **Terraform Validation** through MCP tools
- **End-to-End Automation** for deployment issues

## Notes

- First practical application of GitHub MCP server for CodeRipple project
- Establishes pattern for MCP-based DevOps problem resolution
- Validates multi-MCP server coordination for complex workflows
- Demonstrates Q CLI as comprehensive DevOps management interface
