# CodeRipple Lambda Layers Configuration
# Terraform configuration for CodeRipple dependencies and package layers

# CodeRipple Dependencies Layer
resource "aws_lambda_layer_version" "coderipple_dependencies" {
  layer_name               = "coderipple-dependencies"
  filename                 = "${path.module}/../../layers/dependencies/coderipple-dependencies-layer.zip"
  source_code_hash         = filebase64sha256("${path.module}/../../layers/dependencies/coderipple-dependencies-layer.zip")
  
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  
  description = "CodeRipple external dependencies (boto3, strands-agents, requests, etc.)"
  
  lifecycle {
    create_before_destroy = true
  }
}

# CodeRipple Package Layer
resource "aws_lambda_layer_version" "coderipple_package" {
  layer_name               = "coderipple-package"
  filename                 = "${path.module}/../../layers/coderipple-package/coderipple-package-layer.zip"
  source_code_hash         = filebase64sha256("${path.module}/../../layers/coderipple-package/coderipple-package-layer.zip")
  
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"]
  
  description = "CodeRipple custom package with agents and tools"
  
  lifecycle {
    create_before_destroy = true
  }
}

# Output layer ARNs for use in functions
output "coderipple_dependencies_layer_arn" {
  description = "ARN of the CodeRipple dependencies layer"
  value       = aws_lambda_layer_version.coderipple_dependencies.arn
}

output "coderipple_dependencies_layer_version" {
  description = "Version of the CodeRipple dependencies layer"
  value       = aws_lambda_layer_version.coderipple_dependencies.version
}

output "coderipple_package_layer_arn" {
  description = "ARN of the CodeRipple package layer"
  value       = aws_lambda_layer_version.coderipple_package.arn
}

output "coderipple_package_layer_version" {
  description = "Version of the CodeRipple package layer"
  value       = aws_lambda_layer_version.coderipple_package.version
}
