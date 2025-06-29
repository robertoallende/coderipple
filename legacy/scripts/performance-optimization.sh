#!/bin/bash
# scripts/performance-optimization.sh
# Performance Optimization for CodeRipple Layer-based Architecture

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

log_section "CodeRipple Performance Optimization"

# Configuration
OPTIMIZATION_MODE=${OPTIMIZATION_MODE:-"full"}  # full, layers-only, function-only
AWS_REGION=${AWS_REGION:-"us-west-2"}
APPLY_OPTIMIZATIONS=${APPLY_OPTIMIZATIONS:-false}
GENERATE_REPORT=${GENERATE_REPORT:-true}

# Optimization results tracking
OPTIMIZATION_RESULTS=()
PERFORMANCE_IMPROVEMENTS=()

# Add optimization result
add_optimization() {
    local category="$1"
    local optimization="$2"
    local impact="$3"
    local status="$4"
    
    OPTIMIZATION_RESULTS+=("$category|$optimization|$impact|$status")
    
    case "$status" in
        "APPLIED") log_success "$optimization: $impact" ;;
        "RECOMMENDED") log_warning "$optimization: $impact (recommended)" ;;
        "SKIPPED") log_debug "$optimization: $impact (skipped)" ;;
        *) log_debug "$optimization: $impact" ;;
    esac
}

# Add performance improvement
add_improvement() {
    local metric="$1"
    local before="$2"
    local after="$3"
    local improvement="$4"
    
    PERFORMANCE_IMPROVEMENTS+=("$metric|$before|$after|$improvement")
    log_success "Performance improvement: $metric improved by $improvement"
}

# Analyze current architecture
analyze_current_architecture() {
    log_step "Analyzing current architecture"
    
    # Check layer sizes
    deps_layer="layers/dependencies/coderipple-dependencies-layer.zip"
    pkg_layer="layers/coderipple-package/coderipple-package-layer.zip"
    function_zip="functions/orchestrator/function.zip"
    
    if [ -f "$deps_layer" ]; then
        deps_size_bytes=$(stat -f%z "$deps_layer" 2>/dev/null || stat -c%s "$deps_layer")
        deps_size_mb=$((deps_size_bytes / 1024 / 1024))
        log_debug "Dependencies layer: ${deps_size_mb}MB"
        
        if [ "$deps_size_mb" -gt 40 ]; then
            add_optimization "LAYER" "Dependencies Layer Size" "Reduce from ${deps_size_mb}MB" "RECOMMENDED"
        else
            add_optimization "LAYER" "Dependencies Layer Size" "${deps_size_mb}MB (optimal)" "GOOD"
        fi
    fi
    
    if [ -f "$pkg_layer" ]; then
        pkg_size_bytes=$(stat -f%z "$pkg_layer" 2>/dev/null || stat -c%s "$pkg_layer")
        pkg_size_kb=$((pkg_size_bytes / 1024))
        log_debug "Package layer: ${pkg_size_kb}KB"
        
        if [ "$pkg_size_kb" -gt 500 ]; then
            add_optimization "LAYER" "Package Layer Size" "Reduce from ${pkg_size_kb}KB" "RECOMMENDED"
        else
            add_optimization "LAYER" "Package Layer Size" "${pkg_size_kb}KB (optimal)" "GOOD"
        fi
    fi
    
    if [ -f "$function_zip" ]; then
        func_size_bytes=$(stat -f%z "$function_zip" 2>/dev/null || stat -c%s "$function_zip")
        func_size_kb=$((func_size_bytes / 1024))
        log_debug "Function package: ${func_size_kb}KB"
        
        if [ "$func_size_kb" -gt 50 ]; then
            add_optimization "FUNCTION" "Function Package Size" "Reduce from ${func_size_kb}KB" "RECOMMENDED"
        else
            add_optimization "FUNCTION" "Function Package Size" "${func_size_kb}KB (excellent)" "GOOD"
        fi
    fi
}

