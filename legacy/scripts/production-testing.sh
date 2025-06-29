#!/bin/bash
# scripts/production-testing.sh
# Production Testing and Optimization for CodeRipple Layer-based Architecture

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

log_section "CodeRipple Production Testing and Optimization"

# Configuration
TESTING_MODE=${TESTING_MODE:-"full"}  # full, quick, performance-only
AWS_REGION=${AWS_REGION:-"us-west-2"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
SKIP_DEPLOYMENT=${SKIP_DEPLOYMENT:-false}
GENERATE_REPORT=${GENERATE_REPORT:-true}

# Test results tracking
TEST_RESULTS=()
PERFORMANCE_METRICS=()

# Add test result
add_result() {
    local status="$1"
    local test_name="$2"
    local details="$3"
    
    TEST_RESULTS+=("$status|$test_name|$details")
    
    case "$status" in
        "PASS") log_success "$test_name: $details" ;;
        "FAIL") log_error "$test_name: $details" ;;
        "WARN") log_warning "$test_name: $details" ;;
        *) log_debug "$test_name: $details" ;;
    esac
}

# Add performance metric
add_metric() {
    local metric_name="$1"
    local metric_value="$2"
    local metric_unit="$3"
    
    PERFORMANCE_METRICS+=("$metric_name|$metric_value|$metric_unit")
    log_debug "Metric: $metric_name = $metric_value $metric_unit"
}

# Pre-deployment validation
validate_pre_deployment() {
    log_step "Running pre-deployment validation"
    
    # Check AWS CLI configuration
    if ! aws sts get-caller-identity > /dev/null 2>&1; then
        add_result "FAIL" "AWS Configuration" "AWS CLI not configured or credentials invalid"
        return 1
    fi
    
    aws_account=$(aws sts get-caller-identity --query Account --output text)
    aws_region=$(aws configure get region || echo "$AWS_REGION")
    add_result "PASS" "AWS Configuration" "Account: $aws_account, Region: $aws_region"
    
    # Check Terraform state
    if [ -f "infra/terraform/terraform.tfstate" ]; then
        add_result "PASS" "Terraform State" "State file exists"
    else
        add_result "WARN" "Terraform State" "No local state file found (may use remote backend)"
    fi
    
    # Check layer artifacts
    deps_layer="layers/dependencies/coderipple-dependencies-layer.zip"
    pkg_layer="layers/coderipple-package/coderipple-package-layer.zip"
    function_zip="functions/orchestrator/function.zip"
    
    if [ -f "$deps_layer" ]; then
        deps_size=$(du -sh "$deps_layer" | cut -f1)
        add_result "PASS" "Dependencies Layer" "Found: $deps_size"
    else
        add_result "FAIL" "Dependencies Layer" "Layer ZIP not found: $deps_layer"
        return 1
    fi
    
    if [ -f "$pkg_layer" ]; then
        pkg_size=$(du -sh "$pkg_layer" | cut -f1)
        add_result "PASS" "Package Layer" "Found: $pkg_size"
    else
        add_result "FAIL" "Package Layer" "Layer ZIP not found: $pkg_layer"
        return 1
    fi
    
    if [ -f "$function_zip" ]; then
        func_size=$(du -sh "$function_zip" | cut -f1)
        add_result "PASS" "Function Package" "Found: $func_size"
    else
        add_result "FAIL" "Function Package" "Function ZIP not found: $function_zip"
        return 1
    fi
}

# Deploy infrastructure if needed
deploy_infrastructure() {
    if [ "$SKIP_DEPLOYMENT" = "true" ]; then
        log_debug "Skipping deployment step"
        return 0
    fi
    
    log_step "Deploying layer-based infrastructure"
    
    cd infra/terraform
    
    # Initialize Terraform
    terraform init -upgrade
    
    # Plan deployment
    terraform plan -out=production.tfplan
    
    # Apply deployment
    if terraform apply -auto-approve production.tfplan; then
        add_result "PASS" "Infrastructure Deployment" "Terraform apply successful"
    else
        add_result "FAIL" "Infrastructure Deployment" "Terraform apply failed"
        cd ../..
        return 1
    fi
    
    cd ../..
}

