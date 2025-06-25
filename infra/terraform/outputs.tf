# Terraform outputs for CodeRipple infrastructure
# These outputs provide essential information for GitHub webhook configuration
# and monitoring setup in subsequent steps

# ================================
# API Gateway Outputs
# ================================

output "webhook_url" {
  description = "Complete webhook URL for GitHub repository configuration"
  value       = "${aws_api_gateway_stage.webhook_stage.invoke_url}/webhook"
  sensitive   = false
}

output "api_gateway_id" {
  description = "API Gateway REST API ID"
  value       = aws_api_gateway_rest_api.coderipple_webhook_api.id
  sensitive   = false
}

output "api_gateway_arn" {
  description = "API Gateway ARN for IAM and monitoring configuration"
  value       = aws_api_gateway_rest_api.coderipple_webhook_api.arn
  sensitive   = false
}

output "api_gateway_stage_name" {
  description = "API Gateway deployment stage name"
  value       = aws_api_gateway_stage.webhook_stage.stage_name
  sensitive   = false
}

output "api_gateway_execution_arn" {
  description = "API Gateway execution ARN for Lambda permissions"
  value       = aws_api_gateway_rest_api.coderipple_webhook_api.execution_arn
  sensitive   = false
}

# ================================
# Lambda Function Outputs
# ================================

output "lambda_function_name" {
  description = "Lambda function name for monitoring and invocation"
  value       = aws_lambda_function.coderipple_orchestrator.function_name
  sensitive   = false
}

output "lambda_function_arn" {
  description = "Lambda function ARN for IAM policies and triggers"
  value       = aws_lambda_function.coderipple_orchestrator.arn
  sensitive   = false
}

output "lambda_function_qualified_arn" {
  description = "Lambda function qualified ARN with version"
  value       = aws_lambda_function.coderipple_orchestrator.qualified_arn
  sensitive   = false
}

output "lambda_invoke_arn" {
  description = "Lambda invoke ARN for API Gateway integration"
  value       = aws_lambda_function.coderipple_orchestrator.invoke_arn
  sensitive   = false
}

output "lambda_version" {
  description = "Lambda function version for deployment tracking"
  value       = aws_lambda_function.coderipple_orchestrator.version
  sensitive   = false
}

output "lambda_alias_arn" {
  description = "Lambda function alias ARN for environment management"
  value       = aws_lambda_alias.coderipple_orchestrator_alias.arn
  sensitive   = false
}

# ================================
# CloudWatch Outputs
# ================================

output "lambda_log_group_name" {
  description = "CloudWatch log group name for Lambda function"
  value       = aws_cloudwatch_log_group.lambda_logs.name
  sensitive   = false
}

output "lambda_log_group_arn" {
  description = "CloudWatch log group ARN for Lambda function"
  value       = aws_cloudwatch_log_group.lambda_logs.arn
  sensitive   = false
}

output "api_gateway_log_group_name" {
  description = "CloudWatch log group name for API Gateway"
  value       = aws_cloudwatch_log_group.api_gateway_logs.name
  sensitive   = false
}

output "api_gateway_log_group_arn" {
  description = "CloudWatch log group ARN for API Gateway"
  value       = aws_cloudwatch_log_group.api_gateway_logs.arn
  sensitive   = false
}

# ================================
# IAM Outputs
# ================================

output "lambda_execution_role_arn" {
  description = "Lambda execution role ARN for permissions management"
  value       = aws_iam_role.lambda_execution_role.arn
  sensitive   = false
}

output "lambda_execution_role_name" {
  description = "Lambda execution role name for policy attachments"
  value       = aws_iam_role.lambda_execution_role.name
  sensitive   = false
}

# ================================
# Configuration Outputs
# ================================

output "aws_region" {
  description = "AWS region where resources are deployed"
  value       = var.aws_region
  sensitive   = false
}

output "environment" {
  description = "Environment name for resource identification"
  value       = var.environment
  sensitive   = false
}

output "project_name" {
  description = "Project name used for resource naming"
  value       = var.project_name
  sensitive   = false
}

# ================================
# GitHub Configuration Outputs
# ================================

output "github_repo_owner" {
  description = "GitHub repository owner for webhook configuration"
  value       = var.github_repo_owner
  sensitive   = false
}

output "github_repo_name" {
  description = "GitHub repository name for webhook configuration"
  value       = var.github_repo_name
  sensitive   = false
}

output "github_repo_full_name" {
  description = "Full GitHub repository name (owner/repo)"
  value       = "${var.github_repo_owner}/${var.github_repo_name}"
  sensitive   = false
}

# ================================
# Step 9.3 Integration Outputs
# ================================

output "webhook_configuration_summary" {
  description = "Complete webhook configuration details for GitHub setup"
  value = {
    webhook_url    = "${aws_api_gateway_stage.webhook_stage.invoke_url}/webhook"
    content_type   = "application/json"
    events         = ["push", "pull_request"]
    active         = true
    ssl_verification = true
  }
  sensitive = false
}

# ================================
# Monitoring Integration Outputs
# ================================

output "monitoring_resources" {
  description = "CloudWatch resources for monitoring setup (Step 9.8)"
  value = {
    lambda_log_group    = aws_cloudwatch_log_group.lambda_logs.name
    api_gateway_log_group = aws_cloudwatch_log_group.api_gateway_logs.name
    lambda_function_name = aws_lambda_function.coderipple_orchestrator.function_name
    api_gateway_name    = aws_api_gateway_rest_api.coderipple_webhook_api.name
    namespace          = "CodeRipple"
  }
  sensitive = false
}

# ================================
# Security Configuration Outputs
# ================================

output "kms_key_id" {
  description = "KMS key ID for encryption operations"
  value       = aws_kms_key.coderipple_key.key_id
  sensitive   = false
}

output "kms_key_arn" {
  description = "KMS key ARN for IAM policies and encryption"
  value       = aws_kms_key.coderipple_key.arn
  sensitive   = false
}

output "dead_letter_queue_url" {
  description = "SQS Dead Letter Queue URL for error monitoring"
  value       = aws_sqs_queue.lambda_dlq.url
  sensitive   = false
}

output "dead_letter_queue_arn" {
  description = "SQS Dead Letter Queue ARN for monitoring setup"
  value       = aws_sqs_queue.lambda_dlq.arn
  sensitive   = false
}

output "security_features_enabled" {
  description = "Summary of security features implemented"
  value = {
    kms_encryption           = true
    xray_tracing            = true
    dead_letter_queue       = true
    concurrency_limits      = true
    api_gateway_lifecycle   = true
    cloudwatch_monitoring   = true
  }
  sensitive = false
}