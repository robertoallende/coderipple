#!/bin/bash
# layers/dependencies/ci-cd-integration.sh
# CI/CD integration script for CodeRipple Dependencies Layer

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

log_section "CodeRipple Dependencies Layer - CI/CD Integration"

# CI/CD Environment Detection
detect_ci_environment() {
    log_step "Detecting CI/CD environment"
    
    if [ -n "$GITHUB_ACTIONS" ]; then
        CI_ENVIRONMENT="github-actions"
        CI_BUILD_ID="$GITHUB_RUN_ID"
        CI_COMMIT_SHA="$GITHUB_SHA"
        CI_BRANCH="$GITHUB_REF_NAME"
    elif [ -n "$GITLAB_CI" ]; then
        CI_ENVIRONMENT="gitlab-ci"
        CI_BUILD_ID="$CI_PIPELINE_ID"
        CI_COMMIT_SHA="$CI_COMMIT_SHA"
        CI_BRANCH="$CI_COMMIT_REF_NAME"
    elif [ -n "$JENKINS_URL" ]; then
        CI_ENVIRONMENT="jenkins"
        CI_BUILD_ID="$BUILD_NUMBER"
        CI_COMMIT_SHA="$GIT_COMMIT"
        CI_BRANCH="$GIT_BRANCH"
    else
        CI_ENVIRONMENT="local"
        CI_BUILD_ID="local-$(date +%s)"
        CI_COMMIT_SHA="$(git rev-parse HEAD 2>/dev/null || echo 'unknown')"
        CI_BRANCH="$(git branch --show-current 2>/dev/null || echo 'unknown')"
    fi
    
    log_success "CI Environment: $CI_ENVIRONMENT"
    log_debug "Build ID: $CI_BUILD_ID"
    log_debug "Commit SHA: $CI_COMMIT_SHA"
    log_debug "Branch: $CI_BRANCH"
}

# Environment-specific configuration
configure_ci_environment() {
    log_step "Configuring CI environment"
    
    case "$CI_ENVIRONMENT" in
        "github-actions")
            # GitHub Actions specific configuration
            export BUILD_MODE="full"
            export VALIDATE_LAYERS="true"
            export GENERATE_REPORT="true"
            export PARALLEL_JOBS="2"  # GitHub Actions has limited resources
            
            # Set GitHub Actions outputs
            if [ -n "$GITHUB_OUTPUT" ]; then
                echo "ci_environment=$CI_ENVIRONMENT" >> "$GITHUB_OUTPUT"
                echo "build_id=$CI_BUILD_ID" >> "$GITHUB_OUTPUT"
            fi
            ;;
        "gitlab-ci")
            # GitLab CI specific configuration
            export BUILD_MODE="full"
            export VALIDATE_LAYERS="true"
            export GENERATE_REPORT="true"
            export PARALLEL_JOBS="4"
            ;;
        "jenkins")
            # Jenkins specific configuration
            export BUILD_MODE="full"
            export VALIDATE_LAYERS="true"
            export GENERATE_REPORT="true"
            export PARALLEL_JOBS="4"
            ;;
        "local")
            # Local development configuration
            export BUILD_MODE="${BUILD_MODE:-quick}"
            export VALIDATE_LAYERS="${VALIDATE_LAYERS:-true}"
            export GENERATE_REPORT="${GENERATE_REPORT:-false}"
            export PARALLEL_JOBS="${PARALLEL_JOBS:-4}"
            ;;
    esac
    
    log_success "CI configuration applied for $CI_ENVIRONMENT"
}