# Optimize layer sizes
optimize_layers() {
    if [ "$OPTIMIZATION_MODE" = "function-only" ]; then
        log_debug "Skipping layer optimization in function-only mode"
        return 0
    fi
    
    log_step "Optimizing layer sizes"
    
    # Dependencies layer optimization
    deps_layer="layers/dependencies/coderipple-dependencies-layer.zip"
    if [ -f "$deps_layer" ]; then
        original_size=$(stat -f%z "$deps_layer" 2>/dev/null || stat -c%s "$deps_layer")
        
        if [ "$APPLY_OPTIMIZATIONS" = "true" ]; then
            log_debug "Rebuilding dependencies layer with optimization..."
            cd layers/dependencies
            BUILD_MODE=full DO_OPTIMIZE=true ./build-automation.sh
            cd ../..
            
            new_size=$(stat -f%z "$deps_layer" 2>/dev/null || stat -c%s "$deps_layer")
            if [ "$new_size" -lt "$original_size" ]; then
                reduction=$((100 - (new_size * 100 / original_size)))
                add_improvement "Dependencies Layer Size" "${original_size} bytes" "${new_size} bytes" "${reduction}%"
                add_optimization "LAYER" "Dependencies Layer Optimization" "Applied advanced optimization" "APPLIED"
            else
                add_optimization "LAYER" "Dependencies Layer Optimization" "No significant reduction achieved" "APPLIED"
            fi
        else
            add_optimization "LAYER" "Dependencies Layer Optimization" "Rebuild with DO_OPTIMIZE=true" "RECOMMENDED"
        fi
    fi
    
    # Package layer optimization
    pkg_layer="layers/coderipple-package/coderipple-package-layer.zip"
    if [ -f "$pkg_layer" ]; then
        original_size=$(stat -f%z "$pkg_layer" 2>/dev/null || stat -c%s "$pkg_layer")
        
        if [ "$APPLY_OPTIMIZATIONS" = "true" ]; then
            log_debug "Rebuilding package layer with optimization..."
            cd layers/coderipple-package
            BUILD_MODE=full DO_OPTIMIZE=true ./build-automation.sh
            cd ../..
            
            new_size=$(stat -f%z "$pkg_layer" 2>/dev/null || stat -c%s "$pkg_layer")
            if [ "$new_size" -lt "$original_size" ]; then
                reduction=$((100 - (new_size * 100 / original_size)))
                add_improvement "Package Layer Size" "${original_size} bytes" "${new_size} bytes" "${reduction}%"
                add_optimization "LAYER" "Package Layer Optimization" "Applied advanced optimization" "APPLIED"
            else
                add_optimization "LAYER" "Package Layer Optimization" "No significant reduction achieved" "APPLIED"
            fi
        else
            add_optimization "LAYER" "Package Layer Optimization" "Rebuild with DO_OPTIMIZE=true" "RECOMMENDED"
        fi
    fi
}

# Optimize function package
optimize_function() {
    if [ "$OPTIMIZATION_MODE" = "layers-only" ]; then
        log_debug "Skipping function optimization in layers-only mode"
        return 0
    fi
    
    log_step "Optimizing function package"
    
    function_zip="functions/orchestrator/function.zip"
    if [ -f "$function_zip" ]; then
        original_size=$(stat -f%z "$function_zip" 2>/dev/null || stat -c%s "$function_zip")
        
        if [ "$APPLY_OPTIMIZATIONS" = "true" ]; then
            log_debug "Rebuilding function with optimization..."
            cd functions/orchestrator
            BUILD_MODE=full DO_OPTIMIZE=true ./build-automation.sh
            cd ../..
            
            new_size=$(stat -f%z "$function_zip" 2>/dev/null || stat -c%s "$function_zip")
            if [ "$new_size" -lt "$original_size" ]; then
                reduction=$((100 - (new_size * 100 / original_size)))
                add_improvement "Function Package Size" "${original_size} bytes" "${new_size} bytes" "${reduction}%"
                add_optimization "FUNCTION" "Function Package Optimization" "Applied advanced optimization" "APPLIED"
            else
                add_optimization "FUNCTION" "Function Package Optimization" "Already optimally sized" "APPLIED"
            fi
        else
            add_optimization "FUNCTION" "Function Package Optimization" "Rebuild with DO_OPTIMIZE=true" "RECOMMENDED"
        fi
    fi
}

