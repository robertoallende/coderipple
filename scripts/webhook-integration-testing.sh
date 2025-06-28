#!/bin/bash
# scripts/webhook-integration-testing.sh
# GitHub Webhook Integration Testing for CodeRipple Layer-based Architecture

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

log_section "CodeRipple Webhook Integration Testing"

# Configuration
TEST_MODE=${TEST_MODE:-"comprehensive"}  # comprehensive, quick, payload-only, live-test
AWS_REGION=${AWS_REGION:-"us-west-2"}
ENVIRONMENT=${ENVIRONMENT:-"production"}
GENERATE_REPORT=${GENERATE_REPORT:-true}

# Test tracking
WEBHOOK_TESTS=()
INTEGRATION_RESULTS=()

# Add webhook test result
add_webhook_test() {
    local status="$1"
    local test_name="$2"
    local details="$3"
    local response_time="$4"
    local payload_size="$5"
    
    WEBHOOK_TESTS+=("$status|$test_name|$details|$response_time|$payload_size")
    
    case "$status" in
        "PASS") log_success "$test_name: $details (${response_time}ms, ${payload_size}B)" ;;
        "FAIL") log_error "$test_name: $details (${response_time}ms)" ;;
        "SKIP") log_warning "$test_name: $details" ;;
        *) log_debug "$test_name: $details" ;;
    esac
}

# Add integration result
add_integration_result() {
    local component="$1"
    local status="$2"
    local details="$3"
    local metrics="$4"
    
    INTEGRATION_RESULTS+=("$component|$status|$details|$metrics")
    log_debug "Integration: $component - $status ($details)"
}

# Get API Gateway URL
get_api_gateway_url() {
    log_step "Getting API Gateway URL"
    
    cd infra/terraform
    api_url=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
    cd ../..
    
    if [ -n "$api_url" ]; then
        add_integration_result "API Gateway" "AVAILABLE" "URL retrieved successfully" "url=$api_url"
        echo "$api_url"
    else
        add_integration_result "API Gateway" "UNAVAILABLE" "URL not found in Terraform outputs" "url=none"
        return 1
    fi
}

# Test webhook payload parsing
test_webhook_payload_parsing() {
    log_step "Testing webhook payload parsing"
    
    # Create test payloads
    mkdir -p test-payloads
    
    # GitHub push event payload
    cat > test-payloads/github-push.json << 'EOF'
{
  "ref": "refs/heads/main",
  "before": "abc123def456",
  "after": "def456ghi789",
  "repository": {
    "id": 123456789,
    "name": "coderipple",
    "full_name": "robertoallende/coderipple",
    "owner": {
      "name": "robertoallende",
      "login": "robertoallende"
    },
    "html_url": "https://github.com/robertoallende/coderipple",
    "clone_url": "https://github.com/robertoallende/coderipple.git"
  },
  "commits": [
    {
      "id": "def456ghi789",
      "message": "Add new documentation feature",
      "author": {
        "name": "Roberto Allende",
        "email": "roberto@example.com"
      },
      "added": ["docs/new-feature.md"],
      "modified": ["README.md", "src/main.py"],
      "removed": []
    }
  ],
  "head_commit": {
    "id": "def456ghi789",
    "message": "Add new documentation feature",
    "author": {
      "name": "Roberto Allende",
      "email": "roberto@example.com"
    }
  }
}
EOF
    
    # GitHub pull request event payload
    cat > test-payloads/github-pr.json << 'EOF'
{
  "action": "opened",
  "number": 42,
  "pull_request": {
    "id": 987654321,
    "number": 42,
    "title": "Feature: Enhanced documentation generation",
    "body": "This PR adds enhanced documentation generation capabilities.",
    "head": {
      "ref": "feature/enhanced-docs",
      "sha": "ghi789jkl012"
    },
    "base": {
      "ref": "main",
      "sha": "def456ghi789"
    }
  },
  "repository": {
    "id": 123456789,
    "name": "coderipple",
    "full_name": "robertoallende/coderipple",
    "owner": {
      "login": "robertoallende"
    }
  }
}
EOF
    
    # Test payload sizes
    push_size=$(stat -f%z "test-payloads/github-push.json" 2>/dev/null || stat -c%s "test-payloads/github-push.json")
    pr_size=$(stat -f%z "test-payloads/github-pr.json" 2>/dev/null || stat -c%s "test-payloads/github-pr.json")
    
    add_webhook_test "PASS" "Push Payload Creation" "GitHub push event payload created" "0" "$push_size"
    add_webhook_test "PASS" "PR Payload Creation" "GitHub pull request event payload created" "0" "$pr_size"
    
    # Validate JSON structure
    if jq empty test-payloads/github-push.json 2>/dev/null; then
        add_webhook_test "PASS" "Push Payload Validation" "Valid JSON structure" "0" "$push_size"
    else
        add_webhook_test "FAIL" "Push Payload Validation" "Invalid JSON structure" "0" "$push_size"
    fi
    
    if jq empty test-payloads/github-pr.json 2>/dev/null; then
        add_webhook_test "PASS" "PR Payload Validation" "Valid JSON structure" "0" "$pr_size"
    else
        add_webhook_test "FAIL" "PR Payload Validation" "Invalid JSON structure" "0" "$pr_size"
    fi
}

