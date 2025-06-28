#!/bin/bash
# layers/coderipple-package/build-automation.sh
# Comprehensive build automation for CodeRipple Package Layer

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

log_section "CodeRipple Package Layer - Build Automation"

# Configuration
LAYER_NAME="coderipple-package"
BUILD_MODE=${BUILD_MODE:-"full"}  # full, quick, validate-only
SKIP_VALIDATION=${SKIP_VALIDATION:-false}
FORCE_REBUILD=${FORCE_REBUILD:-false}
CODERIPPLE_SOURCE="../../coderipple"

# Build mode configuration
configure_build_mode() {
    log_step "Configuring build mode: $BUILD_MODE"
    
    case "$BUILD_MODE" in
        "full")
            DO_INSTALL=true
            DO_PACKAGE=true
            DO_VALIDATE=true
            DO_OPTIMIZE=true
            DO_SOURCE_ANALYSIS=true
            ;;
        "quick")
            DO_INSTALL=true
            DO_PACKAGE=true
            DO_VALIDATE=false
            DO_OPTIMIZE=false
            DO_SOURCE_ANALYSIS=false
            ;;
        "validate-only")
            DO_INSTALL=false
            DO_PACKAGE=false
            DO_VALIDATE=true
            DO_OPTIMIZE=false
            DO_SOURCE_ANALYSIS=false
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
    if [ ! -f "coderipple-package-layer.zip" ]; then
        log_debug "Layer ZIP not found, rebuild needed"
        return 0
    fi
    
    # Check if CodeRipple source is newer than ZIP
    if [ "$CODERIPPLE_SOURCE" -nt "coderipple-package-layer.zip" ]; then
        log_debug "CodeRipple source newer than layer ZIP, rebuild needed"
        return 0
    fi
    
    # Check if any Python file in CodeRipple source is newer
    if find "$CODERIPPLE_SOURCE/src" -name "*.py" -newer "coderipple-package-layer.zip" | grep -q .; then
        log_debug "CodeRipple source files newer than layer ZIP, rebuild needed"
        return 0
    fi
    
    # Check if any build script is newer than ZIP
    for script in 1-install.sh 2-package.sh 3-validate.sh; do
        if [ "$script" -nt "coderipple-package-layer.zip" ]; then
            log_debug "$script newer than layer ZIP, rebuild needed"
            return 0
        fi
    done
    
    log_success "Layer is up to date, skipping rebuild"
    return 1
}

# Source code analysis
analyze_source_code() {
    if [ "$DO_SOURCE_ANALYSIS" != "true" ]; then
        log_debug "Skipping source code analysis"
        return 0
    fi
    
    log_step "Analyzing CodeRipple source code"
    
    # Validate source structure
    if [ ! -d "$CODERIPPLE_SOURCE/src/coderipple" ]; then
        log_error "CodeRipple source directory not found: $CODERIPPLE_SOURCE/src/coderipple"
        exit 1
    fi
    
    # Count source files and analyze structure
    python3.13 -c "
import os
import ast
import sys

source_dir = '$CODERIPPLE_SOURCE/src/coderipple'
sys.path.insert(0, source_dir)

# Analyze source structure
total_files = 0
total_lines = 0
total_functions = 0
total_classes = 0
agents = []
tools = []

for root, dirs, files in os.walk(source_dir):
    for file in files:
        if file.endswith('.py') and not file.startswith('__'):
            total_files += 1
            filepath = os.path.join(root, file)
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    total_lines += len(content.splitlines())
                    
                    # Parse AST to count functions and classes
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            total_functions += 1
                        elif isinstance(node, ast.ClassDef):
                            total_classes += 1
                    
                    # Categorize files
                    if 'agent' in file:
                        agents.append(file)
                    elif 'tool' in file:
                        tools.append(file)
                        
            except Exception as e:
                print(f'Warning: Could not analyze {file}: {e}')

print(f'Source Analysis Results:')
print(f'  Files: {total_files}')
print(f'  Lines: {total_lines}')
print(f'  Functions: {total_functions}')
print(f'  Classes: {total_classes}')
print(f'  Agents: {len(agents)} ({', '.join(agents)})')
print(f'  Tools: {len(tools)} ({', '.join(tools)})')
"
    
    log_success "Source code analysis completed"
}

# Enhanced installation with source validation
enhanced_install() {
    if [ "$DO_INSTALL" != "true" ]; then
        log_debug "Skipping installation step"
        return 0
    fi
    
    log_step "Running enhanced installation"
    
    # Pre-installation validation
    if [ ! -f "$CODERIPPLE_SOURCE/setup.py" ]; then
        log_error "CodeRipple setup.py not found: $CODERIPPLE_SOURCE/setup.py"
        exit 1
    fi
    
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
        optimize_package_advanced
    fi
}

