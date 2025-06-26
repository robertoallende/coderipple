# CodeRipple AWS Infrastructure
# Creates Lambda function, API Gateway, and supporting resources

# ================================
# Data Sources
# ================================

# Get current AWS account ID and region
data "aws_caller_identity" "current" {}

# ================================
# Provider Configuration
# ================================

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Repository  = "${var.github_repo_owner}/${var.github_repo_name}"
    }
  }
}

# Null provider for local-exec provisioners
provider "null" {}

# Local provider for file operations
provider "local" {}

# ================================
# KMS Key for CodeRipple Encryption
# ================================

# KMS key for encrypting CodeRipple resources
resource "aws_kms_key" "coderipple_key" {
  description             = "CodeRipple encryption key for S3, Lambda, and other resources"
  deletion_window_in_days = 7
  enable_key_rotation     = true
  
  # KMS key policy for proper access control
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "Enable IAM User Permissions"
        Effect = "Allow"
        Principal = {
          AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
        }
        Action   = "kms:*"
        Resource = "*"
      },
      {
        Sid    = "Allow CloudWatch Logs"
        Effect = "Allow"
        Principal = {
          Service = "logs.${var.aws_region}.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
        Condition = {
          ArnEquals = {
            "kms:EncryptionContext:aws:logs:arn" = "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:*"
          }
        }
      },
      {
        Sid    = "Allow S3 Service"
        Effect = "Allow"
        Principal = {
          Service = "s3.amazonaws.com"
        }
        Action = [
          "kms:Encrypt",
          "kms:Decrypt",
          "kms:ReEncrypt*",
          "kms:GenerateDataKey*",
          "kms:DescribeKey"
        ]
        Resource = "*"
      }
    ]
  })
  
  tags = {
    Name        = "coderipple-encryption-key"
    Environment = var.environment
    Purpose     = "encryption"
    Project     = var.project_name
  }
}

# KMS key alias for easier reference
resource "aws_kms_alias" "coderipple_key_alias" {
  name          = "alias/coderipple-encryption-key"
  target_key_id = aws_kms_key.coderipple_key.key_id
}

# ================================
# S3 Bucket for Terraform State
# ================================

# S3 bucket for Terraform state storage (bootstrap resource)
resource "aws_s3_bucket" "terraform_state" {
  bucket = "coderipple-terraform-state"
  
  # Prevent accidental deletion
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Name        = "CodeRipple Terraform State"
    Purpose     = "terraform-state-storage"
    Environment = var.environment
  }
}

# Enable versioning for state file safety
resource "aws_s3_bucket_versioning" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption with KMS
resource "aws_s3_bucket_server_side_encryption_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    apply_server_side_encryption_by_default {
      kms_master_key_id = aws_kms_key.coderipple_key.arn
      sse_algorithm     = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 bucket lifecycle configuration for state management
resource "aws_s3_bucket_lifecycle_configuration" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  rule {
    id     = "terraform_state_lifecycle"
    status = "Enabled"
    
    # Apply to all objects in the bucket
    filter {
      prefix = ""
    }

    # Keep recent versions but clean up old ones
    noncurrent_version_expiration {
      noncurrent_days = 90
    }

    # Abort incomplete multipart uploads
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  depends_on = [aws_s3_bucket_versioning.terraform_state]
}

# S3 bucket for access logs (separate bucket to avoid recursive logging)
resource "aws_s3_bucket" "terraform_state_access_logs" {
  bucket = "${var.project_name}-terraform-state-access-logs"
  
  tags = {
    Name        = "CodeRipple Terraform State Access Logs"
    Purpose     = "access-logging"
    Environment = var.environment
  }
}

# Block public access for access logs bucket
resource "aws_s3_bucket_public_access_block" "terraform_state_access_logs" {
  bucket = aws_s3_bucket.terraform_state_access_logs.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable access logging for the main state bucket
resource "aws_s3_bucket_logging" "terraform_state" {
  bucket = aws_s3_bucket.terraform_state.id

  target_bucket = aws_s3_bucket.terraform_state_access_logs.id
  target_prefix = "access-logs/"
}

# ================================
# IAM Role for Lambda Execution
# ================================

# Lambda execution role with basic permissions
resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-lambda-execution-role"
  }
}

# Basic Lambda execution permissions (VPC, logging)
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# ================================
# IAM Policy for Bedrock Access
# ================================