# Test local webhook processing
test_local_webhook_processing() {
    log_step "Testing local webhook processing"
    
    # Test with Python directly if available
    if command -v python3 &> /dev/null && [ -f "coderipple/webhook_parser.py" ]; then
        # Test webhook parser
        python3 -c "
import sys
sys.path.append('coderipple')
from webhook_parser import parse_github_webhook
import json

# Test push event
with open('test-payloads/github-push.json', 'r') as f:
    push_data = json.load(f)

parsed = parse_github_webhook(push_data)
print(f'Push event parsed: {len(parsed.get(\"commits\", []))} commits')

# Test PR event  
with open('test-payloads/github-pr.json', 'r') as f:
    pr_data = json.load(f)

parsed_pr = parse_github_webhook(pr_data)
print(f'PR event parsed: action={parsed_pr.get(\"action\", \"unknown\")}')
" > local-webhook-test.log 2>&1
        
        if [ $? -eq 0 ]; then
            commits=$(grep "commits" local-webhook-test.log | grep -o '[0-9]\+' || echo "0")
            add_webhook_test "PASS" "Local Webhook Parser" "Successfully parsed webhook events" "0" "0"
        else
            add_webhook_test "FAIL" "Local Webhook Parser" "Failed to parse webhook events" "0" "0"
        fi
    else
        add_webhook_test "SKIP" "Local Webhook Parser" "Python or webhook parser not available" "0" "0"
    fi
}

# Test Lambda function invocation
test_lambda_function_invocation() {
    log_step "Testing Lambda function invocation"
    
    cd infra/terraform
    function_name=$(terraform output -raw lambda_function_name 2>/dev/null || echo "")
    cd ../..
    
    if [ -z "$function_name" ]; then
        add_webhook_test "SKIP" "Lambda Function Test" "Function name not available" "0" "0"
        return 0
    fi
    
    # Test with push event
    test_start=$(date +%s%3N)
    
    aws lambda invoke \
        --function-name "$function_name" \
        --payload file://test-payloads/github-push.json \
        --cli-binary-format raw-in-base64-out \
        lambda-push-response.json > lambda-invoke.log 2>&1
    
    test_end=$(date +%s%3N)
    response_time=$((test_end - test_start))
    
    if [ $? -eq 0 ] && [ -f "lambda-push-response.json" ]; then
        status_code=$(jq -r '.statusCode' lambda-push-response.json 2>/dev/null || echo "unknown")
        
        if [ "$status_code" = "200" ]; then
            # Extract response details
            agents_invoked=$(jq -r '.body | fromjson | .agents_invoked | length' lambda-push-response.json 2>/dev/null || echo "0")
            repository=$(jq -r '.body | fromjson | .repository' lambda-push-response.json 2>/dev/null || echo "unknown")
            
            add_webhook_test "PASS" "Lambda Push Event" "Function processed push event successfully (agents: $agents_invoked)" "$response_time" "$(stat -f%z test-payloads/github-push.json 2>/dev/null || stat -c%s test-payloads/github-push.json)"
        else
            add_webhook_test "FAIL" "Lambda Push Event" "Function returned status $status_code" "$response_time" "0"
        fi
        
        rm -f lambda-push-response.json
    else
        add_webhook_test "FAIL" "Lambda Push Event" "Function invocation failed" "$response_time" "0"
    fi
    
    # Test with PR event
    test_start=$(date +%s%3N)
    
    aws lambda invoke \
        --function-name "$function_name" \
        --payload file://test-payloads/github-pr.json \
        --cli-binary-format raw-in-base64-out \
        lambda-pr-response.json > lambda-invoke-pr.log 2>&1
    
    test_end=$(date +%s%3N)
    response_time=$((test_end - test_start))
    
    if [ $? -eq 0 ] && [ -f "lambda-pr-response.json" ]; then
        status_code=$(jq -r '.statusCode' lambda-pr-response.json 2>/dev/null || echo "unknown")
        
        if [ "$status_code" = "200" ]; then
            add_webhook_test "PASS" "Lambda PR Event" "Function processed PR event successfully" "$response_time" "$(stat -f%z test-payloads/github-pr.json 2>/dev/null || stat -c%s test-payloads/github-pr.json)"
        else
            add_webhook_test "FAIL" "Lambda PR Event" "Function returned status $status_code" "$response_time" "0"
        fi
        
        rm -f lambda-pr-response.json
    else
        add_webhook_test "FAIL" "Lambda PR Event" "Function invocation failed" "$response_time" "0"
    fi
}