# Pre-build validation
pre_build_validation() {
    log_step "Running pre-build validation"
    
    # Check Python version
    python_version=$(python3.12 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [ "$python_version" != "3.12" ]; then
        log_error "Python version mismatch: expected 3.13, got $python_version"
        exit 1
    fi
    log_success "Python version validated: $python_version"
    
    # Check required files
    required_files=("requirements.txt" "1-install.sh" "2-package.sh" "3-validate.sh")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Required file missing: $file"
            exit 1
        fi
    done
    log_success "Required files validated"
    
    # Check disk space (need at least 1GB for build)
    available_space=$(df . | tail -1 | awk '{print $4}')
    required_space=1048576  # 1GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        log_error "Insufficient disk space: $(($available_space / 1024))MB available, need $(($required_space / 1024))MB"
        exit 1
    fi
    log_success "Disk space validated: $(($available_space / 1024))MB available"
}

# Build with CI optimizations
ci_optimized_build() {
    log_step "Running CI-optimized build"
    
    # Set build timestamp
    export BUILD_TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    # Run build automation with CI settings
    ./build-automation.sh
    
    # Verify build artifacts
    if [ ! -f "coderipple-dependencies-layer.zip" ]; then
        log_error "Build failed: layer ZIP not created"
        exit 1
    fi
    
    layer_size=$(du -sh "coderipple-dependencies-layer.zip" | cut -f1)
    log_success "Build completed: layer size $layer_size"
}

# CI-specific validation
ci_validation() {
    log_step "Running CI-specific validation"
    
    # Run comprehensive validation
    ./comprehensive-validation.sh
    
    # Check validation results
    if [ -f "validation-report.json" ]; then
        # Extract key metrics from validation report
        failed_tests=$(python3.12 -c "
import json
with open('validation-report.json', 'r') as f:
    data = json.load(f)
print(data['validation_report']['summary']['failed'])
" 2>/dev/null || echo "0")
        
        if [ "$failed_tests" -gt 0 ]; then
            log_error "Validation failed: $failed_tests test(s) failed"
            exit 1
        fi
        
        log_success "All validation tests passed"
    else
        log_warning "Validation report not generated"
    fi
}

# Artifact management
manage_artifacts() {
    log_step "Managing build artifacts"
    
    # Create artifacts directory
    mkdir -p artifacts
    
    # Copy key artifacts
    cp "coderipple-dependencies-layer.zip" "artifacts/"
    
    if [ -f "build-report.json" ]; then
        cp "build-report.json" "artifacts/"
    fi
    
    if [ -f "validation-report.json" ]; then
        cp "validation-report.json" "artifacts/"
    fi
    
    # Generate artifact manifest
    cat > "artifacts/manifest.json" << EOF
{
  "build_info": {
    "timestamp": "$BUILD_TIMESTAMP",
    "ci_environment": "$CI_ENVIRONMENT",
    "build_id": "$CI_BUILD_ID",
    "commit_sha": "$CI_COMMIT_SHA",
    "branch": "$CI_BRANCH"
  },
  "artifacts": [
    {
      "name": "coderipple-dependencies-layer.zip",
      "type": "lambda_layer",
      "size": "$(du -b coderipple-dependencies-layer.zip | cut -f1)",
      "checksum": "$(shasum -a 256 coderipple-dependencies-layer.zip | cut -d' ' -f1)"
    }
  ]
}
EOF
    
    log_success "Artifacts prepared in artifacts/ directory"
    
    # List artifacts for CI logs
    log_debug "Generated artifacts:"
    ls -la artifacts/
}

# Environment-specific artifact upload
upload_artifacts() {
    log_step "Uploading artifacts (environment: $CI_ENVIRONMENT)"
    
    case "$CI_ENVIRONMENT" in
        "github-actions")
            # GitHub Actions artifact upload is handled by workflow
            log_debug "Artifacts ready for GitHub Actions upload"
            
            # Set outputs for workflow
            if [ -n "$GITHUB_OUTPUT" ]; then
                echo "layer_zip=artifacts/coderipple-dependencies-layer.zip" >> "$GITHUB_OUTPUT"
                echo "layer_size=$(du -sh artifacts/coderipple-dependencies-layer.zip | cut -f1)" >> "$GITHUB_OUTPUT"
            fi
            ;;
        "gitlab-ci")
            # GitLab CI artifacts are defined in .gitlab-ci.yml
            log_debug "Artifacts ready for GitLab CI collection"
            ;;
        "jenkins")
            # Jenkins artifacts are archived by Jenkins job
            log_debug "Artifacts ready for Jenkins archival"
            ;;
        "local")
            log_debug "Local build - artifacts available in artifacts/ directory"
            ;;
    esac
    
    log_success "Artifact upload prepared"
}

# Generate CI summary
generate_ci_summary() {
    log_step "Generating CI summary"
    
    layer_size=$(du -sh "coderipple-dependencies-layer.zip" | cut -f1)
    layer_size_bytes=$(du -b "coderipple-dependencies-layer.zip" | cut -f1)
    
    # Create summary for CI logs
    cat > "ci-summary.md" << EOF
# CodeRipple Dependencies Layer Build Summary

## Build Information
- **Environment**: $CI_ENVIRONMENT
- **Build ID**: $CI_BUILD_ID
- **Commit**: $CI_COMMIT_SHA
- **Branch**: $CI_BRANCH
- **Timestamp**: $BUILD_TIMESTAMP

## Build Results
- **Layer Size**: $layer_size ($layer_size_bytes bytes)
- **Build Mode**: $BUILD_MODE
- **Validation**: $([ -f "validation-report.json" ] && echo "✅ Passed" || echo "⚠️ Skipped")

## Artifacts Generated
- \`coderipple-dependencies-layer.zip\` - Lambda layer package
- \`build-report.json\` - Detailed build metrics
- \`validation-report.json\` - Validation results
- \`ci-summary.md\` - This summary

## Next Steps
1. Deploy layer to AWS Lambda
2. Update Lambda functions to use new layer version
3. Test integration with CodeRipple agents

---
*Generated by CodeRipple CI/CD Pipeline*
EOF
    
    log_success "CI summary generated: ci-summary.md"
    
    # Output summary to CI logs
    echo ""
    echo "📋 Build Summary:"
    echo "   Layer: $layer_size"
    echo "   Environment: $CI_ENVIRONMENT"
    echo "   Build ID: $CI_BUILD_ID"
    echo ""
}

# Cleanup CI environment
cleanup_ci_environment() {
    log_step "Cleaning up CI environment"
    
    # Remove temporary files but keep artifacts
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf validation_test 2>/dev/null || true
    
    # Keep build directory for debugging in CI
    if [ "$CI_ENVIRONMENT" = "local" ]; then
        rm -rf build 2>/dev/null || true
    fi
    
    log_success "CI environment cleaned"
}

# Main CI/CD execution flow
main() {
    detect_ci_environment
    configure_ci_environment
    pre_build_validation
    ci_optimized_build
    ci_validation
    manage_artifacts
    upload_artifacts
    generate_ci_summary
    cleanup_ci_environment
    
    log_section_complete "CI/CD Integration"
    
    echo ""
    echo "🎉 CodeRipple Dependencies Layer CI/CD Build Complete!"
    echo ""
    echo "📊 Summary:"
    echo "   Environment: $CI_ENVIRONMENT"
    echo "   Layer Size: $(du -sh coderipple-dependencies-layer.zip | cut -f1)"
    echo "   Artifacts: $(ls artifacts/ | wc -l) files in artifacts/"
    echo ""
    echo "✅ Ready for deployment!"
}

# Execute main function
main "$@"
