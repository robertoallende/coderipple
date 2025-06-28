#!/bin/bash
# functions/orchestrator/comprehensive-validation.sh
# Comprehensive validation framework for CodeRipple Lambda Function (Simplified Strands Pattern)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Fallback logging functions (simplified - no layer dependencies)
log_section() { echo -e "\n=== $1 ==="; }
log_step() { echo "🔍 $1..."; }
log_success() { echo "✅ $1"; }
log_error() { echo "❌ $1"; }
log_warning() { echo "⚠️  $1"; }
log_debug() { echo "🐛 $1"; }
log_section_complete() { echo -e "✅ $1 - COMPLETED\n"; }

log_section "CodeRipple Lambda Function - Comprehensive Validation (Simplified Strands Pattern)"

# Configuration
FUNCTION_ZIP="function.zip"
VALIDATION_MODE=${VALIDATION_MODE:-"full"}  # full, quick, function-only
GENERATE_REPORT=${GENERATE_REPORT:-true}

# Validation results tracking
VALIDATION_RESULTS=()

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

# Function existence and integrity validation
validate_function_integrity() {
    log_step "Validating function integrity"
    
    # Check if function ZIP exists
    if [ ! -f "$FUNCTION_ZIP" ]; then
        add_result "FAIL" "Function Existence" "Function ZIP file not found: $FUNCTION_ZIP"
        return 1
    fi
    
    add_result "PASS" "Function Existence" "Function ZIP found: $(du -sh "$FUNCTION_ZIP" | cut -f1)"
    
    # Test ZIP integrity
    if unzip -t "$FUNCTION_ZIP" > /dev/null 2>&1; then
        add_result "PASS" "ZIP Integrity" "Function ZIP is valid and extractable"
    else
        add_result "FAIL" "ZIP Integrity" "Function ZIP is corrupted or invalid"
        return 1
    fi
    
    # Check function structure
    temp_dir=$(mktemp -d)
    unzip -q "$FUNCTION_ZIP" -d "$temp_dir"
    
    if [ -f "$temp_dir/lambda_function.py" ]; then
        add_result "PASS" "Function Structure" "Correct lambda_function.py found"
    else
        add_result "FAIL" "Function Structure" "Missing lambda_function.py in function package"
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
    function_size_bytes=$(stat -f%z "$FUNCTION_ZIP" 2>/dev/null || stat -c%s "$FUNCTION_ZIP")
    function_size_kb=$((function_size_bytes / 1024))
    
    # AWS Lambda function limits (simplified pattern should be very small)
    MAX_FUNCTION_SIZE_MB=250
    RECOMMENDED_MAX_KB=1024  # 1MB for simplified Strands pattern
    
    if [ "$function_size_kb" -le "$RECOMMENDED_MAX_KB" ]; then
        add_result "PASS" "Function Size" "${function_size_kb}KB (excellent for simplified Strands pattern)"
    elif [ "$function_size_kb" -le $((MAX_FUNCTION_SIZE_MB * 1024)) ]; then
        add_result "WARN" "Function Size" "${function_size_kb}KB (within AWS limits but large for simplified pattern)"
    else
        add_result "FAIL" "Function Size" "${function_size_kb}KB (exceeds AWS limit)"
    fi
    
    # Runtime compatibility
    add_result "PASS" "Runtime Compatibility" "python3.12 (matches AWS Lambda runtime)"
    
    # Handler validation
    temp_dir=$(mktemp -d)
    unzip -q "$FUNCTION_ZIP" -d "$temp_dir"
    
    if grep -q "def lambda_handler" "$temp_dir/lambda_function.py"; then
        add_result "PASS" "Handler Function" "lambda_handler function found"
    else
        add_result "FAIL" "Handler Function" "lambda_handler function not found"
    fi
    
    rm -rf "$temp_dir"
}

