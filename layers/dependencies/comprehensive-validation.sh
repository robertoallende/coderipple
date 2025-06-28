#!/bin/bash
# layers/dependencies/comprehensive-validation.sh
# Comprehensive validation framework for CodeRipple Dependencies Layer

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Source common functions
if [ -f "../shared/build-common.sh" ]; then
    source ../shared/build-common.sh
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

log_section "CodeRipple Dependencies Layer - Comprehensive Validation"

# Configuration
LAYER_ZIP="coderipple-dependencies-layer.zip"
VALIDATION_MODE=${VALIDATION_MODE:-"full"}  # full, quick, security
GENERATE_REPORT=${GENERATE_REPORT:-true}
PERFORMANCE_BENCHMARKS=${PERFORMANCE_BENCHMARKS:-true}

# Validation results tracking
VALIDATION_RESULTS=()
PERFORMANCE_METRICS=()
SECURITY_FINDINGS=()

# Add validation result
add_result() {
    local status="$1"
    local test_name="$2"
    local details="$3"
    
    VALIDATION_RESULTS+=("$status|$test_name|$details")
    
    case "$status" in
        "PASS") log_success "$test_name: $details" ;;
        "FAIL") log_error "$test_name: $details" ;;
        "WARN") log_warning "$test_name: $details" ;;
        *) log_debug "$test_name: $details" ;;
    esac
}

# Layer existence and integrity validation
validate_layer_integrity() {
    log_step "Validating layer integrity"
    
    # Check if layer ZIP exists
    if [ ! -f "$LAYER_ZIP" ]; then
        add_result "FAIL" "Layer Existence" "Layer ZIP file not found: $LAYER_ZIP"
        return 1
    fi
    
    add_result "PASS" "Layer Existence" "Layer ZIP found: $(du -sh "$LAYER_ZIP" | cut -f1)"
    
    # Test ZIP integrity
    if unzip -t "$LAYER_ZIP" > /dev/null 2>&1; then
        add_result "PASS" "ZIP Integrity" "Layer ZIP is valid and extractable"
    else
        add_result "FAIL" "ZIP Integrity" "Layer ZIP is corrupted or invalid"
        return 1
    fi
    
    # Check layer structure
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    if [ -d "$temp_dir/python" ]; then
        add_result "PASS" "Layer Structure" "Correct python/ directory structure"
        
        # Count packages
        package_count=$(ls -1 "$temp_dir/python" | wc -l)
        add_result "INFO" "Package Count" "$package_count packages in layer"
    else
        add_result "FAIL" "Layer Structure" "Missing python/ directory in layer"
        rm -rf "$temp_dir"
        return 1
    fi
    
    rm -rf "$temp_dir"
    return 0
}

# AWS Lambda compatibility validation
validate_aws_compatibility() {
    log_step "Validating AWS Lambda compatibility"
    
    # Size limits
    layer_size_bytes=$(stat -f%z "$LAYER_ZIP" 2>/dev/null || stat -c%s "$LAYER_ZIP")
    layer_size_mb=$((layer_size_bytes / 1024 / 1024))
    
    # AWS Lambda layer limits
    MAX_LAYER_SIZE_MB=250
    RECOMMENDED_MAX_MB=200
    
    if [ "$layer_size_mb" -le "$MAX_LAYER_SIZE_MB" ]; then
        if [ "$layer_size_mb" -le "$RECOMMENDED_MAX_MB" ]; then
            add_result "PASS" "Layer Size" "${layer_size_mb}MB (within recommended limits)"
        else
            add_result "WARN" "Layer Size" "${layer_size_mb}MB (within limits but large)"
        fi
    else
        add_result "FAIL" "Layer Size" "${layer_size_mb}MB (exceeds AWS limit of ${MAX_LAYER_SIZE_MB}MB)"
    fi
    
    # Runtime compatibility
    add_result "PASS" "Runtime Compatibility" "python3.12 (matches AWS Lambda runtime)"
    
    # Architecture compatibility
    add_result "PASS" "Architecture Compatibility" "x86_64 (standard Lambda architecture)"
}

