#!/bin/bash
# scripts/deployment-orchestrator.sh
# Deployment orchestrator for CodeRipple layer-based architecture
# Coordinates layer building, infrastructure deployment, and validation

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

log_section "CodeRipple Deployment Orchestrator"

# Configuration
DEPLOYMENT_ACTION=${DEPLOYMENT_ACTION:-"build-and-validate"}  # build-layers, build-and-validate, full-deploy, validate-only
ENVIRONMENT=${ENVIRONMENT:-"production"}
AWS_REGION=${AWS_REGION:-"us-west-2"}
VALIDATION_MODE=${VALIDATION_MODE:-"comprehensive"}
SKIP_CONFIRMATION=${SKIP_CONFIRMATION:-false}

# Deployment tracking
ORCHESTRATION_RESULTS=()
DEPLOYMENT_ARTIFACTS=()

# Add orchestration result
add_orchestration_result() {
    local status="$1"
    local phase="$2"
    local details="$3"
    local duration="$4"
    
    ORCHESTRATION_RESULTS+=("$status|$phase|$details|$duration")
    
    case "$status" in
        "SUCCESS") log_success "$phase: $details (${duration}s)" ;;
        "FAILED") log_error "$phase: $details (${duration}s)" ;;
        "SKIPPED") log_warning "$phase: $details" ;;
        *) log_debug "$phase: $details" ;;
    esac
}

# Add deployment artifact
add_deployment_artifact() {
    local artifact_type="$1"
    local artifact_path="$2"
    local artifact_size="$3"
    
    DEPLOYMENT_ARTIFACTS+=("$artifact_type|$artifact_path|$artifact_size")
    log_debug "Artifact: $artifact_type at $artifact_path ($artifact_size)"
}

# Build all layers
build_layers() {
    log_step "Building Lambda layers"
    local start_time=$(date +%s)
    
    # Build dependencies layer
    if [ -f "layers/dependencies/build-automation.sh" ]; then
        cd layers/dependencies
        if BUILD_MODE=quick ./build-automation.sh > build.log 2>&1; then
            if [ -f "coderipple-dependencies-layer.zip" ]; then
                deps_size=$(stat -f%z "coderipple-dependencies-layer.zip" 2>/dev/null || stat -c%s "coderipple-dependencies-layer.zip")
                deps_size_mb=$((deps_size / 1024 / 1024))
                add_deployment_artifact "dependencies-layer" "layers/dependencies/coderipple-dependencies-layer.zip" "${deps_size_mb}MB"
            fi
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            add_orchestration_result "FAILED" "Dependencies Layer Build" "Build failed - check layers/dependencies/build.log" "$duration"
            cd ../..
            return 1
        fi
        cd ../..
    else
        add_orchestration_result "SKIPPED" "Dependencies Layer Build" "Build script not found" "0"
    fi
    
    # Build package layer
    if [ -f "layers/coderipple-package/build-automation.sh" ]; then
        cd layers/coderipple-package
        if BUILD_MODE=quick ./build-automation.sh > build.log 2>&1; then
            if [ -f "coderipple-package-layer.zip" ]; then
                pkg_size=$(stat -f%z "coderipple-package-layer.zip" 2>/dev/null || stat -c%s "coderipple-package-layer.zip")
                pkg_size_kb=$((pkg_size / 1024))
                add_deployment_artifact "package-layer" "layers/coderipple-package/coderipple-package-layer.zip" "${pkg_size_kb}KB"
            fi
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            add_orchestration_result "FAILED" "Package Layer Build" "Build failed - check layers/coderipple-package/build.log" "$duration"
            cd ../..
            return 1
        fi
        cd ../..
    else
        add_orchestration_result "SKIPPED" "Package Layer Build" "Build script not found" "0"
    fi
    
    # Build function package
    if [ -f "functions/orchestrator/build-automation.sh" ]; then
        cd functions/orchestrator
        if ./build-automation.sh > build.log 2>&1; then
            if [ -f "function.zip" ]; then
                func_size=$(stat -f%z "function.zip" 2>/dev/null || stat -c%s "function.zip")
                func_size_kb=$((func_size / 1024))
                add_deployment_artifact "function-package" "functions/orchestrator/function.zip" "${func_size_kb}KB"
            fi
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            add_orchestration_result "FAILED" "Function Package Build" "Build failed - check functions/orchestrator/build.log" "$duration"
            cd ../..
            return 1
        fi
        cd ../..
    else
        add_orchestration_result "SKIPPED" "Function Package Build" "Build script not found" "0"
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    add_orchestration_result "SUCCESS" "Layer Building" "All layers built successfully" "$duration"
}

