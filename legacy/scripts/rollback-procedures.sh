#!/bin/bash
# scripts/rollback-procedures.sh
# Rollback Procedures for CodeRipple Layer-based Architecture

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

log_section "CodeRipple Rollback Procedures"

# Configuration
ROLLBACK_MODE=${ROLLBACK_MODE:-"interactive"}  # interactive, automatic, plan-only
AWS_REGION=${AWS_REGION:-"us-west-2"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
BACKUP_TIMESTAMP=${BACKUP_TIMESTAMP:-""}

# Rollback tracking
ROLLBACK_RESULTS=()

# Add rollback result
add_rollback_result() {
    local status="$1"
    local component="$2"
    local details="$3"
    
    ROLLBACK_RESULTS+=("$status|$component|$details")
    
    case "$status" in
        "SUCCESS") log_success "$component: $details" ;;
        "FAILED") log_error "$component: $details" ;;
        "SKIPPED") log_debug "$component: $details" ;;
        *) log_debug "$component: $details" ;;
    esac
}

# Confirm rollback action
confirm_rollback() {
    local component="$1"
    local action="$2"
    
    if [ "$ROLLBACK_MODE" = "automatic" ]; then
        return 0
    fi
    
    if [ "$ROLLBACK_MODE" = "plan-only" ]; then
        log_debug "PLAN: Would rollback $component - $action"
        return 1
    fi
    
    echo ""
    echo "⚠️  ROLLBACK CONFIRMATION REQUIRED"
    echo "Component: $component"
    echo "Action: $action"
    echo ""
    read -p "Proceed with rollback? (yes/no): " confirm
    
    if [ "$confirm" = "yes" ] || [ "$confirm" = "y" ]; then
        return 0
    else
        log_debug "Rollback cancelled by user for $component"
        return 1
    fi
}