# Custom IAM policy for Bedrock model invocation
resource "aws_iam_policy" "bedrock_access_policy" {
  name        = "${var.project_name}-bedrock-access"
  description = "Allow Lambda to invoke Bedrock models for AI content generation"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          # Allow access to Claude models in the specified region
          "arn:aws:bedrock:${var.aws_region}::foundation-model/anthropic.claude-*",
          # Allow access to other potential models for content generation
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.titan-*"
        ]
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-bedrock-access"
  }
}

# Attach Bedrock policy to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_bedrock_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.bedrock_access_policy.arn
}

# ================================
# IAM Policy for CloudWatch Enhanced Logging
# ================================

# Custom policy for enhanced CloudWatch operations
resource "aws_iam_policy" "cloudwatch_enhanced_policy" {
  name        = "${var.project_name}-cloudwatch-enhanced"
  description = "Enhanced CloudWatch permissions for logging and metrics"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogGroups",
          "logs:DescribeLogStreams"
        ]
        Resource = [
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.lambda_function_name}",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/lambda/${var.lambda_function_name}:*",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/apigateway/${var.api_gateway_name}",
          "arn:aws:logs:${var.aws_region}:*:log-group:/aws/apigateway/${var.api_gateway_name}:*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "CodeRipple"
          }
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-cloudwatch-enhanced"
  }
}

# Attach enhanced CloudWatch policy to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_cloudwatch_enhanced" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.cloudwatch_enhanced_policy.arn
}

# ================================
# IAM Policy for Parameter Store Access (Future Step 9.9)
# ================================