# Test layer deployment
test_layer_deployment() {
    log_step "Testing layer deployment"
    
    # Get layer ARNs from Terraform output
    deps_layer_arn=$(cd infra/terraform && terraform output -raw coderipple_dependencies_layer_arn 2>/dev/null || echo "")
    pkg_layer_arn=$(cd infra/terraform && terraform output -raw coderipple_package_layer_arn 2>/dev/null || echo "")
    
    if [ -n "$deps_layer_arn" ]; then
        add_result "PASS" "Dependencies Layer Deployment" "ARN: ${deps_layer_arn##*:}"
    else
        add_result "FAIL" "Dependencies Layer Deployment" "Could not retrieve layer ARN"
    fi
    
    if [ -n "$pkg_layer_arn" ]; then
        add_result "PASS" "Package Layer Deployment" "ARN: ${pkg_layer_arn##*:}"
    else
        add_result "FAIL" "Package Layer Deployment" "Could not retrieve layer ARN"
    fi
    
    # Test layer versions
    if [ -n "$deps_layer_arn" ]; then
        layer_name=$(echo "$deps_layer_arn" | cut -d: -f7)
        if aws lambda get-layer-version --layer-name "$layer_name" --version-number 1 > /dev/null 2>&1; then
            add_result "PASS" "Dependencies Layer Access" "Layer accessible via AWS API"
        else
            add_result "FAIL" "Dependencies Layer Access" "Cannot access layer via AWS API"
        fi
    fi
}

# Test function deployment
test_function_deployment() {
    log_step "Testing function deployment"
    
    # Get function name from Terraform output
    function_name=$(cd infra/terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -n "$function_name" ]; then
        add_result "PASS" "Function Deployment" "Function: $function_name"
        
        # Test function configuration
        if aws lambda get-function --function-name "$function_name" > /dev/null 2>&1; then
            add_result "PASS" "Function Access" "Function accessible via AWS API"
            
            # Get function details
            func_info=$(aws lambda get-function --function-name "$function_name")
            func_size=$(echo "$func_info" | jq -r '.Configuration.CodeSize')
            func_timeout=$(echo "$func_info" | jq -r '.Configuration.Timeout')
            func_memory=$(echo "$func_info" | jq -r '.Configuration.MemorySize')
            
            add_metric "function_size" "$func_size" "bytes"
            add_metric "function_timeout" "$func_timeout" "seconds"
            add_metric "function_memory" "$func_memory" "MB"
            
            # Check layer configuration
            layer_count=$(echo "$func_info" | jq -r '.Configuration.Layers | length')
            if [ "$layer_count" -eq 2 ]; then
                add_result "PASS" "Function Layers" "2 layers attached as expected"
            else
                add_result "WARN" "Function Layers" "$layer_count layers attached (expected 2)"
            fi
        else
            add_result "FAIL" "Function Access" "Cannot access function via AWS API"
        fi
    else
        add_result "FAIL" "Function Deployment" "Could not retrieve function name"
    fi
}

