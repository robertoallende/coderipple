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