# Custom policy for Parameter Store access
resource "aws_iam_policy" "parameter_store_policy" {
  name        = "${var.project_name}-parameter-store-access"
  description = "Allow Lambda to read CodeRipple configuration from Parameter Store"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:*:parameter/coderipple/*"
        ]
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-parameter-store-access"
  }
}

# Attach Parameter Store policy to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_parameter_store" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.parameter_store_policy.arn
}

# ================================
# Security-Related IAM Policies
# ================================

# KMS access policy for Lambda encryption
resource "aws_iam_policy" "lambda_kms_policy" {
  name        = "${var.project_name}-lambda-kms-policy"
  description = "Policy for Lambda to access KMS key for encryption"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "kms:Decrypt",
          "kms:DescribeKey",
          "kms:Encrypt",
          "kms:GenerateDataKey",
          "kms:ReEncrypt*"
        ]
        Resource = [
          aws_kms_key.coderipple_key.arn
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-lambda-kms-policy"
    Environment = var.environment
  }
}

# X-Ray tracing policy for Lambda
resource "aws_iam_policy" "lambda_xray_policy" {
  name        = "${var.project_name}-lambda-xray-policy"
  description = "Policy for Lambda X-Ray tracing"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "xray:PutTraceSegments",
          "xray:PutTelemetryRecords"
        ]
        Resource = "*"
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-lambda-xray-policy"
    Environment = var.environment
  }
}

# SQS Dead Letter Queue access policy
resource "aws_iam_policy" "lambda_sqs_policy" {
  name        = "${var.project_name}-lambda-sqs-policy"
  description = "Policy for Lambda to access SQS Dead Letter Queue"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage",
          "sqs:GetQueueAttributes"
        ]
        Resource = [
          aws_sqs_queue.lambda_dlq.arn
        ]
      }
    ]
  })

  tags = {
    Name        = "${var.project_name}-lambda-sqs-policy"
    Environment = var.environment
  }
}

# Attach security policies to Lambda execution role
resource "aws_iam_role_policy_attachment" "lambda_kms_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_kms_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_xray_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_xray_policy.arn
}

resource "aws_iam_role_policy_attachment" "lambda_sqs_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_sqs_policy.arn
}

# ================================
# SQS Dead Letter Queue for Lambda
# ================================

# Dead Letter Queue for failed Lambda executions
resource "aws_sqs_queue" "lambda_dlq" {
  name                      = "${var.project_name}-lambda-dlq"
  message_retention_seconds = 1209600  # 14 days
  
  # Enable server-side encryption
  kms_master_key_id = aws_kms_key.coderipple_key.arn
  
  tags = {
    Name        = "${var.project_name}-lambda-dlq"
    Environment = var.environment
    Purpose     = "lambda-error-handling"
  }
}

# ================================
# Lambda Function
# ================================

# Data source to create deployment package from lambda_orchestrator
# Create build directory structure before package assembly
resource "local_file" "lambda_build_placeholder" {
  content  = "# Lambda build directory placeholder - ensures directory exists for Terraform archive operation"
  filename = "${path.module}/lambda_build/.terraform_placeholder"
  
  # Ensure directory exists before creating placeholder file
  provisioner "local-exec" {
    command = "mkdir -p ${path.module}/lambda_build"
  }
}

# Prepare Lambda package with CodeRipple source
resource "null_resource" "prepare_lambda_package" {
  depends_on = [local_file.lambda_build_placeholder]
  
  provisioner "local-exec" {
    command = <<EOF
      # Directory already exists from placeholder, safe to proceed
      
      # Create proper src/ module for Lambda handler
      mkdir -p ${path.module}/lambda_build/src
      echo "# Lambda handler module" > ${path.module}/lambda_build/src/__init__.py
      cp ${path.root}/../../aws/lambda_orchestrator/src/lambda_handler.py ${path.module}/lambda_build/src/
      
      # Copy package configuration files
      cp ${path.root}/../../aws/lambda_orchestrator/requirements.txt ${path.module}/lambda_build/
      cp ${path.root}/../../aws/lambda_orchestrator/setup.py ${path.module}/lambda_build/ 2>/dev/null || true
      
      # Install all dependencies including CodeRipple package
      cd ${path.module}/lambda_build
      python3 -m pip install -r requirements.txt -t .
      python3 -m pip install -e ${path.root}/../../coderipple -t .
      
      # Clean up unnecessary files
      find ${path.module}/lambda_build -name "*.pyc" -delete
      find ${path.module}/lambda_build -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
      find ${path.module}/lambda_build -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
      rm -rf ${path.module}/lambda_build/tests/ 2>/dev/null || true
      rm -rf ${path.module}/lambda_build/venv/ 2>/dev/null || true
      rm -rf ${path.module}/lambda_build/.pytest_cache/ 2>/dev/null || true
      rm -f ${path.module}/lambda_build/coverage.xml 2>/dev/null || true
      rm -f ${path.module}/lambda_build/README.md 2>/dev/null || true
    EOF
  }
  
  # Trigger rebuild when source files change
  triggers = {
    lambda_handler_hash = filemd5("${path.root}/../../aws/lambda_orchestrator/src/lambda_handler.py")
    coderipple_agents_hash = sha1(join("", [
      for f in fileset("${path.root}/../../coderipple/src", "*.py") : 
      filemd5("${path.root}/../../coderipple/src/${f}")
    ]))
  }
}

data "archive_file" "lambda_deployment_package" {
  depends_on = [
    local_file.lambda_build_placeholder,
    null_resource.prepare_lambda_package
  ]
  
  type        = "zip"
  source_dir  = "${path.module}/lambda_build"
  output_path = "${path.module}/lambda_deployment.zip"
}

# Lambda function for CodeRipple orchestration
resource "aws_lambda_function" "coderipple_orchestrator" {
  function_name = var.lambda_function_name
  role         = aws_iam_role.lambda_execution_role.arn
  
  # Deployment package
  filename         = data.archive_file.lambda_deployment_package.output_path
  source_code_hash = data.archive_file.lambda_deployment_package.output_base64sha256
  
  # Runtime configuration
  runtime = var.lambda_runtime
  handler = "src.lambda_handler.lambda_handler"
  
  # Performance configuration for multi-agent processing
  memory_size = var.lambda_memory_size
  timeout     = var.lambda_timeout
  
  # Environment variables with KMS encryption
  environment {
    variables = {
      # AWS_DEFAULT_REGION is automatically set by Lambda runtime - removed reserved variable
      PYTHONPATH        = "/var/runtime:/var/task/src:/opt"
      
      # GitHub repository information
      CODERIPPLE_GITHUB_REPO_OWNER = var.github_repo_owner
      CODERIPPLE_GITHUB_REPO_NAME  = var.github_repo_name
      
      # Environment and project info
      CODERIPPLE_ENVIRONMENT = var.environment
      CODERIPPLE_PROJECT     = var.project_name
      
      # Note: GitHub token and other sensitive config will come from Parameter Store
      # See Step 9.9 for Parameter Store configuration
    }
  }
  
  # Security configurations
  kms_key_arn = aws_kms_key.coderipple_key.arn
  
  # X-Ray tracing for observability
  tracing_config {
    mode = "Active"
  }
  
  # Dead Letter Queue for error handling
  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }
  
  # Concurrency limits for cost control
  reserved_concurrent_executions = 10
  
  # Deployment configuration
  publish = true
  
  # Ensure IAM role and CloudWatch log group are created before Lambda function
  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_bedrock_access,
    aws_iam_role_policy_attachment.lambda_cloudwatch_enhanced,
    aws_iam_role_policy_attachment.lambda_parameter_store,
    aws_iam_role_policy_attachment.lambda_kms_access,
    aws_iam_role_policy_attachment.lambda_xray_access,
    aws_iam_role_policy_attachment.lambda_sqs_access,
    aws_cloudwatch_log_group.lambda_logs,
    aws_sqs_queue.lambda_dlq
  ]

  tags = {
    Name = var.lambda_function_name
  }
}

# Lambda function alias for versioning (optional)
resource "aws_lambda_alias" "coderipple_orchestrator_alias" {
  name             = var.environment
  description      = "Alias for ${var.environment} environment"
  function_name    = aws_lambda_function.coderipple_orchestrator.function_name
  function_version = aws_lambda_function.coderipple_orchestrator.version
}

# ================================
# API Gateway
# ================================

# API Gateway REST API for GitHub webhooks
resource "aws_api_gateway_rest_api" "coderipple_webhook_api" {
  name        = var.api_gateway_name
  description = "API Gateway for CodeRipple GitHub webhook integration"
  
  endpoint_configuration {
    types = ["REGIONAL"]
  }

  # Security: Lifecycle management for zero-downtime updates
  lifecycle {
    create_before_destroy = true
  }

  tags = {
    Name = var.api_gateway_name
  }
}

# API Gateway resource for webhook endpoint (root path)
resource "aws_api_gateway_resource" "webhook_resource" {
  rest_api_id = aws_api_gateway_rest_api.coderipple_webhook_api.id
  parent_id   = aws_api_gateway_rest_api.coderipple_webhook_api.root_resource_id
  path_part   = "webhook"
}

# API Gateway request validator for webhook endpoint
resource "aws_api_gateway_request_validator" "webhook_validator" {
  name                        = "${var.project_name}-webhook-validator"
  rest_api_id                 = aws_api_gateway_rest_api.coderipple_webhook_api.id
  validate_request_body       = true
  validate_request_parameters = false  # GitHub webhooks have flexible headers
}

# API Gateway method for POST requests
resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.coderipple_webhook_api.id
  resource_id   = aws_api_gateway_resource.webhook_resource.id
  http_method   = "POST"
  authorization = "NONE"
  
  # Add request validation for security compliance
  request_validator_id = aws_api_gateway_request_validator.webhook_validator.id

  # Enable CORS for browser-based testing (optional)
  request_parameters = {
    "method.request.header.X-GitHub-Delivery" = false
    "method.request.header.X-GitHub-Event"    = false
    "method.request.header.X-Hub-Signature"   = false
    "method.request.header.X-Hub-Signature-256" = false
  }
}

# API Gateway integration with Lambda function
resource "aws_api_gateway_integration" "lambda_integration" {
  rest_api_id             = aws_api_gateway_rest_api.coderipple_webhook_api.id
  resource_id             = aws_api_gateway_resource.webhook_resource.id
  http_method             = aws_api_gateway_method.webhook_post.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.coderipple_orchestrator.invoke_arn
}

# API Gateway method response
resource "aws_api_gateway_method_response" "webhook_response_200" {
  rest_api_id = aws_api_gateway_rest_api.coderipple_webhook_api.id
  resource_id = aws_api_gateway_resource.webhook_resource.id
  http_method = aws_api_gateway_method.webhook_post.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
}

# API Gateway integration response
resource "aws_api_gateway_integration_response" "lambda_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.coderipple_webhook_api.id
  resource_id = aws_api_gateway_resource.webhook_resource.id
  http_method = aws_api_gateway_method.webhook_post.http_method
  status_code = aws_api_gateway_method_response.webhook_response_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
  }

  depends_on = [aws_api_gateway_integration.lambda_integration]
}

# Lambda permission for API Gateway to invoke the function
resource "aws_lambda_permission" "api_gateway_invoke" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.coderipple_orchestrator.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.coderipple_webhook_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "webhook_deployment" {
  rest_api_id = aws_api_gateway_rest_api.coderipple_webhook_api.id
  # stage_name removed - handled by separate aws_api_gateway_stage resource

  # Ensure all methods and integrations are created before deployment
  depends_on = [
    aws_api_gateway_method.webhook_post,
    aws_api_gateway_integration.lambda_integration,
    aws_api_gateway_method_response.webhook_response_200,
    aws_api_gateway_integration_response.lambda_integration_response
  ]

  # Force redeployment when configuration changes
  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.webhook_resource.id,
      aws_api_gateway_method.webhook_post.id,
      aws_api_gateway_integration.lambda_integration.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# ================================
# CloudWatch Logging
# ================================

# CloudWatch log group for Lambda function
resource "aws_cloudwatch_log_group" "lambda_logs" {
  name              = "/aws/lambda/${var.lambda_function_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.coderipple_key.arn

  tags = {
    Name        = "${var.lambda_function_name}-logs"
    Environment = var.environment
    Service     = "lambda"
  }
}

# ================================
# CloudWatch Alarms for Security Monitoring
# ================================

# CloudWatch alarm for Lambda throttling (concurrency limit monitoring)
resource "aws_cloudwatch_metric_alarm" "lambda_throttles" {
  alarm_name          = "${var.project_name}-lambda-throttles"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Throttles"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "This metric monitors lambda throttles due to concurrency limits"
  alarm_actions       = []

  dimensions = {
    FunctionName = aws_lambda_function.coderipple_orchestrator.function_name
  }

  tags = {
    Name        = "${var.project_name}-lambda-throttles"
    Environment = var.environment
  }
}

# CloudWatch alarm for Dead Letter Queue messages
resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "${var.project_name}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfVisibleMessages"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "0"
  alarm_description   = "This metric monitors messages in the Dead Letter Queue"
  alarm_actions       = []

  dimensions = {
    QueueName = aws_sqs_queue.lambda_dlq.name
  }

  tags = {
    Name        = "${var.project_name}-dlq-messages"
    Environment = var.environment
  }
}

# CloudWatch log group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway_logs" {
  name              = "/aws/apigateway/${var.api_gateway_name}"
  retention_in_days = var.log_retention_days
  kms_key_id        = aws_kms_key.coderipple_key.arn

  tags = {
    Name        = "${var.api_gateway_name}-logs"
    Environment = var.environment
    Service     = "apigateway"
  }
}

# API Gateway account configuration for CloudWatch logging
resource "aws_api_gateway_account" "api_gateway_account" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch_role.arn
}

# IAM role for API Gateway CloudWatch logging
resource "aws_iam_role" "api_gateway_cloudwatch_role" {
  name = "${var.project_name}-api-gateway-cloudwatch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Name = "${var.project_name}-api-gateway-cloudwatch-role"
  }
}

# Attach CloudWatch logging policy to API Gateway role
resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch_logs" {
  role       = aws_iam_role.api_gateway_cloudwatch_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# API Gateway stage configuration with logging
resource "aws_api_gateway_stage" "webhook_stage" {
  deployment_id = aws_api_gateway_deployment.webhook_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.coderipple_webhook_api.id
  stage_name    = var.api_gateway_stage

  # Enable X-Ray tracing for security compliance
  xray_tracing_enabled = true
  
  # Enable caching for performance (will be disabled for webhook endpoint specifically)
  cache_cluster_enabled = true
  cache_cluster_size    = "0.5"  # Smallest size for cost efficiency

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway_logs.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
      responseTime   = "$context.responseTime"
      error_message  = "$context.error.message"
      error_type     = "$context.error.messageString"
    })
  }

  # Method-level logging settings
  depends_on = [
    aws_api_gateway_account.api_gateway_account,
    aws_cloudwatch_log_group.api_gateway_logs
  ]

  tags = {
    Name        = "${var.api_gateway_name}-${var.api_gateway_stage}"
    Environment = var.environment
  }
}

# API Gateway method settings for detailed logging
resource "aws_api_gateway_method_settings" "webhook_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.coderipple_webhook_api.id
  stage_name  = aws_api_gateway_stage.webhook_stage.stage_name
  method_path = "*/*"

  settings {
    # Enable detailed CloudWatch metrics
    metrics_enabled    = true
    data_trace_enabled = false  # Security requirement: disable data tracing
    logging_level      = "INFO"
    
    # Caching settings - disabled for webhook endpoint (GitHub needs fresh responses)
    caching_enabled = false
    
    # Throttling settings
    throttling_rate_limit  = 100
    throttling_burst_limit = 50
  }
}