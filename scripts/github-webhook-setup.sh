#!/bin/bash
# scripts/github-webhook-setup.sh
# GitHub Webhook Configuration Helper for CodeRipple

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

log_section "CodeRipple GitHub Webhook Setup"

# Configuration
SETUP_MODE=${SETUP_MODE:-"configure"}  # configure, validate, test, remove
GITHUB_REPO_OWNER=${GITHUB_REPO_OWNER:-"robertoallende"}
GITHUB_REPO_NAME=${GITHUB_REPO_NAME:-"coderipple"}
GITHUB_TOKEN=${GITHUB_TOKEN:-""}
AWS_REGION=${AWS_REGION:-"us-west-2"}

# Setup tracking
SETUP_RESULTS=()

# Add setup result
add_setup_result() {
    local status="$1"
    local component="$2"
    local details="$3"
    local resource_id="$4"
    
    SETUP_RESULTS+=("$status|$component|$details|$resource_id")
    
    case "$status" in
        "SUCCESS") log_success "$component: $details" ;;
        "FAILED") log_error "$component: $details" ;;
        "WARNING") log_warning "$component: $details" ;;
        *) log_debug "$component: $details" ;;
    esac
}

# Get API Gateway URL
get_api_gateway_url() {
    log_step "Getting API Gateway webhook URL"
    
    cd infra/terraform
    api_url=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
    cd ../..
    
    if [ -n "$api_url" ]; then
        add_setup_result "SUCCESS" "API Gateway URL" "Retrieved webhook URL" "$api_url"
        echo "$api_url"
    else
        add_setup_result "FAILED" "API Gateway URL" "Could not retrieve webhook URL from Terraform outputs" "none"
        return 1
    fi
}

# Validate GitHub token
validate_github_token() {
    log_step "Validating GitHub token"
    
    if [ -z "$GITHUB_TOKEN" ]; then
        add_setup_result "FAILED" "GitHub Token" "GITHUB_TOKEN environment variable not set" "none"
        return 1
    fi
    
    # Test GitHub API access
    response=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME" 2>/dev/null || echo "error")
    
    if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
        repo_id=$(echo "$response" | jq -r '.id')
        add_setup_result "SUCCESS" "GitHub Token" "Valid token with repository access" "$repo_id"
        return 0
    else
        add_setup_result "FAILED" "GitHub Token" "Invalid token or no repository access" "none"
        return 1
    fi
}

# Configure GitHub webhook
configure_github_webhook() {
    log_step "Configuring GitHub webhook"
    
    api_url=$(get_api_gateway_url)
    if [ -z "$api_url" ]; then
        return 1
    fi
    
    if ! validate_github_token; then
        return 1
    fi
    
    # Check if webhook already exists
    existing_webhooks=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/hooks" 2>/dev/null || echo "[]")
    
    webhook_id=""
    if echo "$existing_webhooks" | jq -e '.[] | select(.config.url == "'$api_url'")' > /dev/null 2>&1; then
        webhook_id=$(echo "$existing_webhooks" | jq -r '.[] | select(.config.url == "'$api_url'") | .id')
        add_setup_result "WARNING" "Existing Webhook" "Webhook already exists with ID $webhook_id" "$webhook_id"
        
        # Update existing webhook
        webhook_config='{
            "config": {
                "url": "'$api_url'",
                "content_type": "json",
                "insecure_ssl": "0"
            },
            "events": ["push", "pull_request"],
            "active": true
        }'
        
        response=$(curl -s -X PATCH \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$webhook_config" \
            "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/hooks/$webhook_id" 2>/dev/null || echo "error")
        
        if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
            add_setup_result "SUCCESS" "Webhook Update" "Updated existing webhook configuration" "$webhook_id"
        else
            add_setup_result "FAILED" "Webhook Update" "Failed to update existing webhook" "$webhook_id"
            return 1
        fi
    else
        # Create new webhook
        webhook_config='{
            "config": {
                "url": "'$api_url'",
                "content_type": "json",
                "insecure_ssl": "0"
            },
            "events": ["push", "pull_request"],
            "active": true
        }'
        
        response=$(curl -s -X POST \
            -H "Authorization: token $GITHUB_TOKEN" \
            -H "Content-Type: application/json" \
            -d "$webhook_config" \
            "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/hooks" 2>/dev/null || echo "error")
        
        if echo "$response" | jq -e '.id' > /dev/null 2>&1; then
            webhook_id=$(echo "$response" | jq -r '.id')
            add_setup_result "SUCCESS" "Webhook Creation" "Created new webhook with ID $webhook_id" "$webhook_id"
        else
            error_msg=$(echo "$response" | jq -r '.message' 2>/dev/null || echo "Unknown error")
            add_setup_result "FAILED" "Webhook Creation" "Failed to create webhook: $error_msg" "none"
            return 1
        fi
    fi
    
    # Store webhook ID for future reference
    echo "$webhook_id" > .github-webhook-id
    add_setup_result "SUCCESS" "Webhook Configuration" "Webhook configured successfully" "$webhook_id"
}

