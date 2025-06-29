#!/bin/bash
# scripts/aws-infrastructure-deployment.sh
# AWS Infrastructure Deployment for CodeRipple Layer-based Architecture

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Source common functions
if [ -f "layers/shared/build-common.sh" ]; then
    source layers/shared/build-common.sh
else
    # Fallback logging functions
    log_section() { echo -e "\n=== $1 ==="; }
    log_step() { echo "🔍 $1..."; }
    log_success() { echo "✅ $1"; }
    log_error() { echo "❌ $1"; }
    log_warning() { echo "⚠️  $1"; }
    log_debug() { echo "🐛 $1"; }
    log_section_complete() { echo -e "✅ $1 - COMPLETED\n"; }
fi

log_section "CodeRipple AWS Infrastructure Deployment"

# Configuration
DEPLOYMENT_MODE=${DEPLOYMENT_MODE:-"deploy"}  # deploy, plan, validate, destroy
AWS_REGION=${AWS_REGION:-"us-west-2"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
TERRAFORM_DIR="infra/terraform"
GENERATE_REPORT=${GENERATE_REPORT:-true}

# Deployment tracking
DEPLOYMENT_RESULTS=()
INFRASTRUCTURE_OUTPUTS=()

# Add deployment result
add_deployment_result() {
    local status="$1"
    local component="$2"
    local details="$3"
    local resource_id="$4"
    
    DEPLOYMENT_RESULTS+=("$status|$component|$details|$resource_id")
    
    case "$status" in
        "SUCCESS") log_success "$component: $details" ;;
        "FAILED") log_error "$component: $details" ;;
        "WARNING") log_warning "$component: $details" ;;
        *) log_debug "$component: $details" ;;
    esac
}

# Add infrastructure output
add_infrastructure_output() {
    local output_name="$1"
    local output_value="$2"
    local output_type="$3"
    
    INFRASTRUCTURE_OUTPUTS+=("$output_name|$output_value|$output_type")
    log_debug "Output: $output_name = $output_value ($output_type)"
}

# Pre-deployment validation
validate_prerequisites() {
    log_step "Validating deployment prerequisites"
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        add_deployment_result "FAILED" "AWS CLI" "AWS CLI not installed" "N/A"
        return 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        add_deployment_result "FAILED" "AWS Credentials" "AWS credentials not configured or invalid" "N/A"
        return 1
    fi
    
    # Get AWS account info
    aws_account=$(aws sts get-caller-identity --query Account --output text)
    aws_user=$(aws sts get-caller-identity --query Arn --output text)
    add_deployment_result "SUCCESS" "AWS Authentication" "Authenticated as $aws_user in account $aws_account" "$aws_account"
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        add_deployment_result "FAILED" "Terraform" "Terraform not installed" "N/A"
        return 1
    fi
    
    terraform_version=$(terraform version -json | jq -r '.terraform_version')
    add_deployment_result "SUCCESS" "Terraform" "Version $terraform_version available" "$terraform_version"
    
    # Check required tools
    for tool in jq bc; do
        if ! command -v $tool &> /dev/null; then
            add_deployment_result "WARNING" "Tool Check" "$tool not installed (may affect reporting)" "$tool"
        else
            add_deployment_result "SUCCESS" "Tool Check" "$tool available" "$tool"
        fi
    done
    
    # Validate layer artifacts
    if [ -f "layers/dependencies/coderipple-dependencies-layer.zip" ]; then
        deps_size=$(stat -f%z "layers/dependencies/coderipple-dependencies-layer.zip" 2>/dev/null || stat -c%s "layers/dependencies/coderipple-dependencies-layer.zip")
        deps_size_mb=$((deps_size / 1024 / 1024))
        add_deployment_result "SUCCESS" "Dependencies Layer" "Artifact ready: ${deps_size_mb}MB" "dependencies-layer"
    else
        add_deployment_result "FAILED" "Dependencies Layer" "Artifact missing: layers/dependencies/coderipple-dependencies-layer.zip" "dependencies-layer"
        return 1
    fi
    
    if [ -f "layers/coderipple-package/coderipple-package-layer.zip" ]; then
        pkg_size=$(stat -f%z "layers/coderipple-package/coderipple-package-layer.zip" 2>/dev/null || stat -c%s "layers/coderipple-package/coderipple-package-layer.zip")
        pkg_size_kb=$((pkg_size / 1024))
        add_deployment_result "SUCCESS" "Package Layer" "Artifact ready: ${pkg_size_kb}KB" "package-layer"
    else
        add_deployment_result "FAILED" "Package Layer" "Artifact missing: layers/coderipple-package/coderipple-package-layer.zip" "package-layer"
        return 1
    fi
    
    # Validate function build
    if [ -f "functions/orchestrator/function.zip" ]; then
        func_size=$(stat -f%z "functions/orchestrator/function.zip" 2>/dev/null || stat -c%s "functions/orchestrator/function.zip")
        func_size_kb=$((func_size / 1024))
        add_deployment_result "SUCCESS" "Function Package" "Artifact ready: ${func_size_kb}KB" "function-package"
    else
        add_deployment_result "WARNING" "Function Package" "Pre-built artifact missing, will build during deployment" "function-package"
    fi
}