# Analyze Lambda configuration
analyze_lambda_configuration() {
    log_step "Analyzing Lambda configuration"
    
    function_name=$(cd infra/terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -n "$function_name" ]; then
        # Get current function configuration
        func_config=$(aws lambda get-function-configuration --function-name "$function_name" 2>/dev/null || echo '{}')
        
        if [ "$func_config" != '{}' ]; then
            memory_size=$(echo "$func_config" | jq -r '.MemorySize')
            timeout=$(echo "$func_config" | jq -r '.Timeout')
            
            log_debug "Current configuration: ${memory_size}MB memory, ${timeout}s timeout"
            
            # Memory optimization recommendations
            if [ "$memory_size" -gt 1536 ]; then
                add_optimization "LAMBDA" "Memory Allocation" "Reduce from ${memory_size}MB to 1024MB for layer-based architecture" "RECOMMENDED"
            elif [ "$memory_size" -lt 512 ]; then
                add_optimization "LAMBDA" "Memory Allocation" "Increase from ${memory_size}MB to 512MB for better performance" "RECOMMENDED"
            else
                add_optimization "LAMBDA" "Memory Allocation" "${memory_size}MB (optimal for layer-based)" "GOOD"
            fi
            
            # Timeout optimization
            if [ "$timeout" -gt 60 ]; then
                add_optimization "LAMBDA" "Timeout Setting" "Reduce from ${timeout}s to 30s for webhook processing" "RECOMMENDED"
            elif [ "$timeout" -lt 15 ]; then
                add_optimization "LAMBDA" "Timeout Setting" "Increase from ${timeout}s to 30s for safety" "RECOMMENDED"
            else
                add_optimization "LAMBDA" "Timeout Setting" "${timeout}s (appropriate)" "GOOD"
            fi
            
            # Reserved concurrency check
            reserved_concurrency=$(echo "$func_config" | jq -r '.ReservedConcurrencyExecutions // "null"')
            if [ "$reserved_concurrency" = "null" ]; then
                add_optimization "LAMBDA" "Reserved Concurrency" "Set to 10 for cost control" "RECOMMENDED"
            else
                add_optimization "LAMBDA" "Reserved Concurrency" "${reserved_concurrency} (configured)" "GOOD"
            fi
        else
            add_optimization "LAMBDA" "Configuration Analysis" "Function not deployed or not accessible" "SKIPPED"
        fi
    else
        add_optimization "LAMBDA" "Configuration Analysis" "Function name not available from Terraform" "SKIPPED"
    fi
}

# Optimize CloudWatch logging
optimize_cloudwatch_logging() {
    log_step "Optimizing CloudWatch logging"
    
    function_name=$(cd infra/terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -n "$function_name" ]; then
        log_group_name="/aws/lambda/$function_name"
        
        # Check log retention
        retention_days=$(aws logs describe-log-groups \
            --log-group-name-prefix "$log_group_name" \
            --query 'logGroups[0].retentionInDays' \
            --output text 2>/dev/null || echo "null")
        
        if [ "$retention_days" = "null" ] || [ "$retention_days" = "None" ]; then
            add_optimization "CLOUDWATCH" "Log Retention" "Set to 14 days to reduce costs" "RECOMMENDED"
        elif [ "$retention_days" -gt 30 ]; then
            add_optimization "CLOUDWATCH" "Log Retention" "Reduce from ${retention_days} to 14 days" "RECOMMENDED"
        else
            add_optimization "CLOUDWATCH" "Log Retention" "${retention_days} days (appropriate)" "GOOD"
        fi
        
        # Check log level optimization
        add_optimization "CLOUDWATCH" "Log Level" "Use INFO level in production, DEBUG for troubleshooting" "RECOMMENDED"
    fi
}

# Performance monitoring recommendations
recommend_monitoring() {
    log_step "Analyzing monitoring setup"
    
    # X-Ray tracing
    function_name=$(cd infra/terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -n "$function_name" ]; then
        func_config=$(aws lambda get-function-configuration --function-name "$function_name" 2>/dev/null || echo '{}')
        
        if [ "$func_config" != '{}' ]; then
            tracing_mode=$(echo "$func_config" | jq -r '.TracingConfig.Mode // "PassThrough"')
            
            if [ "$tracing_mode" = "Active" ]; then
                add_optimization "MONITORING" "X-Ray Tracing" "Active (good for performance analysis)" "GOOD"
            else
                add_optimization "MONITORING" "X-Ray Tracing" "Enable Active tracing for performance insights" "RECOMMENDED"
            fi
        fi
    fi
    
    # CloudWatch alarms
    add_optimization "MONITORING" "CloudWatch Alarms" "Set up alarms for duration, errors, and throttles" "RECOMMENDED"
    add_optimization "MONITORING" "Custom Metrics" "Add custom metrics for layer load times" "RECOMMENDED"
    add_optimization "MONITORING" "Dashboard" "Create CloudWatch dashboard for layer-based architecture" "RECOMMENDED"
}