# Validate webhook configuration
validate_webhook_configuration() {
    log_step "Validating webhook configuration"
    
    if ! validate_github_token; then
        return 1
    fi
    
    # Get webhook configuration
    webhooks=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/hooks" 2>/dev/null || echo "[]")
    
    api_url=$(get_api_gateway_url)
    if [ -z "$api_url" ]; then
        return 1
    fi
    
    # Find our webhook
    webhook_info=$(echo "$webhooks" | jq '.[] | select(.config.url == "'$api_url'")')
    
    if [ -n "$webhook_info" ] && [ "$webhook_info" != "null" ]; then
        webhook_id=$(echo "$webhook_info" | jq -r '.id')
        webhook_active=$(echo "$webhook_info" | jq -r '.active')
        webhook_events=$(echo "$webhook_info" | jq -r '.events | join(", ")')
        
        add_setup_result "SUCCESS" "Webhook Validation" "Webhook found: ID $webhook_id, Active: $webhook_active, Events: $webhook_events" "$webhook_id"
        
        # Validate configuration
        if [ "$webhook_active" = "true" ]; then
            add_setup_result "SUCCESS" "Webhook Status" "Webhook is active" "$webhook_id"
        else
            add_setup_result "WARNING" "Webhook Status" "Webhook is inactive" "$webhook_id"
        fi
        
        if echo "$webhook_events" | grep -q "push" && echo "$webhook_events" | grep -q "pull_request"; then
            add_setup_result "SUCCESS" "Webhook Events" "Correct events configured (push, pull_request)" "$webhook_id"
        else
            add_setup_result "WARNING" "Webhook Events" "Events may not be configured correctly: $webhook_events" "$webhook_id"
        fi
    else
        add_setup_result "FAILED" "Webhook Validation" "No webhook found for API Gateway URL" "none"
        return 1
    fi
}

# Test webhook functionality
test_webhook_functionality() {
    log_step "Testing webhook functionality"
    
    api_url=$(get_api_gateway_url)
    if [ -z "$api_url" ]; then
        return 1
    fi
    
    # Create test payload
    test_payload='{
        "ref": "refs/heads/main",
        "repository": {
            "name": "'$GITHUB_REPO_NAME'",
            "full_name": "'$GITHUB_REPO_OWNER'/'$GITHUB_REPO_NAME'",
            "owner": {
                "login": "'$GITHUB_REPO_OWNER'"
            }
        },
        "commits": [
            {
                "id": "test123",
                "message": "Test webhook configuration",
                "author": {
                    "name": "Webhook Test",
                    "email": "test@example.com"
                }
            }
        ]
    }'
    
    # Test webhook endpoint
    test_start=$(date +%s%3N)
    response=$(curl -s -w "%{http_code}" \
        -X POST \
        -H "Content-Type: application/json" \
        -H "User-Agent: GitHub-Hookshot/webhook-test" \
        -H "X-GitHub-Event: push" \
        -d "$test_payload" \
        "$api_url" 2>/dev/null || echo "000")
    test_end=$(date +%s%3N)
    
    http_code="${response: -3}"
    response_time=$((test_end - test_start))
    
    if [ "$http_code" = "200" ]; then
        add_setup_result "SUCCESS" "Webhook Test" "Webhook endpoint responding correctly (${response_time}ms)" "test-successful"
    elif [ "$http_code" = "500" ]; then
        add_setup_result "WARNING" "Webhook Test" "Webhook endpoint returned 500 (function may have errors)" "test-error"
    else
        add_setup_result "FAILED" "Webhook Test" "Webhook endpoint returned HTTP $http_code" "test-failed"
    fi
}

