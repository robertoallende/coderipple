# CodeRipple Lambda Functions Configuration (Layer-based)
# Replaces complex package bundling with clean layer-based architecture

# ================================
# Lambda Function Package (Simple)
# ================================

# Simple archive for function code only (no dependencies)
data "archive_file" "orchestrator_function_package" {
  type        = "zip"
  source_dir  = "${path.module}/../../functions/orchestrator/build"
  output_path = "${path.module}/orchestrator-function.zip"
  
  # Only rebuild if function code changes
  depends_on = [
    null_resource.build_orchestrator_function
  ]
}

# Build orchestrator function
resource "null_resource" "build_orchestrator_function" {
  # Rebuild when function code changes
  triggers = {
    function_code = filebase64sha256("${path.module}/../../functions/orchestrator/lambda_function.py")
    build_script  = filebase64sha256("${path.module}/../../functions/orchestrator/1-build.sh")
  }
  
  provisioner "local-exec" {
    command = "cd ${path.module}/../../functions/orchestrator && ./1-build.sh"
  }
}

# ================================
# CodeRipple Single Lambda Function (Layer-based)
# ================================

resource "aws_lambda_function" "coderipple_orchestrator" {
  function_name = var.lambda_function_name
  filename      = data.archive_file.orchestrator_function_package.output_path
  source_code_hash = data.archive_file.orchestrator_function_package.output_base64sha256
  
  # Layers attached in dependency order
  layers = [
    aws_lambda_layer_version.coderipple_dependencies.arn,
    aws_lambda_layer_version.coderipple_package.arn
  ]
  
  # Function configuration (optimized for layer-based architecture)
  handler = "lambda_function.lambda_handler"
  runtime = var.lambda_runtime  # Python 3.12 for OpenTelemetry compatibility (Unit 15.10)
  
  # Optimized resource allocation (layers reduce memory needs)
  memory_size = 1536  # Reduced from 2048 (dependencies in layers)
  timeout     = var.lambda_timeout
  
  # Environment variables (same as current)
  environment {
    variables = {
      # Core configuration
      PYTHONPATH = "/var/runtime:/var/task:/opt/python"
      
      # GitHub repository information
      CODERIPPLE_GITHUB_REPO_OWNER = var.github_repo_owner
      CODERIPPLE_GITHUB_REPO_NAME  = var.github_repo_name
      
      # Environment and project info
      CODERIPPLE_ENVIRONMENT = var.environment
      CODERIPPLE_PROJECT     = var.project_name
      
      # Layer-based architecture indicators
      CODERIPPLE_LAYER_BASED           = "true"
      CODERIPPLE_ARCHITECTURE          = "single-lambda-with-layers"
      CODERIPPLE_DEPENDENCIES_LAYER    = aws_lambda_layer_version.coderipple_dependencies.arn
      CODERIPPLE_PACKAGE_LAYER         = aws_lambda_layer_version.coderipple_package.arn
      
      # OpenTelemetry configuration - enabled for Python 3.12 compatibility with Strands SDK
      OTEL_SDK_DISABLED     = "false"
      OTEL_TRACES_EXPORTER  = "otlp"
      OTEL_METRICS_EXPORTER = "otlp"
      OTEL_LOGS_EXPORTER    = "otlp"
    }
  }
  
  # IAM role (same as current)
  role = aws_iam_role.lambda_execution_role.arn
  
  # Security configurations (same as current)
  kms_key_arn = aws_kms_key.coderipple_key.arn
  
  # X-Ray tracing for observability
  tracing_config {
    mode = "Active"
  }
  
  # Dead letter queue (same as current)
  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_dlq.arn
  }
  
  # Concurrency limits for cost control
  reserved_concurrent_executions = 10
  
  # Deployment configuration
  publish = true
  
  # Tags
  tags = {
    Name         = var.lambda_function_name
    Environment  = var.environment
    Project      = var.project_name
    LayerBased   = "true"
    Architecture = "single-lambda-with-layers"
    Version      = "2.0.0"  # Layer-based version
  }
  
  # Lifecycle management
  lifecycle {
    create_before_destroy = true
  }
  
  depends_on = [
    aws_lambda_layer_version.coderipple_dependencies,
    aws_lambda_layer_version.coderipple_package,
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
}

# Lambda function alias for versioning
resource "aws_lambda_alias" "coderipple_orchestrator_alias" {
  name             = var.environment
  description      = "Alias for ${var.environment} environment (layer-based)"
  function_name    = aws_lambda_function.coderipple_orchestrator.function_name
  function_version = aws_lambda_function.coderipple_orchestrator.version
}

# ================================
# Outputs
# ================================

output "lambda_function_arn" {
  description = "ARN of the CodeRipple Lambda function"
  value       = aws_lambda_function.coderipple_orchestrator.arn
}

output "lambda_function_name" {
  description = "Name of the CodeRipple Lambda function"
  value       = aws_lambda_function.coderipple_orchestrator.function_name
}

output "lambda_function_version" {
  description = "Version of the CodeRipple Lambda function"
  value       = aws_lambda_function.coderipple_orchestrator.version
}

output "lambda_function_package_size" {
  description = "Size of the Lambda function package"
  value       = "${data.archive_file.orchestrator_function_package.output_size} bytes"
}