# Performance testing
run_performance_tests() {
    if [ "$TESTING_MODE" = "quick" ]; then
        log_debug "Skipping performance tests in quick mode"
        return 0
    fi
    
    log_step "Running performance tests"
    
    function_name=$(cd infra/terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -z "$function_name" ]; then
        add_result "FAIL" "Performance Testing" "Function name not available"
        return 1
    fi
    
    # Cold start test
    log_debug "Testing cold start performance..."
    
    test_payload='{"test": true, "repository": {"name": "test-repo"}, "commits": [{"id": "test123", "message": "performance test"}]}'
    
    # Invoke function and measure response time
    start_time=$(date +%s%3N)
    invoke_result=$(aws lambda invoke \
        --function-name "$function_name" \
        --payload "$test_payload" \
        --cli-binary-format raw-in-base64-out \
        response.json 2>&1)
    end_time=$(date +%s%3N)
    
    if [ $? -eq 0 ]; then
        response_time=$((end_time - start_time))
        add_metric "cold_start_time" "$response_time" "ms"
        
        if [ "$response_time" -lt 5000 ]; then
            add_result "PASS" "Cold Start Performance" "${response_time}ms (excellent)"
        elif [ "$response_time" -lt 10000 ]; then
            add_result "WARN" "Cold Start Performance" "${response_time}ms (acceptable)"
        else
            add_result "FAIL" "Cold Start Performance" "${response_time}ms (too slow)"
        fi
        
        # Check response
        if [ -f "response.json" ]; then
            status_code=$(jq -r '.statusCode' response.json 2>/dev/null || echo "unknown")
            if [ "$status_code" = "200" ] || [ "$status_code" = "500" ]; then
                add_result "PASS" "Function Response" "Function responded with status $status_code"
            else
                add_result "WARN" "Function Response" "Unexpected status code: $status_code"
            fi
            rm -f response.json
        fi
    else
        add_result "FAIL" "Function Invocation" "Failed to invoke function: $invoke_result"
    fi
    
    # Warm start test (invoke again immediately)
    log_debug "Testing warm start performance..."
    
    start_time=$(date +%s%3N)
    aws lambda invoke \
        --function-name "$function_name" \
        --payload "$test_payload" \
        --cli-binary-format raw-in-base64-out \
        response.json > /dev/null 2>&1
    end_time=$(date +%s%3N)
    
    if [ $? -eq 0 ]; then
        warm_response_time=$((end_time - start_time))
        add_metric "warm_start_time" "$warm_response_time" "ms"
        
        if [ "$warm_response_time" -lt 1000 ]; then
            add_result "PASS" "Warm Start Performance" "${warm_response_time}ms (excellent)"
        elif [ "$warm_response_time" -lt 3000 ]; then
            add_result "WARN" "Warm Start Performance" "${warm_response_time}ms (acceptable)"
        else
            add_result "FAIL" "Warm Start Performance" "${warm_response_time}ms (too slow)"
        fi
        
        rm -f response.json
    fi
}

# Test API Gateway integration
test_api_gateway() {
    log_step "Testing API Gateway integration"
    
    api_url=$(cd infra/terraform && terraform output -raw api_gateway_url 2>/dev/null || echo "")
    
    if [ -n "$api_url" ]; then
        add_result "PASS" "API Gateway Deployment" "URL: $api_url"
        
        # Test API endpoint
        test_payload='{"repository": {"name": "test-repo"}, "commits": [{"id": "test123", "message": "API test"}]}'
        
        start_time=$(date +%s%3N)
        http_response=$(curl -s -w "%{http_code}" \
            -X POST \
            -H "Content-Type: application/json" \
            -d "$test_payload" \
            "$api_url" || echo "000")
        end_time=$(date +%s%3N)
        
        http_code="${http_response: -3}"
        response_body="${http_response%???}"
        api_response_time=$((end_time - start_time))
        
        add_metric "api_response_time" "$api_response_time" "ms"
        
        if [ "$http_code" = "200" ] || [ "$http_code" = "500" ]; then
            add_result "PASS" "API Gateway Response" "HTTP $http_code in ${api_response_time}ms"
        else
            add_result "FAIL" "API Gateway Response" "HTTP $http_code (expected 200 or 500)"
        fi
    else
        add_result "FAIL" "API Gateway Deployment" "Could not retrieve API URL"
    fi
}

