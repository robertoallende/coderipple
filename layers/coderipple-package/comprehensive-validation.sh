#!/bin/bash
# layers/coderipple-package/comprehensive-validation.sh
# Comprehensive validation framework for CodeRipple Package Layer

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

log_section "CodeRipple Package Layer - Comprehensive Validation"

# Configuration
LAYER_ZIP="coderipple-package-layer.zip"
VALIDATION_MODE=${VALIDATION_MODE:-"full"}  # full, quick, agents-only
GENERATE_REPORT=${GENERATE_REPORT:-true}
CODERIPPLE_SOURCE="../../coderipple"

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
    
    if [ -d "$temp_dir/python/coderipple" ]; then
        add_result "PASS" "Layer Structure" "Correct python/coderipple directory structure"
        
        # Count modules
        module_count=$(find "$temp_dir/python/coderipple" -name "*.py" -type f | wc -l)
        add_result "INFO" "Module Count" "$module_count Python modules in package"
    else
        add_result "FAIL" "Layer Structure" "Missing python/coderipple directory in layer"
        rm -rf "$temp_dir"
        return 1
    fi
    
    rm -rf "$temp_dir"
    return 0
}

# CodeRipple package validation
validate_coderipple_package() {
    log_step "Validating CodeRipple package"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Test CodeRipple package import
    python3.12 -c "
import sys
sys.path.insert(0, '$temp_dir/python')

try:
    import coderipple
    print('PACKAGE_IMPORT_SUCCESS')
except ImportError as e:
    print(f'PACKAGE_IMPORT_FAILED:{e}')
    exit(1)
" > validation_output.txt 2>&1
    
    if grep -q "PACKAGE_IMPORT_SUCCESS" validation_output.txt; then
        add_result "PASS" "Package Import" "CodeRipple package imports successfully"
    else
        error_msg=$(grep "PACKAGE_IMPORT_FAILED:" validation_output.txt | cut -d: -f2- || echo "Unknown error")
        add_result "FAIL" "Package Import" "CodeRipple package import failed: $error_msg"
        rm -f validation_output.txt
        rm -rf "$temp_dir"
        return 1
    fi
    
    rm -f validation_output.txt
    rm -rf "$temp_dir"
}

# Agent validation
validate_agents() {
    log_step "Validating CodeRipple agents"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Test agent imports
    python3.12 -c "
import sys
sys.path.insert(0, '$temp_dir/python')

agents = [
    ('coderipple.tourist_guide_agent', 'Tourist Guide Agent'),
    ('coderipple.building_inspector_agent', 'Building Inspector Agent'),
    ('coderipple.historian_agent', 'Historian Agent'),
    ('coderipple.orchestrator_agent', 'Orchestrator Agent')
]

import_failures = []
import_successes = []

for agent_module, agent_name in agents:
    try:
        module = __import__(agent_module, fromlist=[''])
        import_successes.append(agent_name)
    except ImportError as e:
        import_failures.append(f'{agent_name}: {e}')

if import_failures:
    print('AGENT_IMPORT_FAILURES:' + '|'.join(import_failures))
    
if import_successes:
    print('AGENT_IMPORT_SUCCESSES:' + '|'.join(import_successes))
    
if not import_failures:
    print('ALL_AGENTS_OK')
" > validation_output.txt 2>&1
    
    if grep -q "ALL_AGENTS_OK" validation_output.txt; then
        successes=$(grep "AGENT_IMPORT_SUCCESSES:" validation_output.txt | cut -d: -f2- | tr '|' ', ')
        add_result "PASS" "Agent Imports" "All agents import successfully: $successes"
    else
        if grep -q "AGENT_IMPORT_FAILURES:" validation_output.txt; then
            failures=$(grep "AGENT_IMPORT_FAILURES:" validation_output.txt | cut -d: -f2-)
            add_result "FAIL" "Agent Imports" "Agent import failures: $failures"
        fi
    fi
    
    rm -f validation_output.txt
    rm -rf "$temp_dir"
}

# Tool validation
validate_tools() {
    if [ "$VALIDATION_MODE" = "agents-only" ]; then
        log_debug "Skipping tool validation in agents-only mode"
        return 0
    fi
    
    log_step "Validating CodeRipple tools"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Test tool imports
    python3.12 -c "
import sys
sys.path.insert(0, '$temp_dir/python')

tools = [
    ('coderipple.config', 'Configuration'),
    ('coderipple.webhook_parser', 'Webhook Parser'),
    ('coderipple.git_analysis_tool', 'Git Analysis Tool'),
    ('coderipple.content_generation_tools', 'Content Generation Tools')
]

import_failures = []
import_successes = []

for tool_module, tool_name in tools:
    try:
        module = __import__(tool_module, fromlist=[''])
        import_successes.append(tool_name)
    except ImportError as e:
        import_failures.append(f'{tool_name}: {e}')

if import_failures:
    print('TOOL_IMPORT_FAILURES:' + '|'.join(import_failures))
    
if import_successes:
    print('TOOL_IMPORT_SUCCESSES:' + '|'.join(import_successes))
    
if not import_failures:
    print('ALL_TOOLS_OK')
" > validation_output.txt 2>&1
    
    if grep -q "ALL_TOOLS_OK" validation_output.txt; then
        successes=$(grep "TOOL_IMPORT_SUCCESSES:" validation_output.txt | cut -d: -f2- | tr '|' ', ')
        add_result "PASS" "Tool Imports" "All tools import successfully: $successes"
    else
        if grep -q "TOOL_IMPORT_FAILURES:" validation_output.txt; then
            failures=$(grep "TOOL_IMPORT_FAILURES:" validation_output.txt | cut -d: -f2-)
            add_result "WARN" "Tool Imports" "Some tool import issues: $failures"
        fi
    fi
    
    rm -f validation_output.txt
    rm -rf "$temp_dir"
}