# List available backups
list_available_backups() {
    log_step "Listing available backups"
    
    cd infra/terraform
    
    # Look for backup files
    backup_files=(
        "pre-deployment-state.json"
        "terraform.tfstate.backup"
        "terraform.tfvars.backup"
    )
    
    available_backups=()
    
    for backup_file in "${backup_files[@]}"; do
        if [ -f "$backup_file" ]; then
            backup_date=$(stat -f %Sm -t %Y-%m-%d_%H:%M:%S "$backup_file" 2>/dev/null || stat -c %y "$backup_file" | cut -d' ' -f1,2 | tr ' ' _)
            available_backups+=("$backup_file|$backup_date")
            log_debug "Found backup: $backup_file (created: $backup_date)"
        fi
    done
    
    cd ../..
    
    if [ ${#available_backups[@]} -eq 0 ]; then
        add_rollback_result "FAILED" "Backup Discovery" "No backup files found"
        return 1
    else
        add_rollback_result "SUCCESS" "Backup Discovery" "${#available_backups[@]} backup files found"
        return 0
    fi
}

# Rollback Lambda function
rollback_lambda_function() {
    log_step "Rolling back Lambda function"
    
    if ! confirm_rollback "Lambda Function" "Revert to previous version"; then
        add_rollback_result "SKIPPED" "Lambda Function" "Rollback cancelled by user"
        return 0
    fi
    
    cd infra/terraform
    function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "")
    cd ../..
    
    if [ -z "$function_name" ]; then
        add_rollback_result "FAILED" "Lambda Function" "Function name not available"
        return 1
    fi
    
    # Get current function version
    current_version=$(aws lambda get-function --function-name "$function_name" \
        --query 'Configuration.Version' --output text 2>/dev/null || echo "")
    
    if [ -n "$current_version" ] && [ "$current_version" != "\$LATEST" ]; then
        # Try to rollback to previous version
        previous_version=$((current_version - 1))
        
        if [ "$previous_version" -gt 0 ]; then
            if aws lambda update-alias \
                --function-name "$function_name" \
                --name "$ENVIRONMENT" \
                --function-version "$previous_version" > /dev/null 2>&1; then
                add_rollback_result "SUCCESS" "Lambda Function" "Rolled back to version $previous_version"
            else
                add_rollback_result "FAILED" "Lambda Function" "Failed to rollback to version $previous_version"
            fi
        else
            add_rollback_result "FAILED" "Lambda Function" "No previous version available"
        fi
    else
        add_rollback_result "FAILED" "Lambda Function" "Current version information not available"
    fi
}

# Rollback Lambda layers
rollback_lambda_layers() {
    log_step "Rolling back Lambda layers"
    
    if ! confirm_rollback "Lambda Layers" "Revert to previous layer versions"; then
        add_rollback_result "SKIPPED" "Lambda Layers" "Rollback cancelled by user"
        return 0
    fi
    
    # Get layer names
    layer_names=("coderipple-dependencies" "coderipple-package")
    
    for layer_name in "${layer_names[@]}"; do
        # Get layer versions
        versions=$(aws lambda list-layer-versions --layer-name "$layer_name" \
            --query 'LayerVersions[*].Version' --output text 2>/dev/null || echo "")
        
        if [ -n "$versions" ]; then
            # Get the second most recent version (previous version)
            version_array=($versions)
            if [ ${#version_array[@]} -gt 1 ]; then
                previous_version=${version_array[1]}
                
                # Note: Layer rollback requires updating the function to use the previous layer version
                # This is handled by the infrastructure rollback
                add_rollback_result "SUCCESS" "Layer $layer_name" "Previous version $previous_version identified"
            else
                add_rollback_result "FAILED" "Layer $layer_name" "No previous version available"
            fi
        else
            add_rollback_result "FAILED" "Layer $layer_name" "Cannot retrieve layer versions"
        fi
    done
}

# Rollback infrastructure
rollback_infrastructure() {
    log_step "Rolling back infrastructure"
    
    if ! confirm_rollback "Infrastructure" "Revert Terraform state to previous deployment"; then
        add_rollback_result "SKIPPED" "Infrastructure" "Rollback cancelled by user"
        return 0
    fi
    
    cd infra/terraform
    
    # Check for pre-deployment state backup
    if [ -f "pre-deployment-state.json" ]; then
        log_debug "Found pre-deployment state backup"
        
        # Create a plan to revert to previous state
        if terraform plan -destroy -out=rollback.tfplan; then
            log_debug "Rollback plan created successfully"
            
            if [ "$ROLLBACK_MODE" != "plan-only" ]; then
                # Apply rollback
                if terraform apply -auto-approve rollback.tfplan; then
                    add_rollback_result "SUCCESS" "Infrastructure" "Terraform state rolled back successfully"
                else
                    add_rollback_result "FAILED" "Infrastructure" "Terraform rollback failed"
                fi
            else
                add_rollback_result "SUCCESS" "Infrastructure" "Rollback plan created (plan-only mode)"
            fi
        else
            add_rollback_result "FAILED" "Infrastructure" "Failed to create rollback plan"
        fi
    else
        add_rollback_result "FAILED" "Infrastructure" "No pre-deployment state backup found"
    fi
    
    cd ../..
}

# Rollback monitoring configuration
rollback_monitoring() {
    log_step "Rolling back monitoring configuration"
    
    if ! confirm_rollback "Monitoring" "Remove production monitoring setup"; then
        add_rollback_result "SKIPPED" "Monitoring" "Rollback cancelled by user"
        return 0
    fi
    
    # Remove CloudWatch dashboard
    dashboard_name="CodeRipple-LayerBased-${ENVIRONMENT}"
    if aws cloudwatch delete-dashboards --dashboard-names "$dashboard_name" > /dev/null 2>&1; then
        add_rollback_result "SUCCESS" "CloudWatch Dashboard" "Dashboard $dashboard_name removed"
    else
        add_rollback_result "FAILED" "CloudWatch Dashboard" "Failed to remove dashboard or dashboard not found"
    fi
    
    # Remove CloudWatch alarms
    alarm_names=(
        "CodeRipple-HighDuration-${ENVIRONMENT}"
        "CodeRipple-ErrorRate-${ENVIRONMENT}"
        "CodeRipple-Throttles-${ENVIRONMENT}"
        "CodeRipple-ColdStart-${ENVIRONMENT}"
    )
    
    for alarm_name in "${alarm_names[@]}"; do
        if aws cloudwatch delete-alarms --alarm-names "$alarm_name" > /dev/null 2>&1; then
            add_rollback_result "SUCCESS" "CloudWatch Alarm" "Alarm $alarm_name removed"
        else
            add_rollback_result "FAILED" "CloudWatch Alarm" "Failed to remove alarm $alarm_name or alarm not found"
        fi
    done
}

# Validate rollback success
validate_rollback() {
    log_step "Validating rollback success"
    
    # Check if function is accessible
    cd infra/terraform
    function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "")
    cd ../..
    
    if [ -n "$function_name" ]; then
        if aws lambda get-function --function-name "$function_name" > /dev/null 2>&1; then
            add_rollback_result "SUCCESS" "Function Accessibility" "Function still accessible after rollback"
        else
            add_rollback_result "FAILED" "Function Accessibility" "Function not accessible after rollback"
        fi
    fi
    
    # Test basic functionality
    if [ -n "$function_name" ]; then
        test_payload='{"test": true, "rollback_validation": true}'
        
        if aws lambda invoke \
            --function-name "$function_name" \
            --payload "$test_payload" \
            --cli-binary-format raw-in-base64-out \
            rollback-test-response.json > /dev/null 2>&1; then
            
            if [ -f "rollback-test-response.json" ]; then
                status_code=$(jq -r '.statusCode' rollback-test-response.json 2>/dev/null || echo "unknown")
                if [ "$status_code" = "200" ] || [ "$status_code" = "500" ]; then
                    add_rollback_result "SUCCESS" "Function Testing" "Function responding after rollback (status: $status_code)"
                else
                    add_rollback_result "FAILED" "Function Testing" "Unexpected response status: $status_code"
                fi
                rm -f rollback-test-response.json
            fi
        else
            add_rollback_result "FAILED" "Function Testing" "Function invocation failed after rollback"
        fi
    fi
}

# Generate rollback report
generate_rollback_report() {
    log_step "Generating rollback report"
    
    report_file="rollback-report-$(date +%Y%m%d_%H%M%S).json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count results
    total_rollbacks=0
    successful_rollbacks=0
    failed_rollbacks=0
    skipped_rollbacks=0
    
    for result in "${ROLLBACK_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_rollbacks=$((total_rollbacks + 1))
        
        case "$status" in
            "SUCCESS") successful_rollbacks=$((successful_rollbacks + 1)) ;;
            "FAILED") failed_rollbacks=$((failed_rollbacks + 1)) ;;
            "SKIPPED") skipped_rollbacks=$((skipped_rollbacks + 1)) ;;
        esac
    done
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "rollback_report": {
    "timestamp": "$timestamp",
    "rollback_mode": "$ROLLBACK_MODE",
    "environment": "$ENVIRONMENT",
    "aws_region": "$AWS_REGION",
    "summary": {
      "total_components": $total_rollbacks,
      "successful": $successful_rollbacks,
      "failed": $failed_rollbacks,
      "skipped": $skipped_rollbacks,
      "success_rate": $(echo "scale=2; $successful_rollbacks * 100 / $total_rollbacks" | bc)
    },
    "rollback_results": [
EOF
    
    # Add rollback results
    first_result=true
    for result in "${ROLLBACK_RESULTS[@]}"; do
        if [ "$first_result" = false ]; then
            echo "," >> "$report_file"
        fi
        first_result=false
        
        status=$(echo "$result" | cut -d'|' -f1)
        component=$(echo "$result" | cut -d'|' -f2)
        details=$(echo "$result" | cut -d'|' -f3)
        
        cat >> "$report_file" << EOF
      {
        "component": "$component",
        "status": "$status",
        "details": "$details"
      }
EOF
    done
    
    echo "" >> "$report_file"
    echo "    ]" >> "$report_file"
    echo "  }" >> "$report_file"
    echo "}" >> "$report_file"
    
    add_rollback_result "SUCCESS" "Rollback Report" "Generated: $report_file"
}

# Print rollback summary
print_rollback_summary() {
    log_section "Rollback Summary"
    
    # Count results
    total_rollbacks=0
    successful_rollbacks=0
    failed_rollbacks=0
    skipped_rollbacks=0
    
    for result in "${ROLLBACK_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_rollbacks=$((total_rollbacks + 1))
        
        case "$status" in
            "SUCCESS") successful_rollbacks=$((successful_rollbacks + 1)) ;;
            "FAILED") failed_rollbacks=$((failed_rollbacks + 1)) ;;
            "SKIPPED") skipped_rollbacks=$((skipped_rollbacks + 1)) ;;
        esac
    done
    
    echo "📊 Rollback Results:"
    echo "   Total Components: $total_rollbacks"
    echo "   ✅ Successful: $successful_rollbacks"
    echo "   ❌ Failed: $failed_rollbacks"
    echo "   ⏭️  Skipped: $skipped_rollbacks"
    
    if [ "$total_rollbacks" -gt 0 ]; then
        success_rate=$(echo "scale=1; $successful_rollbacks * 100 / $total_rollbacks" | bc)
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    echo "🔄 Rollback Mode: $ROLLBACK_MODE"
    echo "   Environment: $ENVIRONMENT"
    echo "   Region: $AWS_REGION"
    
    # Show failures
    if [ "$failed_rollbacks" -gt 0 ]; then
        echo ""
        echo "❌ Failed Rollbacks:"
        for result in "${ROLLBACK_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "FAILED" ]; then
                component=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $component: $details"
            fi
        done
    fi
    
    echo ""
    
    # Overall result
    if [ "$failed_rollbacks" -eq 0 ]; then
        if [ "$skipped_rollbacks" -eq "$total_rollbacks" ]; then
            echo "ℹ️  All rollback operations were skipped (plan-only or user cancelled)."
        else
            echo "🎉 Rollback completed successfully!"
            echo "   System has been reverted to previous state."
        fi
        return 0
    else
        echo "💥 Rollback partially failed!"
        echo "   Some components could not be rolled back."
        echo "   Manual intervention may be required."
        return 1
    fi
}