# Deploy infrastructure (GitHub Actions only)
deploy_infrastructure() {
    log_step "Triggering infrastructure deployment"
    local start_time=$(date +%s)
    
    if [ -n "$GITHUB_ACTIONS" ]; then
        # Running in GitHub Actions - deployment handled by workflow
        add_orchestration_result "SUCCESS" "Infrastructure Deployment" "Handled by GitHub Actions workflow" "0"
    else
        # Local environment - provide instructions
        log_warning "Infrastructure deployment requires GitHub Actions"
        log_warning "Trigger deployment via GitHub Actions workflow:"
        log_warning "  1. Go to Actions tab in GitHub repository"
        log_warning "  2. Select 'Deploy Layer-based Infrastructure' workflow"
        log_warning "  3. Choose 'deploy' action and confirm with 'yes'"
        
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        add_orchestration_result "SKIPPED" "Infrastructure Deployment" "Manual trigger required via GitHub Actions" "$duration"
    fi
}

# Run validation
run_validation() {
    log_step "Running end-to-end validation"
    local start_time=$(date +%s)
    
    if [ -f "scripts/end-to-end-validation.sh" ]; then
        export VALIDATION_MODE="$VALIDATION_MODE"
        export ENVIRONMENT="$ENVIRONMENT"
        export AWS_REGION="$AWS_REGION"
        
        if ./scripts/end-to-end-validation.sh > validation.log 2>&1; then
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            add_orchestration_result "SUCCESS" "End-to-End Validation" "All validations passed" "$duration"
            
            # Extract validation summary if report exists
            if [ -f "e2e-validation-report.json" ]; then
                total_tests=$(jq -r '.e2e_validation_report.summary.total_tests' e2e-validation-report.json 2>/dev/null || echo "unknown")
                success_rate=$(jq -r '.e2e_validation_report.summary.success_rate' e2e-validation-report.json 2>/dev/null || echo "unknown")
                log_debug "Validation summary: $total_tests tests, ${success_rate}% success rate"
            fi
        else
            local end_time=$(date +%s)
            local duration=$((end_time - start_time))
            add_orchestration_result "FAILED" "End-to-End Validation" "Validation failed - check validation.log" "$duration"
            return 1
        fi
    else
        local end_time=$(date +%s)
        local duration=$((end_time - start_time))
        add_orchestration_result "SKIPPED" "End-to-End Validation" "Validation script not found" "$duration"
    fi
}

