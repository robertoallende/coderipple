# CodeRipple AWS Infrastructure
# Creates Lambda function, API Gateway, and supporting resources

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
# Lambda Function
# ================================

# Data source to create deployment package from lambda_orchestrator
data "archive_file" "lambda_deployment_package" {
  type        = "zip"
  output_path = "${path.module}/lambda_deployment.zip"

  # Include the lambda_orchestrator source code
  source_dir = "${path.root}/../../aws/lambda_orchestrator"
  
  # Exclude files we don't need in deployment
  excludes = [
    "tests/",
    "venv/",
    "coverage.xml",
    "*.pyc",
    "__pycache__/",
    "*.egg-info/",
    ".pytest_cache/",
    "README.md"
  ]
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
  
  # Environment variables
  environment {
    variables = {
      AWS_DEFAULT_REGION = var.aws_region
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
  
  # Deployment configuration
  publish = true
  
  # Ensure IAM role is created before Lambda function
  depends_on = [
    aws_iam_role_policy_attachment.lambda_basic_execution,
    aws_iam_role_policy_attachment.lambda_bedrock_access,
    aws_iam_role_policy_attachment.lambda_cloudwatch_enhanced,
    aws_iam_role_policy_attachment.lambda_parameter_store
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

# API Gateway method for POST requests
resource "aws_api_gateway_method" "webhook_post" {
  rest_api_id   = aws_api_gateway_rest_api.coderipple_webhook_api.id
  resource_id   = aws_api_gateway_resource.webhook_resource.id
  http_method   = "POST"
  authorization = "NONE"

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
  stage_name  = var.api_gateway_stage

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