# Initialize Terraform
initialize_terraform() {
    log_step "Initializing Terraform"
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    if terraform init -upgrade > terraform-init.log 2>&1; then
        add_deployment_result "SUCCESS" "Terraform Init" "Terraform initialized successfully" "terraform-init"
    else
        add_deployment_result "FAILED" "Terraform Init" "Terraform initialization failed - check terraform-init.log" "terraform-init"
        cd ../..
        return 1
    fi
    
    # Validate Terraform configuration
    if terraform validate > terraform-validate.log 2>&1; then
        add_deployment_result "SUCCESS" "Terraform Validate" "Configuration is valid" "terraform-validate"
    else
        add_deployment_result "FAILED" "Terraform Validate" "Configuration validation failed - check terraform-validate.log" "terraform-validate"
        cd ../..
        return 1
    fi
    
    cd ../..
}

# Plan Terraform deployment
plan_terraform() {
    log_step "Planning Terraform deployment"
    
    cd "$TERRAFORM_DIR"
    
    # Create Terraform plan
    if terraform plan -out=tfplan -detailed-exitcode > terraform-plan.log 2>&1; then
        plan_exit_code=$?
        case $plan_exit_code in
            0)
                add_deployment_result "SUCCESS" "Terraform Plan" "No changes needed" "terraform-plan"
                ;;
            2)
                add_deployment_result "SUCCESS" "Terraform Plan" "Changes planned successfully" "terraform-plan"
                
                # Extract planned changes
                terraform show -json tfplan > tfplan.json 2>/dev/null || true
                if [ -f "tfplan.json" ]; then
                    planned_creates=$(jq -r '.planned_values.root_module.resources[]? | select(.mode == "managed") | .type' tfplan.json 2>/dev/null | sort | uniq -c | head -10)
                    if [ -n "$planned_creates" ]; then
                        log_debug "Planned resource changes:"
                        echo "$planned_creates" | while read count type; do
                            log_debug "  $count x $type"
                        done
                    fi
                fi
                ;;
        esac
    else
        add_deployment_result "FAILED" "Terraform Plan" "Planning failed - check terraform-plan.log" "terraform-plan"
        cd ../..
        return 1
    fi
    
    cd ../..
}

# Apply Terraform deployment
apply_terraform() {
    log_step "Applying Terraform deployment"
    
    cd "$TERRAFORM_DIR"
    
    # Apply Terraform plan
    if terraform apply -auto-approve tfplan > terraform-apply.log 2>&1; then
        add_deployment_result "SUCCESS" "Terraform Apply" "Infrastructure deployed successfully" "terraform-apply"
        
        # Capture outputs
        capture_terraform_outputs
    else
        add_deployment_result "FAILED" "Terraform Apply" "Deployment failed - check terraform-apply.log" "terraform-apply"
        cd ../..
        return 1
    fi
    
    cd ../..
}

# Capture Terraform outputs
capture_terraform_outputs() {
    log_step "Capturing Terraform outputs"
    
    # Get all outputs
    if terraform output -json > terraform-outputs.json 2>/dev/null; then
        # Parse key outputs
        function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "")
        function_arn=$(terraform output -raw lambda_function_arn 2>/dev/null || echo "")
        api_url=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
        deps_layer_arn=$(terraform output -raw coderipple_dependencies_layer_arn 2>/dev/null || echo "")
        pkg_layer_arn=$(terraform output -raw coderipple_package_layer_arn 2>/dev/null || echo "")
        
        # Store outputs
        [ -n "$function_name" ] && add_infrastructure_output "lambda_function_name" "$function_name" "string"
        [ -n "$function_arn" ] && add_infrastructure_output "lambda_function_arn" "$function_arn" "string"
        [ -n "$api_url" ] && add_infrastructure_output "api_gateway_url" "$api_url" "string"
        [ -n "$deps_layer_arn" ] && add_infrastructure_output "dependencies_layer_arn" "$deps_layer_arn" "string"
        [ -n "$pkg_layer_arn" ] && add_infrastructure_output "package_layer_arn" "$pkg_layer_arn" "string"
        
        add_deployment_result "SUCCESS" "Terraform Outputs" "Infrastructure outputs captured" "terraform-outputs"
    else
        add_deployment_result "WARNING" "Terraform Outputs" "Could not capture outputs" "terraform-outputs"
    fi
}