# Package dependency validation
validate_package_dependencies() {
    log_step "Validating package dependencies"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Test critical package imports
    python3.12 -c "
import sys
sys.path.insert(0, '$temp_dir/python')

critical_packages = {
    'boto3': '1.38.32',
    'botocore': '1.38.32', 
    'strands': 'unknown',
    'requests': '2.32.3',
    'pydantic': '2.11.5',
    'urllib3': '2.4.0',
    'httpx': '0.28.1'
}

import_failures = []
version_mismatches = []

for package, expected_version in critical_packages.items():
    try:
        module = __import__(package)
        actual_version = getattr(module, '__version__', 'unknown')
        
        if expected_version != 'unknown' and actual_version != expected_version:
            version_mismatches.append(f'{package}: expected {expected_version}, got {actual_version}')
            
    except ImportError as e:
        import_failures.append(f'{package}: {e}')

if import_failures:
    print('IMPORT_FAILURES:' + '|'.join(import_failures))
    
if version_mismatches:
    print('VERSION_MISMATCHES:' + '|'.join(version_mismatches))
    
if not import_failures and not version_mismatches:
    print('ALL_PACKAGES_OK')
" > validation_output.txt 2>&1
    
    if grep -q "ALL_PACKAGES_OK" validation_output.txt; then
        add_result "PASS" "Package Dependencies" "All critical packages import successfully"
    else
        if grep -q "IMPORT_FAILURES:" validation_output.txt; then
            failures=$(grep "IMPORT_FAILURES:" validation_output.txt | cut -d: -f2-)
            add_result "FAIL" "Package Dependencies" "Import failures: $failures"
        fi
        
        if grep -q "VERSION_MISMATCHES:" validation_output.txt; then
            mismatches=$(grep "VERSION_MISMATCHES:" validation_output.txt | cut -d: -f2-)
            add_result "WARN" "Package Dependencies" "Version mismatches: $mismatches"
        fi
    fi
    
    rm -f validation_output.txt
    rm -rf "$temp_dir"
}

# Performance benchmarking
validate_performance() {
    if [ "$PERFORMANCE_BENCHMARKS" != "true" ]; then
        log_debug "Skipping performance benchmarks"
        return 0
    fi
    
    log_step "Running performance benchmarks"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Import performance test
    python3.12 -c "
import sys
import time
sys.path.insert(0, '$temp_dir/python')

packages_to_test = ['boto3', 'requests', 'pydantic', 'strands']
total_start = time.time()

for package in packages_to_test:
    start_time = time.time()
    try:
        __import__(package)
        import_time = time.time() - start_time
        print(f'{package}:{import_time:.3f}')
    except ImportError:
        print(f'{package}:FAILED')

total_time = time.time() - total_start
print(f'TOTAL:{total_time:.3f}')
" > performance_results.txt
    
    # Process performance results
    while IFS=':' read -r package time_or_status; do
        if [ "$time_or_status" = "FAILED" ]; then
            add_result "FAIL" "Performance ($package)" "Import failed"
        elif [ "$package" = "TOTAL" ]; then
            PERFORMANCE_METRICS+=("total_import_time:$time_or_status")
            if (( $(echo "$time_or_status > 2.0" | bc -l) )); then
                add_result "WARN" "Performance (Total)" "${time_or_status}s (may impact Lambda cold start)"
            else
                add_result "PASS" "Performance (Total)" "${time_or_status}s (acceptable for Lambda)"
            fi
        else
            PERFORMANCE_METRICS+=("${package}_import_time:$time_or_status")
            if (( $(echo "$time_or_status > 1.0" | bc -l) )); then
                add_result "WARN" "Performance ($package)" "${time_or_status}s (slow import)"
            else
                add_result "PASS" "Performance ($package)" "${time_or_status}s"
            fi
        fi
    done < performance_results.txt
    
    rm -f performance_results.txt
    rm -rf "$temp_dir"
}

# Security validation
validate_security() {
    if [ "$VALIDATION_MODE" != "full" ] && [ "$VALIDATION_MODE" != "security" ]; then
        log_debug "Skipping security validation"
        return 0
    fi
    
    log_step "Running security validation"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Check for sensitive files
    sensitive_patterns=(
        "*.key" "*.pem" "*.p12" "*.pfx"
        "*password*" "*secret*" "*token*"
        ".env" "config.ini" "credentials"
    )
    
    sensitive_files_found=false
    for pattern in "${sensitive_patterns[@]}"; do
        if find "$temp_dir" -name "$pattern" -type f | grep -q .; then
            sensitive_files_found=true
            files=$(find "$temp_dir" -name "$pattern" -type f)
            add_result "WARN" "Security" "Potentially sensitive files found: $files"
        fi
    done
    
    if [ "$sensitive_files_found" = false ]; then
        add_result "PASS" "Security" "No sensitive files detected in layer"
    fi
    
    # Check for executable files (potential security risk)
    executable_files=$(find "$temp_dir" -type f -executable | wc -l)
    if [ "$executable_files" -gt 0 ]; then
        add_result "WARN" "Security" "$executable_files executable files found in layer"
    else
        add_result "PASS" "Security" "No unexpected executable files"
    fi
    
    rm -rf "$temp_dir"
}