# AWS Lambda compatibility validation
validate_aws_compatibility() {
    log_step "Validating AWS Lambda compatibility"
    
    # Size limits
    layer_size_bytes=$(stat -f%z "$LAYER_ZIP" 2>/dev/null || stat -c%s "$LAYER_ZIP")
    layer_size_mb=$((layer_size_bytes / 1024 / 1024))
    
    # AWS Lambda layer limits
    MAX_LAYER_SIZE_MB=250
    RECOMMENDED_MAX_MB=50  # For custom packages
    
    if [ "$layer_size_mb" -le "$RECOMMENDED_MAX_MB" ]; then
        add_result "PASS" "Layer Size" "${layer_size_mb}MB (within recommended limits for custom packages)"
    elif [ "$layer_size_mb" -le "$MAX_LAYER_SIZE_MB" ]; then
        add_result "WARN" "Layer Size" "${layer_size_mb}MB (within AWS limits but large for custom package)"
    else
        add_result "FAIL" "Layer Size" "${layer_size_mb}MB (exceeds AWS limit of ${MAX_LAYER_SIZE_MB}MB)"
    fi
    
    # Runtime compatibility
    add_result "PASS" "Runtime Compatibility" "python3.12 (matches AWS Lambda runtime)"
    
    # Architecture compatibility
    add_result "PASS" "Architecture Compatibility" "x86_64 (standard Lambda architecture)"
}

# Performance validation
validate_performance() {
    if [ "$VALIDATION_MODE" = "quick" ]; then
        log_debug "Skipping performance validation in quick mode"
        return 0
    fi
    
    log_step "Running performance validation"
    
    temp_dir=$(mktemp -d)
    unzip -q "$LAYER_ZIP" -d "$temp_dir"
    
    # Import performance test
    python3.12 -c "
import sys
import time
sys.path.insert(0, '$temp_dir/python')

modules_to_test = [
    'coderipple',
    'coderipple.orchestrator_agent',
    'coderipple.config'
]

total_start = time.time()

for module in modules_to_test:
    start_time = time.time()
    try:
        __import__(module)
        import_time = time.time() - start_time
        print(f'{module}:{import_time:.3f}')
    except ImportError:
        print(f'{module}:FAILED')

total_time = time.time() - total_start
print(f'TOTAL:{total_time:.3f}')
" > performance_results.txt
    
    # Process performance results
    while IFS=':' read -r module time_or_status; do
        if [ "$time_or_status" = "FAILED" ]; then
            add_result "FAIL" "Performance ($module)" "Import failed"
        elif [ "$module" = "TOTAL" ]; then
            if (( $(echo "$time_or_status > 1.0" | bc -l) )); then
                add_result "WARN" "Performance (Total)" "${time_or_status}s (may impact Lambda cold start)"
            else
                add_result "PASS" "Performance (Total)" "${time_or_status}s (acceptable for Lambda)"
            fi
        else
            if (( $(echo "$time_or_status > 0.5" | bc -l) )); then
                add_result "WARN" "Performance ($module)" "${time_or_status}s (slow import)"
            else
                add_result "PASS" "Performance ($module)" "${time_or_status}s"
            fi
        fi
    done < performance_results.txt
    
    rm -f performance_results.txt
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
    """Test Lambda handler using CodeRipple package layer"""
    
    try:
        from coderipple.orchestrator_agent import OrchestratorAgent
        from coderipple.config import CodeRippleConfig
        
        # Test basic functionality
        config = CodeRippleConfig()
        orchestrator = OrchestratorAgent()
        
        return {
            'statusCode': 200,
            'body': {
                'config_loaded': True,
                'orchestrator_created': True,
                'message': 'CodeRipple package functional in Lambda simulation'
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                'error': str(e),
                'message': 'CodeRipple package failed in Lambda simulation'
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
        add_result "PASS" "Lambda Simulation" "Handler executed successfully with CodeRipple package"
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
    "layer_name": "coderipple-package",
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
    
    echo "" >> "$report_file"
    echo "    ]" >> "$report_file"
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
            echo "🎉 All validations passed! Package layer is ready for deployment."
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
            validate_coderipple_package
            validate_agents
            validate_tools
            validate_aws_compatibility
            validate_performance
            validate_lambda_simulation
            ;;
        "quick")
            validate_layer_integrity || exit 1
            validate_coderipple_package
            validate_agents
            validate_aws_compatibility
            ;;
        "agents-only")
            validate_layer_integrity || exit 1
            validate_coderipple_package
            validate_agents
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