# Validate deployed infrastructure
validate_deployment() {
    log_step "Validating deployed infrastructure"
    
    cd "$TERRAFORM_DIR"
    
    # Get function name
    function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -n "$function_name" ]; then
        # Test function invocation
        test_payload='{"test": true, "deployment_validation": true}'
        
        if aws lambda invoke \
            --function-name "$function_name" \
            --payload "$test_payload" \
            --cli-binary-format raw-in-base64-out \
            deployment-test-response.json > /dev/null 2>&1; then
            
            # Check response
            if [ -f "deployment-test-response.json" ]; then
                status_code=$(jq -r '.statusCode' deployment-test-response.json 2>/dev/null || echo "unknown")
                if [ "$status_code" = "200" ]; then
                    add_deployment_result "SUCCESS" "Function Test" "Function responding correctly" "$function_name"
                else
                    add_deployment_result "WARNING" "Function Test" "Function returned status $status_code" "$function_name"
                fi
                rm -f deployment-test-response.json
            else
                add_deployment_result "WARNING" "Function Test" "No response file generated" "$function_name"
            fi
        else
            add_deployment_result "WARNING" "Function Test" "Function invocation failed" "$function_name"
        fi
        
        # Check function configuration
        func_config=$(aws lambda get-function-configuration --function-name "$function_name" 2>/dev/null || echo '{}')
        if [ "$func_config" != '{}' ]; then
            layer_count=$(echo "$func_config" | jq -r '.Layers | length' 2>/dev/null || echo "0")
            memory_size=$(echo "$func_config" | jq -r '.MemorySize' 2>/dev/null || echo "unknown")
            
            if [ "$layer_count" = "2" ]; then
                add_deployment_result "SUCCESS" "Layer Configuration" "2 layers attached as expected" "$function_name"
            else
                add_deployment_result "WARNING" "Layer Configuration" "$layer_count layers attached (expected 2)" "$function_name"
            fi
            
            add_deployment_result "SUCCESS" "Function Configuration" "Memory: ${memory_size}MB, Layers: $layer_count" "$function_name"
        fi
    else
        add_deployment_result "FAILED" "Function Validation" "Function name not available from outputs" "N/A"
    fi
    
    cd ../..
}