# Advanced package optimization
optimize_package_advanced() {
    log_step "Running advanced package optimization"
    
    cd build/python
    
    # Remove additional unnecessary files specific to CodeRipple
    find . -name "*.md" -delete 2>/dev/null || true
    find . -name "*.rst" -delete 2>/dev/null || true
    find . -name "*.txt" -delete 2>/dev/null || true
    find . -name "LICENSE*" -delete 2>/dev/null || true
    find . -name "MANIFEST*" -delete 2>/dev/null || true
    
    # Remove development and testing files
    find . -name "*test*" -type f -delete 2>/dev/null || true
    find . -name "debug_*" -delete 2>/dev/null || true
    find . -name "example*" -delete 2>/dev/null || true
    
    # Remove version control artifacts
    find . -name ".git*" -delete 2>/dev/null || true
    find . -name ".svn" -type d -exec rm -rf {} + 2>/dev/null || true
    
    cd ../..
    
    # Recreate ZIP with better compression
    cd build
    rm -f "../coderipple-package-layer.zip"
    zip -9 -r "../coderipple-package-layer.zip" python/ -q
    cd ..
    
    optimized_size=$(du -sh "coderipple-package-layer.zip" | cut -f1)
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
    layer_size_mb=$(du -sm "coderipple-package-layer.zip" | cut -f1)
    if [ "$layer_size_mb" -gt 10 ]; then
        log_warning "Package layer size ($layer_size_mb MB) is large for a custom package"
    fi
    
    # Test agent functionality
    python3.13 -c "
import sys
sys.path.insert(0, 'build/python')

# Test agent imports and basic functionality
agents = [
    'coderipple.tourist_guide_agent',
    'coderipple.building_inspector_agent', 
    'coderipple.historian_agent',
    'coderipple.orchestrator_agent'
]

print('Testing agent functionality:')
for agent_module in agents:
    try:
        module = __import__(agent_module, fromlist=[''])
        
        # Check for expected classes/functions
        if hasattr(module, 'Agent') or hasattr(module, 'agent') or 'agent' in dir(module):
            print(f'✅ {agent_module}: Agent class/function found')
        else:
            print(f'⚠️  {agent_module}: No obvious agent class found')
            
    except ImportError as e:
        print(f'❌ {agent_module}: Import failed - {e}')
        exit(1)

print('\\n✅ Agent functionality tests passed')
"
    
    log_success "Comprehensive tests completed"
}

# Generate build report
generate_build_report() {
    log_step "Generating build report"
    
    layer_size=$(du -sh "coderipple-package-layer.zip" | cut -f1)
    layer_size_bytes=$(du -b "coderipple-package-layer.zip" | cut -f1)
    uncompressed_size=$(du -sh "build/python" | cut -f1)
    
    # Count modules in layer
    module_count=$(find "build/python" -name "*.py" -type f | wc -l)
    
    # Get CodeRipple version
    coderipple_version=$(cd "$CODERIPPLE_SOURCE" && python3.13 setup.py --version 2>/dev/null || echo "unknown")
    
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
    "module_count": $module_count,
    "compression_ratio": "$(echo "scale=2; $layer_size_bytes / $(du -b build/python | cut -f1)" | bc)"
  },
  "source_info": {
    "coderipple_version": "$coderipple_version",
    "source_path": "$CODERIPPLE_SOURCE",
    "source_modified": "$(stat -f %Sm -t %Y-%m-%dT%H:%M:%SZ "$CODERIPPLE_SOURCE" 2>/dev/null || stat -c %y "$CODERIPPLE_SOURCE" | cut -d' ' -f1,2 | tr ' ' T)"
  },
  "build_configuration": {
    "optimization_enabled": $DO_OPTIMIZE,
    "validation_enabled": $DO_VALIDATE,
    "source_analysis_enabled": $DO_SOURCE_ANALYSIS,
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
    log_debug "Module count: $module_count"
    log_debug "CodeRipple version: $coderipple_version"
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
    analyze_source_code
    
    if check_rebuild_needed; then
        enhanced_install
        enhanced_package
    fi
    
    enhanced_validate
    generate_build_report
    cleanup_build_artifacts
    
    log_section_complete "CodeRipple Package Layer Build Automation"
    
    # Summary
    echo ""
    echo "🎉 CodeRipple Package Layer Build Complete!"
    echo ""
    echo "📊 Build Summary:"
    echo "   Layer: $(du -sh coderipple-package-layer.zip | cut -f1)"
    echo "   Modules: $(find build/python -name "*.py" -type f 2>/dev/null | wc -l)"
    echo "   Mode: $BUILD_MODE"
    echo "   Source: $coderipple_version"
    echo ""
    echo "📁 Generated Files:"
    echo "   • coderipple-package-layer.zip"
    echo "   • build-report.json"
    echo "   • metadata/layer-metadata.json"
    echo ""
}

# Execute main function
main "$@"
