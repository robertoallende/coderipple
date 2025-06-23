# CodeRipple Terraform Infrastructure

This directory contains Terraform configuration for deploying CodeRipple's AWS infrastructure.

## Quick Start

1. **Copy the example variables file:**
   ```bash
   cp terraform.tfvars.example terraform.tfvars
   ```

2. **Edit terraform.tfvars with your values:**
   ```hcl
   github_repo_owner = "your-github-username"
   github_repo_name  = "your-repo-name"
   ```

3. **Initialize and plan:**
   ```bash
   terraform init
   terraform plan
   ```

## Required Variables

- `github_repo_owner` - Your GitHub username or organization
- `github_repo_name` - Your GitHub repository name

## Optional Variables

All other variables have sensible defaults. See `variables.tf` for full documentation.

## State Management

- **Local Development**: Uses local state by default
- **CI/CD**: Use S3 backend with `-backend-config` flags

## Deployment

- **Local**: `terraform apply`
- **CI/CD**: Use the manual GitHub Actions workflow