# Apply Terraform optimizations
apply_terraform_optimizations() {
    if [ "$APPLY_OPTIMIZATIONS" != "true" ]; then
        log_debug "Skipping Terraform optimizations (APPLY_OPTIMIZATIONS=false)"
        return 0
    fi
    
    log_step "Applying Terraform optimizations"
    
    cd infra/terraform
    
    # Create optimized variables
    cat > terraform.tfvars.optimized << EOF
# Optimized configuration for layer-based architecture
lambda_memory_size = 1024
lambda_timeout = 30
lambda_reserved_concurrency = 10
log_retention_days = 14

# Performance optimizations
enable_xray_tracing = true
enable_enhanced_monitoring = true
EOF
    
    if [ -f "terraform.tfvars" ]; then
        log_debug "Backing up existing terraform.tfvars"
        cp terraform.tfvars terraform.tfvars.backup
    fi
    
    log_debug "Applying optimized configuration"
    cp terraform.tfvars.optimized terraform.tfvars
    
    # Plan and apply optimizations
    terraform plan -out=optimization.tfplan
    
    if terraform apply -auto-approve optimization.tfplan; then
        add_optimization "TERRAFORM" "Configuration Optimization" "Applied optimized Lambda configuration" "APPLIED"
    else
        add_optimization "TERRAFORM" "Configuration Optimization" "Failed to apply optimizations" "FAILED"
        
        # Restore backup if it exists
        if [ -f "terraform.tfvars.backup" ]; then
            mv terraform.tfvars.backup terraform.tfvars
        fi
    fi
    
    cd ../..
}

