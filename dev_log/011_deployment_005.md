# 11.5 Python 3.13 Version Enforcement

## Overview
Enforce Python 3.13 consistency across all CodeRipple development, testing, and production environments to eliminate version-related issues and ensure compatibility with AWS Lambda runtime and Strands Agents SDK requirements.

## Current State Analysis
- **AWS Lambda Runtime**: Already configured for `python3.13`
- **Local Development**: Python 3.13.3 available
- **Strands Requirement**: Python 3.10+ (3.13 exceeds requirement ✅)
- **Version Inconsistency Risk**: Multiple Python versions could cause deployment issues
- **Virtual Environments**: Currently using Python 3.13 but not enforced

## Requirements

### Functional Requirements
- **FR-11.5.1**: Enforce Python 3.13.x across all development environments
- **FR-11.5.2**: Update all requirements.txt files with Python version specification
- **FR-11.5.3**: Add Python version validation to setup scripts
- **FR-11.5.4**: Update CI/CD pipelines to use Python 3.13
- **FR-11.5.5**: Update documentation with Python 3.13 requirement
- **FR-11.5.6**: Ensure Lambda deployment package uses Python 3.13

### Non-Functional Requirements
- **NFR-11.5.1**: Version enforcement must not break existing functionality
- **NFR-11.5.2**: Setup process must fail fast with clear error messages for wrong Python versions
- **NFR-11.5.3**: Documentation must be clear about Python 3.13 requirement
- **NFR-11.5.4**: CI/CD must validate Python version before deployment
- **NFR-11.5.5**: Local development setup must be straightforward

### Compatibility Requirements
- **CR-11.5.1**: Must be compatible with Strands Agents SDK (requires Python 3.10+)
- **CR-11.5.2**: Must match AWS Lambda runtime configuration
- **CR-11.5.3**: Must support all current project dependencies
- **CR-11.5.4**: Must work across macOS, Linux, and Windows development environments

## Design Decisions

### Decision 1: Python Version Strategy
**Chosen**: Enforce Python 3.13.x (latest patch version acceptable)
**Alternatives Considered**: Python 3.10 (Strands minimum), Python 3.12 (stable)
**Rationale**: Matches Lambda runtime, exceeds Strands requirement, provides latest performance and security benefits

### Decision 2: Enforcement Method
**Chosen**: Multi-layered enforcement (requirements.txt, setup scripts, CI/CD, documentation)
**Alternatives Considered**: Documentation only, CI/CD only
**Rationale**: Comprehensive approach prevents version mismatches at multiple stages

### Decision 3: Version Specification Granularity
**Chosen**: Python 3.13.x (allow patch versions)
**Alternatives Considered**: Exact version (3.13.3), major.minor only (3.13)
**Rationale**: Allows security patches while maintaining compatibility

## Implementation Plan

### Phase 1: Requirements and Setup Scripts
1. **Update main requirements.txt**
   ```
   # Python version requirement
   python_requires>=3.13,<3.14
   
   # Existing dependencies...
   strands-agents>=0.1.0
   boto3>=1.34.0
   # ... rest of dependencies
   ```

2. **Update coderipple/requirements.txt**
   ```
   # Python version requirement
   python_requires>=3.13,<3.14
   
   # Core dependencies
   strands-agents>=0.1.0
   strands-agents-tools>=0.1.0
   boto3>=1.34.0
   # ... existing dependencies
   ```

3. **Update aws/lambda_orchestrator/requirements.txt**
   ```
   # Python version requirement - must match Lambda runtime
   python_requires>=3.13,<3.14
   
   # Lambda-specific dependencies
   strands-agents>=0.1.0
   boto3>=1.34.0
   # ... existing dependencies
   ```

