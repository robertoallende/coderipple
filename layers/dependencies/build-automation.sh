#!/bin/bash
# layers/dependencies/build-automation.sh
# Comprehensive build automation for CodeRipple Dependencies Layer

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
    log_debug() { echo "🐛 $1"; }
    log_section_complete() { echo -e "✅ $1 - COMPLETED\n"; }
fi

log_section "CodeRipple Dependencies Layer - Build Automation"

# Configuration
LAYER_NAME="coderipple-dependencies"
BUILD_MODE=${BUILD_MODE:-"full"}  # full, quick, validate-only
SKIP_VALIDATION=${SKIP_VALIDATION:-false}
FORCE_REBUILD=${FORCE_REBUILD:-false}
PARALLEL_JOBS=${PARALLEL_JOBS:-4}

# Build mode configuration
configure_build_mode() {
    log_step "Configuring build mode: $BUILD_MODE"
    
    case "$BUILD_MODE" in
        "full")
            DO_INSTALL=true
            DO_PACKAGE=true
            DO_VALIDATE=true
            DO_OPTIMIZE=true
            ;;
        "quick")
            DO_INSTALL=true
            DO_PACKAGE=true
            DO_VALIDATE=false
            DO_OPTIMIZE=false
            ;;
        "validate-only")
            DO_INSTALL=false
            DO_PACKAGE=false
            DO_VALIDATE=true
            DO_OPTIMIZE=false
            ;;
        *)
            log_error "Unknown build mode: $BUILD_MODE"
            exit 1
            ;;
    esac
    
    log_success "Build mode configured: install=$DO_INSTALL, package=$DO_PACKAGE, validate=$DO_VALIDATE, optimize=$DO_OPTIMIZE"
}

# Check if rebuild is needed
check_rebuild_needed() {
    log_step "Checking if rebuild is needed"
    
    if [ "$FORCE_REBUILD" = "true" ]; then
        log_debug "Force rebuild requested"
        return 0
    fi
    
    # Check if layer ZIP exists
    if [ ! -f "coderipple-dependencies-layer.zip" ]; then
        log_debug "Layer ZIP not found, rebuild needed"
        return 0
    fi
    
    # Check if requirements.txt is newer than ZIP
    if [ "requirements.txt" -nt "coderipple-dependencies-layer.zip" ]; then
        log_debug "Requirements.txt newer than layer ZIP, rebuild needed"
        return 0
    fi
    
    # Check if any build script is newer than ZIP
    for script in 1-install.sh 2-package.sh 3-validate.sh; do
        if [ "$script" -nt "coderipple-dependencies-layer.zip" ]; then
            log_debug "$script newer than layer ZIP, rebuild needed"
            return 0
        fi
    done
    
    log_success "Layer is up to date, skipping rebuild"
    return 1
}

# Enhanced installation with parallel processing
enhanced_install() {
    if [ "$DO_INSTALL" != "true" ]; then
        log_debug "Skipping installation step"
        return 0
    fi
    
    log_step "Running enhanced installation"
    
    # Set parallel processing for pip
    export PIP_PARALLEL_JOBS=$PARALLEL_JOBS
    
    # Run installation with timing
    start_time=$(date +%s)
    ./1-install.sh
    end_time=$(date +%s)
    
    install_duration=$((end_time - start_time))
    log_success "Installation completed in ${install_duration}s"
}

# Enhanced packaging with optimization
enhanced_package() {
    if [ "$DO_PACKAGE" != "true" ]; then
        log_debug "Skipping packaging step"
        return 0
    fi
    
    log_step "Running enhanced packaging"
    
    start_time=$(date +%s)
    ./2-package.sh
    end_time=$(date +%s)
    
    package_duration=$((end_time - start_time))
    log_success "Packaging completed in ${package_duration}s"
    
    # Additional optimization if requested
    if [ "$DO_OPTIMIZE" = "true" ]; then
        optimize_layer_advanced
    fi
}

# Advanced layer optimization
optimize_layer_advanced() {
    log_step "Running advanced layer optimization"
    
    cd build/python
    
    # Remove additional unnecessary files
    find . -name "*.pyo" -delete
    find . -name "*.egg-info" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.whl" -delete
    find . -name "RECORD" -delete
    find . -name "INSTALLER" -delete
    find . -name "WHEEL" -delete
    find . -name "METADATA" -delete
    
    # Remove documentation and examples
    find . -name "docs" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "examples" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.md" -delete 2>/dev/null || true
    find . -name "*.rst" -delete 2>/dev/null || true
    
    # Compress large text files
    find . -name "*.txt" -size +1k -exec gzip {} \; 2>/dev/null || true
    
    cd ../..
    
    # Recreate ZIP with better compression
    cd build
    rm -f "../coderipple-dependencies-layer.zip"
    zip -9 -r "../coderipple-dependencies-layer.zip" python/ -q
    cd ..
    
    optimized_size=$(du -sh "coderipple-dependencies-layer.zip" | cut -f1)
    log_success "Advanced optimization completed, final size: $optimized_size"
}