# Generate optimization report
generate_optimization_report() {
    if [ "$GENERATE_REPORT" != "true" ]; then
        return 0
    fi
    
    log_step "Generating optimization report"
    
    report_file="optimization-report.json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count optimizations by category and status
    total_optimizations=0
    applied_optimizations=0
    recommended_optimizations=0
    
    for result in "${OPTIMIZATION_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f4)
        total_optimizations=$((total_optimizations + 1))
        
        case "$status" in
            "APPLIED") applied_optimizations=$((applied_optimizations + 1)) ;;
            "RECOMMENDED") recommended_optimizations=$((recommended_optimizations + 1)) ;;
        esac
    done
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "optimization_report": {
    "timestamp": "$timestamp",
    "optimization_mode": "$OPTIMIZATION_MODE",
    "optimizations_applied": $APPLY_OPTIMIZATIONS,
    "architecture": "single-lambda-with-layers",
    "summary": {
      "total_optimizations": $total_optimizations,
      "applied": $applied_optimizations,
      "recommended": $recommended_optimizations,
      "application_rate": $(echo "scale=2; $applied_optimizations * 100 / $total_optimizations" | bc)
    },
    "optimization_results": [
EOF
    
    # Add optimization results
    first_result=true
    for result in "${OPTIMIZATION_RESULTS[@]}"; do
        if [ "$first_result" = false ]; then
            echo "," >> "$report_file"
        fi
        first_result=false
        
        category=$(echo "$result" | cut -d'|' -f1)
        optimization=$(echo "$result" | cut -d'|' -f2)
        impact=$(echo "$result" | cut -d'|' -f3)
        status=$(echo "$result" | cut -d'|' -f4)
        
        cat >> "$report_file" << EOF
      {
        "category": "$category",
        "optimization": "$optimization",
        "impact": "$impact",
        "status": "$status"
      }
EOF
    done
    
    # Add performance improvements if available
    if [ ${#PERFORMANCE_IMPROVEMENTS[@]} -gt 0 ]; then
        echo "," >> "$report_file"
        echo '    ],' >> "$report_file"
        echo '    "performance_improvements": [' >> "$report_file"
        
        first_improvement=true
        for improvement in "${PERFORMANCE_IMPROVEMENTS[@]}"; do
            if [ "$first_improvement" = false ]; then
                echo "," >> "$report_file"
            fi
            first_improvement=false
            
            metric=$(echo "$improvement" | cut -d'|' -f1)
            before=$(echo "$improvement" | cut -d'|' -f2)
            after=$(echo "$improvement" | cut -d'|' -f3)
            improvement_pct=$(echo "$improvement" | cut -d'|' -f4)
            
            cat >> "$report_file" << EOF
      {
        "metric": "$metric",
        "before": "$before",
        "after": "$after",
        "improvement": "$improvement_pct"
      }
EOF
        done
        
        echo "    ]" >> "$report_file"
    else
        echo "" >> "$report_file"
        echo "    ]" >> "$report_file"
    fi
    
    echo "  }" >> "$report_file"
    echo "}" >> "$report_file"
    
    log_success "Optimization report generated: $report_file"
}

# Print optimization summary
print_optimization_summary() {
    log_section "Optimization Summary"
    
    # Count results by category and status
    total_optimizations=0
    applied_optimizations=0
    recommended_optimizations=0
    
    layer_optimizations=0
    function_optimizations=0
    lambda_optimizations=0
    monitoring_optimizations=0
    
    for result in "${OPTIMIZATION_RESULTS[@]}"; do
        category=$(echo "$result" | cut -d'|' -f1)
        status=$(echo "$result" | cut -d'|' -f4)
        total_optimizations=$((total_optimizations + 1))
        
        case "$status" in
            "APPLIED") applied_optimizations=$((applied_optimizations + 1)) ;;
            "RECOMMENDED") recommended_optimizations=$((recommended_optimizations + 1)) ;;
        esac
        
        case "$category" in
            "LAYER") layer_optimizations=$((layer_optimizations + 1)) ;;
            "FUNCTION") function_optimizations=$((function_optimizations + 1)) ;;
            "LAMBDA") lambda_optimizations=$((lambda_optimizations + 1)) ;;
            "MONITORING") monitoring_optimizations=$((monitoring_optimizations + 1)) ;;
        esac
    done
    
    echo "📊 Optimization Results:"
    echo "   Total Optimizations: $total_optimizations"
    echo "   ✅ Applied: $applied_optimizations"
    echo "   💡 Recommended: $recommended_optimizations"
    
    if [ "$total_optimizations" -gt 0 ]; then
        application_rate=$(echo "scale=1; $applied_optimizations * 100 / $total_optimizations" | bc)
        echo "   📈 Application Rate: ${application_rate}%"
    fi
    
    echo ""
    echo "🏗️  Optimization Categories:"
    echo "   • Layer Optimizations: $layer_optimizations"
    echo "   • Function Optimizations: $function_optimizations"
    echo "   • Lambda Config: $lambda_optimizations"
    echo "   • Monitoring: $monitoring_optimizations"
    echo ""
    
    # Show performance improvements
    if [ ${#PERFORMANCE_IMPROVEMENTS[@]} -gt 0 ]; then
        echo "⚡ Performance Improvements:"
        for improvement in "${PERFORMANCE_IMPROVEMENTS[@]}"; do
            metric=$(echo "$improvement" | cut -d'|' -f1)
            improvement_pct=$(echo "$improvement" | cut -d'|' -f4)
            echo "   • $metric: $improvement_pct improvement"
        done
        echo ""
    fi
    
    # Show recommendations
    if [ "$recommended_optimizations" -gt 0 ]; then
        echo "💡 Recommended Optimizations:"
        for result in "${OPTIMIZATION_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f4)
            if [ "$status" = "RECOMMENDED" ]; then
                optimization=$(echo "$result" | cut -d'|' -f2)
                impact=$(echo "$result" | cut -d'|' -f3)
                echo "   • $optimization: $impact"
            fi
        done
        echo ""
        echo "To apply recommendations, run with APPLY_OPTIMIZATIONS=true"
        echo ""
    fi
    
    # Overall result
    if [ "$applied_optimizations" -gt 0 ]; then
        echo "🎉 Optimizations applied successfully! Performance improvements achieved."
    elif [ "$recommended_optimizations" -gt 0 ]; then
        echo "✅ Analysis completed. Review recommendations for performance improvements."
    else
        echo "✅ Architecture is already optimally configured."
    fi
}

# Main execution flow
main() {
    analyze_current_architecture
    
    case "$OPTIMIZATION_MODE" in
        "full")
            optimize_layers
            optimize_function
            analyze_lambda_configuration
            optimize_cloudwatch_logging
            recommend_monitoring
            apply_terraform_optimizations
            ;;
        "layers-only")
            optimize_layers
            ;;
        "function-only")
            optimize_function
            ;;
        *)
            log_error "Unknown optimization mode: $OPTIMIZATION_MODE"
            exit 1
            ;;
    esac
    
    generate_optimization_report
    print_optimization_summary
    
    log_section_complete "Performance Optimization"
}

# Execute main function
main "$@"