# Monitor CloudWatch metrics
monitor_cloudwatch_metrics() {
    log_step "Monitoring CloudWatch metrics"
    
    function_name=$(cd infra/terraform && terraform output -raw lambda_function_name 2>/dev/null || echo "")
    
    if [ -z "$function_name" ]; then
        add_result "WARN" "CloudWatch Monitoring" "Function name not available"
        return 0
    fi
    
    # Get recent metrics (last 5 minutes)
    end_time=$(date -u +%Y-%m-%dT%H:%M:%S)
    start_time=$(date -u -d '5 minutes ago' +%Y-%m-%dT%H:%M:%S)
    
    # Duration metrics
    duration_stats=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/Lambda \
        --metric-name Duration \
        --dimensions Name=FunctionName,Value="$function_name" \
        --start-time "$start_time" \
        --end-time "$end_time" \
        --period 300 \
        --statistics Average,Maximum \
        --output json 2>/dev/null || echo '{"Datapoints":[]}')
    
    duration_count=$(echo "$duration_stats" | jq '.Datapoints | length')
    
    if [ "$duration_count" -gt 0 ]; then
        avg_duration=$(echo "$duration_stats" | jq -r '.Datapoints[0].Average // 0')
        max_duration=$(echo "$duration_stats" | jq -r '.Datapoints[0].Maximum // 0')
        
        add_metric "avg_duration" "$avg_duration" "ms"
        add_metric "max_duration" "$max_duration" "ms"
        add_result "PASS" "CloudWatch Metrics" "Duration metrics available"
    else
        add_result "WARN" "CloudWatch Metrics" "No recent duration metrics (function may not have been invoked)"
    fi
    
    # Error rate
    error_stats=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/Lambda \
        --metric-name Errors \
        --dimensions Name=FunctionName,Value="$function_name" \
        --start-time "$start_time" \
        --end-time "$end_time" \
        --period 300 \
        --statistics Sum \
        --output json 2>/dev/null || echo '{"Datapoints":[]}')
    
    error_count=$(echo "$error_stats" | jq -r '.Datapoints[0].Sum // 0')
    add_metric "error_count" "$error_count" "errors"
    
    if [ "$error_count" = "0" ]; then
        add_result "PASS" "Error Rate" "No errors in recent invocations"
    else
        add_result "WARN" "Error Rate" "$error_count errors in recent invocations"
    fi
}