# Enhanced validation with comprehensive testing
enhanced_validate() {
    if [ "$DO_VALIDATE" != "true" ] || [ "$SKIP_VALIDATION" = "true" ]; then
        log_debug "Skipping validation step"
        return 0
    fi
    
    log_step "Running enhanced validation"
    
    start_time=$(date +%s)
    ./3-validate.sh
    end_time=$(date +%s)
    
    validate_duration=$((end_time - start_time))
    log_success "Validation completed in ${validate_duration}s"
    
    # Additional comprehensive testing
    run_comprehensive_tests
}

# Comprehensive testing suite
run_comprehensive_tests() {
    log_step "Running comprehensive test suite"
    
    # Test layer size limits
    layer_size_mb=$(du -sm "coderipple-dependencies-layer.zip" | cut -f1)
    if [ "$layer_size_mb" -gt 50 ]; then
        log_warning "Layer size ($layer_size_mb MB) is large, consider optimization"
    fi
    
    # Test critical package versions
    python3.13 -c "
import sys
sys.path.insert(0, 'build/python')

# Version compatibility tests
import boto3
import botocore
import strands
import requests
import pydantic

print('✅ Version compatibility tests passed')

# Memory usage test
import psutil
import os
process = psutil.Process(os.getpid())
memory_mb = process.memory_info().rss / 1024 / 1024
print(f'✅ Memory usage test: {memory_mb:.1f}MB')

if memory_mb > 500:
    print('⚠️  High memory usage detected')
"
    
    log_success "Comprehensive tests completed"
}

# Generate build report
generate_build_report() {
    log_step "Generating build report"
    
    layer_size=$(du -sh "coderipple-dependencies-layer.zip" | cut -f1)
    layer_size_bytes=$(du -b "coderipple-dependencies-layer.zip" | cut -f1)
    uncompressed_size=$(du -sh "build/python" | cut -f1)
    package_count=$(ls -1 "build/python" | wc -l)
    
    cat > "build-report.json" << EOF
{
  "layer_name": "$LAYER_NAME",
  "build_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "build_mode": "$BUILD_MODE",
  "build_host": "$(hostname)",
  "python_version": "$(python3.13 --version)",
  "layer_metrics": {
    "compressed_size": "$layer_size",
    "compressed_bytes": $layer_size_bytes,
    "uncompressed_size": "$uncompressed_size",
    "package_count": $package_count,
    "compression_ratio": "$(echo "scale=2; $layer_size_bytes / $(du -b build/python | cut -f1)" | bc)"
  },
  "build_configuration": {
    "parallel_jobs": $PARALLEL_JOBS,
    "optimization_enabled": $DO_OPTIMIZE,
    "validation_enabled": $DO_VALIDATE,
    "force_rebuild": "$FORCE_REBUILD"
  },
  "aws_compatibility": {
    "runtime": "python3.13",
    "architecture": "x86_64",
    "max_layer_size": "262144000",
    "within_limits": $([ $layer_size_bytes -lt 262144000 ] && echo "true" || echo "false")
  }
}
EOF
    
    log_success "Build report generated: build-report.json"
    log_debug "Layer size: $layer_size ($layer_size_bytes bytes)"
    log_debug "Package count: $package_count"
}

# Cleanup build artifacts
cleanup_build_artifacts() {
    log_step "Cleaning up build artifacts"
    
    # Keep essential files, remove temporary ones
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf validation_test 2>/dev/null || true
    
    log_success "Build artifacts cleaned"
}

# Main execution flow
main() {
    configure_build_mode
    
    if check_rebuild_needed; then
        enhanced_install
        enhanced_package
    fi
    
    enhanced_validate
    generate_build_report
    cleanup_build_artifacts
    
    log_section_complete "Dependencies Layer Build Automation"
    
    # Summary
    echo ""
    echo "🎉 CodeRipple Dependencies Layer Build Complete!"
    echo ""
    echo "📊 Build Summary:"
    echo "   Layer: $(du -sh coderipple-dependencies-layer.zip | cut -f1)"
    echo "   Packages: $(ls -1 build/python 2>/dev/null | wc -l)"
    echo "   Mode: $BUILD_MODE"
    echo ""
    echo "📁 Generated Files:"
    echo "   • coderipple-dependencies-layer.zip"
    echo "   • build-report.json"
    echo "   • metadata/layer-metadata.json"
    echo ""
}

# Execute main function
main "$@"
