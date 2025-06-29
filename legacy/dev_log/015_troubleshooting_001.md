# Unit 015_troubleshooting_001: Terraform Duplicate Resource Configuration

## Objective

Resolve Terraform configuration conflicts caused by duplicate Lambda function resources between `main.tf` and `functions.tf` that prevent infrastructure deployment initialization.

## Problem Analysis

### Error Details
Terraform initialization failed with duplicate resource errors:

```
Error: Duplicate resource "aws_lambda_function" configuration
  on main.tf line 715:
 715: resource "aws_lambda_function" "coderipple_orchestrator" {
A aws_lambda_function resource named "coderipple_orchestrator" was already
declared at functions.tf:37,1-57.

Error: Duplicate resource "aws_lambda_alias" configuration
  on main.tf line 788:
 788: resource "aws_lambda_alias" "coderipple_orchestrator_alias" {
A aws_lambda_alias resource named "coderipple_orchestrator_alias" was
already declared at functions.tf:131,1-60.

Error: Duplicate output definition
  on outputs.tf line 43:
  43: output "lambda_function_name" {
An output named "lambda_function_name" was already defined at
functions.tf:147,1-30.

Error: Duplicate output definition
  on outputs.tf line 49:
  49: output "lambda_function_arn" {
An output named "lambda_function_arn" was already defined at
functions.tf:142,1-29.
```

### Root Cause Analysis (Updated)
During Units 14.6-14.10 layer-based architecture implementation, we created new layer-optimized Lambda function resources in `functions.tf` but did not remove the original monolithic Lambda function resources from `main.tf`. 

**Key Finding**: Analysis reveals `functions.tf` already contains **more complete configuration** than `main.tf`, including:
- ✅ All critical IAM policy dependencies from `main.tf`
- ✅ Additional layer-specific dependencies
- ✅ Layer-optimized environment variables
- ✅ Enhanced security and monitoring configuration

**Configuration Gap**: Only missing complete tags in `functions.tf`

## Implementation Plan

### Phase 1: Minor Configuration Enhancement (Optional)
1. **Add complete tags** to `functions.tf` Lambda function resource
2. **Maintain layer-based optimizations** (1536MB memory, layer-specific env vars)
3. **Preserve enhanced dependencies** (includes layer dependencies + all main.tf dependencies)

### Phase 2: Remove Duplicate Resources (Primary)
1. **Remove duplicate Lambda function** from `main.tf` (lines 715-787)
2. **Remove duplicate Lambda alias** from `main.tf` (lines 788-794)
3. **Remove duplicate outputs** from `outputs.tf` (lines 43-48, 49-54)
4. **Keep enhanced `functions.tf`** as authoritative source (more complete than main.tf)

### Phase 3: Configuration Validation
1. **Verify Terraform syntax** with `terraform validate`
2. **Test initialization** with `terraform init`
3. **Validate layer references** ensure proper layer ARN usage
4. **Check resource dependencies** confirm all dependencies intact

### Phase 4: Deployment Verification
1. **Run terraform plan** to verify intended changes
2. **Confirm layer-based architecture** in plan output
3. **Validate all outputs available** from functions.tf
4. **Proceed with deployment** once validation passes

## Files to Modify

### 1. `infra/terraform/functions.tf` (OPTIONAL: Minor Enhancement)
**Add complete tags** to match main.tf standards:

```hcl
tags = {
  Name         = var.lambda_function_name
  Environment  = var.environment
  Project      = var.project_name
  LayerBased   = "true"
  Architecture = "single-lambda-with-layers"
  Version      = "2.0.0"  # Layer-based version
}
```

**Note**: `functions.tf` already contains all critical configuration:
- ✅ **Complete dependencies**: All main.tf dependencies PLUS layer dependencies
- ✅ **Security configuration**: KMS, X-Ray, DLQ properly configured
- ✅ **Layer integration**: Dependencies and package layers attached
- ✅ **Optimized settings**: 1536MB memory, layer-specific PYTHONPATH

### 2. `infra/terraform/main.tf` (PRIMARY: Remove Duplicates)
**Remove duplicate resources** (lines 715-794):
```hcl
# Remove entire blocks:
resource "aws_lambda_function" "coderipple_orchestrator" { ... }
resource "aws_lambda_alias" "coderipple_orchestrator_alias" { ... }
```

**Replace with comment**:
```hcl
# Lambda function and alias are now defined in functions.tf (layer-based architecture)
# functions.tf contains enhanced configuration with layer dependencies and optimizations
```

### 3. `infra/terraform/outputs.tf` (PRIMARY: Remove Duplicates)
**Remove duplicate outputs**:
- Lines 43-48: `output "lambda_function_name" { ... }`
- Lines 49-54: `output "lambda_function_arn" { ... }`

**Note**: Keep outputs in `functions.tf` - they reference the layer-based resources and are more comprehensive.

## Validation Steps

### Pre-modification Validation
```bash
cd infra/terraform
terraform validate  # Should fail with duplicate errors
```

### Post-modification Validation
```bash
cd infra/terraform
terraform validate  # Should pass
terraform init      # Should succeed
terraform plan      # Should show layer-based resources
```

### Expected Results
- ✅ No duplicate resource errors
- ✅ Terraform initialization successful  
- ✅ Layer-based Lambda function as authoritative source (enhanced vs original)
- ✅ All outputs available from functions.tf (more comprehensive)
- ✅ Ready for GitHub Actions deployment with layer-based architecture

### Simplified Resolution
**Key Insight**: The problem is simpler than initially assessed. `functions.tf` contains enhanced configuration that surpasses `main.tf`, so we primarily need to remove duplicates rather than consolidate configurations.

## Risk Assessment

### Configuration Analysis Results
**✅ Low Risk**: `functions.tf` already contains superior configuration:
- **Enhanced Dependencies**: All main.tf dependencies PLUS layer-specific dependencies
- **Layer Integration**: Proper layer attachment and environment variables
- **Security**: Complete KMS, X-Ray, DLQ configuration
- **Optimization**: Memory and timeout optimized for layer architecture

### Minimal Changes Required
- **Primary Action**: Remove duplicates from main.tf and outputs.tf (safe operation)
- **Optional Enhancement**: Add complete tags to functions.tf
- **No Critical Gaps**: All essential configuration already in functions.tf

### Validation Confirmed
- **Dependencies**: functions.tf has MORE comprehensive depends_on than main.tf
- **Handler Paths**: Both are correct for their respective architectures
- **Layer Architecture**: functions.tf is the authoritative layer-based implementation

## AI Interactions

### Effective Approach
- **Problem identification**: Clear error message analysis
- **Root cause analysis**: Traced issue to architecture evolution
- **MDD compliance**: Following proper unit documentation process
- **Systematic solution**: Phased approach with validation steps

## Status: Ready for Implementation

### Next Steps
1. **Review this troubleshooting unit** for completeness
2. **Update 000_main.md** to reference this unit
3. **Execute planned modifications** following documented steps
4. **Validate resolution** with Terraform commands
5. **Proceed with deployment** once conflicts resolved

This troubleshooting unit provides systematic resolution of the Terraform duplicate resource conflicts while maintaining the layer-based architecture achievements from Units 14.6-14.10.