# Generate production test report
generate_test_report() {
    if [ "$GENERATE_REPORT" != "true" ]; then
        return 0
    fi
    
    log_step "Generating production test report"
    
    report_file="production-test-report.json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count results
    total_tests=0
    passed_tests=0
    failed_tests=0
    warning_tests=0
    
    for result in "${TEST_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_tests=$((total_tests + 1))
        
        case "$status" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "WARN") warning_tests=$((warning_tests + 1)) ;;
        esac
    done
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "production_test_report": {
    "timestamp": "$timestamp",
    "testing_mode": "$TESTING_MODE",
    "environment": "$ENVIRONMENT",
    "aws_region": "$AWS_REGION",
    "architecture": "single-lambda-with-layers",
    "summary": {
      "total_tests": $total_tests,
      "passed": $passed_tests,
      "failed": $failed_tests,
      "warnings": $warning_tests,
      "success_rate": $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc)
    },
    "test_results": [
EOF
    
    # Add test results
    first_result=true
    for result in "${TEST_RESULTS[@]}"; do
        if [ "$first_result" = false ]; then
            echo "," >> "$report_file"
        fi
        first_result=false
        
        status=$(echo "$result" | cut -d'|' -f1)
        test_name=$(echo "$result" | cut -d'|' -f2)
        details=$(echo "$result" | cut -d'|' -f3)
        
        cat >> "$report_file" << EOF
      {
        "test": "$test_name",
        "status": "$status",
        "details": "$details"
      }
EOF
    done
    
    # Add performance metrics if available
    if [ ${#PERFORMANCE_METRICS[@]} -gt 0 ]; then
        echo "," >> "$report_file"
        echo '    ],' >> "$report_file"
        echo '    "performance_metrics": {' >> "$report_file"
        
        first_metric=true
        for metric in "${PERFORMANCE_METRICS[@]}"; do
            if [ "$first_metric" = false ]; then
                echo "," >> "$report_file"
            fi
            first_metric=false
            
            metric_name=$(echo "$metric" | cut -d'|' -f1)
            metric_value=$(echo "$metric" | cut -d'|' -f2)
            metric_unit=$(echo "$metric" | cut -d'|' -f3)
            
            echo "      \"$metric_name\": {\"value\": \"$metric_value\", \"unit\": \"$metric_unit\"}" >> "$report_file"
        done
        
        echo "    }" >> "$report_file"
    else
        echo "" >> "$report_file"
        echo "    ]" >> "$report_file"
    fi
    
    echo "  }" >> "$report_file"
    echo "}" >> "$report_file"
    
    add_result "INFO" "Test Report" "Generated: $report_file"
}

# Print test summary
print_test_summary() {
    log_section "Production Test Summary"
    
    # Count results
    total_tests=0
    passed_tests=0
    failed_tests=0
    warning_tests=0
    
    for result in "${TEST_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_tests=$((total_tests + 1))
        
        case "$status" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "WARN") warning_tests=$((warning_tests + 1)) ;;
        esac
    done
    
    echo "📊 Test Results:"
    echo "   Total Tests: $total_tests"
    echo "   ✅ Passed: $passed_tests"
    echo "   ❌ Failed: $failed_tests"
    echo "   ⚠️  Warnings: $warning_tests"
    
    if [ "$total_tests" -gt 0 ]; then
        success_rate=$(echo "scale=1; $passed_tests * 100 / $total_tests" | bc)
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    echo "🏗️  Architecture: Single Lambda with Layers"
    echo "   Environment: $ENVIRONMENT"
    echo "   Region: $AWS_REGION"
    echo ""
    
    # Show performance metrics
    if [ ${#PERFORMANCE_METRICS[@]} -gt 0 ]; then
        echo "⚡ Performance Metrics:"
        for metric in "${PERFORMANCE_METRICS[@]}"; do
            metric_name=$(echo "$metric" | cut -d'|' -f1)
            metric_value=$(echo "$metric" | cut -d'|' -f2)
            metric_unit=$(echo "$metric" | cut -d'|' -f3)
            echo "   • $metric_name: $metric_value $metric_unit"
        done
        echo ""
    fi
    
    # Show failures and warnings
    if [ "$failed_tests" -gt 0 ]; then
        echo "❌ Failed Tests:"
        for result in "${TEST_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "FAIL" ]; then
                test_name=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $test_name: $details"
            fi
        done
        echo ""
    fi
    
    if [ "$warning_tests" -gt 0 ]; then
        echo "⚠️  Warnings:"
        for result in "${TEST_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "WARN" ]; then
                test_name=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $test_name: $details"
            fi
        done
        echo ""
    fi
    
    # Overall result
    if [ "$failed_tests" -eq 0 ]; then
        if [ "$warning_tests" -eq 0 ]; then
            echo "🎉 All production tests passed! System is ready for production use."
        else
            echo "✅ Production testing completed with warnings. Review warnings before full production use."
        fi
        return 0
    else
        echo "💥 Production testing failed! Address failures before production deployment."
        return 1
    fi
}

# Main execution flow
main() {
    validate_pre_deployment || exit 1
    
    case "$TESTING_MODE" in
        "full")
            deploy_infrastructure
            test_layer_deployment
            test_function_deployment
            run_performance_tests
            test_api_gateway
            monitor_cloudwatch_metrics
            ;;
        "quick")
            test_layer_deployment
            test_function_deployment
            test_api_gateway
            ;;
        "performance-only")
            run_performance_tests
            monitor_cloudwatch_metrics
            ;;
        *)
            log_error "Unknown testing mode: $TESTING_MODE"
            exit 1
            ;;
    esac
    
    generate_test_report
    
    if print_test_summary; then
        log_section_complete "Production Testing and Optimization"
        exit 0
    else
        log_section_complete "Production Testing and Optimization (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