# Generate orchestration report
generate_orchestration_report() {
    log_step "Generating orchestration report"
    
    report_file="deployment-orchestration-report.json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count results
    total_phases=0
    successful_phases=0
    failed_phases=0
    skipped_phases=0
    
    for result in "${ORCHESTRATION_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_phases=$((total_phases + 1))
        
        case "$status" in
            "SUCCESS") successful_phases=$((successful_phases + 1)) ;;
            "FAILED") failed_phases=$((failed_phases + 1)) ;;
            "SKIPPED") skipped_phases=$((skipped_phases + 1)) ;;
        esac
    done
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "deployment_orchestration_report": {
    "timestamp": "$timestamp",
    "deployment_action": "$DEPLOYMENT_ACTION",
    "environment": "$ENVIRONMENT",
    "aws_region": "$AWS_REGION",
    "validation_mode": "$VALIDATION_MODE",
    "summary": {
      "total_phases": $total_phases,
      "successful": $successful_phases,
      "failed": $failed_phases,
      "skipped": $skipped_phases,
      "success_rate": $(echo "scale=2; $successful_phases * 100 / $total_phases" | bc 2>/dev/null || echo "0")
    },
    "orchestration_results": [
EOF
    
    # Add orchestration results
    first_result=true
    for result in "${ORCHESTRATION_RESULTS[@]}"; do
        if [ "$first_result" = false ]; then
            echo "," >> "$report_file"
        fi
        first_result=false
        
        status=$(echo "$result" | cut -d'|' -f1)
        phase=$(echo "$result" | cut -d'|' -f2)
        details=$(echo "$result" | cut -d'|' -f3)
        duration=$(echo "$result" | cut -d'|' -f4)
        
        cat >> "$report_file" << EOF
      {
        "phase": "$phase",
        "status": "$status",
        "details": "$details",
        "duration_seconds": $duration
      }
EOF
    done
    
    # Add deployment artifacts if available
    if [ ${#DEPLOYMENT_ARTIFACTS[@]} -gt 0 ]; then
        echo "," >> "$report_file"
        echo '    ],' >> "$report_file"
        echo '    "deployment_artifacts": [' >> "$report_file"
        
        first_artifact=true
        for artifact in "${DEPLOYMENT_ARTIFACTS[@]}"; do
            if [ "$first_artifact" = false ]; then
                echo "," >> "$report_file"
            fi
            first_artifact=false
            
            artifact_type=$(echo "$artifact" | cut -d'|' -f1)
            artifact_path=$(echo "$artifact" | cut -d'|' -f2)
            artifact_size=$(echo "$artifact" | cut -d'|' -f3)
            
            cat >> "$report_file" << EOF
      {
        "type": "$artifact_type",
        "path": "$artifact_path",
        "size": "$artifact_size"
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
    
    add_orchestration_result "SUCCESS" "Report Generation" "Generated: $report_file" "0"
}

# Print orchestration summary
print_orchestration_summary() {
    log_section "Deployment Orchestration Summary"
    
    # Count results
    total_phases=0
    successful_phases=0
    failed_phases=0
    skipped_phases=0
    
    for result in "${ORCHESTRATION_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_phases=$((total_phases + 1))
        
        case "$status" in
            "SUCCESS") successful_phases=$((successful_phases + 1)) ;;
            "FAILED") failed_phases=$((failed_phases + 1)) ;;
            "SKIPPED") skipped_phases=$((skipped_phases + 1)) ;;
        esac
    done
    
    echo "📊 Orchestration Results:"
    echo "   Total Phases: $total_phases"
    echo "   ✅ Successful: $successful_phases"
    echo "   ❌ Failed: $failed_phases"
    echo "   ⏭️  Skipped: $skipped_phases"
    
    if [ "$total_phases" -gt 0 ]; then
        success_rate=$(echo "scale=1; $successful_phases * 100 / $total_phases" | bc 2>/dev/null || echo "0")
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    echo "🏗️  Deployment Configuration:"
    echo "   Action: $DEPLOYMENT_ACTION"
    echo "   Environment: $ENVIRONMENT"
    echo "   Region: $AWS_REGION"
    echo "   Validation Mode: $VALIDATION_MODE"
    
    # Show deployment artifacts
    if [ ${#DEPLOYMENT_ARTIFACTS[@]} -gt 0 ]; then
        echo ""
        echo "📦 Deployment Artifacts:"
        for artifact in "${DEPLOYMENT_ARTIFACTS[@]}"; do
            artifact_type=$(echo "$artifact" | cut -d'|' -f1)
            artifact_size=$(echo "$artifact" | cut -d'|' -f3)
            echo "   • $artifact_type: $artifact_size"
        done
    fi
    
    # Show failures
    if [ "$failed_phases" -gt 0 ]; then
        echo ""
        echo "❌ Failed Phases:"
        for result in "${ORCHESTRATION_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "FAILED" ]; then
                phase=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $phase: $details"
            fi
        done
    fi
    
    echo ""
    
    # Overall result
    if [ "$failed_phases" -eq 0 ]; then
        echo "🎉 Deployment orchestration completed successfully!"
        echo ""
        echo "✅ Next Steps:"
        if [ "$DEPLOYMENT_ACTION" = "build-layers" ]; then
            echo "   • Trigger infrastructure deployment via GitHub Actions"
            echo "   • Run validation: DEPLOYMENT_ACTION=validate-only ./scripts/deployment-orchestrator.sh"
        elif [ "$DEPLOYMENT_ACTION" = "build-and-validate" ]; then
            echo "   • Review validation results in e2e-validation-report.json"
            echo "   • Trigger infrastructure deployment via GitHub Actions"
        else
            echo "   • Monitor CloudWatch dashboards for performance"
            echo "   • Test webhook integration with repository changes"
        fi
        return 0
    else
        echo "💥 Deployment orchestration failed!"
        echo "   Address failed phases before proceeding."
        return 1
    fi
}

# Main execution flow
main() {
    case "$DEPLOYMENT_ACTION" in
        "build-layers")
            build_layers
            ;;
        "build-and-validate")
            build_layers
            run_validation
            ;;
        "full-deploy")
            build_layers
            deploy_infrastructure
            run_validation
            ;;
        "validate-only")
            run_validation
            ;;
        *)
            log_error "Unknown deployment action: $DEPLOYMENT_ACTION"
            log_error "Valid actions: build-layers, build-and-validate, full-deploy, validate-only"
            exit 1
            ;;
    esac
    
    generate_orchestration_report
    
    if print_orchestration_summary; then
        log_section_complete "Deployment Orchestration"
        exit 0
    else
        log_section_complete "Deployment Orchestration (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