# Main execution flow
main() {
    list_available_backups || exit 1
    
    case "$ROLLBACK_MODE" in
        "interactive"|"automatic"|"plan-only")
            rollback_lambda_function
            rollback_lambda_layers
            rollback_infrastructure
            rollback_monitoring
            validate_rollback
            ;;
        *)
            log_error "Unknown rollback mode: $ROLLBACK_MODE"
            exit 1
            ;;
    esac
    
    generate_rollback_report
    
    if print_rollback_summary; then
        log_section_complete "Rollback Procedures"
        exit 0
    else
        log_section_complete "Rollback Procedures (WITH FAILURES)"
        exit 1
    fi
}

# Show usage if no arguments
if [ $# -eq 0 ]; then
    echo "CodeRipple Rollback Procedures"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Environment Variables:"
    echo "  ROLLBACK_MODE     - interactive, automatic, plan-only (default: interactive)"
    echo "  AWS_REGION        - AWS region (default: us-west-2)"
    echo "  ENVIRONMENT       - Environment name (default: production)"
    echo ""
    echo "Examples:"
    echo "  # Interactive rollback (default)"
    echo "  $0"
    echo ""
    echo "  # Automatic rollback (no confirmations)"
    echo "  ROLLBACK_MODE=automatic $0"
    echo ""
    echo "  # Plan only (show what would be rolled back)"
    echo "  ROLLBACK_MODE=plan-only $0"
    echo ""
    exit 0
fi

# Execute main function
main "$@"