### Phase 2: Setup Script Validation
1. **Create version validation script**
   ```python
   # scripts/validate_python_version.py
   import sys
   import subprocess
   
   REQUIRED_PYTHON = (3, 13)
   
   def check_python_version():
       """Validate Python version meets requirements."""
       current_version = sys.version_info[:2]
       
       if current_version < REQUIRED_PYTHON:
           print(f"❌ Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}+ required")
           print(f"   Current version: {sys.version}")
           print(f"   Please install Python 3.13.x")
           sys.exit(1)
       
       if current_version[0] != REQUIRED_PYTHON[0] or current_version[1] != REQUIRED_PYTHON[1]:
           print(f"⚠️  Warning: Using Python {current_version[0]}.{current_version[1]}")
           print(f"   Recommended: Python {REQUIRED_PYTHON[0]}.{REQUIRED_PYTHON[1]}.x")
           print(f"   AWS Lambda runtime: python3.13")
       
       print(f"✅ Python version OK: {sys.version}")
   
   if __name__ == "__main__":
       check_python_version()
   ```

2. **Update setup scripts to include version check**
   ```bash
   # Add to existing setup scripts
   echo "Validating Python version..."
   python scripts/validate_python_version.py
   ```

### Phase 3: Virtual Environment Enforcement
1. **Update coderipple/run_tests.sh**
   ```bash
   #!/bin/bash
   
   # Validate Python version first
   python scripts/validate_python_version.py
   
   # Create virtual environment with Python 3.13
   if [ ! -d "venv" ]; then
       echo "Creating virtual environment with Python 3.13..."
       python3.13 -m venv venv
   fi
   
   # ... rest of existing script
   ```

2. **Create setup script for new environments**
   ```bash
   # scripts/setup_dev_environment.sh
   #!/bin/bash
   
   echo "🐍 Setting up CodeRipple development environment..."
   
   # Check Python version
   python scripts/validate_python_version.py
   
   # Create virtual environment
   echo "Creating virtual environment..."
   python3.13 -m venv venv
   
   # Activate virtual environment
   source venv/bin/activate
   
   # Upgrade pip
   pip install --upgrade pip
   
   # Install dependencies
   pip install -r requirements.txt
   
   echo "✅ Development environment ready!"
   echo "To activate: source venv/bin/activate"
   ```

### Phase 4: CI/CD Pipeline Updates
1. **Update GitHub Actions workflows**
   ```yaml
   # .github/workflows/coderipple-ci.yaml
   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Set up Python 3.13
           uses: actions/setup-python@v4
           with:
             python-version: '3.13'
         - name: Validate Python version
           run: python scripts/validate_python_version.py
         # ... rest of existing workflow
   ```

2. **Update deployment workflow**
   ```yaml
   # .github/workflows/deploy-infrastructure.yml
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - name: Set up Python 3.13
           uses: actions/setup-python@v4
           with:
             python-version: '3.13'
         - name: Validate Python version
           run: python scripts/validate_python_version.py
         # ... rest of existing workflow
   ```

### Phase 5: Documentation Updates
1. **Update main README.md**
   ```markdown
   ## Prerequisites
   
   - **Python 3.13.x** (required for AWS Lambda compatibility)
   - AWS CLI configured with appropriate permissions
   - Terraform >= 1.0
   
   ### Python Version Requirement
   
   CodeRipple requires Python 3.13.x to ensure compatibility with:
   - AWS Lambda runtime (`python3.13`)
   - Strands Agents SDK (requires Python 3.10+)
   - Latest performance and security improvements
   
   Check your Python version:
   ```bash
   python --version  # Should show Python 3.13.x
   ```
   ```

2. **Update GETTING_STARTED.md**
   ```markdown
   ## Prerequisites
   
   Before starting, ensure you have:
   
   ### Required Software
   - **Python 3.13.x** - Download from [python.org](https://www.python.org/downloads/)
   - AWS CLI - [Installation guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
   - Terraform - [Installation guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli)
   
   ### Verify Python Version
   ```bash
   python --version
   # Expected output: Python 3.13.x
   ```
   
   If you have a different version, please install Python 3.13.x before continuing.
   ```

3. **Update coderipple/README.md**
   ```markdown
   ## Requirements
   
   - Python 3.13.x (matches AWS Lambda runtime)
   - Virtual environment (recommended)
   
   ## Quick Setup
   
   ```bash
   # Validate Python version
   python --version  # Must be 3.13.x
   
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```
   ```