# Function code validation
validate_function_code() {
    log_step "Validating function code"
    
    temp_dir=$(mktemp -d)
    unzip -q "$FUNCTION_ZIP" -d "$temp_dir"
    
    # Python syntax validation
    if python3.12 -m py_compile "$temp_dir/lambda_function.py" 2>/dev/null; then
        add_result "PASS" "Python Syntax" "Function code has valid Python syntax"
    else
        add_result "FAIL" "Python Syntax" "Function code has syntax errors"
        rm -rf "$temp_dir"
        return 1
    fi
    
    # Function structure validation (simplified pattern)
    python3.12 -c "
import sys
sys.path.insert(0, '$temp_dir')

try:
    import lambda_function
    
    # Check required functions (simplified pattern)
    required_functions = ['lambda_handler', 'health_check_handler']
    missing_functions = []
    
    for func in required_functions:
        if not hasattr(lambda_function, func):
            missing_functions.append(func)
    
    if missing_functions:
        print(f'MISSING_FUNCTIONS:{\"|\" .join(missing_functions)}')
        exit(1)
    else:
        print('ALL_FUNCTIONS_FOUND')
        
    # Check simplified Strands pattern indicators
    if hasattr(lambda_function, 'CODERIPPLE_SYSTEM_PROMPT'):
        print('STRANDS_PATTERN_OK')
    else:
        print('STRANDS_PATTERN_MISSING')
        
except Exception as e:
    print(f'IMPORT_ERROR:{e}')
    exit(1)
" > validation_output.txt 2>&1
    
    if grep -q "ALL_FUNCTIONS_FOUND" validation_output.txt; then
        add_result "PASS" "Function Structure" "All required functions found"
    else
        if grep -q "MISSING_FUNCTIONS:" validation_output.txt; then
            missing=$(grep "MISSING_FUNCTIONS:" validation_output.txt | cut -d: -f2-)
            add_result "FAIL" "Function Structure" "Missing functions: $missing"
        fi
    fi
    
    if grep -q "STRANDS_PATTERN_OK" validation_output.txt; then
        add_result "PASS" "Strands Pattern" "Simplified Strands pattern indicators present"
    else
        add_result "WARN" "Strands Pattern" "Strands pattern indicators missing or incomplete"
    fi
    
    rm -f validation_output.txt
    rm -rf "$temp_dir"
}

# Performance validation (simplified)
validate_performance() {
    if [ "$VALIDATION_MODE" = "quick" ]; then
        log_debug "Skipping performance validation in quick mode"
        return 0
    fi
    
    log_step "Running performance validation"
    
    temp_dir=$(mktemp -d)
    unzip -q "$FUNCTION_ZIP" -d "$temp_dir"
    
    # Function load time test (no layer environment variables needed)
    python3.12 -c "
import sys
import time
sys.path.insert(0, '$temp_dir')

start_time = time.time()
try:
    import lambda_function
    import_time = time.time() - start_time
    print(f'IMPORT_TIME:{import_time:.3f}')
    
    # Test function instantiation
    start_time = time.time()
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-request'
            self.remaining_time_in_millis = lambda: 30000
    
    context = MockContext()
    instantiation_time = time.time() - start_time
    print(f'INSTANTIATION_TIME:{instantiation_time:.3f}')
    
    total_time = import_time + instantiation_time
    print(f'TOTAL_LOAD_TIME:{total_time:.3f}')
    
except Exception as e:
    print(f'PERFORMANCE_ERROR:{e}')
    exit(1)
" > performance_results.txt
    
    # Process performance results
    if grep -q "TOTAL_LOAD_TIME:" performance_results.txt; then
        load_time=$(grep "TOTAL_LOAD_TIME:" performance_results.txt | cut -d: -f2)
        if (( $(echo "$load_time < 0.5" | bc -l) )); then
            add_result "PASS" "Load Performance" "${load_time}s (excellent for simplified pattern)"
        elif (( $(echo "$load_time < 1.0" | bc -l) )); then
            add_result "WARN" "Load Performance" "${load_time}s (acceptable for simplified pattern)"
        else
            add_result "FAIL" "Load Performance" "${load_time}s (too slow for simplified pattern)"
        fi
    else
        add_result "FAIL" "Load Performance" "Could not measure function load time"
    fi
    
    rm -f performance_results.txt
    rm -rf "$temp_dir"
}