# Remove webhook
remove_webhook() {
    log_step "Removing GitHub webhook"
    
    if ! validate_github_token; then
        return 1
    fi
    
    api_url=$(get_api_gateway_url)
    if [ -z "$api_url" ]; then
        return 1
    fi
    
    # Get webhook ID
    webhooks=$(curl -s -H "Authorization: token $GITHUB_TOKEN" \
        "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/hooks" 2>/dev/null || echo "[]")
    
    webhook_id=$(echo "$webhooks" | jq -r '.[] | select(.config.url == "'$api_url'") | .id')
    
    if [ -n "$webhook_id" ] && [ "$webhook_id" != "null" ]; then
        response=$(curl -s -X DELETE \
            -H "Authorization: token $GITHUB_TOKEN" \
            "https://api.github.com/repos/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/hooks/$webhook_id" 2>/dev/null || echo "error")
        
        if [ "$response" = "" ]; then
            add_setup_result "SUCCESS" "Webhook Removal" "Webhook removed successfully" "$webhook_id"
            rm -f .github-webhook-id
        else
            add_setup_result "FAILED" "Webhook Removal" "Failed to remove webhook" "$webhook_id"
        fi
    else
        add_setup_result "WARNING" "Webhook Removal" "No webhook found to remove" "none"
    fi
}

