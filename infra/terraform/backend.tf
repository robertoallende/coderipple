# Backend configuration for hybrid state management
# 
# Local Development: Uses local backend by default (no configuration needed)
# GitHub Actions CI/CD: Uses S3 backend with -backend-config flag
#
# Usage:
# Local:    terraform init
# CI/CD:    terraform init -backend-config="bucket=coderipple-terraform-state" -backend-config="region=ap-southeast-2"

terraform {
  # No backend configuration by default - uses local state
  # This allows local development without S3 dependencies
  
  # For CI/CD deployment, S3 backend can be configured with:
  # terraform init -backend-config="bucket=coderipple-terraform-state" \
  #                -backend-config="key=coderipple/terraform.tfstate" \
  #                -backend-config="region=ap-southeast-2" \
  #                -backend-config="encrypt=true"
  
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}