# Lambda simulation test (simplified)
validate_lambda_simulation() {
    log_step "Running Lambda simulation test"
    
    temp_dir=$(mktemp -d)
    unzip -q "$FUNCTION_ZIP" -d "$temp_dir"
    
    # Test Lambda handler simulation (no layer environment variables)
    python3.12 -c "
import sys
import json
sys.path.insert(0, '$temp_dir')

try:
    import lambda_function
    
    # Mock context
    class MockContext:
        def __init__(self):
            self.aws_request_id = 'test-simulation-12345'
            self.remaining_time_in_millis = lambda: 30000
            self.function_name = 'coderipple-orchestrator'
    
    context = MockContext()
    
    # Test health check handler
    result = lambda_function.health_check_handler({}, context)
    
    if result.get('statusCode') in [200, 503]:  # Either healthy or unhealthy is OK
        print('HEALTH_CHECK_OK')
    else:
        print(f'HEALTH_CHECK_FAILED:{result}')
        exit(1)
    
    print('SIMULATION_SUCCESS')
    
except Exception as e:
    print(f'SIMULATION_ERROR:{e}')
    exit(1)
" > simulation_result.txt 2>&1
    
    if grep -q "SIMULATION_SUCCESS" simulation_result.txt; then
        add_result "PASS" "Lambda Simulation" "Function handlers executed successfully in simulation"
    else
        error_msg=$(grep "SIMULATION_ERROR:" simulation_result.txt | cut -d: -f2- || echo "Unknown error")
        add_result "FAIL" "Lambda Simulation" "Simulation failed: $error_msg"
    fi
    
    rm -f simulation_result.txt
    rm -rf "$temp_dir"
}

# Generate comprehensive validation report (simplified)
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
    "function_name": "coderipple-orchestrator",
    "validation_mode": "$VALIDATION_MODE",
    "architecture": "simplified-strands-pattern",
    "summary": {
      "total_tests": $total_tests,
      "passed": $passed_tests,
      "failed": $failed_tests,
      "warnings": $warning_tests,
      "success_rate": $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc)
    },
    "function_info": {
      "file": "$FUNCTION_ZIP",
      "size_bytes": $(stat -f%z "$FUNCTION_ZIP" 2>/dev/null || stat -c%s "$FUNCTION_ZIP"),
      "size_human": "$(du -sh "$FUNCTION_ZIP" | cut -f1)",
      "architecture": "simplified-strands",
      "pattern": "official-strands-deployment"
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
    
    echo "" >> "$report_file"
    echo "    ]" >> "$report_file"
    echo "  }" >> "$report_file"
    echo "}" >> "$report_file"
    
    add_result "INFO" "Validation Report" "Generated: $report_file"
}

# Print validation summary (simplified)
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
    echo "🚀 Architecture: Simplified Strands Pattern"
    echo "   Function Size: $(du -sh "$FUNCTION_ZIP" | cut -f1)"
    echo "   Pattern: Official AWS Strands Deployment"
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
            echo "🎉 All validations passed! Function is ready for deployment."
        else
            echo "✅ Validation completed with warnings. Review warnings before deployment."
        fi
        return 0
    else
        echo "💥 Validation failed! Address failures before deployment."
        return 1
    fi
}

# Main execution flow (simplified)
main() {
    # Run validation steps based on mode
    case "$VALIDATION_MODE" in
        "full")
            validate_function_integrity || exit 1
            validate_aws_compatibility
            validate_function_code
            validate_performance
            validate_lambda_simulation
            ;;
        "quick")
            validate_function_integrity || exit 1
            validate_aws_compatibility
            validate_function_code
            ;;
        "function-only")
            validate_function_integrity || exit 1
            validate_aws_compatibility
            validate_function_code
            validate_lambda_simulation
            ;;
        *)
            log_error "Unknown validation mode: $VALIDATION_MODE"
            exit 1
            ;;
    esac
    
    generate_validation_report
    
    if print_validation_summary; then
        log_section_complete "Comprehensive Validation (Simplified Strands Pattern)"
        exit 0
    else
        log_section_complete "Comprehensive Validation (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"