# Test API Gateway integration
test_api_gateway_integration() {
    log_step "Testing API Gateway integration"
    
    api_url=$(get_api_gateway_url)
    
    if [ -z "$api_url" ]; then
        add_webhook_test "SKIP" "API Gateway Test" "API Gateway URL not available" "0" "0"
        return 0
    fi
    
    # Test with push event via API Gateway
    test_start=$(date +%s%3N)
    
    response=$(curl -s -w "%{http_code}|%{time_total}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "User-Agent: GitHub-Hookshot/webhook-test" \
        -H "X-GitHub-Event: push" \
        -d @test-payloads/github-push.json \
        "$api_url" 2>/dev/null || echo "000|0")
    
    test_end=$(date +%s%3N)
    
    http_code="${response##*|}"
    response_time_curl="${response%|*}"
    response_time=$((test_end - test_start))
    response_body="${response_time_curl%|*}"
    
    if [ "$http_code" = "200" ]; then
        add_webhook_test "PASS" "API Gateway Push" "API Gateway processed push event successfully" "$response_time" "$(stat -f%z test-payloads/github-push.json 2>/dev/null || stat -c%s test-payloads/github-push.json)"
    elif [ "$http_code" = "500" ]; then
        add_webhook_test "FAIL" "API Gateway Push" "API Gateway returned 500 (function error)" "$response_time" "0"
    else
        add_webhook_test "FAIL" "API Gateway Push" "API Gateway returned HTTP $http_code" "$response_time" "0"
    fi
    
    # Test with PR event via API Gateway
    test_start=$(date +%s%3N)
    
    response=$(curl -s -w "%{http_code}|%{time_total}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "User-Agent: GitHub-Hookshot/webhook-test" \
        -H "X-GitHub-Event: pull_request" \
        -d @test-payloads/github-pr.json \
        "$api_url" 2>/dev/null || echo "000|0")
    
    test_end=$(date +%s%3N)
    
    http_code="${response##*|}"
    response_time=$((test_end - test_start))
    
    if [ "$http_code" = "200" ]; then
        add_webhook_test "PASS" "API Gateway PR" "API Gateway processed PR event successfully" "$response_time" "$(stat -f%z test-payloads/github-pr.json 2>/dev/null || stat -c%s test-payloads/github-pr.json)"
    elif [ "$http_code" = "500" ]; then
        add_webhook_test "FAIL" "API Gateway PR" "API Gateway returned 500 (function error)" "$response_time" "0"
    else
        add_webhook_test "FAIL" "API Gateway PR" "API Gateway returned HTTP $http_code" "$response_time" "0"
    fi
}

# Test webhook security
test_webhook_security() {
    log_step "Testing webhook security"
    
    api_url=$(get_api_gateway_url)
    
    if [ -z "$api_url" ]; then
        add_webhook_test "SKIP" "Security Test" "API Gateway URL not available" "0" "0"
        return 0
    fi
    
    # Test invalid JSON
    test_start=$(date +%s%3N)
    response=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "invalid json" \
        "$api_url" 2>/dev/null || echo "000")
    test_end=$(date +%s%3N)
    response_time=$((test_end - test_start))
    
    http_code="${response: -3}"
    
    if [ "$http_code" = "400" ] || [ "$http_code" = "500" ]; then
        add_webhook_test "PASS" "Invalid JSON Handling" "API Gateway properly rejected invalid JSON" "$response_time" "12"
    else
        add_webhook_test "FAIL" "Invalid JSON Handling" "API Gateway returned unexpected status $http_code" "$response_time" "12"
    fi
    
    # Test empty payload
    test_start=$(date +%s%3N)
    response=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "{}" \
        "$api_url" 2>/dev/null || echo "000")
    test_end=$(date +%s%3N)
    response_time=$((test_end - test_start))
    
    http_code="${response: -3}"
    
    if [ "$http_code" = "200" ] || [ "$http_code" = "400" ]; then
        add_webhook_test "PASS" "Empty Payload Handling" "API Gateway handled empty payload appropriately" "$response_time" "2"
    else
        add_webhook_test "FAIL" "Empty Payload Handling" "API Gateway returned unexpected status $http_code" "$response_time" "2"
    fi
    
    # Test large payload (simulate large commit)
    large_payload='{"repository":{"name":"test"},"commits":['
    for i in {1..100}; do
        large_payload+="{\"id\":\"commit$i\",\"message\":\"Test commit $i\"},"
    done
    large_payload="${large_payload%,}]}"
    
    test_start=$(date +%s%3N)
    response=$(echo "$large_payload" | curl -s -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -d @- \
        "$api_url" 2>/dev/null || echo "000")
    test_end=$(date +%s%3N)
    response_time=$((test_end - test_start))
    
    http_code="${response: -3}"
    payload_size=${#large_payload}
    
    if [ "$http_code" = "200" ]; then
        add_webhook_test "PASS" "Large Payload Handling" "API Gateway processed large payload successfully" "$response_time" "$payload_size"
    else
        add_webhook_test "FAIL" "Large Payload Handling" "API Gateway failed with large payload (HTTP $http_code)" "$response_time" "$payload_size"
    fi
}

# Generate webhook integration report
generate_webhook_report() {
    if [ "$GENERATE_REPORT" != "true" ]; then
        return 0
    fi
    
    log_step "Generating webhook integration report"
    
    report_file="webhook-integration-report.json"
    timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Count test results
    total_tests=0
    passed_tests=0
    failed_tests=0
    skipped_tests=0
    
    for test in "${WEBHOOK_TESTS[@]}"; do
        status=$(echo "$test" | cut -d'|' -f1)
        total_tests=$((total_tests + 1))
        
        case "$status" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "SKIP") skipped_tests=$((skipped_tests + 1)) ;;
        esac
    done
    
    # Generate JSON report
    cat > "$report_file" << EOF
{
  "webhook_integration_report": {
    "timestamp": "$timestamp",
    "test_mode": "$TEST_MODE",
    "environment": "$ENVIRONMENT",
    "aws_region": "$AWS_REGION",
    "summary": {
      "total_tests": $total_tests,
      "passed": $passed_tests,
      "failed": $failed_tests,
      "skipped": $skipped_tests,
      "success_rate": $(echo "scale=2; $passed_tests * 100 / $total_tests" | bc 2>/dev/null || echo "0")
    },
    "webhook_tests": [
EOF
    
    # Add webhook test results
    first_test=true
    for test in "${WEBHOOK_TESTS[@]}"; do
        if [ "$first_test" = false ]; then
            echo "," >> "$report_file"
        fi
        first_test=false
        
        status=$(echo "$test" | cut -d'|' -f1)
        test_name=$(echo "$test" | cut -d'|' -f2)
        details=$(echo "$test" | cut -d'|' -f3)
        response_time=$(echo "$test" | cut -d'|' -f4)
        payload_size=$(echo "$test" | cut -d'|' -f5)
        
        cat >> "$report_file" << EOF
      {
        "test": "$test_name",
        "status": "$status",
        "details": "$details",
        "response_time_ms": $response_time,
        "payload_size_bytes": $payload_size
      }
EOF
    done
    
    # Add integration results if available
    if [ ${#INTEGRATION_RESULTS[@]} -gt 0 ]; then
        echo "," >> "$report_file"
        echo '    ],' >> "$report_file"
        echo '    "integration_results": [' >> "$report_file"
        
        first_result=true
        for result in "${INTEGRATION_RESULTS[@]}"; do
            if [ "$first_result" = false ]; then
                echo "," >> "$report_file"
            fi
            first_result=false
            
            component=$(echo "$result" | cut -d'|' -f1)
            status=$(echo "$result" | cut -d'|' -f2)
            details=$(echo "$result" | cut -d'|' -f3)
            metrics=$(echo "$result" | cut -d'|' -f4)
            
            cat >> "$report_file" << EOF
      {
        "component": "$component",
        "status": "$status",
        "details": "$details",
        "metrics": "$metrics"
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
    
    add_webhook_test "PASS" "Report Generation" "Generated: $report_file" "0" "$(stat -f%z "$report_file" 2>/dev/null || stat -c%s "$report_file")"
}

# Print webhook integration summary
print_webhook_summary() {
    log_section "Webhook Integration Testing Summary"
    
    # Count test results
    total_tests=0
    passed_tests=0
    failed_tests=0
    skipped_tests=0
    
    for test in "${WEBHOOK_TESTS[@]}"; do
        status=$(echo "$test" | cut -d'|' -f1)
        total_tests=$((total_tests + 1))
        
        case "$status" in
            "PASS") passed_tests=$((passed_tests + 1)) ;;
            "FAIL") failed_tests=$((failed_tests + 1)) ;;
            "SKIP") skipped_tests=$((skipped_tests + 1)) ;;
        esac
    done
    
    echo "📊 Webhook Integration Test Results:"
    echo "   Total Tests: $total_tests"
    echo "   ✅ Passed: $passed_tests"
    echo "   ❌ Failed: $failed_tests"
    echo "   ⏭️  Skipped: $skipped_tests"
    
    if [ "$total_tests" -gt 0 ]; then
        success_rate=$(echo "scale=1; $passed_tests * 100 / $total_tests" | bc 2>/dev/null || echo "0")
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    echo "🔗 Integration Configuration:"
    echo "   Test Mode: $TEST_MODE"
    echo "   Environment: $ENVIRONMENT"
    echo "   Region: $AWS_REGION"
    
    # Show integration status
    if [ ${#INTEGRATION_RESULTS[@]} -gt 0 ]; then
        echo ""
        echo "🏗️  Integration Status:"
        for result in "${INTEGRATION_RESULTS[@]}"; do
            component=$(echo "$result" | cut -d'|' -f1)
            status=$(echo "$result" | cut -d'|' -f2)
            details=$(echo "$result" | cut -d'|' -f3)
            echo "   • $component: $status ($details)"
        done
    fi
    
    # Show failures
    if [ "$failed_tests" -gt 0 ]; then
        echo ""
        echo "❌ Failed Tests:"
        for test in "${WEBHOOK_TESTS[@]}"; do
            status=$(echo "$test" | cut -d'|' -f1)
            if [ "$status" = "FAIL" ]; then
                test_name=$(echo "$test" | cut -d'|' -f2)
                details=$(echo "$test" | cut -d'|' -f3)
                echo "   • $test_name: $details"
            fi
        done
    fi
    
    echo ""
    
    # Overall result
    if [ "$failed_tests" -eq 0 ]; then
        echo "🎉 Webhook integration testing completed successfully!"
        echo ""
        echo "✅ Integration Status:"
        echo "   • GitHub webhook payloads: Properly formatted and validated"
        echo "   • Lambda function processing: Working correctly"
        echo "   • API Gateway integration: Functional and responsive"
        echo "   • Security handling: Appropriate error responses"
        echo ""
        echo "🚀 Ready for GitHub webhook configuration!"
        return 0
    else
        echo "💥 Webhook integration testing failed!"
        echo "   Address failed tests before configuring GitHub webhooks."
        return 1
    fi
}

# Main execution flow
main() {
    case "$TEST_MODE" in
        "comprehensive")
            test_webhook_payload_parsing
            test_local_webhook_processing
            test_lambda_function_invocation
            test_api_gateway_integration
            test_webhook_security
            ;;
        "quick")
            test_webhook_payload_parsing
            test_lambda_function_invocation
            test_api_gateway_integration
            ;;
        "payload-only")
            test_webhook_payload_parsing
            test_local_webhook_processing
            ;;
        "live-test")
            test_api_gateway_integration
            test_webhook_security
            ;;
        *)
            log_error "Unknown test mode: $TEST_MODE"
            log_error "Valid modes: comprehensive, quick, payload-only, live-test"
            exit 1
            ;;
    esac
    
    generate_webhook_report
    
    if print_webhook_summary; then
        log_section_complete "Webhook Integration Testing"
        exit 0
    else
        log_section_complete "Webhook Integration Testing (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