# Generate deployment report
generate_deployment_report() {
    if [ "$GENERATE_REPORT" != "true" ]; then
        return 0
    fi
    
    log_step "Generating deployment report"
    
    report_file="aws-deployment-report.json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count results
    total_components=0
    successful_components=0
    failed_components=0
    warning_components=0
    
    for result in "${DEPLOYMENT_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_components=$((total_components + 1))
        
        case "$status" in
            "SUCCESS") successful_components=$((successful_components + 1)) ;;
            "FAILED") failed_components=$((failed_components + 1)) ;;
            "WARNING") warning_components=$((warning_components + 1)) ;;
        esac
    done
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "aws_deployment_report": {
    "timestamp": "$timestamp",
    "deployment_mode": "$DEPLOYMENT_MODE",
    "environment": "$ENVIRONMENT",
    "aws_region": "$AWS_REGION",
    "architecture": "single-lambda-with-layers",
    "summary": {
      "total_components": $total_components,
      "successful": $successful_components,
      "failed": $failed_components,
      "warnings": $warning_components,
      "success_rate": $(echo "scale=2; $successful_components * 100 / $total_components" | bc 2>/dev/null || echo "0")
    },
    "deployment_results": [
EOF
    
    # Add deployment results
    first_result=true
    for result in "${DEPLOYMENT_RESULTS[@]}"; do
        if [ "$first_result" = false ]; then
            echo "," >> "$report_file"
        fi
        first_result=false
        
        status=$(echo "$result" | cut -d'|' -f1)
        component=$(echo "$result" | cut -d'|' -f2)
        details=$(echo "$result" | cut -d'|' -f3)
        resource_id=$(echo "$result" | cut -d'|' -f4)
        
        cat >> "$report_file" << EOF
      {
        "component": "$component",
        "status": "$status",
        "details": "$details",
        "resource_id": "$resource_id"
      }
EOF
    done
    
    # Add infrastructure outputs if available
    if [ ${#INFRASTRUCTURE_OUTPUTS[@]} -gt 0 ]; then
        echo "," >> "$report_file"
        echo '    ],' >> "$report_file"
        echo '    "infrastructure_outputs": {' >> "$report_file"
        
        first_output=true
        for output in "${INFRASTRUCTURE_OUTPUTS[@]}"; do
            if [ "$first_output" = false ]; then
                echo "," >> "$report_file"
            fi
            first_output=false
            
            output_name=$(echo "$output" | cut -d'|' -f1)
            output_value=$(echo "$output" | cut -d'|' -f2)
            output_type=$(echo "$output" | cut -d'|' -f3)
            
            cat >> "$report_file" << EOF
      "$output_name": {
        "value": "$output_value",
        "type": "$output_type"
      }
EOF
        done
        
        echo "    }" >> "$report_file"
    else
        echo "" >> "$report_file"
        echo "    ]" >> "$report_file"
    fi
    
    echo "  }" >> "$report_file"
    echo "}" >> "$report_file"
    
    add_deployment_result "SUCCESS" "Deployment Report" "Generated: $report_file" "deployment-report"
}

# Print deployment summary
print_deployment_summary() {
    log_section "AWS Infrastructure Deployment Summary"
    
    # Count results
    total_components=0
    successful_components=0
    failed_components=0
    warning_components=0
    
    for result in "${DEPLOYMENT_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_components=$((total_components + 1))
        
        case "$status" in
            "SUCCESS") successful_components=$((successful_components + 1)) ;;
            "FAILED") failed_components=$((failed_components + 1)) ;;
            "WARNING") warning_components=$((warning_components + 1)) ;;
        esac
    done
    
    echo "📊 Deployment Results:"
    echo "   Total Components: $total_components"
    echo "   ✅ Successful: $successful_components"
    echo "   ❌ Failed: $failed_components"
    echo "   ⚠️  Warnings: $warning_components"
    
    if [ "$total_components" -gt 0 ]; then
        success_rate=$(echo "scale=1; $successful_components * 100 / $total_components" | bc 2>/dev/null || echo "0")
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    echo "🏗️  Infrastructure Deployment:"
    echo "   Mode: $DEPLOYMENT_MODE"
    echo "   Environment: $ENVIRONMENT"
    echo "   Region: $AWS_REGION"
    echo "   Architecture: single-lambda-with-layers"
    
    # Show infrastructure outputs
    if [ ${#INFRASTRUCTURE_OUTPUTS[@]} -gt 0 ]; then
        echo ""
        echo "🔗 Infrastructure Outputs:"
        for output in "${INFRASTRUCTURE_OUTPUTS[@]}"; do
            output_name=$(echo "$output" | cut -d'|' -f1)
            output_value=$(echo "$output" | cut -d'|' -f2)
            echo "   • $output_name: $output_value"
        done
    fi
    
    # Show failures and warnings
    if [ "$failed_components" -gt 0 ]; then
        echo ""
        echo "❌ Failed Components:"
        for result in "${DEPLOYMENT_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "FAILED" ]; then
                component=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $component: $details"
            fi
        done
    fi
    
    if [ "$warning_components" -gt 0 ]; then
        echo ""
        echo "⚠️  Warnings:"
        for result in "${DEPLOYMENT_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "WARNING" ]; then
                component=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $component: $details"
            fi
        done
    fi
    
    echo ""
    
    # Overall result
    if [ "$failed_components" -eq 0 ]; then
        if [ "$warning_components" -eq 0 ]; then
            echo "🎉 AWS infrastructure deployment completed successfully!"
            echo "   Layer-based architecture is now deployed and operational."
            echo ""
            echo "✅ Next Steps:"
            echo "   • Run end-to-end validation: ./scripts/end-to-end-validation.sh"
            echo "   • Test webhook integration: curl -X POST [API_GATEWAY_URL]"
            echo "   • Monitor performance: Check CloudWatch dashboards"
        else
            echo "✅ AWS infrastructure deployment completed with warnings."
            echo "   Layer-based architecture is deployed but may need attention."
        fi
        return 0
    else
        echo "💥 AWS infrastructure deployment failed!"
        echo "   Critical issues prevent successful deployment."
        echo "   Address failed components before retrying deployment."
        return 1
    fi
}

# Main execution flow
main() {
    case "$DEPLOYMENT_MODE" in
        "plan")
            validate_prerequisites
            initialize_terraform
            plan_terraform
            ;;
        "deploy")
            validate_prerequisites
            initialize_terraform
            plan_terraform
            apply_terraform
            validate_deployment
            ;;
        "validate")
            validate_prerequisites
            validate_deployment
            ;;
        "destroy")
            log_warning "Destroy mode not implemented for safety"
            log_warning "Use 'terraform destroy' manually in $TERRAFORM_DIR if needed"
            exit 1
            ;;
        *)
            log_error "Unknown deployment mode: $DEPLOYMENT_MODE"
            log_error "Valid modes: plan, deploy, validate"
            exit 1
            ;;
    esac
    
    generate_deployment_report
    
    if print_deployment_summary; then
        log_section_complete "AWS Infrastructure Deployment"
        exit 0
    else
        log_section_complete "AWS Infrastructure Deployment (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