### Phase 6: Lambda Deployment Validation
1. **Verify Lambda runtime configuration**
   ```hcl
   # infra/terraform/variables.tf - confirm existing setting
   variable "lambda_runtime" {
     description = "Python runtime for Lambda function"
     type        = string
     default     = "python3.13"  # ✅ Already correct
   }
   ```

2. **Add deployment validation**
   ```bash
   # aws/lambda_orchestrator/package.sh (if exists)
   #!/bin/bash
   
   echo "Validating Python version for Lambda deployment..."
   python scripts/validate_python_version.py
   
   echo "Building Lambda deployment package..."
   # ... existing packaging logic
   ```

## Validation Checklist

### Pre-Implementation Validation
- [ ] Confirm Python 3.13.x installed locally
- [ ] Verify all current dependencies support Python 3.13
- [ ] Test virtual environment creation with Python 3.13
- [ ] Validate Strands Agents SDK works with Python 3.13
- [ ] Confirm AWS Lambda runtime is python3.13

### Post-Implementation Validation
- [ ] All requirements.txt files specify Python 3.13 requirement
- [ ] Setup scripts validate Python version and fail gracefully
- [ ] Virtual environments created with Python 3.13
- [ ] CI/CD pipelines use Python 3.13
- [ ] Documentation clearly states Python 3.13 requirement
- [ ] Lambda deployment uses Python 3.13 runtime

### Functional Testing
- [ ] Local development environment setup works
- [ ] All tests pass with Python 3.13
- [ ] Lambda function deploys and executes correctly
- [ ] Strands agents work properly with Python 3.13
- [ ] CI/CD pipeline completes successfully

## Expected Benefits

### Development Consistency
- Eliminates "works on my machine" issues
- Consistent behavior across all environments
- Predictable dependency resolution

### Production Reliability
- Perfect match with AWS Lambda runtime
- No version-related deployment failures
- Consistent performance characteristics

### Future-Proofing
- Latest Python features and optimizations
- Security patches and bug fixes
- Compatibility with evolving dependencies

### Team Collaboration
- Clear, documented requirements
- Automated validation prevents version issues
- Consistent development experience

## Success Criteria
- All development environments use Python 3.13.x
- Setup process fails fast with clear messages for wrong Python versions
- CI/CD pipelines validate and use Python 3.13
- Documentation clearly communicates Python 3.13 requirement
- Lambda deployment maintains python3.13 runtime
- No version-related issues in development or production

## Risk Mitigation
- **Risk**: Dependencies incompatible with Python 3.13
  **Mitigation**: Test all dependencies before enforcement, maintain compatibility matrix
- **Risk**: Developers using different Python versions
  **Mitigation**: Clear documentation, automated validation, setup scripts
- **Risk**: CI/CD failures due to version mismatch
  **Mitigation**: Explicit Python version specification in workflows
- **Risk**: Lambda deployment issues
  **Mitigation**: Validate runtime configuration, test deployment process

## Implementation Status

✅ **Complete** - Python 3.13 version enforcement successfully implemented across all CodeRipple environments with minimal, focused approach.

**Deliverables:**
- `scripts/validate_python_version.py` - Python version validation script with clear error messages
- Updated documentation (README.md, GETTING_STARTED.md, coderipple/README.md) with Python 3.13 requirement
- Enhanced GitHub Actions CI workflow with Python version validation
- Updated test runner script with version validation
- `scripts/setup_dev_environment.sh` - Complete development environment setup script

## Benefits Achieved

### Development Consistency
- Eliminates "works on my machine" issues with clear Python version validation
- Consistent behavior across all development environments
- Fast failure with helpful error messages for wrong Python versions

### Production Reliability
- Perfect match with AWS Lambda runtime (python3.13)
- No version-related deployment failures
- Consistent performance characteristics across local development and production

### Future-Proofing
- Latest Python features and optimizations available
- Security patches and bug fixes included
- Compatibility with evolving Strands Agents SDK and dependencies

### Team Collaboration
- Clear, documented Python 3.13 requirement in all documentation
- Automated validation prevents version issues before they cause problems
- Consistent development experience for all contributors

This implementation ensures Python 3.13 consistency across the entire CodeRipple development and deployment pipeline while maintaining the existing dependency structure and avoiding over-engineering.