# Generate setup instructions
generate_setup_instructions() {
    log_step "Generating setup instructions"
    
    api_url=$(get_api_gateway_url)
    
    cat > github-webhook-instructions.md << EOF
# GitHub Webhook Setup Instructions

## Automatic Setup (Recommended)

Run the webhook setup script:
\`\`\`bash
export GITHUB_TOKEN="your_github_token_here"
./scripts/github-webhook-setup.sh
\`\`\`

## Manual Setup

If you prefer to configure the webhook manually:

### 1. Navigate to Repository Settings
- Go to https://github.com/$GITHUB_REPO_OWNER/$GITHUB_REPO_NAME/settings/hooks
- Click "Add webhook"

### 2. Configure Webhook Settings
- **Payload URL**: \`$api_url\`
- **Content type**: \`application/json\`
- **Secret**: (leave empty for now)
- **SSL verification**: ✅ Enable SSL verification

### 3. Select Events
Choose "Let me select individual events" and select:
- ✅ **Pushes** - For commit-based documentation updates
- ✅ **Pull requests** - For PR-based documentation reviews

### 4. Activate Webhook
- ✅ **Active** - Ensure the webhook is active
- Click "Add webhook"

## Verification

After setup, verify the webhook is working:

\`\`\`bash
# Test webhook integration
./scripts/webhook-integration-testing.sh

# Validate webhook configuration
SETUP_MODE=validate ./scripts/github-webhook-setup.sh
\`\`\`

## Webhook Events

CodeRipple will process the following GitHub events:

### Push Events
- Triggered on commits to any branch
- Processes changed files for documentation updates
- Invokes appropriate agents based on file changes

### Pull Request Events
- Triggered on PR open, update, close
- Reviews documentation changes in PRs
- Provides documentation feedback and suggestions

## Troubleshooting

### Common Issues

1. **Webhook not receiving events**
   - Check webhook URL is correct: \`$api_url\`
   - Verify SSL certificate is valid
   - Check GitHub webhook delivery logs

2. **Function errors (500 responses)**
   - Check CloudWatch logs: \`/aws/lambda/coderipple-orchestrator\`
   - Verify layer-based architecture is deployed correctly
   - Run end-to-end validation

3. **Permission errors**
   - Verify GitHub token has repository webhook permissions
   - Check AWS Lambda execution role permissions

### Testing Commands

\`\`\`bash
# Test webhook payload processing
TEST_MODE=payload-only ./scripts/webhook-integration-testing.sh

# Test API Gateway integration
TEST_MODE=live-test ./scripts/webhook-integration-testing.sh

# Comprehensive webhook testing
TEST_MODE=comprehensive ./scripts/webhook-integration-testing.sh
\`\`\`

## Security Considerations

- Webhook secret validation (to be implemented in future versions)
- IP allowlisting for GitHub webhook IPs
- Request validation and sanitization
- Rate limiting and abuse prevention

## Monitoring

Monitor webhook activity through:
- **CloudWatch Logs**: \`/aws/lambda/coderipple-orchestrator\`
- **API Gateway Logs**: \`/aws/apigateway/coderipple-webhook-api\`
- **GitHub Webhook Deliveries**: Repository Settings > Webhooks > Recent Deliveries

EOF

    add_setup_result "SUCCESS" "Setup Instructions" "Generated: github-webhook-instructions.md" "instructions"
}

# Print setup summary
print_setup_summary() {
    log_section "GitHub Webhook Setup Summary"
    
    # Count results
    total_components=0
    successful_components=0
    failed_components=0
    warning_components=0
    
    for result in "${SETUP_RESULTS[@]}"; do
        status=$(echo "$result" | cut -d'|' -f1)
        total_components=$((total_components + 1))
        
        case "$status" in
            "SUCCESS") successful_components=$((successful_components + 1)) ;;
            "FAILED") failed_components=$((failed_components + 1)) ;;
            "WARNING") warning_components=$((warning_components + 1)) ;;
        esac
    done
    
    echo "📊 Setup Results:"
    echo "   Total Components: $total_components"
    echo "   ✅ Successful: $successful_components"
    echo "   ❌ Failed: $failed_components"
    echo "   ⚠️  Warnings: $warning_components"
    
    if [ "$total_components" -gt 0 ]; then
        success_rate=$(echo "scale=1; $successful_components * 100 / $total_components" | bc 2>/dev/null || echo "0")
        echo "   📈 Success Rate: ${success_rate}%"
    fi
    
    echo ""
    echo "🔗 Webhook Configuration:"
    echo "   Repository: $GITHUB_REPO_OWNER/$GITHUB_REPO_NAME"
    echo "   Setup Mode: $SETUP_MODE"
    echo "   Region: $AWS_REGION"
    
    # Show failures and warnings
    if [ "$failed_components" -gt 0 ]; then
        echo ""
        echo "❌ Failed Components:"
        for result in "${SETUP_RESULTS[@]}"; do
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
        for result in "${SETUP_RESULTS[@]}"; do
            status=$(echo "$result" | cut -d'|' -f1)
            if [ "$status" = "WARNING" ]; then
                component=$(echo "$result" | cut -d'|' -f2)
                details=$(echo "$result" | cut -d'|' -f3)
                echo "   • $component: $details"
            fi
        done
    fi
    
    echo ""
    
    # Overall result and next steps
    if [ "$failed_components" -eq 0 ]; then
        echo "🎉 GitHub webhook setup completed successfully!"
        echo ""
        echo "✅ Next Steps:"
        case "$SETUP_MODE" in
            "configure")
                echo "   • Test webhook: SETUP_MODE=test ./scripts/github-webhook-setup.sh"
                echo "   • Run integration tests: ./scripts/webhook-integration-testing.sh"
                echo "   • Make a test commit to trigger webhook"
                ;;
            "validate")
                echo "   • Webhook configuration is valid"
                echo "   • Test functionality: SETUP_MODE=test ./scripts/github-webhook-setup.sh"
                ;;
            "test")
                echo "   • Webhook is functional"
                echo "   • Make a real commit to see CodeRipple in action"
                ;;
        esac
        return 0
    else
        echo "💥 GitHub webhook setup failed!"
        echo "   Address failed components before proceeding."
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   • Check GITHUB_TOKEN environment variable"
        echo "   • Verify API Gateway is deployed"
        echo "   • Run: ./scripts/webhook-integration-testing.sh"
        return 1
    fi
}

# Main execution flow
main() {
    case "$SETUP_MODE" in
        "configure")
            configure_github_webhook
            generate_setup_instructions
            ;;
        "validate")
            validate_webhook_configuration
            ;;
        "test")
            test_webhook_functionality
            ;;
        "remove")
            remove_webhook
            ;;
        *)
            log_error "Unknown setup mode: $SETUP_MODE"
            log_error "Valid modes: configure, validate, test, remove"
            exit 1
            ;;
    esac
    
    if print_setup_summary; then
        log_section_complete "GitHub Webhook Setup"
        exit 0
    else
        log_section_complete "GitHub Webhook Setup (WITH FAILURES)"
        exit 1
    fi
}

# Execute main function
main "$@"