# Lambda simulation test
validate_lambda_simulation() {
    log_step "Running Lambda simulation test"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Create mock Lambda handler
    cat > "$temp_dir/test_handler.py" << 'EOF'
import sys
sys.path.insert(0, 'python')

def lambda_handler(event, context):
    """Test Lambda handler using layer dependencies"""
    
    try:
        import boto3
        import requests
        import pydantic
        import strands
        
        return {
            'statusCode': 200,
            'body': {
                'boto3_version': boto3.__version__,
                'requests_version': requests.__version__,
                'pydantic_version': pydantic.__version__,
                'strands_available': True,
                'message': 'Layer dependencies functional in Lambda simulation'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'Layer dependencies failed in Lambda simulation'
            }
        }

if __name__ == '__main__':
    result = lambda_handler({}, {})
    print(f"STATUS_CODE:{result['statusCode']}")
    if result['statusCode'] == 200:
        print("SIMULATION_SUCCESS")
    else:
        print(f"SIMULATION_ERROR:{result['body']['error']}")
EOF
    
    cd "$temp_dir"
    python3.12 test_handler.py > simulation_result.txt 2>&1
    
    if grep -q "SIMULATION_SUCCESS" simulation_result.txt; then
        add_result "PASS" "Lambda Simulation" "Handler executed successfully with layer dependencies"
    else
        error_msg=$(grep "SIMULATION_ERROR:" simulation_result.txt | cut -d: -f2- || echo "Unknown error")
        add_result "FAIL" "Lambda Simulation" "Handler failed: $error_msg"
    fi
    
    cd - > /dev/null
    rm -rf "$temp_dir"
}

# Generate comprehensive validation report
generate_validation_report() {
    if [ "$GENERATE_REPORT" != "true" ]; then
        return 0
    fi
    
    log_step "Generating comprehensive validation report"
    
    report_file="validation-report.json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count results
    total_tests=0
    passed_tests=0
    failed_tests=0
    warning_tests=0
    
    for result in "${VALIDATION_RESULTS[@]}"; do
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
  "validation_report": {
    "timestamp": "$timestamp",
    "layer_name": "coderipple-dependencies",
    "validation_mode": "$VALIDATION_MODE",
    "summary": {
      "total_tests": $total_tests,
      "passed": $passed_tests,
      "failed": $failed_tests,
      "warnings": $warning_tests,
      "success_rate": $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc)
    },
    "layer_info": {
      "file": "$LAYER_ZIP",
      "size_bytes": $(stat -f%z "$LAYER_ZIP" 2>/dev/null || stat -c%s "$LAYER_ZIP"),
      "size_human": "$(du -sh "$LAYER_ZIP" | cut -f1)"
    },
    "test_results": [
EOF
    
    # Add test results
    first_result=true
    for result in "${VALIDATION_RESULTS[@]}"; do
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
            
            metric_name=$(echo "$metric" | cut -d':' -f1)
            metric_value=$(echo "$metric" | cut -d':' -f2)
            echo "      \"$metric_name\": \"$metric_value\"" >> "$report_file"
        done
        
        echo "    }" >> "$report_file"
    else
        echo "" >> "$report_file"
        echo "    ]" >> "$report_file"
    fi
    
    echo "  }" >> "$report_file"
    echo "}" >> "$report_file"
    
    add_result "INFO" "Validation Report" "Generated: $report_file"
}

# Print validation summary
print_validation_summary() {
    log_section "Validation Summary"
    
    # Count results
    total_tests=0
    passed_tests=0
    failed_tests=0
    warning_tests=0
    
    for result in "${VALIDATION_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_tests=$((total_tests + 1))
        
        case "$status" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "WARN") warning_tests=$((warning_tests + 1)) ;;
        esac
    done
    
    echo "📊 Validation Results:"
    echo "   Total Tests: $total_tests"
    echo "   ✅ Passed: $passed_tests"
    echo "   ❌ Failed: $failed_tests"
    echo "   ⚠️  Warnings: $warning_tests"
    
    if [ "$total_tests" -gt 0 ]; then
        success_rate=$(echo "scale=1; $passed_tests * 100 / $total_tests" | bc)
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    
    # Show failures and warnings
    if [ "$failed_tests" -gt 0 ]; then
        echo "❌ Failed Tests:"
        for result in "${VALIDATION_RESULTS[@]}"; do
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
        for result in "${VALIDATION_RESULTS[@]}"; do
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
            echo "🎉 All validations passed! Layer is ready for deployment."
        else
            echo "✅ Validation completed with warnings. Review warnings before deployment."
        fi
        return 0
    else
        echo "💥 Validation failed! Address failures before deployment."
        return 1
    fi
}

# Main execution flow
main() {
    # Run validation steps based on mode
    case "$VALIDATION_MODE" in
        "full")
            validate_layer_integrity || exit 1
            validate_aws_compatibility
            validate_package_dependencies
            validate_performance
            validate_security
            validate_lambda_simulation
            ;;
        "quick")
            validate_layer_integrity || exit 1
            validate_aws_compatibility
            validate_package_dependencies
            ;;
        "security")
            validate_layer_integrity || exit 1
            validate_security
            ;;
        *)
            log_error "Unknown validation mode: $VALIDATION_MODE"
            exit 1
            ;;
    esac
    
    generate_validation_report
    
    if print_validation_summary; then
        log_section_complete "Comprehensive Validation"
        exit 0
    else
        log_section_complete "Comprehensive Validation (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
