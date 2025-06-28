# Variables for CodeRipple Terraform Infrastructure
# Configure all aspects of the AWS deployment

# ================================
# AWS Configuration
# ================================

variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "ap-southeast-2"  # Sydney region
}

# ================================
# GitHub Repository Configuration
# ================================

variable "github_repo_owner" {
  description = "GitHub repository owner (username or organization)"
  type        = string
  # No default - must be provided via terraform.tfvars or command line
}

variable "github_repo_name" {
  description = "GitHub repository name"
  type        = string
  # No default - must be provided via terraform.tfvars or command line
}

variable "github_token" {
  description = "GitHub personal access token for repository access (optional - can use environment variable)"
  type        = string
  default     = null
  sensitive   = true
}

# ================================
# Lambda Function Configuration
# ================================

variable "lambda_function_name" {
  description = "Name of the Lambda function"
  type        = string
  default     = "coderipple-orchestrator"
}

variable "lambda_memory_size" {
  description = "Memory allocation for Lambda function (MB)"
  type        = number
  default     = 2048  # Required for multi-agent processing
  
  validation {
    condition     = var.lambda_memory_size >= 512 && var.lambda_memory_size <= 10240
    error_message = "Lambda memory size must be between 512 and 10240 MB."
  }
}

variable "lambda_timeout" {
  description = "Timeout for Lambda function (seconds)"
  type        = number
  default     = 900  # 15 minutes for multi-agent processing
  
  validation {
    condition     = var.lambda_timeout >= 1 && var.lambda_timeout <= 900
    error_message = "Lambda timeout must be between 1 and 900 seconds."
  }
}

variable "lambda_runtime" {
  description = "Python runtime for Lambda function"
  type        = string
  default     = "python3.13"
}

# ================================
# API Gateway Configuration
# ================================

variable "api_gateway_name" {
  description = "Name of the API Gateway"
  type        = string
  default     = "coderipple-webhook-api"
}

variable "api_gateway_stage" {
  description = "API Gateway deployment stage"
  type        = string
  default     = "prod"
}

# ================================
# CloudWatch Configuration
# ================================

variable "log_retention_days" {
  description = "CloudWatch log retention period in days"
  type        = number
  default     = 14
  
  validation {
    condition = contains([
      1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1096, 1827, 2192, 2557, 2922, 3288, 3653
    ], tonumber(var.log_retention_days))
    error_message = "Log retention days must be a valid CloudWatch retention period."
  }
}

# ================================
# Environment Configuration
# ================================

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "prod"
  
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be one of: dev, staging, prod."
  }
}

variable "project_name" {
  description = "Project name for resource naming and tagging"
  type        = string
  default     = "coderipple"
}

# ================================
# CodeRipple Configuration
# ================================

# Note: CodeRipple runtime configuration will be stored in AWS Parameter Store
# and managed in Step 9.9. This allows runtime configuration changes without
# Terraform redeployment. See CLAUDE.md Step 9.9 for Parameter Store hierarchy.